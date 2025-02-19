import numpy as np
import pandas as pd
from tqdm import tqdm
import threading
import queue
from main import create_users, simulate_transmission, PRINT_MODE

# パラメータ
rate = 24  # Mbps
duration = 60  # seconds
mode = 'a'  # Transmission mode
# n_values = [1, 10, 20, 30, 40, 50, 60, 70, 80]
n_values = list(range(1, 81))
num_simulations = 100  # 各nでのシミュレーション回数
max_threads = 10  # 同時実行スレッド数の上限

results = []
results_lock = threading.Lock()  # 結果の保存用ロック

# タスクキューの作成
task_queue = queue.Queue()

# シミュレーションタスクをキューに追加
for simu_index in range(num_simulations):
    task_queue.put(simu_index)

# プログレスバーの設定
overall_pbar = tqdm(total=num_simulations, desc='全体の進行度', position=0)
thread_pbars = {}  # スレッドIDとプログレスバーのマッピング

# スレッドのワーカー関数
def worker_thread(thread_id, position):
    thread_pbar = tqdm(total=len(n_values), desc=f'スレッド{thread_id-1}', position=position, leave=True)
    while not task_queue.empty():
        try:
            simu_index = task_queue.get_nowait()
        except queue.Empty:
            break
        res = []
        for n in n_values:
            users = create_users(n)
            data_transmitted = simulate_transmission(users, duration, rate, output_mode=PRINT_MODE[3], mode=mode)
            res.append(float(data_transmitted))
            thread_pbar.update(1)
        with results_lock:
            results.append(res)
        overall_pbar.update(1)
        thread_pbar.reset()
        task_queue.task_done()
    thread_pbar.close()

# スレッドの作成と開始
threads = []
for i in range(max_threads):
    t = threading.Thread(target=worker_thread, args=(i+1, i+1))
    t.start()
    threads.append(t)

# 全てのタスクが完了するのを待機
for t in threads:
    t.join()

overall_pbar.close()

# DataFrameの作成と保存
df_results = pd.DataFrame(np.array(results), columns=n_values)
df_results.to_csv('./out/out.csv', index=False)
