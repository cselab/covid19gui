import pandas as pd
import os
import re
import sys
import json
import numpy as np
from glob import glob

from countries import LAST_DAY


def days_to_delta(t):
    return np.timedelta64(int(t + 0.5), 'D')

def printerr(m ,end='\n'):
    sys.stderr.write(str(m) + end)
    sys.stderr.flush()

folder_to_fullname = {
    "RussianFederation": "Russia",
    "UnitedKingdom": "United Kingdom",
    "BosniaandHerzegovina": "Bosnia and Herzegovina",
    "NorthMacedonia": "North Macedonia",
    "CzechRepublic": "Czech Republic",
    "VaticanCity": "Vatican City",
    "SanMarino": "San Marino",
}


def CollectCountryData(datafolder):
    """
    Collects data for countries in subfolders of `datafolder` containing `intervals.json`.
    Returns: `pandas.DataFrame()`
        columns:
            folder: subfolder name
            startday: day of first data point
            ...
    """
    v_folder = []
    v_startday = []
    v_fullname = []
    v_displayname = []
    for i, path in enumerate(
            sorted(glob(os.path.join(datafolder, "*", "intervals.json")))):
        folder = re.findall(os.path.join(datafolder, "(.*)", "intervals.json"),
                            path)[0]
        v_folder.append(folder)
        with open(path) as f:
            js = json.loads(f.read())
        v_startday.append(
            np.datetime64(LAST_DAY) - days_to_delta(max(js['x-data'])))
        fullname = folder_to_fullname.get(folder, folder)
        v_fullname.append(fullname)
        v_displayname.append(fullname)

    df = pd.DataFrame({
        "folder": v_folder,
        "startday": v_startday,
        "displayname": v_displayname,
        "fullname": v_fullname,
    })
    return df


def AppendColor(df):
    """
    Appends country data by columns:
        color: hex RGB color from matplotlib cycle.
    df: `pandas.DataFrame`
        Output of CollectCountryData()
    """
    import matplotlib.pyplot as plt

    def Color(i):
        prop_cycle = plt.rcParams['axes.prop_cycle']
        colors = prop_cycle.by_key()['color']
        return colors[i % len(colors)]

    df = df.copy()
    df['color'] = [Color(i) for i in range(len(df))]
    return df


def AppendOfficalLockdown(df, path="official_lockdowns.csv"):
    """
    Appends country data by columns:
        official_lockdown: date of official lockdown.
    df: `pandas.DataFrame`
        Output of CollectCountryData()
    path: `str`
        Path to csv generated by `official_lockdowns.py`
    """
    csv = pd.read_csv(path)
    v_date = []
    for c in df['fullname']:
        date = csv['date'].loc[csv['country'] == c]
        if not date.empty:
            v_date.append(pd.to_datetime(date.values.min()))
        else:
            v_date.append(pd.NaT)

    df = df.copy()
    df['official_lockdown'] = v_date
    return df


def GetSampleStat(df, datafolder, expr, plow, phigh):
    """
    Statistics of inferred parameters computed from an evaluated expression.
    df: `pandas.DataFrame`
        Output of CollectCountryData()
    datafolder: `str`
        Folder containing country subfolders with from `sample_params.dat`
        generated by `stat_params.py
    expr: `str`
        Expression to evaluate. Parameter names are substituted.
        (example: "R0 * kbeta")

    Returns: `dict`

    mean: `list`, len(df)
        Mean values.
    median: `list`, len(df)
        Median values.
    std: `list`, len(df)
        Standard deviation.
    low: `list`, len(df)
        Quantile `plow`.
    high: `list`, len(df)
        Quantile `phigh`.
    """
    v_mean = []
    v_median = []
    v_std = []
    v_low = []
    v_high = []
    for folder in df['folder']:
        samples_path = os.path.join(datafolder, folder, 'sample_params.dat')
        assert os.path.isfile(samples_path)
        samples = np.genfromtxt(samples_path, names=True)
        pars = {parname: samples[parname] for parname in samples.dtype.names}
        try:
            values = eval(expr, pars)
        except:
            print("Can't evaluate '{:}'".format(expr))
            return dict()
        v_mean.append(np.mean(values))
        v_median.append(np.median(values))
        v_std.append(np.std(values))
        v_low.append(np.quantile(values, plow))
        v_high.append(np.quantile(values, phigh))
    return {
        'mean': v_mean,
        'median': v_median,
        'std': v_std,
        'low': v_low,
        'high': v_high,
    }


# Modified copy of `epidemics/utils/cache.py`
import inspect
import pickle
import functools


def cache_to_file(target):
    """Factory for a decorator that caches the result of function and stores it to a target file.

    Example:

    @cache_to_file("_cache.pickle")
    def F(a):
        return a
    """

    ext = os.path.splitext(target)[1]
    if ext == '.pickle':

        def load(path):
            with open(path, 'rb') as f:
                print("Loading cache '{}'".format(path))
                return pickle.load(f)

        def save(content, path):
            with open(path, 'wb') as f:
                pickle.dump(content, f)
    else:
        raise ValueError(
            "Unrecognized extension '{}', expected .pickle.".format(ext))

    def decorator(func):
        def inner(*args, **kwargs):
            if os.path.isfile(target):
                return load(target)
            result = func(*args, **kwargs)
            d = os.path.dirname(target)
            if d: os.makedirs(d, exist_ok=True)
            save(result, target)
            return result

        return functools.wraps(func)(inner)

    return decorator


@cache_to_file("_cache_AppendInferred.df.pickle")
def AppendInferred(df, datafolder):
    """
    Appends country data from CollectCountryData() by inferred intervenion time.
    Columns: `[..., tint_mean, tint_std, tint_low, tint_high]`

    Fields representing date (tint, tintstart) are converted to `pandas.datetime`
    except for `*_std` which is kept `float`, number of days.
    """
    df = df.copy()

    p = 0.9  # confidence level
    plow = 0.5 - p / 2
    phigh = 0.5 + p / 2

    def add_startday(k, v):
        if k in ['std']: return v
        return [
            startday + days_to_delta(d)
            for startday, d in zip(df['startday'], v)
        ]

    parname = 'tint'
    stat = GetSampleStat(df, datafolder, parname, plow, phigh)
    for k, v in stat.items():
        df[f"{parname}_{k}"] = add_startday(k, v)

    parname = 'tintstart'
    stat = GetSampleStat(df, datafolder, "tint - dint * 0.5", plow, phigh)
    for k, v in stat.items():
        df[f"{parname}_{k}"] = add_startday(k, v)

    parname = 'dint'
    stat = GetSampleStat(df, datafolder, parname, plow, phigh)
    for k, v in stat.items():
        df[f"{parname}_{k}"] = v

    parname = 'R0'
    stat = GetSampleStat(df, datafolder, parname, plow, phigh)
    for k, v in stat.items():
        df[f"{parname}_{k}"] = v

    parname = 'R0int'
    stat = GetSampleStat(df, datafolder, "R0 * kbeta", plow, phigh)
    for k, v in stat.items():
        df[f"{parname}_{k}"] = stat[k]
    return df
