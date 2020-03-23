import unittest

from sea3d.math.quaternion import Quaternion
from sea3d.math.vector3 import Vector3
from sea3d.math.matrix4 import Matrix4

class TestMatrix(unittest.TestCase):

    def test_matrix(self):
        print("Identity :")
        print(Matrix4.Identity())

        print("\nTranslation of (0, 2, 4) :")
        print(Matrix4.Translate(Vector3(0, 2, 4)))

        print("\nTranslation of (-4, 0, 1) :")
        print(Matrix4.Translate(Vector3(-4, 0, 1)))

        print("\nScale of (2.5, 2, 1) :")
        print(Matrix4.Scale(Vector3(2.5, 2, 1)))

        print("\nRotation of ((0, 1, 0), 45°) :")
        print(Matrix4.Quaternion(Quaternion.AxisAngle(Vector3(0, 1, 0), 45)))

        print("\nRotation of ((-1, 1, 0), -30°) :")
        print(Matrix4.Quaternion(Quaternion.AxisAngle(Vector3(-1, 1, 0), -30)))

if __name__ == '__main__':
    unittest.main()