import typing,uuid

from .SimEvent import SimEvent,InitEvent,ReserveEvent,UpdateEvent,PhysicalEvent
from .TransData import TransData
from .SimCore import Vector3
from .PhysicalManager import PhysicalManager

if typing.TYPE_CHECKING:
    from .Simulator import Simulator

#class
class DeviceController:
    Null : 'DeviceController' = None

    _physical  : 'PhysicalManager' = None

    _ID        : str = ''
    _name      : str = ''
    _position  : 'Vector3' = None
    _transData : 'TransData' = None
    _nextEvent : 'ReserveEvent' = None
    _queue     : list[typing.Callable[[],None]] = []


    def __init__(self,name:str='',position:'Vector3'=None) -> None:
        self._ID        = uuid.uuid4().hex
        self._name      = name
        self._position  = Vector3(0,0,0) if position is None else position
        self._nextEvent = SimEvent.Null
        self._transData = TransData.Null
        self._queue     = []

        self._physical  = PhysicalManager

    def simPropertySetter(func):
        def _(self:'DeviceController',*args,**kwargs):
            self._queue.append(lambda:func(self,*args,**kwargs))
        return _

    @property
    def Sim(self) -> 'Simulator':
        from .Simulator import Simulator
        return Simulator.Instance

    @property
    def Phy(self) -> 'PhysicalManager':
        return self._physical

    @Phy.setter
    def Phy(self,value:'PhysicalManager'):
        self._physical = value

    @property
    def ID(self) -> str:
        return self._ID

    @property
    def name(self) -> str:
        return self._name

    @property
    def position(self) -> 'Vector3':
        return self._position

    @position.setter
    @simPropertySetter
    def position(self,value:str):
        self._position = value

    @property
    def transData(self) -> 'TransData':
        return self._transData

    @transData.setter
    @simPropertySetter
    def transData(self,value:'TransData'):
        self._transData = value
        self.TriggerPhysic()

    @property
    def nextEvent(self) -> 'ReserveEvent':
        return self._nextEvent

    @nextEvent.setter
    def nextEvent(self,value:'ReserveEvent'):
        self._nextEvent = value


    def Event(self, event:'SimEvent', obj:'DeviceController'):
        if (type(event) is UpdateEvent):
            self.Update()
        elif (type(event) is InitEvent):
            self.Init()
        elif (type(event) is PhysicalEvent):
            self.Physical()
        pass

    def Update(self):
        while (len(self._queue)>0):
            self._queue.pop()()

    def Init(self):
        self._nextEvent = SimEvent.Null
        self._transData = TransData.Null
        pass

    def Physical(self):
        pass

    def TriggerPhysic(self) -> None:
        self.Sim.TriggerPhysic()
