from datetime import datetime, timedelta
import time
import pandas as pd
from email.mime.text import MIMEText
from smtplib import SMTP


# sleep
def next_run_time(time_interval, ahead_time=1):
    if time_interval.endswith('m'):
        now_time = datetime.now()
        time_interval = int(time_interval.strip('m'))

        target_min = (int(now_time.minute / time_interval) + 1) * time_interval
        if target_min < 60:
            target_time = now_time.replace(minute=target_min, second=0, microsecond=0)
        else:
            if now_time.hour == 23:
                target_time = now_time.replace(hour=0, minute=0, second=0, microsecond=0)
                target_time += timedelta(days=1)
            else:
                target_time = now_time.replace(hour=now_time.hour + 1, minute=0, second=0, microsecond=0)

        # sleep直到靠近目标时间之前
        if (target_time - datetime.now()).seconds < ahead_time + 1:
            print('距离target_time不足', ahead_time, '秒，下下个周期再运行')
            target_time += timedelta(minutes=time_interval)
        print('下次运行时间', target_time)
        return target_time
    else:
        exit('time_interval doesn\'t end with m')


# 获取okex的k线数据
def get_okex_candle_data(exchange, symbol, time_interval, limit=None):
    # 抓取数据
    content = exchange.fetch_ohlcv(symbol, timeframe=time_interval, since=0, limit=limit)

    # 整理数据
    df = pd.DataFrame(content, dtype=float)
    df.rename(columns={0: 'MTS', 1: 'open', 2: 'high', 3: 'low', 4: 'close', 5: 'volume'}, inplace=True)
    df['candle_begin_time'] = pd.to_datetime(df['MTS'], unit='ms')
    df['candle_begin_time_GMT8'] = df['candle_begin_time'] + timedelta(hours=8)
    df = df[['candle_begin_time_GMT8', 'open', 'high', 'low', 'close', 'volume']]

    return df


# 获取okex的交割合约k线数据
# k线数据最多可获取最近1440条，单次请求的最大数据量是300条
# 更大的时间范围内获取足够精细的数据，则需要使用多个开始时间/结束时间范围进行多次请求。时间使用ISO 8601标准，如2018-06-20T02:31:00Z
# 开始时间/结束时间参数与北京时间相差8个小时
# 时间粒度，以秒为单位60/180/300/900/1800/3600/7200/14400/21600/43200/86400/604800
#  对应1分钟、3分钟、5分钟、15分钟、30分钟、1小时、2小时、4小时、6小时、12小时、1天、1周
def get_okex_future_candle_data(exchange, symbol, time_interval='1m', start='', end=''):
    # 抓取数据
    granularity = 60
    time_num = int(time_interval[0:-1])
    if time_interval[-1] == 'h':
        granularity *= time_num * 60
    elif time_interval[-1] == 'm':
        granularity *= time_num
    content = exchange.futures_get_instruments_instrument_id_candles(
        params={'instrument_id': symbol,
                'start': start,
                'end': end,
                'granularity': granularity}
    )
    # 整理数据
    df = pd.DataFrame(content, dtype=float)
    df.rename(columns={0: 'MTS', 1: 'open', 2: 'high', 3: 'low', 4: 'close', 5: 'volume'}, inplace=True)
    df['candle_begin_time'] = pd.to_datetime(df['MTS'])
    df['candle_begin_time_GMT8'] = df['candle_begin_time'] + timedelta(hours=8)
    df = df[['candle_begin_time_GMT8', 'open', 'high', 'low', 'close', 'volume']]

    return df


