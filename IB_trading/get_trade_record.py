from ib_insync import *


def get_recent_trades(ib):
    # Get all recent trades (executions)
    trades = ib.trades()
    trade_list = []
    for trade in trades:
        trade_list.append({'symbol': trade.contract.symbol,
                           'action': trade.order.action,
                           'totalQuantity': trade.order.totalQuantity,
                           'avgFillPrice': trade.orderStatus.avgFillPrice,
                           'order_status': trade.orderStatus.status})

    return trade_list


def get_open_orders(ib):
    # Get all open orders
    open_orders = ib.reqAllOpenOrders()
    print(open_orders)

    open_orders_dict = {}
    for my_order in open_orders:
        open_orders_dict['symbol'] = my_order.contract.symbol
        open_orders_dict['action'] = my_order.order.action
        open_orders_dict['totalQuantity'] = my_order.order.totalQuantity
        open_orders_dict['order_status'] = my_order.orderStatus.status

    return open_orders_dict


if __name__ == '__main__':
    # Connect to IBKR TWS or Gateway
    ib = IB()
    ib.connect('127.0.0.1', 7497, clientId=1)  # Adjust port and clientId as needed

    trade_dict = get_recent_trades(ib)
    print(trade_dict)
    open_orders_dict = get_open_orders(ib)
    print(open_orders_dict)