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

fpath = "R0.csv"
print(fpath)
with open(fpath, 'w') as f:
    f.write("country,R0,R0_low,R0_high,Rt,Rt_low,Rt_high\n")
    for i, row in enumerate(df.sort_values(by='fullname').itertuples()):
        country = "{} ({})".format(row.fullname, ABBREV2[row.folder])
        f.write(','.join([country] + ["{:.2f}".format(t) for t in [row.R0_mean, row.R0_low, row.R0_high, row.R0int_mean,
                row.R0int_low, row.R0int_high
            ]]) + '\n')
