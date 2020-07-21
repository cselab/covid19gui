#!/usr/bin/env python3
import os
import numpy as np
import datetime as dt


def load(path):
    dehning = {}
    dehning['effective'] = np.genfromtxt(os.path.join(path, '3a.csv'),
                                         delimiter=',')
    dehning['daily'] = np.genfromtxt(os.path.join(path, '3b.csv'),
                                     delimiter=',')
    dehning['total'] = np.genfromtxt(os.path.join(path, '3c.csv'),
                                     delimiter=',')

    ndays = 8 * 7 + 6 + 1
    x = np.linspace(-1 / 7 * 6, 8, ndays)
    base = dt.date(2020, 3, 2)
    days = np.array([base + dt.timedelta(days=i) for i in range(ndays)])

    class Entry:
        pass

    for k, v in dehning.items():
        yi = np.interp(x, v[:, 0], v[:, 1])
        data = Entry()
        data.days = days
        data.values = yi
        dehning[k] = data

    return dehning
