#!/usr/bin/env python

import geopandas as gpd
import pandas as pd
import geoplot
import matplotlib
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np
import json
import os
from glob import glob
import re

import countrydata

# path to folder with output from `request_country.py`
datafolder = "."
df = countrydata.CollectCountryData(datafolder)
df = countrydata.AppendInferred(df, datafolder)

folder_to_geo = {
    'CentralAfricanRepublic': 'CentralAfricanRep.',
    'UnitedStates': 'UnitedStatesofAmerica',
    'DominicanRepublic': 'DominicanRep.',
    'UnitedKingdom': 'United Kingdom',
    'SouthSudan': 'S.Sudan',
    'CzechRepublic': 'Czech Republic',
    'RussianFederation': 'Russia',
    'BosniaandHerzegovina': 'Bosnia and Herzegovina',
    'NorthMacedonia': 'Republic of Macedonia',
    'VaticanCity': 'Vatican City',
    'SanMarino': 'San Marino',
}
df['geoname'] = [folder_to_geo.get(f, f) for f in df['folder']]

# http://naciscdn.org/naturalearth/packages/natural_earth_vector.zip
path = "50m_cultural/ne_50m_admin_0_countries.shp"
if os.path.isfile(path):
    print("Loading highres map '{:}'".format(path))
    world = gpd.read_file(path)
    world['name'] = world['NAME_EN']
else:
    print("Highres map not found in '{:}'".format(path))
    world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))

world = world.to_crs(epsg=3395)

world_folder = world.name.copy()
geo_to_folder = dict(zip(df['geoname'], df['folder']))

world.insert(len(world.columns), 'folder',
             [geo_to_folder.get(geo, geo) for geo in world.name])

shapes = world[world['folder'].isin(df['folder'])]

missing = '\n'.join(f for f in df['folder'] if f not in shapes.folder.values)
if missing:
    print("Warning: Folders missing on the map:")
    print(missing)

shapes = shapes.merge(df[['folder', 'R0_mean', 'R0int_mean']], on='folder')

#print("Countries on the map:")
#print('\n'.join(world.name.values))

#print("Matched folders:")
#print('\n'.join(shapes.folder.values))

fig, [ax, ax2] = plt.subplots(1, 2, figsize=(9, 5.5))
ax.get_xaxis().set_visible(False)
ax.get_yaxis().set_visible(False)
ax2.get_xaxis().set_visible(False)
ax2.get_yaxis().set_visible(False)

switzerland = shapes[shapes.name == "Switzerland"]
bb = switzerland.total_bounds
ext = [5e6, 5e6]
shift = [1.4e6, 2e6]
xlim = [bb[0] - ext[0] + shift[0], bb[2] + ext[0] + shift[0]]
ylim = [bb[1] - ext[1] + shift[1], bb[3] + ext[1] + shift[1]]


class Norm(mcolors.Normalize):
    def __init__(self, vmin=None, vmax=None, vcenter=None, clip=False):
        self.vcenter = vcenter
        mcolors.Normalize.__init__(self, vmin, vmax, clip)

    def __call__(self, value, clip=None):
        x, y = [self.vmin, self.vcenter, self.vmax], [0, 0.5, 1]
        return np.ma.masked_array(np.interp(value, x, y))


norm = Norm(vmin=0.5, vmax=2.5, vcenter=1)
cmap = plt.get_cmap('coolwarm')

ax.set_title(r"$R_t$ after intervention", fontsize=15)
shapes.plot(column='R0int_mean',
            ax=ax,
            edgecolor='black',
            lw=0.1,
            norm=norm,
            cmap=cmap,
            vmin=0,
            vmax=3)

ax.set_xlim(*xlim)
ax.set_ylim(*ylim)

ax2.set_title(r"$R_0$ before intervention", fontsize=15)
shapes.plot(column='R0_mean',
            ax=ax2,
            edgecolor='black',
            lw=0.1,
            norm=norm,
            cmap=cmap,
            vmin=0,
            vmax=3)

ax2.set_xlim(*xlim)
ax2.set_ylim(*ylim)

fig.subplots_adjust(top=1, bottom=0.05, left=0.025, right=0.975, wspace=0.05)
cbar_ax = fig.add_axes([0.025, 0.07, 0.95, 0.05])
sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])
fig.colorbar(sm,
             cax=cbar_ax,
             cmap=cmap,
             norm=norm,
             orientation='horizontal',
             ticks=[0.5, 1, 1.5, 2, 2.5])

fpath = "map_R0.pdf"
print(fpath)
fig.savefig(fpath)
