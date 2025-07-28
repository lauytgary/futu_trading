from ib_insync import *
import pandas as pd


def get_ib_hist_data(ib, contract, endDateTime, durationStr):
    # Request historical data
    bars = ib.reqHistoricalData(
        contract,
        endDateTime=endDateTime,  # empty string means current time
        durationStr=durationStr,  # 1 year of data
        barSizeSetting='1 day',  # daily bars
        whatToShow='TRADES',  # trade prices
        useRTH=False,  # only regular trading hours
        formatDate=1  # return as pandas DataFrame
    )

    # Convert to pandas DataFrame
    df = util.df(bars)
    df = df.rename(columns={'date':'datetime'})
    df['datetime'] = pd.to_datetime(df['datetime'], format='%Y-%m-%d')
    df = df.set_index('datetime', drop=True)

    return df


if __name__ == '__main__':
    # Connect to TWS or IB Gateway
    ib = IB()
    ib.connect('127.0.0.1', 7497, clientId=1)  # Adjust host/port/clientId as needed

    # Define the AAPL stock contract
    contract = Stock('MSFT', 'SMART', 'USD')

    df = get_ib_hist_data(ib, contract, '', '1 Y')

    # Disconnect
    ib.disconnect()

    # Display the data
    print(df)