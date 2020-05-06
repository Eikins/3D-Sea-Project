"""
Quaternion class
@author: Eikins
"""

# Python 3.7+
# PEP 563: postponed evaluation of annotations
# Used for typing
from __future__ import annotations

from numbers import Number
import math
import numpy as np

from sea3d.math import Vector3

class Quaternion:

    def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 0.0, w: float = 1.0):
        """ w is the real, and x, y, z  are imaginary components """
        self.x = x
        self.y = y
        self.z = z
        self.w = w

    def __str__(self):
        return str(self.w) + " + (" + str(self.x) + "i " + str(self.y) + "j " + str(self.z) + "k)" 

    def __eq__(self, other):
        if isinstance(other, Number):
            return self.w == other
        else:
            return self.x == other.x and self.y == other.y and self.z == other.z and self.w == other.w

    def __add__(self, other):
        if isinstance(other, Number):
            return Quaternion(self.x, self.y, self.z, self.w + other)
        else:
            return Quaternion(
                self.x + other.x,
                self.y + other.y,
                self.z + other.z,
                self.w + other.w
            )

    def __sub__(self, other):
        return self + (-1 * other)

    def __mul__(self, other):
        """ Quaternion multiplications """

        if isinstance(other, Number):
            return Quaternion(other * self.x, other * self.y, other * self.z, other * self.w)
        else:
            return Quaternion(
                x = self.x*other.w   +self.w*other.x   -self.z*other.y   +self.y*other.z,
                y = self.y*other.w   +self.z*other.x   +self.w*other.y   -self.x*other.z,
                z = self.z*other.w   -self.y*other.x   +self.x*other.y   +self.w*other.z,
                w = self.w*other.w   -self.x*other.x   -self.y*other.y   -self.z*other.z
            )

    def __rmul__(self, other):
        if isinstance(other, Number):
            return self * other
        else:
            return other * self

    def __radd__(self, other):
        return self + other

    def __rsub__(self, other):
        return (-1 * self) + other

    def __truediv__(self, other):
        if isinstance(other, Number):
            return self * (1 / other)

    def RightVector(self) -> Vector3:
        # Equivalent to Matrix4.Quaternion(self) * Vector3(1, 0, 0)
        x = self.x
        y = self.y
        z = self.z
        w = self.w

        return Vector3(
            x = 1 - 2 * (y * y + x * x),
            y = 2 * (x * y + z * w),
            z = 2 * (x * z - y * w)
        )

    def UpVector(self) -> Vector3:
        # Equivalent to Matrix4.Quaternion(self) * Vector3(0, 1, 0)
        x = self.x
        y = self.y
        z = self.z
        w = self.w

        return Vector3(
            x = 2 * (x * y - z * w),
            y = 1 - 2 * (x * x + z * z),
            z = 2 * (y * z + x * w)
        )

    def ForwardVector(self) -> Vector3:
        # Equivalent to Matrix4.Quaternion(self) * Vector3(0, 0, 1)
        x = self.x
        y = self.y
        z = self.z
        w = self.w

        return Vector3(
            x = 2 * (x * z + y * w),
            y = 2 * (y * z - x * w),
            z = 1 - 2 * (x * x + y * y)
        )


    @staticmethod
    def Normalize(q: Quaternion) -> Quaternion:
        mag = math.sqrt(q.x * q.x + q.y * q.y + q.z * q.z + q.w * q.w)
        return q / mag if mag > 0.0 else q

    @staticmethod
    def AxisAngle(axis: Vector3, angle: float) -> Quaternion:
        """ Return a quaternion representing the roation around axis of angle """
        theta = math.radians(angle)
        sin = math.sin(theta / 2)
        cos = math.cos(theta / 2)
        v = sin * Vector3.Normalize(axis)
        return Quaternion(
            x = v.x,
            y = v.y,
            z = v.z,
            w = cos
        )

    @staticmethod
    def Eulerf(roll: float = 0.0, pitch: float = 0.0, yaw: float = 0.0) -> Quaternion:
        """ Convert euler angles to quaternion """

        y = math.radians(yaw)
        p = math.radians(pitch)
        r = math.radians(roll)

        cy = math.cos(y * 0.5)
        cp = math.cos(p * 0.5)
        cr = math.cos(r * 0.5)
        sy = math.sin(y * 0.5)
        sp = math.sin(p * 0.5)
        sr = math.sin(r * 0.5)

        return Quaternion(
            x = cy * cp * sr - sy * sp * cr,
            y = sy * cp * sr + cy * sp * cr,
            z = sy * cp * cr - cy * sp * sr,
            w = cy * cp * cr + sy * sp * sr
        )

    @staticmethod
    def Euler(angles: Vector3) -> Quaternion:
        """ Convert euler angles to quaternion """
        return Quaternion.Eulerf(angles.x, angles.y, angles.z)

    @staticmethod
    def Slerp(start : Quaternion, end : Quaternion, progress : float):
        # Only unit quaternions are valid rotations.
        # Normalize to avoid undefined behavior.
        q0 = Quaternion.Normalize(start)
        q1 = Quaternion.Normalize(end)

        # Compute dot product.
        dot = q0.x * q1.x + q0.y * q1.y + q0.z * q1.z + q0.w * q1.w

        # If the dot product is negative, slerp won't take
        # the shorter path. Note that end and -end are equivalent when
        # the negation is applied to all four components. Fix by 
        # reversing one quaternion.

        if dot < 0:
            q1 = -1 * q1
            dot = -dot
        
        theta0 = math.acos(np.clip(dot, -1, 1)) # Angle between input vectors
        theta = theta0 * progress # Angle between q0 and result
        q1 = Quaternion.Normalize(q1 - q0 * dot) # Orthogonalize the basis

        return q0 * math.cos(theta) + q1 * math.sin(theta)
