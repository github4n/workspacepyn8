import ccxt
import pandas as pd
import time


# =====okex合约交易接口
# 获取合约账户基本信息
def okex_future_balance(exchange):
    """
    返回数据说明：
    account_rights:账户权益
    keep_deposit：保证金
    profit_real：已实现盈亏
    profit_unreal：未实现盈亏
    risk_rate：保证金率
    """

    # 获取期货账户数据
    future_balance = exchange.private_post_future_userinfo()
    future_balance = pd.DataFrame(future_balance['info']).T

    return future_balance


# 获取具体合约账户的信息
def okex_future_position(exchange, symbol='eos_usd', contract_type='quarter'):
    """
    返回数据说明：
    buy_amount(double):多仓数量
    buy_available:多仓可平仓数量
    buy_price_avg(double):开仓平均价
    buy_price_cost(double):结算基准价
    buy_profit_real(double):多仓已实现盈余
    contract_id(long):合约id
    create_date(long):创建日期
    lever_rate:杠杆倍数
    sell_amount(double):空仓数量
    sell_available:空仓可平仓数量
    sell_price_avg(double):开仓平均价
    sell_price_cost(double):结算基准价
    sell_profit_real(double):空仓已实现盈余
    symbol:btc_usd   ltc_usd    eth_usd    etc_usd    bch_usd
    contract_type:合约类型
    force_liqu_price:预估爆仓价
    """
    coin = symbol.split('_')[0].lower()

    rtn_dict = {}

    # 获取合约持仓数据
    temp = exchange.private_post_future_position(params={'symbol': symbol, 'contract_type': contract_type})
    if len(temp['holding']) == 0:  # 持仓数据为空
        return {}
    future_position = temp['holding'][0]
    future_position['force_liqu_price'] = temp['force_liqu_price']
    return future_position


# 合约账户下单
def okex_future_place_order(exchange, symbol, contract_type, order_type, buy_or_sell, price, amount, lever_rate='10'):
    """
    下单
    :param lever_rate:
    :param exchange:
    :param symbol:
    :param contract_type: 合约类型: this_week:当周 next_week:下周 quarter:季度
    :param order_type:
    :param buy_or_sell: 1:开多 2:开空 3:平多 4:平空
    :param price:
    :param amount: 这里的amount是合约张数
    :return:
    """
    new_symbol = symbol.split('/')[0].lower() + '_usd'

    if order_type == 'market':
        match_price = '1'
    elif order_type == 'limit':
        match_price = '0'

    if buy_or_sell == '开多':
        order_type = '1'
    elif buy_or_sell == '开空':
        order_type = '2'
    elif buy_or_sell == '平多':
        order_type = '3'
    elif buy_or_sell == '平空':
        order_type = '4'

    # 下单
    for i in range(5):
        try:
            order_info = exchange.private_post_future_trade(params={'symbol': new_symbol,
                                                                    'contract_type': contract_type,
                                                                    'price': str(price),
                                                                    'amount': str(amount),
                                                                    'type': order_type,
                                                                    'match_price': match_price,
                                                                    'lever_rate': str(lever_rate)
                                                                    }
                                                            )

            print('okex 合约交易下单成功：', symbol, contract_type, order_type, buy_or_sell, price, amount, lever_rate)
            print('下单信息：', order_info, '\n')

            return order_info

        except Exception as e:
            print('okex 合约交易下单报错，1s后重试', e)
            time.sleep(1)

    raise ValueError('okex 合约交易下单报错次数过多，程序终止')


# 合约账户和币币账户之间互相转账
def okex_transfer_spot_to_future(exchange, symbol, amount, direction='spot_to_future'):
    """
    从币币交易账户转币到合约账户
    :param direction:
    :param symbol: 此处symbol的明名和其他的不一样，例如转移xrp，symbol使用xrp_usd
    :param amount:
    :param exchange:
    :return:
    # 1: 币币转合约 2: 合约转币币
    # 改变symbol格式，此处symbol的明名和其他的不一样，例如转移xrp，symbol使用xrp_usd
    """

    new_symbol = symbol.split('/')[0].lower() + '_usd'

    if direction == 'spot_to_future':
        transfer_type = '1'
        transfer_content = 'okex 币币转账至合约：'
    elif direction == 'future_to_spot':
        transfer_type = '2'
        transfer_content = 'okex 合约转账至币币：'
    else:
        print('direction is wrong')
        exit()

    for i in range(5):
        try:
            transfer_info = exchange.private_post_future_devolve(params={'symbol': new_symbol, 'type': transfer_type,
                                                                         'amount': str(amount)})
            print(transfer_content, symbol, amount)
            print('转账信息：', transfer_info, '\n')
            return transfer_info

        except Exception as e:
            print(transfer_content, '报错，1s后重试', e)
            time.sleep(1)

    print(transfer_content, '报错次数过多，程序终止')
    exit()


# =====bitfinex交易所margin账户
# 获取margin账户当前的持仓基本信息
exchange = ccxt.bitfinex2()  # bitfinex2是该交易所的v2版本api，最新的，建议使用。
exchange.apiKey = ''
exchange.secret = ''
margin_info = exchange.private_post_auth_r_positions()  # 获取exchange账户资产
print(margin_info)  # margin_info中的字段含义，需要对着网页上的实际数据，一一对比



