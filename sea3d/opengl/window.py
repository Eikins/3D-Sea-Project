"""
OpenGL Window stuff
@author: Eikins
"""

import OpenGL.GL as GL
import glfw    
import numpy as np

from sea3d.core import Scene, Time
from sea3d.core.components import Camera
from sea3d.math import Vector3, Quaternion, Matrix4


from sea3d.opengl import GLVertexArray, GLMaterial

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

        # initialize GL by setting viewport and default render characteristics
        GL.glClearColor(0.1, 0.1, 0.1, 0.1)

        # ======================================= DEBUG =====================================================
        position = np.array(((0, .5, 0), (.5, -.5, 0), (-.5, -.5, 0)), 'f')
        normals = np.array(((0, 0, -1), (0.70710678118, 0, -0.70710678118), (-0.70710678118, 0, -0.70710678118)), 'f')
        indexes = np.array((0, 1, 2), 'u4')

        triangle = GLVertexArray(Mesh(position, normals, indexes))
        triangle.Init()
        self.vertexArrays = [triangle]
        self.material:GLMaterial = GLMaterial("BaseMaterial", "assets/shaders/base.vert", "assets/shaders/base.frag")
        self.material.Init()

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

        while not glfw.window_should_close(self.window):

            GL.glClear(GL.GL_COLOR_BUFFER_BIT)

            self.scene.Update()


            ##### Example of Update Usage
            ## Rotate around Y at 60° / second
            self.camera.object.transform._rotation *= Quaternion.AxisAngle(Vector3(0, 1, 0), 2 * 51.4285714286 * Time.deltaTime)
            ## Mark transform for update, this mean recomputation of the model matrix for the next frame
            self.camera.object.transform.MarkForUpdate() 
            ## Ping-pong translation along X
            # self.camera.object.transform.SetPosition(Vector3(0, 0, 1) + Vector3(1, 0, 0) * np.sin(Time.time * 2))


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
        _Model = Matrix4.Identity()

        # Draw Scene
        GL.glUseProgram(self.material.glid)
        for vertexArray in self.vertexArrays:

            _ProjViewPTR = GL.glGetUniformLocation(self.material.glid, "_ProjectionViewMatrix")
            _ModelPTR = GL.glGetUniformLocation(self.material.glid, "_ModelMatrix")

            GL.glUniformMatrix4fv(_ProjViewPTR, 1, True, _ProjectionView)
            GL.glUniformMatrix4fv(_ModelPTR, 1, True, _Model)

            vertexArray.Draw()
        
        GL.glBindVertexArray(0)

