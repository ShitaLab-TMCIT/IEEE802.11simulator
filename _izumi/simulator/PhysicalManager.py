
import dataclasses,typing,math,copy

import numpy

import SimCore as simc
import DeviceController as devc
import TransData as trad
import Simulator as sim

import TransData,SimCore,DeviceController



# class

class PhysicalManager:
    Instance : 'PhysicalManager' = None

    @property
    def Sim(self) -> 'sim.Simulator':
        return sim.Simulator.Instance

    def __init__(self):
        PhysicalManager.Instance = self

    def CulcDistance(self,dev1:'devc.DeviceController',dev2:'devc.DeviceController') -> float:
        vec1 = dev1.position
        vec2 = dev2.position
        return math.sqrt(
            (vec2[0] - vec1[0])**2 +
            (vec2[1] - vec1[1])**2 +
            (vec2[2] - vec1[2])**2
        )

    def Sense(self,dev:'devc.DeviceController') -> 'trad.TransData':
        l : typing.List[trad.TransData] = []
        for i in self.Sim.devices:
            if (i is dev):
                continue
            elif (i.transData is trad.TransData.Null):
                continue
            else:
                l.append(i.transData)

        if (len(l)>1):
            return TransData.TransData(
                DeviceController.DeviceController.Null,
                DeviceController.DeviceController.Null,
                0,0,100,
                {}
            )
        elif (len(l)==1):
            data = copy.deepcopy(l[0])
            data._power = 100
            return data
        else:
            return TransData.TransData.Null
