import typing,random,math,enum

from pack import *

DataLength = typing.TypedDict('DataLength',{
    'device':DeviceController,
    'length':int,
    'IP':int,'TCP':int,'UDP':int
    })


class TransRate(enum.IntEnum):
    r6Mbps  = 6
    r9Mbps  = 9
    r12Mbps = 12
    r18Mbps = 18
    r24Mbps = 24
    r36Mbps = 36
    r48Mbps = 48
    r54Mbps = 54

    def ToMinPower(self) -> float:
        if   (self is TransRate.r6Mbps) :return -82.0
        elif (self is TransRate.r9Mbps) :return -81.0
        elif (self is TransRate.r12Mbps):return -79.0
        elif (self is TransRate.r18Mbps):return -77.0
        elif (self is TransRate.r24Mbps):return -74.0
        elif (self is TransRate.r36Mbps):return -70.0
        elif (self is TransRate.r48Mbps):return -66.0
        elif (self is TransRate.r54Mbps):return -65.0
        else                            :return   0.0

    def ToOFDMsymbol(self) -> int:
        return self.value*4

    @property
    def minPower(self) -> float:
        if   (self is TransRate.r6Mbps) :return -82.0
        elif (self is TransRate.r9Mbps) :return -81.0
        elif (self is TransRate.r12Mbps):return -79.0
        elif (self is TransRate.r18Mbps):return -77.0
        elif (self is TransRate.r24Mbps):return -74.0
        elif (self is TransRate.r36Mbps):return -70.0
        elif (self is TransRate.r48Mbps):return -66.0
        elif (self is TransRate.r54Mbps):return -65.0
        else                            :return   0.0

    @property
    def OFDMsymbol(self) -> int:
        return self.value*4
    # +85

class IEEE802dot11Version(enum.Enum):
    a = enum.auto()
    b = enum.auto()
    g = enum.auto()

    @property
    def slotTime(self) -> int:
        return {
            IEEE802dot11Version.a : 9,
            IEEE802dot11Version.b : 20,
            IEEE802dot11Version.g : 20
        }[self]

    @property
    def SIFS(self) -> int:
        return {
            IEEE802dot11Version.a : 16,
            IEEE802dot11Version.b : 10,
            IEEE802dot11Version.g : 10
        }[self]

    @property
    def DIFS(self) -> int:
        return {
            IEEE802dot11Version.a : 34,
            IEEE802dot11Version.b : 50,
            IEEE802dot11Version.g : 56
        }[self]

    @property
    def cwMin(self) -> int:
        return {
            IEEE802dot11Version.a : 4,
            IEEE802dot11Version.b : 5,
            IEEE802dot11Version.g : 4
        }[self]

    @property
    def cwMax(self) -> int:
        return {
            IEEE802dot11Version.a : 10,
            IEEE802dot11Version.b : 10,
            IEEE802dot11Version.g : 10
        }[self]

class IEEE802dot11FrameType(enum.Enum):
    Null = -1
    Ack  = bin( 11101)
    Data = bin(100000)

class IEEE802dot11TransData(TransData):
    _frameType : IEEE802dot11FrameType = IEEE802dot11FrameType.Null
    _rate : TransRate = TransRate.r6Mbps


    @property
    def frameType(self) -> IEEE802dot11FrameType:
        return self._frameType

    @property
    def rate(self) -> TransRate:
        return self._rate

    def __init__(self,
            author:'CSMACA_DeviceController',
            target:'CSMACA_DeviceController',
            startTime:int,
            endTime:int,
            power:float,
            rate:TransRate,
            frameType:IEEE802dot11FrameType,
            data:typing.Dict[str,typing.Any] = {}
            ):
        super().__init__(author,target,startTime,endTime,power,data)
        self._frameType = frameType
        self._rate = rate
    
    def copy(self) -> 'IEEE802dot11TransData':
        return IEEE802dot11TransData(
            self._author,
            self._target,
            self._startTime,
            self._endTime,
            self._power,
            self._rate,
            self._frameType,
            self._data
        )


