"""
Numpy utilities
@author: Eikins
"""

import numpy as np

# stackoverflow.com/questions/21030391
def Normalize(a, axis = -1, order = 2):
    mag = np.atleast_1d(np.linalg.norm(a, order, axis))
    mag[mag==0] = 1
    return a / np.expand_dims(mag, axis)