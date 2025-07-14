from ib_insync import IB


def get_account_summary():
    # Get account summary
    account = ib.managedAccounts()[0]  # Get first account if multiple exist
    account_summary_list = ib.accountSummary(account)

    summary_dict = {}
    for item in account_summary_list:
        summary_dict[item.tag] = item.value

    return summary_dict


def get_portfolio_positions():
    # Fetch portfolio
    portfolio_list = ib.portfolio()

    position_list = []

    for i in range(len(portfolio_list)):
        position_list.append({'symbol': portfolio_list[i].contract.symbol,
                              'qty': portfolio_list[i].position,
                              'market_price': portfolio_list[i].marketPrice,
                              'avg_cost':portfolio_list[i].averageCost,
                              'unrealized_pnl': portfolio_list[i].unrealizedPNL
                              })

    return position_list


if __name__ == '__main__':
    # Connect to TWS or IB Gateway
    ib = IB()
    ib.connect('127.0.0.1', 7497, clientId=1)  # Paper trading port is 7497, live is 7496

    # print(get_account_summary())
    position_list = get_portfolio_positions()
    print(position_list)

    # Disconnect
    ib.disconnect()