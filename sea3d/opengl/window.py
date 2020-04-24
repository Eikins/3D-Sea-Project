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

        self.mode = cycle([GL.GL_LINE, GL.GL_FILL])

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

        pipeline = GLRenderPipeline(self.scene, self.camera, self.width, self.height)
        pipeline.Init()

        while not glfw.window_should_close(self.window):

            pipeline.Execute()

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
