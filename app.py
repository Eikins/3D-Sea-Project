
#!/usr/bin/env python3
"""
3D Sea Application
"""

import glfw
import math
import numpy as np
import numpy.random as rng

from sea3d.math import Vector3, Quaternion, Matrix4
from sea3d.core import Scene, SceneObject, Mesh, Material, Behaviour, Time, Texture, TextureWrapMode, TextureFilter, Layers, KeyFrames, Animation
from sea3d.core.components import Camera, Renderer, Animator

from sea3d.opengl import GLWindow


def GetHeightAt(heightMap:Texture, x:float, y:float):
    ux = int(math.floor(x))
    uy = int(math.floor(y))
    if heightMap.filter == TextureFilter.POINT:
        return heightMap.data[ux, uy][0] / 255
    else:
        tx = x - ux
        ty = y - uy
        h00 = heightMap.data[ux, uy][0]
        h10 = heightMap.data[ux + 1, uy][0]
        h01 = heightMap.data[ux, uy + 1][0]
        h11 = heightMap.data[ux + 1, uy + 1][0]
        linear0 = h00 * tx + h10 * (1 - tx)
        linear1 = h01 * tx + h11 * (1 - tx)
        h = linear0 * ty + linear1 * (1 - ty)
        return h / 255


def AddTerrain(scene: Scene, plane: Mesh):
    terrain = SceneObject("Terrain")
    terrain.transform.SetPosition(Vector3(0, -18, 0))

    terrainMaterial = Material("TerrainMaterial", "terrain", "terrain")
    terrainMaterial.AddTessellation("terrain", "terrain")
    renderer = Renderer(plane, terrainMaterial)
    renderer.properties.SetTexture("_HeightMap", Texture.LoadFromFile("terrain/heightmap.png"))
    renderer.properties.SetTexture("_Albedo", Texture.LoadFromFile("pbr/water_stone/albedo.png"))
    renderer.properties.SetTexture("_Normal", Texture.LoadFromFile("pbr/water_stone/normal.png"))
    renderer.properties.SetTexture("_Roughness", Texture.LoadFromFile("pbr/water_stone/roughness.png"))
    renderer.properties.SetTexture("_Metalness", Texture.LoadFromFile("pbr/water_stone/metalness.png"))
    renderer.properties.SetTexture("_AmbientOcclusion", Texture.LoadFromFile("pbr/water_stone/ao.png"))
    terrain.AddComponent(renderer)
    
    scene.AddObject(terrain)
    AddVegetation(scene, terrain)

def GenerateVegetationMesh(referenceMesh:Mesh, size = (40, 40), count = (10, 10)):
    # MESH CREATION
    # Instead of having a big number of sceneobjects, that slows down a lot the CPU,
    # we merge all similar vegetation to 1 mesh
    # First, create an empty mesh
    vegeMesh = Mesh(
        vertices = np.empty((0, 3), 'f'),
        normals = np.empty((0, 3), 'f'),
        uvs = [np.empty((0, 2), 'f')],
        indexes = np.empty((0, 3), 'u4'),
        tangents = np.empty((0, 3), 'f')
    )

    # Merge meshes
    X = np.linspace(-size[0] / 2, size[0] / 2, num = count[0])
    Z = np.linspace(-size[1] / 2, size[1] / 2, num = count[1])
    for x in X:
        for z in Z:
            # The terrain height is 30, and its size is 500 x 500
            # We sample the height
            y = 30 * GetHeightAt(Texture.Atlas["terrain/heightmap.png"], (0.5 + z / 500) * 1024, (0.5 + x / 500) * 1024)
            # We translate & rotate the vegetation
            T = Matrix4.Translate(Vector3(x, y, z))
            R = Matrix4.Quaternion(Quaternion.Eulerf(0, rng.random() * 360, 0))
            S = Matrix4.Scale(Vector3(rng.random() + 1.0, rng.random() + 1.0, rng.random() + 1.0) * 0.5)
            transformMatrix = T @ R @ S
            mesh = Mesh.Transform(referenceMesh, transformMatrix)
            vegeMesh = Mesh.Combine(vegeMesh, mesh)
    return vegeMesh


