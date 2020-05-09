"""
OpenGL Render Pipeline
@author: Eikins
"""

import OpenGL.GL as GL
import glfw    
import numpy as np
import heapq

from itertools import cycle

from PIL import Image  

from sea3d.core import Scene, Time, Material, PropertyBlock, Layers, Mesh
from sea3d.core.components import Camera, Renderer
from sea3d.math import Vector3, Quaternion, Matrix4

from sea3d.opengl import GLStdVBO, GLMaterialBatch, GLTextureAtlas, GLSkybox, GLFramebuffer

class GLRenderPipeline:

    def __init__(self, scene:Scene, camera:Camera, width:int, height:int):
        self.scene = scene
        self.camera = camera
        self.materialBatch = GLMaterialBatch()
        self.textureAtlas = GLTextureAtlas()
        self.skybox = GLSkybox()
        self.renderers = dict()
        self.width = width
        self.height = height
        self.framebuffer = None
        self.postProcess = True

    def Init(self):
        # initialize GL by setting viewport and default render characteristics
        GL.glClearColor(0.1, 0.1, 0.1, 0.1)
        # Left handed coordinate system, invert Depth Range
        GL.glDepthRange(1.0, 0.0)
        GL.glEnable(GL.GL_DEPTH_TEST) 
        GL.glDepthFunc(GL.GL_LESS)
        GL.glEnable(GL.GL_CULL_FACE)
        GL.glCullFace(GL.GL_BACK)

        self.framebuffer = GLFramebuffer(self.width, self.height, "post")
        self.framebuffer.Init()

        # Initialize Material Batch
        for renderer in self.scene.GetAllComponents():
            if isinstance(renderer, Renderer):
                self.materialBatch.AddMaterial(renderer.material)
                vertexArray = GLStdVBO(renderer.mesh)
                if (renderer.material.useTessellation):
                    vertexArray.primitive = GL.GL_PATCHES
                vertexArray.Init()
                self.renderers.setdefault(renderer.object.layer, []).append((vertexArray, renderer))

        # TODO : Change to dynamic sorted list
        # Sort renderers
        for renderers in self.renderers.values():
            renderers.sort(key = lambda r : r[1].material.orderInQueue)
            # print(layer)
            # for r in renderers:
            #    print(r[1].material.name + ":",r[1].material.orderInQueue)

        self.skyboxMaterial = Material("Skybox", "skybox", "skybox")
        self.materialBatch.AddMaterial(self.skyboxMaterial)
        self.skybox.Init()

        if self.camera._skybox is not None:
            if self.camera._skybox not in self.textureAtlas.textures:
                self.textureAtlas.AddTexture(self.camera._skybox)
                self.textureAtlas.BakeTextures()

        self.scene.Start()

    def Execute(self):

        self.materialBatch.BakeMaterials()
        self.textureAtlas.BakeTextures()

        self.scene.Update()

        self._Projection = self.camera.GetProjectionMatrix()
        self._View = np.linalg.inv(self.camera.object.transform.GetTRSMatrix())
        self._ViewPos = self.camera.object.transform._position

        if self.postProcess:
            self.framebuffer.Bind()
        self.DrawFrame()
        if self.postProcess:
            self.framebuffer.Unbind()
            props = PropertyBlock()
            props.SetVector3("_ViewPos", self._ViewPos)
            props.SetFloat("_Time", Time.time)   
            self.framebuffer.Draw(props)

    def DrawFrame(self):
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        GL.glEnable(GL.GL_DEPTH_TEST)
        for layer in self.renderers.keys():
            if layer & self.camera._renderingLayer:
                self.DrawLayer(layer)
        self.DrawSkybox()


    def DrawLayer(self, layer:Layers):
        # In case of transparent & water layers, we need to activate color blending
        if layer & (Layers.TRANSPARENT | Layers.WATER):
            GL.glEnable(GL.GL_BLEND)

            GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)

        # Draw Scene
        for vbo, renderer in self.renderers[layer]:

            if renderer.material.renderBothFaces:
                # We want to render water both sides, so disable face culling
                GL.glDisable(GL.GL_CULL_FACE)
            
            glid = self.materialBatch.GetProgramID(renderer.material)

            GL.glUseProgram(glid)
            _ViewPTR = GL.glGetUniformLocation(glid, "_ViewMatrix")
            _ProjPTR = GL.glGetUniformLocation(glid, "_ProjectionMatrix")
            _ModelPTR = GL.glGetUniformLocation(glid, "_ModelMatrix")
            _ViewPosPTR = GL.glGetUniformLocation(glid, "_ViewPos")
            _TimePTR = GL.glGetUniformLocation(glid, "_Time")   
            _LightPosPTR = GL.glGetUniformLocation(glid, "_LightPos")

            GL.glUniformMatrix4fv(_ViewPTR, 1, True, self._View)
            GL.glUniformMatrix4fv(_ProjPTR, 1, True, self._Projection)
            GL.glUniformMatrix4fv(_ModelPTR, 1, True, renderer.object.transform.GetTRSMatrix())
            GL.glUniform3f(_ViewPosPTR, self._ViewPos.x, self._ViewPos.y, self._ViewPos.z)
            GL.glUniform1f(_TimePTR, Time.time)
 
            # Bind Properties
            props:PropertyBlock = renderer.properties
            for name, value in props.floatProperties.items():
                loc = GL.glGetUniformLocation(glid, name)
                GL.glUniform1f(loc, value)

            for name, value in props.intProperties.items():
                loc = GL.glGetUniformLocation(glid, name)
                GL.glUniform1i(loc, value)
        
            for name, value in props.vec3Properties.items():
                loc = GL.glGetUniformLocation(glid, name)
                GL.glUniform3f(loc, value.x, value.y, value.z)

            for index, (name, tex) in enumerate(props.textures.items()):
                if tex not in self.textureAtlas.textures:
                    self.textureAtlas.AddTexture(tex)
                    self.textureAtlas.BakeTextures()
                GL.glActiveTexture(GL.GL_TEXTURE0 + index)
                if tex.isCubemap:
                    GL.glBindTexture(GL.GL_TEXTURE_CUBE_MAP, self.textureAtlas.textures[tex])
                else:
                    GL.glBindTexture(GL.GL_TEXTURE_2D, self.textureAtlas.textures[tex])
                loc = GL.glGetUniformLocation(glid, name)
                GL.glUniform1i(loc, index)

            vbo.Draw()

            if renderer.material.renderBothFaces:
                # Reset OpenGL State
                GL.glDisable(GL.GL_CULL_FACE)

        # Reset OpenGL states
        if layer & (Layers.TRANSPARENT | Layers.WATER):
            GL.glDisable(GL.GL_BLEND)

    def DrawSkybox(self):
        # Draw skybox at the end (avoiding fragment shader overhead)
        if self.camera._skybox is not None:
            if self.camera._skybox not in self.textureAtlas.textures:
                self.textureAtlas.AddTexture(self.camera._skybox)
                self.textureAtlas.BakeTextures()
            glid = self.materialBatch.GetProgramID(self.skyboxMaterial)
            GL.glUseProgram(glid)
            GL.glActiveTexture(GL.GL_TEXTURE0)
            GL.glBindTexture(GL.GL_TEXTURE_CUBE_MAP, self.textureAtlas.textures[self.camera._skybox])

            _ViewPTR = GL.glGetUniformLocation(glid, "_ViewMatrix")
            _ProjPTR = GL.glGetUniformLocation(glid, "_ProjectionMatrix")

            GL.glUniformMatrix4fv(_ViewPTR, 1, True, self._View)
            GL.glUniformMatrix4fv(_ProjPTR, 1, True, self._Projection)

            loc = GL.glGetUniformLocation(glid, "_Skybox")
            GL.glUniform1i(loc, 0)
            self.skybox.Draw()

    def FrameBufferToFile(self):   
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.framebuffer.texture)
        data = GL.glGetTexImage(GL.GL_TEXTURE_2D, 0, GL.GL_RGBA, GL.GL_UNSIGNED_BYTE)
        img = Image.fromarray(np.reshape(np.fromstring(data, np.uint8), (self.height, self.width, 4)))
        img.save("framebuffer.png", "PNG")