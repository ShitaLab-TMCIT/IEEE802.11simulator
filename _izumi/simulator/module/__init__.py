import os
os.environ['PATH'] = os.path.abspath(os.path.dirname(__file__)) + ';' + os.environ['PATH']



from .SimCore import Vector3
from .TransData import TransData
from .SimEvent import SimEvent,UpdateEvent,InitEvent,PhysicalEvent,EventTarget,ReserveEvent
from .DeviceController import DeviceController
from .PhysicalManager import PhysicalManager
from .Simulator import Simulator

TransData.Null = TransData()
TransData.Null._transID = 0
TransData._TransData__transID = 0

SimEvent.Null  = SimEvent()
SimEvent.Null._time = -1

DeviceController.Null = DeviceController('Null')
Simulator()

TransData.Null._author = DeviceController.Null
TransData.Null._target = DeviceController.Null

SimEvent.Null._author = DeviceController.Null

DeviceController.Null._nextEvent = SimEvent.Null
DeviceController.Null._transData = TransData.Null

Simulator.SimDev = DeviceController('Simulator')
Simulator.SimDev._nextEvent = SimEvent.Null
Simulator.SimDev._transData = TransData.Null

__all__ = [
    'Vector3',
    'TransData',
    'SimEvent',
    'UpdateEvent',
    'InitEvent',
    'PhysicalEvent',
    'EventTarget',
    'ReserveEvent',
    'DeviceController',
    'PhysicalManager',
    'Simulator'
]
