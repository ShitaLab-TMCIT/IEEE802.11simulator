import numpy as np
import pandas as pd
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from main import create_users, simulate_transmission, PRINT_MODE

# パラメータ
rate = 24  # Mbps
duration = 60  # seconds
mode = 'a'  # Transmission mode
n_values = [1, 10, 20, 30, 40, 50, 60, 70, 80]
num_simulations = 10  # 各nでのシミュレーション回数

# 並列処理を実行する関数
def process_single_n(n):
    users = create_users(n)
    data_transmitted = simulate_transmission(users, duration, rate, output_mode=PRINT_MODE[3], mode=mode)
    return n, float(data_transmitted)

# 結果格納用リスト
results = []

# 並列処理の実行
for simu in tqdm(range(num_simulations), desc="Simulations", leave=False):
    with ThreadPoolExecutor() as executor:
        # フューチャーオブジェクトを生成
        futures = {executor.submit(process_single_n, n): n for n in n_values}
        
        # tqdmでn_valuesに対応した進捗バーを表示
        res = []
        for future in tqdm(as_completed(futures), total=len(n_values), desc=f"Simulation {simu + 1}", leave=False):
            n, data_transmitted = future.result()
            res.append(data_transmitted)
        results.append(res)

# DataFrameの作成
df_results = pd.DataFrame(np.array(results), columns=n_values).to_csv('./out/out.csv')
