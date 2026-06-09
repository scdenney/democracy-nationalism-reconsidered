#!/usr/bin/env python3
"""
Exploratory ISSP 2023 analysis: democratic values, democracy performance,
and nationalism across regions and regime settings.

The script keeps the analysis descriptive and reproducible. It separates
nationalism into ISSP-observable dimensions, uses the full ISSP 2023 sample,
and adds a simple regional/regime classification for comparing Western
democracies, newer democracies in Eastern Europe, newer democracies in East
Asia, and non-democratic settings.
"""

from __future__ import annotations

from pathlib import Path
import os
import re

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pyreadstat
from scipy import stats


ROOT = Path(__file__).resolve().parents[3]      # national_identity_survey_data/ (external ISSP data)
# ISSP_DIR overrides the data location for a portable archive; defaults to the in-repo tree.
ISSP_DIR = Path(os.environ.get("ISSP_DIR", ROOT / "ISSP (1995-2023)"))
EXPLORE = Path(__file__).resolve().parents[1]   # replication/ (outputs + figures live here)
OUT = EXPLORE / "outputs"
FIG = EXPLORE / "figures"
DATA = ISSP_DIR / "ISSP 2023" / "National Identity & Citizenship - ISSP 2023.dta"

OUT.mkdir(parents=True, exist_ok=True)
FIG.mkdir(parents=True, exist_ok=True)


# Regime labels use V-Dem Democracy Report 2024, Regimes of the World 2023:
# LD = liberal democracy; ED = electoral democracy; EA = electoral autocracy.
# The simple binary used here codes LD/ED as democracy and EA/CA as non-democracy.
COUNTRY_CLASS = {
    36: {
        "country": "Australia",
        "region": "West",
        "region_regime": "Western democracies",
        "vdem_row_2023": "LD",
    },
    40: {
        "country": "Austria",
        "region": "West",
        "region_regime": "Western democracies",
        "vdem_row_2023": "ED+",
    },
    124: {
        "country": "Canada",
        "region": "West",
        "region_regime": "Western democracies",
        "vdem_row_2023": "LD",
    },
    158: {
        "country": "Taiwan",
        "region": "East Asia",
        "region_regime": "East Asian democracies",
        "vdem_row_2023": "LD",
    },
    191: {
        "country": "Croatia",
        "region": "Eastern Europe",
        "region_regime": "Eastern Europe democracies",
        "vdem_row_2023": "ED",
    },
    208: {
        "country": "Denmark",
        "region": "West",
        "region_regime": "Western democracies",
        "vdem_row_2023": "LD",
    },
    246: {
        "country": "Finland",
        "region": "West",
        "region_regime": "Western democracies",
        "vdem_row_2023": "LD",
    },
    250: {
        "country": "France",
        "region": "West",
        "region_regime": "Western democracies",
        "vdem_row_2023": "LD",
    },
    276: {
        "country": "Germany",
        "region": "West",
        "region_regime": "Western democracies",
        "vdem_row_2023": "LD",
    },
    300: {
        "country": "Greece",
        "region": "West",
        "region_regime": "Western democracies",
        "vdem_row_2023": "ED+",
    },
    348: {
        "country": "Hungary",
        "region": "Eastern Europe",
        "region_regime": "Eastern Europe non-democracies",
        "vdem_row_2023": "EA",
    },
    356: {
        "country": "India",
        "region": "South/Southeast Asia",
        "region_regime": "South/Southeast Asia non-democracies",
        "vdem_row_2023": "EA",
    },
    376: {
        "country": "Israel",
        "region": "Other",
        "region_regime": "Other democracies",
        "vdem_row_2023": "ED+",
    },
    380: {
        "country": "Italy",
        "region": "West",
        "region_regime": "Western democracies",
        "vdem_row_2023": "LD",
    },
    410: {
        "country": "South Korea",
        "region": "East Asia",
        "region_regime": "East Asian democracies",
        "vdem_row_2023": "LD-",
    },
    440: {
        "country": "Lithuania",
        "region": "Eastern Europe",
        "region_regime": "Eastern Europe democracies",
        "vdem_row_2023": "ED+",
    },
    484: {
        "country": "Mexico",
        "region": "Other",
        "region_regime": "Other democracies",
        "vdem_row_2023": "ED-",
    },
    528: {
        "country": "Netherlands",
        "region": "West",
        "region_regime": "Western democracies",
        "vdem_row_2023": "LD",
    },
    554: {
        "country": "New Zealand",
        "region": "West",
        "region_regime": "Western democracies",
        "vdem_row_2023": "LD",
    },
    578: {
        "country": "Norway",
        "region": "West",
        "region_regime": "Western democracies",
        "vdem_row_2023": "LD",
    },
    608: {
        "country": "Philippines",
        "region": "South/Southeast Asia",
        "region_regime": "South/Southeast Asia non-democracies",
        "vdem_row_2023": "EA",
    },
    643: {
        "country": "Russia",
        "region": "Eastern Europe",
        "region_regime": "Eastern Europe non-democracies",
        "vdem_row_2023": "EA",
    },
    703: {
        "country": "Slovakia",
        "region": "Eastern Europe",
        "region_regime": "Eastern Europe democracies",
        "vdem_row_2023": "ED",
    },
    705: {
        "country": "Slovenia",
        "region": "Eastern Europe",
        "region_regime": "Eastern Europe democracies",
        "vdem_row_2023": "ED+",
    },
    710: {
        "country": "South Africa",
        "region": "Other",
        "region_regime": "Other democracies",
        "vdem_row_2023": "ED",
    },
    752: {
        "country": "Sweden",
        "region": "West",
        "region_regime": "Western democracies",
        "vdem_row_2023": "LD",
    },
    756: {
        "country": "Switzerland",
        "region": "West",
        "region_regime": "Western democracies",
        "vdem_row_2023": "LD",
    },
    764: {
        "country": "Thailand",
        "region": "South/Southeast Asia",
        "region_regime": "South/Southeast Asia non-democracies",
        "vdem_row_2023": "EA",
    },
    840: {
        "country": "United States",
        "region": "West",
        "region_regime": "Western democracies",
        "vdem_row_2023": "LD",
    },
}

CORE_WEST = {
    code: meta["country"]
    for code, meta in COUNTRY_CLASS.items()
    if meta["region_regime"] == "Western democracies"
}

