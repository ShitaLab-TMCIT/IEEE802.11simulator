import typing,dataclasses,json,os,random,time

from .SimEvent import EventTarget,SimEvent,InitEvent,UpdateEvent,PhysicalEvent
from .DeviceController import DeviceController


class SimulationError(Exception):
    pass

class SimulateUnfinishedError(SimulationError):
    pass

class SimulateStackError(SimulationError):
    pass


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

    _isPhysicFlag : bool = False

    _simProperties : dict[str,typing.Any] = {}


    def __init__(self):
        self.SimDev = DeviceController('Simulator')
        self.SimDev._simulator = self

        self.Rand = random.Random()
        self._time = 0
        self._devices  = []
        self._simProperties = {}

    @property
    def time(self) -> int:
        """
        シミュレーション時間(us)

        :return:
        :rtype: int
        """
        return self._time

    @property
    def devices(self) -> list['DeviceController']:
        """
        シミュレーション対象のデバイス配列

        :return:
        :rtype: List[DeviceController]
        """
        return self._devices

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

        self._TriggerEvent(InitEvent  (self.time,self.SimDev))
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
            device.EventHandler(event)


    def _SimulateOne (self,stack_count:int) -> None:
        t = self.time

        nextEvent = (
            sorted(
                [dev.nextEvent for dev in self._devices if dev.nextEvent.time > 0],
                key = lambda e: e.time
            ) + [UpdateEvent(self.time,self.SimDev)]
        )
        self._time = max(nextEvent[0].time,self.time)

        update = UpdateEvent(self.time,self.SimDev)
        update.target = EventTarget.Custom
        for i in nextEvent[:-1]:
            if (self._time >= i.time):
                self._TriggerEvent(i)
                update.targets.append(i.author)
            else:
                break
        self._TriggerEvent(update)

        count = 0
        while (self._isPhysicFlag):
            self._isPhysicFlag = False
            self._TriggerEvent(PhysicalEvent(self.time,self.SimDev))
            self._TriggerEvent(UpdateEvent(self.time,self.SimDev))
            count += 1
            if (count > stack_count): raise SimulateStackError()


        if (t == self.time): raise SimulateUnfinishedError()


