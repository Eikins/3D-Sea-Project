"""
Scene management
Component and Behaviour class used for objects logic
@author: Eikins
"""

# Python 3.7+
# PEP 563: postponed evaluation of annotations
# Used for typing
from __future__ import annotations

from sea3d.core import Transform, Layers

class SceneObject:

    def __init__(self, name:str, parent: Transform = None):
        self.name = name
        self.transform = Transform(parent)
        self.transform.object = self
        self.components = []
        self.layer = Layers.DEFAULT # Default Layer

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

    def ToStr(self, indentLevel:int):
        s = " " * indentLevel + self.name + " "
        for comp in self.components:
            s += "[" + type(comp).__name__ + "]"
        s += "\n"
        for child in self.transform._children:
            s += child.object.ToStr(indentLevel + 4)
        return s


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

    def GetAllComponents(self):
        # TODO : Change this terrible search
        comps = []
        for obj in self.objects:
            for comp in obj.components:
                comps += [comp]
        return comps

    def Find(self, name:str):
        for o in self.objects:
            if o.name == name:
                return o

    def __str__(self):
        sceneStr = self.name + "\n-----------\n"
        for o in self.objects:
            obj:SceneObject = o
            if obj.transform._parent is None:
                sceneStr += obj.ToStr(0)
        return sceneStr

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

    def __init__(self):
        super().__init__()

    def Start(self):
        pass

    def Update(self):
        pass
    