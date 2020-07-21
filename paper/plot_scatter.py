#!/usr/bin/env python

import matplotlib.pyplot as plt
import json
import os
from glob import glob
import re
import numpy as np

import countries
import countrydata
from countrydata import printerr

# path to folder with output from `request_country.py`
datafolder = "."
df = countrydata.CollectCountryData(datafolder)
df = countrydata.AppendColor(df)
df = countrydata.AppendInferred(df, datafolder)

fig, axes = plt.subplots(1, figsize=(9, 6))
axes = [axes, axes]

dfs = df.sort_values(by='R0int_mean', ascending=False)

xlim = (-0, 4)
for before, parname, ax in zip([False, True], ['R0int', 'R0'], axes):
    ax.axvline(x=1, color='black', linestyle='-', alpha=0.25, zorder=-10)
    i = 0
    ax.get_yaxis().set_visible(False)
    for i, row in enumerate(dfs.itertuples()):
        y = i
        xy = [getattr(row, parname + "_mean"), y]
        p = ax.scatter(*xy, s=16, c=row.color)
        ax.annotate(row.displayname,
                    xy=xy,
                    fontsize=7,
                    xytext=(4, 0),
                    textcoords='offset points',
                    va='center')
        xx = [
            getattr(row, parname + "_low"),
            getattr(row, parname + "_high"),
        ]
        yy = [y, y]
        ax.plot(xx, yy, c="black", lw=3, alpha=0.15, zorder=-10)
    ax.set_xlim(*xlim)
    ax.text(0.03 if not before else 0.55,
            1.01,
            r"$R_0$ before intervention" if before else r"$R_t$ after intervention",
            transform=ax.transAxes,
            fontsize=15)

fig.tight_layout()
fpath = "scatter_R0.pdf"
print(fpath)
fig.savefig(fpath)
