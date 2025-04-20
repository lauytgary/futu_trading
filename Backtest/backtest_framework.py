import datetime
import sys

from get_lot_size import update_securities_list
from get_hist_data_yfinance import get_hist_data
from util_backtest import get_sec_profile
import pandas as pd

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)


def backtest(df, lot_size, initial_capital):
    # Initialization 初始化 #
    open_date = datetime.date(1970, 1, 1)
    open_price = 0
    num_of_share = 0
    last_realized_capital = initial_capital
    pnl = 0
    net_profit = 0
    num_of_trade = 0

    for i, row in df.iterrows():
        now_date = i.date()
        now_open = row['open']
        now_high = row['high']
        now_low = row['low']
        now_close = row['close']

        now_candle = round(now_close - now_open, 2)

        # Equity Value #
        unrealized_pnl = num_of_share * (now_close - open_price)
        equity_value = last_realized_capital + unrealized_pnl

        net_profit = round(equity_value - initial_capital, 2)

        # Open position condition 開倉條件 #
        trade_logic = now_candle < -5
        # Profit taking condition 止賺條件 #
        profit_taking_cond = now_close - open_price > 15
        # Stop loss condition 止蝕條件 #
        stop_loss_cond = open_price - now_close > 20
        # Close position on last day 最後一日平倉 #
        last_index_cond = i == df.index[-1]
        # Max holding period 最長持貨期 #
        close_logic = (now_date - open_date).days >= 7
        # Sufficient fund 資金充足 #
        min_cost_cond =  last_realized_capital > now_close * lot_size

        # Open position 開倉 #
        if num_of_share == 0 and trade_logic and min_cost_cond and not last_index_cond:
            num_of_lot = last_realized_capital // (lot_size * now_close)
            num_of_share = num_of_lot * lot_size
            open_date = now_date
            open_price = now_close
            print(now_date, 'open position', open_price)

        # Close position 平倉 #
        elif num_of_share > 0 and (profit_taking_cond or stop_loss_cond or last_index_cond or close_logic):
            num_of_share = 0
            realized_pnl = unrealized_pnl
            last_realized_capital += realized_pnl
            num_of_trade += 1
            print(now_date, 'close position', realized_pnl)
    return net_profit, num_of_trade


if __name__ == '__main__':
    initial_capital = 200000  # hkd
    start_date = '2024-01-01'
    end_date = '2024-12-31'
    data_folder = 'data'
    update_data = False
    code_list = ['0700.HK']
    df_dict = get_hist_data(code_list, start_date, end_date, data_folder, update_data)
    update_securities_list(update_data)

    for code in code_list:
        stock_name, lot_size, market, initial_capital = get_sec_profile(code, initial_capital)
        net_profit, num_of_trade = backtest(df_dict[code], lot_size, initial_capital)
        print('net profit', net_profit)
        print('number of trade', num_of_trade)

