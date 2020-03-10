class Component:
    """
    Base component class for scene objects

    Attributes:
        _object (SceneObject)
    """

class Behaviour(Component):
    """
    Base behaviour class for scene objects
    Behaviour components have multiple callbacks :
    - Start
    - Update
    """

    def Start(self):
        pass

    def Update(self):
        pass
    