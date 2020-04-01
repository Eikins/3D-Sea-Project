"""
Component and Behaviour class used for objects logic
@author: Eikins
"""

from enum import Enum
import numpy as np

from sea3d.core import Component

# TODO : Add Orthogonal camera support
class Camera(Component):

    def __init__(self,
                 fov:float = 60,
                 aspect:float = 16/9,
                 near:float = 0.3,
                 far:float = 1000):
        super().__init__()
        self._fov = fov
        self._aspect = aspect
        self._near = near
        self._far = far
        self.__changed = True
        self._Projection = self.GetProjectionMatrix()

    def SetFOV(self, fov:float):
        self._fov = fov
        self.__changed = True

    def SetAspectRatio(self, aspect:float):
        self._aspect = aspect
        self.__changed = True

    def SetNearPlane(self, near:float):
        self._near = near
        self.__changed = True

    def SetFarPlane(self, far:float):
        self._far = far
        self.__changed = True


    def GetProjectionMatrix(self):
        """ Perspective projection matrix"""
        # Perspective for now

        if self.__changed:
            # Recompute matrix
            scale = 1.0 / np.tan(np.radians(self._fov) / 2)
            # Project along positive values
            near = -self._near
            far = -self._far
            depth = far - near

            m00 = scale / self._aspect
            m11 = scale
            m22 = -(far + near) / depth
            m23 = -2 * far * near / depth

            self._Projection = np.array([[m00,   0,   0,   0],
                                         [  0, m11,   0,   0],
                                         [  0,   0, m22, m23],
                                         [  0,   0,  1,   0]], 'f')

        return self._Projection
    

    