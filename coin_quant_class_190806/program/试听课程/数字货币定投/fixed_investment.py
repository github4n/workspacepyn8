import pandas as pd
import numpy as np


#基础设置
pd.set_option('expand_frame_repr', False) #换行设置
pd.set_option('display.max_columns', 10000, 'display.max_rows', 10000) #显示的最大行列
pd.set_option('precision', 5) #设置pandas显示数字精度
pd.set_option('display.float_format', lambda x: '%.5f' % x) #为了直观的显示数字，不采用科学计数法

#读取表格数据
df=pd.read_csv("BTCUSD_1D.csv",skiprows=1,encoding="gbk")
#选取处理需要的几列数据
df = df[['candle_begin_time', 'close']]

#处理表格数据,目的是计算总收益，总收益需要计算定投到当前时间总成本和总市值

#总成本计算,每日投入金额，投入时间
df['每日定投金额']=100
#投入时间
# df = df[df['candle_begin_time'] >= '2019/1/04']  # 定投开始时间
# df = df[df['candle_begin_time'] <= '2019/1/31']  # 定投结束时间
df['总成本']=df['每日定投金额'].cumsum()

#总市值计算,根据购得数量和价格
df['每日购入数量']=df['每日定投金额']/df['close']
df['累积购入数量']=df['每日购入数量'].cumsum()
df['总市值']=df['累积购入数量']*df['close']
# print(df['总市值'])

#输出数据
de=df[['candle_begin_time','每日定投金额','总成本','每日购入数量','累积购入数量','总市值']]
# print(de)
de.to_csv('fixed_investment.csv',index=False)


