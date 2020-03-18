from src.core.components.transform import Transform
from src.core.components.component import Behaviour

class SceneObject:

    def __init__(self, parent : Transform = None):
        self.transform = Transform(parent)
        self.components = []

    def Start(self):
        for comp in self.components:
            if isinstance(comp, Behaviour):  
                comp.Start()

    def Update(self):
        for comp in self.components:
            if isinstance(comp, Behaviour):
                comp.Update()