import typing


if typing.TYPE_CHECKING:
    from .DeviceController import DeviceController



class TransData:
    Null : 'TransData' = None
    __transID : int = 0

    @property
    def transID(self) -> int:
        return self._transID


    @property
    def author(self) -> 'DeviceController':
        return self._author

    @property
    def target(self) -> 'DeviceController':
        return self._target


    @property
    def stratTime(self) -> int:
        return self._startTime

    @property
    def endTime(self) -> int:
        return self._endTime


    @property
    def power(self) -> float:
        return self._power


    @property
    def data(self) -> typing.Dict[str,typing.Any]:
        return self._data

    @data.setter
    def data(self,value:typing.Dict[str,typing.Any]) -> None:
        self._data = value


    @typing.overload
    def __init__(
            self,
            author:'DeviceController',
            target:'DeviceController',
            startTime:int,
            endTime:int,
            power:float,
            data:typing.Dict[str,typing.Any] = {}
            ):...

    def __init__(self,
            author:'DeviceController' = None,
            target:'DeviceController' = None,
            startTime:int = 0,
            endTime:int = 0,
            power:float = 0,
            data:typing.Dict[str,typing.Any] = {}
            ):
        self._transID   : int = TransData.__transID
        self._author    : DeviceController = author
        self._target    : DeviceController = target
        self._startTime : int = startTime
        self._endTime   : int = endTime
        self._power     : float = power
        self._data      : typing.Dict[str,typing.Any] = data
        TransData.__transID += 1


    def ToSendData(self) -> typing.Dict[str,typing.Any]:
        return {
            'device' : self._target.ID,
            'length' : self._data.get('length',0),
            'IP' : self._data.get('IP',0),
            'TCP' : self._data.get('TCP',0),
            'UDP' : self._data.get('UDP',0)
        }

    def ToReceiveData(self) -> typing.Dict[str,typing.Any]:
        return {
            'device' : self._author.ID,
            'length' : self._data.get('length',0),
            'IP' : self._data.get('IP',0),
            'TCP' : self._data.get('TCP',0),
            'UDP' : self._data.get('UDP',0)
        }

    def copy(self) -> 'TransData':
        return TransData(
            self._author,
            self._target,
            self._startTime,
            self._endTime,
            self._power,
            self._data
        )

