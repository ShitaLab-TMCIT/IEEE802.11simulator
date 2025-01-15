import numpy as np
import pandas as pd
from tqdm import tqdm
from multiprocessing import Pool, Manager, Lock
from main import create_users, simulate_transmission, PRINT_MODE

# パラメータ
rate = 24  # Mbps
duration = 60  # seconds
mode = 'a'  # Transmission mode
n_values = [1, 10, 20, 30, 40, 50, 60, 70, 80]
num_simulations = 500  # 各nでのシミュレーション回数
max_processes = 10  # 同時に動作するプロセスの上限

# ロックと共有オブジェクトの初期化
manager = Manager()
lock = manager.Lock()
overall_progress = manager.Value('i', 0)  # 全体の進行度
progress_bars = manager.list([0] * max_processes)  # 各プロセスの進行度

# プログレスバーの更新関数
def update_progress_bar(position, n_completed):
    with lock:
        progress_bars[position] = n_completed

# シミュレーションタスク
def process_simulation(task_info):
    simu_index, position = task_info
    local_results = []
    for i, n in enumerate(n_values):
        users = create_users(n)
        data_transmitted = simulate_transmission(users, duration, rate, output_mode=PRINT_MODE[3], mode=mode)
        local_results.append(float(data_transmitted))
        update_progress_bar(position, i + 1)  # プロセスの進行状況を更新
    with lock:
        overall_progress.value += 1  # 全体の進行状況を更新
    return local_results

# メイン関数
if __name__ == '__main__':
    pre = np.inf
    
    while True:
    
        # マルチプロセスのセットアップ
        with Pool(processes=max_processes) as pool:
            # プログレスバーの設定
            overall_pbar = tqdm(total=num_simulations, desc='全体の進行度', position=0)
            thread_pbars = [tqdm(total=len(n_values), desc=f'プロセス{i+1}', position=i+1, leave=True) for i in range(max_processes)]

            # タスクの準備
            tasks = [(simu_index, i % max_processes) for simu_index, i in enumerate(range(num_simulations))]

            # プロセスの実行と結果の収集
            results = []
            for res in pool.imap_unordered(process_simulation, tasks):
                results.append(res)

                # プログレスバーを更新
                overall_pbar.n = overall_progress.value
                overall_pbar.refresh()
                for i, bar in enumerate(thread_pbars):
                    bar.n = progress_bars[i]
                    bar.refresh()

            # プログレスバーを閉じる
            overall_pbar.close()
            for bar in thread_pbars:
                bar.close()

        # DataFrameの作成と保存
        df_results = pd.DataFrame(np.array(results), columns=n_values)
        print(df_results[80].mean())
        
        if df_results[80].mean() < pre:
            pre = df_results[80].mean()
            print(pre)
            df_results.to_csv('./out/out.csv', index=False)
