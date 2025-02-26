import random

# 出力形式あんま使ってない
PRINT_MODE = {
    0: "Only Collision",
    1: "ALL",
    2: "Only Results",
    3: "No Output"
}

# モードによって辞書型で管理してる
TRANS_MODE = {
    "a": {
        "SLOT_TIME": 9,
        "SIFS": 16,
        "DIFS": 34
    },

    "b": {
        "SLOT_TIME": 20,
        "SIFS": 10,
        "DIFS": 50
    },

    "g": {
        "SLOT_TIME": 9,
        "SIFS": 10,
        "DIFS": 28
    }
}


# パケット作るときに使おうと思ったけど使ってない
OFDM_DATA_BIT = {
    6: 24,
    9: 35,
    12: 48,
    18: 72,
    24: 96,
    36: 144,
    48: 192,
    54: 216
}

# ACKを送るのにかかる時間`./data/20100211_11a-mac-frame.pdf`にある資料から抜粋
ACK_TIME = {
    6: 52,
    9: 44,
    12: 36,
    18: 32,
    24: 28,
    36: 28,
    48: 24,
    54: 24
}

# Userクラス
class User:
    def __init__(self, id, n=0, seed=None):
        # ID
        self.id = id
        # 再送回数
        self.num_re_trans = n
        # スロット生成
        self.slots = self.calc_slots()
        # 何回送信したか
        self.num_transmitted = 0
        # 送信したデータ量
        self.data_transmitted = 0

    def calc_slots(self):
        cw_max = 2 ** (4 + self.num_re_trans) - 1
        self.slots = random.randint(0, min(cw_max, 1023))
        return self.slots

    def re_transmit(self):
        self.num_re_trans += 1
        self.slots = self.calc_slots()

    def reset_slots(self):
        self.num_re_trans = 0
        self.slots = self.calc_slots()


# パケット生成クラスを作ろうと思って辞めた
class Packet:
    def __init__(self, mode, rate, level):
        self.PLCP_preamble = 16

# Userリストを作成(現在は全く同じUserをnum_users分作成している)(今後Userごとに何かしらのパラメータを変更する場合,ここを変更する)
def create_users(num_users, seed=None):
    return [User(id=i, seed=seed) for i in range(num_users)]


# 送るデータ量と伝送レートから伝送時間を計算
def calc_trans_time(data, rate):
    return data / (rate * 10**6)


# バックオフ時間の計算
def calc_cw_time(slots, mode):
    return slots * TRANS_MODE[mode]['SLOT_TIME'] * 10**(-6)


# 任意のIFSの時間を持ってくる関数
def calc_ifs_time(ifs, mode):
    return TRANS_MODE[mode][ifs] * 10**(-6)

# シミュレーション関数
def simulate_transmission(users: User, duration: int, rate, output_mode, mode):
    current_time = 0
    collision_count = 0
    trans_data = 1472 * 8 # UDP level
    # trans_data = 1500 * 8 # IP level
    total_data_transmitted = 0
    trans_num = 0

    preamble_time = 20 / (10**6)
    FCS_time = 4 * 8 / (rate * 10**6)
    ACK_time = 28 / 10**6
    MAC_header_time = 24 * 8 / (rate * 10**6)

    cw_time_list = [(user.id, user.slots) for user in users]
    # print(cw_time_list)

    EIFS_time = calc_ifs_time('SIFS', mode) + ACK_time + calc_ifs_time('DIFS', mode)
    trans_time = calc_trans_time(trans_data, rate)

    while current_time < duration:
        cw_time_list.sort(key=lambda x: x[1])

        min_user = min(users, key=lambda u: u.slots)
        collisions = sorted([user for user in users if (
            user.slots == min_user.slots and user.id != min_user.id)], key=lambda u: u.id)
        if collisions:
            collisions.append(min_user)
        collisions_ids = [user.id for user in collisions]


        # print(cw_time_list)
        # print('collisions_ids: ', collisions_ids)

        cw_time = calc_cw_time(min_user.slots, mode)
        min_slots = min_user.slots

        # 衝突時処理
        if collisions_ids:
            collision_count += 1

            # バックオフ + DIFS時間 + データ送信が今の時間を超えないなら
            if (current_time + cw_time + preamble_time + MAC_header_time + trans_time + FCS_time + EIFS_time) < duration:
                current_time += cw_time + preamble_time + MAC_header_time + trans_time + FCS_time + EIFS_time

                if output_mode in [PRINT_MODE[0], PRINT_MODE[1]]:

                    print(f"\nTime: {current_time}s - Collision detected! Users: {collisions_ids}")

                    for user in collisions:
                        print(f"User {user.id} waited {user.slots} slots before collision.")

                for user in users:
                    # 衝突Userだったら再送処理
                    if user in collisions:
                        user.re_transmit()

                    # それ以外はslotsから最小slotsを引く
                    else:
                        user.slots -= min_slots

                # print([(user.id, user.num_re_trans, user.slots) for user in users])

            # 超えるなら終了
            else:
                current_time = duration

        # 成功時処理
        else:
            trans_num += 1
            min_user.num_transmitted += 1

            # 送信時間が制限時間を超えないなら
            if (current_time + cw_time + preamble_time + MAC_header_time + trans_time + FCS_time + EIFS_time) < duration:
                current_time += cw_time + preamble_time + MAC_header_time + trans_time + FCS_time + EIFS_time
                min_user.data_transmitted += trans_data
                total_data_transmitted += trans_data

            # 超えるなら
            else:
                # print(f"current : {current_time}")
                
                current_time = duration
                remaining_time = duration -  (cw_time + preamble_time + MAC_header_time + current_time)
                
                # print(f"remaining : {remaining_time}")

                # 残り伝送時間内にデータフレームを送る時間があるなら`remaining_time`がプラス
                if 0 < remaining_time:
                
                    transmitted_data = remaining_time * rate * 10**6

                    total_data_transmitted += transmitted_data
                    min_user.data_transmitted = transmitted_data
                

            if output_mode == PRINT_MODE[1]:
                print(
                    f"\nTime: {current_time}s - User {min_user.id} transmitted successfully with CW = {cw_time:.6f} seconds (waited {min_user.slots} slots)")

                for user in users:
                    print(f'User {user.id} , waited {user.slots} slots')

            for user in users:
                # 送信したUserのslotsを再生成
                if user.id == min_user.id:
                    user.reset_slots()

                # 送信していないUserのslotsから最小slotsを引く
                else:
                    user.slots -= min_slots

            # print([(user.id, user.num_re_trans, user.slots) for user in users])

    if output_mode != PRINT_MODE[3]:
        print("\nSimulation ended. Results:")
        print('Total rate : ', total_data_transmitted / duration / 10**6)

    return float(total_data_transmitted / duration / 10**6)


if __name__ == "__main__":
    # python main.pyで実行すると以下が実行される
    n = 80

    users = create_users(n)
    simulate_transmission(users, 60, 24, output_mode=PRINT_MODE[2], mode='a')
