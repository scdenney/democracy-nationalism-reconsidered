#!/usr/bin/env Rscript
# Second-stage diagnostic (N=29 countries): what moderates the country-specific
# democratic-rights <-> nationalism slope? Candidate moderators:
#  (a) V-Dem LIBERAL component (institutional liberalism)
#  (b) V-Dem ELECTORAL component (polyarchy)
#  (c) civic-vs-ethnic CONTENT of nationhood (country mean), measured from ISSP itself
# This previews the cross-level interaction before fitting the full multilevel model.
suppressMessages({library(stats)})

cc <- read.csv("outputs/country_correlations.csv", stringsAsFactors = FALSE)
cl <- read.csv("outputs/country_level.csv", stringsAsFactors = FALSE)

cc <- cc[cc$predictor == "democracy_rights_liberal",
         c("country","outcome","corr","p_value","region_regime")]
m <- merge(cc, cl, by.x = "country", by.y = "country_name", all.x = TRUE,
           suffixes = c("", "_cl"))

outs <- c("anti_immigrant_exclusion","ascriptive_membership",
          "national_superiority","national_pride_non_democracy")

cat("=== Country-level (N=29) correlations of the dem-rights<->outcome slope with candidate moderators ===\n")
cat(sprintf("%-26s %8s %8s %8s %8s\n","outcome","libcomp","polyarchy","civic-eth","ascr.mean"))
for (o in outs) {
  d <- m[m$outcome == o, ]
  r_lib  <- cor(d$corr, d$v2x_liberal,  use="complete.obs")
  r_poly <- cor(d$corr, d$v2x_polyarchy,use="complete.obs")
  r_civ  <- cor(d$corr, d$cm_civic_minus_ethnic, use="complete.obs")
  r_asc  <- cor(d$corr, d$cm_ascriptive_membership, use="complete.obs")
  cat(sprintf("%-26s %8.2f %8.2f %8.2f %8.2f\n", o, r_lib, r_poly, r_civ, r_asc))
}
cat("\n(Interpretation: a NEGATIVE corr with civic-minus-ethnic + POSITIVE with ascr.mean\n")
cat(" means the slope becomes more negative where nationhood is more civic / less ethnic.)\n")

cat("\n=== Anti-immigrant slope: West vs East Asia at similar institutional liberalism ===\n")
d <- m[m$outcome == "anti_immigrant_exclusion", ]
show <- d[d$region_regime %in% c("Western democracies","East Asian democracies"),
          c("country","region_regime","corr","v2x_liberal","cm_ascriptive_membership")]
show <- show[order(show$region_regime, -show$v2x_liberal), ]
print(show, row.names = FALSE, digits = 3)

cat("\n=== mean per-country slope by region-regime group ===\n")
for (o in c("anti_immigrant_exclusion","ascriptive_membership")) {
  cat("--", o, "--\n")
  agg <- aggregate(corr ~ region_regime, data = m[m$outcome==o,], FUN = function(x) round(mean(x),3))
  agg <- agg[order(agg$corr), ]
  print(agg, row.names = FALSE)
}

# Does civic-ethnic content beat V-Dem in a head-to-head country-level regression?
cat("\n=== Head-to-head country-level regressions (standardized predictors) ===\n")
for (o in c("anti_immigrant_exclusion","ascriptive_membership")) {
  d <- m[m$outcome==o, ]
  d$z_lib  <- scale(d$v2x_liberal)
  d$z_poly <- scale(d$v2x_polyarchy)
  d$z_civ  <- scale(d$cm_civic_minus_ethnic)
  cat("\n--", o, ": slope ~ V-Dem liberal + civic-ethnic content --\n")
  fit1 <- lm(corr ~ z_lib + z_civ, data = d)
  print(round(summary(fit1)$coefficients, 3)); cat("adj R2:", round(summary(fit1)$adj.r.squared,3), "\n")
  cat("-- ", o, ": slope ~ polyarchy + civic-ethnic content --\n")
  fit2 <- lm(corr ~ z_poly + z_civ, data = d)
  print(round(summary(fit2)$coefficients, 3)); cat("adj R2:", round(summary(fit2)$adj.r.squared,3), "\n")
}
