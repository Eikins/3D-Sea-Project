"""
OpenGL Window stuff
@author: Eikins
"""
import os
import OpenGL.GL as GL

from sea3d.core import Material
from sea3d.opengl import GLStdVBO

class GLMaterialBatch:

    def __init__(self):
        self.materialsToBake = []
        self.vertexShaders = dict()
        self.fragmentShaders = dict()
        self.tesselationControlShaders = dict()
        self.tesselationEvaluationShaders = dict()
        self.programs = dict()
        self.materialPrograms = dict()

    def AddMaterial(self, material:Material):
        self.materialsToBake += [material]

    def BakeMaterials(self):
        for material in self.materialsToBake:

            if material.vertex not in self.vertexShaders:
                vertex = self.vertexShaders[material.vertex] = GLMaterialBatch.Compile("assets/shaders/" + material.vertex + ".vert", GL.GL_VERTEX_SHADER)
            else:
                vertex = self.vertexShaders[material.vertex]

            if material.fragment not in self.fragmentShaders:
                frag = self.fragmentShaders[material.fragment] = GLMaterialBatch.Compile("assets/shaders/" + material.fragment + ".frag", GL.GL_FRAGMENT_SHADER)
            else:
                frag = self.fragmentShaders[material.fragment]

            # Add Tessellation support
            if material.useTessellation:
                if material.tessellationControl not in self.tesselationControlShaders:
                    tcs = self.tesselationControlShaders[material.tessellationControl] = GLMaterialBatch.Compile("assets/shaders/" + material.tessellationControl + ".tcs", GL.GL_TESS_CONTROL_SHADER)
                else:
                    tcs = self.tesselationControlShaders[material.tessellationControl]

                if material.tessellationEvaluation not in self.tesselationEvaluationShaders:
                    tes = self.tesselationEvaluationShaders[material.tessellationEvaluation] = GLMaterialBatch.Compile("assets/shaders/" + material.tessellationEvaluation + ".tes", GL.GL_TESS_EVALUATION_SHADER)
                else:
                    tes = self.tesselationEvaluationShaders[material.tessellationEvaluation]
            # 

            if (vertex, frag) in self.programs:
                self.materialPrograms[material] = self.programs[(vertex, frag)]
            else:
                glid = GL.glCreateProgram()
                GL.glAttachShader(glid, vertex)
                GL.glAttachShader(glid, frag)

                if material.useTessellation:
                    GL.glAttachShader(glid, tcs)
                    GL.glAttachShader(glid, tes)

                # Bind Std attributes
                for attrib, loc in GLStdVBO.AttributeLocations.items():
                    GL.glBindAttribLocation(glid, loc, attrib) 

                GL.glLinkProgram(glid)

                status = GL.glGetProgramiv(glid, GL.GL_LINK_STATUS)
                if not status:
                    print(GL.glGetProgramInfoLog(glid).decode("ascii"))
                    GL.glDeleteProgram(glid)
                else:
                    self.materialPrograms[material] = glid
        
        self.materialsToBake.clear()

    def BindProgram(self, material:Material):
        GL.glUseProgram(self.materialPrograms[material]) 

    def GetProgramID(self, material:Material):
        return self.materialPrograms[material]  

    def __del__(self):
        for vertex in self.vertexShaders.values():
            GL.glDeleteShader(vertex)

        for frag in self.fragmentShaders.values():
            GL.glDeleteShader(frag)

        for program in self.materialPrograms.values():
            GL.glDeleteProgram(program)

    
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