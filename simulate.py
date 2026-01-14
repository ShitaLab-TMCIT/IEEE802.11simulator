import random
import typing
import enum
import math
import time



class IEEE_Standard(enum.Enum) :
    """
    IEEE 802.11の規格を表す列挙型
    """

    a = enum.auto(),
    b = enum.auto(),
    g = enum.auto()


__IEEE_ParamType = typing.TypedDict(
    'IEEE_Param',
    {
        "SLOT_TIME": int,
        "SIFS": int,
        "DIFS": int
    }
)

TRANS_MODE_DATA : typing.Dict[IEEE_Standard,__IEEE_ParamType] = {
    IEEE_Standard.a: {
        "SLOT_TIME": 9,
        "SIFS": 16,
        "DIFS": 34,
        "T": 1500
    },

    IEEE_Standard.b: {
        "SLOT_TIME": 20,
        "SIFS": 10,
        "DIFS": 50,
        "T": 1472
    },

    IEEE_Standard.g: {
        "SLOT_TIME": 20,
        "SIFS": 10,
        "DIFS": 56,
        "T": 2920
    }
}


class TrafficLevel(enum.Enum):
    """
    トラフィックレベルを表す列挙型
    """

    IP = enum.auto(),
    UDP = enum.auto(),
    TCP = enum.auto(),


class User:
    '''
    各ユーザーの送信状態を管理するクラス
    '''

    _Rand : random.Random = None
    ''' 乱数生成器 '''


    id : int = 0
    ''' ユーザーのID '''


    cw_max   : int = 1023
    '''CWの最大値'''

    cw_list  : list[int] = []
    '''cw_maxのリスト'''


    re_trans : int = 0
    ''' 再送回数 '''

    slot     : int = 0
    ''' スロット生成 '''


    num_transmitted  : int = 0
    ''' 送信した回数 '''

    data_transmitted : int = 0
    ''' 送信したデータ量 '''



    def __init__(self, id : int):
        '''
        Userクラスのコンストラクタ
        Args:
            id (int): ユーザーのID
        '''

        self.cw_list = []
        i = 0
        while 2**(4+i)-1 <= self.cw_max:
            self.cw_list.append(2**(4+i)-1)
            i+=1

        self.id = id
        self.re_trans : int = 0
        self.slot : int = 0
        self.num_transmitted : int = 0
        self.data_transmitted : int = 0

    def reset(self):
        self.re_trans = 0
        self.slot = 0
        self.num_transmitted = 0
        self.data_transmitted = 0

    # スロット生成
    def calc_slots(self) -> int :
        return self._Rand.randint(0,self.cw_list[self.re_trans])

    # 再送処理
    def re_transmit(self):
        self.re_trans = min(self.re_trans+1, 6)
        self.slot = self.calc_slots()

    # スロットリセット
    def reset_slots(self):
        self.re_trans = 0
        self.slot = self.calc_slots()


    def set_rand(self,rand:random.Random):
        self._Rand = rand


