import typing,uuid,dataclasses

import numpy as np

import SimEvent as sime
import TransData as trad
import SimCore as simc
import PhysicalManager as phym
import Simulator as sim


#class
class DeviceController:
    Null : 'DeviceController' = None

    _physical  : 'phym.PhysicalManager' = None

    _ID        : str = ''
    _name      : str = ''
    _position  : 'simc.Vector3' = None
    _transData : 'trad.TransData' = None
    _nextEvent : 'sime.ReserveEvent' = None
    _queue     : list[typing.Callable[[],None]] = []

    
    def __init__(self,name:str='',position:'simc.Vector3'=None) -> None:
        if (self.Null is None):
            DeviceController.Null = self
        
        self._ID        = uuid.uuid4().hex
        self._name      = name
        self._position  = simc.Vector3(0,0,0) if position is None else position
        self._nextEvent = sime.SimEvent.Null
        self._transData = trad.TransData.Null
        self._queue     = []

    def simPropertySetter(func):
        def _(self:'DeviceController',*args,**kwargs):
            self._queue.append(lambda:func(self,*args,**kwargs))
        return _

    @property
    def Sim(self) -> 'sim.Simulator':
        return sim.Simulator.Instance

    @property
    def Phy(self) -> 'phym.PhysicalManager':
        return self._physical
    
    @Phy.setter
    def Phy(self,value:'phym.PhysicalManager'):
        self._physical = value

    @property
    def ID(self) -> str:
        return self._ID

    @property
    def name(self) -> str:
        return self._name

    @property
    def position(self) -> 'simc.Vector3':
        return self._position
    
    @position.setter
    @simPropertySetter
    def position(self,value:str):
        self._position = value

    @property
    def transData(self) -> 'trad.TransData':
        return self._transData

    @transData.setter
    @simPropertySetter
    def transData(self,value:'trad.TransData'):
        self._transData = value
        self.TriggerPhysic()

    @property
    def nextEvent(self) -> 'sime.ReserveEvent':
        return self._nextEvent

    @nextEvent.setter
    def nextEvent(self,value:'sime.ReserveEvent'):
        self._nextEvent = value

    
    def Event(self, event:'sime.SimEvent', obj:'DeviceController'):
        if (type(event) is sime.UpdateEvent):
            self.Update()
        elif (type(event) is sime.InitEvent):
            self.Reset()
        elif (type(event) is sime.PhysicalEvent):
            self.Physical()
        pass

    def Update(self):
        while (len(self._queue)>0):
            self._queue.pop()()

    def Reset(self):
        self._nextEvent = sime.SimEvent.Null
        self._transData = trad.TransData.Null
        pass

    def Physical(self):
        pass

    def TriggerPhysic(self) -> None:
        self.Sim.TriggerPhysic()