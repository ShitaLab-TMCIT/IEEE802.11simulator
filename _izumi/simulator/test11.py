import time,typing,random

from module import Simulator
from CSMACA_DeviceController import (
    CSMACA_DeviceController,
    CSMACA_AP_Controller,
    CSMACA_STA_Controller,
    TransRate,
    IEEE802dot11Version
)


if __name__ == "__main__":
    simulator = Simulator()
    simulator.SetRandomSeed(0)
    simulator.SetProperty('version', IEEE802dot11Version.a)

    ap = CSMACA_AP_Controller('AP')
    ap.rate = TransRate.r54Mbps
    simulator.devices.append(ap)

    for i in range(100):
        sta = CSMACA_STA_Controller(f'STA{i}')
        sta.target = ap
        sta.rate = TransRate.r54Mbps
        simulator.devices.append(sta)

    for i in range(100):
        simulator.Simulate(1_000_000*10)
        print(f'COMPLETE : {i}')