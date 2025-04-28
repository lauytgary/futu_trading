from get_lot_size import get_lot_size
from get_hist_data_yfinance import get_hist_data

def get_sec_profile(code, initial_capital):
    if '.HK' in code:
        market = 'HK'
        code_5digit = code.replace('.HK', '').zfill(5)
        stock_name, lot_size = get_lot_size(code_5digit)
    else:
        market = 'US'
        lot_size = 1
        stock_name = code
        initial_capital = initial_capital / 7.8
    return stock_name, lot_size, market, initial_capital


def cal_commission(share_price, num_of_share, market):
    # commission 佣金
    commission_rate = 0.03 / 100
    min_commission = 3
    platform_fee = 15
    other_fee_rate = 0.1105 / 100
    us_commission_each_stock = 0.0049
    us_min_commission = 0.99
    us_platform_fee_each_stock = 0.05
    us_min_platform_fee = 1
    us_settlement_fee_each_stock = 0.003

    # commission calculation
    if num_of_share > 0:
        if market == 'HK':
            commission = max(round(share_price * num_of_share * commission_rate, 2), min_commission)
            other_fee = round(share_price * num_of_share * other_fee_rate, 2)
            commission += (platform_fee + other_fee)
        elif market == 'US':
            commission = max(round(num_of_share * us_commission_each_stock, 2), us_min_commission)
            platform_fee = max(round(num_of_share * us_platform_fee_each_stock, 2), us_min_platform_fee)
            us_settlement_fee = us_settlement_fee_each_stock * num_of_share
            commission += (platform_fee + us_settlement_fee)
        else:
            commission = 0
    else:
        commission = 0

    return commission * 2


def find_bnh_net_profit_mdd(df, initial_capital, lot_size):
    # 計buy & hold 回報率 & mdd
    bnh_open = df.at[df.index[0], 'open']
    bnh_close = df.at[df.index[-1], 'close']
    num_of_share_bnh = initial_capital // (lot_size * bnh_open) * lot_size
    bnh_net_profit = round((bnh_close - bnh_open) * num_of_share_bnh, 2)

    df['cumulative_max'] = df['close'].cummax()
    bnh_mdd = (df['cumulative_max'] - df['close']).max() * num_of_share_bnh
    bnh_mdd_pct = ((df['cumulative_max'] - df['close']) / df['cumulative_max']).max()

    return bnh_net_profit, bnh_mdd, bnh_mdd_pct


def find_equity_mdd(df):
    # Find mdd of equity curve
    df['equity_cumulative_max'] = df['equity_value'].cummax()
    mdd = round((df['equity_cumulative_max'] - df['equity_value']).max(), 2)
    mdd_pct = round(((df['equity_cumulative_max'] - df['equity_value']) / df['equity_cumulative_max']).max(), 2)

    return mdd, mdd_pct



if __name__ == '__main__':
    initial_capital = 200000  # hkd
    start_date = '2024-01-01'
    end_date = '2024-12-31'
    data_folder = 'data'
    update_data = False
    code_list = ['0700.HK']
    df_dict = get_hist_data(code_list, start_date, end_date, data_folder, update_data)

    bnh_net_profit, bnh_mdd, bnh_mdd_pct = find_bnh_net_profit_mdd(df_dict['0700.HK'], 200000, 100)
    print(bnh_net_profit)
    print(bnh_mdd)
    print(bnh_mdd_pct)


