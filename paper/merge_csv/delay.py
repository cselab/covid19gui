#!/usr/bin/env python3

import pandas as pd
'''
For the csv file 'delay.csv'
1. Put 'merge.csv' to current directory
2. Run this script.
'''

merged = pd.read_csv('merged.csv')
out = merged.copy()

print(len(merged))

out['delay'] = len(out) * ['']

for i in range(len(out)):
    date = merged['date'][i]
    exact = merged['exactDate'][i]
    if exact and exact != 'nan':
        date = pd.to_datetime(date)
        exact = pd.to_datetime(exact)
        delay = date - exact
        if not pd.isna(delay):
            out['delay'][i] = "{:+d}".format(int(delay.days + 0.5))

out.to_csv('delay.csv')