#  普通委托
def futures_post_order(exchange, symbol, action_type, adjust_rate=0, size=0):

    ticker_data = exchange.fetch_ticker(symbol)  # 获取最新报价信息
    price = ticker_data['ask']
    if (action_type == 1) | (action_type == 4):
        #  开多或者平空，用卖一价增加一定幅度作为执行价格，确保绝大部分情况能成交
        price = (1 + adjust_rate) * ticker_data['ask']
    if (action_type == 2) | (action_type == 3):
        #  开空或者平多，用买一价降低一定幅度作为执行价格，确保绝大部分情况能成交
        price = (1 - adjust_rate) * ticker_data['bid']

    order_info = exchange.futures_post_order(
        params={'instrument_id': symbol,
                'type': action_type,
                'price': price,
                'size': size
                }
    )
    #  发消息通知
    # ===监控邮件内容
    trade_type = ''
    if action_type == 1:
        trade_type = '开多'
    elif action_type == 2:
        trade_type = '开空'
    elif action_type == 3:
        trade_type = '平多'
    elif action_type == 4:
        trade_type = '平空'

    email_title = '交割合约_' + symbol
    email_content = ''
    email_title += '_交易类型_' + trade_type
    # 邮件内容
    email_content += '交易信息：\n'
    email_content += '数量：' + str(size) + '\n'
    email_content += '价格：' + str(price) + '\n'
    email_content += '买一价：' + str(ticker_data['bid']) + '\n'
    email_content += '卖一价：' + str(ticker_data['ask']) + '\n'
    auto_send_email('444073364@qq.com', email_title, email_content)
    return order_info


#  策略委托
def futures_post_order_algo(exchange, symbol, action_type, size=0):
    # ticker_data = exchange.fetch_ticker(symbol)  # 获取最新报价信息
    # price = ticker_data['ask']
    algo_variance = 0.0001  # # 委托深度 0.0001-0.01
    order_type = 3  # 1：止盈止损2：跟踪委托3：冰山委托4：时间加权
    price_limit = 0.000001  # 价格限制 >0  <=1000000
    if (action_type == 1) | (action_type == 4):
        price_limit = 1000000
    order_info = exchange.futures_post_order_algo(
        params={'instrument_id': symbol,
                'type': action_type,  # 1:开多2:开空3:平多4:平空
                'order_type': order_type,  # 1：止盈止损2：跟踪委托3：冰山委托4：时间加权
                'size': size,  # 张数
                'algo_variance': algo_variance,  # 委托深度 0.0001-0.01
                'avg_amount': size,  # 单笔均值 2-1000的整数
                'price_limit': price_limit,  # 价格限制 0-1000000
                }
    )
    return order_info


# 下单
def place_order(exchange, order_type, buy_or_sell, symbol, price, amount):
    """
    下单
    :param exchange: 交易所
    :param order_type: limit, market
    :param buy_or_sell: buy, sell
    :param symbol: 买卖品种
    :param price: 当market订单的时候，price无效
    :param amount: 买卖量
    :return:
    """
    for i in range(5):
        try:
            # 限价单
            if order_type == 'limit':
                # 买
                if buy_or_sell == 'buy':
                    order_info = exchange.create_limit_buy_order(symbol, amount, price)  # 买单
                # 卖
                elif buy_or_sell == 'sell':
                    order_info = exchange.create_limit_sell_order(symbol, amount, price)  # 卖单
            # 市价单
            elif order_type == 'market':
                # 买
                if buy_or_sell == 'buy':
                    order_info = exchange.create_market_buy_order(symbol=symbol, amount=amount)  # 买单
                # 卖
                elif buy_or_sell == 'sell':
                    order_info = exchange.create_market_sell_order(symbol=symbol, amount=amount)  # 卖单
            else:
                pass

            print('下单成功：', order_type, buy_or_sell, symbol, price, amount)
            print('下单信息：', order_info, '\n')
            return order_info

        except Exception as e:
            print('下单报错，1s后重试', e)
            time.sleep(1)

    print('下单报错次数过多，程序终止')
    exit()


# 自动发送邮件
def auto_send_email(to_address, subject, content, from_address='1479784663@qq.com', if_add_time=True):
    """
    :param to_address:
    :param subject:
    :param content:
    :param from_address:
    :return:
    使用foxmail发送邮件的程序
    """
    try:
        if if_add_time:
            msg = MIMEText(datetime.now().strftime("%m-%d %H:%M:%S") + '\n\n' + content)
        else:
            msg = MIMEText(content)
        msg["Subject"] = subject + ' ' + datetime.now().strftime("%m-%d %H:%M:%S")
        msg["From"] = from_address
        msg["To"] = to_address

        username = from_address
        password = 'rodefomjbklufhgb'

        server = SMTP('smtp.qq.com', port=587)
        server.starttls()
        server.login(username, password)
        server.sendmail(from_address, to_address, msg.as_string())
        server.quit()

        print('邮件发送成功')
    except Exception as err:
        print('邮件发送失败', err)

# auto_send_email('444073364@qq.com', 'title 你好', "内容")
