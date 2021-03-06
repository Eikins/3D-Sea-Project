
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

# Sample a texture at pixel coordinate and return the red value normalized (height)
def GetHeightAt(heightMap:Texture, x:float, y:float):
    ux = int(math.floor(x))
    uy = int(math.floor(y))
    if heightMap.filter == TextureFilter.POINT:
        return heightMap.data[ux, uy][0] / 255
    else:
        # Bilinear interpolation...
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
    for fish, descriptors in fishes.items():
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
        for descriptor in descriptors:
            fishObj = SceneObject(fish + " " + str(i))

            animationChannels = dict()

            # descriptor[0] is either a Vector3, either Position keyframes
            if isinstance(descriptor[0], Vector3):
                fishObj.transform.SetPosition(descriptor[0])
            else:
                animationChannels[fishObj.transform.SetPosition] = descriptor[0]

            # descriptor[1] is either a Quaternion, either Rotation keyframes
            if isinstance(descriptor[1], Quaternion):
                fishObj.transform.SetRotation(descriptor[1])
            else:
                animationChannels[fishObj.transform.SetRotation] = descriptor[1]  

            # descriptor[2] is either a Vector3, either Scale keyframes
            if isinstance(descriptor[2], Vector3):
                fishObj.transform.SetScale(descriptor[2])
            else:
                animationChannels[fishObj.transform.SetScale] = descriptor[2]  

            if animationChannels:
                animation = Animation(animationChannels)
                fishObj.AddComponent(Animator(animation, playOnStart=True, loop=True))

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

    def Start(self):
        self.firstMouseUpdate = True

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

        # Fix first update bug
        if self.firstMouseUpdate:
            self.firstMouseUpdate = False
            return

        delta = Time.deltaTime * self.rotateSpeed * self.sensitivity
        # Invert rotation order for world axis rotation
        newRotation = Quaternion.Eulerf(0, drag.x * delta) * Quaternion.AxisAngle(self.object.transform.RightVector(), drag.y * delta) * self.object.transform._rotation
        self.object.transform.SetRotation(newRotation)
        

### DEMO ONLY
### TERRAIN ROTATOR ###
class TerrainController(Behaviour):

    # Attach GLWindows, a proper  platform-independent Input System needs to be implemented
    def __init__(self, window:GLWindow):
        super().__init__()
        window.key_handlers += [self.OnKey]
        self.angle = 0
        self.offset = 0

    def Start(self):
        self.initialPosition = self.object.transform._position

    def Update(self):
        self.object.transform.Rotate(Quaternion.Eulerf(0, self.angle * Time.deltaTime * 60, 0))
        self.object.transform.Translate(Vector3(0, self.offset * 5 * Time.deltaTime, 0))

    def OnKey(self, key, _scancode, action, _mods):
        if action == glfw.PRESS or action == glfw.RELEASE:
            state = 1 if action == glfw.PRESS else -1
            if key == glfw.KEY_LEFT:
                self.angle -= 1 * state
            if key == glfw.KEY_RIGHT:
                self.angle += 1 * state
            if key == glfw.KEY_UP:
                self.offset += 1 * state
            if key == glfw.KEY_DOWN:
                self.offset -= 1 * state

        if action == glfw.PRESS and key == glfw.KEY_BACKSPACE:
                self.object.transform.SetRotation(Quaternion())
                self.object.transform.SetPosition(self.initialPosition)

