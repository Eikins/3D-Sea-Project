"""
OpenGL Window stuff
@author: Eikins
"""

import OpenGL.GL as GL
import glfw    
import numpy as np

from sea3d.core import Scene, Time, Material, PropertyBlock
from sea3d.core.components import Camera, Renderer
from sea3d.math import Vector3, Quaternion, Matrix4

from sea3d.opengl import GLStdVBO, GLMaterialBatch, GLTextureAtlas

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


    def OnKey(self, _win, key, _scancode, action, _mods):
        if action == glfw.PRESS or action == glfw.REPEAT:
            if key == glfw.KEY_ESCAPE or key == glfw.KEY_Q:
                glfw.set_window_should_close(self.window, True)

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
                self.materialBatch.AddMaterial(renderer.material)
                vertexArray = GLStdVBO(renderer.mesh)
                vertexArray.Init()
                self.renderers += [(vertexArray, renderer)]

        while not glfw.window_should_close(self.window):

            GL.glClear(GL.GL_COLOR_BUFFER_BIT)

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

    def _Draw_(self):

        _Projection = self.camera.GetProjectionMatrix()
        _View = np.linalg.inv(self.camera.object.transform.GetTRSMatrix())
        _ProjectionView = _Projection @ _View

        # Draw Scene
        for vbo, renderer in self.renderers:
            
            glid = self.materialBatch.GetProgramID(renderer.material)

            GL.glUseProgram(glid)
            _ProjViewPTR = GL.glGetUniformLocation(glid, "_ProjectionViewMatrix")
            _ModelPTR = GL.glGetUniformLocation(glid, "_ModelMatrix")

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
                GL.glBindTexture(GL.GL_TEXTURE_2D, self.textureAtlas.textures[tex])
                loc = GL.glGetUniformLocation(glid, name)
                GL.glUniform1i(loc, index)

            GL.glUniformMatrix4fv(_ProjViewPTR, 1, True, _ProjectionView)
            GL.glUniformMatrix4fv(_ModelPTR, 1, True, renderer.object.transform.GetTRSMatrix())

            vbo.Draw()
        
        GL.glBindVertexArray(0)

