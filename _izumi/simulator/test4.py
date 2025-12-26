from pack import Simulator
from CSMACA_DeviceController import (
    CSMACA_DeviceController,
    CSMACA_AP_Controller,
    CSMACA_STA_Controller,
    TransRate,
    IEEE802dot11Version
)

from concurrent.futures import ProcessPoolExecutor
import time


def run_one(rate_val,ver, seed, duration, num):
    rate = TransRate(rate_val)
    version = IEEE802dot11Version(ver)

    #Simulator.Instance.Reset()
    Simulator()
    Simulator.Instance.SetRandomSeed(seed)
    Simulator.Instance.SetProperty('version', version)

    ap = CSMACA_AP_Controller()
    ap._rate = rate
    ap._name = 'AP'
    Simulator.Instance.devices.append(ap)

    for i in range(num):
        sta = CSMACA_STA_Controller()
        sta._target = ap
        sta._rate = rate
        sta._name = f'STA{i}'
        Simulator.Instance.devices.append(sta)

    start = time.time()
    Simulator.Instance.Simulate(duration)
    lap = time.time() - start

    ip = udp = success = 0
    for dev in Simulator.Instance.devices:
        if isinstance(dev, CSMACA_DeviceController):
            ip += sum(data.get('IP', 0) for data in dev.sentData)
            udp += sum(data.get('UDP', 0) for data in dev.sentData)
            success += len(dev.sentData)

    return rate_val, lap, ip, udp, success


if __name__ == "__main__":   # ← ★これが絶対に必要

    rates = [
        TransRate.r6Mbps,
        TransRate.r9Mbps,
        TransRate.r12Mbps,
        TransRate.r18Mbps,
        TransRate.r24Mbps,
        TransRate.r36Mbps,
        TransRate.r48Mbps,
        TransRate.r54Mbps
    ]

    count = 10
    duration = 60*1_000_000
    num = 70
    version = IEEE802dot11Version.a

    tasks = []
    seed = 0
    for rate in rates:
        for _ in range(count):
            tasks.append((int(rate), version.value, seed, duration, num))
            seed += 1

    all_result = {}

    with ProcessPoolExecutor() as exe:
        futures = [exe.submit(run_one, *t) for t in tasks]

        for f in futures:
            rate, lap, ip, udp, success = f.result()
            all_result.setdefault(rate, []).append((lap, ip, udp, success))

    final = {}
    for rate, values in all_result.items():
        L = [v[0] for v in values]
        IP = [v[1] for v in values]
        UDP = [v[2] for v in values]
        S = [v[3] for v in values]

        final[rate] = {
            'lap_time': (sum(L)/len(L)),
            'IP': (sum(IP)/len(IP))/duration,
            'UDP': (sum(UDP)/len(UDP))/duration,
            'success': (sum(S)/len(S))
        }

    d = {
        'version': str(version),
        'duration' : duration,
        'device' : num,
        'count' : count,
        'result' : final
    }

    import os, json, datetime
    path = os.path.join(os.path.dirname(__file__),'result',f'test{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}.json')
    with open(path,'w',encoding='utf-8') as f:
        json.dump(d,f,indent=4,ensure_ascii=False)
