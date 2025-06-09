import pandas as pd
import datetime

def create_new_trade_status(code, initial_capital, trade_status_file):
    trade_status_dict = {'code': code,
                         'qty': 0,
                         'cost_price': 0.0,
                         'open_datetime': '1999-12-31 00:00:00',
                         'last_realized_capital': float(initial_capital),
                         'temp_max_equity': float(initial_capital),
                         'equity_value': float(initial_capital),
                         'realized_pnl': 0.0,
                         'unrealized_pnl': 0.0,
                         'mdd_out_sample': 0.0,
                         'num_of_trade': 0}

    trade_status_df = pd.DataFrame([trade_status_dict])
    trade_status_df.to_csv(trade_status_file, index=False)


def read_trade_status(trade_status_df):
    qty = trade_status_df.at[0, 'qty']
    cost_price = trade_status_df.at[0, 'cost_price']
    last_realized_capital = trade_status_df.at[0, 'last_realized_capital']
    temp_max_equity = trade_status_df.at[0, 'temp_max_equity']
    open_datetime = trade_status_df.at[0, 'open_datetime']
    num_of_trade = trade_status_df.at[0, 'num_of_trade']

    open_date = datetime.datetime.strptime(open_datetime, '%Y-%m-%d %H:%M:%S').date()

    return qty, cost_price, open_date, last_realized_capital, temp_max_equity, num_of_trade


def cal_commission(share_price, num_of_share, is_etf):
    # commission 佣金
    commission_rate = 0.03 / 100
    min_commission = 3
    platform_fee = 15
    other_fee_rate = 0.0105 / 100  # 交收費, 交易費, 證監
    stamp_duty_rate = 0.01 / 100 if not is_etf else 0

    # commission calculation
    if num_of_share > 0:
        commission = max(round(share_price * num_of_share * commission_rate, 2), min_commission)
        other_fee = round(share_price * num_of_share * (other_fee_rate + stamp_duty_rate), 2)
        commission += (platform_fee + other_fee)
    else:
        commission = 0

    return commission  # one-time commission only