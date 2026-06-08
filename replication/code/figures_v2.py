#!/usr/bin/env python3
"""Matplotlib publication figures: F3 two faces (principles vs performance) and the
SI longitudinal panel (1995-2023, West vs rest). The two country-level figures
(fig1_moderation, fig2_random_slopes) and the SI country-slopes facet are produced by
code/figures_ggrepel.R (ggplot2 + ggrepel, colorblind-safe palette).
"""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

EXPLORE = Path(__file__).resolve().parents[1]   # replication/
OUT, FIG = EXPLORE / "outputs", EXPLORE / "figures"
FIG.mkdir(exist_ok=True)
plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False,
                     "figure.dpi": 150, "savefig.dpi": 240, "axes.titlesize": 11})

# F3 two faces: principles vs performance pooled within-country slopes
fe = pd.read_csv(OUT / "ml_fixed_effects.csv")
pf = pd.read_csv(OUT / "ml_performance_fixed_effects.csv")
prin = fe[(fe.model == "M1") & (fe.term == "dr_cwc")].set_index("outcome")["est"]
perf = pf[pf.term == "perf_cwc"].set_index("outcome")["est"]
outs = ["anti_immigrant_exclusion", "ascriptive_membership", "national_superiority",
        "national_pride_non_democracy"]
labels = ["Anti-immigrant\nexclusion", "Ascriptive\nmembership", "National\nsuperiority", "National\npride"]
xp = np.arange(len(outs)); w = 0.38
fig, ax = plt.subplots(figsize=(8.2, 4.8))
ax.bar(xp - w/2, [prin.get(o, np.nan) for o in outs], w, color="#0072B2", label="Democratic principles (rights endorsement)")
ax.bar(xp + w/2, [perf.get(o, np.nan) for o in outs], w, color="#E69F00", label="Democratic performance (works well)")
ax.axhline(0, color="#333", lw=1)
ax.set_xticks(xp, labels=labels, fontsize=9)
ax.set_ylabel("Pooled within-country slope (0–1 outcome)")
ax.legend(frameon=False, fontsize=8.5, loc="lower right")  # title lives in the caption
fig.tight_layout(); fig.savefig(FIG / "fig3_two_faces.png", bbox_inches="tight"); plt.close(fig)

# F4 longitudinal (SI)
lt = pd.read_csv(OUT / "longitudinal_trends.csv")
fig, axes = plt.subplots(1, 2, figsize=(10, 4.3), sharex=True)
# panel tags only; panel descriptions and the overall title live in the caption
for ax, meas, tag in [(axes[0], "ascriptive", "(A)"), (axes[1], "anti_imm", "(B)")]:
    for grp, c in [("West", "#1f6f8b"), ("Non-West", "#d1495b")]:
        s = lt[(lt.measure == meas) & (lt.group == grp)].sort_values("year")
        ax.plot(s["year"], s["mean"], "-o", color=c, label=grp, lw=1.8, ms=6)
    ax.set_title(tag, loc="left", fontsize=11, fontweight="bold"); ax.set_xticks([1995, 2003, 2013, 2023])
    ax.set_ylim(0.3, 0.7); ax.grid(axis="y", color="#eee")
axes[0].set_ylabel("Weighted mean (0–1)"); axes[0].legend(frameon=False, fontsize=9)
fig.tight_layout(); fig.savefig(FIG / "figS_longitudinal.png", bbox_inches="tight"); plt.close(fig)

print("Wrote: fig3_two_faces, figS_longitudinal")
print("Two-faces slopes:\n", pd.DataFrame({"principles": prin.reindex(outs), "performance": perf.reindex(outs)}).round(3))
