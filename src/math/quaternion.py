from numbers import Number
import math

from src.math.vector3 import Vector3

class Quaternion:

    def __init__(self, x = 0.0, y = 0.0, z = 0.0, w = 1.0):
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
                self.x*other.w   +self.w*other.x   -self.z*other.y   +self.y*other.z,
                self.y*other.w   +self.z*other.x   +self.w*other.y   -self.x*other.z,
                self.z*other.w   -self.y*other.x   +self.x*other.y   +self.w*other.z,
                self.w*other.w   -self.x*other.x   -self.y*other.y   -self.z*other.z
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

    @staticmethod
    def AxisAngle(axis, angle):
        theta = math.radians(angle)
        sin = math.sin(theta / 2)
        cos = math.cos(theta / 2)
        v = sin * Vector3.Normalize(axis)
        return Quaternion(
            v.x,
            v.y,
            v.z,
            cos
        )
