import pandas as pd
import numpy as np
import os
import json
from datetime import datetime as dt
from formatz import formatWB


def repoClean(dp: dict):
    df = dp['amzOrd_Exp'].copy()
    prod = dp['prod'].copy()

    # Filter DF for Sales Channel and entries with valid amount
    df = df[(df['Sales Channel'] == 'Amazon.com') &
            (df['Product/Service Amount'].notna())]

    # Correcting date column values
    df['Sales Receipt Date'] = pd.to_datetime(
        df['Sales Receipt Date']
    ).dt.strftime('%m-%d-%Y')

    # Get Product/Service Name against SKUs
    df = pd.merge(df, prod[['Product/Service Name',
                  'SKU']], on='SKU', how='left')
    df['Product/Service Name'] = df['Product/Service Name'].replace(
        np.nan, '[Error Term]')

    # Calculate Item rate from Item Amount and Quantity
    df['Product/Service Rate'] = df['Product/Service Amount'] / \
        df['Product/Service Quantity']

    # Filter for Orders in Order Report posted in system
    df['Check'] = df['Sales Receipt No'].isin(
        dp['sysRcrds'][dp['data']['sysfltr']]
    )
    df = df[df['Check'] == False]

    # Filter out unnecessary columns from the DF
    df = df[dp['data']['ordWorkColz']]

    # Include the filtered DF in dp dict for later use
    dp['Working_Exp'] = df.copy()

    print(f'Adjusted DataFrame:\n{df}')
    return dp


def toExcel(dp: dict):
    # Create the output workbook path
    wbN = os.path.join(dp['data']['wrk'], dp['data']['wbN'])

    # ExcelWriter loop for saving all dp values with '_Exp' in key
    with pd.ExcelWriter(wbN) as writer:
        for key, value in dp.items():
            if key.endswith('_Exp'):
                sh = key.replace('_Exp', '')
                value.to_excel(writer, sheet_name=sh, index=False)

    print(f'Saved Extracts: {os.path.basename(wbN)}')
    formatWB(wbN, wbN)
    print(f'Formatted Extracts: {os.path.basename(wbN)}')


def depen():
    # Getting JSON variables
    with open('variables.json', 'r') as j:
        data = json.load(j)

    # Reading row Amazon Order Report extracts
    ordRepo = os.path.join(data['src'], data['ordRepo'])
    amzOrd = pd.read_csv(
        ordRepo, delimiter='\t', encoding='utf-16', usecols=data['ordRepoColz'].keys()
    ).rename(columns=data['ordRepoColz'])

    # Getting QBO records for comparison
    sysRcrds = pd.read_excel(
        os.path.join(data['src'], data['sysRcrds']),
        header=3
    ).dropna(subset=data['sysfltr'])
    prod = pd.read_excel(os.path.join(data['src'], data['prod']))

    print(f'Amazon Order Report:\n{amzOrd}')
    return {
        "data": data,
        'amzOrd_Exp': amzOrd,
        'sysRcrds': sysRcrds,
        'prod': prod
    }


def main():
    dp = depen()  # Getting dependencies
    print("="*100)
    dp = repoClean(dp)  # Cleaning and formatting file
    print("="*100)
    toExcel(dp)  # Saving cleaned data to excel
    print("="*100)


if __name__ == '__main__':
    main()
