#!/usr/bin/env python3

import scipy.stats

import matplotlib.pyplot as plt

import numpy as np

m = 1000
r = 1.3
p = np.clip(m / (m + r), 0, 1)
ns = 10000000
xn = np.array(np.random.negative_binomial(r, 1 - p, size=ns))
xnt = np.array(np.random.negative_binomial(int(r), 1 - p, size=ns))
xs = np.array(scipy.stats.nbinom.rvs(r, 1 - p, size=ns))
bins = np.linspace(0, m * 4, 20)

plt.hist([xs, xn, xnt],
         bins=bins,
         label=[
             'scipy.stats.nbinom.rvs, r=1.3',
             'numpy.random.negative_binomial, r=1.3',
             'numpy.random.negative_binomial, r=1',
         ])

plt.legend()

plt.savefig('a.pdf')
