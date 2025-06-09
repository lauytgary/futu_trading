import sys

import pandas as pd
import pandas_ta_remake as ta


def get_candle_len(df, single_para_combination_dict):
    candle_direction = single_para_combination_dict['candle_direction']
    sd_multiple = single_para_combination_dict['sd_multiple']
    holding_day = single_para_combination_dict['holding_day']

    df['candle_len'] = df['close'] - df['open']

    if candle_direction == 'positive':
        df['trade_logic'] = (df['candle_len'] > 0) & (df['candle_len'] > df['candle_len'].rolling(holding_day).mean() + sd_multiple * df['candle_len'].rolling(holding_day).std())
    elif candle_direction == 'negative':
        df['trade_logic'] = (df['candle_len'] < 0) & (df['candle_len'] > df['candle_len'].rolling(holding_day).mean() - sd_multiple * df['candle_len'].rolling(holding_day).std())

    df['trade_logic'] = df['trade_logic'].shift(1)

    return df


def get_rsi(df, single_para_combination_dict, rsi_period=14):
    # 計算RSI指標
    df['rsi'] = ta.rsi(df['close'], length=rsi_period)

    rsi_direction = single_para_combination_dict['rsi_direction']
    oversold = single_para_combination_dict['rsi_threshold']
    overbought = 100 - oversold

    # 生成交易條件
    if rsi_direction == 'positive':
        df['trade_logic'] = (df['rsi'] > overbought) & (df['rsi'].shift(1) <= overbought)
    elif rsi_direction == 'negative':
        df['trade_logic'] = (df['rsi'] < oversold) & (df['rsi'].shift(1) >= oversold)

    return df


def get_macd(df, single_para_combination_dict, fast=12, slow=26, signal=9):

    # 計算MACD指標
    macd = ta.macd(df['close'], fast=fast, slow=slow, signal=signal)
    df = pd.concat([df, macd], axis=1)

    cross_direction = single_para_combination_dict['cross_direction']
    macd_zone = single_para_combination_dict['macd_zone']

    # 定義MACD列名
    macd_line = f'MACD_{fast}_{slow}_{signal}'  # 快線（MACD線）
    signal_line = f'MACDs_{fast}_{slow}_{signal}'  # 慢線（信號線）

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
