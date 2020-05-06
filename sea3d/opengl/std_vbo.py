"""
OpenGL Vertex Array
@author: Eikins
"""

import OpenGL.GL as GL

import numpy as np

from sea3d.core import Mesh

from sea3d.opengl import GLVertexArrayObject

class GLStdVBO(GLVertexArrayObject):

    AttributeLocations = {
        "InPosition":0,
        "InNormal":1,
        "InTangent":2, # Optional
        "InTexCoord0":3,
        "InTexCoord1":4,
        "InTexCoord2":5,
        "InTexCoord3":6,
        "InTexCoord4":7,
        "InTexCoord5":8,
        "InTexCoord6":9,
        "InTexCoord7":10
    }

    def __init__(self, mesh:Mesh):
        super().__init__()
        self.mesh = mesh
        self.primitive = GL.GL_TRIANGLES

    def Init(self):

        attributes = [self.mesh.vertices, self.mesh.normals, self.mesh.tangents]
        if self.mesh.uvs is not None:
            attributes += self.mesh.uvs

        super().Init(attributes, self.mesh.indexes)


    def Draw(self):
        super().Draw()
