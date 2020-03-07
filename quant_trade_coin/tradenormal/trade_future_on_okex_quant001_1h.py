#coding=utf-8
import time
from datetime import datetime, timedelta
from time import sleep
import traceback

import ccxt
import pandas as pd

# import auto_trade_function as fuc
import quant_trade_coin.function.auto_trade_function as fuc

pd.set_option('expand_frame_repr', False)  # 当列太多时不换行
pd.set_option('display.max_rows', 1000)  # 显示行数

"""
在OK交易所实现布林策略的合约实盘交易

持续自动交易，需要循环操作，下面是循环内容
1.获取账户信息
2.获取对应周期K线数据并计算交易信号
3.根据交易信号执行开多、平多、开空、平空、平空开多、平多开空操作
4.监控账户保证金率情况，防止爆仓
5.等待到下个周期开始时，继续循环

1倍杠杆测试，多倍杠杆要考虑止损和强平
"""

try_num = 0  # 异常初始尝试次数
max_try_num = 10  # 异常后最大尝试次数

while True:
    # break
    try:
        # exit()

        size = 50  # 每次买卖单的张数
        adjust_rate = 0.02  # 买卖价调整幅度
        time_interval = '60m'  # 策略周期

        symbol = "EOS-USD-200327"  # 币本位交割合约
        trade_coin = 'EOS'  # 交易币种，结算币种

        # ===监控邮件内容
        account = "quant001"
        email_title = account+'交割合约_' + symbol
        email_content = ''

        # 初始化交易所
        exchange = ccxt.okex3()
        # ok子账号001
        exchange.apiKey = "11095b41-5ac5-477d-a5c2-cf2dccfe4fcb"
        exchange.secret = "2AD6A8C4EE2E7DF5AEEDD3F23879EAAB"
        exchange.password = "841122"
        balance = exchange.fetch_balance(params={'type': 'futures'})  # 获取币本位交割合约账户信息

        if trade_coin not in balance['total'].keys():
            balance['total'][trade_coin] = 0
        trade_coin_amount = float(balance['total'][trade_coin])
        print('当前资产:', trade_coin, trade_coin_amount)

        #  如何找出隐含方法
        # print(dir(exchange))  #  输出所有可用的方法，包含隐含api的方法
        # print(exchange.api)  #  api访问点列表

        # # ===计算下个周期时间
        run_time = fuc.next_run_time(time_interval)

        # 获取实时K线数据
        while True:
            df = fuc.get_okex_future_candle_data(exchange, symbol, time_interval)
            df.sort_values(ascending=True, inplace=True, by='candle_begin_time_GMT8')
            _temp = df[df['candle_begin_time_GMT8'] == (
                    run_time - timedelta(minutes=int(time_interval.strip('m'))))]  # 判断是否包含最新的数据
            if _temp.empty:
                print('获取数据不包含最新的数据，重新获取')
                sleep(2)
                # break
                continue
            else:
                print('获取数据包含最新的数据')
                break
        # print(df)
        # break
        # exit()
        # 根据K线数据计算交易信号
        # =====产生交易信号：布林线策略
        # ===布林线策略
        # 布林线中轨：n天收盘价的移动平均线
        # 布林线上轨：n天收盘价的移动平均线 + m * n天收盘价的标准差
        # 布林线下轨：n天收盘价的移动平均线 - m * n天收盘价的标准差
        # 当收盘价处于上轨上方，有空仓，则平空，没多仓，则开多
        # 当收盘价处于上轨下方，中轨上方，有空仓，则平空
        # 当收盘价处于中轨下方，下轨上方，有多仓，则平多
        # 当收盘价处于下轨下方，有多仓，则平多，没空仓，则开空

        # 参数设置
        n = 20
        m = 2
        # 均线计算
        df['median'] = df['close'].rolling(n, min_periods=1).mean()
        # 计算上轨和下轨
        df['std'] = df['close'].rolling(n, min_periods=1).std(ddof=0)  # ddof代表标准差自由度
        df['upper'] = df['median'] + m * df['std']
        df['lower'] = df['median'] - m * df['std']
        # print(df)
        # print(df.iloc[-2]['close'])
        # break
        # exit()
        # pos = 0  # 默认没有仓位为0，有仓位为1

        #  交易信号计算
        condition1 = df.iloc[-2]['close'] > df.iloc[-2]['upper']  # 上轨上方
        condition2 = df.iloc[-2]['close'] > df.iloc[-2]['median']  # 中轨上方
        condition3 = df.iloc[-2]['close'] < df.iloc[-2]['median']  # 中轨下方
        condition4 = df.iloc[-2]['close'] < df.iloc[-2]['lower']  # 下轨下方

        #  获取合约仓位信息，long_qty为多仓持仓数，short_qty为空仓持仓数
        position = exchange.futures_get_instrument_id_position(
            params={'instrument_id': symbol}
        )
        long_qty = position['holding'][0]['long_qty']
        short_qty = position['holding'][0]['short_qty']
        long_qty = int(long_qty)
        short_qty = int(short_qty)

        if condition2:
            # 中轨上方，如果有空仓，则平空，如果在上轨上方，没多仓，则开多
            print('中轨上方')
            if short_qty > 0:
                print("平仓----空")
                size = short_qty  # 空仓张数
                action_type = 4  # 1.开多 2.开空 3.平多 4.平空
                order_info = fuc.futures_post_order(exchange, symbol, action_type, adjust_rate, size)  # 下单平空
            # condition1 = True
            # long_qty = 0
            if condition1 & (long_qty == 0):
                print("上轨上方---开仓---多")
                action_type = 1  # 1.开多 2.开空 3.平多 4.平空
                order_info = fuc.futures_post_order(exchange, symbol, action_type, adjust_rate, size)  # 下单开多
                # print(order_info)
            elif long_qty > 0:
                print("持仓----多")
            else:
                print("开仓条件未达成")
        elif condition3:
            # 中轨下方，如果有多仓，则平多，如果在下轨下方，没空仓，则开空
            print('中轨下方')
            if long_qty > 0:
                print("平仓----多")
                size = long_qty  # 多仓张数
                action_type = 3  # 1.开多 2.开空 3.平多 4.平空
                order_info = fuc.futures_post_order(exchange, symbol, action_type, adjust_rate, size)  # 下单平多
            if condition4 & (short_qty == 0):
                print("下轨下方---开仓---空")
                action_type = 2  # 1.开多 2.开空 3.平多 4.平空
                order_info = fuc.futures_post_order(exchange, symbol, action_type, adjust_rate, size)  # 下单开空
            elif short_qty > 0:
                print("持仓----空")
            else:
                print("开仓条件未达成")

        # break
        # exit()

        # break

        print("sleep----等待，直到下个周期")
        sleep(max(0, (run_time - datetime.now()).seconds))
        sleep(5)  # 多等待5秒，有交易数据
        print("\n")
        print("sleep----结束，新周期开始")
        while True:  # 在靠近目标时间时
            if datetime.now() < run_time:
                continue
            else:
                break

        # =====发送邮件
        # 每个半小时发送邮件
        print(run_time)
        if run_time.minute % 30 == 0:
            email_title += '_定期通知'
            email_content += trade_coin + '账户权益：' + str(trade_coin_amount) + '\n'
            fuc.auto_send_email('444073364@qq.com', email_title, email_content)

    except Exception as e:
        print('警告！出现异常，停止3秒后再次尝试')
        try_num += 1
        max_try_num = 10
        time.sleep(3)
        #  发邮件通知异常内容、时间和尝试次数
        email_title = '异常出现次数_' + str(try_num)
        email_content = '异常内容提示：' + str(e) + '\n'
        print(str(e))
        traceback.print_exc()
        exc = traceback.format_exc()
        email_content = '异常内容提示2：' + str(exc) + '\n'
        fuc.auto_send_email('444073364@qq.com', email_title, email_content)
        if try_num >= max_try_num:
            print('超过最大尝试次数，下单失败。通知***查看报错内容')

            # 尝试多次失败，停止运行
            break
        else:
            continue
    else:
        try_num = 0  # 没有报错重置尝试次数，继续运行
        continue
