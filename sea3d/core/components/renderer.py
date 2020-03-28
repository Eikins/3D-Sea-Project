"""
Renderer component, used to render 3D Models
@author: Eikins
"""

from sea3d.core import Component, Mesh, Material


class Renderer(Component):
    
    def __init__(self, mesh:Mesh, material:Material):
        super().__init__()
        self.mesh = mesh
        self.material = material