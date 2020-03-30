"""
OpenGL Window stuff
@author: Eikins
"""
import os
import OpenGL.GL as GL

import numpy as np

from sea3d.core import Texture, TextureFilter, TextureWrapMode
from sea3d.opengl import GLStdVBO

class GLTextureAtlas:

    WrapModes = {
        TextureWrapMode.REPEAT: GL.GL_REPEAT,
        TextureWrapMode.MIRRORED_REPEAT: GL.GL_MIRRORED_REPEAT,
        TextureWrapMode.CLAMP_TO_BORDER: GL.GL_CLAMP_TO_BORDER,
        TextureWrapMode.CLAMP_TO_EDGE: GL.GL_CLAMP_TO_EDGE
    }

    Filters = {
        TextureFilter.POINT: GL.GL_NEAREST,
        TextureFilter.LINEAR: GL.GL_LINEAR
    }

    MipFilters = {
        (TextureFilter.POINT, TextureFilter.POINT): GL.GL_NEAREST_MIPMAP_NEAREST,
        (TextureFilter.LINEAR, TextureFilter.POINT): GL.GL_LINEAR_MIPMAP_NEAREST,
        (TextureFilter.POINT, TextureFilter.LINEAR): GL.GL_NEAREST_MIPMAP_LINEAR,
        (TextureFilter.LINEAR, TextureFilter.LINEAR): GL.GL_LINEAR_MIPMAP_LINEAR
    }

    def __init__(self):
        self.glid = None
        self.texturesToBake = []
        self.textures = dict()

    def AddTexture(self, texture:Texture):
        self.texturesToBake += [texture]

    def BakeTextures(self):
        
        if len(self.texturesToBake) == 0:
            return

        textureIDs = [GL.glGenTextures(len(self.texturesToBake))]
        for index, glid in enumerate(textureIDs):
            tex:Texture = self.texturesToBake[index]
            height, width = tex.data.shape[0:2]

            GL.glBindTexture(GL.GL_TEXTURE_2D, glid)
            GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, GL.GL_RGBA, width, height, 0, GL.GL_RGBA, GL.GL_UNSIGNED_BYTE, tex.data)
            GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S, GLTextureAtlas.WrapModes[tex.wrapMode])
            GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_T, GLTextureAtlas.WrapModes[tex.wrapMode])
            GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GLTextureAtlas.Filters[tex.filter])

            if tex.useMipmaps:
                GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GLTextureAtlas.MipFilters[(tex.mipLevelFilter, tex.mipMapFilter)])
                GL.glGenerateMipmap(GL.GL_TEXTURE_2D)
            else:
                GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GLTextureAtlas.Filters[tex.filter])

            self.textures[tex] = glid

        self.texturesToBake.clear()

    def DeleteTexture(self, texture:Texture):
        tex = self.textures.pop(texture)
        if tex:
            GL.glDeleteTextures(tex)

    def __del__(self):
        GL.glDeleteTextures(np.fromiter(self.textures.values(), 'u4'))