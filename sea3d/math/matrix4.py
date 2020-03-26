"""
Matrix class
@author: Eikins
"""

import numpy as np

from sea3d.math import Vector3, Quaternion

class Matrix4:


    @staticmethod
    def Identity():
        """ Identity matrix """
        return np.identity(4, 'f')

    @staticmethod
    def Translate(vec3):
        """ Translation matrix """
        T = np.identity(4, 'f')
        T[:3, 3] = np.array([vec3.x, vec3.y, vec3.z], 'f')
        return T


    @staticmethod
    def Scale(vec3):
        """ Scale matrix """
        return np.diag((vec3.x, vec3.y, vec3.z, 1))

    @staticmethod
    def Quaternion(q):
        """ Rotation matrix from a quaterion """
        n = Quaternion.Normalize(q)
        xx = n.x * n.x
        yy = n.y * n.y
        zz = n.z * n.z

        xy = n.x * n.y
        xz = n.x * n.z
        xw = n.x * n.w
        yz = n.y * n.z
        yw = n.y * n.w
        zw = n.z * n.w

        return np.array([[1 - 2 * (yy + zz), 2 * (xy - zw), 2 * (xz + yw), 0],
                         [2 * (xy + zw), 1 - 2 * (xx + zz), 2 * (yz - xw), 0],
                         [2 * (xz - yw), 2 * (yz + xw), 1 - 2 * (xx + yy), 0],
                         [0, 0, 0, 1]], 'f')


