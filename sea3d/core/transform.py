"""
Transform class used for all geometric transforms
@author: Eikins
"""

# Python 3.7+
# PEP 563: postponed evaluation of annotations
# Used for typing
from __future__ import annotations

from sea3d.math import Matrix4, Quaternion, Vector3

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

    def __init__(self, parent: Transform = None):
        self._parent = parent
        self._children = []
        self._position = Vector3()
        self._rotation = Quaternion()
        self._scale = Vector3(1, 1, 1)
        self.__changed = True
        self.__notifyChildren = True
        self.__LocalTRS = None
        self.object = None
        self._Model = self.GetTRSMatrix()

        if not parent is None:
            parent._children += [self]

    def MarkForUpdate(self):
        self.__changed = True

    def SetPosition(self, position: Vector3):
        """ Sets the local position """
        self._position = position
        self.__changed = True

    def SetRotation(self, rotation: Quaternion):
        """ Sets the local rotation """
        self._rotation = rotation
        self.__changed = True

    def SetScale(self, scale: Vector3):
        """ Sets the local rotation """
        self._scale = scale
        self.__changed = True

    def Translate(self, translation: Vector3):
        """ Translate the transform """
        self._position += translation
        self.__changed = True

    def Rotate(self, rotation: Quaternion):
        """ Translate the transform """
        self._rotation *= rotation
        self.__changed = True

    def SetParent(self, parent: Transform):
        if not self._parent is None:
            self._parent._children.remove(self)
        self._parent = parent
        parent._children += [self]
        self.__changed = True

    def AddChild(self, child: Transform):
        if not child._parent is None:
            child._parent._children.remove(self)
        child._parent = self
        self._children += [self]
        child.__changed = True

    def _ParentChanged(self) -> bool:
        if(self._parent is None):
            return False
        return self._parent._ParentChanged() or self._parent.__changed

    def RightVector(self):
        vec3 = self._Model[:3, 0]
        return Vector3.Normalize(Vector3(vec3[0], vec3[1], vec3[2]))

    def UpVector(self):
        vec3 = self._Model[:3, 1]
        return Vector3.Normalize(Vector3(vec3[0], vec3[1], vec3[2]))

    def ForwardVector(self):
        vec3 = self._Model[:3, 2]
        return Vector3.Normalize(Vector3(vec3[0], vec3[1], vec3[2]))

    def GetTRSMatrix(self):
        """ Returns the model matrix for this object """
        if self.__changed:
            
            # self._Model = ...
            self.__LocalTRS = Matrix4.Translate(self._position) @ Matrix4.Quaternion(self._rotation) @ Matrix4.Scale(self._scale)

            # Hierarchical modeling
            if self._parent is not None:
                self._Model = self._parent.GetTRSMatrix() @ self.__LocalTRS
            else:
                self._Model = self.__LocalTRS
                
            self.__changed = False
        
        elif self._parent:
            self._Model = self._parent.GetTRSMatrix() @ self.__LocalTRS

        return self._Model
