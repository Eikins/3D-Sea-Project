"""
Texture classes
@author: Eikins
"""
# Python 3.7+
# PEP 563: postponed evaluation of annotations
# Used for typing
from __future__ import annotations

from enum import Enum

import numpy as np

from PIL import Image  

class TextureWrapMode(Enum):
    REPEAT = 0
    MIRRORED_REPEAT = 1
    CLAMP_TO_BORDER = 2
    CLAMP_TO_EDGE = 3

class TextureFilter(Enum):
    POINT = 0
    LINEAR = 1

class Texture:

    Atlas = dict()

    def __init__(self, name:str, data):
        self.name = name
        self.useMipmaps = True
        self.wrapMode = TextureWrapMode.REPEAT
        self.filter = TextureFilter.LINEAR
        self.mipLevelFilter = TextureFilter.POINT
        self.mipMapFilter = TextureFilter.LINEAR
        self.data = data
        self.isCubemap = False

    def __hash__(self):
        return hash(self.name)

    @staticmethod
    def LoadFromFile(location:str, loadAsCubemap=False, fileExtension=None) -> Texture:

        if location in Texture.Atlas:
            return Texture.Atlas[location]

        if (loadAsCubemap):
            if fileExtension is None:
                fileExtension = ".png"
            data = [
                np.asarray(Image.open("assets/textures/" + location + "/right" + fileExtension).convert("RGB")),
                np.asarray(Image.open("assets/textures/" + location + "/left" + fileExtension).convert("RGB")),
                np.asarray(Image.open("assets/textures/" + location + "/top" + fileExtension).convert("RGB")),
                np.asarray(Image.open("assets/textures/" + location + "/bottom" + fileExtension).convert("RGB")),
                np.asarray(Image.open("assets/textures/" + location + "/front" + fileExtension).convert("RGB")),
                np.asarray(Image.open("assets/textures/" + location + "/back" + fileExtension).convert("RGB"))
            ]
        else:
            data = np.asarray(Image.open("assets/textures/" + location).convert("RGBA"))
        tex = Texture(location, data)
        if loadAsCubemap:
            tex.isCubemap = True
        Texture.Atlas[location] = tex
        return tex



    