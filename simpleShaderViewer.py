__author__ = 'Henry Vogt'

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GL.shaders import *
from OpenGL.arrays import vbo
from transform import *
from model import *

MYVBO = None
BB = None
DATA = []
TEXTUREID = None
TEXTURE = True
IMG = None
AKTMODEL = 1

LIGHTPOS = [0, 0, 1]
DIFFCOLOR = None
AMBCOLOR = None
SPECCOLOR = None

ACTORI = 1
AXIS = [0., 0., 0.]
ANGLE = 0
WIDTHGLOBAL = 1
HEIGHTGLOBAL = 0
STARTPOINT = None
ROTATION = False
TRANSLATION = False
ZOOM = False

OLDX = 0
OLDY = 0
X = 0
Y = 0
ZOOMFAKTOR = 0
DIFFYOLD = 0

SCALE = 0.
CENTER = None

PROJECTIONMATRIX = None

SHADERPROGRAM = None

SCHWARZ = (0., 0., 0., 0.)
GRAU = (0.5, 0.5, 0.5, 0.5)
WEISS = (1., 1., 1., 1.)
ROT = (1., 0., 0., 0.)
BLAU = (0., 0., 1., 0.)
GELB = (1., 1., 0., 0.)

SOLID = True
WIRE = False
POINT = False


def init(width, height):
    """ OpenGL Fenster initialisieren """
    global SHADERPROGRAM, PROJECTIONMATRIX, TEXTUREID
    glClearColor(*GRAU)
    PROJECTIONMATRIX = perspectivematrix(45., float(width) / height, 0.1, 100.)

    vertexshader = compileShader(open("shader/phongShader.vs", "r").read(), GL_VERTEX_SHADER)
    fragmentshader = compileShader(open("shader/phongShader.fs", "r").read(), GL_FRAGMENT_SHADER)

    image = array(IMG)[::-1,:].tostring()

    TEXTUREID = glGenTextures(1)

    glBindTexture(GL_TEXTURE_2D, TEXTUREID)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, IMG.size[0], IMG.size[1], 0, GL_RGB, GL_UNSIGNED_BYTE, image)
    glGenerateMipmap(GL_TEXTURE_2D)

    SHADERPROGRAM = compileProgram(vertexshader, fragmentshader)

    glEnable(GL_DEPTH_TEST)


def display():
    """ Objekte rendern """
    global MYVBO, BB, SCALE, CENTER
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    SCALE = BB.getScale()
    CENTER = BB.getCenter()

    mvmat = lookatmatrix(0, 0, 4+ZOOMFAKTOR, 0, 0, 0, 0, 1, 0)
    mvmat *= translationmatrix(X, Y, 0)
    mvmat *= (rotationmatrix(ANGLE, AXIS)*ACTORI)
    mvmat *= scalematrix(SCALE, SCALE, SCALE)
    mvmat *= translationmatrix(-(CENTER[0]), -(CENTER[1]), -CENTER[2])
    normalmat = np.linalg.inv(mvmat[0:3, 0:3]).T
    mvpmat = PROJECTIONMATRIX * mvmat

    if SOLID:
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    if WIRE:
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    if POINT:
        glPolygonMode(GL_FRONT_AND_BACK, GL_POINT)

    glUseProgram(SHADERPROGRAM)

    sendmatrix4(SHADERPROGRAM, "mvMatrix", mvmat)
    sendmatrix4(SHADERPROGRAM, "mvpMatrix", mvpmat)
    sendmatrix3(SHADERPROGRAM, "normalMatrix", normalmat)
    sendvector4(SHADERPROGRAM, "diffuseColor", DIFFCOLOR)
    sendvector4(SHADERPROGRAM, "ambientColor", AMBCOLOR)
    sendvector4(SHADERPROGRAM, "specularColor", SPECCOLOR)
    sendvector3(SHADERPROGRAM, "lightPosition", LIGHTPOS)
    sendvalue(SHADERPROGRAM, "texturize", TEXTURE)

    glEnableClientState(GL_VERTEX_ARRAY)
    glEnableClientState(GL_TEXTURE_COORD_ARRAY)
    glEnableClientState(GL_NORMAL_ARRAY)

    MYVBO.bind()
    glVertexPointer(3, GL_FLOAT, 32, MYVBO)
    glTexCoordPointer(2, GL_FLOAT, 32, MYVBO+24)
    glNormalPointer(GL_FLOAT, 32, MYVBO+12)
    glBindTexture(GL_TEXTURE_2D, TEXTUREID)
    glDrawArrays(GL_TRIANGLES, 0, len(DATA))
    MYVBO.unbind()

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
    global MYVBO, BB, DATA, MYVBOS, IMG, DIFFCOLOR, AMBCOLOR, SPECCOLOR

    if len(sys.argv) == 1:
        print "python simpleShaderViewer.py object.obj"
        sys.exit(-1)

    vertices, normals, textures, faces, IMG, DIFFCOLOR, AMBCOLOR, SPECCOLOR = loadobjfile(sys.argv[1])

    BB = BoundingBox(map(min, *vertices), map(max, *vertices))

    for face in faces:
        for vertex in face:
            vn = vertex[0]-1
            tn = vertex[1]-1
            nn = vertex[2]-1
            DATA.append(vertices[vn]+normals[nn]+textures[tn])

    MYVBO = vbo.VBO(np.array(DATA, 'f'))