class CSMACA_Event(SimEvent):
    pass

class CSMACA_SlotEvent(CSMACA_Event):
    slot : int = 0

    def __init__(self, time: int, author: DeviceController, slot:int):
        super().__init__(time, author)
        self.slot = slot
    pass
class CSMACA_EndDIFS_Event(CSMACA_Event): pass
class CSMACA_SendStartEvent(CSMACA_Event): pass
class CSMACA_SendCompleteEvent(CSMACA_Event): pass
class CSMACA_ReceiveCompleteEvent(CSMACA_Event): pass


class CSMACA_State(enum.Enum):
    Idle = enum.auto()
    WaitBackoff = enum.auto()
    WaitDIFS = enum.auto()
    WaitSIFS = enum.auto()
    Receiving = enum.auto()
    Sending = enum.auto()
    Busy = enum.auto()






class CSMACA_DeviceController(DeviceController):
    def __init__(self):
        super().__init__()

        self._state : CSMACA_State = CSMACA_State.Idle
        self._rate : TransRate = TransRate.r6Mbps
        self._sentData : typing.List[TransData] = []
        self._receivedData : typing.List[TransData] = []

    _log = []

    @property
    def version(self) -> IEEE802dot11Version:
        return Simulator.Instance.GetProperty('version',IEEE802dot11Version.a)

    @property
    def rate(self) -> TransRate:
        return self._rate

    @rate.setter
    def rate(self,value):
        self._rate = value


    @property
    def sentData(self) -> typing.List[TransData]:
        return self._sentData

    @property
    def receivedData(self) -> typing.List[TransData]:
        return self._receivedData

    @property
    def state(self) -> CSMACA_State:
        return self._state

    @state.setter
    @DeviceController.simPropertySetter
    def state(self,value:CSMACA_State):
        if (self._state == value):
            return
        #print(self.name,value)
        self._log.append((self.Sim.time,self.name,value.name))
        self._state = value


    def Reset(self):
        super().Reset()
        self._sentData = []
        self._receivedData = []
        self._log = []




