"""
Mesh class
@author: Eikins
"""

class Mesh:
    """
    Attributes:
        vertices: float[]
        normals: float[]
        indexes: int[]
    """

    def __init__(self, vertices, normals, indexes):
        self.vertices = vertices
        self.normals = normals
        self.indexes = indexes