def keypressed(key, x, y):
    """ Tastatureingaben verarbeiten """
    global SOLID, WIRE, POINT, TEXTURE

    if key == chr(27):
        sys.exit()

    if key == 's':
        SOLID = True
        WIRE = False
        POINT = False

    if key == 'w':
        WIRE = True
        SOLID = False
        POINT = False

    if key == 'p':
        POINT = True
        SOLID = False
        WIRE = False

    if key == 't':
        if TEXTURE:
            TEXTURE = False
        else:
            TEXTURE = True

    glutPostRedisplay()


def mousebuttonpressed(button, state, x, y):
    """ Mausklicks verarbeiten """
    global STARTPOINT, ACTORI, ANGLE, ROTATION, TRANSLATION, OLDX, OLDY, ZOOM, DIFFYOLD

    r = min(WIDTHGLOBAL, HEIGHTGLOBAL) / 2.0

    if button == GLUT_LEFT_BUTTON:
        if state == GLUT_DOWN:
            ROTATION = True
            STARTPOINT = projectonsphere(x, y, r)
        if state == GLUT_UP:
            ROTATION = False
            ACTORI = rotationmatrix(ANGLE, AXIS)*ACTORI
            ANGLE = 0

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
    global ANGLE, AXIS

    if ROTATION:
        r = min(WIDTHGLOBAL, HEIGHTGLOBAL) / 2.0
        moveP = projectonsphere(x, y, r)
        ANGLE = acos(np.dot(STARTPOINT, moveP))
        AXIS = np.cross(STARTPOINT, moveP)

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
    global OLDX, OLDY, X, Y

    diffx, diffy = x - OLDX, y - OLDY

    if diffx != 0:
        X += diffx / (WIDTHGLOBAL / 4.0)

    if diffy != 0:
        Y += -diffy / (HEIGHTGLOBAL / 4.0)

    OLDX = x
    OLDY = y


def zoom(y):
    """ Zoom verarbeiten """
    global ZOOMFAKTOR, DIFFYOLD

    diffy = y - OLDY

    if (diffy < 0 and DIFFYOLD < diffy) or (diffy > 0 and DIFFYOLD > diffy):
        ZOOMFAKTOR += (diffy / float(HEIGHTGLOBAL))

    if (diffy < 0 and DIFFYOLD > diffy) or (diffy > 0 and DIFFYOLD < diffy):
        ZOOMFAKTOR -= (diffy / float(HEIGHTGLOBAL))

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