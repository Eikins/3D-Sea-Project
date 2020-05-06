"""
OpenGL Vertex Array
@author: Eikins
"""

import OpenGL.GL as GL

import numpy as np

from sea3d.core import Mesh

class GLVertexArrayObject:

    def __init__(self):
        self.glid = None
        self.buffers = []
        self.primitive = GL.GL_TRIANGLES

    def Init(self, attributes, indexes = None, usage = GL.GL_STATIC_DRAW):
        self.glid = GL.glGenVertexArrays(1)
        GL.glBindVertexArray(self.glid)

        n, size = 0, 0

        for loc, data in enumerate(attributes):
            if data is not None:
                # Bind a new buffer and upload its data to GPU
                self.buffers += [GL.glGenBuffers(1)]
                # Ensuire numpy format
                data = np.array(data, np.float32, copy = False)
                n, size = data.shape # pylint: disable=unpacking-non-sequence  # pylint/issues/3139
                
                GL.glEnableVertexAttribArray(loc)
                GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.buffers[-1])
                GL.glBufferData(GL.GL_ARRAY_BUFFER, data, usage)
                GL.glVertexAttribPointer(loc, size, GL.GL_FLOAT, False, 0, None)

        if indexes is not None:
            self.buffers += [GL.glGenBuffers(1)]
            index_buffer = np.array(indexes, np.int32, copy = False)
            GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.buffers[-1])
            GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER, index_buffer, usage)
            self.draw_command = GL.glDrawElements
            self.arguments = (index_buffer.size, GL.GL_UNSIGNED_INT, None)
        else:
            self.draw_command = GL.glDrawArrays
            self.arguments = (0, n)

        GL.glBindVertexArray(0)

    def Draw(self):
        GL.glBindVertexArray(self.glid)
        self.draw_command(self.primitive, *self.arguments)
        GL.glBindVertexArray(0)

    def __del__(self):
        if self.glid is not None:
            GL.glDeleteVertexArrays(1, [self.glid])
        if not self.buffers:
            GL.glDeleteBuffers(len(self.buffers), self.buffers)