GROUPS = [
    ("all_issp", "All ISSP countries", lambda d: pd.Series(True, index=d.index)),
    ("democracies", "All democracies", lambda d: d["regime_binary"] == "Democracy"),
    ("non_democracies", "All non-democracies", lambda d: d["regime_binary"] == "Non-democracy"),
    ("western_democracies", "Western democracies", lambda d: d["region_regime"] == "Western democracies"),
    (
        "east_europe_democracies",
        "Eastern Europe democracies",
        lambda d: d["region_regime"] == "Eastern Europe democracies",
    ),
    (
        "east_europe_non_democracies",
        "Eastern Europe non-democracies",
        lambda d: d["region_regime"] == "Eastern Europe non-democracies",
    ),
    (
        "east_asia_democracies",
        "East Asian democracies",
        lambda d: d["region_regime"] == "East Asian democracies",
    ),
    (
        "south_se_asia_non_democracies",
        "South/Southeast Asia non-democracies",
        lambda d: d["region_regime"] == "South/Southeast Asia non-democracies",
    ),
    ("other_democracies", "Other democracies", lambda d: d["region_regime"] == "Other democracies"),
]

GROUP_ORDER = [g[1] for g in GROUPS]
REGION_REGIME_ORDER = [
    "Western democracies",
    "Eastern Europe democracies",
    "Eastern Europe non-democracies",
    "East Asian democracies",
    "South/Southeast Asia non-democracies",
    "Other democracies",
]

SELECTED_OUTCOMES = [
    "ascriptive_membership",
    "national_superiority",
    "anti_immigrant_exclusion",
    "national_pride_non_democracy",
]

PERFORMANCE_OUTCOMES = [
    "civic_membership",
    "national_superiority",
    "protective_sovereignty",
    "anti_immigrant_exclusion",
    "national_pride_non_democracy",
    "pride_democracy",
]

MEASURE_LABELS = {
    "democracy_rights_all": "Democratic rights, all four ISSP items",
    "democracy_rights_liberal": "Democratic rights: minority, participation, civil disobedience",
    "democracy_works_today": "Perceived performance of democracy today",
    "ascriptive_membership": "Closed/ascriptive national membership",
    "civic_membership": "Civic national membership",
    "national_superiority": "National superiority and unconditional support",
    "nation_state_self_determination": "Every nation should have its own state",
    "protective_sovereignty": "Protectionist/sovereigntist nationalism",
    "anti_immigrant_exclusion": "Anti-immigrant exclusion",
    "national_pride_non_democracy": "National pride, excluding pride in democracy",
    "pride_democracy": "Pride in the way democracy works",
}

SHORT_LABELS = {
    "ascriptive_membership": "Ascriptive\nmembership",
    "civic_membership": "Civic\nmembership",
    "national_superiority": "National\nsuperiority",
    "nation_state_self_determination": "Every nation,\nown state",
    "protective_sovereignty": "Protective\nsovereignty",
    "anti_immigrant_exclusion": "Anti-immigrant\nexclusion",
    "national_pride_non_democracy": "National\npride",
    "pride_democracy": "Pride in\ndemocracy",
}

ITEM_GROUPS = {
    "democracy_rights_all": [
        "dem_adequate_living",
        "dem_minority_rights",
        "dem_more_participation",
        "dem_civil_disobedience",
    ],
    "democracy_rights_liberal": [
        "dem_minority_rights",
        "dem_more_participation",
        "dem_civil_disobedience",
    ],
    "ascriptive_membership": [
        "born_important",
        "religion_important",
        "ancestry_important",
        "born_not_effort",
    ],
    "civic_membership": [
        "citizenship_important",
        "respect_institutions_important",
        "feel_national_important",
    ],
    "national_superiority": [
        "world_better_if_like_us",
        "country_better_than_most",
        "support_country_wrong",
    ],
    "protective_sovereignty": [
        "limit_imports",
        "oppose_international_enforcement",
        "own_interests_even_conflict",
        "no_foreign_land",
        "national_tv_preference",
        "intl_companies_damage",
    ],
    "anti_immigrant_exclusion": [
        "immigrants_increase_crime",
        "immigrants_bad_economy",
        "immigrants_take_jobs",
        "immigrants_not_improve_society",
        "native_born_preference",
        "reduce_immigration",
    ],
    "national_pride_non_democracy": [
        "proud_political_influence",
        "proud_economy",
        "proud_sports",
        "proud_arts",
        "proud_history",
    ],
}

OUTCOMES = [
    "ascriptive_membership",
    "civic_membership",
    "national_superiority",
    "nation_state_self_determination",
    "protective_sovereignty",
    "anti_immigrant_exclusion",
    "national_pride_non_democracy",
    "pride_democracy",
]


def regime_binary(vdem_code: str) -> str:
    return "Democracy" if vdem_code.startswith(("LD", "ED")) else "Non-democracy"


def clean_range(series: pd.Series, low: int | float, high: int | float) -> pd.Series:
    s = pd.to_numeric(series, errors="coerce")
    return s.where((s >= low) & (s <= high))


def scale_important_1_4(series: pd.Series) -> pd.Series:
    return (4 - clean_range(series, 1, 4)) / 3


def scale_agree_high(series: pd.Series) -> pd.Series:
    return (5 - clean_range(series, 1, 5)) / 4


def scale_disagree_high(series: pd.Series) -> pd.Series:
    return (clean_range(series, 1, 5) - 1) / 4


def scale_pride_1_4(series: pd.Series) -> pd.Series:
    return (4 - clean_range(series, 1, 4)) / 3


def scale_1_7(series: pd.Series) -> pd.Series:
    return (clean_range(series, 1, 7) - 1) / 6


def scale_0_10(series: pd.Series) -> pd.Series:
    return clean_range(series, 0, 10) / 10


def weighted_mean(x: pd.Series, w: pd.Series) -> float:
    mask = x.notna() & w.notna() & (w > 0)
    if not mask.any():
        return np.nan
    return float(np.average(x[mask], weights=w[mask]))


def effective_n(w: np.ndarray) -> float:
    total = np.sum(w)
    sq = np.sum(w**2)
    if total <= 0 or sq <= 0:
        return np.nan
    return float(total**2 / sq)


def weighted_corr_stats(x: pd.Series, y: pd.Series, w: pd.Series) -> dict[str, float]:
    mask = x.notna() & y.notna() & w.notna() & (w > 0)
    n = int(mask.sum())
    if n < 5:
        return {"r": np.nan, "p": np.nan, "n": n, "n_eff": np.nan}
    xv = x[mask].to_numpy(dtype=float)
    yv = y[mask].to_numpy(dtype=float)
    wv = w[mask].to_numpy(dtype=float)
    mx = np.average(xv, weights=wv)
    my = np.average(yv, weights=wv)
    cov = np.average((xv - mx) * (yv - my), weights=wv)
    vx = np.average((xv - mx) ** 2, weights=wv)
    vy = np.average((yv - my) ** 2, weights=wv)
    if vx <= 0 or vy <= 0:
        return {"r": np.nan, "p": np.nan, "n": n, "n_eff": np.nan}
    r = float(cov / np.sqrt(vx * vy))
    n_eff = effective_n(wv)
    if not np.isfinite(n_eff) or n_eff <= 3 or abs(r) >= 1:
        p = np.nan
    else:
        tval = r * np.sqrt((n_eff - 2) / max(1e-12, 1 - r**2))
        p = float(2 * stats.t.sf(abs(tval), df=n_eff - 2))
    return {"r": r, "p": p, "n": n, "n_eff": n_eff}


