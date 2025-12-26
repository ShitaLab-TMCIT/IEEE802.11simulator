import random
import typing
import enum
import math
import copy
import time
import numpy

class IEEE_Standard(enum.Enum) :
    """
    IEEE 802.11の規格を表す列挙型
    """
    a = enum.auto(),
    b = enum.auto(),
    g = enum.auto()

__IEEE_ParamType = typing.TypedDict('IEEE_Param', {"SLOT_TIME": int, "SIFS": int, "DIFS": int})

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





    """
    各ユーザーの送信状態を管理するクラス
    """
    cw_max : int = 1023
    cw_list : typing.List[int]

    id : int
    """ ユーザーのID """

    num_re_trans : int
    """ 再送回数 """

    slots : int
    """ スロット生成 """

    num_transmitted : int
    """ 何回送信したか """

    data_transmitted : int
    """ 送信したデータ量 """


    def __init__(self, id : int, n : int = 0, seed = None):
        """
        Userクラスのコンストラクタ
        Args:
            id (int): ユーザーのID
            n (int): 再送回数。デフォルトは0。
            seed: 乱数生成のためのシード値（未使用）
        """

        self.cw_list = []
        i = 0
        while 2**(4+i)-1 <= self.cw_max:
            self.cw_list.append(2**(4+i)-1)
            i+=1

        # ID
        self.id = id
        # 再送回数
        self.num_re_trans : int = n
        # スロット生成
        self.slots : int = 0
        # 何回送信したか
        self.num_transmitted : int = 0
        # 送信したデータ量
        self.data_transmitted : int = 0

    # スロット生成
    def calc_slots(self) -> int :
        return random.randint(0,self.cw_list[self.num_re_trans])

    # 再送処理
    def re_transmit(self):
        self.num_re_trans = min(self.num_re_trans+1, 6)
        self.slots = random.randint(0,self.cw_list[self.num_re_trans])

    # スロットリセット
    def reset_slots(self):
        self.num_re_trans = 0
        self.slots = random.randint(0,self.cw_list[self.num_re_trans])



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



    def __init__(self, mode : IEEE_Standard):
        """
        シミュレーターのコンストラクタ
        Args:
            mode (IEEE_Standard): IEEE 802.11の規格
        """
        self.mode = mode

    def calc_cw_time(self, slots : int) -> float:
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


    def Simulate(self, users : typing.List[User], duration: int, seed = None) -> typing.Dict[int, User]:
        """
        シミュレーションを実行する
        Args:
            users (typing.List[User]): ユーザーのリスト
            seed: 乱数生成のためのシード値（未使用）
        Returns:
            typing.Dict[int, User]: ユーザーのIDをキーとするユーザーの状態を格納した辞書
        """
        success = 0

        duration *= 10**6  # マイクロ秒単位に変換

        total_data_transmitted = 0
        current_time = 0

        while current_time < duration:
            #print(f"Current Time: {current_time} microseconds")
            users.sort(key=lambda x: x.slots)  # スロットの小さい順にソート
            min_slots = users[0].slots

            cw_time = self.calc_cw_time(min_slots)

            if users[1].slots == min_slots:
                # 衝突が発生した場合
                current_time += self.__Total_Frame_length + self.__Backoff_count*cw_time
                if (current_time < duration):
                    min_slots = min_slots
                    for user in users:
                        if user.slots == min_slots:
                            user.re_transmit()
                        else:
                            user.slots -= min_slots
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
                    user.slots -= min_slots

                users[0].reset_slots()

        print('success:',success)
        return float(total_data_transmitted / duration)

if __name__ == "__main__":
    # python main.pyで実行すると以下が実行される
    n = 10

    # Userのリスト(users)を作成シミュレータに渡す
    users = [User(i) for i in range(n)]

    simulator = Simulator(IEEE_Standard.a)
    simulator.SetConfig(IEEE_Standard.a, TrafficLevel.IP, 24)
    results = []
    start_time = time.time()
    for i in range(10):
        results.append(simulator.Simulate(users, 1, seed=42))
    end_time = time.time()
    print(f"Simulation took {end_time - start_time:.2f} seconds\nresult : {sum(results) / len(results)} Mbps")
