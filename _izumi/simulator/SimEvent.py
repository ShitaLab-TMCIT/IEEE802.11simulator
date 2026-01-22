import dataclasses,enum,typing

import Simulator as sim
import DeviceController as devc




class EventTarget(enum.Enum):
    Null      = enum.auto()
    Author    = enum.auto()
    BroadCast = enum.auto()
    Custom    = enum.auto()


class SimEvent:
    Null : 'SimEvent' = None

    @typing.overload
    def __init__(self,time:int,author:'devc.DeviceController'):...

    def __init__(self,time:int = 0,author:'devc.DeviceController' = None):
        if (self.Null is None):
            self._time    : int = -1
            self._author  : devc.DeviceController = None
            self._target  : EventTarget = EventTarget.Null
            self._targets : typing.List[devc.DeviceController] = []
            SimEvent.Null = self
        else:
            self._time    : int = time
            self._author  : devc.DeviceController = author if author is not None else devc.DeviceController.Null
            self._target  : EventTarget = EventTarget.Author
            self._targets : typing.List[devc.DeviceController] = []

    @property
    def time(self) -> int:
        return self._time

    @property
    def author(self) -> 'devc.DeviceController':
        return self._author

    @property
    def target(self) -> 'EventTarget':
        return self._target

    @target.setter
    def target(self,value:'EventTarget') -> None:
        self._target = value

    @property
    def targets(self) -> typing.List['devc.DeviceController']:
        return self._targets

    @targets.setter
    def targets(self,value:typing.List['devc.DeviceController']) -> None:
        self._targets = value


    def get_target(self) -> typing.List['devc.DeviceController']:
        if (self._target is EventTarget.Author):
            return [self._author]
        elif (self._target is EventTarget.BroadCast):
            return sim.Simulator.Instance.devices
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