# Data access

The microdata are **not redistributed** in this package. Both inputs are free but require registration / package install.

## ISSP (primary)

- **ISSP 2023 — National Identity & Citizenship.** GESIS Data Archive, `ZA10010` v1.0.0. https://doi.org/10.4232/5.ZA10010.1.0.0
- Earlier waves (descriptive longitudinal panel only): ISSP 1995 `ZA2880`, 2003 `ZA3910`, 2013 `ZA5950`.

Obtain free after GESIS registration. The expected layout is an `ISSP (1995-2023)/` folder holding one subfolder per wave (`ISSP 2023/National Identity & Citizenship - ISSP 2023.dta`, and likewise for 1995/2003/2013). By default the scripts look for that folder three levels above `code/`, i.e. inside the `national_identity_survey_data` clone (`../../../ISSP (1995-2023)/...` relative to this package). For a portable archive, set the `ISSP_DIR` environment variable to the absolute path of your `ISSP (1995-2023)/` folder — the Python scripts read it. Otherwise place the files at the default location or edit the `ROOT` path at the top of `code/issp2023_democracy_nationalism.py` and `code/longitudinal_trends.py`.

## V-Dem (country-level moderators)

- **V-Dem v15 (2025), 2023 values.** Retrieved through the `vdemdata` R package: `remotes::install_github("vdeminstitute/vdemdata")`. `code/vdem_extract.R` writes the 29-country subset to `outputs/vdem_2023_issp.csv`.
