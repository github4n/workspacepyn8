"""
程序开头注释
author: xingbuxing
date: 2018年01月11日
功能：本程序主要介绍python的异常处理功能
"""
# 导入python自带的库
import random  # 随机数相关的库
import time  # 时间相关库


# =====异常处理
# 语法
"""
try:
    执行相关语句1
except:
    执行相关语句2
else:
    执行相关语句3
"""

# 说明
"""
1. 先尝试执行相关语句1
2. 若在执行语句1的过程中报错，那么执行相关语句2
3. 若在执行语句1的过程中没有报错，那么执行相关语句3
"""

# =====异常处理的一个例子


# ===买入btc函数
def buy_btc():  # 这个函数没有参数
    """
    此程序用于下单买入BTC，但是买入过程中，程序有80%的概率报错。
    """
    random_num = random.random()  # 产生0-1之间的随机数
    if random_num <= 0.1:
        print('成功买入BTC！')
        return
    else:
        raise ValueError('程序报错！买入BTC失败！')

# buy_btc()


# === 下单买入BTC，若买入失败的话重新尝试买入，最多尝试5次。
max_try_num = 5
tyr_num = 0

while True:
    try:  # 尝试做以下事情
        buy_btc()
    except:  # 如果因为各种原因报错
        print('警告！下单出错，停止1秒后再次尝试')
        tyr_num += 1
        time.sleep(2)
        if tyr_num >= max_try_num:
            print('超过最大尝试次数，下单失败。通知***查看报错内容')
            # 此处需要执行相关程序，通知某些人
            break
        else:
            continue
    else:  # 如果没有报错
        break
