"""
Scene management
Component and Behaviour class used for objects logic
@author: Eikins
"""

# Python 3.7+
# PEP 563: postponed evaluation of annotations
# Used for typing
from __future__ import annotations

from sea3d.core.components.transform import Transform

class SceneObject:

    def __init__(self, name:str, parent: Transform = None):
        self.name = name
        self.transform = Transform(parent)
        self.components = []

    def AddComponent(self, component: Component):
        if component.object is None:
            component.object = self
            self.components += [component]

    def GetComponent(self, component:type):
        for comp in self.components:
            if isinstance(comp, component):
                return comp

    def GetComponents(self, types):
        comps = []
        for comp in self.components:
            if isinstance(comp, types):
                comps += [comp]
        return comps

    def Start(self):
        for comp in self.components:
            if isinstance(comp, Behaviour):  
                comp.Start()

    def Update(self):
        for comp in self.components:
            if isinstance(comp, Behaviour):
                comp.Update()

class Scene:

    def __init__(self, name:str):
        self.name = name
        self.objects = []

    def AddObject(self, object:SceneObject):
        self.objects += [object]

    def Start(self):
        for obj in self.objects:
            obj.Start()

    def Update(self):
        for obj in self.objects:
            obj.Update()

class Component:
    """
    Base component class for scene objects

    Attributes:
        object (SceneObject)
    """

    def __init__(self):
        self.object:SceneObject = None


class Behaviour(Component):
    """
    Base behaviour class for scene objects
    Behaviour components have multiple callbacks :
    - Start
    - Update
    """

    def Start(self):
        pass

    def Update(self):
        pass
    