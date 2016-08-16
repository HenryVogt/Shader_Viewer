__author__ = 'Henry Vogt'

from PIL import Image
import numpy as np


def loadobjfile(filename):
    """ *.obj Datei laden """
    vertices = []
    normals = []
    textures = []
    faces = []
    image = None
    path = "/".join(filename.split("/")[:-1])
    if len(path) > 0:
        path += "/"

    diffcolor = None
    ambcolor = None
    speccolor = None

    with open(filename) as objFile:
        for line in objFile:
            if line.split(" ")[0] == "v":
                vertices.append(map(float, line.split()[1:4]))

            if line.split(" ")[0] == "vn":
                normals.append(map(float, line.split()[1:]))

            if line.split(" ")[0] == "vt":
                textures.append(map(float, line.split()[1:]))

            if line.split(" ")[0] == "mtllib":
                with open(path+line.split()[1:][0].strip("./")) as mtlFile:
                    for line in mtlFile:
                        if line.split(" ")[0] == "map_Kd":
                            image = Image.open(path+line.split()[1:][0])
                        if line.split(" ")[0] == "Ka":
                            ambcolor = map(float, line.split()[1:])
                            if len(ambcolor) == 3:
                                ambcolor.append(1.)
                        if line.split(" ")[0] == "Kd":
                            diffcolor = map(float, line.split()[1:])
                            if len(diffcolor) == 3:
                                diffcolor.append(1.)
                        if line.split(" ")[0] == "Ks":
                            speccolor = map(float, line.split()[1:])
                            if len(speccolor) == 3:
                                speccolor.append(1.)

            if line.split(" ")[0] == "f":
                faceline = line.split()[1:]
                face = []
                for item in faceline:
                    if "//" in item:
                        face.append(map(int, item.split("//")))
                    else:
                        face.append(map(int, item.split("/")))
                faces.append(face)

    if not normals:
        for i in range(0, len(vertices)):
            normals.insert(i, np.array([0., 0., 0.]))

        for face in faces:

            # Punkte der Vertices auslesen
            p1 = vertices[face[0][0]-1]
            p2 = vertices[face[1][0]-1]
            p3 = vertices[face[2][0]-1]

            # Indizes der Vertices
            v1Index = face[0][0]
            v2Index = face[1][0]
            v3Index = face[2][0]

            # Vektoren des Dreiecks berechnen
            v1 = np.array(p2)-np.array(p1)
            v2 = np.array(p3)-np.array(p1)

            # Normale des Dreiecks berechnen
            n = np.cross(v1, v2)

            # Normalen hinzufuegen am gleichen Index wie die Vertices
            normals[v1Index-1] += n
            normals[v2Index-1] += n
            normals[v3Index-1] += n

            # Faces ergaenzen um Normaleninformation
            face[0].insert(2, v1Index)
            face[1].insert(2, v2Index)
            face[2].insert(2, v3Index)

        for i in range(0, len(normals)):
            normalized = normals[i]
            normals[i] = list(normalized)

    return vertices, normals, textures, faces, image, diffcolor, ambcolor, speccolor