__author__ = 'Henry Vogt'

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GL.shaders import *
from model import *


MODELS = []
AKTMODEL = None

LIGHTPOS = [0, 0, 1]

WIDTHGLOBAL = 1
HEIGHTGLOBAL = 0
STARTPOINT = None

ROTATION = False
TRANSLATION = False
ZOOM = False

OLDX = 0
OLDY = 0
DIFFYOLD = 0

PROJECTIONMATRIX = None

SHADERPROGRAM = None

SCHWARZ = (0., 0., 0., 0.)
GRAU = (0.5, 0.5, 0.5, 0.5)
WEISS = (1., 1., 1., 1.)
ROT = (1., 0., 0., 0.)
BLAU = (0., 0., 1., 0.)
GELB = (1., 1., 0., 0.)


def init(width, height):
    """ OpenGL Fenster initialisieren """
    global SHADERPROGRAM, PROJECTIONMATRIX, AKTMODEL

    glClearColor(*GRAU)
    PROJECTIONMATRIX = perspectivematrix(45., float(width) / height, 0.1, 100.)
    AKTMODEL = MODELS[0]
    vertexshader = compileShader(open("shader/phongShader.vs", "r").read(), GL_VERTEX_SHADER)
    fragmentshader = compileShader(open("shader/phongShader.fs", "r").read(), GL_FRAGMENT_SHADER)
    glGenTextures(len(MODELS))
    SHADERPROGRAM = compileProgram(vertexshader, fragmentshader)
    glEnable(GL_DEPTH_TEST)


def display():
    """ Objekte rendern """
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glEnableClientState(GL_VERTEX_ARRAY)
    glEnableClientState(GL_TEXTURE_COORD_ARRAY)
    glEnableClientState(GL_NORMAL_ARRAY)

    for i in range(len(MODELS)):
        myvbo = MODELS[i].getvbo()
        mvmat = MODELS[i].getmvmat()
        mvpmat = PROJECTIONMATRIX * mvmat

        if MODELS[i].getsolid():
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        if MODELS[i].getwire():
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        if MODELS[i].getpoint():
            glPolygonMode(GL_FRONT_AND_BACK, GL_POINT)

        glUseProgram(SHADERPROGRAM)

        sendmatrix4(SHADERPROGRAM, "mvMatrix", mvmat)
        sendmatrix4(SHADERPROGRAM, "mvpMatrix", mvpmat)
        sendmatrix3(SHADERPROGRAM, "normalMatrix", MODELS[i].getnormalmat())
        sendvector4(SHADERPROGRAM, "diffuseColor", MODELS[i].getdiffcolor())
        sendvector4(SHADERPROGRAM, "ambientColor", MODELS[i].getambcolor())
        sendvector4(SHADERPROGRAM, "specularColor", MODELS[i].getspeccolor())
        sendvector3(SHADERPROGRAM, "lightPosition", LIGHTPOS)
        sendvalue(SHADERPROGRAM, "texturize", MODELS[i].gettexturize())

        myvbo.bind()
        glVertexPointer(3, GL_FLOAT, 32, myvbo)
        glTexCoordPointer(2, GL_FLOAT, 32, myvbo+24)
        glNormalPointer(GL_FLOAT, 32, myvbo+12)
        glBindTexture(GL_TEXTURE_2D, MODELS[i].getposition())
        glDrawArrays(GL_TRIANGLES, 0, MODELS[i].getdatalength())
        myvbo.unbind()

    glDisableClientState(GL_VERTEX_ARRAY)
    glDisableClientState(GL_TEXTURE_COORD_ARRAY)
    glDisableClientState(GL_NORMAL_ARRAY)

    glutSwapBuffers()


def sendvalue(shaderprogram, varname, value):
    varlocation = glGetUniformLocation(shaderprogram, varname)
    glUniform1f(varlocation, value)


def sendvector3(shaderprogram, varname, value):
    varlocation = glGetUniformLocation(shaderprogram, varname)
    glUniform3f(varlocation, *value)


def sendvector4(shaderprogram, varname, value):
    varlocation = glGetUniformLocation(shaderprogram, varname)
    glUniform4f(varlocation, *value)


def sendmatrix3(shaderprogram, varname, matr):
    varlocation = glGetUniformLocation(shaderprogram, varname)
    glUniformMatrix3fv(varlocation, 1, GL_TRUE, matr.tolist())


def sendmatrix4(shaderprogram, varname, matr):
    varlocation = glGetUniformLocation(shaderprogram, varname)
    glUniformMatrix4fv(varlocation, 1, GL_TRUE, matr.tolist())


def reshape(width, height):
    """ Anpassung Seitenverhaeltnis """
    global WIDTHGLOBAL, HEIGHTGLOBAL, PROJECTIONMATRIX

    WIDTHGLOBAL = width
    HEIGHTGLOBAL = height
    PROJECTIONMATRIX = perspectivematrix(45., float(width) / height, 0.1, 100.)
    glViewport(0, 0, width, height)

    glutPostRedisplay()


