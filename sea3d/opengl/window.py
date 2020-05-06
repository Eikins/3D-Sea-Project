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

        self.mode = cycle([(GL.GL_LINE, False), (GL.GL_FILL, True)])

    def OnKey(self, _win, key, _scancode, action, _mods):

        if action == glfw.PRESS:
            if key == glfw.KEY_Y:
                mode = next(self.mode)
                GL.glPolygonMode(GL.GL_FRONT_AND_BACK, mode[0])
                self.pipeline.postProcess = mode[1]

        if action == glfw.PRESS or action == glfw.REPEAT:
            if key == glfw.KEY_ESCAPE or key == glfw.KEY_Q:
                glfw.set_window_should_close(self.window, True)

            movement = None
            rotate = None

            moveSpeed = 10
            rotateSpeed = 360

            if key == glfw.KEY_LEFT:
                movement = self.camera.object.transform._rotation.RightVector() * -1

            if key == glfw.KEY_RIGHT:
                movement = self.camera.object.transform._rotation.RightVector()

            if key == glfw.KEY_UP:
                movement = self.camera.object.transform._rotation.ForwardVector()

            if key == glfw.KEY_DOWN:
                movement = self.camera.object.transform._rotation.ForwardVector() * -1

            if key == glfw.KEY_SPACE:
                movement = self.camera.object.transform._rotation.UpVector()

            if key == glfw.KEY_LEFT_SHIFT:
                movement = self.camera.object.transform._rotation.UpVector() * -1

            if key == glfw.KEY_R:
                rotate = Quaternion.AxisAngle(Vector3(0, 1, 0), rotateSpeed * Time.deltaTime)

            if key == glfw.KEY_T:
                rotate = Quaternion.AxisAngle(Vector3(0, 1, 0), -rotateSpeed * Time.deltaTime)

            if key == glfw.KEY_U:
                rotate = Quaternion.AxisAngle(Vector3(1, 0, 0), rotateSpeed * Time.deltaTime)

            if key == glfw.KEY_J:
                rotate = Quaternion.AxisAngle(Vector3(1, 0, 0), -rotateSpeed * Time.deltaTime)

            if movement:
                self.camera.object.transform._position += movement * moveSpeed * Time.deltaTime
                self.camera.object.transform.MarkForUpdate()

            if rotate:
                self.camera.object.transform._rotation *= rotate
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