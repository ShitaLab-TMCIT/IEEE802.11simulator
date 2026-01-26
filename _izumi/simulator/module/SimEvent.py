import enum,typing

if typing.TYPE_CHECKING:
    from .DeviceController import DeviceController




class EventTarget(enum.Enum):
    Null      = enum.auto()
    Author    = enum.auto()
    BroadCast = enum.auto()
    Custom    = enum.auto()


class SimEvent:
    Null : 'SimEvent' = None

    @typing.overload
    def __init__(self,time:int,author:'DeviceController'):...

    def __init__(self,time:int = 0,author:'DeviceController' = None):
        from .DeviceController import DeviceController
        self._time    : int = time
        self._author  : DeviceController = author if author is not None else DeviceController.Null
        self._target  : EventTarget = EventTarget.Author
        self._targets : typing.List['DeviceController'] = []

    @property
    def time(self) -> int:
        return self._time

    @property
    def author(self) -> 'DeviceController':
        return self._author

    @property
    def target(self) -> 'EventTarget':
        return self._target

    @target.setter
    def target(self,value:'EventTarget') -> None:
        self._target = value

    @property
    def targets(self) -> typing.List['DeviceController']:
        return self._targets

    @targets.setter
    def targets(self,value:typing.List['DeviceController']) -> None:
        self._targets = value


    def get_target(self) -> typing.List['DeviceController']:
        if (self._target is EventTarget.Author):
            return [self._author]
        elif (self._target is EventTarget.BroadCast):
            from .Simulator import Simulator
            return Simulator.Instance.devices
        elif (self._target is EventTarget.Custom):
            return self._targets
        else:
            return []

class InitEvent(SimEvent):
    def __init__(self, time, author):
        super().__init__(time, author)
        self._target = EventTarget.BroadCast
    pass

class UpdateEvent(SimEvent):
    def __init__(self, time, author):
        super().__init__(time, author)
        self._target = EventTarget.BroadCast
    pass

class PhysicalEvent(SimEvent):
    def __init__(self, time, author):
        super().__init__(time, author)
        self._target = EventTarget.BroadCast
    pass

class ReserveEvent(SimEvent):
    def __init__(self, time, author):
        super().__init__(time, author)
        self._target = EventTarget.Author
