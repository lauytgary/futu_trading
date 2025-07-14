from ib_insync import *


def get_recent_trades(ib):
    # Get all recent trades (executions)
    trades = ib.trades()
    trade_dict = {}
    for trade in trades:
        trade_dict['symbol'] = trade.contract.symbol
        trade_dict['action'] = trade.order.action
        trade_dict['totalQuantity'] = trade.order.totalQuantity
        trade_dict['avgFillPrice'] = trade.orderStatus.avgFillPrice
        trade_dict['order_status'] = trade.orderStatus.status

    return trade_dict


def get_open_orders(ib):
    # Get all open orders
    open_orders = ib.reqAllOpenOrders()

    open_orders_dict = {}
    for order in open_orders:
        open_orders_dict['symbol'] = order.contract.symbol
        open_orders_dict['action'] = order.action
        open_orders_dict['totalQuantity'] = order.totalQuantity
        open_orders_dict['order_status'] = order.orderStatus.status

    return open_orders_dict


if __name__ == '__main__':
    # Connect to IBKR TWS or Gateway
    ib = IB()
    ib.connect('127.0.0.1', 7497, clientId=1)  # Adjust port and clientId as needed

    trade_dict = get_recent_trades(ib)
    print(trade_dict)
    open_orders_dict = get_open_orders(ib)
    print(open_orders_dict)