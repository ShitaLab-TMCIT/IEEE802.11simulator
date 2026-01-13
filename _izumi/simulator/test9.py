import json,os,datetime
import csv

INPUT_JSON = os.path.join(os.path.dirname(__file__),"result","perfect_result20260114065048.json")
OUTPUT_CSV = os.path.join(os.path.dirname(__file__),"result",f"{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}_result.csv")

# JSONを読み込む
with open(INPUT_JSON, "r", encoding="utf-8") as f:
    data = json.load(f)

result = data["result"]

# device_count と rate を取得（文字列→数値にしてソート）
device_counts = sorted(result.keys(), key=lambda x: int(x))

rates = set()
for dc in result.values():
    rates.update(dc.keys())

rates = sorted(rates, key=lambda x: int(x))

# CSV書き出し
with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)

    # ヘッダ
    writer.writerow(["device_count"] + rates)

    # 各 device_count の行
    for dc in device_counts:
        row = [f"{dc}台"]
        for rate in rates:
            if rate in result[dc]:
                val = result[dc][rate].get("UDP", "")
                row.append(val)
            else:
                row.append("")
        writer.writerow(row)

print("CSV written to", OUTPUT_CSV)
