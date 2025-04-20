from get_lot_size import get_lot_size

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