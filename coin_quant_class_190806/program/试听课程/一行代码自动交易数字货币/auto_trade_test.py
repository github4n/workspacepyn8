#程序化自动交易简单尝试

#一般流程1.获取行情信息，账户信息 2.根据策略处理信息，获取操作信号 3.执行操作

import ccxt
import time

exchange=ccxt.okex3()
#设置翻墙代理
# exchange.proxies = {
#     'http': 'socks5://127.0.0.1:1080',
#     'https': 'socks5h://127.0.0.1:1080'
# }
#访问固定账户必要信息
# exchange.apiKey="24478a2b-1639-46fa-897a-f518652b654b"
# exchange.secret="AAE1FDFCB1BC5B6991D48A7C024DD85A"
# exchange.password="841122"
#子账号信息
exchange.apiKey="64e867b6-a008-4fc4-81c5-d1d017e382b3"
exchange.secret="FCE2B0918CD3876B51184F6A53028DDD"
exchange.password="841122"

#获取账户信息
# balance=exchange.fetch_balance()
# print(balance)

#获取当前成交信息
# ticker=exchange.fetch_ticker(symbol="EOS/USDT")
# print(ticker)

#获取K线信息
onlcv_info=exchange.fetch_ohlcv(symbol="EOS/USDT",timeframe="1h",limit=10)
print(onlcv_info)
#模拟循环下单撤单
# while True:
#     order_info=exchange.create_limit_sell_order("EOS/USDT",1,10)
#     # print(order_info)
#     print('下单成功')
#     time.sleep(5)
#     exchange.cancel_order(id=order_info['id'],symbol="EOS/USDT")
#     print('撤销成功')
#     time.sleep(5)
