from SimCore import Vector3
from TransData import TransData
from SimEvent import SimEvent,UpdateEvent,InitEvent,PhysicalEvent,EventTarget,ReserveEvent
from DeviceController import DeviceController
from PhysicalManager import PhysicalManager
from Simulator import Simulator

TransData()
SimEvent()
DeviceController()
PhysicalManager()
Simulator()

TransData.Null._author = DeviceController.Null
TransData.Null._target = DeviceController.Null

SimEvent.Null._author = DeviceController.Null

DeviceController.Null._nextEvent = SimEvent.Null
DeviceController.Null._transData = TransData.Null

Simulator.SimDev._nextEvent = SimEvent.Null
Simulator.SimDev._transData = TransData.Null
