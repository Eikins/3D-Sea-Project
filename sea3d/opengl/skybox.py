"""
OpenGL Vertex Array
@author: Eikins
"""

import OpenGL.GL as GL

import numpy as np

from sea3d.core import Mesh

from sea3d.opengl import GLVertexArrayObject

class GLSkybox(GLVertexArrayObject):

    def __init__(self):
        super().__init__()
        self.vertices = np.array(
        (
            (-1, 1, 1), (-1, -1, 1), (1, -1, 1), (1, 1, 1),
            (-1, -1, -1), (-1,-1, 1), (-1, 1, 1), (-1, 1, -1),
            (1, -1, 1), (1, -1, -1), (1, 1, -1), (1, 1, 1),
            (-1, -1, -1), (-1, 1, -1), (1, 1, -1), (1, -1, 1),
            (-1, 1, 1), (1, 1, 1), (1, 1, -1), (-1, 1, -1),
            (-1, -1, 1), (-1, -1, -1), (1, -1, 1), (1, -1, -1) 
        ),'f')
        self.indexes = np.array(
        (
            (0, 1, 2), (0, 2, 3),
            (4, 5, 6), (4, 6, 7),
            (8, 9, 10), (8, 10, 11),
            (12, 13, 14), (12, 14, 15),
            (16, 17, 18), (16, 18, 19),
            (20, 21, 22), (20, 22, 23)
        ),'u4')
        self.primitive = GL.GL_TRIANGLES

    def Init(self):
        super().Init([self.vertices], self.indexes)

    def Draw(self):
        GL.glDepthFunc(GL.GL_LEQUAL)
        super().Draw()
        GL.glDepthFunc(GL.GL_LESS)
