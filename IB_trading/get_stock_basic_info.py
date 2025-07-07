from ib_insync import *


def get_shares_per_lot(ib, contract):

    # Request contract details
    details = ib.reqContractDetails(contract)  # details is a list

    contract_details = details[0]
    stock_per_lot = contract_details.minSize

    return stock_per_lot


if __name__ == '__main__':
    ib = IB()
    # Connect to IBKR TWS or Gateway
    ib.connect('127.0.0.1', 7497, clientId=1)

    # Create a stock contract object
    contract = Stock('700', 'SEHK', 'HKD')

    shares_per_lot = get_shares_per_lot(ib, contract)
    print(shares_per_lot)