def initgeometry():
    """ Geometriedaten des Objekts aufbereiten """
    global MODELS

    if len(sys.argv) == 1:
        print 'python multiShaderViewer.py object.obj ...'
        sys.exit(-1)

    for i in range(1, len(sys.argv)):
        MODELS.append(Model(i))


def keypressed(key, x, y):
    """ Tastatureingaben verarbeiten """
    global AKTMODEL

    if key == chr(27):
        sys.exit()

    if key == 's':
        AKTMODEL.setsolid(True)
        AKTMODEL.setwire(False)
        AKTMODEL.setpoint(False)

    if key == 'w':
        AKTMODEL.setwire(True)
        AKTMODEL.setsolid(False)
        AKTMODEL.setpoint(False)

    if key == 'p':
        AKTMODEL.setpoint(True)
        AKTMODEL.setsolid(False)
        AKTMODEL.setwire(False)

    if key == 't':
        if AKTMODEL.gettexturize():
            AKTMODEL.settexturize(False)
        else:
            AKTMODEL.settexturize(True)

    if key == '1':
        AKTMODEL = MODELS[0]
        print AKTMODEL.getname() + " active"

    if key == '2':
        if len(MODELS) > 1:
            AKTMODEL = MODELS[1]
            print AKTMODEL.getname() + " active"

    glutPostRedisplay()


def mousebuttonpressed(button, state, x, y):
    """ Mausklicks verarbeiten """
    global STARTPOINT, ROTATION, TRANSLATION, OLDX, OLDY, ZOOM, DIFFYOLD

    angl = AKTMODEL.getangle()
    axis = AKTMODEL.getaxis()
    actori = AKTMODEL.getactori()
    r = min(WIDTHGLOBAL, HEIGHTGLOBAL) / 2.0

    if button == GLUT_LEFT_BUTTON:
        if state == GLUT_DOWN:
            ROTATION = True
            STARTPOINT = projectonsphere(x, y, r)
        if state == GLUT_UP:
            ROTATION = False
            AKTMODEL.setactori((rotationmatrix(angl, axis)*actori))
            AKTMODEL.setangle(0)

    if button == GLUT_RIGHT_BUTTON:
        if state == GLUT_DOWN:
            TRANSLATION = True
            OLDX, OLDY = x, y
        if state == GLUT_UP:
            TRANSLATION = False

    if button == GLUT_MIDDLE_BUTTON:
        if state == GLUT_DOWN:
            ZOOM = True
            OLDY = y
        if state == GLUT_UP:
            ZOOM = False
            DIFFYOLD = 0


def mousemoved(x, y):
    """ Mausbewegungen verarbeiten """

    if ROTATION:
        r = min(WIDTHGLOBAL, HEIGHTGLOBAL) / 2.0
        moveP = projectonsphere(x, y, r)
        AKTMODEL.setangle(acos(np.dot(STARTPOINT, moveP)))
        AKTMODEL.setaxis(np.cross(STARTPOINT, moveP))

    if TRANSLATION:
        translate(x, y)

    if ZOOM:
        zoom(y)

    glutPostRedisplay()


def projectonsphere(x, y, r):
    x, y = x-WIDTHGLOBAL/2.0, HEIGHTGLOBAL/2.0-y
    a = min(r*r, x**2 + y**2)
    z = sqrt(r*r -a)
    l = sqrt(x**2 + y**2 + z**2)
    return x/l, y/l, z/l


def translate(x, y):
    """ Translation verarbeiten """
    global OLDX, OLDY

    diffx, diffy = x - OLDX, y - OLDY
    aktx = AKTMODEL.getx()
    akty = AKTMODEL.gety()

    if diffx != 0:
        AKTMODEL.setx(aktx + (diffx / (WIDTHGLOBAL / 4.0)))

    if diffy != 0:
        AKTMODEL.sety(akty - (diffy / (HEIGHTGLOBAL / 4.0)))

    OLDX = x
    OLDY = y


def zoom(y):
    """ Zoom verarbeiten """
    global DIFFYOLD, AKTMODEL

    diffy = y - OLDY
    aktzoomfaktor = AKTMODEL.getzoomfaktor()

    if (diffy < 0 and DIFFYOLD < diffy) or (diffy > 0 and DIFFYOLD > diffy):
        AKTMODEL.setzoomfaktor(aktzoomfaktor + (diffy / float(HEIGHTGLOBAL)))

    if (diffy < 0 and DIFFYOLD > diffy) or (diffy > 0 and DIFFYOLD < diffy):
        AKTMODEL.setzoomfaktor(aktzoomfaktor - (diffy / float(HEIGHTGLOBAL)))

    DIFFYOLD = diffy


def main():
    """ Initialisiere GLUT """
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(600, 500)
    glutCreateWindow("ShaderViewer")
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(keypressed)
    glutMouseFunc(mousebuttonpressed)
    glutMotionFunc(mousemoved)
    initgeometry()
    init(600, 500)
    glutMainLoop()


if __name__ == "__main__":
    main()