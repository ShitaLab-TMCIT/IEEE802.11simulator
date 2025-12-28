import typing

device_count = typing.Literal['2','5','10','20','30','40','50','60','70','80','90','100']
# 基地局を除くデバイスの数

rate = typing.Literal['6','9','12','18','24','36','48','54']
# 送信レート(Mbps)

result_data_TY = typing.TypedDict('result_data', {'lap_time':float,'IP':float,'UDP':float,'success':float})
# lap_time : シミュレーションにかかった時間
# IP : IP通信のスループット(Mbps)
# UDP : UDP通信のスループット(Mbps)
# success : 通信の成功回数

result_data : typing.Dict[device_count,typing.Dict[rate,typing.List[result_data_TY]]]