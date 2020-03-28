"""
Material class
@author: Eikins
"""

class Material:

    def __init__(self, name:str, vertex:str, frag:str):
        self.name = name
        self.vertex = vertex
        self.fragment = frag
    
    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name

    def __ne__(self, other):
        return not(self == other)

    