def weighted_corr(x: pd.Series, y: pd.Series, w: pd.Series) -> float:
    return weighted_corr_stats(x, y, w)["r"]


def country_equal_weights(df: pd.DataFrame, weight: str = "WEIGHT_COM") -> pd.Series:
    w = pd.to_numeric(df[weight], errors="coerce").where(lambda s: s > 0, 1.0)
    denom = w.groupby(df["country_name"]).transform("sum")
    return w / denom


def weighted_within_corr_stats(df: pd.DataFrame, x: str, y: str, w: str) -> dict[str, float]:
    cols = [x, y, w, "country_name"]
    d = df[cols].dropna().copy()
    d = d[d[w] > 0]
    if d.empty:
        return {"r": np.nan, "p": np.nan, "n": 0, "n_eff": np.nan}
    for col in [x, y]:
        means = d.groupby("country_name").apply(lambda g: weighted_mean(g[col], g[w]))
        d[f"{col}_demeaned"] = d[col] - d["country_name"].map(means)
    return weighted_corr_stats(d[f"{x}_demeaned"], d[f"{y}_demeaned"], d[w])


def weighted_within_corr(df: pd.DataFrame, x: str, y: str, w: str) -> float:
    return weighted_within_corr_stats(df, x, y, w)["r"]


def wls_beta(df: pd.DataFrame, y: str, x: str, controls: list[str], weight: str) -> tuple[float, int]:
    cols = [y, x, weight, "country_name", *controls]
    d = df[cols].dropna().copy()
    d = d[d[weight] > 0]
    if len(d) < 100:
        return np.nan, len(d)

    country_dummies = pd.get_dummies(d["country_name"], prefix="country", drop_first=True, dtype=float)
    xmat = pd.concat(
        [
            pd.Series(1.0, index=d.index, name="const"),
            d[[x, *controls]].astype(float),
            country_dummies,
        ],
        axis=1,
    )
    yvec = d[y].astype(float).to_numpy()
    wvec = d[weight].astype(float).to_numpy()
    sqrtw = np.sqrt(wvec)
    xw = xmat.to_numpy(dtype=float) * sqrtw[:, None]
    yw = yvec * sqrtw
    beta = np.linalg.pinv(xw.T @ xw) @ (xw.T @ yw)
    return float(beta[1]), len(d)


def cronbach_alpha(df: pd.DataFrame, items: list[str]) -> float:
    d = df[items].dropna()
    if len(d) < 50 or len(items) < 2:
        return np.nan
    cov = d.cov().to_numpy(dtype=float)
    k = len(items)
    total_var = cov.sum()
    if total_var <= 0:
        return np.nan
    return float(k / (k - 1) * (1 - np.trace(cov) / total_var))


def sig_stars(p: float) -> str:
    if not np.isfinite(p):
        return ""
    if p < 0.001:
        return "***"
    if p < 0.01:
        return "**"
    if p < 0.05:
        return "*"
    return ""


def fmt_r(r: float, p: float | None = None) -> str:
    if not np.isfinite(r):
        return ""
    stars = sig_stars(p) if p is not None else ""
    return f"{r:.2f}{stars}"


def parse_country_label(label: str) -> str:
    if not isinstance(label, str):
        return str(label)
    label = re.sub(r"^\d+\.\s*[A-Z]{2}-", "", label)
    return label.replace("Korea (South)", "South Korea")


def add_scaled_measures(df: pd.DataFrame) -> pd.DataFrame:
    # Membership criteria.
    df["born_important"] = scale_important_1_4(df["v1"])
    df["citizenship_important"] = scale_important_1_4(df["v2"])
    df["religion_important"] = scale_important_1_4(df["v3"])
    df["respect_institutions_important"] = scale_important_1_4(df["v4"])
    df["feel_national_important"] = scale_important_1_4(df["v5"])
    df["ancestry_important"] = scale_important_1_4(df["v6"])
    df["born_not_effort"] = (clean_range(df["v13"], 1, 4) - 1) / 3

    # National superiority, support, and nation-state ideas.
    df["prefer_citizenship"] = scale_agree_high(df["v7"])
    df["not_ashamed"] = scale_disagree_high(df["v8"])
    df["world_better_if_like_us"] = scale_agree_high(df["v9"])
    df["country_better_than_most"] = scale_agree_high(df["v10"])
    df["support_country_wrong"] = scale_agree_high(df["v11"])
    df["nation_state_self_determination"] = scale_agree_high(df["v12"])

    # Pride items.
    df["pride_democracy"] = scale_pride_1_4(df["v14"])
    df["proud_political_influence"] = scale_pride_1_4(df["v15"])
    df["proud_economy"] = scale_pride_1_4(df["v16"])
    df["proud_sports"] = scale_pride_1_4(df["v17"])
    df["proud_arts"] = scale_pride_1_4(df["v18"])
    df["proud_history"] = scale_pride_1_4(df["v19"])

    # Sovereignty, protectionism, and anti-immigrant exclusion.
    df["limit_imports"] = scale_agree_high(df["v20"])
    df["oppose_international_enforcement"] = scale_disagree_high(df["v21"])
    df["own_interests_even_conflict"] = scale_agree_high(df["v22"])
    df["no_foreign_land"] = scale_agree_high(df["v23"])
    df["national_tv_preference"] = scale_agree_high(df["v24"])
    df["intl_companies_damage"] = scale_agree_high(df["v25"])
    df["immigrants_increase_crime"] = scale_agree_high(df["v26"])
    df["immigrants_bad_economy"] = scale_disagree_high(df["v27"])
    df["immigrants_take_jobs"] = scale_agree_high(df["v28"])
    df["immigrants_not_improve_society"] = scale_disagree_high(df["v29"])
    df["native_born_preference"] = scale_agree_high(df["v30"])
    df["reduce_immigration"] = (clean_range(df["v31"], 1, 5) - 1) / 4

    # Democracy items.
    df["good_citizen_watch_government"] = scale_1_7(df["v35"])
    df["democracy_works_today"] = scale_0_10(df["v38"])
    df["dem_adequate_living"] = scale_1_7(df["v41"])
    df["dem_minority_rights"] = scale_1_7(df["v42"])
    df["dem_more_participation"] = scale_1_7(df["v43"])
    df["dem_civil_disobedience"] = scale_1_7(df["v44"])

    for index, items in ITEM_GROUPS.items():
        df[index] = df[items].mean(axis=1, skipna=True)

    df["female"] = clean_range(df["SEX"], 1, 2).map({1: 0.0, 2: 1.0})
    df["age"] = clean_range(df["AGE"], 15, 120)
    df["education_level"] = clean_range(df["EDULEVEL"], 0, 8)
    df["left_right"] = clean_range(df["v46"], 0, 10) / 10
    return df