class CSMACA_STA_Controller(CSMACA_DeviceController):
    def __init__(self):
        super().__init__()
        self._slot : int = 0
        self._resend : int = 0
        self._target : 'CSMACA_AP_Controller' = None

        self._holdData : IEEE802dot11TransData = TransData.Null
        self._receivingData : IEEE802dot11TransData = TransData.Null


    @property
    def slot(self) -> int:
        return self._slot

    @property
    def resend(self) -> int:
        return self._resend


    def generateSlot(self):
        self._slot = self.Sim.Rand.randint(0,int(math.pow(2,self.resend)))

    def ResetResendCount(self):
        self._resend = self.version.cwMin

    def addResendCount(self):
        self._resend = min(self.version.cwMax,max(self.version.cwMin,self._resend+1))

    def Event(self, event:SimEvent, obj:DeviceController):
        super().Event(event,obj)

        if (obj.name == self.name):
            if (type(event) is CSMACA_SlotEvent):
                if (event.slot > 0):
                    #
                    self._slot = event.slot
                    self.nextEvent = CSMACA_SlotEvent(self.Sim.time+self.version.slotTime,self,event.slot-1)
                else:
                    #
                    self.addResendCount()
                    self.generateSlot()

                    self.SendStart()
                    pass
            elif (type(event) is CSMACA_EndDIFS_Event):
                self.EndDIFS()
            elif (type(event) is CSMACA_SendStartEvent):
                self.SendStart()
            elif (type(event) is CSMACA_SendCompleteEvent):
                self.SendComplete()
            elif (type(event) is CSMACA_ReceiveCompleteEvent):
                self.RecieveComplete()

    def EndDIFS(self):
        self.state = CSMACA_State.WaitBackoff
        self.nextEvent = CSMACA_SlotEvent(self.Sim.time+self.version.slotTime,self,self._slot-1)


    def SendStart(self):
        #print(self.Sim.time,self.name,'sending')
        t = 16+(1+math.floor(12310/self._rate.OFDMsymbol))*4
        self.transData = IEEE802dot11TransData(
            self,
            self._target,
            self.Sim.time,
            self.Sim.time+t,
            100,
            self._rate,
            IEEE802dot11FrameType.Data,
            {'IP':1500*8,'UDP':1472*8}
        )
        self.nextEvent = CSMACA_SendCompleteEvent(self.Sim.time+t,self)
        self.state = CSMACA_State.Sending

        #self.BookEvent(PhysicalEvent)
        pass

    def RecieveComplete(self):
        #print('aaa')
        self.receivedData.append(self._receivingData)
        self.sentData.append(self._holdData)

        target : CSMACA_DeviceController = self._receivingData.author

        target.receivedData.append(self._holdData)
        target.sentData.append(self._receivingData)
        self.Sim.SetProperty('trans_count',self.Sim.GetProperty('trans_count',0)+1)


        self._holdData = TransData.Null
        self._receivingData = TransData.Null
        self.state = CSMACA_State.WaitDIFS
        self.nextEvent = SimEvent.Null

        self.ResetResendCount()
        self.generateSlot()


    def SendComplete(self):
        self._holdData = self.transData
        self.state = CSMACA_State.WaitDIFS
        self.nextEvent = CSMACA_EndDIFS_Event(self.Sim.time+self.version.DIFS,self)
        self.transData = TransData.Null
        #self.BookEvent(PhysicalEvent)


    def Reset(self):
        super().Reset()
        self.state = CSMACA_State.WaitBackoff
        self.ResetResendCount()
        self.generateSlot()
        self.nextEvent = CSMACA_SlotEvent(self.Sim.time+self.version.slotTime,self,self._slot-1)



    def Physical(self):
        super().Physical()

        if (self.state in [CSMACA_State.WaitBackoff,CSMACA_State.WaitDIFS,CSMACA_State.Receiving,CSMACA_State.Busy]):
            trans = self.Phy.Sense(self)

            if (self.state in [CSMACA_State.WaitBackoff,CSMACA_State.WaitDIFS]):
                if (trans.power > 0):
                    if (type(trans) is IEEE802dot11TransData and trans.target.name == self.name):
                        self._receivingData = trans
                        self.state = CSMACA_State.Receiving
                        self.nextEvent = CSMACA_ReceiveCompleteEvent(trans.endTime,self)
                    else:
                        self.state = CSMACA_State.Busy
                        self.nextEvent = SimEvent.Null

            elif (self.state is CSMACA_State.Receiving):
                if (self.nextEvent.time <= self.Sim.time):
                    self.RecieveComplete()
                else:
                    if (trans.power<=0):
                        self.state = CSMACA_State.WaitDIFS
                        self.nextEvent = CSMACA_EndDIFS_Event(self.Sim.time+self.version.DIFS,self)
                    elif (trans.transID != self._receivingData.transID):
                        self.state = CSMACA_State.Busy
                        self.nextEvent = SimEvent.Null

            elif (self.state is CSMACA_State.Busy):
                if (trans.power <= 0):
                    self.state = CSMACA_State.WaitDIFS
                    self.nextEvent = CSMACA_EndDIFS_Event(self.Sim.time+self.version.DIFS,self)







