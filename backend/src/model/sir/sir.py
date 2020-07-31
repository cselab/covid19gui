#!/usr/bin/env python3
# Author: George Arampatzis
# Date:   16/3/2020
# Email:  garampat@ethz.ch

from scipy.integrate import solve_ivp
import os
import sys
import shutil
import glob
import numpy as np
import json


def printerr(m):
    sys.stderr.write(str(m) + '\n')


from ...tools.tools import *

params_fixed = {
    'R0': 1.3,
    'I0': 1,
    'gamma': 1. / 5.2,
    # first intervention
    'tint': 23.,
    'dint': 10,
    'kbeta': 0.5,
    # second intervention
    'tint2_minus_tint': 60.,
    'dint2': 10,
    'kbeta2_div_kbeta': 1,
    # distribution
    '[Sigma]': 300.,
    '[Dispersion]': 1.5,
}

params_prior = {
    'R0': (1., 4.),
    'I0': (0.1, 10.),
    'gamma': (0.09, 0.18),
    # first intervention
    'tint': (0., 80.),
    'dint': (1., 30),
    'kbeta': (0.01, 0.99),
    # second intervention
    'tint2_minus_tint': (30, 90),
    'dint2': (1., 30),
    'kbeta2_div_kbeta': (1., 3.),
    # distribution
    '[Sigma]': (1., 3000.),
    '[Dispersion]': (0., 50.),
}

#params_to_infer = ['R0', 'gamma', 'tint']
#params_to_infer = ['R0', 'gamma', 'tint', 'I0']
#params_to_infer = ['R0', 'tint', 'kbeta', 'I0']
params_to_infer = ['R0', 'tint', 'kbeta']
#params_to_infer = ['R0', 'gamma', 'tint', 'kbeta']
#params_to_infer = ['R0', 'gamma', 'tint', 'dint']
#params_to_infer = ['R0', 'gamma', 'tint', 'kbeta', 'dint']
params_to_infer += ['[Dispersion]']

pretty_dict = {
    # 'I0': r'$I_0$',
    'I0': r'$k_I$',
    'R0': r'$R_0$',
    'r': r'$r$',
    '[Dispersion]': r'$r$',
    'gamma': r'$\\gamma$',
    'tact': r'$t_{\\mathrm{int}}$', # XXX legacy
    'tint': r'$t_{\\mathrm{int}}$',
    'dtact': r'$\\delta_{\\mathrm{int}}$', # XXX legacy
    'dint': r'$\\delta_{\\mathrm{int}}$',
    'kbeta': r'$k_{\\mathrm{int}}$',
    'tint2_minus_tint': r'$t^{(2)}_{\\mathrm{int}}-t_{\\mathrm{int}}$',
    'dint2': r'$\\delta^{(2)}_{\\mathrm{int}}$',
    'kbeta2_div_kbeta': r'$k^{(2)}_{\\mathrm{int}}/k_{\\mathrm{int}}$',
}
params_to_infer_pretty = []
for p in pretty_dict:
    try:
        params_to_infer_pretty.append(pretty_dict[p])
    except KeyError:
        printerr(f"Warning: pretty parameter for '{p}' does not exist.",
              sys.stderr)
        params_to_infer_pretty.append(p)


def set_custom_params(args):
    global params_to_infer
    global params_fixed
    # append before last; needed to keep [Sigma] as last parameter
    def append1(v, a):
        return v[:-1] + [a, v[-1]]
    def infer_if_new(varname):
        global params_to_infer
        if varname not in params_to_infer:
            params_to_infer = append1(params_to_infer, varname)

    if args.reduction is not None:
        params_fixed['kbeta'] = args.reduction
    if args.duration is not None:
        params_fixed['dint'] = args.duration
    if args.infer_reduction:
        infer_if_new('kbeta')
    if args.infer_duration:
        infer_if_new('dint')
    if args.infer_reopening:
        infer_if_new('tint2_minus_tint')
        infer_if_new('kbeta2_div_kbeta')


class Likelihood:
    normal = "Normal"
    nbin = "Negative Binomial"


# Likelihood model
likelihood = Likelihood.nbin
# Fit on daily incidence (1: daily incidence, 0: cumulative)
DAILY = 1
DATA_EPS = 1e-16
#DATA_EPS = 0


def params_list_to_dict(p):
    """
    p: `list(float)`
        Parameter values from Korali
    Returns:
    `dict(str -> float)`
        Mapping from parameter name to value. Includes `params_fixed`.
    """

    r = dict(params_fixed)
    r.update({var: p[i] for i, var in enumerate(params_to_infer)})
    return r


sys.path.append(
    os.path.join(os.path.dirname(__file__), '..', '..', '..', 'build'))
try:
    import libsir
except ModuleNotFoundError:
    printerr('C++ version not found, scipy ODE solver will be used.')
    libsir = None


def getReferenceData(js):
    y = js['Infected']
    t = js['Time'] # starts from 0
    N = js['Population Size']
    I0 = y[1] - y[0]
    S0 = N - y[0]
    R0 = N - S0 - I0
    y0 = S0, I0, R0
    jsOde = {}
    jsOde['Time'] = t[1:] # starts from 1
    # daily: backward difference
    jsOde['Data'] = list(np.maximum(DATA_EPS, np.diff(y))) if DAILY else y[1:]
    jsOde['Initial Condition'] = y0
    jsOde['Population Size'] = js['Population Size']
    return jsOde


def smooth_trans(u0, u1, t, tc, teps):
    """
    Smooth transition from u0 to u1 in interval `tc - teps < t < tc + teps`.
    """
    t0 = tc - teps
    t1 = tc + teps
    return u0 if t <= t0 else u1 if t >= t1 else \
        u0 + (u1 - u0) * (1 - np.cos(np.pi/(t1 - t0)*(t - t0))) * 0.5


