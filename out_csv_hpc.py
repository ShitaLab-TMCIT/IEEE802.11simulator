import numpy as np
import pandas as pd
from tqdm import tqdm
from multiprocessing import Pool, Manager, Lock
from main import create_users, simulate_transmission, PRINT_MODE

# 固定パラメータ
duration = 60         # シミュレーション時間（秒）
mode = 'a'            # 通信モード
# n_values = [1, 10, 20, 30, 40, 50, 60, 70, 80]
n_values = list(range(1, 81))
num_simulations = 1000  # 各シミュレーション回数
max_processes = 16     # 同時に動作するプロセス数の上限

# プログレスバー更新関数
def update_progress_bar(position, n_completed, lock, progress_bars):
    with lock:
        progress_bars[position] = n_completed

# シミュレーションタスク
# ※process_simulation内でグローバル変数 rate を利用しているため、
#    各シミュレーション実行前にグローバル変数 rate を上書きします。
def process_simulation(task_info):
    simu_index, position = task_info
    local_results = []
    for i, n in enumerate(n_values):
        users = create_users(n)
        # グローバル変数 rate が利用される
        data_transmitted = simulate_transmission(users, duration, rate, output_mode=PRINT_MODE[3], mode=mode)
        local_results.append(float(data_transmitted))
        update_progress_bar(position, i + 1, lock, progress_bars)
    with lock:
        overall_progress.value += 1
    return local_results

if __name__ == '__main__':
    # 伝送レートのリスト（単位: Mbps）
    transmission_rates = [6, 9, 12, 18, 24, 36, 48, 54]

    # 各伝送レートでシミュレーションを実行
    for rate in transmission_rates:
        print(f"\n=== Transmission rate: {rate} Mbps ===")
        
        # Manager等の共有オブジェクトをシミュレーション開始前に初期化
        manager = Manager()
        lock = manager.Lock()
        overall_progress = manager.Value('i', 0)
        progress_bars = manager.list([0] * max_processes)
        
        with Pool(processes=max_processes) as pool:
            overall_pbar = tqdm(total=num_simulations, desc=f'全体の進行度 (rate={rate} Mbps)', position=0)
            thread_pbars = [
                tqdm(total=len(n_values), desc=f'プロセス{i+1}', position=i+1, leave=True)
                for i in range(max_processes)
            ]
            
            tasks = [(simu_index, i % max_processes) for simu_index, i in enumerate(range(num_simulations))]
            results = []
            for res in pool.imap_unordered(process_simulation, tasks):
                results.append(res)
                overall_pbar.n = overall_progress.value
                overall_pbar.refresh()
                for i, bar in enumerate(thread_pbars):
                    bar.n = progress_bars[i]
                    bar.refresh()
            overall_pbar.close()
            for bar in thread_pbars:
                bar.close()
        
        # 結果をDataFrameにまとめ、出力
        df_results = pd.DataFrame(np.array(results), columns=n_values)
        mean_val = df_results[80].mean()
        print(f"Transmission rate: {rate} Mbps, 平均値 (n=80): {mean_val}")
        df_results.to_csv(f'./out/{rate} Mbps_line.csv', index=False)
