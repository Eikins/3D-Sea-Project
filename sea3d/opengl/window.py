"""
OpenGL Window stuff
@author: Eikins
"""

import OpenGL.GL as GL
import glfw    
import numpy as np

from sea3d.core.scene import Scene
from sea3d.core.components.camera import Camera

from sea3d.math.quaternion import Quaternion
from sea3d.math.vector3 import Vector3

class GLWindow:

    def __init__(self, width:int = 800, height:int = 600):
        self.width = width
        self.height = height
        self.window = None
        self.scene = None
        self.camera = None

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

        # initially empty list of object to draw
        self.drawables = []

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
        self.scene.Start()
    
        while not glfw.window_should_close(self.window):

            GL.glClear(GL.GL_COLOR_BUFFER_BIT)

            ## TODO : Draw Scene

            t = self.camera.object.transform
            # t.SetRotation(t._rotation * Quaternion.AxisAngle(Vector3(0, 1, 0), 0.1))
            t._rotation *= Quaternion.AxisAngle(Vector3(0, 1, 0), 0.025)
            t.MarkForUpdate()


            _Projection = self.camera.GetProjectionMatrix()
            _View = self.camera.object.transform.GetTRSMatrix()
            _ProjectionView = _Projection @ _View

            # Debug
            position = _View @ np.array([0, 0, 1, 1])

            GL.glClearColor(position[0], position[1], position[2], 1.0)

            # Flush render commands, and swap buffers
            glfw.swap_buffers(self.window)

            # Poll for and process events
            glfw.poll_events()