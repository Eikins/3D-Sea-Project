import unittest

from sea3d.core import KeyFrames

def lerp(a, b, t):
    return a + (b - a) * t

class TestMath(unittest.TestCase):

    def test_keyframes(self):

        keyframes = KeyFrames({0: 1, 3: 7, 6: 20}, lerp)

        print(keyframes.times)
        print(keyframes.values)

        print("Keyframes are {0: 1, 3: 7, 6: 20}")
        print("Value at 1.5 : ", keyframes.Evaluate(1.5))
        print("Value at -1 : ", keyframes.Evaluate(-1))
        print("Value at 5 : ", keyframes.Evaluate(5))
        print("Value at 7 : ", keyframes.Evaluate(7))

if __name__ == '__main__':
    unittest.main()