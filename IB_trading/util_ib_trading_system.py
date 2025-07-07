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