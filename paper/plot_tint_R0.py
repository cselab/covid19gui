#!/usr/bin/env python

import matplotlib.pyplot as plt
import json
import os
from glob import glob
import re
import numpy as np
import adjustText
import sys
from scipy import stats

import countries
import countrydata
from countrydata import printerr

# path to folder with output from `request_country.py`
datafolder = "."
df = countrydata.CollectCountryData(datafolder)
df = countrydata.AppendColor(df)
df = countrydata.AppendInferred(df, datafolder)

fig, axes = plt.subplots(1, 2, figsize=(9, 4))

corrout = []

for before, parname, ax in zip([False, True], ['R0int', 'R0'], axes):
    printerr(parname)

    r = df[parname + "_mean"]
    t = [t.days for t in df.tintstart_mean - df.startday]
    slope, intercept, rvalue, pvalue, std_err = stats.linregress(r, t)
    rlin = np.array([r.min(), r.max()])
    corrout.append(parname)
    corrout.append("slope={:}".format(slope))
    corrout.append("correlation={:}".format(rvalue))
    corrout.append("pvalue={:}".format(pvalue))
    ax.plot(rlin, intercept + slope * rlin, ls='--', c='r', alpha=0.5)

    ax.axvline(x=1, color='k', linestyle='-', alpha=0.25, zorder=-10)
    i = 0
    texts = []
    for i, row in enumerate(df.itertuples()):
        t = (row.tintstart_mean - row.startday).days
        xy = [getattr(row, parname + "_mean"), t]
        p = ax.scatter(*xy, s=16, c=row.color)
        texts.append(ax.annotate(countries.ABBREV2[row.folder], xy=xy, fontsize=6))
    printerr("adjusting text locations... ", end="")
    adjustText.adjust_text(texts, lim=10, on_basemap=True, ax=ax)
    printerr("done")
    xlim = [0.2,1.4] if not before else [1, 4]
    ax.set_xlim(*xlim)
    ax.set_ylim(0, 45)
    ax.text(0.2,
            1.03,
            r"$R_0$ before intervention" if before else r"$R_t$ after intervention",
            transform=ax.transAxes,
            fontsize=15)
    ax.set_ylabel('days from first cases to intervention')
fig.tight_layout()
fpath = "scatter_tint_R0.pdf"
print(fpath)
fig.savefig(fpath)

corrpath = "scatter_tint_R0.corr"
print(corrpath)
with open(corrpath, 'w') as f:
    f.write('\n'.join(corrout))
