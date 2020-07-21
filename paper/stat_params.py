#!/usr/bin/env python3

import json
import numpy as np
import argparse
import os
import glob
import sys


def load_param_samples(datadir):
    """
    Returns parameters and log-likelihood from the last generation of samples.
    datadir: `str`
        Path to directory containing `_korali_samples`
    """
    samplespath = sorted(
        glob.glob(os.path.join(datadir, '_korali_samples', '*.json')))[-1]

    with open(samplespath) as f:
        js = json.load(f)

    names = [v['Name'] for v in js['Variables']]
    names.append('logLikelihood')

    samples = np.array(js['Results']['Sample Database'])
    loglike = np.array([v['logLikelihood'] for v in js['Samples']])

    dtype = np.dtype({'names': names, 'formats': [np.float] * len(names)})
    comb = np.empty(samples.shape[0], dtype=dtype)
    for i,name in enumerate(names[:-1]):
        comb[name] = samples[:,i]
    comb[names[-1]] = loglike
    return comb

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('datadir',
                        help="Path to directory containing '_korali_samples'.")
    args = parser.parse_args()
    samples = load_param_samples(args.datadir)
    np.savetxt(sys.stdout, samples, fmt='%s', delimiter=" ",
            header=' '.join(map(str, samples.dtype.names)), comments='')

if __name__ == "__main__":
    main()
