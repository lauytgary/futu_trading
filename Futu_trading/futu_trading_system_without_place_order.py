from futu import *
import pandas as pd
import os
import datetime
from util_futu_trading_system import create_new_trade_status, read_trade_status, cal_commission
from futu_history_kline import get_futu_hist_kline
from ta_backtest import get_macd

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1200)


def record_buy_sell(action, last_price, trd_side, equity_value, lot_size, code, is_etf, trade_status_df):
    open_datetime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if trd_side == 'BUY':
        qty = (equity_value // (lot_size * last_price)) * lot_size
        trade_status_df.at[0, 'qty'] = qty
    if trd_side == 'SELL':
        qty = trade_status_df.at[0, 'qty']
        trade_status_df[0, 'qty'] = 0

    print(trd_side, code, qty, last_price, action)
    commission = cal_commission(last_price, qty, is_etf)

    trade_status_df.at[0, 'cost_price'] = float(last_price)
    trade_status_df.at[0, 'open_datetime'] = open_datetime
    trade_status_df.at[0, 'last_realized_capital'] = float(equity_value - commission)

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
    is_etf = (data.at[0, 'stock_type'] == 'ETF')

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

        trade_status_df = record_buy_sell(action, last_price, trd_side, equity_value, lot_size, code, is_etf, trade_status_df)

    ##################### Close position #####################
    elif not qty_cond and (profit_taking_cond or stop_loss_cond or close_logic or mdd_cond):
        if close_logic: action = 'CLOSE'
        elif profit_taking_cond: action = 'PROFIT_TARGET'
        elif stop_loss_cond: action = 'STOP_LOSS'
        elif mdd_cond: action = 'MDD'

        trd_side = 'SELL'

        trade_status_df = record_buy_sell(action, last_price, trd_side, equity_value, lot_size, code, is_etf, trade_status_df)

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

        #if now_weekday <= 4 and (120000 > now_hhmmss_int >= 93000 or 155900> now_hhmmss_int >= 130000):
        if True:
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
    main(code, para_dict)