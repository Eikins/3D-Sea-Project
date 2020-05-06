"""
Animator component
@author: Eikins
"""

import numpy as np

from sea3d.core import Behaviour, Time, Animation

class Animator(Behaviour):

    def __init__(self, animation, playOnStart = False, loop=False):
        super().__init__()
        self.time = 0.0
        self.animation = animation
        self.playing = playOnStart
        self.loop = loop

    def Start(self):
        self.time = self.animation.start

    def Update(self):
        if self.playing:
            self.time += Time.deltaTime
            self.animation.Evaluate(self.time)

            if(self.time >= self.animation.end):
                if self.loop:
                    self.Replay()
                else:
                    self.Stop()
        
    def Replay(self):
        self.time = self.animation.start

    def Stop(self):
        self.playing = False
        self.time = self.animation.start
    
    def Play(self, animation : Animation):
        self.animation = animation
        self.time = animation.start