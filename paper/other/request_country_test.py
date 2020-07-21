#!/usr/bin/env python

import json
import subprocess as sp
from data._european_countries import EUROPEAN_COUNTRIES

for country in EUROPEAN_COUNTRIES:
    country = country.lower()
    print(country)
    cmd = ["./main.py"] + ["-c", country
                           ] + ["-df", './data/run_test/' + country]
    o = sp.run(cmd)
    print(o)
