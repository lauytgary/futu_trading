import pandas as pd
from datetime import datetime


def get_tick_size(stock_price):
    if stock_price < 0.01:
        return 0.0001
    elif 0.01 <= stock_price < 0.25:
        return 0.001
    elif 0.25 <= stock_price < 0.50:
        return 0.005
    elif 0.50 <= stock_price < 10.00:
        return 0.01
    elif 10.00 <= stock_price < 20.00:
        return 0.02
    elif 20.00 <= stock_price < 100.00:
        return 0.05
    elif 100.00 <= stock_price < 200.00:
        return 0.10
    elif 200.00 <= stock_price < 500.00:
        return 0.20
    elif 500.00 <= stock_price < 1000.00:
        return 0.50
    elif 1000.00 <= stock_price < 2000.00:
        return 1.00
    elif 2000.00 <= stock_price < 5000.00:
        return 2.00
    elif 5000.00 <= stock_price < 9995.00:
        return 5.00
    else:  # 9995.00 and above
        return 0.00  # No price limit for stocks at or above $9,995


def create_new_trade_status(code, initial_capital, trade_status_file):
    # Create a dictionary with the specified headers and values
    data = {
        'code': code,
        'qty': 0,
        'cost_price': 0.0,
        'open_datetime': '1999-12-31 00:00:00',
        'last_realized_capital': initial_capital,
        'equity_value': initial_capital,
        'realized_pnl': 0.0,
        'unrealized_pnl': 0.0,
        'mdd_out_sample': 0.0,
        'num_of_trade': 0
    }

    # Create a DataFrame from the dictionary
    df = pd.DataFrame([data])

    # Save the DataFrame to a CSV file
    df.to_csv(trade_status_file, index=False)


def read_trade_status(trade_status_df):
    # Convert the DataFrame to a dictionary
    trade_status_dict = trade_status_df.iloc[0].to_dict()

    # Extract the required columns from the first row
    qty = trade_status_df.iloc[0]['qty']
    cost_price = trade_status_df.iloc[0]['cost_price']
    open_datetime_str = trade_status_df.iloc[0]['open_datetime']
    last_realized_capital = trade_status_df.iloc[0]['last_realized_capital']
    temp_max_equity = trade_status_df.iloc[0]['temp_max_equity']
    num_of_trade = trade_status_df.iloc[0]['num_of_trade']

    # Convert the open_datetime string to a datetime object
    open_datetime = datetime.strptime(open_datetime_str, '%Y-%m-%d %H:%M:%S')

    return qty, cost_price, open_datetime, last_realized_capital, temp_max_equity, num_of_trade, trade_status_dict