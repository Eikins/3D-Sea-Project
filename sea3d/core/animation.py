"""
Animation data classes
@author: Eikins
"""

import bisect

class KeyFrames:

    def __init__(self, values, interpolate_func):
        # Convert to list of pairs
        if isinstance(values, dict):
            values = values.items()

        keyframes = sorted(((key[0], key[1]) for key in values))
        self.times, self.values = zip(*keyframes)  # pairs list -> 2 lists
        self.interpolate = interpolate_func
        self.start = self.times[0]
        self.end = self.times[-1]
        self.duration = self.end - self.start

    def Evaluate(self, time:float):
        # Check boundaries
        if time <= self.start:
            return self.values[0]
        if time >= self.end:
            return self.values[-1]

        # Get the index of the left neighbour
        index = bisect.bisect_left(self.times, time) - 1
        # Compute interpolation fractional value
        t0 = self.times[index]
        t1 = self.times[index + 1]
        t = (time - t0) / (t1 - t0)
        # Interpolate
        return self.interpolate(self.values[index], self.values[index + 1], t)

class Animation:

    """
    An animation is a set of property linked to keyframes
    The idea is to bind properties to keyframe, as for example

    Example :

    properties = {
        self.transform.SetPosition: KeyFrames({0: Vector3(0, 0, 0), 10: Vector3(10, 0, 0)}, Vector3.Lerp),
        self.transform.SetRotation: KeyFrames({0: Quaternion.identity, 10: Quaternion.AxisAngle(...)}, Quaternion.Slerp)
    }
    """

    def __init__(self, animation_channels):
        """
        An animation is a set of property linked to keyframes
        The idea is to bind properties to keyframe, as for example

        Example :

        channels = {
            self.transform.SetPosition: KeyFrames({0: Vector3(0, 0, 0), 10: Vector3(10, 0, 0)}, Vector3.Lerp),
            self.transform.SetRotation: KeyFrames({0: Quaternion.identity, 10: Quaternion.AxisAngle(...)}, Quaternion.Slerp)
        }
        """
        self.channels = animation_channels
        self.start = min([kf.start for kf in self.channels.values()])
        self.end = max([kf.end for kf in self.channels.values()])

    def Evaluate(self, time:float):
        for prop, keyframes in self.channels.items():
            prop(keyframes.Evaluate(time))

