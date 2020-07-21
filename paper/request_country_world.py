#!/usr/bin/env python

import json
import subprocess as sp
# from european_countries import EUROPEAN_COUNTRIES
presets = "./countries.json"

with open(presets) as f:
    js = json.loads(f.read())

print(len(js))


def filter_few(confirmed, population):
    i = 0
    for i, c in enumerate(confirmed):
        if c > 5 and c > 2e-6 * population:
            break
    return confirmed[i:]


countries = [js_i['country'] for js_i in js]

# countries_to_infer = ['Switzerland','France','Spain','Italy','Netherlands']
# countries_to_infer = EUROPEAN_COUNTRIES
countries_to_infer = ['Switzerland']

# Not avail Czech Republic

js_infer = [js_i for js_i in js if js_i['country'] in countries_to_infer]

for row in js_infer:
    country = row["country"]
    data = row["confirmed"]
    pop = row["population"]

    print('Processing {}'.format(country))
    data = filter_few(data, pop)
    outdir = 'data/' + country.replace(' ', '')
    cmd = ["./main.py"] + \
            ["--dataFolder", outdir] + \
            ["--populationSize", str(pop)] + \
            ["--data"] + list(map(str, data))
    o = sp.run(cmd)
    print(o)
