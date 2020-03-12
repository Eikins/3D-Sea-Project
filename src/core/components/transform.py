"""
Transform class used for all geometric transforms
@author: Eikins
"""

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
        self._position = None
        self._rotation = None
        self._scale = None
        self._Model = None
        self.__changed = False

    def SetPosition(self, position):
        """ Sets the local position """
        self.position = position
        self.__changed = True

    def SetRotation(self, rotation):
        """ Sets the local rotation """
        self.rotation = rotation
        self.__changed = True

    def SetScale(self, scale):
        """ Sets the local rotation """
        self.scale = scale
        self.__changed = True

    def GetMatrix4x4(self):
        """ Returns the model matrix for this object """
        if self.__changed:
            
            # self._Model = ...

            # Hierarchical modeling
            if(not self._parent is None):
                self._Model = self._parent.GetMatrix4x4() @ self._Model
                
            self.__changed = False

        return self._Model
