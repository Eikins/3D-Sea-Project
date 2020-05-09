"""
Mesh class
@author: Eikins
"""
# Python 3.7+
# PEP 563: postponed evaluation of annotations
# Used for typing
from __future__ import annotations

import numpy as np
import assimpcy.all as assimpcy

from sea3d.math import NumpyUtils, Matrix4

class Mesh:
    """
    Attributes:
        vertices: float[]
        normals: float[]
        uvs: float[8][]
        indexes: int[]
    """

    def __init__(self, vertices, normals, uvs, indexes, tangents = None):
        self.vertices = vertices
        self.normals = normals
        self.uvs = uvs
        self.indexes = indexes
        self.tangents = tangents
        # Removed bitangeants, it's faster to compute the cross product in GLSL
        # Than doing the model mat multiplication on an attribute and then normalize
        #self.bitangeants = bitangeants
    
    def ComputeTangents(self, uvChannel:int = 0):
        """ Compute the mesh tangeants using the uvChannel as reference """
        # For each triangle, solve the problem
        self.tangents = np.zeros(self.normals.shape)
        for tri in self.indexes:
            vertices = self.vertices[tri]
            uvs = self.uvs[uvChannel][tri]

            # Edges
            E = vertices[1:] - vertices[0]
            # UV Diff
            dUV = uvs[1:] - uvs[0]

            # Solve the System to get Tangeant and Bitangeant (UV aligned)
            try:
                T = np.linalg.solve(dUV, E)[0]
            except np.linalg.LinAlgError:
                T = np.array([1, 0, 0])
            # Add all the tangeants and then normalize to have influence of all triangles
            self.tangents[tri] += T
            #self.bitangeants[tri] += B

        # Normalize everything
        self.tangents = NumpyUtils.Normalize(self.tangents)
        #self.bitangeants = NumpyUtils.Normalize(self.bitangeants)

    @staticmethod
    def LoadFromFile(file, flip_uvs = True, gen_normals = True, fix_normals = True):
        """ Load resources from file using assimp, return list of Mesh """
        try:
            pp = assimpcy.aiPostProcessSteps
            flags = pp.aiProcess_Triangulate | pp.aiProcess_CalcTangentSpace | pp.aiProcess_MakeLeftHanded   
            if gen_normals:
                flags |= pp.aiProcess_GenSmoothNormals
            if flip_uvs:
                flags |= pp.aiProcess_FlipUVs

            if fix_normals:
                flags |= pp.aiProcess_FixInfacingNormals 
            scene = assimpcy.aiImportFile("assets/models/" + file, flags)
        except assimpcy.AssimpError as exception:
            print('ERROR loading', file + ': ', exception.args[0].decode())
            return []

        meshes = []


        for mesh in scene.mMeshes:

            vertices = mesh.mVertices
            normals = mesh.mNormals
            uvs = [texCoords for texCoords in mesh.mTextureCoords if texCoords is not None]
            
            tangents = mesh.mTangents
            indexes = mesh.mFaces

            loadedMesh = Mesh(vertices, normals, uvs, indexes, tangents)

            if tangents is None:
                loadedMesh.ComputeTangents()
            
            meshes += [loadedMesh]


        return meshes

    @staticmethod
    def Quad(size = (1, 1), offset = (0, 0)):
        """
        Generate a quad mesh (XY)
        """
        w = size[0] / 2
        h = size[1] / 2
        ow = offset[0]
        oh = offset[1]
        vertices = np.array(((-w + ow, h + oh, 0), (-w + ow, -h + oh, 0), (w + ow, -h + oh, 0), (w + ow, h + oh, 0)), 'f')
        normals  = np.array(((0, 0, -1), (0, 0, -1), (0, 0, -1), (0, 0, -1)), 'f')
        tangents = np.array(((1, 0, 0), (1, 0, 0), (1, 0, 0), (1, 0, 0)), 'f')
        uvs  = np.array(((0, 0), (0, 1), (1, 1), (1, 0)), 'f') # Flipped uvs

        indexes = np.array(((0, 1, 2), (0, 2, 3)), 'u4')
        return Mesh(vertices, normals, [uvs], indexes, tangents)

    @staticmethod
    def Plane(size = (10, 10), count = (2, 2), repeat_uv = False):
        """
        Generate a XZ plane
        """

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

    @staticmethod
    def Transform(mesh:Mesh, transformMatrix:Matrix4):
        """
        Apply the transform Matrix to the mesh vertices, normals and tangents.
        /!\ This should never be done in realtime /!\ 
        This helps to either modify the offset, or to combine meshes
        """
        vertices = np.array([np.array(transformMatrix @ np.append(vertex, 1.0))[0:3] for vertex in mesh.vertices])
        normals = np.array([np.array(transformMatrix @ np.append(normal, 0.0))[0:3] for normal in mesh.normals])
        tangents = np.array([np.array(transformMatrix @ np.append(tangent, 0.0))[0:3] for tangent in mesh.tangents])
        return Mesh(vertices, normals, [np.copy(mesh.uvs[0])], np.copy(mesh.indexes), tangents)

    @staticmethod
    def Combine(mesh1:Mesh, mesh2:Mesh):
        """
        Combine twos mesh in one
        Be careful, the meshes must have the same textures !
        """
        firstIndex = len(mesh1.vertices)
        vertices = np.concatenate((mesh1.vertices, mesh2.vertices))
        normals = np.concatenate((mesh1.normals, mesh2.normals))
        tangents = np.concatenate((mesh1.tangents, mesh2.tangents))
        uvs = np.concatenate((mesh1.uvs[0], mesh2.uvs[0]))
        indexes = np.concatenate((mesh1.indexes, mesh2.indexes + firstIndex))
        return Mesh(vertices, normals, [uvs], indexes, tangents)

