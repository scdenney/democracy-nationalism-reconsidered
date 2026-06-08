#!/usr/bin/env Rscript
# Multilevel models: individuals (L1) nested in countries (L2).
# Headline: random-slope models for the democratic-rights <-> nationalism link, with a
# cross-level MODERATION HORSE RACE -- does the civic/ethnic CONTENT of nationhood
# (country-mean ascriptive endorsement) moderate the slope, net of V-Dem institutional
# liberalism? Plus the "two faces" performance models.
suppressMessages({library(lme4)})
has_lmerTest <- requireNamespace("lmerTest", quietly = TRUE)
if (has_lmerTest) suppressMessages(library(lmerTest))

d <- read.csv("outputs/analysis_individual.csv", stringsAsFactors = FALSE)

# ---- L1 predictors: group-mean-center democratic-rights within country (pure within effect) ----
cm_dr <- tapply(d$democracy_rights_liberal, d$country_code, mean, na.rm = TRUE)
d$dr_cm  <- as.numeric(cm_dr[as.character(d$country_code)])
d$dr_cwc <- d$democracy_rights_liberal - d$dr_cm           # within-country deviation
cm_perf  <- tapply(d$democracy_works_today, d$country_code, mean, na.rm = TRUE)
d$perf_cm  <- as.numeric(cm_perf[as.character(d$country_code)])
d$perf_cwc <- d$democracy_works_today - d$perf_cm
d$dr_cm_c   <- d$dr_cm   - mean(cm_dr, na.rm = TRUE)        # grand-mean center the L2 mean
d$perf_cm_c <- d$perf_cm - mean(cm_perf, na.rm = TRUE)

# ---- L2 moderators: standardize across the 29 COUNTRIES (equal country weight) ----
cl <- aggregate(cbind(cm_ascriptive_membership, v2x_liberal, v2x_polyarchy) ~ country_code,
                data = d, FUN = function(x) x[1])
z <- function(v) (v - mean(v)) / sd(v)
cl$z_content <- z(cl$cm_ascriptive_membership)   # higher = more ETHNIC conception of nationhood
cl$z_liberal <- z(cl$v2x_liberal)                # V-Dem liberal component
cl$z_polyarchy <- z(cl$v2x_polyarchy)
d <- merge(d, cl[, c("country_code","z_content","z_liberal","z_polyarchy")], by="country_code")

# ---- L1 controls (standardize continuous) ----
d$age_z  <- as.numeric(scale(d$age))
d$edu_z  <- as.numeric(scale(d$education_level))
d$lr     <- d$left_right
d$female <- d$female

ctrl <- lmerControl(optimizer = "bobyqa", optCtrl = list(maxfun = 2e5))
pval <- function(t) 2 * pnorm(-abs(t))

extract_fe <- function(fit, outcome, model) {
  cf <- summary(fit)$coefficients
  tcol <- if ("t value" %in% colnames(cf)) "t value" else colnames(cf)[3]
  data.frame(outcome = outcome, model = model, term = rownames(cf),
             est = round(cf[, "Estimate"], 4), se = round(cf[, "Std. Error"], 4),
             t = round(cf[, tcol], 3), p = signif(pval(cf[, tcol]), 3), row.names = NULL)
}
extract_re <- function(fit, outcome) {
  vc <- as.data.frame(VarCorr(fit))
  sd_int <- vc$sdcor[vc$grp=="country_code" & vc$var1=="(Intercept)" & is.na(vc$var2)]
  sd_slp <- vc$sdcor[vc$grp=="country_code" & vc$var1=="dr_cwc" & is.na(vc$var2)]
  rho    <- vc$sdcor[vc$grp=="country_code" & !is.na(vc$var2)]
  resid  <- vc$sdcor[vc$grp=="Residual"]
  data.frame(outcome=outcome, sd_intercept=round(sd_int,4),
             sd_slope=ifelse(length(sd_slp),round(sd_slp,4),NA),
             corr_int_slope=ifelse(length(rho),round(rho,3),NA),
             sd_resid=round(resid,4), singular=isSingular(fit))
}

OUT <- c("anti_immigrant_exclusion","ascriptive_membership","national_superiority",
         "national_pride_non_democracy")
fe_all <- list(); re_all <- list(); slopes <- list()

