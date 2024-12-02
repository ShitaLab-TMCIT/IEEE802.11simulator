import random
import math

PRINT_MODE = {
    0: "Only Collision",
    1: "ALL",
    2: "Only Results",
    3: "No Output"
}

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


class User:
    def __init__(self, id, n=0, seed=None):
        # if seed is not None:
        #     random.seed(seed+id)

        self.id = id
        self.num_re_trans = n
        self.slots = self.calc_slots()
        self.num_transmitted = 0
        self.data_transmitted = 0

    def calc_slots(self):
        cw_max = 2 ** (4 + self.num_re_trans) - 1
        self.slots = random.randint(1, min(cw_max, 1023))
        return self.slots

    def re_transmit(self):
        self.num_re_trans += 1
        self.slots = self.calc_slots()

    def reset_slots(self):
        self.num_re_trans = 0
        self.slots = self.calc_slots()


class Packet:
    def __init__(self, mode, rate, level):
        self.PLCP_preamble = 16

def create_users(num_users, seed=None):
    return [User(id=i, seed=seed) for i in range(num_users)]


def calc_trans_time(data, rate):
    return data / (rate * 10**6)


def calc_cw_time(slots, mode):
    return slots * TRANS_MODE[mode]['SLOT_TIME'] * 10**(-6)


def calc_ifs_time(ifs, mode):
    return TRANS_MODE[mode][ifs] * 10**(-6)


def simulate_transmission(users: User, duration: int, rate, output_mode, mode):
    current_time = 0
    collision_count = 0
    trans_data = 1472 * 8 # UDP
    # trans_data = 1500 * 8 # IP
    total_data_transmitted = 0
    trans_num = 0

    preamble_time = 20 / (10**6)
    FCS_time = 4 * 8 / (rate * 10**6)
    # ACK_time = 14 * 8 / (rate * 10**6)
    ACK_time = 20 / 10**6
    MAC_header_time = 24 * 8 / (rate * 10**6)

    cw_time_list = [(user.id, user.slots) for user in users]
    # print(cw_time_list)
    
    nav_time = calc_ifs_time('SIFS', mode) + ACK_time + calc_ifs_time('DIFS', mode)
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

        # nav_time = calc_ifs_time('DIFS', mode) + (15 * TRANS_MODE[mode]['SLOT_TIME'] / 2) * 10**(-6)
        cw_time = calc_cw_time(min_user.slots, mode)
        min_slots = min_user.slots

        # print('trans_time: ', trans_time, 'cw_time: ', cw_time, 'min_user_slots', min_slots)
        # 衝突
        if collisions_ids:
            collision_count += 1

            # バックオフ + データ送信 + DIFS時間が今の時間を超えないなら
            if (current_time + cw_time + preamble_time + MAC_header_time + trans_time + FCS_time + nav_time) < duration:
                current_time += cw_time + preamble_time + MAC_header_time + trans_time + FCS_time + nav_time
                # print(current_time)

                if output_mode in [PRINT_MODE[0], PRINT_MODE[1]]:

                    print(f"\nTime: {current_time}s - Collision detected! Users: {collisions_ids}")

                    for user in collisions:
                        print(
                            f"User {user.id} waited {user.slots} slots before collision.")

                for user in users:
                    if user in collisions:
                        user.re_transmit()

                    else:
                        user.slots -= min_slots

                # print([(user.id, user.num_re_trans, user.slots) for user in users])

            # 超えるなら終了
            else:
                current_time = duration

        # 成功
        else:
            trans_num += 1
            min_user.num_transmitted += 1

            # 送信時間が制限時間を超えないなら
            if (current_time + cw_time + preamble_time + MAC_header_time + trans_time + FCS_time + calc_ifs_time('SIFS', mode) + ACK_time + calc_ifs_time('DIFS', mode)) < duration:
                current_time += cw_time + preamble_time + MAC_header_time + trans_time + FCS_time + calc_ifs_time('SIFS', mode) + ACK_time + calc_ifs_time('DIFS', mode)
                min_user.data_transmitted += trans_data
                total_data_transmitted += trans_data

            # 超えるなら
            else:
                current_time = duration
                remaining_time = duration -  (cw_time + preamble_time + MAC_header_time)
                transmitted_data = remaining_time * rate * 10**6

                total_data_transmitted += transmitted_data
                min_user.data_transmitted = transmitted_data

            if output_mode == PRINT_MODE[1]:
                print(
                    f"\nTime: {current_time}s - User {min_user.id} transmitted successfully with CW = {cw_time:.6f} seconds (waited {min_user.slots} slots)")

                for user in users:
                    print(f'User {user.id} , waited {user.slots} slots')

            for user in users:
                if user.id == min_user.id:
                    user.reset_slots()

                else:
                    user.slots -= min_slots

            # print([(user.id, user.num_re_trans, user.slots) for user in users])

    # for user in users:
    #     average_transmission_rate = user.data_transmitted / duration / 10**6
    #     print(f"User {user.id} transmitted {user.num_transmitted} times, total data transmitted: {user.data_transmitted} bits, average transmission rate: {average_transmission_rate:.3f} Mbps")

    if output_mode != PRINT_MODE[3]:
        print("\nSimulation ended. Results:")
        print('Total rate : ', total_data_transmitted / duration / 10**6)

    return float(total_data_transmitted / duration / 10**6)


if __name__ == "__main__":
    n = 40

    users = create_users(n)
    simulate_transmission(users, 60, 24, output_mode=PRINT_MODE[2], mode='a')