class Simulator :
    """
    シミュレーターの基本クラス
    """

    __Symbol_bit : int = 8
    """ シンボルのビット数 """

    __PLCP_preamble : float = 16
    """ PLCPプリアンブルの長さ（マイクロ秒） """
    __PLCP_header : float = 4
    """ PLCPヘッダーの長さ（マイクロ秒） """
    __Packet_length : float = 1500 * 8
    """ パケットの長さ（ビット） """

    __SIFS_time : int
    __DIFS_time : int


    __Ack_Frame_length : int = 28 * 8
    """ ACKフレームの長さ（ビット） """

    __Ack_Tcp_length : int = 2 * 1460 * 8
    """ ACK TCPフレームの長さ（ビット） """

    __Data_Frame_length : int = 1472 * 8
    """ データフレームの長さ（ビット） """

    __Total_Frame_length : float = 0


    __Backoff_count : int = 1

    __Packet_thorough : int = 0

    __SlotTime : float = 0

    _Rand : random.Random



    def __init__(self):
        """
        シミュレーターのコンストラクタ
        Args:
            mode (IEEE_Standard): IEEE 802.11の規格
        """
        self._Rand = random.Random()

    def _calc_cw_time(self, slots : int) -> float:
        return slots * self.__SlotTime


    def SetConfig(self, mode : IEEE_Standard, level : TrafficLevel, rate : int):
        """
        シミュレーターのモードを設定する
        Args:
            mode (IEEE_Standard): IEEE 802.11の規格
            level (TrafficLevel): トラフィックレベル
        """

        self.mode = mode
        self.level = level
        self.rate = rate

        self.__Symbol_bit = rate * 4
        self.__SlotTime = TRANS_MODE_DATA[mode]["SLOT_TIME"]
        self.__Packet_thorough = TRANS_MODE_DATA[mode]["T"] * 8

        Symbol_bit : float = rate * 4

        PLCP_preamble : float
        PLCP_header : float

        Ack_Frame_length : float
        Ack_Tcp_Frame_length : float
        Data_Frame_length : float

        if (mode == IEEE_Standard.a or mode == IEEE_Standard.g):
            PLCP_preamble = 16
            PLCP_header = 4
            Ack_Frame_length = math.ceil(134/Symbol_bit) * 4
            Ack_Tcp_Frame_length = math.ceil(630/Symbol_bit) * 4
            Data_Frame_length = math.ceil(12310/Symbol_bit) * 4
        elif (mode == IEEE_Standard.b):
            PLCP_preamble = 144/100000
            PLCP_header = 48/100000
            Ack_Frame_length = 112/rate
            Ack_Tcp_Frame_length = 608/rate
            Data_Frame_length = 12288/rate

        self.__PLCP_frame_length = PLCP_preamble + PLCP_header

        if (level == TrafficLevel.IP):
            self.__Total_Frame_length = PLCP_preamble*2 + PLCP_header*2 + Data_Frame_length + Ack_Frame_length + TRANS_MODE_DATA[mode]["SIFS"] + TRANS_MODE_DATA[mode]["DIFS"]
            self.__Backoff_count = 1
        elif (level == TrafficLevel.UDP):
            self.__Total_Frame_length = PLCP_preamble*2 + PLCP_header*2 + Data_Frame_length + Ack_Frame_length + TRANS_MODE_DATA[mode]["SIFS"] + TRANS_MODE_DATA[mode]["DIFS"]
            self.__Backoff_count = 1
        elif (level == TrafficLevel.TCP):
            self.__Total_Frame_length = PLCP_preamble*6 + PLCP_header*6 + Data_Frame_length*2 + Ack_Tcp_Frame_length + Ack_Frame_length*3 + TRANS_MODE_DATA[mode]["SIFS"]*3 + TRANS_MODE_DATA[mode]["DIFS"]*3
            self.__Backoff_count = 3

        print(f"""
Simulator Config
-Mode                 : {mode.name}
-Traffic Level        : {level.name}
-Rate                 : {rate} Mbps
-PLCP Preamble        : {PLCP_preamble} microseconds
-PLCP Header          : {PLCP_header} microseconds
-ACK Frame Length     : {Ack_Frame_length} microseconds
-ACK TCP Frame Length : {Ack_Tcp_Frame_length} microseconds
-Data Frame Length    : {Data_Frame_length} microseconds
-Total Frame Length   : {self.__Total_Frame_length} microseconds
""")

    def Simulate(self, users : list[User], duration: int, seed = None) -> float:
        """
        シミュレーションを実行する
        Args:
            users (list[User]): ユーザーのリスト
            duration (int): シミュレーション時間（秒）
            seed: 乱数生成のためのシード値
        Returns:
            dict[int, User]: ユーザーのIDをキーとするユーザーの状態を格納した辞書
        """
        if seed is not None:
            self._Rand.seed(seed)

        for user in users:
            user.reset()
            user.set_rand(self._Rand)


        success = 0

        duration *= 10**6  # マイクロ秒単位に変換

        total_data_transmitted = 0
        current_time = 0

        while current_time < duration:
            #print(f"Current Time: {current_time} microseconds")
            users.sort(key=lambda x: x.slot)  # スロットの小さい順にソート
            min_slots = users[0].slot

            cw_time = self._calc_cw_time(min_slots)

            if users[1].slot == min_slots:
                # 衝突が発生した場合
                current_time += self.__Total_Frame_length + self.__Backoff_count*cw_time
                if (current_time < duration):
                    min_slots = min_slots
                    for user in users:
                        if user.slot == min_slots:
                            user.re_transmit()
                        else:
                            user.slot -= min_slots
                else:
                    break
            else:
                users[0].num_transmitted += 1

                current_time += self.__Total_Frame_length + self.__Backoff_count*cw_time
                if (current_time < duration):
                    users[0].data_transmitted += self.__Packet_thorough
                    total_data_transmitted += self.__Packet_thorough
                    success += 1
                else:
                    break

                for user in users:
                    user.slot -= min_slots

                users[0].reset_slots()

        #print('success:',success)
        return float(total_data_transmitted / duration)


if __name__ == "__main__":
    # サンプルコード

    # シミュレーション条件
    # *デバイス数             : 70台
    # *シミュレーション時間    : 1秒(1000000us)
    # *伝送レート             : 24Mbps
    # *IEEE802.11バージョン   : IEEE802.11a
    # *パケット               : IPレベル


    sim = Simulator() # シミュレーターのインスタンスを作成
    sim.SetConfig(  # シミュレーション条件を設定
        IEEE_Standard.a, # IEEE802.11バージョン
        TrafficLevel.IP, # パケット
        24               # 伝送レート
    )

    # デバイス設定
    users = []
    for i in range(70):
        users.append(User(i)) # ユーザーをリストにする

    result = sim.Simulate(users, 1) # シミュレーションを実行

    print(f'Throughput : {result}Mbps')








