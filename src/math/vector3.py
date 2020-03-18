"""
Vector3 class
@author: Eikins
"""

from numbers import Number
import math

class Vector3:

    def __init__(self, x = 0.0, y = 0.0, z = 0.0):
        self.x = x
        self.y = y
        self.z = z

    def __str__(self):
        return "(" + str(self.x) + ", " + str(self.y) + ", " + str(self.z) + ")" 

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y and self.z == other.z

    def __add__(self, other):
        return Vector3(
            self.x + other.x,
            self.y + other.y,
            self.z + other.z
        )

    def __sub__(self, other):
        return self + (-1 * other)

    def __mul__(self, other):
        """ Product """
        if isinstance(other, Number):
            return Vector3(other * self.x, other * self.y, other * self.z)
        else:
            return Vector3(other.x * self.x, other.y * self.y, other.z * self.z)

    def __rmul__(self, other):
        if isinstance(other, Number):
            return self * other

    def __radd__(self, other):
        return self + other

    def __rsub__(self, other):
        return (-1 * self) + other

    def __truediv__(self, other):
        if isinstance(other, Number):
            return self * (1 / other)

    def Magnitude(self):
        return math.sqrt(self.x * self.x + self.y * self.y + self.z * self.z)

    @staticmethod
    def Normalize(vector):
        mag = vector.Magnitude()
        return vector / mag if mag > 0.0 else vector
