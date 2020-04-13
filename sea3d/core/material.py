"""
Material class
@author: Eikins
"""

import numpy as np

from sea3d.core import Texture

from sea3d.math import Vector3

class Material:

    def __init__(self, name:str, vertex:str, frag:str):
        self.name = name
        self.vertex = vertex
        self.fragment = frag
        self.useTessellation = False
        self.tessellationControl = ""
        self.tessellationEvaluation = ""

    def AddTessellation(self, control:str, evaluation:str):
        """
        Add Tessellation stage 
        
        A Tessellation Control Shader (TCS) & Evaluation Shader (TES) are required.
        For more information, visit https://web.engr.oregonstate.edu/~mjb/cs519/Handouts/tessellation.1pp.pdf
        """
        self.useTessellation = True
        self.tessellationControl = control
        self.tessellationEvaluation = evaluation

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name

    def __ne__(self, other):
        return not(self == other)

class PropertyBlock:

    def __init__(self):
        self.floatProperties = dict()
        self.intProperties = dict()
        self.textures = dict()
        self.vec3Properties = dict()
        # Color properties are vec4
        self.colorProperties = dict() 

    def SetTexture(self, name:str, texture:Texture):
        self.textures[name] = texture
        
    def SetInt(self, name:str, value:int):
        self.intProperties[name] = value

    def SetFloat(self, name:str, value:float):
        self.floatProperties[name] = value

    def SetVector3(self, name:str, value:Vector3):
        self.vec3Properties[name] = value
    