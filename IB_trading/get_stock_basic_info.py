from ib_insync import *


def get_shares_per_lot(ib, contract):

    # Request contract details
    details = ib.reqContractDetails(contract)  # details is a list
    contract_details = details[0]

    contract_info_dict = {}
    contract_info_dict['symbol'] = contract_details.contract.symbol
    contract_info_dict['longname'] = contract_details.longName
    contract_info_dict['lot_size'] = contract_details.minSize  # for hk stocks only
    contract_info_dict['minTick'] = contract_details.minTick  # for US stocks only

    return contract_info_dict


if __name__ == '__main__':
    ib = IB()
    # Connect to IBKR TWS or Gateway
    ib.connect('127.0.0.1', 7497, clientId=1)

    # Create a stock contract object
    contract = Stock('700', 'SEHK', 'HKD')

    contract_info_dict = get_shares_per_lot(ib, contract)
    print(contract_info_dict)
