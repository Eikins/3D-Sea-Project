"""
OpenGL Window stuff
@author: Eikins
"""
import os
import OpenGL.GL as GL

class GLMaterial:

    def __init__(self, name:str, vertex:str, frag:str):
        self.name = name
        self.glid = -1

    def __hash__(self):
        return hash(self.glid)

    def __eq__(self, other):
        return self.glid == other.glid

    def __ne__(self, other):
        return not(self == other)

    
    @staticmethod
    def Compile(src, shader_type):
        src = open(src, 'r').read() if os.path.exists(src) else src
        src = src.decode('ascii') if isinstance(src, bytes) else src
        shader = GL.glCreateShader(shader_type) # pylint: disable=E1111
        GL.glShaderSource(shader, src)
        GL.glCompileShader(shader)
        status = GL.glGetShaderiv(shader, GL.GL_COMPILE_STATUS)
        src = ('%3d: %s' % (i+1, l) for i, l in enumerate(src.splitlines()))
        if not status:
            log = GL.glGetShaderInfoLog(shader).decode('ascii')
            GL.glDeleteShader(shader)
            src = '\n'.join(src)
            print('Compile failed for %s\n%s\n%s' % (shader_type, log, src))
            return None
        return shader