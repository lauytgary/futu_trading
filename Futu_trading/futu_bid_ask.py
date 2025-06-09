import pandas as pd
import time
import queue
from futu import *

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1200)


class OrderBookTest(OrderBookHandlerBase):
    def __init__(self, my_queue):
        self.my_queue = my_queue

    def on_recv_rsp(self, rsp_pb):
        ret_code, data = super(OrderBookTest,self).on_recv_rsp(rsp_pb)
        self.my_queue.put(data)


if __name__ == '__main__':
    my_queue = queue.Queue()
    quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
    handler = OrderBookTest(my_queue)
    quote_ctx.set_handler(handler)  # 设置实时摆盘回调
    ret, data = quote_ctx.subscribe(['HK.HSImain', 'HK.HHImain'], [SubType.ORDER_BOOK])  # 订阅买卖摆盘类型，OpenD 开始持续收到服务器的推送

    while True:
        bid_ask_data_dict = my_queue.get()
        print(bid_ask_data_dict)
        # code = bid_ask_data_dict['code']
        # bid_price = bid_ask_data_dict['Bid'][0][0]
        # ask_price = bid_ask_data_dict['Ask'][0][0]
        # print(code, bid_price, ask_price)
