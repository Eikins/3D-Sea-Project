"""
OpenGL Vertex Array
@author: Eikins
"""

import OpenGL.GL as GL

import numpy as np

from sea3d.core import Mesh

class GLStdVBO:

    AttributeLocations = {
        "InPosition":0,
        "InNormal":1,
        "InTangeant":2, # Optional
        "InTexCoord0":3,
        "InTexCoord1":4,
        "InTexCoord2":5,
        "InTexCoord3":6,
        "InTexCoord4":7,
        "InTexCoord5":8,
        "InTexCoord6":9,
        "InTexCoord7":10
    }

    def __init__(self, mesh:Mesh, primitive = GL.GL_TRIANGLES):
        self.mesh = mesh
        self.glid = None
        self.primitive = primitive
        self.buffers = []

    def Init(self):

        # Ensure Numpy formats
        self.mesh.indexes = np.array(self.mesh.indexes, np.int32, copy = False)
        self.mesh.vertices = np.array(self.mesh.vertices, np.float32, copy = False)
        self.mesh.normals = np.array(self.mesh.normals, np.float32, copy = False)
        if self.mesh.tangents is not None:
            self.mesh.tangents = np.array(self.mesh.tangents, np.float32, copy = False)
        if self.mesh.uvs is not None :
            for uv in self.mesh.uvs:
                uv = np.array(uv, dtype = np.float32, copy = False)

        self.glid = GL.glGenVertexArrays(1)

        GL.glBindVertexArray(self.glid)

        self.buffers = GL.glGenBuffers(3)

        # Indexes Attribute
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.buffers[0])
        GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER, self.mesh.indexes, GL.GL_STATIC_DRAW)

        # Vertices Attribute
        _, size = self.mesh.vertices.shape
        GL.glEnableVertexAttribArray(0)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.buffers[1])
        GL.glBufferData(GL.GL_ARRAY_BUFFER, self.mesh.vertices, GL.GL_STATIC_DRAW)
        GL.glVertexAttribPointer(0, size, GL.GL_FLOAT, False, 0, None)

        # Normals Attribute
        _, size = self.mesh.normals.shape
        GL.glEnableVertexAttribArray(1)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.buffers[2])
        GL.glBufferData(GL.GL_ARRAY_BUFFER, self.mesh.normals, GL.GL_STATIC_DRAW)
        GL.glVertexAttribPointer(1, size, GL.GL_FLOAT, False, 0, None)

        # Tangeant Attribute
        if self.mesh.tangents is not None:
            self.buffers = np.append(self.buffers, GL.glGenBuffers(1))
            _, size = self.mesh.tangents.shape
            GL.glEnableVertexAttribArray(2)
            GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.buffers[3])
            GL.glBufferData(GL.GL_ARRAY_BUFFER, self.mesh.tangents, GL.GL_STATIC_DRAW)
            GL.glVertexAttribPointer(2, size, GL.GL_FLOAT, False, 0, None)

        if self.mesh.uvs is not None :
            first = len(self.buffers) 
            self.buffers = np.append(self.buffers, GL.glGenBuffers(len(self.mesh.uvs)))
            for loc, uvChannel in enumerate(self.mesh.uvs):
                _, size = uvChannel.shape

                GL.glEnableVertexAttribArray(3 + loc)
                GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.buffers[first + loc])
                GL.glBufferData(GL.GL_ARRAY_BUFFER, uvChannel, GL.GL_STATIC_DRAW)
                GL.glVertexAttribPointer(3 + loc, size, GL.GL_FLOAT, False, 0, None)

    def Draw(self):
        GL.glBindVertexArray(self.glid)
        GL.glDrawElements(self.primitive, self.mesh.indexes.size, GL.GL_UNSIGNED_INT, None)

    def __del__(self):
        GL.glDeleteVertexArrays(1, [self.glid])
        GL.glDeleteBuffers(len(self.buffers), self.buffers)
