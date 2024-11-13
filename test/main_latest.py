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

def trans_time(data, rate):
    return data / rate

def calc_cw_time(slots, mode):
    return slots * trans_mode[mode]['SLOT_TIME'] * 10**(-6)

def simulate_transmission(users: User, duration: int, rate, print_mode, trans_mode):
    current_time = 0
    collision_count = 0
    transed_data = 0
    trans_rate = rate * 10**6
    n = 0
    
    while current_time < duration:
        cw_time = [(user.id, user.slots) for user in users]
        cw_time.sort(key=lambda x: x[1])
        
        current_time = duration

if __name__ == "__main__":
    n=3