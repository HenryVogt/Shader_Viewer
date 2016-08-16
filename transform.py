__author__ = 'Henry Vogt'

from math import *
from numpy import *


def rotationmatrix(angle, axis):
    c = cos(angle)
    mc = 1-cos(angle)
    s = sin(angle)
    l = sqrt(dot(array(axis), array(axis)))
    if l == 0:
        return eye(4)
    x, y, z = array(axis) / l
    r = matrix([
        [x*x*mc+c, x*y*mc-z*s, x*z*mc+y*s, 0],
        [x*y*mc+z*s, y*y*mc+c, y*z*mc-x*s, 0],
        [x*z*mc-y*s, y*z*mc+x*s, z*z*mc+c, 0],
        [0, 0, 0, 1]])
    return r


def scalematrix(sx, sy, sz):
    s = matrix([[sx, 0, 0, 0],
               [0, sy, 0, 0],
               [0, 0, sz, 0],
               [0, 0, 0, 1]])
    return s


def translationmatrix(tx, ty, tz):
    t = matrix([[1, 0, 0, tx],
               [0, 1, 0, ty],
               [0, 0, 1, tz],
               [0, 0, 0, 1]])
    return t


def lookatmatrix(ex, ey, ez, cx, cy, cz, ux, uy, uz):
    e = array([ex, ey, ez])  # eye position
    c = array([cx, cy, cz])  # center
    up = array([ux, uy, uz])  # up vector
    f = c - e  # view direction

    up = up / sqrt(dot(up, up))  # normalize up vector
    f = f / sqrt(dot(f, f))  # normalize view direction

    s = cross(f, up)  # calculate s
    s = s / sqrt(dot(s, s))  # normalize s
    u = cross(s, f)  # calculate u

    l = matrix([
        [s[0], s[1], s[2], -dot(s, e)],
        [u[0], u[1], u[2], -dot(u, e)],
        [-f[0], -f[1], -f[2], dot(f, e)],
        [0, 0, 0, 1]])
    return l


def perspectivematrix(fovy, aspect, znear, zfar):
    f = 1.0 / tan(fovy/2.0)
    aspect = float(aspect)
    znear = float(znear)
    zfar = float(zfar)
    p = matrix([[f/aspect, 0, 0, 0],
               [0, f, 0, 0],
               [0, 0, (zfar+znear)/(znear-zfar), (2*zfar*znear)/(znear-zfar)],
               [0, 0, -1, 0]])
    return p