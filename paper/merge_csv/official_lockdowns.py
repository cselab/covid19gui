#!/usr/bin/env python3

import pandas as pd
'''
For the df file 'real.csv'
1. Copy the link https://en.wikipedia.org/wiki/COVID-19_pandemic_lockdowns
2. to the site   https://wikitable2csv.ggor.de
3. and get Table 1
'''

csv = pd.read_csv('real.csv')

print(len(csv))

df = pd.DataFrame(data={'country': [''] * len(csv), 'date': [''] * len(csv)})

for i in range(len(csv)):
    df['country'][i] = csv['country'][i]
    df['date'][i] = csv['date'][i].split('[')[0]

fpath = "official_lockdowns.csv"

print(fpath)
df.to_csv(fpath)
