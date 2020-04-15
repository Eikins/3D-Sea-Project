"""
OpenGL Window stuff
@author: Eikins
"""

import time as pythonTime

import OpenGL.GL as GL
import glfw    
import numpy as np

from itertools import cycle;

from sea3d.core import Scene, Time, Material, PropertyBlock, Layers
from sea3d.core.components import Camera, Renderer
from sea3d.math import Vector3, Quaternion, Matrix4

from sea3d.opengl import GLStdVBO, GLMaterialBatch, GLTextureAtlas, GLSkybox

from sea3d.core import Mesh

class GLWindow:

    def __init__(self, width:int = 800, height:int = 600):
        self.width:int = width
        self.height:int = height
        self.window = None
        self.scene:Scene = None
        self.camera:Camera = None
        self.materialBatch = GLMaterialBatch()
        self.textureAtlas = GLTextureAtlas()
        self.renderers = []
        self.skybox = GLSkybox()

    def Init(self):
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL.GL_TRUE)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        glfw.window_hint(glfw.RESIZABLE, False)
        self.window = glfw.create_window(self.width, self.height, '3D Sea', None, None)

        # make win's OpenGL context current; no OpenGL calls can happen before
        glfw.make_context_current(self.window)

        # register event handlers
        glfw.set_key_callback(self.window, self.OnKey)

        # useful message to check OpenGL renderer characteristics
        print('OpenGL', GL.glGetString(GL.GL_VERSION).decode() + ', GLSL',
              GL.glGetString(GL.GL_SHADING_LANGUAGE_VERSION).decode() +
              ', Renderer', GL.glGetString(GL.GL_RENDERER).decode())

        # initialize GL by setting viewport and default render characteristics
        GL.glClearColor(0.1, 0.1, 0.1, 0.1)
        # Left handed coordinate system, invert Depth Range
        GL.glDepthRange(1.0, 0.0)
        GL.glEnable(GL.GL_DEPTH_TEST) 
        GL.glDepthFunc(GL.GL_LESS)
        GL.glEnable(GL.GL_CULL_FACE)
        GL.glCullFace(GL.GL_BACK)

        self.mode = cycle([GL.GL_LINE, GL.GL_FILL])

        # GL.glPatchParameteri(GL.GL_PATCH_VERTICES, 3)

    def OnKey(self, _win, key, _scancode, action, _mods):

        if action == glfw.PRESS:
            if key == glfw.KEY_Y:
                GL.glPolygonMode(GL.GL_FRONT_AND_BACK, next(self.mode))

        if action == glfw.PRESS or action == glfw.REPEAT:
            if key == glfw.KEY_ESCAPE or key == glfw.KEY_Q:
                glfw.set_window_should_close(self.window, True)

            if key == glfw.KEY_LEFT:
                self.camera.object.transform._position += -1 * Vector3(1, 0, 0) * 5 * Time.deltaTime
                self.camera.object.transform.MarkForUpdate()

            if key == glfw.KEY_RIGHT:
                self.camera.object.transform._position += Vector3(1, 0, 0) * 5 * Time.deltaTime
                self.camera.object.transform.MarkForUpdate()

            if key == glfw.KEY_UP:
                self.camera.object.transform._position += Vector3(0, 0, 1) * 5 * Time.deltaTime
                self.camera.object.transform.MarkForUpdate()

            if key == glfw.KEY_DOWN:
                self.camera.object.transform._position += -1 * Vector3(0, 0, 1) * 5 * Time.deltaTime
                self.camera.object.transform.MarkForUpdate()

            if key == glfw.KEY_SPACE:
                self.camera.object.transform._position += Vector3(0, 1, 0) * 5 * Time.deltaTime
                self.camera.object.transform.MarkForUpdate()

            if key == glfw.KEY_LEFT_SHIFT:
                self.camera.object.transform._position += -1 * Vector3(0, 1, 0) * 5 * Time.deltaTime
                self.camera.object.transform.MarkForUpdate()

            if key == glfw.KEY_R:
                self.camera.object.transform._rotation *= Quaternion.AxisAngle(Vector3(0, 1, 0), 60 * Time.deltaTime)
                self.camera.object.transform.MarkForUpdate()

            if key == glfw.KEY_T:
                self.camera.object.transform._rotation *= Quaternion.AxisAngle(Vector3(0, 1, 0), -60 * Time.deltaTime)
                self.camera.object.transform.MarkForUpdate()

            if key == glfw.KEY_U:
                self.camera.object.transform._rotation *= Quaternion.AxisAngle(Vector3(1, 0, 0), -60 * Time.deltaTime)
                self.camera.object.transform.MarkForUpdate()

            if key == glfw.KEY_J:
                self.camera.object.transform._rotation *= Quaternion.AxisAngle(Vector3(1, 0, 0), 60 * Time.deltaTime)
                self.camera.object.transform.MarkForUpdate()


    def AttachScene(self, scene:Scene):
        glfw.set_window_title(self.window, scene.name)
        self.scene = scene

    def SetRenderingCamera(self, camera:Camera):
        self.camera = camera

    def Run(self):
        """ Main render loop for this OpenGL Window """
        glfw.set_time(0.0)
        lastFrameTime = glfw.get_time()
        self.scene.Start()

        # Initialize Material Batch
        for renderer in self.scene.GetAllComponents():
            if isinstance(renderer, Renderer):
                if renderer.object.layer & self.camera._renderingLayer:
                    self.materialBatch.AddMaterial(renderer.material)
                    vertexArray = GLStdVBO(renderer.mesh)
                    if (renderer.material.useTessellation):
                        vertexArray.primitive = GL.GL_PATCHES
                    vertexArray.Init()
                    self.renderers += [(vertexArray, renderer)]

        self.skyboxMaterial = Material("Skybox", "skybox", "skybox")
        self.materialBatch.AddMaterial(self.skyboxMaterial)
        self.skybox.Init()

        while not glfw.window_should_close(self.window):

            GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

            self.materialBatch.BakeMaterials()
            self.textureAtlas.BakeTextures()

            self.scene.Update()

            self._Draw_()

            # Flush render commands, and swap buffers
            glfw.swap_buffers(self.window)

            # Poll for and process events
            glfw.poll_events()

            # Update Delta Time
            Time.time = glfw.get_time()
            Time.deltaTime = Time.time - lastFrameTime
            lastFrameTime = Time.time

            if (Time.deltaTime < 1.0 / 60.0):
                pythonTime.sleep (1.0 / 60.0 - Time.deltaTime)
                Time.deltaTime = 1.0 / 60.0
                Time.time = glfw.get_time()

    def _Draw_(self):

        _Projection = self.camera.GetProjectionMatrix()
        _View = np.linalg.inv(self.camera.object.transform.GetTRSMatrix())
        _ViewPos = self.camera.object.transform._position

        # Draw Scene
        for vbo, renderer in self.renderers:
            
            glid = self.materialBatch.GetProgramID(renderer.material)

            GL.glUseProgram(glid)
            _ViewPTR = GL.glGetUniformLocation(glid, "_ViewMatrix")
            _ProjPTR = GL.glGetUniformLocation(glid, "_ProjectionMatrix")
            _ModelPTR = GL.glGetUniformLocation(glid, "_ModelMatrix")
            _ViewPosPTR = GL.glGetUniformLocation(glid, "_ViewPos")
            _TimePTR = GL.glGetUniformLocation(glid, "_Time")   
            _LightPosPTR = GL.glGetUniformLocation(glid, "_LightPos")

            GL.glUniformMatrix4fv(_ViewPTR, 1, True, _View)
            GL.glUniformMatrix4fv(_ProjPTR, 1, True, _Projection)
            GL.glUniformMatrix4fv(_ModelPTR, 1, True, renderer.object.transform.GetTRSMatrix())
            GL.glUniform3f(_ViewPosPTR, _ViewPos.x, _ViewPos.y, _ViewPos.z)
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

            if renderer.object.layer & Layers.TRANSPARENT:
                GL.glEnable(GL.GL_BLEND)
                GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
                vbo.Draw()
                GL.glDisable(GL.GL_BLEND)
            else:
                vbo.Draw()

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

            GL.glUniformMatrix4fv(_ViewPTR, 1, True, _View)
            GL.glUniformMatrix4fv(_ProjPTR, 1, True, _Projection)

            loc = GL.glGetUniformLocation(glid, "_Skybox")
            GL.glUniform1i(loc, 0)
            self.skybox.Draw()
        
        GL.glBindVertexArray(0)

