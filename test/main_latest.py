import random

print_mode = {
    0: "Only Collision",
    1: "ALL",
    2: "No Output"
}

trans_mode = {
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


class User:
    def __init__(self, id, n=0, seed=None):
        # if seed is not None:
        #     random.seed(seed+id)

        self.id = id
        self.n = n
        self.slots = self.calc_slots()
        self.num_transmitted = 0
        self.total_data_transmitted = 0

    def calc_slots(self):
        cw_max = 2 ** (4 + self.n) - 1
        self.slots = random.randint(1, min(cw_max, 1023))
        return self.slots

    def re_transmit(self):
        self.n += 1
        self.slots = self.calc_slots()

    def reset_slots(self):
        self.n = 0
        self.slots = self.calc_slots()


def create_users(num_users, seed=None):
    return [User(id=i, seed=seed) for i in range(num_users)]


def calc_trans_time(data, rate):
    return data / (rate * 10**6)


def calc_cw_time(slots, mode):
    return slots * trans_mode[mode]['SLOT_TIME'] * 10**(-6)


def calc_ifs_time(ifs, mode):
    return trans_mode[mode][ifs] * 10**(-6)


def simulate_transmission(users: User, duration: int, rate, output_mode, mode):
    current_time = 0
    collision_count = 0
    transe_data = 1500 * 8
    trans_rate = rate * 10**6
    n = 0

    cw_time = [(user.id, user.slots) for user in users]

    while current_time < duration:
        cw_time.sort(key=lambda x: x[1])

        min_user = min(users, key=lambda u: u.slots)
        collisions = sorted(
            [user for user in users if (user.slots == min_user.slots and user.id != min_user.id)],
            key=lambda u: u.id
        )
        if collisions:
            collisions.append(min_user)
        collisions_ids = [user.id for user in collisions]


        print(cw_time)
        print('collisions_ids: ', collisions_ids)

        trans_time = calc_trans_time(transe_data, rate)
        cw_time = calc_cw_time(min_user.slots, mode)

        print('trans_time: ', trans_time, 'cw_time: ', cw_time)
        if collisions_ids:
            collision_count += 1

            if (current_time + cw_time + trans_time + calc_ifs_time('DIFS', mode)) < duration:
                current_time += cw_time + trans_time + calc_ifs_time('DIFS', mode)
                print(current_time)
                
                if output_mode in [print_mode[0], print_mode[1]]:
                    
                    print(f"\nTime: {current_time}s - Collision detected! Users: {collisions_ids}")
                    
                    for user in collisions:
                        print(f"User {user.id} waited {user.slots} slots before collision.")
            
            for user in users:
                if user in collisions:
                    user.re_transmit()
                
                else:
                    user.slots -= min_user.slots
            
            else:
                current_time = duration
                        
                        

        current_time = duration


if __name__ == "__main__":
    n = 30

    users = create_users(n)
    simulate_transmission(users, 1, 24, output_mode=print_mode[1], mode='g')