def country_classification_table() -> pd.DataFrame:
    rows = []
    for code, meta in COUNTRY_CLASS.items():
        rows.append(
            {
                "country_code": code,
                "country": meta["country"],
                "region": meta["region"],
                "region_regime": meta["region_regime"],
                "vdem_row_2023": meta["vdem_row_2023"],
                "regime_binary": regime_binary(meta["vdem_row_2023"]),
                "grey_zone": "+" in meta["vdem_row_2023"] or "-" in meta["vdem_row_2023"],
            }
        )
    return pd.DataFrame(rows).sort_values(["region_regime", "country"])


def read_data() -> pd.DataFrame:
    cols = [
        "country",
        "c_sample",
        "AGE",
        "SEX",
        "EDUCYRS",
        "EDULEVEL",
        "v1",
        "v2",
        "v3",
        "v4",
        "v5",
        "v6",
        "v7",
        "v8",
        "v9",
        "v10",
        "v11",
        "v12",
        "v13",
        "v14",
        "v15",
        "v16",
        "v17",
        "v18",
        "v19",
        "v20",
        "v21",
        "v22",
        "v23",
        "v24",
        "v25",
        "v26",
        "v27",
        "v28",
        "v29",
        "v30",
        "v31",
        "v35",
        "v38",
        "v41",
        "v42",
        "v43",
        "v44",
        "v46",
        "WEIGHT_COM",
    ]
    df, meta = pyreadstat.read_dta(str(DATA), usecols=cols, apply_value_formats=False)
    country_labels = meta.value_labels[meta.variable_to_label["country"]]
    country_lookup = {int(k): parse_country_label(v) for k, v in country_labels.items()}
    df["country_code"] = df["country"].astype(int)
    df["country_name"] = df["country_code"].map(country_lookup)

    class_df = country_classification_table()
    df = df.merge(class_df, on="country_code", how="left", suffixes=("", "_class"))
    df["country_name"] = df["country_class"].where(df["country_class"].notna(), df["country_name"])
    df = df.drop(columns=["country", "country_class"], errors="ignore")

    weight = pd.to_numeric(df["WEIGHT_COM"], errors="coerce")
    df["WEIGHT_COM"] = weight.where(weight > 0, 1.0)
    return add_scaled_measures(df)


def write_measure_summary(df: pd.DataFrame) -> None:
    measure_rows = []
    for measure in [
        "democracy_rights_all",
        "democracy_rights_liberal",
        "democracy_works_today",
        *OUTCOMES,
    ]:
        items = ITEM_GROUPS.get(measure)
        alpha = cronbach_alpha(df, items) if items else np.nan
        measure_rows.append(
            {
                "measure": measure,
                "label": MEASURE_LABELS[measure],
                "items": ", ".join(items) if items else measure,
                "n_nonmissing": int(df[measure].notna().sum()),
                "mean_all_issp_weighted": weighted_mean(df[measure], df["WEIGHT_COM"]),
                "alpha_unweighted_all_issp": alpha,
            }
        )
    pd.DataFrame(measure_rows).to_csv(OUT / "measure_summary.csv", index=False)


def write_country_means(df: pd.DataFrame) -> pd.DataFrame:
    country_rows = []
    for country, g in df.groupby("country_name", sort=False):
        row = {
            "country": country,
            "n": len(g),
            "weighted_n": g["WEIGHT_COM"].sum(),
            "region": g["region"].iloc[0],
            "region_regime": g["region_regime"].iloc[0],
            "vdem_row_2023": g["vdem_row_2023"].iloc[0],
            "regime_binary": g["regime_binary"].iloc[0],
            "grey_zone": bool(g["grey_zone"].iloc[0]),
            "core_west": g["region_regime"].iloc[0] == "Western democracies",
        }
        for measure in ["democracy_rights_liberal", "democracy_works_today", *OUTCOMES]:
            row[measure] = weighted_mean(g[measure], g["WEIGHT_COM"])
        country_rows.append(row)
    country_means = pd.DataFrame(country_rows).sort_values(["region_regime", "country"])
    country_means.to_csv(OUT / "country_means.csv", index=False)
    return country_means


def write_country_correlations(df: pd.DataFrame) -> pd.DataFrame:
    corr_rows = []
    for country, g in df.groupby("country_name", sort=False):
        for predictor in ["democracy_rights_liberal", "democracy_works_today"]:
            for outcome in OUTCOMES:
                s = weighted_corr_stats(g[predictor], g[outcome], g["WEIGHT_COM"])
                corr_rows.append(
                    {
                        "country": country,
                        "region": g["region"].iloc[0],
                        "region_regime": g["region_regime"].iloc[0],
                        "regime_binary": g["regime_binary"].iloc[0],
                        "predictor": predictor,
                        "outcome": outcome,
                        "outcome_label": MEASURE_LABELS[outcome],
                        "corr": s["r"],
                        "p_value": s["p"],
                        "sig": sig_stars(s["p"]),
                        "n_pairwise": s["n"],
                        "n_eff": s["n_eff"],
                    }
                )
    country_corrs = pd.DataFrame(corr_rows)
    country_corrs.to_csv(OUT / "country_correlations.csv", index=False)
    return country_corrs


