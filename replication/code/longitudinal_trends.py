#!/usr/bin/env python3
"""SI longitudinal panel: trajectory of exclusionary-nationalism LEVELS across ISSP
National Identity waves 1995/2003/2013/2023. The democratic-RIGHTS battery is 2023-only,
so this descriptively tracks the nationalism outcomes common to all waves. Framed
cautiously: cross-wave mean comparison leans on scalar comparability (which this paper
shows is imperfect), so we restrict to identically-worded items and read trajectories,
not precise levels. ISSP item codings are consistent across waves (1=very important..4;
1=agree strongly..5; 1=increased a lot..5=reduced a lot); 8/9/0 are missing.
"""
from pathlib import Path
import os
import re
import numpy as np
import pandas as pd
import pyreadstat

# ISSP_DIR overrides the data location for a portable archive; defaults to the in-repo tree.
ROOT = Path(os.environ.get("ISSP_DIR", Path(__file__).resolve().parents[3] / "ISSP (1995-2023)"))
OUT = Path(__file__).resolve().parents[1] / "outputs"

WAVES = {
    1995: dict(f=ROOT/"ISSP 1995"/"National Identity I - ISSP 1995.dta",
               born="v15", relig="v19", crime="v47", econ="v48", jobs="v49", num="v51",
               country="v3", weight="v342"),
    2003: dict(f=ROOT/"ISSP 2003"/"National Identity II - ISSP 2003.dta",
               born="v11", relig="v15", crime="v50", econ="v51", jobs="v52", num="v55",
               country="COUNTRY", weight="weight"),
    2013: dict(f=ROOT/"ISSP 2013"/"National Identity III - ISSP 2013.dta",
               born="V9", relig="V13", crime="V48", econ="V49", jobs="V50", num="V56",
               country="V4", weight="WEIGHT"),
    2023: dict(f=ROOT/"ISSP 2023"/"National Identity & Citizenship - ISSP 2023.dta",
               born="v1", relig="v3", crime="v26", econ="v27", jobs="v28", num="v31",
               country="country", weight="WEIGHT_COM"),
}

WEST = re.compile(r"austral|austria|canada|denmark|finland|france|german|^d-|great britain|"
                  r"^gb|britain|ireland|italy|netherl|new zealand|norway|portugal|spain|"
                  r"sweden|switzerl|united states|^us\b|usa|belgium|luxembourg|iceland", re.I)

def rng(s, lo, hi):
    s = pd.to_numeric(s, errors="coerce"); return s.where((s >= lo) & (s <= hi))

def imp(s):    return (4 - rng(s, 1, 4)) / 3            # high = important (ascriptive)
def agree(s):  return (5 - rng(s, 1, 5)) / 4            # high = agree
def agreer(s): return (rng(s, 1, 5) - 1) / 4            # high = disagree (reverse: economy good)
def number(s): return (rng(s, 1, 5) - 1) / 4            # high = reduce (anti)

rows = []; csets = {}
for yr, m in WAVES.items():
    cols = [m[k] for k in ("born","relig","crime","econ","jobs","num","country","weight")]
    df, meta = pyreadstat.read_dta(str(m["f"]), usecols=cols, apply_value_formats=False)
    clab = meta.value_labels.get(meta.variable_to_label.get(m["country"], ""), {})
    name = {int(k): str(v) for k, v in clab.items() if str(k).lstrip("-").isdigit()}
    cc = pd.to_numeric(df[m["country"]], errors="coerce")
    g = pd.DataFrame({
        "cname": cc.map(name),
        "born": imp(df[m["born"]]), "relig": imp(df[m["relig"]]),
        "crime": agree(df[m["crime"]]), "econ": agreer(df[m["econ"]]),
        "jobs": agree(df[m["jobs"]]), "num": number(df[m["num"]]),
        "w": pd.to_numeric(df[m["weight"]], errors="coerce").fillna(1).clip(lower=1e-6),
    })
    g["ascriptive"] = g[["born", "relig"]].mean(axis=1)
    g["anti_imm"]   = g[["crime", "econ", "jobs", "num"]].mean(axis=1)
    g["west"] = g["cname"].fillna("").str.contains(WEST)
    csets[yr] = sorted(g.loc[g.cname.notna(), "cname"].unique())
    for grp, sub in [("West", g[g.west]), ("Non-West", g[~g.west])]:
        for var in ["ascriptive", "anti_imm", "born", "crime"]:
            mm = sub[var].notna() & (sub["w"] > 0)
            rows.append(dict(year=yr, group=grp, measure=var,
                             mean=round(float(np.average(sub.loc[mm, var], weights=sub.loc[mm, "w"])), 4) if mm.any() else np.nan,
                             n=int(mm.sum()), n_countries=int(sub.loc[mm, "cname"].nunique())))

res = pd.DataFrame(rows)
res.to_csv(OUT / "longitudinal_trends.csv", index=False)
print("=== weighted means by wave (West vs Non-West) ===")
print(res[res.measure.isin(["ascriptive","anti_imm"])].pivot_table(
      index=["measure","group"], columns="year", values="mean").round(3))
print("\n=== single identically-worded items (robustness) ===")
print(res[res.measure.isin(["born","crime"])].pivot_table(
      index=["measure","group"], columns="year", values="mean").round(3))
print("\nN Western countries per wave:")
for yr in WAVES:
    w = [c for c in csets[yr] if WEST.search(c or "")]
    print(f"  {yr}: {len(w)} West / {len(csets[yr])} total")
