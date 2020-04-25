"""
OpenGL Render Pipeline
@author: Eikins
"""

import OpenGL.GL as GL
import glfw    
import numpy as np

from sea3d.core import PropertyBlock
from sea3d.opengl import GLMaterialBatch, GLVertexBufferObject

class GLFramebuffer:

    def __init__(self, width:int, height:int, frag:str):
        self.width = width
        self.height = height
        self.frag = frag
        self.glid:int = None
        self.texture:int = None
        self.depth:int = None
        self.depthTex:int = None
        self.vbo:int = None
        self.program:int = None
        self.texUniform:int = None
        self.depthTexUniform:int = None
        self.sizeUniform:int = None
        self.coordAttribute:int = None

    def Init(self):
        if self.CreateFramebuffer():
            self.CreateVBO()
            self.CreateProgram()


    def CreateFramebuffer(self):
        noError = True

        # Create the buffer
        self.texture = GL.glGenTextures(1)
        GL.glActiveTexture(GL.GL_TEXTURE0)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.texture)
        # CLAMP TO EDGE to avoid border warping
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S, GL.GL_CLAMP_TO_EDGE)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_T, GL.GL_CLAMP_TO_EDGE)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
        GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, GL.GL_RGBA, self.width, self.height, 0, GL.GL_RGBA, GL.GL_UNSIGNED_BYTE, None)

        self.depthTex = GL.glGenTextures(1)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.depthTex)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S, GL.GL_CLAMP_TO_EDGE)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_T, GL.GL_CLAMP_TO_EDGE)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
        GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, GL.GL_DEPTH_COMPONENT, self.width, self.height, 0, GL.GL_DEPTH_COMPONENT, GL.GL_UNSIGNED_BYTE, None)

        # Declare depth buffer
        self.depth = GL.glGenRenderbuffers(1)
        GL.glBindRenderbuffer(GL.GL_RENDERBUFFER, self.depth)
        GL.glRenderbufferStorage(GL.GL_RENDERBUFFER, GL.GL_DEPTH_COMPONENT32, self.width, self.height)
        GL.glBindRenderbuffer(GL.GL_RENDERBUFFER, 0)

        # Generate framebuffer and link all
        self.glid = GL.glGenFramebuffers(1)
        GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, self.glid)
        # Link depth to the framebuffer
        GL.glFramebufferRenderbuffer(GL.GL_FRAMEBUFFER, GL.GL_DEPTH_ATTACHMENT, GL.GL_RENDERBUFFER, self.depth)

        # We don't want mipmaps on a framebuffer, mip level set to 0
        GL.glFramebufferTexture2D(GL.GL_FRAMEBUFFER, GL.GL_COLOR_ATTACHMENT0, GL.GL_TEXTURE_2D, self.texture, 0)
        GL.glFramebufferTexture2D(GL.GL_FRAMEBUFFER, GL.GL_DEPTH_ATTACHMENT, GL.GL_TEXTURE_2D, self.depthTex, 0)
        # Error check
        status = GL.glCheckFramebufferStatus(GL.GL_FRAMEBUFFER)
        if (status != GL.GL_FRAMEBUFFER_COMPLETE):
            print("Error when creating framebuffer : ", status)
            noError = False

        GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, 0)

        return noError

    def CreateVBO(self):
        vertices = np.array(
        (
            (-1.0, -1.0), (1.0, -1.0), (-1.0, 1.0),
            (-1.0, 1.0), (1.0, -1.0), (1.0, 1.0)
        ),'f')

        self.vbo = GLVertexBufferObject()
        self.vbo.Init([vertices])


    def CreateProgram(self):
        vertex = GLMaterialBatch.Compile("assets/shaders/post/post.vert", GL.GL_VERTEX_SHADER)
        frag = GLMaterialBatch.Compile("assets/shaders/post/" + self.frag + ".frag", GL.GL_FRAGMENT_SHADER)

        self.program = GL.glCreateProgram()
        GL.glAttachShader(self.program, vertex)
        GL.glAttachShader(self.program, frag)
        GL.glLinkProgram(self.program)

        status = GL.glGetProgramiv(self.program, GL.GL_LINK_STATUS)
        if not status:
            print(GL.glGetProgramInfoLog(self.program).decode("ascii"))
            GL.glDeleteProgram(self.program)

        GL.glBindAttribLocation(self.program, 0, "_Coords")
        self.texUniform = GL.glGetUniformLocation(self.program, "_MainTex")
        self.depthTexUniform = GL.glGetUniformLocation(self.program, "_DepthTex")
        self.sizeUniform = GL.glGetUniformLocation(self.program, "_ScreenSize")

    def Bind(self):
        GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, self.glid)

    def Unbind(self):
        GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, 0)

    def Draw(self, props:PropertyBlock = None):
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)
        GL.glDisable(GL.GL_DEPTH_TEST)
        GL.glUseProgram(self.program)

        GL.glActiveTexture(GL.GL_TEXTURE0)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.texture)

        GL.glActiveTexture(GL.GL_TEXTURE1)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.depthTex)

        GL.glUniform1i(self.texUniform, 0)
        GL.glUniform1i(self.depthTexUniform, 1)

        if props is not None:
            # Bind Properties
            for name, value in props.floatProperties.items():
                loc = GL.glGetUniformLocation(self.program, name)
                GL.glUniform1f(loc, value)

            for name, value in props.intProperties.items():
                loc = GL.glGetUniformLocation(self.program, name)
                GL.glUniform1i(loc, value)
        
            for name, value in props.vec3Properties.items():
                loc = GL.glGetUniformLocation(self.program, name)
                GL.glUniform3f(loc, value.x, value.y, value.z)

            #TODO : Add Textures

        GL.glUniform2f(self.sizeUniform, self.width, self.height)
        self.vbo.Draw()

    
    def __del__(self):
        if self.depth is not None:
            GL.glDeleteRenderbuffers(1, [self.depth])
        if self.texture is not None:
            GL.glDeleteTextures(1, [self.texture])
        if self.glid is not None:
            GL.glDeleteFramebuffers(1, [self.glid])
        if self.program is not None:
            GL.glDeleteProgram(self.program)

                

