"""
Renderer component, used to render 3D Models
@author: Eikins
"""

from sea3d.core import Component, Mesh, Material, PropertyBlock


class Renderer(Component):
    
    def __init__(self, mesh:Mesh, material:Material, propertyBlock:PropertyBlock = None):
        super().__init__()
        self.mesh = mesh
        self.material = material
        if propertyBlock is None:
            self.properties = PropertyBlock()