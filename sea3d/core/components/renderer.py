"""
Renderer component, used to render 3D Models
@author: Eikins
"""

from sea3d.core import Component, Mesh


class Renderer(Component):
    
    def __init__(self, mesh:Mesh):
        self.mesh = mesh