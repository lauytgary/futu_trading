import datetime
import sys

from get_lot_size import update_securities_list
from get_hist_data_yfinance import get_hist_data
from util_backtest import get_sec_profile, cal_commission, find_bnh_net_profit_mdd, find_equity_mdd, get_all_para_combination
from util_result_metric import initiate_result_dict, record_result
from ta_backtest import get_candle_len
import graphplotyt as gp
import pandas as pd

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)


def backtest(df, lot_size, single_para_combination_dict, initial_capital, market):
    # Initialization 初始化 #
    open_date = datetime.date(1970, 1, 1)
    open_price = 0
    num_of_share = 0
    last_realized_capital = initial_capital
    net_profit = 0
    num_of_trade = 0
    num_of_win = 0

    #### Strategy Specific ####
    profit_target_pct = single_para_combination_dict['profit_target_pct']
    stop_loss_pct = single_para_combination_dict['stop_loss_pct']
    holding_day = single_para_combination_dict['holding_day']

    for i, row in df.iterrows():
        now_date = i.date()
        now_open = row['open']
        now_high = row['high']
        now_low = row['low']
        now_close = row['close']
        trade_logic = row['trade_logic']

        now_candle = round(now_close - now_open, 2)

        commission = cal_commission(now_close, num_of_share, market)

        # Equity Value #
        unrealized_pnl = num_of_share * (now_close - open_price) - commission
        equity_value = last_realized_capital + unrealized_pnl
        df.at[i, 'equity_value'] = equity_value

        net_profit = round(equity_value - initial_capital, 2)

        # Profit taking condition 止賺條件 #
        profit_taking_cond = now_close - open_price > profit_target_pct * open_price / 100
        # Stop loss condition 止蝕條件 #
        stop_loss_cond = open_price - now_close > stop_loss_pct * open_price / 100
        # Close position on last day 最後一日平倉 #
        last_index_cond = i == df.index[-1]
        # Max holding period 最長持貨期 #
        close_logic = (now_date - open_date).days >= holding_day
        # Sufficient fund 資金充足 #
        min_cost_cond =  last_realized_capital > now_close * lot_size

        # Open position 開倉 #
        if num_of_share == 0 and trade_logic and min_cost_cond and not last_index_cond:
            num_of_lot = last_realized_capital // (lot_size * now_close)
            num_of_share = num_of_lot * lot_size
            open_date = now_date
            open_price = now_close
            df.at[i, 'action'] = 'BUY'
            print(now_date, 'open position', open_price)

        # Close position 平倉 #
        elif num_of_share > 0 and (profit_taking_cond or stop_loss_cond or last_index_cond or close_logic):
            num_of_share = 0
            realized_pnl = unrealized_pnl
            last_realized_capital += realized_pnl
            num_of_trade += 1

            if last_index_cond or close_logic:
                df.at[i, 'action'] = 'SELL'
            if profit_taking_cond:
                df.at[i, 'action'] = 'TAKE_PROFIT'
            if stop_loss_cond:
                df.at[i, 'action'] = 'STOP_LOSS'

            if realized_pnl > 0:
                num_of_win += 1
            print(now_date, 'close position', realized_pnl)
        else:
            df.at[i, 'action'] = ''

    # Find win rate
    if num_of_trade > 0:
        win_rate = num_of_win / num_of_trade
    else:
        win_rate = 0

    return df, net_profit, num_of_trade, win_rate


if __name__ == '__main__':
    initial_capital = 200000  # hkd
    start_date = '2020-01-01'
    end_date = '2024-12-31'
    data_folder = 'data'
    update_data = False
    code_list = ['3690.HK']

    df_dict = get_hist_data(code_list, start_date, end_date, data_folder, update_data)
    update_securities_list(update_data)

    #### Strategy Specific ####
    para_dict = {'candle_direction': ['positive', 'negative'],
                 'sd_multiple_list': [1.5, 2, 2.5],
                 'profit_target_pct_list': [4, 8],
                 'stop_loss_pct_list': [10, 15],
                 'holding_day_list': [3, 7, 14]}

    all_para_combination_list = get_all_para_combination(para_dict)

    for code in code_list:
        result_dict = initiate_result_dict(para_dict)
        stock_name, lot_size, market, initial_capital = get_sec_profile(code, initial_capital)
        bnh_net_profit, bnh_mdd, bnh_mdd_pct =  find_bnh_net_profit_mdd(df_dict[code], initial_capital, lot_size)

        for single_para_combination_dict in all_para_combination_list:
            df = get_candle_len(df_dict[code], single_para_combination_dict)
            df, net_profit, num_of_trade, win_rate = backtest(df, lot_size, single_para_combination_dict, initial_capital, market)

            mdd, mdd_pct = find_equity_mdd(df)

            file_name = gp.save_backtest_df(df, code, single_para_combination_dict)
            result_dict = record_result(result_dict, net_profit, mdd, mdd_pct, num_of_trade, win_rate, file_name, single_para_combination_dict)

            print('net profit', net_profit)
            print('number of trade', num_of_trade)

        print(f'---------------------------- Backtest result for {stock_name} ----------------------------')
        print(f'From: {df_dict[code].index[0].date()}', f'To: {df_dict[code].index[-1].date()}')
        print('buy & hold net profit', bnh_net_profit)
        print('buy & hold mdd', f'{bnh_mdd:.2f}')
        print('buy & hold mdd pct', f'{bnh_mdd_pct:.2%}')
        result_df = pd.DataFrame(result_dict)
        result_df = result_df.sort_values(by='net_profit', ascending=False)
        file_name_list = result_df['file_name'].to_list()
        print(result_df)

        gp.graphplot(stock_name, file_name_list)

