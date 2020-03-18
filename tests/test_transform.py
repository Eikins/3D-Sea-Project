import unittest
import numpy as np

from src.math.quaternion import Quaternion
from src.math.vector3 import Vector3
from src.core.components.transform import Transform

class TestTransform(unittest.TestCase):

    def test_transform(self):
        t0 = Transform(None)
        t11 = Transform(t0)
        t12 = Transform(t0)

        t0.SetPosition(Vector3(1, 0, 0))
        # t0.SetRotation(Quaternion.AxisAngle(Vector3(1, 0, 0), 90))
        t0.SetRotation(Quaternion.Euler(Vector3(90, 0, 0)))
        t11.SetPosition(Vector3(0, 1, 0))
        t12.SetPosition(Vector3(0, 0, 1))

        print(t12.GetTRSMatrix() @ np.array([0, 0, 0, 1]))

if __name__ == '__main__':
    unittest.main()