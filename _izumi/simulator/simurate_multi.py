from module import Simulator
from CSMACA_DeviceController import (
    CSMACA_DeviceController,
    CSMACA_AP_Controller,
    CSMACA_STA_Controller,
    TransRate,
    IEEE802dot11Version
)

from concurrent.futures import ProcessPoolExecutor
import time,typing,random



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

    #Simulator.Instance.Reset()
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


def auto(count:int,rate:TransRate,version:IEEE802dot11Version,duration:int,num:int,seed:int=0):
    tasks = []
    for _ in range(count):
        tasks.append((version.value,int(rate),num,duration,seed))
        seed += 1

    results : list[Result] = []

    with ProcessPoolExecutor() as exe:
        futures = [exe.submit(run_one, *t) for t in tasks]

        for f in futures:
            results.append(f.result())

    return results


if __name__ == "__main__":
    import json,os,datetime

    rand = random.Random(0)

    count = 16
    duration = int(120*1_000_000)
    version = IEEE802dot11Version.a

    rate_list = [
        TransRate.r6Mbps,
        TransRate.r9Mbps,
        TransRate.r12Mbps,
        TransRate.r18Mbps,
        TransRate.r24Mbps,
        TransRate.r36Mbps,
        TransRate.r48Mbps,
        TransRate.r54Mbps
        ]
    rate_list = [TransRate.r54Mbps]
    
    num_list = [2,5,10,20,30,40,50,60,70,80,90,100]
    num_list = [100]

    all_results = {'version':version.name,'duration':duration,'result':{}}
    for num in num_list:
        all_results['result'][num] = {}
        for rate in rate_list:
            all_results['result'][num][rate.name] = auto(count,rate,version,duration,num,seed=rand.randint(0,1000000))
            
        path = os.path.join(os.path.dirname(__file__),'result',f'result{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}.json')
        with open(path,'w',encoding='utf-8') as f:
            json.dump({'version':version.name,'duration':duration,'num':num,'result':all_results['result'][num][rate.name]},f,indent=4,ensure_ascii=False)

    path = os.path.join(os.path.dirname(__file__),'all_result',f'result{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}.json')
    with open(path,'w',encoding='utf-8') as f:
        json.dump(all_results,f,indent=4,ensure_ascii=False)
    
