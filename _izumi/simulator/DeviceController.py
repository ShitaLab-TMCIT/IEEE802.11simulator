import typing,dataclasses

import numpy as np

import SimEvent as sime
import TransData as trad
import SimCore as simc
import PhysicalManager as phym
import Simulator as sim


#class
class DeviceController:
    Null : 'DeviceController' = None

    @property
    def Sim(self) -> 'sim.Simulator':
        return sim.Simulator.Instance

    @property
    def Phy(self) -> 'phym.PhysicalManager':
        return phym.PhysicalManager.Instance


    def __init__(self) -> None:
        if (self.Null is None):
            DeviceController.Null = self
        self._name      : str = ''
        self._position  : simc.Vector3 = simc.Vector3(0.0,0.0,0.0)
        self._nextEvent : sime.SimEvent = sime.SimEvent.Null
        self._queue     : typing.List[typing.Callable[['DeviceController'],None]] = []
        self._transData : trad.TransData = trad.TransData.Null


    @property
    def name(self) -> str:
        return self._name


    @property
    def position(self) -> 'simc.Vector3':
        return self._position


    @property
    def nextEvent(self) -> 'sime.SimEvent':
        return self._nextEvent

    @nextEvent.setter
    def nextEvent(self,value:'sime.SimEvent'):
        self._nextEvent = value


    @property
    def transData(self) -> 'trad.TransData':
        return self._transData

    @transData.setter
    def transData(self,value:'trad.TransData'):
        def _(dev:DeviceController):
            dev._transData = value
            dev.BookEvent(sime.PhysicalEvent)

        self._queue.append(_)


    def Event(self, event:'sime.SimEvent', obj:'DeviceController'):
        if (type(event) is sime.UpdateEvent):
            self.Update()
        elif (type(event) is sime.ResetEvent):
            self.Reset()
        elif (type(event) is sime.PhysicalEvent):
            self.Physical()
        pass

    def Update(self):
        while (len(self._queue)>0):
            self._queue.pop()(self)

    def Reset(self):
        self._nextEvent = sime.SimEvent.Null
        self._transData = trad.TransData.Null
        pass

    def Physical(self):
        pass

    def BookEvent(
            self,
            event:typing.Type['sime.SimEvent'],
            *args,
            target:'sime.EventTarget'=None,
            targets:typing.List['DeviceController']=None
            ) -> None:

        e = event(self.Sim.time,self,*args)
        if (target is not None):
            e.target = target
        if (targets is not None):
            e.targets = targets

        self.Sim.eventQueue.append(e)