def AddVegetation(scene: Scene, terrain:SceneObject):
    quad1 = Mesh.Quad(size = (0.518, 1.413), offset=(0, 1.413 / 2))
    quad6 = Mesh.Quad(size = (1.029, 1.250), offset=(0, 1.250 / 2))

    albedo1 = Texture.LoadFromFile("pbr/algae/REDALGAE1.png")
    albedo6 = Texture.LoadFromFile("pbr/algae/REDALGAE6.png")

    mesh1 = GenerateVegetationMesh(quad1, count = (20, 20))
    mesh6 = GenerateVegetationMesh(quad6, count = (10, 10))

    vegetationMaterial = Material("StandardCutout", "std_pbr", "std_pbr_cutout")
    vegetationMaterial.renderBothFaces = True
    vegetationMaterial.orderInQueue = 5000 # Default value is 1000, this mean this will be rendered after default objects

    renderer1 = Renderer(mesh1, vegetationMaterial)
    renderer1.properties.SetFloat("_AlphaCutoutThreshold", 0.9)
    renderer1.properties.SetTexture("_Albedo", albedo1)
    renderer1.properties.SetTexture("_Normal", Texture.Atlas["pbr/default/normal.png"])
    renderer1.properties.SetTexture("_Roughness", Texture.Atlas["pbr/default/roughness.png"])
    renderer1.properties.SetTexture("_Metalness", Texture.Atlas["pbr/default/metalness.png"])
    renderer1.properties.SetTexture("_AmbientOcclusion", Texture.Atlas["pbr/default/ao.png"])
    renderer1.properties.SetTexture("_ReflectionProbe", Texture.Atlas["cubemaps/skybox"])

    renderer6 = Renderer(mesh6, vegetationMaterial)
    renderer6.properties.SetFloat("_AlphaCutoutThreshold", 0.9)
    renderer6.properties.SetTexture("_Albedo", albedo6)
    renderer6.properties.SetTexture("_Normal", Texture.Atlas["pbr/default/normal.png"])
    renderer6.properties.SetTexture("_Roughness", Texture.Atlas["pbr/default/roughness.png"])
    renderer6.properties.SetTexture("_Metalness", Texture.Atlas["pbr/default/metalness.png"])
    renderer6.properties.SetTexture("_AmbientOcclusion", Texture.Atlas["pbr/default/ao.png"])
    renderer6.properties.SetTexture("_ReflectionProbe", Texture.Atlas["cubemaps/skybox"])

    algaes1 = SceneObject("Algaes 1", terrain.transform)
    algaes6 = SceneObject("Algaes 6", terrain.transform)

    algaes1.AddComponent(renderer1)
    algaes6.AddComponent(renderer6)

    algaes6.transform.SetPosition(Vector3(1.24, 0, 0))

    scene.AddObject(algaes1)
    scene.AddObject(algaes6)

def AddWater(scene: Scene, plane: Mesh):
    water = SceneObject("Water")
    water.layer = Layers.WATER
    water.transform.SetPosition(Vector3(0, 5, 0))

    waterMaterial = Material("WaterMaterial", "water", "water")
    waterMaterial.AddTessellation("water", "water")
    waterMaterial.renderBothFaces = True
    renderer = Renderer(plane, waterMaterial)
    renderer.properties.SetTexture("_Normal", Texture.LoadFromFile("pbr/water/normal.jpg"))
    renderer.properties.SetTexture("_Skybox", Texture.Atlas["cubemaps/skybox"])
    water.AddComponent(renderer)

    scene.AddObject(water)

def AddFishes(scene: Scene, fishes):
    for fish, transforms in fishes.items():
        mesh = Mesh.LoadFromFile("fish/" + fish + "/" + fish + ".fbx")[0]
        albedo = Texture.LoadFromFile("pbr/fish/" + fish + "/albedo.png")
        normal = Texture.LoadFromFile("pbr/fish/" + fish + "/normal.png")

        renderer = Renderer(mesh, Material("Standard", "std_pbr", "std_pbr"))
        renderer.properties.SetTexture("_Albedo", albedo)
        renderer.properties.SetTexture("_Normal", normal)
        renderer.properties.SetTexture("_Roughness", Texture.Atlas["pbr/default/roughness.png"])
        renderer.properties.SetTexture("_Metalness", Texture.Atlas["pbr/default/metalness.png"])
        renderer.properties.SetTexture("_AmbientOcclusion", Texture.Atlas["pbr/default/ao.png"])
        renderer.properties.SetTexture("_ReflectionProbe", Texture.Atlas["cubemaps/skybox"])

        i = 0
        for transform in transforms:
            fishObj = SceneObject(fish + " " + str(i))
            fishObj.transform.SetPosition(transform[0])
            fishObj.transform.SetRotation(transform[1])
            fishObj.transform.SetScale(transform[2])

            fishObj.AddComponent(renderer.Copy())

            scene.AddObject(fishObj)
            i += 1


