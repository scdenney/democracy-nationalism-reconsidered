# Democracy and Nationalism, Reconsidered — replication package

**Author.** Steven Denney

**Paper.** "Democracy and Nationalism, Reconsidered." Manuscript prepared for *The Journal of Politics* (short article).

**Verified.** 2026-06-04

## What this package reproduces

From the ISSP 2023 microdata and V-Dem v15, `master.sh` regenerates every CSV in `outputs/` and every figure in `figures/` — the three main-text figures, the supplementary figures, and the numbers behind every supplementary table (measurement-invariance, multilevel, second-stage, performance, longitudinal, democratic-socialization cohorts, and the country/V-Dem table).

## How to run

From a shell in the package root:

```bash
bash master.sh
```

`master.sh` runs the mixed Python + R pipeline in dependency order and sets its working directory to the package root so the R scripts' relative `outputs/` paths resolve.

## Software requirements

- Python 3 — pandas, numpy, pyreadstat, scipy, matplotlib.
- R 4.5 — lavaan, semTools, sirt, lme4, ggplot2, ggrepel, and `vdemdata` (`remotes::install_github("vdeminstitute/vdemdata")`).
- Approximate runtime: 3–6 minutes.

The pipeline is deterministic except `sirt::invariance.alignment` (step 4), which is seeded (`set.seed(20260604)`).

## Folder structure

```text
replication/
|-- README.md
|-- master.sh            # one-command entry point
|-- LICENSE
|-- .gitignore
|-- code/                # analysis scripts (ordered by master.sh)
|-- data/                # data-access instructions (restricted; not redistributed)
|-- docs/
|   |-- crosswalk.md     # figure/table -> script map, in paper order
|   `-- codebook.md      # analysis-ready variable definitions
|-- outputs/             # generated CSVs
`-- figures/             # generated PNGs
```

## Data sources

See `data/README.md`. Both inputs are obtained free but require registration and are **not redistributed** here: the ISSP 2023 microdata (GESIS ZA10010) and the earlier ISSP National Identity waves, and V-Dem v15 via the `vdemdata` R package.

## Scripts (run order)

1. `code/issp2023_democracy_nationalism.py` — verified item scaling, regional within-country correlations, descriptive heatmaps.
2. `code/vdem_extract.R` — V-Dem v15 liberal/electoral components for the 29 countries.
3. `code/build_analysis_data.py` — assembles `outputs/analysis_individual.csv` and `outputs/country_level.csv`.
4. `code/measurement_invariance.R` — multi-group CFA and alignment.
5. `code/multilevel_models.R` — random-slope models and the cross-level moderation horse race.
6. `code/diagnostic_secondstage.R` — country-level second-stage regressions.
7. `code/longitudinal_trends.py` — 1995–2023 harmonization.
8. `code/cohort_test.py` — democratic-socialization cohort test for Taiwan and South Korea; writes `cohort_test.csv` and `cohort_relationship.csv` (SI-L).
9. `code/figures_v2.py` and `code/figures_ggrepel.R` — publication figures.

## Figure and table crosswalk

See `docs/crosswalk.md`.

## License

See `LICENSE`. Code is released for replication; the ISSP and V-Dem inputs are governed by their providers' terms.

## Attribution

This package follows the structural conventions in Yusaku Horiuchi's [replication-package-guide](https://github.com/yhoriuchi/replication-package-guide) and the FAIR principles (Wilkinson et al. 2016, doi:10.1038/sdata.2016.18).
