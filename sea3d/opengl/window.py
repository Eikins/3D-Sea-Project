"""
OpenGL Window stuff
@author: Eikins
"""

import time as pythonTime

import OpenGL.GL as GL
import glfw    
import numpy as np

from itertools import cycle

from sea3d.core import Scene, Time, Material, PropertyBlock, Layers
from sea3d.core.components import Camera, Renderer
from sea3d.math import Vector3, Quaternion, Matrix4

from sea3d.opengl import GLStdVBO, GLMaterialBatch, GLTextureAtlas, GLSkybox, GLRenderPipeline

from sea3d.core import Mesh

class GLWindow:

    def __init__(self, width:int = 800, height:int = 600):
        self.width:int = width
        self.height:int = height
        self.window = None
        self.scene:Scene = None
        self.camera:Camera = None
        self.key_handlers = []
        self.mouse_handlers = []

    def Init(self):
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL.GL_TRUE)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        glfw.window_hint(glfw.RESIZABLE, False)
        self.window = glfw.create_window(self.width, self.height, '3D Sea', None, None)

        # make win's OpenGL context current; no OpenGL calls can happen before
        glfw.make_context_current(self.window)

        # Cursor Lock mode
        glfw.set_input_mode(self.window, glfw.CURSOR, glfw.CURSOR_DISABLED)

        # register event handlers
        glfw.set_key_callback(self.window, self.OnKey)
        glfw.set_cursor_pos_callback(self.window, self.OnMouse)

        # useful message to check OpenGL renderer characteristics
        print('OpenGL', GL.glGetString(GL.GL_VERSION).decode() + ', GLSL',
              GL.glGetString(GL.GL_SHADING_LANGUAGE_VERSION).decode() +
              ', Renderer', GL.glGetString(GL.GL_RENDERER).decode())

        # Y Key allows to swap between line and fill mode, the second arg is wether the post
        # process is enabled
        self.mode = cycle([GL.GL_LINE, GL.GL_FILL])

    def OnMouse(self, _win, x, y):
        # Normalized pos
        nx =  2 * (x / self.width) - 1
        ny = 2 * (y / self.height) - 1
        for handler in self.mouse_handlers:
            handler(nx, ny)
                

    def OnKey(self, _win, key, _scancode, action, _mods):

        for handler in self.key_handlers:
            handler(key, _scancode, action, _mods)

        if action == glfw.PRESS:
            if key == glfw.KEY_Y:
                mode = next(self.mode)
                GL.glPolygonMode(GL.GL_FRONT_AND_BACK, mode)

            if key == glfw.KEY_H:
                self.pipeline.postProcess = not self.pipeline.postProcess

        if action == glfw.PRESS or action == glfw.REPEAT:
            if key == glfw.KEY_ESCAPE:
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

        self.pipeline = GLRenderPipeline(self.scene, self.camera, self.width, self.height)
        self.pipeline.Init()

        while not glfw.window_should_close(self.window):

            self.pipeline.Execute()

            # Flush render commands, and swap buffers
            glfw.swap_buffers(self.window)

            # Update Delta Time
            Time.time = glfw.get_time()
            Time.deltaTime = Time.time - lastFrameTime
            lastFrameTime = Time.time

            # Poll for and process events
            glfw.poll_events()