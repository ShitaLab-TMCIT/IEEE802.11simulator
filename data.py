import pandas as pd
import os


os.chdir(r"C:\Users\shugo\OneDrive - 東京都立産業技術高等専門学校\out")
# 使用する列
target_cols = ['1', '10', '20', '30', '40', '50', '60', '70', '80']

# CSVファイルのセット（例）
csv_sets = [
    (f"{i} Mbps.csv", f"out_{i}Mbps.csv") for i in [6,9,12,18,24,36,48,54]
]

# 最終的な結果を格納するリスト
result_list = []

for csv1, csv2 in csv_sets:
    # 読み込み（行名はインデックスとして読み込む）
    df1 = pd.read_csv(csv1)
    df2 = pd.read_csv(csv2)

    # 列名を文字列に統一（数値→文字列）
    df1.columns = df1.columns.astype(str)
    df2.columns = df2.columns.astype(str)

    # ターゲット列で絞り込み（存在する列のみ）
    cols_to_use = [col for col in target_cols if col in df1.columns and col in df2.columns]
    df1 = df1[cols_to_use]
    df2 = df2[cols_to_use]

    df1_mean = df1.mean(axis=0)
    df2_mean = df2.mean(axis=0)

    # 平均値をデータフレームに変換
    result_list.append(pd.DataFrame([df1_mean.values], columns=df1_mean.index, index=[csv1.removesuffix(".csv")]))
    result_list.append(pd.DataFrame([df2_mean.values], columns=df2_mean.index, index=[csv2.removesuffix(".csv")]))



# 全セット結合
final_df = pd.concat(result_list)

# 出力
final_df.to_csv("output.csv")
print(final_df)
