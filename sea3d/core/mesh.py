"""
Mesh class
@author: Eikins
"""
import numpy as np
import assimpcy.all as assimpcy

from sea3d.math import NumpyUtils



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