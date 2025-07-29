import pandas as pd
import os
import json


def depen():
    with open('variables.json', 'r') as j:
        colz = json.load(j)

    return {
        "colz": colz
    }


def main():
    # Get dependencies for the script
    dp = depen()


if __name__ == '__main__':
    main()
