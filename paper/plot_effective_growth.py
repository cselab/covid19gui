#!/usr/bin/env python3

import json
import numpy as np
import argparse
import os
import glob
from datetime import datetime

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt

from countries import LAST_DAY

ALPHA = 0.3


def linear_trans(u0, u1, t, tc, teps):
    """
    Linear transition from u0 to u1 in interval `tc - teps < t < tc + teps`.
    u0,u1,tc,teps: `float` or `numpy.ndarray`
        Values before and after, transition time, transition duration
    t: `float`
        Current time
    """
    t0 = tc - teps
    t1 = tc + teps
    k0 = np.heaviside(t0 - t, 0)
    k1 = np.heaviside(t - t1, 0)
    kc = 1 - k0 - k1
    uc = u0 + (u1 - u0) * (t - t0) / (t1 - t0)
    return k0 * u0 + k1 * u1 + kc * uc


intervention_trans = linear_trans

import matplotlib.dates as mdates

parser = argparse.ArgumentParser()

parser.add_argument('--dataDir',
                    default="data",
                    help="Path to 'intervals.json' and '_korali_samples'.")
parser.add_argument('--title',
                    type=str,
                    default="",
                    help="Title for the figure")
parser.add_argument('--growth',
                    action="store_true",
                    help="Plot effective growth rate instead of R0")
parser.add_argument('--xrotation',
                    action="store_true",
                    help="Rotate x-label by 45 degrees")
parser.add_argument('--output',
                    default="prediction.pdf",
                    help="Path to output pdf.")
parser.add_argument('--dehning2020_dir',
                    help="Extracted data from Dehning et al. (Germany)")
args = parser.parse_args()

intervalFile = os.path.join(args.dataDir, 'intervals.json')
samplesFile = sorted(
    glob.glob(os.path.join(args.dataDir, '_korali_samples', '*.json')))[-1]

with open(intervalFile) as f:
    d = json.load(f)

with open(samplesFile) as f:
    samples = json.load(f)

dehning = None
if args.dehning2020_dir:
    import load_dehning2020 as dg_germany
    dehning = dg_germany.load(args.dehning2020_dir)

plt.rcParams.update({'font.size': 13})
fig = plt.figure(figsize=(6, 9))
# ax = fig.subplots(3)
ax = fig.subplots(3, sharex=True)
ax1, ax2, ax3 = ax

xdata = np.array(d['x-data']).astype(float)

t = np.array(d['x-axis']).astype(float)
mean_params = d['mean_params']


def days_to_delta(t):
    return (t * 24 * 3600).astype('timedelta64[s]')


day0 = np.datetime64(LAST_DAY) - days_to_delta(max(xdata))
days = day0 + days_to_delta(t)

daysdata = day0 + days_to_delta(xdata)

lambdaeff = np.zeros_like(t)
myFmt = mdates.DateFormatter('%b %d')
ax1.xaxis.set_major_formatter(myFmt)
ax2.xaxis.set_major_formatter(myFmt)
ax3.xaxis.set_major_formatter(myFmt)

varnames = [v['Name'] for v in samples['Variables']]

db = np.array(samples['Results']['Sample Database'])


def get_samples(varname):
    global varnames
    global mean_params
    if varname in varnames:
        return db[:, varnames.index(varname)]
    elif varname in mean_params:
        return np.array([mean_params[varname]] * db.shape[0])
    else:
        return None


R0 = get_samples('R0')
tint = get_samples('tint')
dint = get_samples('dint')
gamma = get_samples('gamma')
kbeta = get_samples('kbeta')
tint2_minus_tint = get_samples('tint2_minus_tint')
kbeta2_div_kbeta = get_samples('kbeta2_div_kbeta')

Nt = len(t)
Ns = R0.shape[0]

lambdaeff = np.zeros((Nt, Ns))
vR0 = np.zeros((Nt, Ns))
for i in range(Nt):
    beta = R0 * gamma
    if kbeta is not None:
        beta *= intervention_trans(1., kbeta, t[i], tint, dint * 0.5)
    if kbeta2_div_kbeta is not None:
        beta *= intervention_trans(1., kbeta2_div_kbeta, t[i],
                                   tint + tint2_minus_tint, dint * 0.5)
    lambdaeff[i, :] = beta - gamma
    vR0[i, :] = beta / gamma

# confidence level
Q_LEVEL = 0.9
Q_LO = 0.5 - Q_LEVEL * 0.5
Q_HI = 0.5 + Q_LEVEL * 0.5

if args.xrotation:
    fig.autofmt_xdate(rotation=45)

if args.growth:
    y = lambdaeff
    mean = np.mean(y, axis=1)
    ax1.plot(days, mean)
    median = np.quantile(y, 0.5, axis=1)
    q1 = np.quantile(y, Q_LO, axis=1)
    q2 = np.quantile(y, Q_HI, axis=1)
    ax1.fill_between(days, q1, q2, alpha=ALPHA)
    ax1.axhline(y=0, color='black', linestyle=':')
    ax1.set_ylabel(r'effective growth rate $\lambda^\ast(t)$')
else:
    y = vR0
    mean = np.mean(y, axis=1)
    ax1.plot(days, mean)
    median = np.quantile(y, 0.5, axis=1)
    q1 = np.quantile(y, Q_LO, axis=1)
    q2 = np.quantile(y, Q_HI, axis=1)
    ax1.fill_between(days, q1, q2, alpha=ALPHA)
    ax1.axhline(y=1, color='black', linestyle=':')
    ax1.set_ylabel(r'reproduction number $R_0$')
ax1.set_xlim(left=days.min())

totaldata = np.array(d['y-data']).astype(float)
dailydata = np.diff(totaldata)

mean = d['Daily Infected']['Mean']
median = d['Daily Infected']['Median']
line, = ax2.plot(days, mean)
for v in d['Daily Infected']['Intervals']:
    perc = v['Percentage']
    if perc < 0.7:
        continue
    low = v['Low Interval']
    high = v['High Interval']
    ax2.fill_between(days, low, high, alpha=ALPHA, color=line.get_color())

ax2.scatter(daysdata[1:], dailydata, c='black', s=4)
ax2.set_ylabel('daily infected')
ax2.set_yscale('log')
ax2.set_xlim(left=days.min())
ax2.set_ylim(bottom=1)

mean = d['Total Infected']['Mean']
median = d['Total Infected']['Median']
line, = ax3.plot(days, mean)
for v in d['Total Infected']['Intervals']:
    perc = v['Percentage']
    if perc < 0.7:
        continue
    low = v['Low Interval']
    high = v['High Interval']
    ax3.fill_between(days, low, high, alpha=ALPHA, color=line.get_color())

ax3.scatter(daysdata, totaldata, c='black', s=4)
ax3.set_ylabel('total infected')
ax3.set_xlim(left=days.min())
ax3.set_ylim(bottom=0)

if args.title:
    ax1.set_title(args.title)

if dehning:
    for a, d in zip(ax, dehning.values()):
        a.plot(d.days, d.values, marker='x', ms=4, linestyle='none', c='g')

fig.tight_layout()

output_dir = os.path.dirname(args.output)
os.makedirs(output_dir, exist_ok=True)
p = args.output
print(p)
fig.savefig(p)