def write_group_associations(df: pd.DataFrame, country_corrs: pd.DataFrame) -> pd.DataFrame:
    rows = []
    controls = ["age", "female", "education_level", "left_right"]
    for group_id, group_label, mask_fn in GROUPS:
        sdf = df[mask_fn(df)].copy()
        if sdf.empty:
            continue
        sdf["w_country_equal"] = country_equal_weights(sdf)
        countries = sorted(sdf["country_name"].dropna().unique())
        for predictor in ["democracy_rights_liberal", "democracy_works_today"]:
            for outcome in OUTCOMES:
                cc = country_corrs[
                    (country_corrs["country"].isin(countries))
                    & (country_corrs["predictor"] == predictor)
                    & (country_corrs["outcome"] == outcome)
                ]["corr"].dropna()
                corr = weighted_within_corr_stats(sdf, predictor, outcome, "w_country_equal")
                beta, model_n = wls_beta(sdf, outcome, predictor, controls, "w_country_equal")
                rows.append(
                    {
                        "group": group_id,
                        "group_label": group_label,
                        "predictor": predictor,
                        "predictor_label": MEASURE_LABELS[predictor],
                        "outcome": outcome,
                        "outcome_label": MEASURE_LABELS[outcome],
                        "within_country_weighted_corr": corr["r"],
                        "p_value": corr["p"],
                        "sig": sig_stars(corr["p"]),
                        "formatted_corr": fmt_r(corr["r"], corr["p"]),
                        "n_eff": corr["n_eff"],
                        "pairwise_n": corr["n"],
                        "median_country_corr": float(cc.median()) if len(cc) else np.nan,
                        "mean_country_corr": float(cc.mean()) if len(cc) else np.nan,
                        "n_negative": int((cc < 0).sum()) if len(cc) else 0,
                        "n_positive": int((cc > 0).sum()) if len(cc) else 0,
                        "n_countries": len(countries),
                        "adjusted_wls_beta": beta,
                        "adjusted_model_n": model_n,
                    }
                )
    pooled = pd.DataFrame(rows)
    pooled.to_csv(OUT / "pooled_associations.csv", index=False)
    pooled.to_csv(OUT / "regional_associations.csv", index=False)

    rights = pooled[pooled["predictor"] == "democracy_rights_liberal"].copy()
    rights[rights["outcome"].isin(SELECTED_OUTCOMES)].to_csv(
        OUT / "regional_democratic_rights_selected.csv", index=False
    )

    perf = pooled[pooled["predictor"] == "democracy_works_today"].copy()
    perf[perf["outcome"].isin(PERFORMANCE_OUTCOMES)].to_csv(
        OUT / "regional_democracy_performance_selected.csv", index=False
    )

    # Backward-compatible first-pass summaries.
    core = rights[rights["group"] == "western_democracies"].copy()
    core[
        [
            "outcome_label",
            "within_country_weighted_corr",
            "p_value",
            "sig",
            "median_country_corr",
            "n_negative",
            "n_positive",
            "adjusted_wls_beta",
            "pairwise_n",
        ]
    ].to_csv(OUT / "core_west_democratic_rights_summary.csv", index=False)

    core_perf = perf[perf["group"] == "western_democracies"].copy()
    core_perf[
        [
            "outcome_label",
            "within_country_weighted_corr",
            "p_value",
            "sig",
            "median_country_corr",
            "n_negative",
            "n_positive",
            "adjusted_wls_beta",
            "pairwise_n",
        ]
    ].to_csv(OUT / "core_west_democracy_performance_summary.csv", index=False)
    return pooled


def weighted_quantile(values: pd.Series, weights: pd.Series, quantiles: list[float]) -> np.ndarray:
    d = pd.DataFrame({"value": values, "weight": weights}).dropna()
    d = d[d["weight"] > 0].sort_values("value")
    if d.empty:
        return np.array([np.nan for _ in quantiles])
    v = d["value"].to_numpy(dtype=float)
    w = d["weight"].to_numpy(dtype=float)
    cdf = np.cumsum(w) - 0.5 * w
    cdf = cdf / np.sum(w)
    return np.interp(quantiles, cdf, v)


def fit_wls_hc1(y: pd.Series, xmat: pd.DataFrame, weights: pd.Series) -> dict[str, object]:
    d = pd.concat([y.rename("__y__"), xmat, weights.rename("__w__")], axis=1).dropna()
    d = d[d["__w__"] > 0]
    n = len(d)
    k = xmat.shape[1]
    if n <= k + 5:
        return {"ok": False, "n": n}

    yv = d["__y__"].to_numpy(dtype=float)
    xvals = d[xmat.columns].to_numpy(dtype=float)
    w = d["__w__"].to_numpy(dtype=float)
    xw = xvals * np.sqrt(w)[:, None]
    yw = yv * np.sqrt(w)
    xtx_inv = np.linalg.pinv(xw.T @ xw)
    beta = xtx_inv @ (xw.T @ yw)
    resid = yv - xvals @ beta
    meat = (xvals * (w**2 * resid**2)[:, None]).T @ xvals
    cov = xtx_inv @ meat @ xtx_inv
    cov *= n / max(1, n - k)
    se = np.sqrt(np.maximum(np.diag(cov), 0))
    return {
        "ok": True,
        "n": n,
        "k": k,
        "columns": list(xmat.columns),
        "beta": pd.Series(beta, index=xmat.columns),
        "se": pd.Series(se, index=xmat.columns),
        "cov": pd.DataFrame(cov, index=xmat.columns, columns=xmat.columns),
    }


def p_from_estimate(estimate: float, se: float, df: int) -> float:
    if not np.isfinite(estimate) or not np.isfinite(se) or se <= 0 or df <= 0:
        return np.nan
    return float(2 * stats.t.sf(abs(estimate / se), df=df))


def contrast_from_model(model: dict[str, object], terms: list[tuple[str, float]]) -> tuple[float, float, float]:
    if not model.get("ok"):
        return np.nan, np.nan, np.nan
    beta = model["beta"]
    cov = model["cov"]
    estimate = 0.0
    var = 0.0
    for term, coef in terms:
        if term not in beta.index:
            return np.nan, np.nan, np.nan
        estimate += coef * beta[term]
    for term_i, coef_i in terms:
        for term_j, coef_j in terms:
            var += coef_i * coef_j * cov.loc[term_i, term_j]
    se = float(np.sqrt(max(var, 0)))
    p = p_from_estimate(estimate, se, int(model["n"]) - int(model["k"]))
    return float(estimate), se, p


def model_matrix_region_interaction(d: pd.DataFrame, predictor: str, controls: list[str]) -> pd.DataFrame:
    xmat = pd.DataFrame(index=d.index)
    xmat["const"] = 1.0
    xmat[predictor] = d[predictor].astype(float)
    for control in controls:
        xmat[control] = d[control].astype(float)
    for group in REGION_REGIME_ORDER:
        if group == "Western democracies":
            continue
        col = f"{predictor}:group={group}"
        xmat[col] = d[predictor].astype(float) * (d["region_regime"] == group).astype(float)
    country_dummies = pd.get_dummies(d["country_name"], prefix="country", drop_first=True, dtype=float)
    return pd.concat([xmat, country_dummies], axis=1)


