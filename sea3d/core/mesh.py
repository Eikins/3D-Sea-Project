"""
Mesh class
@author: Eikins
"""

class Mesh:
    """
    Attributes:
        vertices: float[]
        normals: float[]
        uvs: float[8][]
        indexes: int[]
    """

    def __init__(self, vertices, normals, uvs, indexes):
        self.vertices = vertices
        self.normals = normals
        self.uvs = uvs
        self.indexes = indexes