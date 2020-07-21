import sys
sys.path.append('../../')
from epidemics.cantons.data.canton_population import CANTON_LIST, CANTON_LIST_SHORT
import os
from subprocess import call
import argparse
import matplotlib.pyplot as plt
import json
import numpy as np
from data._european_countries import EUROPEAN_COUNTRIES


def create_folder(name):
    if not os.path.exists(name):
        os.makedirs(name)


def get_samples_data(path):

    configFile = path + '/gen00000000.json'

    with open(configFile) as f:
        js = json.load(f)
    configRunId = js['Run ID']

    resultFiles = [
        f for f in os.listdir(path)
        if os.path.isfile(os.path.join(path, f)) and f.startswith('gen')
    ]
    resultFiles = sorted(resultFiles)

    genList = {}

    for file in resultFiles:
        with open(path + '/' + file) as f:
            genJs = json.load(f)
            solverRunId = genJs['Run ID']

        if (configRunId == solverRunId):
            curGen = genJs['Current Generation']
            genList[curGen] = genJs
    del genList[0]

    lastGen = 0
    for i in genList:
        if genList[i]['Current Generation'] > lastGen:
            lastGen = genList[i]['Current Generation']

    return genList[lastGen]


def plot_histogram(ax, ax_i, ax_j, theta, var_idx):
    dim = theta.shape[1]
    num_bins = 30

    ax_loc = ax[ax_i, ax_j]

    hist, bins, _ = ax_loc.hist(theta[:, var_idx],
                                num_bins,
                                density=True,
                                color='lightgreen',
                                ec='black')

    hist = hist / np.max(hist) * (ax_loc.get_xlim()[1] - ax_loc.get_xlim()[0])
    bottom = ax_loc.get_xlim()[0]
    widths = np.diff(bins)
    ax_loc.cla()
    ax_loc.bar(bins[:-1],
               hist,
               widths,
               color='lightgreen',
               ec='black',
               bottom=bottom)
    ax_loc.set_ylim(ax_loc.get_xlim())
    ax_loc.set_yticklabels([])
    ax_loc.tick_params(axis='both', which='both', length=0)

    return np.max(bins), np.min(bins)


def plot_comparison_single_model(data_path, variable, save_dir, regions):

    file_path = '/_korali_samples'

    regions_folders = [
        data_path + region.replace(' ', '') + '/' + file_path
        for region in regions
    ]
    regions = [region.replace(' ', '') for region in regions]
    n_regions = len(regions)

    ref_data = get_samples_data(regions_folders[0])
    variables = [
        ref_data['Variables'][i]['Name']
        for i in range(len(ref_data['Variables']))
    ]
    var_idx = variables.index(variable)

    nrows = 6
    ncols = 5
    fig, ax = plt.subplots(nrows=nrows, ncols=ncols, figsize=(16, 12))

    bin_max = 0
    bin_min = 10

    for i in range(n_regions - 1):
        region = regions[i]
        region = region.replace(' ', '')

        region_path = regions_folders[i]
        print('({}/{}) {}'.format(i + 1, n_regions, region))
        data = get_samples_data(region_path)
        numdim = len(data['Variables'])
        samples = data['Solver']['Sample Database']
        numentries = len(samples)
        samplesTmp = np.reshape(samples, (numentries, numdim))

        # Get subplot index
        ax_i = i // ncols
        ax_j = i % ncols

        bin_max_i, bin_min_i = plot_histogram(ax, ax_i, ax_j, samplesTmp,
                                              var_idx)
        bin_max = np.max([bin_max, bin_max_i])
        bin_min = np.min([bin_min, bin_min_i])
        ax[ax_i, ax_j].set_title(region)

    for i in range(n_regions - 1):
        ax_i = i // ncols
        ax_j = i % ncols
        ax[ax_i, ax_j].set_xlim([bin_min, bin_max])
        ax[ax_i, ax_j].set_yticklabels([])

    plt.savefig(save_dir + '/_comparison/' + variable + '.pdf')


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--data_path',
                        '-p',
                        default='1',
                        help='Which phases to plor.')
    parser.add_argument('--variable', '-v', default='R0', help='Model type')
    parser.add_argument('--save_dir',
                        '-sd',
                        default='data/_figures/',
                        help='Model type')

    args = parser.parse_args()

    regions = EUROPEAN_COUNTRIES
    plot_comparison_single_model(args.data_path, args.variable, args.save_dir,
                                 regions)
