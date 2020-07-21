import os
import pandas as pd

# Day of the last row in `countries.json`
LAST_DAY = "2020-05-18"

LONG_NAME = {
    "RussianFederation": "Russia",
    # "UnitedKingdom": "UK",
    "UnitedKingdom": "United Kingdom",
    # "BosniaandHerzegovina": "BiH",
    "BosniaandHerzegovina": "Bosnia and Herzegovina",
    "NorthMacedonia": "North Macedonia",
    "CzechRepublic": "Czechia",
    "SanMarino": "San Marino",
    "VaticanCity": "Vatican City",
}


def manual():
    """Use this if you need more countries. NOT TESTED"""
    # curl -L https://raw.githubusercontent.com/lukes/ISO-3166-Countries-with-Regional-Codes/master/all/all.csv > country-iso-3166-1.csv
    # https://datahub.io/core/country-list
    ISO = pd.read_csv(
        os.path.join(os.path.dirname(__file__), 'country-iso-3166-1.csv'))

    ABBREV2 = {
        ISO['name'][i].replace(' ', ''): ISO['alpha-2'][i]
        for i in range(len(ISO))
    }
    ABBREV2["CzechRepublic"] = ABBREV2["Czechia"]
    ABBREV2[
        "Kosovo"] = "XK"  # That's what wikipedia says. Kosovo has no ISO abbreviation.
    ABBREV2["Moldova"] = "MD"
    ABBREV2["UnitedKingdom"] = "UK"
    ABBREV2["VaticanCity"] = "VA"  # Hole See


# Verified with data from ISO-3166-1.
# https://www.iso.org/obp/ui/#search
ABBREV2 = {
    "Albania": "AL",
    "Andorra": "AD",
    "Armenia": "AM",
    "Austria": "AT",
    "Azerbaijan": "AZ",
    "Belarus": "BY",
    "Belgium": "BE",
    "BosniaandHerzegovina": "BA",
    "Bulgaria": "BG",
    "Croatia": "HR",
    "Cyprus": "CY",
    "CzechRepublic": "CZ",
    "Denmark": "DK",
    "Estonia": "EE",
    "Finland": "FI",
    "France": "FR",
    "Georgia": "GE",
    "Germany": "DE",
    "Greece": "GR",
    "Hungary": "HU",
    "Iceland": "IS",
    "Ireland": "IE",
    "Italy": "IT",
    "Kazakhstan": "KZ",
    "Kosovo": "XK",
    "Latvia": "LV",
    "Liechtenstein": "LI",
    "Lithuania": "LT",
    "Luxembourg": "LU",
    "Malta": "MT",
    "Moldova": "MD",
    "Monaco": "MC",
    "Montenegro": "ME",
    "Netherlands": "NL",
    "NorthMacedonia": "MK",
    "Norway": "NO",
    "Poland": "PL",
    "Portugal": "PT",
    "Romania": "RO",
    "RussianFederation": "RU",
    "SanMarino": "SM",
    "Serbia": "RS",
    "Slovakia": "SK",
    "Slovenia": "SI",
    "Spain": "ES",
    "Sweden": "SE",
    "Switzerland": "CH",
    "Turkey": "TR",
    "Ukraine": "UA",
    # "UnitedKingdom": "GB",
    "UnitedKingdom": "UK",
    "VaticanCity": "VA",
}
