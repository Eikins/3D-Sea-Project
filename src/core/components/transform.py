"""
Transform class used for all geometric transforms
@author: Eikins
"""

from src.math.vector3 import Vector3
from src.math.quaternion import Quaternion
from src.math.matrix4 import Matrix4

class Transform:
    """
    Transform of a scene object

    Attributes:
        _parent (Transorm)
        _children (Transform[])
        _position (Vec3)
        _rotation (Quaternion)
        _scale (Vec3)

        __changed (bool)

        _Model (Matrix4x4)
    """

    def __init__(self, parent = None):
        self._parent = parent
        self._children = []
        self._position = Vector3()
        self._rotation = Quaternion()
        self._scale = Vector3(1, 1, 1)
        self.__changed = True
        self._Model = self.GetTRSMatrix()

        if not parent is None:
            parent._children += [self]

    def SetPosition(self, position):
        """ Sets the local position """
        self._position = position
        self.__changed = True

    def SetRotation(self, rotation):
        """ Sets the local rotation """
        self._rotation = rotation
        self.__changed = True

    def SetScale(self, scale):
        """ Sets the local rotation """
        self._scale = scale
        self.__changed = True

    def _ParentChanged(self):
        if(self._parent is None):
            return False
        return self._parent._ParentChanged() or self._parent.__changed

    def GetTRSMatrix(self):
        """ Returns the model matrix for this object """
        if self.__changed:
            
            # self._Model = ...
            self._Model = Matrix4.Translate(self._position) @ Matrix4.Quaternion(self._rotation) @ Matrix4.Scale(self._scale)

            # Hierarchical modeling
            if(not self._parent is None):
                self._Model = self._parent.GetTRSMatrix() @ self._Model
                
            self.__changed = False
        
        elif self._ParentChanged():
            self._Model = self._parent.GetTRSMatrix() @ self._Model

        return self._Model
