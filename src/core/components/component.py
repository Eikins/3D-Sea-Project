"""
Component and Behaviour class used for objects logic
@author: Eikins
"""

from src.core.scene import SceneObject

class Component:
    """
    Base component class for scene objects

    Attributes:
        _object (SceneObject)
    """

    def __init__(self, sceneObject: SceneObject):
        self._object = sceneObject


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
    