# TUTORIAL : Create your own Behaviour !
# Let's make a rotator component :
# Define a class that extends Behaviour
class Rotator(Behaviour):

    # MANDATORY ! Implements __init__ with your desired parameters
    # DONT FORGET TO super().__init__() OR IT WILL CAUSE A BUG !
    # Our Rotator has 2 parameters : the axis around which we rotate, and the angular speed
    def __init__(self, axis:Vector3, speed:float):
        super().__init__()
        self.axis = axis
        self.speed = speed

    # The Start method is called on the initialization of the scene
    # Here, gather the components you need
    # Be careful ! That mean that if your behaviour needs a component, 
    # Be sure that it's present on your object
    def Start(self):
        # Example : if we would need to modify the renderer properties, then
        # self.renderer:Renderer = self.object.GetComponent(Renderer)
        pass

    # Update method, called every frame
    # Here, you "integrate" your state
    # For example, we know that theta = integral of d(theta)/dt
    # We have the angular speed (d(theta)/dt)
    # Then each frame, theta += d(theta)/dt * dt
    # dt is given by Time.deltaTime
    def Update(self):
        self.object.transform.Rotate(Quaternion.AxisAngle(self.axis, self.speed * Time.deltaTime))

def main():
    window = GLWindow(width=1600, height=900)
    window.Init()

    # SCENE
    scene = Scene("Main Scene")
    window.AttachScene(scene)

    # CAMERA
    cameraObject = SceneObject("Camera 1")
    cameraObject.transform.SetPosition(Vector3(0, 0, 1))
    cameraObject.transform.SetRotation(Quaternion.Eulerf(0, 0, 0))
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

    # DEMO ONLY - TERRAIN CONTROLLER
    terrain = scene.Find("Terrain")
    if terrain:
        terrain.AddComponent(TerrainController(window))

    # FISH DICITONNARY
    # The key are the fish names, it will automatically load the associated model and textures
    # under assets/models/fish/fish-name/fish-name.fbx for the Mesh
    #       assets/textures/pbr/fish/fish-name/albedo.png for the Albedo
    #       assets/textures/pbr/fish/fish-name/normal.png for the Normal
    # it uses default roughness, metalness and ao
    # The key is a list of Fish Descriptors
    # A fish descriptor is a 3-tuple, of the form (PositionInfo, RotationInfo, ScaleInfo)
    # The PositionInfo is either a Vector3 for a static position, or a KeyFrames of Vector3
    # The RotationInfo is either a Quaternion for a static rotation, or a KeyFrames of Quaternions
    # The ScaleInfo is either a Vector3 for a static Scale, or a KeyFrames of Vector3

    # FISHES
    fishes = {
        "clownfish": [
            # FIRST CLOWNFISH
            (
                KeyFrames({0: Vector3(0, 0, 0), 4.5: Vector3(2.5, 0, 0), 5.5: Vector3(2.5, 0, 0), 9: Vector3(0, 0, 0), 10: Vector3(0, 0, 0)}, Vector3.Lerp),
                KeyFrames({0: Quaternion(), 4.5: Quaternion(), 5.5: Quaternion.Eulerf(0, 180, 0), 9: Quaternion.Eulerf(0, 180, 0), 10: Quaternion()}, Quaternion.Slerp),
                Vector3(1, 1, 1) * 0.1
            ),
            # SECOND CLOWNFISH
            (    KeyFrames({0: Vector3(3.4, 1, 10), 3: Vector3(9.4, 1, 10), 3.5: Vector3(9.4, 1, 10), 6.5: Vector3(9.4, 1, 16), 7: Vector3(9.4, 1, 16), 10: Vector3(3.4, 1, 16), 10.5: Vector3(3.4, 1, 16), 13.5: Vector3(3.4,1,10), 14: Vector3(3.4,1,10)}, Vector3.Lerp),
                KeyFrames({0: Quaternion(), 3: Quaternion(), 3.5: Quaternion.Eulerf(0,270,0), 6.5: Quaternion.Eulerf(0,270,0), 7: Quaternion.Eulerf(0,180,0), 10: Quaternion.Eulerf(0,180,0), 10.5: Quaternion.Eulerf(0, 90, 0), 13.5: Quaternion.Eulerf(0, 90, 0), 14: Quaternion()}, Quaternion.Slerp),
                Vector3(1, 1, 1) * 0.13    
            ),
            ],
        "barracuda": [
            (
                KeyFrames({0: Vector3(-13,-5,0), 10: Vector3(-13,3,0), 10.1: Vector3(-13,3,0), 20.1: Vector3(-13,-5,0), 20.2: Vector3(-13,-5,0)}, Vector3.Lerp),
                KeyFrames({0: Quaternion(),10: Quaternion.Eulerf(0,180,0), 10.1: Quaternion.Eulerf(0,180,0), 20.1: Quaternion.Eulerf(0,360,0), 20.2: Quaternion()}, Quaternion.Slerp),
                Vector3(1, 1, 1) * 0.11)    
            ],
        "shark": [
            (
                KeyFrames({0: Vector3(-10,0,-20), 2.5: Vector3(-8,0,-15), 7.5: Vector3(-12,0,-5), 12.5: Vector3(-8,0,5), 17.5: Vector3(-12,0,15), 20: Vector3(-10,0,20), 
                           22.5:Vector3(-10,0,20), 25:Vector3(-12,0,15), 30: Vector3(-8,0,5), 35: Vector3(-12,0,-5), 40: Vector3(-8,0,-15), 42.5: Vector3(-10,0,-20)}, Vector3.Lerp),
                KeyFrames({0: Quaternion.Eulerf(0,270,0), 2.5: Quaternion.Eulerf(0,240,0), 7.5: Quaternion.Eulerf(0,300,0), 12.5: Quaternion.Eulerf(0,240,0), 17.5: Quaternion.Eulerf(0,300,0), 20: Quaternion.Eulerf(0,300,0),
                           22.5: Quaternion.Eulerf(0,90,0), 25: Quaternion.Eulerf(0,60,0), 30: Quaternion.Eulerf(0,120,0), 35: Quaternion.Eulerf(0,60,0), 40: Quaternion.Eulerf(0,120,0), 42.5: Quaternion.Eulerf(0,270,0)}, Quaternion.Slerp),
                Vector3(1, 1, 1) * 0.8)    
            ],
        "lionfish":  [
            (
                KeyFrames({0: Vector3(5,2,-5), 5: Vector3(6,0,-5), 10: Vector3(7,2,-5), 15: Vector3(8,0,-5), 17: Vector3(8,0,-5), 22: Vector3(7,2,-5), 27: Vector3(6,0,-5), 32: Vector3(5,2,-5), 34: Vector3(5,2,-5)}, Vector3.Lerp),
                KeyFrames({0: Quaternion(),5: Quaternion(), 10: Quaternion(), 15: Quaternion(), 17: Quaternion.Eulerf(0,180,0), 20: Quaternion.Eulerf(0,180,0), 22: Quaternion.Eulerf(0,180,0), 27: Quaternion.Eulerf(0,180,0), 32: Quaternion.Eulerf(0,180,0), 34: Quaternion()}, Quaternion.Slerp),
                Vector3(1, 1, 1) * 0.11)    
            ],            
        "seahorse": [
            (
                KeyFrames({0: Vector3(5,5,-8), 10: Vector3(5,-6,-8), 10.1: Vector3(5,-6,-8), 20.1: Vector3(5,5,-8), 20.2: Vector3(5,5,-8)}, Vector3.Lerp),
                KeyFrames({0: Quaternion(),10: Quaternion(), 10.1: Quaternion(), 20.1: Quaternion(), 20.2: Quaternion()}, Quaternion.Slerp),
                Vector3(1, 1, 1) * 0.11)    
            ],
        "reeffish":  [
            (
                KeyFrames({0: Vector3(-1.5,-4,-3), 5: Vector3(-1.5,0,-2), 10: Vector3(-1.5,-4,-1), 15: Vector3(-1.5,0,0), 20: Vector3(-1.5,-4,1), 22: Vector3(-1.5,-4,1), 27: Vector3(-1.5,0,0), 32: Vector3(-1.5,-4,-1), 37: Vector3(-1.5,0,-2), 42: Vector3(-1.5,-4,-3), 44: Vector3(-1.5,-4,-3)}, Vector3.Lerp),
                KeyFrames({0: Quaternion.Eulerf(0,270,0),5: Quaternion.Eulerf(0,270,0), 10: Quaternion.Eulerf(0,270,0), 15: Quaternion.Eulerf(0,270,0), 20: Quaternion.Eulerf(0,270,0), 22: Quaternion.Eulerf(0,90,0), 27: Quaternion.Eulerf(0,90,0), 32: Quaternion.Eulerf(0,90,0), 37: Quaternion.Eulerf(0,90,0), 42: Quaternion.Eulerf(0,90,0), 44: Quaternion.Eulerf(0,270,0)}, Quaternion.Slerp),
                Vector3(1, 1, 1) * 0.15)    
            ],  
        "dorie": [
            (
                KeyFrames({0: Vector3(1, 0, -1), 4.5: Vector3(3.5, 0, -1), 5.5: Vector3(3.5, 0, -1), 9: Vector3(1, 0, -1), 10: Vector3(1, 0, -1)}, Vector3.Lerp),
                KeyFrames({0: Quaternion(), 4.5: Quaternion(), 5.5: Quaternion.Eulerf(0, 180, 0), 9: Quaternion.Eulerf(0, 180, 0), 10: Quaternion()}, Quaternion.Slerp),
                Vector3(1, 1, 1) * 0.1
            )
            ],
        "yellowfish": [
            (
                KeyFrames({0: Vector3(8, 1, 5), 5: Vector3(8, 1, 5), 5.1: Vector3(8, 1, 5), 10: Vector3(8, 1, 5), 10.1: Vector3(8, 1, 5)}, Vector3.Lerp),
                KeyFrames({0: Quaternion.Eulerf(0, 90, 0), 5.1: Quaternion.Eulerf(0, 270, 0), 7: Quaternion.Eulerf(0, 270, 0), 10: Quaternion.Eulerf(0, 90, 0), 10.1: Quaternion.Eulerf(0, 90, 0)}, Quaternion.Slerp),
                Vector3(1, 1, 1) * 0.1
            )                  
        ]
    }
                
    AddFishes(scene, fishes)
    
    parentFish1 = scene.Find("clownfish 1")
    childFish = SceneObject("clownfish 1 child", parentFish1.transform)
    childFish.transform.SetPosition(Vector3(0, 0, -3))
    childFish.transform.SetScale(Vector3(1, 1, 1) * 0.3)
    childFish.AddComponent(parentFish1.GetComponent(Renderer).Copy())
    scene.AddObject(childFish)
    
    parentFish2 = scene.Find("clownfish 0")
    friendFish = SceneObject("clownfish 0 child", parentFish2.transform)
    friendFish.transform.SetPosition(Vector3(1, 0, 2))
    friendFish.transform.SetScale(Vector3(1, 1, 1) * 0.1)
    friendFish.AddComponent(parentFish2.GetComponent(Renderer).Copy())
    scene.AddObject(friendFish)
    
    parentFish3 = scene.Find("yellowfish 0")
    
    swarmfish1 = SceneObject("swarm fish 1", parentFish3.transform)
    swarmfish1.transform.SetPosition(Vector3(3, 0, 3))
    swarmfish1.transform.SetScale(Vector3(1, 1, 1))
    swarmfish1.AddComponent(parentFish3.GetComponent(Renderer).Copy())
    scene.AddObject(swarmfish1)

    swarmfish2 = SceneObject("swarm fish 2", parentFish3.transform)
    swarmfish2.transform.SetPosition(Vector3(1, 5, 0))
    swarmfish2.transform.SetScale(Vector3(1, 1, 1))
    swarmfish2.AddComponent(parentFish3.GetComponent(Renderer).Copy())
    scene.AddObject(swarmfish2)

    swarmfish3 = SceneObject("swarm fish 3", parentFish3.transform)
    swarmfish3.transform.SetPosition(Vector3(3, -3, 8))
    swarmfish3.transform.SetScale(Vector3(1, 1, 1))
    swarmfish3.AddComponent(parentFish3.GetComponent(Renderer).Copy())
    scene.AddObject(swarmfish3)

    swarmfish4 = SceneObject("swarm fish 4", parentFish3.transform)
    swarmfish4.transform.SetPosition(Vector3(7, 3, 3))
    swarmfish4.transform.SetScale(Vector3(1, 1, 1))
    swarmfish4.AddComponent(parentFish3.GetComponent(Renderer).Copy())
    scene.AddObject(swarmfish4)

    swarmfish5 = SceneObject("swarm fish 5", parentFish3.transform)
    swarmfish5.transform.SetPosition(Vector3(0, -2.6, -2.8))
    swarmfish5.transform.SetScale(Vector3(1, 1, 1))
    swarmfish5.AddComponent(parentFish3.GetComponent(Renderer).Copy())
    scene.AddObject(swarmfish5)

    swarmfish6 = SceneObject("swarm fish 6", parentFish3.transform)
    swarmfish6.transform.SetPosition(Vector3(0, -5, 5.2))
    swarmfish6.transform.SetScale(Vector3(1, 1, 1))
    swarmfish6.AddComponent(parentFish3.GetComponent(Renderer).Copy())
    scene.AddObject(swarmfish6)





