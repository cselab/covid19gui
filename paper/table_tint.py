#!/usr/bin/env python3

import json
import numpy as np
import argparse
import os
from datetime import datetime
from glob import glob
import re
import pandas as pd

import countrydata
from countries import ABBREV2

# XXX path to folder with output from `request_country.py`
datafolder = "."
df = countrydata.CollectCountryData(datafolder)
df = countrydata.AppendInferred(df, datafolder)
df = countrydata.AppendOfficalLockdown(df)

fpath = "tint.csv"
print(fpath)
with open(fpath, 'w') as f:
    f.write("country,inferred,official,delay\n")
    for i, row in enumerate(df.sort_values(by='fullname').itertuples()):
        inferred = row.tintstart_mean
        official = row.official_lockdown
        if not pd.isnull(official):
            delay = "{:+d}".format((inferred - official).days)
            official = official.strftime('%Y-%m-%d')
        else:
            delay = ""
            official = ""
        inferred = inferred.strftime('%Y-%m-%d') + ' ± {:.1f}'.format(row.tintstart_std)
        country = "{} ({})".format(row.fullname, ABBREV2[row.folder])
        f.write(','.join([country, inferred, official, delay]) + '\n')
