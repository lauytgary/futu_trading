import pandas as pd
import time
from futu import *

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1200)


def get_futu_hist_kline(start_date, end_date, code):
    quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
    ret, data, page_req_key = quote_ctx.request_history_kline(code, start=start_date, end=end_date, max_count=None, session=Session.ALL)

    data = data[['time_key', 'open', 'high', 'low', 'close', 'volume', 'change_rate']]
    data['time_key'] = pd.to_datetime(data['time_key'], format='%Y-%m-%d %H:%M:%S')
    data = data.rename(columns={'time_key':'datetime', 'change_rate': 'pct_change'})
    data['pct_change'] = data['pct_change'] / 100
    data = data.set_index('datetime', drop=True)

    return data


if __name__ == '__main__':
    start_date = '2025-01-01'
    end_date = '2025-06-02'
    code = 'HK.00941'

    df = get_futu_hist_kline(start_date, end_date, code)
    print(df)

