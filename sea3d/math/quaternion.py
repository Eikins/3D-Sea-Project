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