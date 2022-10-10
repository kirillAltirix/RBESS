from datetime import datetime
import os

import pandas as pd


BASE_PATH = os.path.dirname(os.path.abspath(__file__))
FILE_1_PATH = os.path.join(BASE_PATH, 'eth-blocktime-7426407-7713931.csv')
FILE_2_PATH = os.path.join(BASE_PATH, 'eth-tx-7426407-7713931.csv')

file_1 = pd.read_csv(FILE_1_PATH, delimiter=';')
for i, row in enumerate(file_1['timestamp']):
    file_1.loc[i, ['timestamp']] = datetime.fromtimestamp(int(row, 0)).strftime('%Y-%m-%d %H:%M:%S')

file_2 = pd.read_csv(FILE_2_PATH, delimiter=';')
file_2['timestamp'] = file_2['block_no'].map(file_1.set_index('block_no')['timestamp'])
file_2.to_csv(FILE_2_PATH, index=False, sep=';')
