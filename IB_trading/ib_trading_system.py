import time
from ib_insync import *
import pandas as pd
import os
from util_ib_trading_system import create_new_trade_status, read_trade_status
from get_stock_basic_info import get_shares_per_lot
from datetime import datetime
from zoneinfo import ZoneInfo


def check_buy_sell_signal(para_dict):
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
            if now_hhmmss_int % 30 == 0:  # for every 30s
                print('Time:', now_hhmmss_int, 'check buy/sell signal for', code)
                print('check_buy_sell_signal(para_dict)')
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