### CUSTOM COMPONENTS ###
class FPSController(Behaviour):

    # Attach GLWindows, a proper  platform-independent Input System needs to be implemented
    def __init__(self, window:GLWindow, moveSpeed:float, rotateSpeed:float, sensitivity:float = 100):
        super().__init__()
        self.movementInput = Vector3()
        self.lastMousePos = Vector3()
        self.sensitivity = sensitivity
        self.movementSpeed = moveSpeed
        self.rotateSpeed = rotateSpeed
        self.speedModifier = 1
        window.key_handlers += [self.OnKey]
        window.mouse_handlers += [self.OnMouse]

    def Update(self):
        movement = (self.movementInput.x * self.object.transform.RightVector()
                  + self.movementInput.z * self.object.transform.ForwardVector()
                  + Vector3(0, self.movementInput.y, 0))

        movement = movement * Time.deltaTime * self.movementSpeed * self.speedModifier
        self.object.transform.Translate(movement)

    def OnKey(self, key, _scancode, action, _mods):
        if action == glfw.PRESS or action == glfw.RELEASE:
            state = 1 if action == glfw.PRESS else -1
            if key == glfw.KEY_W:
                self.movementInput.z += 1 * state
            if key == glfw.KEY_S:
                self.movementInput.z -= 1 * state
            if key == glfw.KEY_A:
                self.movementInput.x -= 1 * state
            if key == glfw.KEY_D:
                self.movementInput.x += 1 * state
            if key == glfw.KEY_LEFT_SHIFT:
                self.movementInput.y -= 1 * state
            if key == glfw.KEY_SPACE:
                self.movementInput.y += 1 * state
            if key == glfw.KEY_LEFT_CONTROL:
                self.speedModifier = 2 + state * 0.5

    def OnMouse(self, x, y):
        pos = Vector3(x, y)
        drag = pos - self.lastMousePos
        self.lastMousePos = pos
        delta = Time.deltaTime * self.rotateSpeed * self.sensitivity
        # Invert rotation order for world axis rotation
        newRotation = Quaternion.Eulerf(0, drag.x * delta) * Quaternion.AxisAngle(self.object.transform.RightVector(), drag.y * delta) * self.object.transform._rotation
        self.object.transform.SetRotation(newRotation)
        

def main():
    window = GLWindow(width=1600, height=900)
    window.Init()

    # SCENE
    scene = Scene("Main Scene")
    window.AttachScene(scene)

    # CAMERA
    cameraObject = SceneObject("Camera 1")
    cameraObject.transform.SetPosition(Vector3(0, 0, 1))
    #cameraObject.transform.SetRotation(Quaternion.Eulerf(0, 0, 0))
    camera = Camera(aspect=1600/900, far=1000)
    cameraObject.AddComponent(camera)
    cameraObject.AddComponent(FPSController(window, 10, 90))
    scene.AddObject(cameraObject)
    window.SetRenderingCamera(camera)

    # SKYBOX
    skyboxTex = Texture.LoadFromFile("cubemaps/skybox", loadAsCubemap=True, fileExtension=".png")
    skyboxTex.wrapMode = TextureWrapMode.CLAMP_TO_EDGE
    camera.AttachSkyBox(skyboxTex)

    # Load Default PBR textures
    Texture.LoadFromFile("pbr/default/ao.png")
    Texture.LoadFromFile("pbr/default/normal.png")
    Texture.LoadFromFile("pbr/default/roughness.png")
    Texture.LoadFromFile("pbr/default/metalness.png")
    Texture.LoadFromFile("pbr/default/ao.png")

    # WATER & TERRAIN
    plane = Mesh.Plane((500, 500), (250, 250))
    AddTerrain(scene, plane)
    AddWater(scene, plane)

    # FISHES
    fishes = {
        "clownfish": [
            (Vector3(0, 0, 0), Quaternion(), Vector3(1, 1, 1) * 0.1),
            (Vector3(3.4, 1, 10), Quaternion.Eulerf(0, 180, 0), Vector3(1, 1, 1) * 0.13),     
            ],
        "barracuda": [
            (Vector3(0, 2, 0), Quaternion(), Vector3(1, 1, 1) * 0.1),
            (Vector3(1, -3, -4), Quaternion.Eulerf(0, 180, 0), Vector3(1, 1, 1) * 0.11),     
            ]
    }
    AddFishes(scene, fishes)

    print("Scene : " + scene.name)
    for obj in scene.objects:
        print(" " + obj.name)

    window.Run()

if __name__ == '__main__':
    glfw.init() # Initialize window system glfw
    main()
    glfw.terminate() # destroy all graphics contexts



# # PBR TEST

#     boxModel = Mesh.LoadFromFile("cube.obj")[0]