def write_region_interaction_models(df: pd.DataFrame) -> pd.DataFrame:
    controls = ["age", "female", "education_level", "left_right"]
    model_df = df.copy()
    model_df["w_country_equal"] = country_equal_weights(model_df)
    rows = []
    for predictor in ["democracy_rights_liberal", "democracy_works_today"]:
        for outcome in OUTCOMES:
            needed = [outcome, predictor, "w_country_equal", "region_regime", "country_name", *controls]
            d = model_df[needed].dropna().copy()
            d = d[d["w_country_equal"] > 0]
            xmat = model_matrix_region_interaction(d, predictor, controls)
            model = fit_wls_hc1(d[outcome], xmat, d["w_country_equal"])
            if not model.get("ok"):
                continue
            for group in REGION_REGIME_ORDER:
                terms = [(predictor, 1.0)]
                if group != "Western democracies":
                    terms.append((f"{predictor}:group={group}", 1.0))
                slope, se, p = contrast_from_model(model, terms)
                g = d[d["region_regime"] == group]
                q10, q90 = weighted_quantile(g[predictor], g["w_country_equal"], [0.10, 0.90])
                span = q90 - q10 if np.isfinite(q10) and np.isfinite(q90) else np.nan
                change = slope * span if np.isfinite(slope) and np.isfinite(span) else np.nan
                change_se = se * span if np.isfinite(se) and np.isfinite(span) else np.nan
                change_p = p_from_estimate(change, change_se, int(model["n"]) - int(model["k"]))
                rows.append(
                    {
                        "predictor": predictor,
                        "predictor_label": MEASURE_LABELS[predictor],
                        "outcome": outcome,
                        "outcome_label": MEASURE_LABELS[outcome],
                        "group_label": group,
                        "slope": slope,
                        "se": se,
                        "p_value": p,
                        "sig": sig_stars(p),
                        "formatted_slope": fmt_r(slope, p),
                        "p10_predictor": q10,
                        "p90_predictor": q90,
                        "p10_to_p90_change": change,
                        "change_se": change_se,
                        "change_p_value": change_p,
                        "change_sig": sig_stars(change_p),
                        "formatted_change": fmt_r(change, change_p),
                        "model_n": int(model["n"]),
                        "group_n": int(len(g)),
                    }
                )
    out = pd.DataFrame(rows)
    out.to_csv(OUT / "region_interaction_model_slopes.csv", index=False)
    out[(out["predictor"] == "democracy_rights_liberal") & (out["outcome"].isin(SELECTED_OUTCOMES))].to_csv(
        OUT / "region_interaction_democratic_rights_selected.csv", index=False
    )
    out[(out["predictor"] == "democracy_works_today") & (out["outcome"].isin(PERFORMANCE_OUTCOMES))].to_csv(
        OUT / "region_interaction_democracy_performance_selected.csv", index=False
    )
    return out


def write_country_slopes(df: pd.DataFrame) -> pd.DataFrame:
    controls = ["age", "female", "education_level", "left_right"]
    rows = []
    for country, g0 in df.groupby("country_name", sort=False):
        for predictor in ["democracy_rights_liberal", "democracy_works_today"]:
            for outcome in OUTCOMES:
                needed = [outcome, predictor, "WEIGHT_COM", *controls]
                g = g0[needed].dropna().copy()
                g = g[g["WEIGHT_COM"] > 0]
                if len(g) < 80:
                    continue
                xmat = pd.DataFrame(index=g.index)
                xmat["const"] = 1.0
                xmat[predictor] = g[predictor].astype(float)
                for control in controls:
                    xmat[control] = g[control].astype(float)
                model = fit_wls_hc1(g[outcome], xmat, g["WEIGHT_COM"])
                if not model.get("ok"):
                    continue
                slope = model["beta"][predictor]
                se = model["se"][predictor]
                p = p_from_estimate(slope, se, int(model["n"]) - int(model["k"]))
                rows.append(
                    {
                        "country": country,
                        "region": g0["region"].iloc[0],
                        "region_regime": g0["region_regime"].iloc[0],
                        "regime_binary": g0["regime_binary"].iloc[0],
                        "predictor": predictor,
                        "outcome": outcome,
                        "outcome_label": MEASURE_LABELS[outcome],
                        "slope": slope,
                        "se": se,
                        "p_value": p,
                        "sig": sig_stars(p),
                        "formatted_slope": fmt_r(slope, p),
                        "model_n": int(model["n"]),
                    }
                )
    out = pd.DataFrame(rows)
    out.to_csv(OUT / "country_adjusted_slopes.csv", index=False)
    return out


