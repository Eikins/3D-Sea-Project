"""
OpenGL Vertex Array
@author: Eikins
"""

import OpenGL.GL as GL

from sea3d.core import Mesh

class GLVertexArray:

    def __init__(self, mesh:Mesh):
        self.mesh = mesh
        self.glid = None
        self.buffers = []

    def Init(self):
        self.glid = GL.glGenVertexArrays(1)

        GL.glBindVertexArray(self.glid)

        self.buffers = GL.glGenBuffers(3)

        # Vertices Attribute
        _, size = self.mesh.vertices.shape
        GL.glEnableVertexAttribArray(0)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.buffers[0])
        GL.glBufferData(GL.GL_ARRAY_BUFFER, self.mesh.vertices, GL.GL_STATIC_DRAW)
        GL.glVertexAttribPointer(0, size, GL.GL_FLOAT, False, 0, None)

        # Normals Attribute
        _, size = self.mesh.normals.shape
        GL.glEnableVertexAttribArray(1)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.buffers[1])
        GL.glBufferData(GL.GL_ARRAY_BUFFER, self.mesh.normals, GL.GL_STATIC_DRAW)
        GL.glVertexAttribPointer(1, size, GL.GL_FLOAT, False, 0, None)

        # Indexes Attribute
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.buffers[2])
        GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER, self.mesh.indexes, GL.GL_STATIC_DRAW)

    def Draw(self):
        GL.glBindVertexArray(self.glid)
        GL.glDrawElements(GL.GL_TRIANGLES, self.mesh.indexes.size, GL.GL_UNSIGNED_INT, None)

    def __del__(self):
        GL.glDeleteVertexArrays(1, [self.glid])
        GL.glDeleteBuffers(len(self.buffers), self.buffers)
