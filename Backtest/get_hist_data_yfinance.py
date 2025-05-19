import os
import datetime

import yfinance as yf
import pandas as pd

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)


def get_hist_data(code_list, start_date, end_date, data_folder, update_data):
    df_dict = {}
    if not os.path.isdir(data_folder):
        os.mkdir(data_folder)

    for code in code_list:
        file_extension = '.US_1D.csv' if '.' not in code else '_1D.csv'
        file_path = os.path.join(data_folder, code + file_extension)
        ticker = yf.Ticker(code)

        if os.path.isfile(file_path) and not update_data:
            df = pd.read_csv(file_path)
            df['datetime'] = pd.to_datetime(df['datetime'], format='%Y-%m-%d %H:%M:%S%z')
            df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
            df = df.set_index('datetime')
            print(datetime.datetime.now(), code, 'successfully read data')
        else:
            # period: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
            # interval: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo
            # start, end date: start=yyyy-mm-dd, end=yyyy-mm-dd

            df = ticker.history(start=start_date, end=end_date)
            df = df[['Open', 'High', 'Low', 'Close', 'Volume']]
            df = df[df['Volume'] > 0]
            df = df.rename(columns={'Open':'open', 'High':'high', 'Low':'low', 'Close':'close', 'Volume':'volume'})
            df = df.rename_axis('datetime')
            df['date'] = df.index.date
            df = df[['date', 'open', 'high', 'low', 'close', 'volume']]

            print(datetime.datetime.now(), code, 'successfully get data from source')
            df.to_csv(file_path)

        df['pct_change'] = df['close'].pct_change()
        df_dict[code] = df

    return df_dict


if __name__ == '__main__':
    start_date = '2020-01-01'
    end_date = '2024-12-31'
    data_folder = 'data'
    update_data = False
    code_list = ['0883.HK']
    df_dict = get_hist_data(code_list, start_date, end_date, data_folder, update_data)
    print(df_dict['0883.HK'])
