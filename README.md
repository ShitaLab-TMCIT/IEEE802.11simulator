# IEEE802.11simulator
Network simulator for IEEE802.11 (Wi-Fi) using MATLAB


- シミュレータ本体は`main.py`
- 同条件複数回行う場合は`out_csv.py`で
- CPUがめちゃつよで安全なPCを持っているのなら`out_csv_hpc.py`を使うと早い(13,14世代Intelで使わないこと)
- 出力されたcsvの確認は`main.ipynb`で行う
- `out_csv.py`と`main.ipynb`は`pip install -r requirements.txt`しないと実行できない
