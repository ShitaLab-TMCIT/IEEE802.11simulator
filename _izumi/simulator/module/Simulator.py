import typing,dataclasses,json,os,random,time

from .SimEvent import SimEvent,InitEvent,UpdateEvent,PhysicalEvent
from .DeviceController import DeviceController


class Simulator:
    """
    シミュレーションを管理するクラス
    """

    Instance : 'Simulator' = None
    """
    インスタンス.
    代入,変更禁止
    """

    SimDev   : 'DeviceController' = None
    """
    イベントの親がシミュレーターであることを明示するデバイス型.
    代入,変更禁止
    """

    Rand : random.Random = None

    _time : int = 0
    _devices : list['DeviceController'] = []
    _eventQueue : list['SimEvent'] = []
    _isPhysicFlag : bool = False
    _simProperties : dict[str,typing.Any] = {}


    def __init__(self):
        Simulator.Instance = self
        Simulator.SimDev = DeviceController()
        Simulator.Rand = random.Random()

        self._time = 0
        self._devices  = []
        self._eventQueue = []
        self._simProperties = {}


    @property
    def devices(self) -> list['DeviceController']:
        """
        シミュレーション対象のデバイス配列

        :return:
        :rtype: List[DeviceController]
        """
        return self._devices

    @property
    def eventQueue(self) -> list['SimEvent']:
        """
        即時発火させるイベントのキュー

        :return:
        :rtype: List[SimEvent]
        """
        return self._eventQueue

    @property
    def time(self) -> int:
        """
        シミュレーション時間(us)

        :return:
        :rtype: int
        """
        return self._time

    @property
    def simProperties(self) -> dict[str,typing.Any]:
        """
        シミュレーション共通のパラメーターを格納する辞書

        :return:
        :rtype: Dict[str, Any]
        """
        return self._simProperties


    def Simulate(self,duration:int,stack_count:int=100) -> bool:
        """
        シミュレーションを実行する関数

        :param duration: シミュレーション時間(us)
        :type duration: int
        """

        self._time = 0
        self._isPhysicFlag = False

        self._TriggerEvent(InitEvent(self.time,self.SimDev))
        self._TriggerEvent(UpdateEvent(self.time,self.SimDev))

        try:
            while (self._time < duration):
                self._SimulateOne(stack_count)
        except Exception as e:
            return e
        else:
            return True

    def TriggerPhysic(self) -> None:
        self._isPhysicFlag = True


    def SetRandomSeed(self,seed:int) -> None:
        """
        シード値を設定する関数

        :param seed: シード値
        :type seed: int
        """

        self.Rand.seed(seed)


    def SetProperty(self,key:str,value:typing.Any) -> None:
        """
        simPropertiesに値を設定する関数

        :param key: 辞書のキー
        :type key: str
        :param value: 格納する値
        :type value: typing.Any
        """

        self._simProperties[key] = value

    def GetProperty(self,key:str,default:typing.Any=None) -> typing.Any:
        """
        simPropertiesから値を取得する関数

        :param key: 辞書のキー
        :type key: str
        :param default: デフォルト値
        :type default: typing.Any
        :return: 格納された値
        :rtype: Any
        """

        return self._simProperties.get(key,default)


    def _TriggerEvent (self,event:'SimEvent') -> None:
        for device in event.get_target():
            device.Event(event,device)


    def _SimulateOne (self,stack_count:int) -> None:
        t = self.time

        nextEvent = (sorted(
            [dev.nextEvent for dev in self._devices if dev.nextEvent.time > 0],
            key = lambda e: e.time
            )+[UpdateEvent(self.time,self.SimDev)])
        self._time = max(nextEvent[0].time,self.time)

        for i in nextEvent[:-1]:
            if (self._time >= i.time):
                self._TriggerEvent(i)
            else:
                break
        self._TriggerEvent(UpdateEvent(self.time,self.SimDev))

        count = 0
        while (self._isPhysicFlag):
            self._isPhysicFlag = False

            event = PhysicalEvent(self.time,self.SimDev)

            self._TriggerEvent(event)
            self._TriggerEvent(UpdateEvent(self.time,self.SimDev))

            count += 1
            if (count > stack_count):
                raise Exception('カウント超過')


        if (t == self.time):
            raise Exception('時間停止')


# if __name__ == '__main__':
#     import CSMACA_DeviceController
#     Simulator()
#     simc.IEEE802dot11Property()

#     Simulator.instance = Simulator()
#     phy = phym.PhysicalManager(Simulator.instance)

#     ap = CSMACA_DeviceController.CSMACA_AP_Controller()
#     ap._rate = simc.TransRate.r24Mbps
#     ap._name = 'AP'
#     ap._simInstance = Simulator.instance
#     ap._phyInstance = phy
#     Simulator.instance.devices.append(ap)

#     for i in range(10):
#         sta = CSMACA_DeviceController.CSMACA_STA_Controller()
#         sta._target = ap
#         sta._rate = simc.TransRate.r24Mbps
#         sta._name = f'STA{i}'
#         sta._simInstance = Simulator.instance
#         sta._phyInstance = phy
#         Simulator.instance.devices.append(sta)

#     L = []
#     L0 = 0
#     for n in range(10):
#         Simulator.instance.Simulate(1000000)
#         l = [sum([j.get('IP',0) for j in i.sentData if (j.get('IP',0)>0)]) for i in Simulator.instance.devices]
#         l0= [len([j.get('IP',0) for j in i.sentData if (j.get('IP',0)>0)]) for i in Simulator.instance.devices]
#         L.append(sum(l)/1000000)
#         print(n,sum(l)/1000000)
#         print(sum(l0))
#     print(sum(L)/len(L))
#     # d = {i.name : i.sentData for i in  Simulator.instance.devices}
#     # l = [sum([j.get('IP',0) for j in i.sentData]) for i in Simulator.instance.devices]
#     # path = os.path.join(os.path.dirname(__file__),'test.json')
#     # with open(path,'w',encoding='utf-8') as f:
#     #     json.dump(d,f,indent=4,ensure_ascii=False)


