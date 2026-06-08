# Figure and table crosswalk

In paper order. Main-text figures and every supplementary exhibit, with the script that generates it and the output it draws on. Supplementary tables are typeset in the manuscript `.tex` from the listed CSV.

## Main text

| # | Type | Short caption | Script | Output |
|---|------|---------------|--------|--------|
| 1 | Figure | Cross-national heterogeneity in the dem-rights → anti-immigrant slope (forest plot) | `code/figures_ggrepel.R` | `figures/fig2_random_slopes.png` |
| 2 | Figure | Slope vs. content of nationhood / vs. institutional liberalism | `code/figures_ggrepel.R` | `figures/fig1_moderation.png` |
| 3 | Figure | Two faces: principles vs. performance, by outcome | `code/figures_v2.py` | `figures/fig3_two_faces.png` |

## Supplementary information

| SI § | Type | Short caption | Script | Output |
|------|------|---------------|--------|--------|
| SI-B | Table | Countries, V-Dem indices, content of nationhood | `code/build_analysis_data.py` | `outputs/country_level.csv` |
| SI-C | Table | Scale reliability by group | `code/issp2023_democracy_nationalism.py` | `outputs/scale_reliability_by_group.csv` |
| SI-D | Table | Multi-group CFA invariance | `code/measurement_invariance.R` | `outputs/invariance_multigroup.csv` |
| SI-D | Table | Alignment ($\bar r$) | `code/measurement_invariance.R` | `outputs/invariance_alignment.csv` |
| SI-E | Table | Multilevel random effects / fixed effects / implied slopes | `code/multilevel_models.R` | `outputs/ml_random_effects.csv`, `ml_fixed_effects.csv`, `ml_implied_slopes.csv` |
| SI-F | Table | Country-level second stage | `code/diagnostic_secondstage.R` | (console; reads `outputs/country_correlations.csv`, `country_level.csv`) |
| SI-G | Table | Performance models | `code/multilevel_models.R` | `outputs/ml_performance_fixed_effects.csv` |
| SI-H | Figure | Regional heatmaps (rights; performance) | `code/issp2023_democracy_nationalism.py` | `figures/regional_democratic_rights_heatmap.png`, `regional_democracy_performance_heatmap.png` |
| SI-I | Figure | Country-specific adjusted slopes | `code/figures_ggrepel.R` | `figures/country_adjusted_democratic_rights_slopes.png` |
| SI-K | Figure | Longitudinal panel 1995–2023 | `code/figures_v2.py` | `figures/figS_longitudinal.png` |
| SI-K | Table | Longitudinal means | `code/longitudinal_trends.py` | `outputs/longitudinal_trends.csv` |
| SI-L | Table | Democratic-socialization cohorts: levels (Taiwan, South Korea) | `code/cohort_test.py` | `outputs/cohort_test.csv` |
| SI-L | Table | Democratic-socialization cohorts: rights–exclusion correlation by cohort | `code/cohort_test.py` | `outputs/cohort_relationship.csv` |

**Notes.** Load-bearing intermediates generated en route: `outputs/vdem_2023_issp.csv` (V-Dem subset, feeds `build_analysis_data.py`) and `outputs/country_adjusted_slopes.csv` (feeds the main-text moderation figures). SI-A and SI-J are narrative sections with no generated exhibit. `outputs/` also holds exploratory files not referenced in the paper.
