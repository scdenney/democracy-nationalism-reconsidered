#!/usr/bin/env python3
"""Cohort/socialization test (SI). Taiwan and South Korea redefined their nations and
democratized in the 1990s and late 1980s; consolidation takes a generation. A blunt
test: do citizens whose formative years (ages 12-25) fell entirely under democratic
institutions hold more civic (less ascriptive) conceptions of nationhood? Expected in
Taiwan (the 1990s break) and weak or absent in South Korea (persistent ethnic nationhood).
The comparison is the within-country cohort gap, and the diagnostic is whether Taiwan's
gap exceeds Korea's. This is observational and confounds cohort with life cycle.
"""
from pathlib import Path
import numpy as np
import pandas as pd

PKG = Path(__file__).resolve().parents[1]
d = pd.read_csv(PKG / "outputs" / "analysis_individual.csv")

SURVEY_YEAR = 2023
TRANSITION = {158: ("Taiwan", 1996), 410: ("South Korea", 1987)}  # TW: first direct presidential; KR: democratization

def wmean(x, w):
    m = x.notna() & w.notna() & (w > 0)
    return float(np.average(x[m], weights=w[m])) if m.any() else np.nan

def wse(x, w):
    m = x.notna() & w.notna() & (w > 0)
    if m.sum() < 3: return np.nan
    xv, wv = x[m].to_numpy(float), w[m].to_numpy(float)
    mu = np.average(xv, weights=wv)
    neff = wv.sum()**2 / (wv**2).sum()
    var = np.average((xv - mu)**2, weights=wv)
    return float(np.sqrt(var / neff))

rows = []
for code, (name, tyear) in TRANSITION.items():
    g = d[d.country_code == code].copy()
    g["birth_year"] = SURVEY_YEAR - g["age"]
    g["civic_minus_ethnic"] = g["civic_membership"] - g["ascriptive_membership"]
    # democratic-socialization cohort: age 12 reached at/after transition -> birth >= tyear-12
    g["dem_cohort"] = (g["birth_year"] >= tyear - 12)
    for lab, sub in [("Democratic-socialized (12-25 post-transition)", g[g.dem_cohort]),
                     ("Earlier cohort", g[~g.dem_cohort])]:
        rows.append(dict(country=name, transition=tyear, cohort=lab, n=int(sub.age.notna().sum()),
                         birth_cutoff=tyear - 12,
                         ascriptive=wmean(sub.ascriptive_membership, sub.WEIGHT_COM),
                         ascriptive_se=wse(sub.ascriptive_membership, sub.WEIGHT_COM),
                         civic_minus_ethnic=wmean(sub.civic_minus_ethnic, sub.WEIGHT_COM),
                         anti_immigrant=wmean(sub.anti_immigrant_exclusion, sub.WEIGHT_COM)))
res = pd.DataFrame(rows)
res.to_csv(PKG / "outputs" / "cohort_test.csv", index=False)

# Does the democratic-rights <-> exclusion RELATIONSHIP shift by cohort? If socialization
# under democracy reorients nationhood toward the civic, the young cohort should show the
# Western (restraining, negative) slope, most clearly in Taiwan.
def wcorr(x, y, w):
    m = x.notna() & y.notna() & w.notna() & (w > 0)
    if m.sum() < 20: return (np.nan, 0)
    xv, yv, wv = x[m].to_numpy(float), y[m].to_numpy(float), w[m].to_numpy(float)
    mx, my = np.average(xv, weights=wv), np.average(yv, weights=wv)
    cov = np.average((xv - mx) * (yv - my), weights=wv)
    vx = np.average((xv - mx)**2, weights=wv); vy = np.average((yv - my)**2, weights=wv)
    return (float(cov / np.sqrt(vx * vy)) if vx > 0 and vy > 0 else np.nan, int(m.sum()))

rel_rows = []
for code, (name, tyear) in TRANSITION.items():
    g = d[d.country_code == code].copy()
    g["birth_year"] = SURVEY_YEAR - g["age"]
    g["dem_cohort"] = g["birth_year"] >= tyear - 12
    for lab, sub in [("Democratic-socialized", g[g.dem_cohort]), ("Earlier cohort", g[~g.dem_cohort])]:
        r_anti, n = wcorr(sub.democracy_rights_liberal, sub.anti_immigrant_exclusion, sub.WEIGHT_COM)
        r_asc, _ = wcorr(sub.democracy_rights_liberal, sub.ascriptive_membership, sub.WEIGHT_COM)
        rel_rows.append(dict(country=name, cohort=lab, n=n, r_dr_anti=r_anti, r_dr_ascriptive=r_asc))
rel = pd.DataFrame(rel_rows)
rel.to_csv(PKG / "outputs" / "cohort_relationship.csv", index=False)
print("\n=== democratic-rights correlation with exclusion, by cohort (negative = Western/restraining) ===")
print(rel.to_string(index=False, float_format=lambda v: f"{v:+.3f}"))

# within-country gap (democratic - earlier); civic orientation = lower ascriptive
print(res[["country","cohort","n","ascriptive","ascriptive_se","civic_minus_ethnic","anti_immigrant"]]
      .to_string(index=False, float_format=lambda v: f"{v:.3f}"))
print()
for name in ["Taiwan", "South Korea"]:
    r = res[res.country == name].set_index("cohort")
    dem = "Democratic-socialized (12-25 post-transition)"; old = "Earlier cohort"
    gap_asc = r.loc[dem, "ascriptive"] - r.loc[old, "ascriptive"]
    gap_cme = r.loc[dem, "civic_minus_ethnic"] - r.loc[old, "civic_minus_ethnic"]
    print(f"{name}: ascriptive gap (dem - earlier) = {gap_asc:+.3f}  | civic-minus-ethnic gap = {gap_cme:+.3f}"
          f"  (negative ascriptive gap / positive civic gap = younger cohort more civic)")
