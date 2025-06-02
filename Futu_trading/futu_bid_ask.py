import pandas as pd
import time
from futu import *

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1200)


class OrderBookTest(OrderBookHandlerBase):
    def on_recv_rsp(self, rsp_pb):
        ret_code, data = super(OrderBookTest,self).on_recv_rsp(rsp_pb)
        print(data)
        # code = data['code']
        # bid_price = data['Bid'][0][0]
        # ask_price = data['Ask'][0][0]
        # print(code, bid_price, ask_price)


quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
handler = OrderBookTest()
quote_ctx.set_handler(handler)  # 设置实时摆盘回调
ret, data = quote_ctx.subscribe(['HK.HSImain', 'HK.HHImain'], [SubType.ORDER_BOOK])  # 订阅买卖摆盘类型，OpenD 开始持续收到服务器的推送

