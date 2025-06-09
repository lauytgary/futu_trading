import pandas as pd
import time
from futu import *

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1200)

quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

code_list = ['HK.00700', 'HK.00941', 'HK.01810', 'HK.02800', 'HK.00823', 'HK.00405']

ret, data = quote_ctx.get_stock_basicinfo(Market.HK, SecurityType.STOCK, code_list)
print(data)
