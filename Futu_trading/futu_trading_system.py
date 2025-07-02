from futu import *
import pandas as pd
import os
import queue
import datetime
from util_futu_trading_system import create_new_trade_status, read_trade_status
from futu_history_kline import get_futu_hist_kline
from ta_backtest import get_macd

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1200)


class OrderBookTest(OrderBookHandlerBase):
    def __init__(self, my_queue):
        self.my_queue = my_queue

    def on_recv_rsp(self, rsp_pb):
        ret_code, data = super(OrderBookTest,self).on_recv_rsp(rsp_pb)
        self.my_queue.put(data)


def get_bid_ask_data():
    while True:
        try:
            bid_ask_data = my_queue.get(timeout=3)
            print('--------------- bid ask data ---------------')
            print(bid_ask_data)
            return bid_ask_data
        except queue.Empty:
            print('queue empty, retry in 3s')
            time.sleep(3)


def place_order_and_record(action, trd_side, equity_value, lot_size, trd_ctx, code, trade_status_df):
    bid_ask_data = get_bid_ask_data()
    open_datetime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    top_up = 1

    if trd_side == 'BUY':
        action_price = bid_ask_data['Ask'][top_up][0]
        qty = (equity_value // (lot_size * action_price)) * lot_size
    if trd_side == 'SELL':
        action_price = bid_ask_data['Bid'][top_up][0]
        qty = trade_status_df.at[0, 'qty']

    ret_po, data_po = trd_ctx.place_order(price=action_price, qty=qty, code=code, trd_side=trd_side, trd_env=trd_env)
    ##################### Record #####################
    order_id = data_po.at[0, 'order_id']
    time.sleep(10)
    ret_olq, data_olq = trd_ctx.order_list_query(trd_env=trd_env)  # olq represents order_list_query

    ##################### Notification and record after transactions #####################
    if ret_po == RET_OK and ret_olq == RET_OK and order_id in data_olq['order_id'].to_list():
        data_olq = data_olq[data_olq['order_id'] == order_id]
        data_olq = data_olq.reset_index(drop=True)

        order_status = data_olq.at[0, 'order_status']

        if order_status == 'FILLED_ALL':
            if trd_side == 'BUY':
                trade_status_df.at[0, 'qty'] = data_olq[0, 'dealt_qty']
            if trd_side == 'SELL':
                trade_status_df.at[0, 'qty'] = 0

            if trd_env == 'REAL':
                ret_ofq, data_ofq = trd_ctx.order_fee_query([order_id])
                commission = data_ofq.at[0, 'fee_amount']
            else:
                commission = 0

            trade_status_df.at[0, 'cost_price'] = data_olq.at[0, 'dealt_avg_price']
            trade_status_df.at[0, 'open_datetime'] = open_datetime
            trade_status_df.at[0, 'last_realized_capital'] = float(equity_value - commission)
            print('ORDER COMPLETED', action)
        else:
            print('ORDER INCOMPLETE!!!', action)

    ########################### Alert if error ###########################
    else:
        if ret_po != RET_OK: print('PLACE ORDER FAILED')
        if ret_olq != RET_OK: print('ORDER_LIST_QUERY FAILED')
        if order_id not in data_olq['order_id'].to_list(): print('order_id not found in data[order_id].to_list()')

    return trade_status_df


def check_buy_sell_signal(para_dict):
    now_datetime = datetime.datetime.now()
    start_date = (now_datetime - datetime.timedelta(days=300)).strftime('%Y-%m-%d')
    end_date = now_datetime.strftime('%Y-%m-%d')

    ##################### Unpack para dict #####################
    code = para_dict['code']
    profit_target = para_dict['profit_target']
    stop_loss = para_dict['stop_loss']
    holding_day = para_dict['holding_day']
    mdd_in_sample = para_dict['mdd_in_sample']
    trd_ctx = para_dict['trd_ctx']
    quote_ctx = para_dict['quote_ctx']

    ##################### Get hist data and MACD data #####################
    df = get_futu_hist_kline(start_date, end_date, code)
    df = get_macd(df, para_dict)

    #### for testing only ###
    #df.at[df.index[-1], 'trade_logic'] = True
    #########################

    trade_logic = df.at[df.index[-1], 'trade_logic']
    last_price = df.at[df.index[-1], 'close']
    print(df.tail(5))

    ##################### Read trade status #####################
    trade_status_file = code + '_trade_status.csv'
    trade_status_df = pd.read_csv(trade_status_file)
    qty, cost_price, open_date, last_realized_capital, temp_max_equity, num_of_trade = read_trade_status(trade_status_df)

    ##################### Mdd out sample% #####################
    realized_pnl = 0
    unrealized_pnl = qty * (last_price - cost_price)
    equity_value = last_realized_capital + unrealized_pnl

    if equity_value > temp_max_equity:
        temp_max_equity = equity_value

    mdd_out_sample = round(100 * (1 - equity_value / temp_max_equity))

    ##################### Action #####################
    ret, data = quote_ctx.get_stock_basicinfo(Market.HK, SecurityType.STOCK, [code])
    lot_size = int(data.at[0, 'lot_size'])

    #### Open position condition ####
    qty_cond = (qty == 0)
    min_cost_cond = (equity_value > last_price * lot_size)

    #### Close position condition ####
    mdd_cond = (mdd_out_sample > mdd_in_sample)
    profit_taking_cond = last_price - cost_price > profit_target * cost_price / 100
    stop_loss_cond = cost_price - last_price > stop_loss * cost_price / 100
    close_logic = (open_date != datetime.datetime(1999, 12, 31).date()) and (now_datetime.date() - open_date).days >= holding_day

    ##################### Open position #####################
    if trade_logic and qty_cond and min_cost_cond:
        action = 'OPEN'
        trd_side = 'BUY'

        trade_status_df = place_order_and_record(action, trd_side, equity_value, lot_size, trd_ctx, code, trade_status_df)

    ##################### Close position #####################
    elif not qty_cond and (profit_taking_cond or stop_loss_cond or close_logic or mdd_cond):
        if close_logic: action = 'CLOSE'
        elif profit_taking_cond: action = 'PROFIT_TARGET'
        elif stop_loss_cond: action = 'STOP_LOSS'
        elif mdd_cond: action = 'MDD'

        trd_side = 'SELL'

        trade_status_df = place_order_and_record(action, trd_side, equity_value, lot_size, trd_ctx, code, trade_status_df)

        realized_pnl = unrealized_pnl
        unrealized_pnl = 0
        num_of_trade += 1

    ##### Record everyday (update trade status) #####
    columns_to_update = ['temp_max_equity', 'equity_value', 'realized_pnl', 'unrealized_pnl', 'mdd_out_sample', 'num_of_trade']
    update_values = [temp_max_equity, equity_value, realized_pnl, unrealized_pnl, mdd_out_sample, num_of_trade]
    trade_status_df.loc[0, columns_to_update] = update_values

    trade_status_df.to_csv(trade_status_file, index=False)



def main(code, para_dict):
    while True:
        now_datetime = datetime.datetime.now()
        now_weekday = now_datetime.weekday()
        now_hhmmss_int = int(now_datetime.strftime('%H%M%S'))

        if now_weekday <= 4 and (120000 > now_hhmmss_int >= 93000 or 155900> now_hhmmss_int >= 130000):
        #if True:
            if now_hhmmss_int % 10 == 0:
                #### Check specific trade logic ####
                print('Check buy/sell signal for', code)
                check_buy_sell_signal(para_dict)
                time.sleep(1)
                ####################################
        else:
            print(now_datetime, 'Market closed, time sleep for 10min')
            time.sleep(600)


if __name__ == '__main__':
    trd_env = 'SIMULATE'
    quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
    trd_ctx = OpenSecTradeContext(filter_trdmarket=TrdMarket.HK, host='127.0.0.1', port=11111, security_firm=SecurityFirm.FUTUSECURITIES)

    ######################### Initiate para table #########################
    para_dict = {'code': 'HK.HSImain',
                 'cross_direction': 'negative',
                 'macd_zone': 'bull',
                 'mdd_in_sample': 19,
                 'profit_target': 8,
                 'stop_loss': 15,
                 'holding_day': 7,
                 'initial_capital': 200000,
                 'trd_ctx': trd_ctx,
                 'quote_ctx': quote_ctx}

    code = para_dict['code']
    initial_capital = para_dict['initial_capital']

    trade_status_file = code + '_trade_status.csv'
    if not os.path.isfile(trade_status_file):
        create_new_trade_status(code, initial_capital, trade_status_file)

    print('============================= Parameter dict is ready =============================')
    print(para_dict)
    print('===================================================================================')

    if trd_env == 'REAL':
        pwd_unlock = os.environ.get('futu_pw')
        ret, data = trd_ctx.unlock_trade(pwd_unlock)

    my_queue = queue.Queue()
    handler = OrderBookTest(my_queue)
    quote_ctx.set_handler(handler)  # 设置实时摆盘回调
    ret, data = quote_ctx.subscribe([code], [SubType.ORDER_BOOK])  # 订阅买卖摆盘类型，OpenD 开始持续收到服务器的推送
    main(code, para_dict)