def linear_trans(u0, u1, t, tc, teps):
    """
    Linear transition from u0 to u1 in interval `tc - teps < t < tc + teps`.
    """
    t0 = tc - teps
    t1 = tc + teps
    return u0 if t <= t0 else u1 if t >= t1 else \
        u0 + (u1 - u0) * (t - t0) / (t1 - t0)


intervention_trans = linear_trans


def sir_rhs(t, y, N, beta, gamma,
        tint, dint, kbeta, tint2, dint2, kbeta2):
    S, I, R = y
    if I < 0:
        I = 0  # Just in case integration goes too fast.
    beta = beta * intervention_trans(
            1., kbeta, t, tint, dint * 0.5)
    beta = beta * intervention_trans(
            1., kbeta2 / kbeta, t, tint2, dint2 * 0.5)
    c1 = beta * S * I / N
    c2 = gamma * I
    dSdt = -c1
    dIdt = c1 - c2
    dRdt = c2
    return dSdt, dIdt, dRdt


def deviation_model(sigma, t, y):
    return [sigma] * len(y)


def model_for_korali_sample(s, jsOde):
    sdict = params_list_to_dict(s['Parameters'])
    R0 = sdict['R0']
    gamma = sdict['gamma']

    tint = sdict['tint']
    dint = sdict['dint']
    kbeta = sdict['kbeta']

    tint2 = tint + sdict['tint2_minus_tint']
    dint2 = sdict['dint2']
    kbeta2 = sdict['kbeta2_div_kbeta'] * kbeta

    beta = R0 * gamma

    t = jsOde['Time'] # starts from 1
    dt = t[1] - t[0]
    tsolve = [t[0] - dt] + t if DAILY else t

    N = jsOde['Population Size']
    y0 = np.copy(jsOde['Initial Condition'])
    y0[1] *= sdict['I0']

    if libsir:
        # The C++ code computes directly N - S(t).
        y = libsir.sir_infected_so_far(y0[0], y0[1], y0[2], tsolve[-1], N, beta,
                                       gamma,
                                       tint, dint, kbeta,
                                       tint2, dint2, kbeta2)
        y = [N - y0[0]] + y
        assert len(y) == len(tsolve)
    else:
        sol = solve_ivp(sir_rhs,
                        t_span=[tsolve[0], tsolve[-1]],
                        y0=y0,
                        args=(N, beta, gamma,
                            tint, dint, kbeta,
                            tint2, dint2, kbeta2),
                    t_eval=tsolve, max_step=1)
        y = (N - sol.y[0]).tolist()

    if DAILY:
        y = list(np.maximum(DATA_EPS, np.diff(y)))

    s['Reference Evaluations'] = y
    s['Standard Deviation'] = deviation_model(sdict['[Sigma]'], t, y)
    s['Dispersion'] = deviation_model(sdict['[Dispersion]'], t, y)


def model_for_korali_execute(s, jsOde):
    sdict = params_list_to_dict(s['Parameters'])
    R0 = sdict['R0']
    gamma = sdict['gamma']

    tint = sdict['tint']
    dint = sdict['dint']
    kbeta = sdict['kbeta']

    tint2 = tint + sdict['tint2_minus_tint']
    dint2 = sdict['dint2']
    kbeta2 = sdict['kbeta2_div_kbeta'] * kbeta

    beta = R0 * gamma

    t = jsOde['Time'] # this Time comes from propagate.py,
                      # has dt=1, starts from 0
    dt = t[1] - t[0]
    assert np.isclose(dt, 1)
    tsolve = t + [t[-1] + dt] if DAILY else t

    N = jsOde['Population Size']
    y0 = np.copy(jsOde['Initial Condition'])
    y0[1] *= sdict['I0']

    sol = solve_ivp(sir_rhs,
                    t_span=[tsolve[0], tsolve[-1]],
                    y0=y0,
                    args=(N, beta, gamma,
                          tint, dint, kbeta, tint2, dint2, kbeta2),
                    t_eval=tsolve, max_step=1)

    js = {}
    js['Variables'] = []
    js['Number of Variables'] = 5
    js['Length of Variables'] = sol.y.shape[1]

    js['Variables'].append({})
    js['Variables'][0]['Name'] = 'S'
    js['Variables'][0]['Values'] = sol.y[0].tolist()
    js['Variables'][0]['derived'] = []

    js['Variables'].append({})
    js['Variables'][1]['Name'] = 'I'
    js['Variables'][1]['Values'] = np.maximum(sol.y[1], 0).tolist()
    js['Variables'][1]['derived'] = []

    js['Variables'].append({})
    js['Variables'][2]['Name'] = 'R'
    js['Variables'][2]['Values'] = sol.y[2].tolist()
    js['Variables'][2]['derived'] = []

    y = (jsOde['Population Size'] - sol.y[0]).tolist()
    js['Variables'].append({})
    js['Variables'][3]['Name'] = 'Total Infected'
    js['Variables'][3]['Values'] = y
    js['Variables'][3]['derived'] = ["cumsum", "Daily Infected"
                                     ] if DAILY else []

    js['Variables'].append({})
    js['Variables'][4]['Name'] = 'Daily Infected'
    js['Variables'][4]['Values'] = list(np.diff(y))
    js['Variables'][4]['derived'] = ["diff", "Total Infected"
                                     ] if not DAILY else []

    js['Standard Deviation'] = deviation_model(sdict['[Sigma]'], t, y)
    js['Dispersion'] = deviation_model(sdict['[Dispersion]'], t, y)

    # FIXME: store common variables only once
    js['x-axis'] = t

    s['Saved Results'] = js