class CSMACA_AP_Controller(CSMACA_DeviceController):

    def __init__(self):
        super().__init__()
        self._target : CSMACA_STA_Controller = None

        self._receivingData : IEEE802dot11TransData = TransData.Null


    def Event(self, event:SimEvent, obj:DeviceController):
        super().Event(event,obj)

        if (obj.name == self.name):
            if   (type(event) is CSMACA_SendStartEvent):
                self.SendStart()
            elif (type(event) is CSMACA_SendCompleteEvent):
                self.SendComplete()
            elif (type(event) is CSMACA_ReceiveCompleteEvent):
                self.RecieveComplete()


    def SendStart(self):
        t = 16+(1+math.floor(134/self._rate.OFDMsymbol))*4

        self.transData = IEEE802dot11TransData(
            self,
            self._target,
            self.Sim.time,
            self.Sim.time+t,
            100,
            self._rate,
            IEEE802dot11FrameType.Ack,
            {'IP':0,'UDP':0}
        )

        self.nextEvent = CSMACA_SendCompleteEvent(self.Sim.time+t,self)
        self.state = CSMACA_State.Sending

        #self.BookEvent(PhysicalEvent)

    def SendComplete(self):
        self.nextEvent = SimEvent.Null
        self.state = CSMACA_State.Idle
        self.transData = TransData.Null
        self._target = DeviceController.Null
        #self.BookEvent(PhysicalEvent)


    def RecieveComplete(self):
        self.nextEvent = CSMACA_SendStartEvent(self.Sim.time+self.version.SIFS,self)
        self.state = CSMACA_State.WaitSIFS
        self._target = self._receivingData.author
        self._receivingData = TransData.Null

        #self.BookEvent(PhysicalEvent)


    def Physical(self):
        super().Physical()

        if (self.state in [CSMACA_State.Idle , CSMACA_State.Receiving, CSMACA_State.Busy]):
            trans = self.Phy.Sense(self)

            if (trans.power > 0):
                if (self.state is CSMACA_State.Idle):
                    if (trans.target.name == self.name and trans.stratTime == self.Sim.time):
                        self.state = CSMACA_State.Receiving
                        self._receivingData = trans
                        self.nextEvent = CSMACA_ReceiveCompleteEvent(trans.endTime,self)
                        pass
                elif (self.state is CSMACA_State.Receiving):
                    if (self.transData is not None and trans.transID != self._receivingData.transID):
                        self.state = CSMACA_State.Busy
                        self._receivingData = TransData.Null
                        self.nextEvent = SimEvent.Null
                        pass
                elif (self.state is CSMACA_State.Busy):
                    if (trans.stratTime == self.Sim.time):
                        self.state = CSMACA_State.Receiving
                        self._receivingData = trans
                        self.nextEvent = CSMACA_ReceiveCompleteEvent(trans.endTime,self)
                        pass
            else:
                if (self.state is CSMACA_State.Receiving and self._receivingData.endTime <= self.Sim.time):
                    self.state = CSMACA_State.Idle
                    self._receivingData = TransData.Null
                    self.nextEvent = SimEvent.Null

    def Update(self):
        super().Update()
        #print('\033[1;31m',self.state,self.nextEvent,'\033[0m')


    def Reset(self):
        super().Reset()
        self.state = CSMACA_State.Idle
        self._target = DeviceController.Null
        self._receivingData = TransData.Null



class Timer_Event(SimEvent):
    def __init__(self, time:int, obj:DeviceController):
        super().__init__(time,obj)
        self.target = EventTarget.Author


class Timer_Device(DeviceController):
    step = 10000

    success = 0
    latest  = 0

    def __init__(self):
        super().__init__()
    

    def Event(self, event, obj):
        if (obj.name == self.name):
            if (type(event) is Timer_Event):
                self.nextEvent = Timer_Event(self.Sim.time+self.step, self)
                self.timer_event()
        return super().Event(event, obj)
    
    def timer_event(self):
        success = 0
        for dev in self.Sim.devices:
            if (isinstance(dev,CSMACA_STA_Controller)):
                success += len(dev.sentData)
        

        print(f'--------------------')
        print(f'Sim-Time   : {self.Sim.time}')
        print(f'RealTime   : {time.time() - self.latest}')
        print(f'Success    : {success - self.success}/{success}')
        print(f'Throughput : {(8*1500*(success - self.success)) / self.step}Mbps')

        self.latest = time.time()
        self.success = success
        pass
    

    def Update(self):
        super().Update()


    def Reset(self):
        super().Reset()
        self.nextEvent = Timer_Event(0,self)
        self.latest = time.time()
        self.success = 0







