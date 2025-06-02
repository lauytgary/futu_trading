import pandas as pd
import time
from futu import *

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1200)


class StockQuoteTest(StockQuoteHandlerBase):
    def on_recv_rsp(self, rsp_pb):
        ret_code, data = super(StockQuoteTest,self).on_recv_rsp(rsp_pb)
        data_date = data.at[0, 'data_date']
        data_time = data.at[0, 'data_time']
        last_price = data.at[0, 'last_price']

        print(data_date, data_time, last_price)


quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
handler = StockQuoteTest()
quote_ctx.set_handler(handler)  # 设置实时报价回调
ret, data = quote_ctx.subscribe(['HK.HSImain'], [SubType.QUOTE])  # 订阅实时报价类型，OpenD 开始持续收到服务器的推送