cat("=== DEMOCRATIC-RIGHTS models (random slope + cross-level moderation horse race) ===\n")
for (o in OUT) {
  d$Y <- d[[o]]
  base_rhs <- "dr_cwc + dr_cm_c + age_z + female + edu_z + lr + (1 + dr_cwc | country_code)"
  m1 <- tryCatch(lmer(reformulate(base_rhs, "Y"), data=d, control=ctrl, REML=FALSE), error=function(e) NULL)
  m2 <- tryCatch(lmer(reformulate(paste(base_rhs, "+ dr_cwc:z_content + z_content"), "Y"),
                      data=d, control=ctrl, REML=FALSE), error=function(e) NULL)
  m3 <- tryCatch(lmer(reformulate(paste(base_rhs,
                      "+ dr_cwc:z_content + z_content + dr_cwc:z_liberal + z_liberal"), "Y"),
                      data=d, control=ctrl, REML=FALSE), error=function(e) NULL)
  for (mm in list(c("M1",m1),c("M2",m2),c("M3",m3))) {
    if (!is.null(mm[[2]])) fe_all[[paste(o,mm[[1]])]] <- extract_fe(mm[[2]], o, mm[[1]])
  }
  if (!is.null(m1)) re_all[[o]] <- extract_re(m1, o)
  # implied within-country slope at civic (z_content=-1), mean (0), ethnic (+1) from M2
  if (!is.null(m2)) {
    b <- fixef(m2); s <- b["dr_cwc"]; im <- b["dr_cwc:z_content"]
    slopes[[o]] <- data.frame(outcome=o,
        slope_civic_m1sd = round(s - im, 4), slope_mean = round(s, 4),
        slope_ethnic_p1sd = round(s + im, 4), interaction_dr_x_content = round(im,4))
  }
  cat(sprintf("  %-30s done (M1 singular=%s)\n", o, if(!is.null(m1)) isSingular(m1) else "NA"))
}

fe <- do.call(rbind, fe_all); re <- do.call(rbind, re_all); sl <- do.call(rbind, slopes)
write.csv(fe, "outputs/ml_fixed_effects.csv", row.names=FALSE)
write.csv(re, "outputs/ml_random_effects.csv", row.names=FALSE)
write.csv(sl, "outputs/ml_implied_slopes.csv", row.names=FALSE)

cat("\n--- Random effects + ICC (M1) ---\n")
re$ICC <- round(re$sd_intercept^2 / (re$sd_intercept^2 + re$sd_resid^2), 3)
print(re, row.names=FALSE)

cat("\n--- Implied WITHIN-country slope of democratic-rights by content of nationhood (M2) ---\n")
print(sl, row.names=FALSE)
cat("(civic = -1SD ascriptive content; ethnic = +1SD. Reversal if civic<<0 and ethnic>=0.)\n")

cat("\n--- KEY fixed effects: cross-level interactions (M3 horse race) ---\n")
key <- fe[fe$model=="M3" & fe$term %in% c("dr_cwc","dr_cwc:z_content","dr_cwc:z_liberal"), ]
print(key, row.names=FALSE)

# ---- PERFORMANCE models ("two faces"): performance travels with pride, not against exclusion the same way ----
cat("\n=== PERFORMANCE models (democracy works today, within-country) ===\n")
perf_fe <- list()
for (o in c("national_pride_non_democracy","anti_immigrant_exclusion","national_superiority","ascriptive_membership","civic_membership")) {
  d$Y <- d[[o]]
  mp <- tryCatch(lmer(Y ~ perf_cwc + perf_cm_c + age_z + female + edu_z + lr + (1 + perf_cwc | country_code),
                      data=d, control=ctrl, REML=FALSE), error=function(e) NULL)
  if (!is.null(mp)) {
    cf <- extract_fe(mp, o, "perf"); perf_fe[[o]] <- cf
    row <- cf[cf$term=="perf_cwc", ]
    cat(sprintf("  %-30s perf_cwc beta = %+.3f (p=%.2g)\n", o, row$est, row$p))
  }
}
write.csv(do.call(rbind, perf_fe), "outputs/ml_performance_fixed_effects.csv", row.names=FALSE)
cat("\nNOTE: pride_democracy is EXCLUDED as a performance outcome (tautological with the predictor).\n")
