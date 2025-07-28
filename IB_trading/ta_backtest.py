import pandas as pd
import pandas_ta_remake as ta

def get_macd(df, single_para_combination_dict, fast=12, slow=26, signal=9):

    # 計算MACD指標
    macd = ta.macd(df['close'], fast=fast, slow=slow, signal=signal)
    df = pd.concat([df, macd], axis=1)

    cross_direction = single_para_combination_dict['cross_direction']
    macd_zone = single_para_combination_dict['macd_zone']

    # 定義MACD列名
    macd_line = f'MACD_{fast}_{slow}_{signal}'  # 快線（MACD線）
    signal_line = f'MACDs_{fast}_{slow}_{signal}'  # 慢線（信號線）

    df['trade_logic'] = False

    # 判斷金叉（快線升穿慢線）
    if cross_direction == 'positive':
        df['trade_logic'] = (df[macd_line] > df[signal_line]) & (df[macd_line].shift(1) <= df[signal_line].shift(1))
    elif cross_direction == 'negative':
        df['trade_logic'] = (df[macd_line] < df[signal_line]) & (df[macd_line].shift(1) >= df[signal_line].shift(1))

    # 判斷牛區（MACD線>0）和熊區（MACD線<0）
    if macd_zone == 'bull':
        df['trade_logic'] =  df['trade_logic'] & df[macd_line] > 0
    elif macd_zone == 'bear':
        df['trade_logic'] = df['trade_logic'] & df[macd_line] < 0

    return df
