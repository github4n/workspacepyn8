import pandas as pd


pd.set_option('expand_frame_repr', False)  # 当列太多时不换行
pd.set_option('display.max_rows', 20)  # 显示行数

# =====读取hdf数据
# 创建hdf文件
# h5_store = pd.HDFStore('quant_trade_coin\data\EOS-USDT.h5', mode='r')
h5_store = pd.HDFStore('F:\workspacepyn\quant_trade_coin\data\EOS-USDT.h5', mode='r')

123

# h5_store中的key
print(h5_store.keys())

for key in h5_store.keys():
    print(h5_store[key])

# exit()

# 读取某个key指向的数据
# print(h5_store.get('eos_20170701'))
# print(h5_store['eos_20180301'])
# 关闭hdf文件
h5_store.close()
