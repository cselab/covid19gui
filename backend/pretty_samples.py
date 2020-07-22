#!/usr/bin/env python3

import src.model.sir.sir as model
from glob import glob
import os
import argparse

parser = argparse.ArgumentParser(
    description=
    "Creates a copy of '_korali_samples' replacing the  names of variables using 'sir.prertty_dict'"
)
aa = parser.add_argument
aa('samples_dir', default='data', help="Path to '_korali_samples/'")
aa('new_samples_dir',
   default='data',
   help="Path to output (e.g. '_korali_samples_pretty'")
args = parser.parse_args()

os.makedirs(args.new_samples_dir, exist_ok=True)
assert os.path.isdir(args.samples_dir)

for fpath in glob(os.path.join(args.samples_dir, "gen*.json")):
    with open(fpath, 'r') as f:
        text = f.read()
    for varname, pretty in model.pretty_dict.items():
        pattern = '"Name": "{}"'
        text = text.replace(pattern.format(varname), pattern.format(pretty))
    fbase = os.path.basename(fpath)
    foutpath = os.path.join(args.new_samples_dir, fbase)
    print(foutpath)
    with open(foutpath, 'w') as fout:
        fout.write(text)
