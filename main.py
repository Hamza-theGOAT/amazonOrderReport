import pandas as pd
import numpy as np
import os
import json


def repoClean(dp: dict):
    df = dp['amzOrd_Exp'].copy()
    prod = dp['prod'].copy()

    # Filter DF for Sales Channel and entries with valid amount
    df = df[(df['Sales Channel'] == 'Amazon.com') &
            (df['Product/Service Amount'].notna())]

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


def depen():
    with open('variables.json', 'r') as j:
        data = json.load(j)

    ordRepo = os.path.join(data['src'], data['ordRepo'])
    amzOrd = pd.read_csv(
        ordRepo, delimiter='\t', encoding='utf-16', usecols=data['ordRepoColz'].keys()
    ).rename(columns=data['ordRepoColz'])

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
    # Get dependencies for the script
    dp = depen()
    dp = repoClean(dp)
    toExcel(dp)


if __name__ == '__main__':
    main()
