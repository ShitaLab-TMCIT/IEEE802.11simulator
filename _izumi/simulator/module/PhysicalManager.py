
import math,typing

if typing.TYPE_CHECKING:
    from .Simulator import Simulator
    from .DeviceController import DeviceController



# class

class PhysicalManager:

    def __init__(self):
        pass

    @classmethod
    def CulcDistance(cls,dev1:'DeviceController',dev2:'DeviceController') -> float:
        vec1 = dev1.position
        vec2 = dev2.position
        return math.sqrt(
            (vec2[0] - vec1[0])**2 +
            (vec2[1] - vec1[1])**2 +
            (vec2[2] - vec1[2])**2
        )
