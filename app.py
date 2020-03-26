
#!/usr/bin/env python3
"""
3D Sea Application
"""

import glfw
import numpy as np

from sea3d.math import Vector3
from sea3d.core import Scene, SceneObject
from sea3d.core.components import Camera

from sea3d.opengl import GLWindow

def main():
    window = GLWindow()
    window.Init()

    scene = Scene("Main Scene")

    camera = Camera()
    cameraObject = SceneObject("Camera 1")
    cameraObject.AddComponent(camera)
    cameraObject.transform.SetPosition(Vector3(0, 0, 0))

    scene.AddObject(cameraObject)
    scene.AddObject(SceneObject("Empty"))

    window.AttachScene(scene)
    window.SetRenderingCamera(camera)

    window.Run()

if __name__ == '__main__':
    glfw.init() # Initialize window system glfw
    main()
    glfw.terminate() # destroy all graphics contexts

