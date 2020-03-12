import unittest

from src.math.quaternion import Quaternion
from src.math.vector3 import Vector3

class TestMath(unittest.TestCase):

    def test_quaternion(self):

        ##### VECTOR3 #####
        v1 = Vector3(1, 2, 3)
        v2 = Vector3(5, 0, 0)

        self.assertEqual(2 * v1, Vector3(2, 4, 6))
        self.assertEqual(v1 * 2, Vector3(2, 4, 6))
        self.assertEqual(v1 * v1, Vector3(1, 4, 9))
        self.assertEqual(Vector3.Normalize(v2), Vector3(1, 0, 0))

        ##### QUATERNION #####
        i = Quaternion(1, 0, 0, 0)
        j = Quaternion(0, 1, 0, 0)
        k = Quaternion(0, 0, 1, 0)

        self.assertEqual(i * i, -1)
        self.assertEqual((3 * i - k) * (2 + j + k), 1 + 7 * i - 3 * j + k)


if __name__ == '__main__':
    unittest.main()