from data._european_countries import EUROPEAN_COUNTRIES
import os
import sys

import argparse
from subprocess import call


def create_shell_script(shell_filename):

    if os.path.exists(shell_filename):
        os.remove(shell_filename)

    with open(shell_filename, 'a') as file:
        file.write('#!/bin/sh \n')


def plot_posterior(data_path, countries):

    shell_filename = 'plot_posterior.sh'
    create_shell_script(shell_filename)

    for country in countries:
        country = country.replace(' ', '')
        samples_dir = data_path + '/' + str(country) + '/_korali_samples/'
        output_file = data_path + '/' + str(country) + '/figures/posterior.png'

        command = 'python -m korali.plotter --dir ' + str(
            samples_dir) + ' --output ' + str(output_file)
        with open(shell_filename, 'a') as file:
            file.write(command + '\n')

    call(['chmod', '744', shell_filename])
    rx = call('./' + shell_filename)
    os.remove(shell_filename)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--dataFolder',
                        '-df',
                        default='data/',
                        help='Which phases to plor.')

    args = parser.parse_args()

    folders = [folder for folder in os.listdir(args.dataFolder)]

    plot_posterior(args.dataFolder, EUROPEAN_COUNTRIES)

    for country in EUROPEAN_COUNTRIES:
        folder_path = args.dataFolder + country + '/'
        call([
            'cp', folder_path + '/figures/posterior.png',
            args.dataFolder + '/_figures/' + country + '_posterior.pdf'
        ])
