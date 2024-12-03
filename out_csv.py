import numpy as np
import pandas as pd
from tqdm import tqdm
from main import create_users, simulate_transmission, PRINT_MODE

# パラメータ
rate = 24  # Mbps
duration = 60  # seconds
mode = 'a'  # Transmission mode
n_values = [1, 10, 20, 30, 40, 50, 60, 70, 80]
num_simulations = 10  # 各nでのシミュレーション回数

results = []

def process_n(d, duration, rate, mode):
    users = create_users(n)
    data_transmitted = simulate_transmission(users, duration, rate, output_mode=PRINT_MODE[3], mode=mode)
    return float(data_transmitted)

for simu in tqdm(range(num_simulations), leave=False):
    res = []
    for n in tqdm(n_values, desc='Number of Users', leave=False):
        users = create_users(n)
        data_transmitted = simulate_transmission(users, duration, rate, output_mode=PRINT_MODE[3], mode=mode)
        res.append(float(data_transmitted))
    results.append(res)


# DataFrameの作成
df_results = pd.DataFrame(np.array(results), columns=n_values).to_csv('./out/out.csv')