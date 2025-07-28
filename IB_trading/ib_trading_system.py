import time
from ib_insync import *
import pandas as pd
import os
from util_ib_trading_system import create_new_trade_status, read_trade_status, get_mdd_out_sample, update_trade_status_df, get_tick_size
from get_stock_basic_info import get_shares_per_lot
from get_hist_data import get_ib_hist_data
from ta_backtest import get_macd
from get_bid_ask_lv1 import get_bid_ask
from datetime import datetime
from zoneinfo import ZoneInfo


def place_order_and_record(action, trd_side, equity_value, lot_size, ib, contract, trade_status_dict, market):
    bid_ask_data = get_bid_ask(ib, contract)
    last_price = float(bid_ask_data['last_price'])
    bid_price = float(bid_ask_data['bid_price'])
    ask_price = float(bid_ask_data['ask_price'])
    top_up = 1

    if market == 'US':
        open_datetime = datetime.now(ZoneInfo('US/Eastern')).strftime('%Y-%m-%d %H:%M:%S')
        contract_info_dict = get_shares_per_lot(ib, contract)
        tick_size = float(contract_info_dict['minTick'])
    else:
        open_datetime = datetime.now(ZoneInfo('Asia/Hong_Kong')).strftime('%Y-%m-%d %H:%M:%S')
        tick_size = get_tick_size(last_price)

    ######################### Place order #########################
    if trd_side == 'BUY':
        action_price = ask_price + top_up * tick_size
        qty = (equity_value // (action_price * lot_size)) * lot_size
    if trd_side == 'SELL':
        action_price = bid_price - top_up * tick_size
        qty = trade_status_dict['qty']

    limit_order = LimitOrder(trd_side, qty, action_price)
    trade = ib.placeOrder(contract, limit_order)
    permID = trade.order.permID
    order_status = trade.orderStatus.status
    ib.sleep(5)

    ############################## Track trade and record ##############################
    if order_status == 'FILLED':
        total_cost = 0.0
        total_commission = 0.0
        for fill in trade.fills:
            # Gross cost for this fill (price * quantity)
            fill_cost = fill.execution.shares * fill.execution.price
            total_cost += fill_cost

            # Commission for this fill
            total_commission += fill.commissionReport.commission

        trade_status_dict['cost_price'] = total_cost / qty
        trade_status_dict['open_datetime'] = open_datetime
        trade_status_dict['last_realized_capital'] = equity_value - total_commission
        print('ORDER COMPLETED!!!', action)

    else:
        print('ORDER INCOMPLETE!!!', action, trd_side, contract, action_price, order_status)

    trade_status_df = pd.DataFrame([trade_status_dict])

    return trade_status_df



def check_buy_sell_signal(para_dict):
    endDateTime = ''
    durationStr = '1 Y'

    ########################### Unpack para_dict ###########################
    code = para_dict['code']
    ib = para_dict['ib']
    market = para_dict['market']
    mdd_in_sample = float(para_dict['mdd_in_sample'])
    profit_target = float(para_dict['profit_target'])
    stop_loss = float(para_dict['stop_loss'])
    holding_day = int(para_dict['holding_day'])
    contract = para_dict['contract']
    lot_size = int(para_dict['lot_size'])

    ########################### Read trade status ###########################
    trade_status_file = code + '_trade_status.csv'
    trade_status_df = pd.read_csv(trade_status_file)
    qty, cost_price, open_datetime, last_realized_capital, temp_max_equity, num_of_trade, trade_status_dict = read_trade_status(trade_status_df)

    ########################## Get Hist & MACD Data ##########################
    df = get_ib_hist_data(ib, contract, endDateTime, durationStr)
    df = get_macd(df, para_dict)
    trade_logic = df.at[df.index[-1], 'trade_logic']
    last_price = df.at[df.index[-1], 'close']
    print(df.tail(5))
    print('-' * 100)

    ######################### MDD out sample % ############################
    realized_pnl, unrealized_pnl, equity_value, temp_max_equity, mdd_out_sample = get_mdd_out_sample(qty, last_price, cost_price, last_realized_capital, temp_max_equity)

    ######################### Open / Close condition ######################
    if market == 'US':
        now_datetime = datetime.now(ZoneInfo('US/Eastern'))
    else:
        now_datetime = datetime.now(ZoneInfo('Asia/Hong_Kong'))

    #### Open position condition ####
    qty_cond = (qty == 0)
    min_cost_cond = equity_value > last_price * lot_size

    #### Close position condition ####
    mdd_cond = (mdd_out_sample > mdd_in_sample)
    profit_target_cond = last_price - cost_price > profit_target * cost_price / 100
    stop_loss_cond = cost_price - last_price > stop_loss * cost_price / 100
    close_logic = (open_datetime != datetime(1999, 12, 31).date()) and ((now_datetime.date() - open_datetime.date()).days >= holding_day)

    ######################## Open Position ########################
    if trade_logic and qty_cond and min_cost_cond:
        action = 'OPEN'
        trd_side = 'BUY'

        trade_status_df = place_order_and_record(action, trd_side, equity_value, lot_size, ib, contract, trade_status_dict, market)

    ######################## Close position ########################
    elif not qty_cond and (profit_target_cond or stop_loss_cond or close_logic or mdd_cond):
        if close_logic: action = 'CLOSE'
        elif profit_target_cond: action = 'PROFIT_TARGET'
        elif stop_loss_cond: action = 'STOP_LOSS'
        elif mdd_cond: action = 'MDD'

        trd_side = 'SELL'

        trade_status_df = place_order_and_record(action, trd_side, equity_value, lot_size, ib, contract, trade_status_dict, market)

        realized_pnl = unrealized_pnl
        unrealized_pnl = 0.0
        num_of_trade += 1

    ################## Record every day (update trade status) #################
    update_trade_status_df(temp_max_equity, equity_value, realized_pnl, unrealized_pnl,
                           mdd_out_sample, num_of_trade, trade_status_file, trade_status_df)



def main(code, para_dict, market):
    while True:
        # Get current time with timezone
        if market == 'US':
            now_et = datetime.now(ZoneInfo('US/Eastern'))
            now_weekday = now_et.weekday()
            now_hhmmss_int = int(now_et.strftime('%H%M%S'))
            trading_hour = (now_weekday <= 4 and 155900 > now_hhmmss_int >= 93000)
        else:
            now_hkt = datetime.now(ZoneInfo('Asia/Hong_Kong'))
            now_weekday = now_hkt.weekday()
            now_hhmmss_int = int(now_hkt.strftime('%H%M%S'))
            trading_hour = (now_weekday <= 4 and (120000 > now_hhmmss_int >= 93000 or 155900 > now_hhmmss_int >= 130000))

        if trading_hour:
        #if True:
            if now_hhmmss_int % 20 == 0:  # for every 30s
                print('Time:', now_hhmmss_int, 'check buy/sell signal for', code)
                check_buy_sell_signal(para_dict)
                time.sleep(1)
        else:
            print(now_hhmmss_int, 'Market closed, time sleep for 10 min')
            time.sleep(600)


if __name__ == '__main__':
    # Connect to TWS or IB Gateway
    ib = IB()
    ib.connect('127.0.0.1', 7497, clientId=1)

    ############################ Initiate para dict ############################
    para_dict = {'code': 'MSFT',
                 'ib': ib,
                 'market': 'US',
                 'cross_direction': 'negative',
                 'macd_zone': 'bear',
                 'mdd_in_sample': 19,
                 'profit_target': 20,
                 'stop_loss': 10,
                 'holding_day': 40,
                 'initial_capital': 50000}

    code = para_dict['code']
    initial_capital = para_dict['initial_capital']
    market = para_dict['market']

    if market == 'HK':
        contract = Stock(symbol=code, exchange='SEHK', currency='HKD')
        contract_info_dict = get_shares_per_lot(ib, contract)
        lot_size = contract_info_dict['lot_size']
    else:
        contract = Stock(symbol=code, exchange='SMART', currency='USD')
        lot_size = 1

    para_dict['contract'] = contract
    para_dict['lot_size'] = lot_size

    trade_status_file = code + '_trade_status.csv'
    if not os.path.isfile(trade_status_file):
        create_new_trade_status(code, initial_capital, trade_status_file)

    print('============================= Parameter dict is ready =============================')
    print(para_dict)
    print('====================================================================================')
    main(code, para_dict, market)