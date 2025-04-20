import os
import pandas as pd
import requests
from io import BytesIO


def update_securities_list(update_data=False):
    if update_data:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
        url = "https://www.hkex.com.hk/eng/services/trading/securities/securitieslists/ListOfSecurities.xlsx"

        response = requests.get(url, headers=headers)
        response.raise_for_status()  # 检查请求是否成功

        excel_data = BytesIO(response.content)
        df = pd.read_excel(excel_data, engine='openpyxl', header=0, skiprows=2)
        df['Stock Code'] = df['Stock Code'].astype(str).str.zfill(5)
        df = df.set_index('Stock Code', drop=True)
        df.to_csv('List_of_Securities.csv')
        print('List of Securities is updated and saved')

        return df


def get_lot_size(code):
    code = str(code).zfill(5)
    # check if file exists
    if os.path.isfile('List_of_Securities.csv'):
        print('List_of_Securities.csv exists, reading from file')
        df = pd.read_csv('List_of_Securities.csv')
        df['Stock Code'] = df['Stock Code'].astype(str).str.zfill(5)
        df = df.set_index('Stock Code', drop=True)
    else:
        print('List_of_Securities.csv not exist, updating from HKEX, pls run again')
        df = update_securities_list(True)

    if code in df.index:  # check if code exist
        lot_size = int(df.at[code, 'Board Lot'].replace(',', ''))
        stock_name = df.at[code, 'Name of Securities']
    else:
        print('Please input correct Stock Code, in the format of eg 00005')
        lot_size = 0
        stock_name = None
    return stock_name, lot_size


if __name__ == '__main__':
    update_securities_list(False)
    stock_name, lot_size = get_lot_size('00005')
    print(stock_name)
    print(lot_size)
