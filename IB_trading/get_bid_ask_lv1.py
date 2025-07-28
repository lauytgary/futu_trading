from ib_insync import *


def get_bid_ask(ib, contract):
    # Request Level 1 market data
    ticker = ib.reqMktData(contract, snapshot=False)
    ib.sleep(1)  # Wait for initial data

    # Extract bid/ask
    bid_ask_info_dict = {'bid_price': ticker.bid,
                         'bid_size': ticker.bidSize,
                         'ask_price': ticker.ask,
                         'ask_size': ticker.askSize,
                         'last_price': ticker.last,
                         'volume': ticker.volume}

    return bid_ask_info_dict


if __name__ == '__main__':
    ib = IB()
    ib.connect('127.0.0.1', 7497, clientId=1)  # Adjust port/clientId as needed

    # Define AAPL stock contract
    contract = Stock('ZM', 'SMART', 'USD')
    #contract = Forex('EURUSD')

    bid_ask_info_dict = get_bid_ask(ib, contract)
    print(bid_ask_info_dict)