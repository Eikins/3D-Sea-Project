"""
OpenGL Window stuff
@author: Eikins
"""
import os
import OpenGL.GL as GL

class GLMaterial:

    def __init__(self, name:str, vertex:str, frag:str):
        self.name = name
        self.glid = None
        self.vertexSrc = vertex
        self.fragSrc = frag

    def Init(self):
        vert = GLMaterial.Compile(self.vertexSrc, GL.GL_VERTEX_SHADER)
        frag = GLMaterial.Compile(self.fragSrc, GL.GL_FRAGMENT_SHADER)

        if vert and frag:
            self.glid = GL.glCreateProgram()
            GL.glAttachShader(self.glid, vert)
            GL.glAttachShader(self.glid, frag)
            GL.glLinkProgram(self.glid)
            GL.glDeleteShader(vert)
            GL.glDeleteShader(frag)

            status = GL.glGetProgramiv(self.glid, GL.GL_LINK_STATUS)
            if not status:
                print(GL.glGetProgramInfoLog(self.glid).decode("ascii"))
                GL.glDeleteProgram(self.glid)
                self.glid = None

    def __del__(self):
        if self.glid is not None:
            GL.glDeleteProgram(self.glid)
    
    @staticmethod
    def Compile(src, shader_type):
        src = open(src, "r").read() if os.path.exists(src) else src
        src = src.decode("ascii") if isinstance(src, bytes) else src
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