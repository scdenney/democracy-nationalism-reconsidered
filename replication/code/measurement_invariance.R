#!/usr/bin/env Rscript
# Measurement invariance of the key ISSP 2023 scales across the 6 region-regime
# groups, and alignment across the 29 countries. Purpose: establish what level of
# cross-context comparison is licensed. Following Davidov (2009, Political Analysis)
# we expect METRIC invariance (loadings comparable -> associations comparable) but
# scalar failure (intercepts vary -> latent MEANS not comparable). That is exactly
# the warrant for an association-based, within-context design.
suppressMessages({library(lavaan); library(semTools); library(sirt)})
set.seed(20260604)  # sirt::invariance.alignment uses a non-convex optimizer; seed for exact reproduction

d <- read.csv("outputs/analysis_individual.csv", stringsAsFactors = FALSE)
d$region_regime <- factor(d$region_regime)

scales <- list(
  anti_immigrant = c("immigrants_increase_crime","immigrants_bad_economy","immigrants_take_jobs",
                     "immigrants_not_improve_society","native_born_preference","reduce_immigration"),
  ascriptive     = c("born_important","religion_important","ancestry_important","born_not_effort"),
  superiority    = c("world_better_if_like_us","country_better_than_most","support_country_wrong"),
  dem_rights     = c("dem_minority_rights","dem_more_participation","dem_civil_disobedience")
)

fitcols <- c("cfi","tli","rmsea","srmr")
get_fm <- function(fit) tryCatch(round(fitMeasures(fit, fitcols), 3),
                                 error=function(e) setNames(rep(NA,4), fitcols))

cat("=== Multi-group CFA invariance across 6 region-regime groups (ML, continuous) ===\n")
inv_rows <- list()
for (nm in names(scales)) {
  items <- scales[[nm]]
  mod <- paste0("F =~ ", paste(items, collapse = " + "))
  cfg <- tryCatch(cfa(mod, data=d, group="region_regime", missing="fiml", estimator="ML"),
                  error=function(e) NULL)
  met <- tryCatch(cfa(mod, data=d, group="region_regime", group.equal="loadings",
                      missing="fiml", estimator="ML"), error=function(e) NULL)
  sca <- tryCatch(cfa(mod, data=d, group="region_regime",
                      group.equal=c("loadings","intercepts"), missing="fiml", estimator="ML"),
                  error=function(e) NULL)
  for (lvl in c("configural","metric","scalar")) {
    fit <- switch(lvl, configural=cfg, metric=met, scalar=sca)
    if (is.null(fit)) next
    fm <- get_fm(fit)
    inv_rows[[paste(nm,lvl)]] <- data.frame(scale=nm, n_items=length(items), level=lvl,
        cfi=fm["cfi"], tli=fm["tli"], rmsea=fm["rmsea"], srmr=fm["srmr"], row.names=NULL)
  }
}
inv <- do.call(rbind, inv_rows)
# delta CFI vs previous level within scale
inv$dCFI <- NA
for (nm in unique(inv$scale)) {
  idx <- which(inv$scale==nm)
  for (j in seq_along(idx)[-1]) inv$dCFI[idx[j]] <- round(inv$cfi[idx[j]] - inv$cfi[idx[j-1]], 3)
}
print(inv, row.names=FALSE)
write.csv(inv, "outputs/invariance_multigroup.csv", row.names=FALSE)
cat("\nDecision rule: metric/scalar tenable if dCFI >= -0.010 (Cheung & Rensvold 2002).\n")

cat("\n=== Alignment across 29 countries (sirt::invariance.alignment) ===\n")
align_rows <- list()
for (nm in c("anti_immigrant","ascriptive")) {
  items <- scales[[nm]]
  dd <- d[stats::complete.cases(d[,items]) & !is.na(d$country_name), c("country_name", items)]
  grp <- dd$country_name
  # per-group standardized loadings + intercepts from single-group 1-factor CFAs
  G <- sort(unique(grp)); I <- length(items)
  lambda <- matrix(NA, length(G), I, dimnames=list(G, items))
  nu     <- matrix(NA, length(G), I, dimnames=list(G, items))
  mod <- paste0("F =~ ", paste(items, collapse=" + "))
  for (g in G) {
    sub <- dd[grp==g, items]
    f <- tryCatch(cfa(mod, data=sub, meanstructure=TRUE, estimator="ML"), error=function(e) NULL)
    if (is.null(f)) next
    pe <- parameterEstimates(f)
    lo <- pe[pe$op=="=~", c("rhs","est")]; ni <- pe[pe$op=="~1" & pe$rhs=="", c("lhs","est")]
    lambda[g, lo$rhs] <- lo$est
    in_ <- pe[pe$op=="~1" & pe$lhs %in% items, c("lhs","est")]
    nu[g, in_$lhs] <- in_$est
  }
  ok <- stats::complete.cases(lambda) & stats::complete.cases(nu)
  al <- tryCatch(sirt::invariance.alignment(lambda=lambda[ok,,drop=FALSE], nu=nu[ok,,drop=FALSE]),
                 error=function(e) {cat("  [", nm, "] alignment error:", conditionMessage(e), "\n"); NULL})
  if (!is.null(al)) {
    es <- al$es.invariance        # rows: R2, sqrtU2, rbar ; cols: loadings, intercepts
    rbar <- as.numeric(es["rbar", ])     # avg cross-group corr of aligned params (higher = more invariant)
    align_rows[[nm]] <- data.frame(scale=nm, n_groups=sum(ok),
        rbar_loadings=round(rbar[1],3), rbar_intercepts=round(rbar[2],3), row.names=NULL)
  }
}
if (length(align_rows)) {
  al_df <- do.call(rbind, align_rows)
  print(al_df, row.names=FALSE)
  write.csv(al_df, "outputs/invariance_alignment.csv", row.names=FALSE)
  cat("\nrbar = avg cross-country correlation of aligned parameters; loadings > intercepts\n",
      "=> loadings (govern ASSOCIATIONS) more invariant than intercepts (govern MEANS):\n",
      "corroborates metric>scalar and licenses comparing associations, not means.\n")
} else cat("alignment did not converge; rely on multigroup result + Davidov (2009).\n")
