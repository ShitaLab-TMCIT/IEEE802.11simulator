import os
import csv
from typing import Dict, List
import json

# 型の前提
# result_old, result_new : Dict[device_count, Dict[rate, List[result_data_TY]]]

def export_throughput_csv(
    result_old: Dict,
    result_new: Dict,
    root_dir: str
):
    os.makedirs(root_dir, exist_ok=True)

    ip_csv_path = os.path.join(root_dir, "throughput_IP_compare.csv")
    udp_csv_path = os.path.join(root_dir, "throughput_UDP_compare.csv")

    # -------------------------
    # IP スループット CSV
    # -------------------------
    with open(ip_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["device_count", "rate", "trial", "IP_old", "IP_new"])

        for device_count in result_old:
            for rate in result_old[device_count]:
                old_list = result_old[device_count][rate]
                new_list = result_new[device_count][rate]

                for i, (old, new) in enumerate(zip(old_list, new_list)):
                    writer.writerow([
                        device_count,
                        rate,
                        i,
                        old["IP"],
                        new["IP"],
                    ])

    # -------------------------
    # UDP スループット CSV
    # -------------------------
    with open(udp_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["device_count", "rate", "trial", "UDP_old", "UDP_new"])

        for device_count in result_old:
            for rate in result_old[device_count]:
                old_list = result_old[device_count][rate]
                new_list = result_new[device_count][rate]

                for i, (old, new) in enumerate(zip(old_list, new_list)):
                    writer.writerow([
                        device_count,
                        rate,
                        i,
                        old["UDP"],
                        new["UDP"],
                    ])

    print("CSV export completed:")
    print(ip_csv_path)
    print(udp_csv_path)

def export_average_throughput_csv(result_old, result_new, root_dir):
    os.makedirs(root_dir, exist_ok=True)

    avg_csv_path = os.path.join(root_dir, "throughput_average_compare.csv")

    with open(avg_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        # ヘッダ
        writer.writerow([
            "device_count",
            "rate",
            "IP_old_avg",
            "IP_new_avg",
            "UDP_old_avg",
            "UDP_new_avg",
        ])

        for device_count in result_old:
            for rate in result_old[device_count]:
                old_list = result_old[device_count][rate]
                new_list = result_new[device_count][rate]

                # --- IP ---
                ip_old_avg = sum(d["IP"] for d in old_list) / len(old_list)
                ip_new_avg = sum(d["IP"] for d in new_list) / len(new_list)

                # --- UDP ---
                udp_old_avg = sum(d["UDP"] for d in old_list) / len(old_list)
                udp_new_avg = sum(d["UDP"] for d in new_list) / len(new_list)

                writer.writerow([
                    device_count,
                    rate,
                    ip_old_avg,
                    ip_new_avg,
                    udp_old_avg,
                    udp_new_avg,
                ])

    print("Average CSV exported to:")
    print(avg_csv_path)



old_path = r'G:\git\IEEE802.11simulator\_izumi\result20251228160746.json'
new_path = r'G:\git\IEEE802.11simulator\_izumi\simulator\result\all_result.json'

with open(old_path, 'r') as f:
    result_old = json.load(f)

with open(new_path, 'r') as f:
    result_new = json.load(f)

export_average_throughput_csv(result_old, result_new, r'G:\git\IEEE802.11simulator\_izumi\simulator\result')