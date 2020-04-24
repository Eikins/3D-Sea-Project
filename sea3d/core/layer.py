"""
Layer module
@author: Eikins
"""

from enum import IntFlag

class Layers(IntFlag):
    NONE = 0
    DEFAULT = 1
    VFX = 2
    TRANSPARENT = 4
    WATER = 8
    ALL = (2 ** 32) - 1