#     pbrTest = SceneObject("PBRTest")
#     pbrTest.transform.SetPosition(Vector3(0, 7, -2))
#     pbrTest.transform.SetRotation(Quaternion.Eulerf(5, 0, -5))
#     pbrTest.transform.SetScale(Vector3(1, 1, 1) * 0.5)

#     pbrTestRenderer = Renderer(boxModel, Material("Standard", "std_pbr", "std_pbr"))

#     pbrTestRenderer.properties.SetTexture("_Albedo", Texture.LoadFromFile("pbr/rock_1/albedo.png"))
#     pbrTestRenderer.properties.SetTexture("_Normal", Texture.LoadFromFile("pbr/rock_1/normal.png"))
#     pbrTestRenderer.properties.SetTexture("_Roughness", Texture.LoadFromFile("pbr/rock_1/roughness.png"))
#     pbrTestRenderer.properties.SetTexture("_Metalness", Texture.LoadFromFile("pbr/rock_1/metalness.png"))
#     pbrTestRenderer.properties.SetTexture("_AmbientOcclusion", Texture.LoadFromFile("pbr/rock_1/ao.png"))
#     pbrTestRenderer.properties.SetTexture("_ReflectionProbe", skyboxTex)

#     pbrTest.AddComponent(pbrTestRenderer.Copy())


#     # floatLerp = lambda a, b, t : a + (b - a) * t

#     moveAnim = Animation({
#         pbrTest.transform.SetPosition: KeyFrames({0: Vector3(0, 7, -2), 10: Vector3(0, 7, 4)}, Vector3.Lerp),
#         pbrTest.transform.SetRotation: KeyFrames({0: Quaternion(), 5: Quaternion.Eulerf(0, 180, 0)}, Quaternion.Slerp)
#     })

#     pbrTest.AddComponent(Animator(moveAnim, playOnStart=True, loop=True))

#     # PBR TEST2

#     pbrTest1 = SceneObject("PBRTest")
#     pbrTest1.transform.SetPosition(Vector3(1, 7, -2))
#     pbrTest1.transform.SetRotation(Quaternion.Eulerf(5, 0, -5))
#     pbrTest1.transform.SetScale(Vector3(1, 1, 1) * 0.5)

#     pbrTestRenderer = Renderer(boxModel, Material("Standard", "std_pbr", "std_pbr"))

#     pbrTestRenderer.properties.SetTexture("_Albedo", Texture.LoadFromFile("pbr/water_stone/albedo.png"))
#     pbrTestRenderer.properties.SetTexture("_Normal", Texture.LoadFromFile("pbr/water_stone/normal.png"))
#     pbrTestRenderer.properties.SetTexture("_Roughness", Texture.LoadFromFile("pbr/water_stone/roughness.png"))
#     pbrTestRenderer.properties.SetTexture("_Metalness", Texture.LoadFromFile("pbr/water_stone/metalness.png"))
#     pbrTestRenderer.properties.SetTexture("_AmbientOcclusion", Texture.LoadFromFile("pbr/water_stone/ao.png"))
#     pbrTestRenderer.properties.SetTexture("_ReflectionProbe", skyboxTex)

#     pbrTest1.AddComponent(pbrTestRenderer.Copy())

#     # PBR TEST3
#     pbrTest2 = SceneObject("PBRTest")
#     pbrTest2.transform.SetPosition(Vector3(-1, 7, -2))
#     pbrTest2.transform.SetRotation(Quaternion.Eulerf(5, 0, -5))
#     pbrTest2.transform.SetScale(Vector3(1, 1, 1) * 0.5)

#     pbrTestRenderer = Renderer(boxModel, Material("Standard", "std_pbr", "std_pbr"))

#     pbrTestRenderer.properties.SetTexture("_Albedo", Texture.LoadFromFile("pbr/rusted_iron/albedo.png"))
#     pbrTestRenderer.properties.SetTexture("_Normal", Texture.LoadFromFile("pbr/rusted_iron/normal.png"))
#     pbrTestRenderer.properties.SetTexture("_Roughness", Texture.LoadFromFile("pbr/rusted_iron/roughness.png"))
#     pbrTestRenderer.properties.SetTexture("_Metalness", Texture.LoadFromFile("pbr/rusted_iron/metalness.png"))
#     pbrTestRenderer.properties.SetTexture("_AmbientOcclusion", Texture.LoadFromFile("pbr/rusted_iron/ao.png"))
#     pbrTestRenderer.properties.SetTexture("_ReflectionProbe", skyboxTex)

#     pbrTest2.AddComponent(pbrTestRenderer)

#     scene.AddObject(pbrTest)
#     scene.AddObject(pbrTest1)
#     scene.AddObject(pbrTest2)
