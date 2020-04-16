
#!/usr/bin/env python3
"""
3D Sea Application
"""

import glfw
import numpy as np

from sea3d.math import Vector3, Quaternion
from sea3d.core import Scene, SceneObject, Mesh, Material, Behaviour, Time, Texture, TextureWrapMode, TextureFilter, Layers
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
        # self.renderer.properties.SetVector3("_Color", Vector3(1.0, 0.2, 0.2) * (np.sin(Time.time) * 0.5 + 0.5))


def GeneratePlane(size = (10, 10), count = (2, 2), repeat_uv = False):
    w, h = size
    cx, cz = count
    cx += 1
    cz += 1
    X = np.linspace(-w / 2, w / 2, num = cx)
    Z = np.linspace(-h / 2, h / 2, num = cz)

    XX, ZZ = np.meshgrid(X, Z)

    XX = XX.reshape(-1, 1)
    ZZ = ZZ.reshape(-1, 1)
    YY = np.zeros_like(XX)

    vertices = np.concatenate((XX, YY, ZZ), axis=1)

    uvs = np.empty((len(vertices), 2), dtype = np.float32)
    uvs[:, 0] = 0.5 + vertices[:, 0] / w
    uvs[:, 1] = 0.5 + vertices[:, 2] / h

    if repeat_uv:
        uvs[:, 0] = (uvs[:, 0] - 0.5) * (cx - 1) 
        uvs[:, 1] = (uvs[:, 1] - 0.5) * (cz - 1) 
    indexes = []

    for z in range(0, cz - 1):
        for x in range(0, cx - 1):
            tri = z * cx + x
            indexes += [
                (tri, tri + 1, tri + 1 + cx),
                (tri, tri + 1 + cx, tri + cx)]

    normals = np.array([(0, 1, 0)] * len(vertices), dtype = np.float32)
    tangeants = np.array([(1, 0, 0)] * len(vertices), dtype = np.float32)
    indexes = np.array(indexes, 'u4')

    return Mesh(vertices, normals, [uvs], indexes, tangeants)


def main():
    window = GLWindow(width=1600, height=900)
    window.Init()

    scene = Scene("Main Scene")

    camera = Camera(aspect=1600/900, far=1000)
    skyboxTex = Texture.LoadFromFile("cubemaps/skybox", loadAsCubemap=True, fileExtension=".png")
    skyboxTex.wrapMode = TextureWrapMode.CLAMP_TO_EDGE
    camera._skybox = skyboxTex

    cameraObject = SceneObject("Camera 1")
    cameraObject.AddComponent(camera)
    cameraObject.transform.SetPosition(Vector3(0, 0, 0))

    plane = GeneratePlane((500, 500), (250, 250))
    # plane.vertices[:, 1] += np.random.normal(size=(len(plane.vertices))) / 40
    
    bunnyModel = Mesh.LoadFromFile("bunny.obj")[0]
    boxModel = Mesh.LoadFromFile("cube.obj")[0]
    fishModel = Mesh.LoadFromFile("TropicalFish01.obj")[0]

    bunnyTex = Texture.LoadFromFile("bunny.png")
    bunnyTexNormal = Texture.LoadFromFile("bunny_normal.png")
    boxTex = Texture.LoadFromFile("cube.png")
    boxTexNormal = Texture.LoadFromFile("normal.png")
    fishTex = Texture.LoadFromFile("TropicalFish01.jpg")
    fishTexNormal = Texture.LoadFromFile("TropicalFish01_NormalMap.jpg")

    waterNoise = Texture.LoadFromFile("noise/water.jpg")
    terrainHeightMap = Texture.LoadFromFile("terrain/heightmap.png")
    terrainNormalMap = Texture.LoadFromFile("terrain/normal.png")

    waterMaterial = Material("WaterMaterial", "water", "water")
    waterMaterial.AddTessellation("water", "water")
    waterPlane = SceneObject("Water")
    waterPlane.layer = Layers.TRANSPARENT
    waterPlane.transform.SetPosition(Vector3(0, 5, 0))
    waterPlane.AddComponent(Renderer(plane, waterMaterial))
    waterPlane.GetComponent(Renderer).properties.SetTexture("_Noise", waterNoise)
    waterPlane.GetComponent(Renderer).properties.SetTexture("_Skybox", skyboxTex)

    terrainMaterial = Material("TerrainMaterial", "terrain", "terrain")
    terrainMaterial.AddTessellation("terrain", "terrain")
    terrain = SceneObject("Terrain")
    terrain.transform.SetPosition(Vector3(0, -8, 0))
    terrain.AddComponent(Renderer(plane, terrainMaterial))
    terrain.GetComponent(Renderer).properties.SetTexture("_HeightMap", terrainHeightMap)
    terrain.GetComponent(Renderer).properties.SetTexture("_NormalMap", terrainNormalMap)

    box = SceneObject("Box")
    box.transform.SetPosition(Vector3(-1, -1, -1))
    box.transform.SetRotation(Quaternion.Eulerf(5, 0, -5))
    box.transform.SetScale(Vector3(1, 1, 1) * 0.5)

    boxRenderer = Renderer(boxModel, Material("Standard", "std_pbr", "std_pbr"))
    box.AddComponent(boxRenderer)
    boxRenderer.properties.SetTexture("_AlbedoMap", boxTex)
    boxRenderer.properties.SetTexture("_NormalMap", boxTexNormal)
    boxRenderer.properties.SetFloat("_Shininess", 16.0)
    box.AddComponent(Rotator(Vector3(0, 1, 0), 30))

    bunny = SceneObject("Bunny", box.transform)
    bunny.transform.SetPosition(Vector3(0, 1, 0))
    bunny.transform.SetRotation(Quaternion.Eulerf(0, 180, 0))
    bunny.AddComponent(Renderer(bunnyModel, Material("Standard", "std_pbr", "std_pbr")))
    bunny.GetComponent(Renderer).properties.SetTexture("_AlbedoMap", bunnyTex)
    bunny.GetComponent(Renderer).properties.SetTexture("_NormalMap", bunnyTexNormal)
    bunny.GetComponent(Renderer).properties.SetFloat("_Shininess", 1.0)
    bunny.GetComponent(Renderer).properties.SetFloat("_Emission", 0.3)
    bunny.GetComponent(Renderer).properties.SetFloat("_Diffusion", 0.4)

    fish = SceneObject("Fish")
    fish.transform.SetPosition(Vector3(3, -3, 3))
    fish.transform.SetRotation(Quaternion.Eulerf(0, 75, 0))
    fish.transform.SetScale(Vector3(1, 1, 1) * 0.002)
    fish.AddComponent(Renderer(fishModel, Material("Standard", "std_pbr", "std_pbr")))
    fish.GetComponent(Renderer).properties.SetTexture("_AlbedoMap", fishTex)
    fish.GetComponent(Renderer).properties.SetTexture("_NormalMap", fishTexNormal)
    fish.GetComponent(Renderer).properties.SetFloat("_Shininess", 16.0)

    # Add to scene
    scene.AddObject(terrain)
    scene.AddObject(bunny)
    scene.AddObject(fish)
    scene.AddObject(box)
    scene.AddObject(waterPlane)


    camera.object.transform.SetPosition(Vector3(0, 0, -3))
    camera.object.transform.SetRotation(Quaternion.Eulerf(0, 0, 0))

    window.AttachScene(scene)
    window.SetRenderingCamera(camera)

    window.Run()

if __name__ == '__main__':
    glfw.init() # Initialize window system glfw
    main()
    glfw.terminate() # destroy all graphics contexts