def write_scale_reliability_by_group(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for group_id, group_label, mask_fn in GROUPS:
        sdf = df[mask_fn(df)].copy()
        for measure, items in ITEM_GROUPS.items():
            rows.append(
                {
                    "group": group_id,
                    "group_label": group_label,
                    "measure": measure,
                    "label": MEASURE_LABELS[measure],
                    "items": ", ".join(items),
                    "alpha_unweighted": cronbach_alpha(sdf, items),
                    "n_complete": int(sdf[items].dropna().shape[0]),
                }
            )
    out = pd.DataFrame(rows)
    out.to_csv(OUT / "scale_reliability_by_group.csv", index=False)
    return out


def write_group_counts(df: pd.DataFrame) -> None:
    class_df = country_classification_table()
    country_n = df.groupby("country_name").size().rename("n_respondents").reset_index()
    country_out = class_df.merge(country_n, left_on="country", right_on="country_name", how="left")
    country_out = country_out.drop(columns=["country_name"], errors="ignore")
    country_out.to_csv(OUT / "country_classification.csv", index=False)

    rows = []
    for group_id, group_label, mask_fn in GROUPS:
        sdf = df[mask_fn(df)].copy()
        rows.append(
            {
                "group": group_id,
                "group_label": group_label,
                "countries": sdf["country_name"].nunique(),
                "respondents": len(sdf),
                "democracy_countries": sdf.loc[sdf["regime_binary"] == "Democracy", "country_name"].nunique(),
                "non_democracy_countries": sdf.loc[
                    sdf["regime_binary"] == "Non-democracy", "country_name"
                ].nunique(),
            }
        )
    pd.DataFrame(rows).to_csv(OUT / "group_counts.csv", index=False)


def plot_core_summary(pooled: pd.DataFrame) -> None:
    core = pooled[
        (pooled["group"] == "western_democracies")
        & (pooled["predictor"] == "democracy_rights_liberal")
    ].copy()
    core = core.sort_values("within_country_weighted_corr")
    colors = ["#b54b4b" if v < 0 else "#2f6f8f" for v in core["within_country_weighted_corr"]]

    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    ax.barh(
        [SHORT_LABELS[o] for o in core["outcome"]],
        core["within_country_weighted_corr"],
        color=colors,
    )
    ax.axvline(0, color="#333333", linewidth=1)
    ax.set_xlim(-0.25, 0.05)
    ax.set_xlabel("Weighted within-country correlation with democratic-rights index")
    ax.set_title("ISSP 2023 Western democracies: democracy values vs. nationalism measures")
    fig.text(
        0.98,
        0.02,
        "Stars are descriptive markers; interpretation emphasizes effect sizes.",
        ha="right",
        va="bottom",
        fontsize=8,
        color="#555555",
    )
    fig.tight_layout(rect=[0, 0.05, 1, 1])
    fig.savefig(FIG / "core_west_democratic_rights_associations.png", dpi=220)
    plt.close(fig)


def _cell_text_color(im, val: float) -> str:
    """White text on dark heatmap cells, black on light ones, using the image's
    own colormap and normalization so the contrast tracks the rendered color."""
    r, g, b, _ = im.cmap(im.norm(val))
    luminance = 0.299 * r + 0.587 * g + 0.114 * b
    return "white" if luminance < 0.5 else "black"


def plot_region_heatmap(
    pooled: pd.DataFrame,
    predictor: str,
    outcomes: list[str],
    filename: str,
    title: str,
    groups: list[str] | None = None,
) -> None:
    d = pooled[(pooled["predictor"] == predictor) & (pooled["outcome"].isin(outcomes))].copy()
    if groups is None:
        groups = GROUP_ORDER
    d = d[d["group_label"].isin(groups)]
    pivot = d.pivot(index="group_label", columns="outcome", values="within_country_weighted_corr")
    pvals = d.pivot(index="group_label", columns="outcome", values="p_value")
    pivot = pivot.reindex(groups)[outcomes]
    pvals = pvals.reindex(groups)[outcomes]

    fig_width = 9.2 if len(outcomes) <= 4 else 11.2
    fig, ax = plt.subplots(figsize=(fig_width, 5.4))
    im = ax.imshow(pivot.to_numpy(), cmap="RdBu", vmin=-0.35, vmax=0.35, aspect="auto")
    ax.set_xticks(range(len(outcomes)), labels=[SHORT_LABELS[o] for o in outcomes])
    ax.set_yticks(range(len(pivot.index)), labels=pivot.index)
    ax.tick_params(axis="x", labelsize=9 if len(outcomes) > 4 else 10)
    ax.tick_params(axis="y", labelsize=10)
    # no in-figure title; the title lives in the LaTeX caption
    for i in range(pivot.shape[0]):
        for j in range(pivot.shape[1]):
            val = pivot.iloc[i, j]
            p = pvals.iloc[i, j]
            if pd.notna(val):
                ax.text(
                    j, i, fmt_r(val, p), ha="center", va="center", fontsize=8,
                    color=_cell_text_color(im, val),
                )
    cbar = fig.colorbar(im, ax=ax, fraction=0.032, pad=0.02)
    cbar.set_label("Within-country weighted correlation")
    fig.text(
        0.98,
        0.02,
        "* p<.05, ** p<.01, *** p<.001; stars are descriptive markers.",
        ha="right",
        fontsize=8,
        color="#555555",
    )
    fig.tight_layout(rect=[0, 0.05, 1, 1])
    fig.savefig(FIG / filename, dpi=220)
    plt.close(fig)


def plot_country_heatmap(country_corrs: pd.DataFrame) -> None:
    d = country_corrs[
        (country_corrs["predictor"] == "democracy_rights_liberal")
        & (country_corrs["outcome"].isin(SELECTED_OUTCOMES))
    ].copy()
    countries = country_classification_table()
    countries["region_order"] = countries["region_regime"].map(
        {v: i for i, v in enumerate(REGION_REGIME_ORDER)}
    )
    countries = countries.sort_values(["region_order", "country"])
    country_order = countries["country"].tolist()
    pivot = d.pivot(index="country", columns="outcome", values="corr").reindex(country_order)
    pvals = d.pivot(index="country", columns="outcome", values="p_value").reindex(country_order)
    pivot = pivot[SELECTED_OUTCOMES]
    pvals = pvals[SELECTED_OUTCOMES]

    fig, ax = plt.subplots(figsize=(8.8, 9.2))
    im = ax.imshow(pivot.to_numpy(), cmap="RdBu", vmin=-0.35, vmax=0.35, aspect="auto")
    ax.set_xticks(range(len(SELECTED_OUTCOMES)), labels=[SHORT_LABELS[o] for o in SELECTED_OUTCOMES])
    ax.set_yticks(range(len(pivot.index)), labels=pivot.index)
    ax.set_title("Country correlations with democratic-rights index, ISSP 2023")
    for i in range(pivot.shape[0]):
        for j in range(pivot.shape[1]):
            val = pivot.iloc[i, j]
            p = pvals.iloc[i, j]
            if pd.notna(val):
                ax.text(
                    j, i, fmt_r(val, p), ha="center", va="center", fontsize=6.5,
                    color=_cell_text_color(im, val),
                )
    cbar = fig.colorbar(im, ax=ax, fraction=0.028, pad=0.02)
    cbar.set_label("Correlation")
    fig.tight_layout()
    fig.savefig(FIG / "all_countries_democratic_rights_country_heatmap.png", dpi=220)
    plt.close(fig)


def plot_performance_scatter(country_means: pd.DataFrame) -> None:
    d = country_means.copy()
    color_map = {"Democracy": "#2f6f8f", "Non-democracy": "#b54b4b"}
    marker_map = {
        "West": "o",
        "Eastern Europe": "s",
        "East Asia": "^",
        "South/Southeast Asia": "D",
        "Other": "P",
    }

    fig, ax = plt.subplots(figsize=(8.2, 5.8))
    for (regime, region), g in d.groupby(["regime_binary", "region"]):
        ax.scatter(
            g["democracy_works_today"],
            g["national_pride_non_democracy"],
            c=color_map[regime],
            marker=marker_map[region],
            edgecolor="#222222",
            linewidth=0.4,
            s=55,
            label=f"{region}, {regime}",
        )
        for _, row in g.iterrows():
            ax.text(
                row["democracy_works_today"] + 0.004,
                row["national_pride_non_democracy"] + 0.004,
                row["country"],
                fontsize=6.6,
            )
    ax.set_xlabel("Country mean: perceived democracy performance")
    ax.set_ylabel("Country mean: national pride, excluding pride in democracy")
    ax.set_title("Democracy performance and national pride across ISSP 2023 countries")
    ax.grid(True, color="#dddddd", linewidth=0.6)
    ax.legend(loc="center left", bbox_to_anchor=(1.02, 0.5), fontsize=7, frameon=False)
    fig.tight_layout()
    fig.savefig(FIG / "country_means_democracy_performance_national_pride.png", dpi=220)
    plt.close(fig)


def plot_regime_bars(pooled: pd.DataFrame) -> None:
    d = pooled[
        (pooled["group"].isin(["democracies", "non_democracies"]))
        & (pooled["predictor"] == "democracy_rights_liberal")
        & (pooled["outcome"].isin(SELECTED_OUTCOMES))
    ].copy()
    d["outcome_short"] = d["outcome"].map(
        {
            "ascriptive_membership": "Ascriptive",
            "national_superiority": "Superiority",
            "anti_immigrant_exclusion": "Anti-immigrant",
            "national_pride_non_democracy": "Pride",
        }
    )
    x = np.arange(len(SELECTED_OUTCOMES))
    width = 0.36
    fig, ax = plt.subplots(figsize=(8.0, 4.7))
    for offset, group, color in [
        (-width / 2, "All democracies", "#2f6f8f"),
        (width / 2, "All non-democracies", "#b54b4b"),
    ]:
        vals = d[d["group_label"] == group].set_index("outcome").reindex(SELECTED_OUTCOMES)
        ax.bar(x + offset, vals["within_country_weighted_corr"], width=width, color=color, label=group)
        for i, (_, row) in enumerate(vals.iterrows()):
            ax.text(
                x[i] + offset,
                row["within_country_weighted_corr"] + (0.015 if row["within_country_weighted_corr"] >= 0 else -0.02),
                sig_stars(row["p_value"]),
                ha="center",
                va="center",
                fontsize=9,
            )
    ax.axhline(0, color="#333333", linewidth=1)
    ax.set_xticks(x, labels=["Ascriptive", "Superiority", "Anti-immigrant", "Pride"])
    ax.set_ylabel("Within-country weighted correlation")
    ax.set_title("Democratic-rights endorsement: democracies vs. non-democracies")
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(FIG / "regime_democratic_rights_comparison.png", dpi=220)
    plt.close(fig)


def plot_adjusted_region_changes(region_models: pd.DataFrame) -> None:
    configs = [
        (
            "democracy_rights_liberal",
            SELECTED_OUTCOMES,
            "adjusted_democratic_rights_region_changes.png",
            "Adjusted change from low to high democratic-rights endorsement",
        ),
        (
            "democracy_works_today",
            PERFORMANCE_OUTCOMES,
            "adjusted_democracy_performance_region_changes.png",
            "Adjusted change from low to high perceived democracy performance",
        ),
    ]
    for predictor, outcomes, filename, title in configs:
        d = region_models[
            (region_models["predictor"] == predictor) & (region_models["outcome"].isin(outcomes))
        ].copy()
        pivot = d.pivot(index="group_label", columns="outcome", values="p10_to_p90_change")
        pvals = d.pivot(index="group_label", columns="outcome", values="change_p_value")
        pivot = pivot.reindex(REGION_REGIME_ORDER)[outcomes]
        pvals = pvals.reindex(REGION_REGIME_ORDER)[outcomes]

        fig_width = 9.2 if len(outcomes) <= 4 else 11.2
        fig, ax = plt.subplots(figsize=(fig_width, 5.4))
        im = ax.imshow(pivot.to_numpy(), cmap="RdBu", vmin=-0.16, vmax=0.16, aspect="auto")
        ax.set_xticks(range(len(outcomes)), labels=[SHORT_LABELS[o] for o in outcomes])
        ax.set_yticks(range(len(pivot.index)), labels=pivot.index)
        ax.tick_params(axis="x", labelsize=9 if len(outcomes) > 4 else 10)
        ax.tick_params(axis="y", labelsize=10)
        ax.set_title(title)
        for i in range(pivot.shape[0]):
            for j in range(pivot.shape[1]):
                val = pivot.iloc[i, j]
                p = pvals.iloc[i, j]
                if pd.notna(val):
                    ax.text(
                        j, i, fmt_r(val, p), ha="center", va="center", fontsize=8,
                        color=_cell_text_color(im, val),
                    )
        cbar = fig.colorbar(im, ax=ax, fraction=0.032, pad=0.02)
        cbar.set_label("Predicted change on 0-1 outcome scale")
        fig.text(
            0.98,
            0.02,
            "Weighted OLS with country fixed effects and controls; low/high use group p10/p90 of predictor.",
            ha="right",
            fontsize=8,
            color="#555555",
        )
        fig.tight_layout(rect=[0, 0.05, 1, 1])
        fig.savefig(FIG / filename, dpi=220)
        plt.close(fig)


def plot_country_adjusted_slopes(country_slopes: pd.DataFrame) -> None:
    outcomes = ["ascriptive_membership", "anti_immigrant_exclusion", "national_pride_non_democracy"]
    d = country_slopes[
        (country_slopes["predictor"] == "democracy_rights_liberal")
        & (country_slopes["outcome"].isin(outcomes))
    ].copy()
    country_order = (
        country_classification_table()
        .assign(region_order=lambda x: x["region_regime"].map({v: i for i, v in enumerate(REGION_REGIME_ORDER)}))
        .sort_values(["region_order", "country"])["country"]
        .tolist()
    )
    x_positions = np.arange(len(country_order))
    offsets = {
        "ascriptive_membership": -0.22,
        "anti_immigrant_exclusion": 0.0,
        "national_pride_non_democracy": 0.22,
    }
    colors = {
        "ascriptive_membership": "#6b6b6b",
        "anti_immigrant_exclusion": "#b54b4b",
        "national_pride_non_democracy": "#2f6f8f",
    }
    labels = {
        "ascriptive_membership": "Ascriptive membership",
        "anti_immigrant_exclusion": "Anti-immigrant exclusion",
        "national_pride_non_democracy": "National pride",
    }

    fig, ax = plt.subplots(figsize=(11.5, 5.8))
    for outcome in outcomes:
        vals = d[d["outcome"] == outcome].set_index("country").reindex(country_order)
        yerr = 1.96 * vals["se"].to_numpy(dtype=float)
        ax.errorbar(
            x_positions + offsets[outcome],
            vals["slope"],
            yerr=yerr,
            fmt="o",
            markersize=3.8,
            color=colors[outcome],
            ecolor=colors[outcome],
            elinewidth=0.8,
            capsize=1.5,
            label=labels[outcome],
        )
    ax.axhline(0, color="#333333", linewidth=1)
    ax.set_xticks(x_positions, labels=country_order, rotation=60, ha="right")
    ax.set_ylabel("Adjusted slope")
    ax.set_title("Country-level adjusted slopes for democratic-rights endorsement")
    ax.legend(frameon=False, ncol=3, loc="upper left")
    ax.grid(axis="y", color="#dddddd", linewidth=0.6)
    fig.tight_layout()
    fig.savefig(FIG / "country_adjusted_democratic_rights_slopes.png", dpi=220)
    plt.close(fig)


def main() -> None:
    df = read_data()
    write_group_counts(df)
    write_measure_summary(df)
    country_means = write_country_means(df)
    country_corrs = write_country_correlations(df)
    pooled = write_group_associations(df, country_corrs)
    region_models = write_region_interaction_models(df)
    country_slopes = write_country_slopes(df)
    write_scale_reliability_by_group(df)

    plot_core_summary(pooled)
    plot_region_heatmap(
        pooled,
        predictor="democracy_rights_liberal",
        outcomes=SELECTED_OUTCOMES,
        filename="regional_democratic_rights_heatmap.png",
        title="Democratic-rights endorsement and nationalism by regional/regime group",
        groups=[
            "Western democracies",
            "Eastern Europe democracies",
            "Eastern Europe non-democracies",
            "East Asian democracies",
            "South/Southeast Asia non-democracies",
            "Other democracies",
        ],
    )
    plot_region_heatmap(
        pooled,
        predictor="democracy_works_today",
        outcomes=PERFORMANCE_OUTCOMES,
        filename="regional_democracy_performance_heatmap.png",
        title="Perceived democracy performance and nationalism by regional/regime group",
        groups=[
            "Western democracies",
            "Eastern Europe democracies",
            "Eastern Europe non-democracies",
            "East Asian democracies",
            "South/Southeast Asia non-democracies",
            "Other democracies",
        ],
    )
    plot_country_heatmap(country_corrs)
    plot_performance_scatter(country_means)
    plot_regime_bars(pooled)
    plot_adjusted_region_changes(region_models)
    plot_country_adjusted_slopes(country_slopes)


if __name__ == "__main__":
    main()
