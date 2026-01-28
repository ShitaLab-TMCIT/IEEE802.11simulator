import time,typing,random

from module import Simulator
from CSMACA_DeviceController import (
    CSMACA_DeviceController,
    CSMACA_AP_Controller,
    CSMACA_STA_Controller,
    TransRate,
    IEEE802dot11Version
)

class Result(typing.TypedDict):
    seed:int
    lap:float
    ip:int
    tcp:int
    udp:int
    success:int


def run_one(version_val:int,rate_val:int,num:int,duration:int,seed:int=0) -> Result:
    version = IEEE802dot11Version(version_val)
    rate = TransRate(rate_val)

    simulator = Simulator()
    simulator.SetRandomSeed(seed)
    simulator.SetProperty('version', version)

    ap = CSMACA_AP_Controller('AP')
    ap.rate = rate
    simulator.devices.append(ap)

    for i in range(num):
        sta = CSMACA_STA_Controller(f'STA{i}')
        sta.target = ap
        sta.rate = rate
        simulator.devices.append(sta)

    start = time.time()
    simulator.Simulate(duration)
    lap = time.time() - start

    ip = tcp = udp = success = 0
    for dev in simulator.devices:
        if isinstance(dev, CSMACA_STA_Controller):
            ip  += dev.Total_IP_payload()
            tcp += dev.Total_TCP_payload()
            udp += dev.Total_UDP_payload()
            success += len(dev.sentData)

    print('complete :',rate,num,lap,ip,tcp,udp,success)
    return Result(seed=seed,lap=lap,ip=ip,tcp=tcp,udp=udp,success=success)

if __name__ == "__main__":
    rand = random.Random(0)

    count = 16
    duration = int(120*1_000_000)
    version = IEEE802dot11Version.a


    all_results = {'version':version.name,'duration':duration,'result':{}}
    run_one(version.value,int(TransRate.r54Mbps),100,duration,seed=rand.randint(0,1000000))