#     pbrTest1 = SceneObject("PBRTest")
#     pbrTest1.transform.SetPosition(Vector3(0, 7, 0))
#     pbrTest1.transform.SetRotation(Quaternion.Eulerf(5, 40, -5))
#     pbrTest1.transform.SetScale(Vector3(1, 1, 1) * 0.5)
#
#     boxModel = Mesh.LoadFromFile("cube.obj")[0]
#     pbrTestRenderer = Renderer(boxModel, Material("Standard", "std_pbr", "std_pbr"))
#     # floatLerp = lambda a, b, t : a + (b - a) * t
#
#     pbrTestRenderer.properties.SetTexture("_Albedo", Texture.LoadFromFile("pbr/water_stone/albedo.png"))
#     pbrTestRenderer.properties.SetTexture("_Normal", Texture.LoadFromFile("pbr/water_stone/normal.png"))
#     pbrTestRenderer.properties.SetTexture("_Roughness", Texture.LoadFromFile("pbr/water_stone/roughness.png"))
#     pbrTestRenderer.properties.SetTexture("_Metalness", Texture.LoadFromFile("pbr/water_stone/metalness.png"))
#     pbrTestRenderer.properties.SetTexture("_AmbientOcclusion", Texture.LoadFromFile("pbr/water_stone/ao.png"))
#     pbrTestRenderer.properties.SetTexture("_ReflectionProbe", skyboxTex)
#     moveAnim = Animation({
#         pbrTest.transform.SetPosition: KeyFrames({0: Vector3(0, 7, -2), 10: Vector3(0, 7, 4)}, Vector3.Lerp),
#         pbrTest.transform.SetRotation: KeyFrames({0: Quaternion(), 5: Quaternion.Eulerf(0, 180, 0)}, Quaternion.Slerp)
#     })
#
#     pbrTest1.AddComponent(pbrTestRenderer.Copy())
#     #pbrTest1.AddComponent(Rotator(Vector3(0, 1, 0), 30))
#     #scene.AddObject(pbrTest1)

    print("=== SCENE ===")
    print(scene)

    print("=== CONTROLS ===")
    print("Move the camera")
    print("     W")
    print("    ASD")
    print("Look Around")
    print("    Drag the mouse")
    print("Go Up")
    print("    Space Bar")
    print("Go Down")
    print("    Left Shift")
    print("Move Faster")
    print("    Left Control")
    print("Toggle Post Processing")
    print("    H")
    print("Toggle Wireframe Mode")
    print("    Y")

    print("-- DEMO ONLY --")
    print("Rotate/Move Terrain")
    print("    Arrows")
    print("Reset Terrain Transform")
    print("    Backspace")

    window.Run()

if __name__ == '__main__':
    glfw.init() # Initialize window system glfw
    main()
    glfw.terminate() # destroy all graphics contexts