if __name__ == '__main__':
    import os,json,datetime,time

    Simulator.Instance.SetRandomSeed(0)
    Simulator.Instance.SetProperty('version',IEEE802dot11Version.a)

    Simulator.Instance.devices.append(Timer_Device())

    # 基地局の作成
    ap = CSMACA_AP_Controller()
    ap._rate = TransRate.r24Mbps
    ap._name = 'AP'
    Simulator.Instance.devices.append(ap) # シミュレーターに追加

    # 端末の作成
    duration = 1000000 # シミュレーション時間(us)
    count = 1 # 試行回数
    num = 70
    s = 10

    for i in range(num):
        sta = CSMACA_STA_Controller()
        sta._target = ap # ターゲットをAPに
        sta._rate = TransRate.r24Mbps
        sta._name = f'STA{i}'
        Simulator.Instance.devices.append(sta)

    L = []
    L0 = 0
    all_result = {}

    for rate in [
            # TransRate.r6Mbps,
            # TransRate.r9Mbps,
            # TransRate.r12Mbps,
            # TransRate.r18Mbps,
            TransRate.r24Mbps,
            # TransRate.r36Mbps,
            # TransRate.r48Mbps,
            # TransRate.r54Mbps
            ]: # すべてのレートで試行

        for dev in Simulator.Instance.devices:
            if (isinstance(dev,CSMACA_DeviceController)):
                dev._rate = rate

        L = []
        IP = []
        UDP = []
        Success = []
        Lap = []
        Step = {}
        for n in range(count):
            Simulator.Instance.SetRandomSeed(s)
            #s+=1
            start = time.time()
            Simulator.Instance.Simulate(duration)
            lap = time.time() - start
            success = 0
            ip = 0
            udp = 0
            log = {}
            for dev in Simulator.Instance.devices:
                if (isinstance(dev,CSMACA_DeviceController)):
                    ip  += sum([data.data.get('IP',0) for data in dev.sentData])
                    udp += sum([data.data.get('UDP',0) for data in dev.sentData])
                    success += len(dev.sentData)
                    log[dev.name] = dev._log
                    if (isinstance(dev,CSMACA_STA_Controller)):
                        for data in dev.sentData:
                            Step.setdefault(str(max(1,data.stratTime)//10000),0)
                            Step[str(max(1,data.stratTime)//10000)] += 1
            Lap.append(lap)
            IP.append(ip)
            UDP.append(udp)
            Success.append(success//2)

            path = os.path.join(os.path.dirname(__file__),'result',f'log_{n}_{rate}_{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}.json')
            with open(path,'w',encoding='utf-8') as f:
                json.dump(log,f,indent=4,ensure_ascii=False)


        all_result[rate] = {
            'lap_time' : sum(Lap)/count,
            'IP' : (sum(IP)/count)/duration,
            'UDP': (sum(UDP)/count)/duration,
            'success':sum(Success)/count
        }
    print(all_result)

    d = {
        'version': str(Simulator.Instance.GetProperty('version')),
        'duration' : duration,
        'device' : num,
        'count' : count,
        'result' : all_result
    }

    path = os.path.join(os.path.dirname(__file__),'result',f'test{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}.json')
    with open(path,'w',encoding='utf-8') as f:
        json.dump(d,f,indent=4,ensure_ascii=False)

    path = os.path.join(os.path.dirname(__file__),'result',f'step{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}.json')
    with open(path,'w',encoding='utf-8') as f:
        json.dump({k:Step[k] for k in sorted(Step.keys(), key=lambda x: int(x))},f,indent=4,ensure_ascii=False)


