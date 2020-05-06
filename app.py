
#!/usr/bin/env python3
"""
3D Sea Application
"""

import glfw
import numpy as np

from sea3d.math import Vector3, Quaternion
from sea3d.core import Scene, SceneObject, Mesh, Material, Behaviour, Time, Texture, TextureWrapMode, TextureFilter, Layers, KeyFrames, Animation
from sea3d.core.components import Camera, Renderer, Animator

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

class Fornicator(Behaviour):

    def __init__(self, axis:Vector3, angle:float, speed:float):
        super().__init__()
        self.axis = axis
        self.speed = speed
        self.angle = angle


    def Start(self):
        self.baseRotation = self.object.transform._rotation

    def Update(self):
        self.object.transform._rotation = self.baseRotation * Quaternion.AxisAngle(self.axis, np.sin(self.speed * Time.time) * self.angle)
        self.object.transform.MarkForUpdate()



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

    plane = GeneratePlane((500, 500), (250, 250))

    # DEFAULT
    defaultAlbedo = Texture.LoadFromFile("pbr/default/ao.png")
    defaultNormal = Texture.LoadFromFile("pbr/default/normal.png")
    defaultRoughness = Texture.LoadFromFile("pbr/default/roughness.png")
    defaultMetalness = Texture.LoadFromFile("pbr/default/metalness.png")
    defaultAO = Texture.LoadFromFile("pbr/default/ao.png")

    # CLOWNFISHES
    clownFishModel = Mesh.LoadFromFile("clownfish/clownfish.fbx")[0]
    clownFishAlbedo = Texture.LoadFromFile("pbr/clownfish/albedo.png")
    clownFishNormal = Texture.LoadFromFile("pbr/clownfish/normal.png")

    renderer = Renderer(clownFishModel, Material("Standard", "std_pbr", "std_pbr"))
    renderer.properties.SetTexture("_Albedo", clownFishAlbedo)
    renderer.properties.SetTexture("_Normal", clownFishNormal)
    renderer.properties.SetTexture("_Roughness", defaultRoughness)
    renderer.properties.SetTexture("_Metalness", defaultMetalness)
    renderer.properties.SetTexture("_AmbientOcclusion", defaultAO)
    renderer.properties.SetTexture("_ReflectionProbe", skyboxTex)

    clownFish01 = SceneObject("ClownFish 1")
    clownFish01.AddComponent(renderer.Copy())
    clownFish01.transform.SetPosition(Vector3(0, 0, 0))
    clownFish01.transform.SetRotation(Quaternion.Eulerf(0, 0, 0))
    clownFish01.transform.SetScale(Vector3(1, 1, 1) * 0.1)

    clownFish02 = SceneObject("ClownFish 2")
    clownFish02.AddComponent(renderer.Copy())
    clownFish02.transform.SetPosition(Vector3(-0.25, 0.2, 0))
    clownFish02.transform.SetRotation(Quaternion.Eulerf(0, 0, 30))
    clownFish02.transform.SetScale(Vector3(1, 1, 1) * 0.1)

    clownFish02.AddComponent(Fornicator(Vector3(0, 0, 1), 10, 25))

    scene.AddObject(clownFish01)
    #scene.AddObject(clownFish02)

    # BARRACUDA
    barracudaModel = Mesh.LoadFromFile("barracuda/barracuda.fbx")[0]
    barracudaAlbedo = Texture.LoadFromFile("pbr/barracuda/albedo.png")
    barracudaNormal = Texture.LoadFromFile("pbr/barracuda/normal.png")

    renderer = Renderer(barracudaModel, Material("Standard", "std_pbr", "std_pbr"))
    renderer.properties.SetTexture("_Albedo", barracudaAlbedo)
    renderer.properties.SetTexture("_Normal", barracudaNormal)
    renderer.properties.SetTexture("_Roughness", defaultRoughness)
    renderer.properties.SetTexture("_Metalness", defaultMetalness)
    renderer.properties.SetTexture("_AmbientOcclusion", defaultAO)
    renderer.properties.SetTexture("_ReflectionProbe", skyboxTex)

    barracuda01 = SceneObject("Barracuda 1")
    barracuda01.AddComponent(renderer.Copy())
    barracuda01.transform.SetPosition(Vector3(2, 0, 0))
    barracuda01.transform.SetRotation(Quaternion.Eulerf(0, 0, 0))
    barracuda01.transform.SetScale(Vector3(1, 1, 1) * 0.1)

    barracuda02 = SceneObject("Barracuda 2")
    barracuda02.AddComponent(renderer.Copy())
    barracuda02.transform.SetPosition(Vector3(1.75, .2, 0))
    barracuda02.transform.SetRotation(Quaternion.Eulerf(0, 0, 30))
    barracuda02.transform.SetScale(Vector3(1, 1, 1) * 0.1)

    #barracuda02.AddComponent(Fornicator(Vector3(0, 0, 1), 10, 15))

    scene.AddObject(barracuda01)
    #scene.AddObject(barracuda02)

    # WATER & TERRAIN
    waterMaterial = Material("WaterMaterial", "water", "water")
    waterMaterial.AddTessellation("water", "water")
    waterPlane = SceneObject("Water")
    waterPlane.layer = Layers.WATER
    waterPlane.transform.SetPosition(Vector3(0, 5, 0))
    waterPlane.AddComponent(Renderer(plane, waterMaterial))
    waterPlane.GetComponent(Renderer).properties.SetTexture("_Normal", Texture.LoadFromFile("pbr/water/normal.jpg"))
    waterPlane.GetComponent(Renderer).properties.SetTexture("_Skybox", skyboxTex)

    terrainMaterial = Material("TerrainMaterial", "terrain", "terrain")
    terrainMaterial.AddTessellation("terrain", "terrain")
    terrain = SceneObject("Terrain")
    terrain.transform.SetPosition(Vector3(0, -18, 0))
    terrain.AddComponent(Renderer(plane, terrainMaterial))
    terrain.GetComponent(Renderer).properties.SetTexture("_HeightMap", Texture.LoadFromFile("terrain/heightmap.png"))
    terrain.GetComponent(Renderer).properties.SetTexture("_Albedo", Texture.LoadFromFile("pbr/water_stone/albedo.png"))
    terrain.GetComponent(Renderer).properties.SetTexture("_Normal", Texture.LoadFromFile("pbr/water_stone/normal.png"))
    terrain.GetComponent(Renderer).properties.SetTexture("_Roughness", Texture.LoadFromFile("pbr/water_stone/roughness.png"))
    terrain.GetComponent(Renderer).properties.SetTexture("_Metalness", Texture.LoadFromFile("pbr/water_stone/metalness.png"))
    terrain.GetComponent(Renderer).properties.SetTexture("_AmbientOcclusion", Texture.LoadFromFile("pbr/water_stone/ao.png"))
    
    scene.AddObject(terrain)
    scene.AddObject(waterPlane)

    # PBR TEST

    boxModel = Mesh.LoadFromFile("cube.obj")[0]

    pbrTest = SceneObject("PBRTest")
    pbrTest.transform.SetPosition(Vector3(0, 7, -2))
    pbrTest.transform.SetRotation(Quaternion.Eulerf(5, 0, -5))
    pbrTest.transform.SetScale(Vector3(1, 1, 1) * 0.5)

    pbrTestRenderer = Renderer(boxModel, Material("Standard", "std_pbr", "std_pbr"))

    pbrTestRenderer.properties.SetTexture("_Albedo", Texture.LoadFromFile("pbr/rock_1/albedo.png"))
    pbrTestRenderer.properties.SetTexture("_Normal", Texture.LoadFromFile("pbr/rock_1/normal.png"))
    pbrTestRenderer.properties.SetTexture("_Roughness", Texture.LoadFromFile("pbr/rock_1/roughness.png"))
    pbrTestRenderer.properties.SetTexture("_Metalness", Texture.LoadFromFile("pbr/rock_1/metalness.png"))
    pbrTestRenderer.properties.SetTexture("_AmbientOcclusion", Texture.LoadFromFile("pbr/rock_1/ao.png"))
    pbrTestRenderer.properties.SetTexture("_ReflectionProbe", skyboxTex)

    pbrTest.AddComponent(pbrTestRenderer.Copy())
    pbrTest.AddComponent(Rotator(Vector3(0, 1, 0), 30))


    # floatLerp = lambda a, b, t : a + (b - a) * t

    moveAnim = Animation({
        pbrTest.transform.SetPosition: KeyFrames({0: Vector3(0, 7, -2), 10: Vector3(0, 7, 4)}, Vector3.Lerp),
        pbrTest.transform.SetRotation: KeyFrames({0: Quaternion(), 5: Quaternion.Eulerf(0, 180, 0)}, Quaternion.Slerp)
    })

    pbrTest.AddComponent(Animator(moveAnim, playOnStart=True, loop=True))

    # PBR TEST2

    pbrTest1 = SceneObject("PBRTest")
    pbrTest1.transform.SetPosition(Vector3(1, 7, -2))
    pbrTest1.transform.SetRotation(Quaternion.Eulerf(5, 0, -5))
    pbrTest1.transform.SetScale(Vector3(1, 1, 1) * 0.5)

    pbrTestRenderer = Renderer(boxModel, Material("Standard", "std_pbr", "std_pbr"))

    pbrTestRenderer.properties.SetTexture("_Albedo", Texture.LoadFromFile("pbr/water_stone/albedo.png"))
    pbrTestRenderer.properties.SetTexture("_Normal", Texture.LoadFromFile("pbr/water_stone/normal.png"))
    pbrTestRenderer.properties.SetTexture("_Roughness", Texture.LoadFromFile("pbr/water_stone/roughness.png"))
    pbrTestRenderer.properties.SetTexture("_Metalness", Texture.LoadFromFile("pbr/water_stone/metalness.png"))
    pbrTestRenderer.properties.SetTexture("_AmbientOcclusion", Texture.LoadFromFile("pbr/water_stone/ao.png"))
    pbrTestRenderer.properties.SetTexture("_ReflectionProbe", skyboxTex)

    pbrTest1.AddComponent(pbrTestRenderer.Copy())
    pbrTest1.AddComponent(Rotator(Vector3(0, 1, 0), 30))

    # PBR TEST3
    pbrTest2 = SceneObject("PBRTest")
    pbrTest2.transform.SetPosition(Vector3(-1, 7, -2))
    pbrTest2.transform.SetRotation(Quaternion.Eulerf(5, 0, -5))
    pbrTest2.transform.SetScale(Vector3(1, 1, 1) * 0.5)

    pbrTestRenderer = Renderer(boxModel, Material("Standard", "std_pbr", "std_pbr"))

    pbrTestRenderer.properties.SetTexture("_Albedo", Texture.LoadFromFile("pbr/rusted_iron/albedo.png"))
    pbrTestRenderer.properties.SetTexture("_Normal", Texture.LoadFromFile("pbr/rusted_iron/normal.png"))
    pbrTestRenderer.properties.SetTexture("_Roughness", Texture.LoadFromFile("pbr/rusted_iron/roughness.png"))
    pbrTestRenderer.properties.SetTexture("_Metalness", Texture.LoadFromFile("pbr/rusted_iron/metalness.png"))
    pbrTestRenderer.properties.SetTexture("_AmbientOcclusion", Texture.LoadFromFile("pbr/rusted_iron/ao.png"))
    pbrTestRenderer.properties.SetTexture("_ReflectionProbe", skyboxTex)

    pbrTest2.AddComponent(pbrTestRenderer)
    pbrTest2.AddComponent(Rotator(Vector3(0, 1, 0), 30))

    scene.AddObject(pbrTest)
    scene.AddObject(pbrTest1)
    scene.AddObject(pbrTest2)

    camera.object.transform.SetPosition(Vector3(0, 7, -3))
    camera.object.transform.SetRotation(Quaternion.Eulerf(0, 0, 0))

    window.AttachScene(scene)
    window.SetRenderingCamera(camera)

    window.Run()

if __name__ == '__main__':
    glfw.init() # Initialize window system glfw
    main()
    glfw.terminate() # destroy all graphics contexts

