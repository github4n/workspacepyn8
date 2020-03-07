import pandas as pd
import ccxt
from time import sleep
from datetime import datetime, timedelta
import time
from coin_quant_class_190806.program.class9.auto_trade_function import next_run_time, place_order, get_okex_candle_data, \
    auto_send_email
import numpy

pd.set_option('expand_frame_repr', False)  # 当列太多时不换行
pd.set_option('display.max_rows', 1000)  # 显示行数

"""
在OK交易所实现布林策略的实盘交易

持续自动交易，需要循环操作，下面是循环内容
1.获取账户信息
2.获取对应周期K线数据并计算交易信号
3.根据交易信号执行买入或卖出操作
4.等待到下个周期开始时，继续循环

"""
"""
处理异常,网络中断如何处理？
"""

# 初始化交易所
exchange = ccxt.okex3()

# ok子账号
exchange.apiKey = "64e867b6-a008-4fc4-81c5-d1d017e382b3"
exchange.secret = "FCE2B0918CD3876B51184F6A53028DDD"
exchange.password = "841122"

try_num = 0  # 异常初始尝试次数
max_try_num = 10  # 异常后最大尝试次数

while True:
    # break
    try:
        # exit()
        # ===监控邮件内容
        email_title = '策略报表'
        email_content = ''

        symbol = "LTC/USDT"  # 交易对
        base_coin = symbol.split('/')[-1]  # 基础币种
        trade_coin = symbol.split('/')[0]  # 交易币种
        balance = exchange.fetch_balance()  # 获取账户信息

        if trade_coin not in balance['total'].keys():
            balance['total'][trade_coin] = 0
        if base_coin not in balance['total'].keys():
            balance['total'][base_coin] = 0

        base_coin_amount = float(balance['total'][base_coin])
        trade_coin_amount = float(balance['total'][trade_coin])
        print('当前资产:\n', base_coin, base_coin_amount, trade_coin, trade_coin_amount)

        # break
        # exit()

        # # ===sleep直到运行时间
        time_interval = '1m'
        run_time = next_run_time(time_interval)
        print("sleep----等待，直到当前周期结束")
        sleep(max(0, (run_time - datetime.now()).seconds))
        print("sleep----结束，开始计算执行")
        while True:  # 在靠近目标时间时
            if datetime.now() < run_time:
                continue
            else:
                break

        # 获取实时K线数据
        while True:
            df = get_okex_candle_data(exchange, symbol, time_interval)
            _temp = df[df['candle_begin_time_GMT8'] == (
                    run_time - timedelta(minutes=int(time_interval.strip('m'))))]  # 判断是否包含最新的数据
            if _temp.empty:
                print('获取数据不包含最新的数据，重新获取')
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
        # 当收盘价由下向上穿过上轨的时候，做多；然后由上向下穿过下轨的时候，平仓。
        # 当收盘价由上向下穿过下轨的时候，做空；然后由下向上穿过上轨的时候，平仓。

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
        # break
        # exit()
        # pos = 0  # 默认没有仓位为0，有仓位为1
        if trade_coin not in balance.keys():  # 判断账户里有没有这个币种的KEY，没有就赋值0
            balance[trade_coin] = {'total': 0}
            # exit()
        if balance[trade_coin]['total'] >= 0.001:  # 如果交易币种余额大于0.01，表示已经买入，持有仓位
            #  当有仓位时，判断当前周期的上一周期K线交易信号，如果收盘价低于中轨，则平仓
            print('当前有仓位')
            condition = df.iloc[-2]['close'] < df.iloc[-2]['median']
            # if True:
            if condition:
                print('平仓条件达成')
                #  平仓，先取消买卖挂单
                orders_info = exchange.fetch_open_orders(symbol)  # 获取买卖挂单
                for orders in orders_info:
                    # print(orders['id'])
                    exchange.cancel_order(orders['id'], symbol=symbol)  # 取消买卖挂单
                # print(orders_info)
                update_balance = exchange.fetch_balance()  # 获取更新账户资产信息
                amount = update_balance[trade_coin]['free']  # 获取账户最新可用资产
                ticker_data = exchange.fetch_ticker(symbol)  # 获取最新报价信息
                sell_price = 0.98 * ticker_data['bid']  # 用买一价的98%作为卖出价，确保绝大部分情况能成交
                order_info = exchange.create_limit_sell_order(symbol, amount, sell_price)  # 卖单
                print('卖出价格' + str(sell_price) + "," + "卖出数量" + str(amount))
                print('平仓完成')
                # 发邮件通知卖出仓位具体信息
                # 邮件标题
                email_title += '_卖出_' + trade_coin
                # 邮件内容
                email_content += '卖出信息：\n'
                email_content += '卖出数量：' + str(amount) + '\n'
                email_content += '卖出价格：' + str(sell_price) + '\n'
                auto_send_email('444073364@qq.com', email_title, email_content)
            else:
                print("平仓条件未达成")
        else:
            #  当没有仓位时，判断当前周期的上一周期K线交易信号，如果收盘价高于上轨，则开仓
            print('当前无仓位')
            condition = df.iloc[-2]['close'] > df.iloc[-2]['upper']
            # if True:
            if condition:
                print('开仓条件达成')
                amount = 0.0011  # 每次买入仓位
                ticker_data = exchange.fetch_ticker(symbol)  # 获取最新报价信息
                buy_price = 1.02 * ticker_data['ask']  # 用卖一价的102%作为买入价，确保绝大部分情况能成交
                order_info = exchange.create_limit_buy_order(symbol, amount, buy_price)
                print('买入价格' + str(buy_price) + "," + "买入数量" + str(amount))
                print('开仓完成')
                # 发邮件通知卖出仓位具体信息
                # 邮件标题
                email_title += '_买入_' + trade_coin
                # 邮件内容
                email_content += '买入信息：\n'
                email_content += '买入数量：' + str(amount) + '\n'
                email_content += '买入价格：' + str(buy_price) + '\n'
                auto_send_email('444073364@qq.com', email_title, email_content)
            else:
                print("开仓条件未达成")

        print("\n")
        # break
        # =====发送邮件
        # 每个半小时发送邮件
        if run_time.minute % 30 == 0:
            email_title += '_定期通知_' + symbol
            email_content += trade_coin + '交易资产数量：' + str(trade_coin_amount) + '\n'
            email_content += base_coin + '基础资产数量：' + str(base_coin_amount) + '\n'
            auto_send_email('444073364@qq.com', email_title, email_content)

    except Exception as e:
        print('警告！出现异常，停止2秒后再次尝试')
        try_num += 1
        max_try_num = 10
        time.sleep(2)
        #  发邮件通知异常内容、时间和尝试次数
        email_title = '异常出现次数_' + str(try_num)
        email_content = '异常内容提示：' + str(e) + '\n'
        auto_send_email('444073364@qq.com', email_title, email_content)
        if try_num >= max_try_num:
            print('超过最大尝试次数，下单失败。通知***查看报错内容')
            # 尝试多次失败，停止运行
            break
        else:
            continue
    else:
        try_num = 0  # 没有报错重置尝试次数，继续运行
        continue
