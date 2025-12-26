import enum,typing

import numpy as np


class Vector3:
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    @typing.overload
    def __init__(self, x: float, y: float, z: float):...

    @typing.overload
    def __init__(self, np_array: np.ndarray):...

    def __init__(self, *args):
        if (len(args) == 1):
            self.x = args[0][0]
            self.y = args[0][1]
            self.z = args[0][2]
        elif (len(args) == 3):
            self.x = args[0]
            self.y = args[1]
            self.z = args[2]

    @property
    def np(self) -> np.ndarray:
        return np.array([self.x,self.y,self.z])
