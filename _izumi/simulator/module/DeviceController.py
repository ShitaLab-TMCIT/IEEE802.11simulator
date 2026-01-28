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

    _simulator : 'Simulator' = None
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
        return self._simulator

    @property
    def Phy(self) -> 'PhysicalManager':
        return self._physical

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


    def TriggerPhysic(self) -> None:
        self.Sim.TriggerPhysic()


    def EventHandler(self, event:'SimEvent'):
        if   (type(event) is InitEvent):
            self.Init(event)
        elif (type(event) is UpdateEvent):
            self.Update(event)
        elif (type(event) is PhysicalEvent):
            self.Physical(event)
        elif (isinstance(event,ReserveEvent)):
            self.Event(event)
        pass


    def Init    (self, event:'SimEvent'):
        self._simulator = event.author.Sim
        self._nextEvent = SimEvent.Null
        self._transData = TransData.Null

    def Update  (self, event:'SimEvent'):
        while (len(self._queue)>0):
            self._queue.pop()()

    def Physical(self, event:'SimEvent'):
        pass

    def Event   (self, event:'SimEvent'):
        pass