#!/usr/bin/env bash
# master.sh — entry point for the replication package.
# Regenerates every CSV in outputs/ and every figure in figures/ from the ISSP
# microdata (see data/README.md) and V-Dem v15. Run from anywhere; the script
# sets its working directory to the package root so the R scripts' relative
# `outputs/` paths resolve. Mixed Python + R pipeline; steps run in order.
set -euo pipefail

cd "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"   # package root (replication/)
mkdir -p outputs figures

echo "[1/9] Descriptive measures, regional correlations, heatmaps..."
python3 code/issp2023_democracy_nationalism.py

echo "[2/9] V-Dem v15 indices for the 29 countries..."
Rscript code/vdem_extract.R

echo "[3/9] Assemble analysis-ready individual + country-level files..."
python3 code/build_analysis_data.py

echo "[4/9] Measurement invariance (multi-group CFA + alignment)..."
Rscript code/measurement_invariance.R

echo "[5/9] Multilevel models + cross-level moderation horse race..."
Rscript code/multilevel_models.R

echo "[6/9] Country-level second-stage diagnostic..."
Rscript code/diagnostic_secondstage.R

echo "[7/9] Longitudinal harmonization (1995-2023)..."
python3 code/longitudinal_trends.py

echo "[8/9] Democratic-socialization cohort test (Taiwan, South Korea)..."
python3 code/cohort_test.py

echo "[9/9] Publication figures..."
python3 code/figures_v2.py
Rscript code/figures_ggrepel.R

echo "Done. Outputs in outputs/, figures in figures/."
echo "To rebuild the manuscript, copy the figures used into ../overleaf/figures/ and run 'make' there."