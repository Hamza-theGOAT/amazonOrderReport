import pandas as pd
import numpy as np
import os
import json


def repoClean(dp: dict):
    df = dp['amzOrd'].copy()
    prod = dp['prod'].copy()
    df = df[df['Sales Channel'] == 'Amazon.com']
    df = pd.merge(df, prod[['Product/Service Name',
                  'SKU']], on='SKU', how='left')
    df['Product/Service Name'] = df['Product/Service Name'].replace(
        np.nan, '[Error Term]')
    df['Product/Service Rate'] = df['Product/Service Amount'] / \
        df['Product/Service Quantity']

    df = df[dp['colz']['ordWorkColz']]
    print(f'Adjusted DataFrame:\n{df}')


def depen(src):
    with open('variables.json', 'r') as j:
        colz = json.load(j)

    ordRepo = os.path.join(src, 'amazonOrdersReport.txt')
    amzOrd = pd.read_csv(
        ordRepo, delimiter='\t', encoding='utf-16', usecols=colz['ordRepoColz'].keys()
    ).rename(columns=colz['ordRepoColz'])

    prod = pd.read_excel(os.path.join(src, 'productManual.xlsx'))
    print(f'Amazon Order Report:\n{amzOrd}')

    return {
        "colz": colz,
        'amzOrd': amzOrd,
        'prod': prod
    }


def main():
    # Get dependencies for the script
    src = 'source_dir'
    dp = depen(src)
    repoClean(dp)


if __name__ == '__main__':
    main()
