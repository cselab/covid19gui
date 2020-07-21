#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.append(
    os.path.join(os.path.dirname(__file__), '..', '..', '..', 'build'))
import numpy as np
import matplotlib.pyplot as plt
import copy
import argparse

from epidemics.epidemics import EpidemicsBase
from epidemics.utils.misc import save_file
import libepidemics


class Par:
    R0 = 2.25
    gamma = 1. / 5.2
    tint = 25.
    dint = 25.
    kint = 0.27
    N = int(8e6)
    I0 = 3
    E0 = 0
    alpha = 1 / 2.9
    tmax = 70

def solve_sir(p):
    model = libepidemics.country.sir_int
    dp    = libepidemics.country.DesignParameters(N=p.N)
    cppsolver = model.Solver(dp)

    y0 = [p.N - p.I0, p.I0]

    params = model.Parameters(beta=p.R0 * p.gamma,
                              gamma=p.gamma,
                              tact=p.tint,
                              dtact=p.dint,
                              kbeta=p.kint)
    S0 = p.N - p.I0
    y0cpp = (S0, p.I0, 0.0)
    initial = model.State(y0cpp)
    t_eval = np.arange(p.tmax)
    cpp_res = cppsolver.solve(params, initial, t_eval=t_eval, dt=0.1)
    S = np.zeros(len(cpp_res))
    for i, e in enumerate(cpp_res):
        S[i] = e.S()
    daily = -np.diff(S)
    return daily, copy.deepcopy(p)


def solve_seir(p):
    model = libepidemics.country.seir_int
    dp    = libepidemics.country.DesignParameters(N=p.N)
    cppsolver = model.Solver(dp)

    params = model.Parameters(beta=p.R0 * p.gamma,
                              a=p.alpha,
                              gamma=p.gamma,
                              tact=p.tint,
                              dtact=p.dint,
                              kbeta=p.kint)

    S0 = p.N - p.I0
    y0cpp = (S0, p.E0, p.I0, 0.0)
    initial = model.State(y0cpp)
    t_eval = np.arange(p.tmax)
    cpp_res = cppsolver.solve(params, initial, t_eval=t_eval, dt=0.1)
    S = np.zeros(len(cpp_res))
    for i, e in enumerate(cpp_res):
        S[i] = e.S()
    daily = -np.diff(S)
    return daily, copy.deepcopy(p)

def plot():
    p = Par()
    sir = solve_sir(p)

    def SirToSeir(R0, gamma, alpha):
        return R0 * (1 + (R0 - 1) * gamma / alpha)

    p_seir = copy.deepcopy(p)
    p_seir.R0 = SirToSeir(p.R0, p.gamma, p.alpha)
    p_seir.kint = SirToSeir(p.R0 * p.kint, p.gamma, p.alpha) / SirToSeir(
        p.R0, p.gamma, p.alpha)
    seir = solve_seir(p_seir)

    fig,ax = plt.subplots(figsize=(5,4))
    plt.plot(sir[0], marker='s', markevery=5,
             label=r"SIR, $R_0$={:.3g}, $k_\mathrm{{int}}$={:.3g}".format(
                 sir[1].R0, sir[1].kint))
    plt.plot(seir[0], marker='o', markevery=5,
             label=r"SEIR, $R_0$={:.3g}, $k_\mathrm{{int}}$={:.3g}".format(
                 seir[1].R0, seir[1].kint))
    plt.axvline(x=p.tint-p.dint*0.5, c='k', ls='--')
    plt.axvline(x=p.tint+p.dint*0.5, c='k', ls='--')
    plt.xlabel("time (days)")
    plt.ylabel("daily infected")
    plt.xlim(0, 70)
    plt.ylim(0.1, 1000)
    plt.yscale('log')
    plt.legend()
    plt.tight_layout()
    plt.savefig("sir_vs_seir.pdf")

def test(update=False):
    p = Par()
    sir = solve_sir(p)

    def SirToSeir(R0, gamma, alpha):
        return R0 * (1 + (R0 - 1) * gamma / alpha)

    p_seir = copy.deepcopy(p)
    p_seir.R0 = SirToSeir(p.R0, p.gamma, p.alpha)
    p_seir.kint = SirToSeir(p.R0 * p.kint, p.gamma, p.alpha) / SirToSeir(
        p.R0, p.gamma, p.alpha)
    seir = solve_seir(p_seir)

    pack = np.vstack((sir[0], seir[0])).T
    testref = "testref"
    if update:
        np.savetxt(testref, pack)
    else:
        packref = np.loadtxt(testref)
        diff = np.max(abs(pack - packref))
        assert diff < 1e-10, "Error exceeded: {:}".format(diff)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--test',
                        action='store_true',
                        help="Run test, exit with 0 if success")
    parser.add_argument('--update',
                        action='store_true',
                        help="Update reference data for test")
    args = parser.parse_args()
    if args.test or args.update:
        test(args.update)
    else:
        plot()


if __name__ == "__main__":
    main()
