"""
邢不行-数字货币量化课程
微信：xingbuxing0807
"""
import ccxt
import pandas as pd
pd.set_option('expand_frame_repr', False)  # 当列太多时不换行


# =====创建ccxt的huobipro交易所
exchange = ccxt.huobipro()
exchange.apiKey = 'rfhfg2mkl3-87f05c13-b2718dd6-fca6c'
exchange.secret = 'f12afb8a-4d068dc0-c6e9f297-5f0c5'
exchange.load_markets()


# =====获取account_id
account = exchange.fetch_accounts()  # 获取margin账户的id
print(account)
id = '9724555'


# =====获取保证金账户持仓数据
balance = exchange.fetch_balance({'id': id})


# =====下单
symbol = 'BTC/USDT'
amount = 0.05
price = 11000
params = {"account-id": id, 'source': 'margin-api'}
# 买单
order_info = exchange.create_limit_buy_order(symbol, amount, price, params)
# 卖单
order_info = exchange.create_limit_sell_order(symbol, amount, price, params)


# =====撤单
order_id = ''
order_info = exchange.cancel_order(order_id)
print(order_info)


# =====借币
params = {
    "symbol": "btcusdt",  # 借币的交易对，必须得是ethusdt这种格式，不是ccxt的BTC/USDT这种标准格式
    'currency': 'usdt',  # 借的币种
    'amount': '1.0',  # 借币的数量，有最小限制。不一定能借到
}
borrow_info = exchange.private_post_margin_orders(params)  # 返回的信息当中有order_id
print(borrow_info)

# =====还币
params = {
    'id': '',  # 告诉是还哪一笔交易
    'amount': '0.50001319',  # 还币的数量，可以只还部分；多还会报错
}
repay_info = exchange.private_post_margin_orders_id_repay(params)
print(repay_info)


