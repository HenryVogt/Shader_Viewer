__author__ = 'Henry Vogt'

import sys
from OpenGL.GL import *
from boundingbox import *
from fileLoader import *
from transform import *
from OpenGL.arrays import vbo
import numpy as np


class Model(object):

    def __init__(self, position):
        self.position = position
        self.name = sys.argv[position].split("/")[len(sys.argv[position].split("/"))-1].strip(".obj")
        self.vertices, self.normals, self.textures, self.faces, self.image, self.diffcolor, self.ambcolor, self.speccolor = loadobjfile(sys.argv[position])
        self.bb = BoundingBox(map(min, *self.vertices), map(max, *self.vertices))
        self.actori = 1
        self.axis = [0., 0., 0.]
        self.angle = 0
        self.zoomfaktor = 0
        self.texturize = True
        self.x = 0
        self.y = 0
        self.data = self.getdata()
        self.vbo = vbo.VBO(np.array(self.data, 'f'))
        self.solid = True
        self.wire = False
        self.point = False
        self.img = np.array(self.image)[::-1,:].tostring()
        self.inittexture()

    def inittexture(self):
        glBindTexture(GL_TEXTURE_2D, self.position)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, self.image.size[0], self.image.size[1], 0, GL_RGB, GL_UNSIGNED_BYTE, self.img)
        glGenerateMipmap(GL_TEXTURE_2D)

    def getmvmat(self):
        scale = self.bb.getScale()
        center = self.bb.getCenter()
        mvmat = lookatmatrix(0, 0, 4+self.zoomfaktor, 0, 0, 0, 0, 1, 0)
        mvmat *= translationmatrix(self.x, self.y, 0)
        mvmat *= (rotationmatrix(self.angle, self.axis)*self.actori)
        mvmat *= scalematrix(scale, scale, scale)
        mvmat *= translationmatrix(-(center[0]), -(center[1]), -center[2])
        return mvmat

    def getnormalmat(self):
        mvmat = self.getmvmat()
        normalmat = np.linalg.inv(mvmat[0:3, 0:3]).T
        return normalmat

    def getdata(self):
        data = []
        for face in self.faces:
            for vertex in face:
                vn = vertex[0]-1
                tn = vertex[1]-1
                nn = vertex[2]-1
                data.append(self.vertices[vn]+self.normals[nn]+self.textures[tn])
        return data

    def getdatalength(self):
        return len(self.data)

    def getbb(self):
        return self.bb

    def getimage(self):
        return self.image

    def getname(self):
        return self.name

    def getactori(self):
        return self.actori

    def setactori(self, actori):
        self.actori = actori

    def getaxis(self):
        return self.axis

    def setaxis(self, axis):
        self.axis = axis

    def getangle(self):
        return self.angle

    def setangle(self, angle):
        self.angle = angle

    def getzoomfaktor(self):
        return self.zoomfaktor

    def setzoomfaktor(self, zoomfaktor):
        self.zoomfaktor = zoomfaktor

    def getdiffcolor(self):
        return self.diffcolor

    def getambcolor(self):
        return self.ambcolor

    def getspeccolor(self):
        return self.speccolor

    def gettexturize(self):
        return self.texturize

    def settexturize(self, texturize):
        self.texturize = texturize

    def getx(self):
        return self.x

    def setx(self, x):
        self.x = x

    def gety(self):
        return self.y

    def sety(self, y):
        self.y = y

    def getvbo(self):
        return self.vbo

    def setvbo(self, vbo):
        self.vbo = vbo

    def getsolid(self):
        return self.solid

    def setsolid(self, solid):
        self.solid = solid

    def getwire(self):
        return self.wire

    def setwire(self, wire):
        self.wire = wire

    def getpoint(self):
        return self.point

    def setpoint(self, point):
        self.point = point

    def getposition(self):
        return self.position