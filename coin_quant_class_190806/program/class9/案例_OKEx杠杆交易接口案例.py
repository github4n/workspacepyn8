"""
邢不行-数字货币量化课程
微信：xingbuxing0807
"""
import ccxt
import pandas as pd
pd.set_option('expand_frame_repr', False)  # 当列太多时不换行


"""
按日计息，很贵
借什么币就还什么币
5倍杠杆，最多借4倍
借的币可以转出到其他账户，但是数量有限
"""


# =====创建ccxt的okex交易所
exchange = ccxt.okex3()  # 此处是okex第三代api接口，所以是okex3
exchange.apiKey = 'd56e9282-9a16-40d2-9d3e-9c75a19c7af0'
exchange.secret = 'D2729413A0CD98B7AC99CA136C9E5993'
exchange.password = 'xingbuxing'  # okex在创建第三代api的时候，需要填写一个Passphrase。这个填写到这里即可
exchange.load_markets()


# =====获取交易对
df = pd.DataFrame(exchange.markets).T
# print(df[df['futures']])  # 找到有交割合约的交易对
# print(df[df['swap']])  # 找到有永续合约的交易对


# =====获取保证金账户持仓数据
# balance = exchange.fetch_balance(params={'type': 'margin'})  # 相应的，获取期货合约、永续账户持仓，只需将margin改成futures、swap
# print(balance)


# =====借币
# params = {
#     'instrument_id': 'BTC-USDT',  # 借币的交易对，必须得是BTC-USDT这种格式，不是ccxt的BTC/USDT这种标准格式
#     'currency': 'USDT',  # 借的币种
#     'amount': '1',  # 借币的数量，有最小限制。不一定能借到
# }
# borrow_info = exchange.margin_post_accounts_borrow(params)
# # print(borrow_info) # '2338561'


# # =====查看借币状态
# params = {
#     'status': '0'  # 0代表查看没有还清的借款
# }
# borrow_info = exchange.margin_get_accounts_borrowed(params)
# print(borrow_info)


# # =====还币
# params = {
#     'instrument_id': 'BTC-USDT',  # 还币的交易对，得是BTC-USDT这种格式
#     'currency': 'USDT',  # 还的币种
#     'amount': '1',  # 还币的数量，可以只还部分；多还会报错
#     'borrow_id': '2338561',  # 告诉是还哪一笔交易
# }
# repay_info = exchange.margin_post_accounts_repayment(params)
# print(repay_info)


# =====下单
# symbol = 'BTC/USDT'
# amount = 0.05
# price = 11000
# params = {'margin_trading': '2'}
# # 卖单
# order_info = exchange.create_limit_sell_order(symbol, amount, price, params)
# # 买单
# order_info = exchange.create_limit_buy_order(symbol, amount, price, params)
# print(order_info)

# 撤单
# order_id = order_info['id']
# order_info = exchange.cancel_order(order_id, symbol=symbol, params={'type': 'margin'})
# print(order_info)
