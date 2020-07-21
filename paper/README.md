# `countries.json` 

geneated by

`git@gitlab.ethz.ch:mavt-cse/coronavirus.git` `python/data/fetch_all.py`

last row of data is `2020-05-18`

**FIXME: After updating `countries.json` change `LAST_DAY` in `countries.py`**

# `request_country.py`


# Workflow

* Create a working directory

* Add a symlink to `main.py` from `korali-apps:covid19/main.py`

* Add symlinks to scripts needed below, `countries.py`, `countries.json` and `countrydata.py`

* Run `./request_country_paper_release.py` to run the model on European
  countries. This creates subfolders with:
  - `intervals.json`: reference data, fits, mean inferred parameters
  - `_korali_samples/gen*.json`: samples

* Run `./plot_all` to create plots of fits and samples:
  - `growth.pdf`
  - `samples.png`
  
* Run `./stat_params_all` to extract samples:
  - `sample_params.dat`

* Run plotting scripts:
  - `plot_map.py`
  - `plot_scatter.py`
  - `plot_tact.py`
  - `plot_tact_actual.py`
  - `table_tact.py`

# Data sources

* Interventions

  <https://www.acaps.org/covid19-government-measures-dataset>
