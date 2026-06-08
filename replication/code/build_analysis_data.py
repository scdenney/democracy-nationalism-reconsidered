#!/usr/bin/env python3
"""Build one analysis-ready individual-level file (shared by Python + R).

Reuses the *verified-correct* scaling in issp2023_democracy_nationalism.py, merges
V-Dem 2023 continuous indices and country-level aggregates, and writes:
  outputs/analysis_individual.csv  (individual level, scaled measures + items + ids + L2 moderators)
  outputs/country_level.csv        (country-level means + V-Dem)
"""
from pathlib import Path
import numpy as np
import pandas as pd

import issp2023_democracy_nationalism as base  # verified scaling + constants

EXPLORE = Path(__file__).resolve().parents[1]   # replication/
OUT = EXPLORE / "outputs"

# Individual items needed for CFA / invariance (membership, superiority, anti-immigrant, pride, dem-rights)
CFA_ITEMS = sorted(set(
    base.ITEM_GROUPS["ascriptive_membership"]
    + base.ITEM_GROUPS["civic_membership"]
    + base.ITEM_GROUPS["national_superiority"]
    + base.ITEM_GROUPS["anti_immigrant_exclusion"]
    + base.ITEM_GROUPS["national_pride_non_democracy"]
    + base.ITEM_GROUPS["protective_sovereignty"]
    + base.ITEM_GROUPS["democracy_rights_liberal"]
    + ["dem_adequate_living"]
))

INDICES = [
    "democracy_rights_liberal", "democracy_rights_all", "democracy_works_today",
    "ascriptive_membership", "civic_membership", "national_superiority",
    "nation_state_self_determination", "protective_sovereignty",
    "anti_immigrant_exclusion", "national_pride_non_democracy", "pride_democracy",
]
CONTROLS = ["age", "female", "education_level", "left_right"]
IDS = ["country_code", "country_name", "c_sample", "region", "region_regime",
       "regime_binary", "vdem_row_2023", "grey_zone", "WEIGHT_COM"]


def main() -> None:
    df = base.read_data()  # verified scaling + classification merge

    # ---- merge V-Dem continuous indices (country level) ----
    vdem = pd.read_csv(OUT / "vdem_2023_issp.csv")
    vdem_cols = ["issp_code", "v2x_polyarchy", "v2x_liberal", "v2x_libdem",
                 "v2x_partipdem", "v2x_regime", "row_2023"]
    df = df.merge(vdem[vdem_cols], left_on="country_code", right_on="issp_code", how="left")

    keep = IDS + ["v2x_polyarchy", "v2x_liberal", "v2x_libdem", "v2x_partipdem",
                  "v2x_regime", "row_2023"] + INDICES + CONTROLS + CFA_ITEMS
    keep = [c for c in dict.fromkeys(keep) if c in df.columns]
    ind = df[keep].copy()

    # ---- country-level aggregates (weighted) as L2 moderators ----
    def wmean(g, col):
        m = g[col].notna() & (g["WEIGHT_COM"] > 0)
        return float(np.average(g.loc[m, col], weights=g.loc[m, "WEIGHT_COM"])) if m.any() else np.nan

    rows = []
    for code, g in df.groupby("country_code"):
        row = {"country_code": code, "country_name": g["country_name"].iloc[0],
               "c_sample_n": g["c_sample"].nunique(), "n": len(g),
               "region": g["region"].iloc[0], "region_regime": g["region_regime"].iloc[0],
               "regime_binary": g["regime_binary"].iloc[0], "row_2023": g["row_2023"].iloc[0],
               "v2x_polyarchy": g["v2x_polyarchy"].iloc[0], "v2x_liberal": g["v2x_liberal"].iloc[0],
               "v2x_libdem": g["v2x_libdem"].iloc[0], "v2x_partipdem": g["v2x_partipdem"].iloc[0]}
        for col in INDICES:
            row[f"cm_{col}"] = wmean(g, col)
        # civic-minus-ethnic balance (higher = more civic relative to ethnic conception)
        row["cm_civic_minus_ethnic"] = row["cm_civic_membership"] - row["cm_ascriptive_membership"]
        rows.append(row)
    country = pd.DataFrame(rows).sort_values("v2x_libdem", ascending=False)
    country.to_csv(OUT / "country_level.csv", index=False)

    # merge selected country aggregates back to individual file as moderators
    cm = country[["country_code", "cm_ascriptive_membership", "cm_civic_membership",
                  "cm_civic_minus_ethnic", "cm_democracy_rights_liberal"]]
    ind = ind.merge(cm, on="country_code", how="left")
    ind.to_csv(OUT / "analysis_individual.csv", index=False)

    print(f"analysis_individual.csv: {ind.shape[0]} rows x {ind.shape[1]} cols")
    print(f"country_level.csv: {country.shape[0]} countries")
    print("CFA items:", len(CFA_ITEMS))
    print("countries w/ V-Dem merged:", ind["v2x_liberal"].notna().sum(), "/", len(ind))


if __name__ == "__main__":
    main()
