#!/usr/bin/env python3
import pandas as pd
'''
For the csv file 'real.csv'
1. Copy the link https://en.wikipedia.org/wiki/COVID-19_pandemic_lockdowns
2. to the site   https://wikitable2csv.ggor.de
3. and get Table 1
'''

real = pd.read_csv('real.csv')
inf = pd.read_csv('tact.csv')

print(len(real))
print(len(inf))

inf['exactDate'] = len(inf) * ['']

for i in range(len(inf)):
    country = inf['country'][i]

    x = real.loc[real['country'] == country]
    x.reset_index(drop=True, inplace=True)

    if not x.empty:
        d = x['date'][0].split('[')[0]
        inf['exactDate'][i] = d
        # print(i,country,d)

print(inf)

inf.to_csv('merged.csv')
