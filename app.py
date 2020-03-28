
#!/usr/bin/env python3
"""
3D Sea Application
"""

import glfw
import numpy as np

from sea3d.math import Vector3, Quaternion
from sea3d.core import Scene, SceneObject, Mesh, Material, Behaviour, Time
from sea3d.core.components import Camera, Renderer

from sea3d.opengl import GLWindow

class Rotator(Behaviour):

    def __init__(self, axis:Vector3, speed:float):
        super().__init__()
        self.axis = axis
        self.speed = speed

    def Update(self):
        self.object.transform._rotation *= Quaternion.AxisAngle(self.axis, self.speed * Time.deltaTime)
        self.object.transform.MarkForUpdate()

def main():
    window = GLWindow(width=800, height=600)
    window.Init()

    scene = Scene("Main Scene")

    camera = Camera(aspect=800/600)
    cameraObject = SceneObject("Camera 1")
    cameraObject.AddComponent(camera)
    cameraObject.transform.SetPosition(Vector3(0, 0, 1))

    # Triangle Mesh
    position = np.array(((0, .5, 0), (.5, -.5, 0), (-.5, -.5, 0), (0, -1.5, -.5)), 'f')
    normals = np.array(((0, 0, -1), (0.70710678118, 0, -0.70710678118), (-0.70710678118, 0, -0.70710678118), (0, 0, -1)), 'f')
    indexes = np.array(((0, 1, 2), (1, 2, 3)), 'u4')


    empty2 = SceneObject("Empty")
    empty2.transform.SetPosition(Vector3(-2, 0, -5))
    empty2.AddComponent(Rotator(Vector3(0, 1, 0), 60))
    empty2.AddComponent(Renderer(Mesh(position, normals, indexes), Material("UnlitRedMaterial", "base", "red")))

    empty1 = SceneObject("Empty")
    empty1.transform.SetPosition(Vector3(2, 0, -5))
    empty1.AddComponent(Rotator(Vector3(0, 1, 0), 30))
    empty1.AddComponent(Renderer(Mesh(position, normals, indexes), Material("UnlitBlueMaterial", "base", "blue")))

    scene.AddObject(cameraObject)
    scene.AddObject(empty1)
    scene.AddObject(empty2)

    # Material("BaseMaterial", "assets/shaders/base.vert", "assets/shaders/base.frag")


    window.AttachScene(scene)
    window.SetRenderingCamera(camera)

    window.Run()

if __name__ == '__main__':
    glfw.init() # Initialize window system glfw
    main()
    glfw.terminate() # destroy all graphics contexts

