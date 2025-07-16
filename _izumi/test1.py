import time
from random import randint as random_randint
from numpy.random import randint as numpy_randint
import numpy


class SlotObject :
    """
    スロットのリストを管理するクラス
    """
    slots = numpy.ndarray
    index : int = 0
    cw_max : int = 1023

    def __init__(self, n : int = 0):
        self.cw_max = n
        self.slots = numpy.random.randint(0, self.cw_max, size=1000000)

    def get(self):
        self.index += 1
        if (self.index < 1000000):
            return self.slots[self.index]
        else:
            self.index = 0
            self.slots = numpy.random.randint(0, self.cw_max, size=1000000)
            return self.slots[self.index]


start_time = time.time()

for i in range(100000):
    random_randint(0, 1023)

end_time = time.time()

print(f"Time taken for 1,000,000 random.randint calls: {end_time - start_time} seconds")


start_time = time.time()

cw = numpy_randint(0, 1023, size=100000)
for i in range(100000):
    cw[i]

end_time = time.time()

print(f"Time taken for 1,000,000 numpy.random.randint calls: {end_time - start_time} seconds")
