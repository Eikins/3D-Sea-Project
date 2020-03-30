
#!/usr/bin/env python3
"""
3D Sea Application
"""

import glfw
import numpy as np

from sea3d.math import Vector3, Quaternion
from sea3d.core import Scene, SceneObject, Mesh, Material, Behaviour, Time, Texture, TextureWrapMode, TextureFilter
from sea3d.core.components import Camera, Renderer

from sea3d.opengl import GLWindow

class Rotator(Behaviour):

    def __init__(self, axis:Vector3, speed:float):
        super().__init__()
        self.axis = axis
        self.speed = speed

    def Start(self):
        self.renderer:Renderer = self.object.GetComponent(Renderer)

    def Update(self):
        self.object.transform._rotation *= Quaternion.AxisAngle(self.axis, self.speed * Time.deltaTime)
        self.object.transform.MarkForUpdate()
        self.renderer.properties.SetVector3("_Color", Vector3(1.0, 0.2, 0.2) * (np.sin(Time.time) * 0.5 + 0.5))


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

    # Define the Quad Mesh
    quad = Mesh(vertices = np.array(((-.5, -.5, 0), (.5, -.5, 0), (.5, .5, 0), (-.5, .5, 0)), 'f'),
                normals  = np.array(((0, 0, -1), (0, 0, -1), (0, 0, -1), (0, 0, -1)), 'f'),
                uvs = [np.array(((0, 1), (1, 1), (1, 0), (0, 0)), 'f')],
                indexes = np.array(((0, 1, 2), (0, 2, 3)), 'u4')
    )

    # Load the texture
    cobbleTexture = Texture.LoadFromFile("cobblestone.png")
    cobbleTexture.useMipmaps = False
    cobbleTexture.filter = TextureFilter.POINT

    moistTexture = Texture.LoadFromFile("cobblestone_moisture.png")
    moistTexture.useMipmaps = False
    moistTexture.filter = TextureFilter.POINT

    # Create Cobble Object
    cobble = SceneObject("Cobble")
    # Set Cobble transform
    cobble.transform.SetPosition(Vector3(-2, 0, -5))

    # Add Cobble Rotation over time component (Axis, Speed)
    cobble.AddComponent(Rotator(Vector3(0, 1, 0), 60))

    # Add Cobble Renderer component
    # Set the diffuse texture property (shader uniform name)
    cobbleRenderer = Renderer(quad, Material("UnlitTextured", "base", "unlit_textured"))
    cobbleRenderer.properties.SetTexture("_DiffuseMap", cobbleTexture)
    cobbleRenderer.properties.SetTexture("_MoistMap", moistTexture)
    cobbleRenderer.properties.SetVector3("_MoistColor", Vector3(0.0, 1.0, 0.0))
    cobble.AddComponent(cobbleRenderer)

    # Add cobble to the scene
    scene.AddObject(cobble)


    empty1 = SceneObject("Empty")
    empty1.transform.SetPosition(Vector3(2, 0, -5))
    empty1.AddComponent(Rotator(Vector3(1, 1, 0), 30))
    re1 = Renderer(Mesh(position, normals, None, indexes), Material("UnlitRedMaterial", "base", "color"))
    #re1.properties.SetFloat("_Atten", 0.0)
    re1.properties.SetVector3("_Color", Vector3(1.0, 0.2, 0.2))
    empty1.AddComponent(re1)

    scene.AddObject(cameraObject)
    scene.AddObject(empty1)


    window.AttachScene(scene)
    window.SetRenderingCamera(camera)

    window.Run()

if __name__ == '__main__':
    glfw.init() # Initialize window system glfw
    main()
    glfw.terminate() # destroy all graphics contexts

