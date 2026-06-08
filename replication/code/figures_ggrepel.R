#!/usr/bin/env Rscript
# Country-level figures in ggplot2 + ggrepel (repelled labels with connector lines),
# colorblind-safe Okabe-Ito palette. Replaces the matplotlib fig1_moderation and
# fig2_random_slopes. Run from the package root (master.sh handles cwd).
suppressMessages({library(ggplot2); library(ggrepel); library(patchwork)})

OKABE <- c(
  "Western democracies"                  = "#0072B2",
  "Eastern Europe democracies"           = "#009E73",
  "Eastern Europe non-democracies"       = "#E69F00",
  "East Asian democracies"               = "#D55E00",
  "South/Southeast Asia non-democracies" = "#CC79A7",
  "Other democracies"                    = "#666666")
LAB <- c("Western democracies"="W. dem.","Eastern Europe democracies"="E. Eur. dem.",
         "Eastern Europe non-democracies"="E. Eur. non-dem.","East Asian democracies"="E. Asian dem.",
         "South/Southeast Asia non-democracies"="S/SE Asia non-dem.","Other democracies"="Other dem.")

sl <- read.csv("outputs/country_adjusted_slopes.csv", stringsAsFactors = FALSE)
cl <- read.csv("outputs/country_level.csv", stringsAsFactors = FALSE)
anti <- merge(
  sl[sl$predictor=="democracy_rights_liberal" & sl$outcome=="anti_immigrant_exclusion",
     c("country","region_regime","slope","se")],
  cl[,c("country_name","cm_ascriptive_membership","v2x_liberal")],
  by.x="country", by.y="country_name")
anti$region_regime <- factor(anti$region_regime, levels=names(OKABE))

base_theme <- theme_bw(base_size=11) +
  theme(panel.grid.minor=element_blank(), legend.position="bottom",
        legend.title=element_blank(), plot.title=element_text(size=11, face="plain"))

# No titles inside the figure: the title, the two panel correlations, and the panel
# descriptions live in the LaTeX caption. Panels carry only (A)/(B) tags.
mod_panel <- function(xvar, xlab) {
  ggplot(anti, aes(.data[[xvar]], slope, color=region_regime)) +
    geom_hline(yintercept=0, color="grey70", linewidth=0.4) +
    geom_smooth(method="lm", se=FALSE, color="grey25", linewidth=0.6, linetype="dashed",
                inherit.aes=FALSE, aes(.data[[xvar]], slope)) +
    geom_point(size=2.2) +
    geom_text_repel(aes(label=country), size=2.5, max.overlaps=Inf, min.segment.length=0,
                    segment.size=0.25, segment.color="grey60", show.legend=FALSE,
                    box.padding=0.3, seed=20260604) +
    scale_color_manual(values=OKABE) +
    labs(x=xlab, y="Adjusted within-country slope of\nanti-immigrant exclusion on democratic rights") +
    base_theme
}

pA <- mod_panel("cm_ascriptive_membership",
                "Ethnic content of nationhood (country-mean ascriptive; low = civic, high = ethnic)")
pB <- mod_panel("v2x_liberal", "Institutional liberalism (V-Dem liberal component, 2023)") + labs(y=NULL)

fig1 <- (pA | pB) + plot_layout(guides="collect") + plot_annotation(tag_levels="A", tag_prefix="(", tag_suffix=")")
fig1 <- fig1 & theme(legend.position="bottom", legend.text=element_text(size=9),
                     plot.tag=element_text(face="bold", size=12))
ggsave("figures/fig1_moderation.png", fig1, width=11.5, height=5.7, dpi=240, bg="white")

# Forest plot: per-country anti-immigrant slope, ordered, with 95% CI
anti$country <- reorder(anti$country, anti$slope)
fig2 <- ggplot(anti, aes(slope, country, color=region_regime)) +
  geom_vline(xintercept=0, color="grey40", linewidth=0.5) +
  geom_pointrange(aes(xmin=slope-1.96*se, xmax=slope+1.96*se), linewidth=0.5, size=0.35) +
  scale_color_manual(values=OKABE) +
  labs(x="Adjusted within-country slope of anti-immigrant exclusion on democratic rights",
       y=NULL) +
  base_theme + theme(axis.text.y=element_text(size=8), legend.position="right",
                     legend.text=element_text(size=9), legend.key.height=unit(1.1,"lines"))
ggsave("figures/fig2_random_slopes.png", fig2, width=9.6, height=7.5, dpi=240, bg="white")

# SI figure: country-level adjusted slopes for three outcomes, faceted (declutters
# the overlapping-series version). Countries share the anti-immigrant ordering.
outs <- c(anti_immigrant_exclusion="Anti-immigrant exclusion",
          ascriptive_membership="Ascriptive membership",
          national_pride_non_democracy="National pride")
si <- sl[sl$predictor=="democracy_rights_liberal" & sl$outcome %in% names(outs),
         c("country","region_regime","outcome","slope","se")]
si$region_regime <- factor(si$region_regime, levels=names(OKABE))
ord <- anti$country[order(anti$slope)]                       # anti-immigrant order
si$country <- factor(si$country, levels=as.character(ord))
si$outcome <- factor(outs[si$outcome], levels=outs)
figSI <- ggplot(si, aes(slope, country, color=region_regime)) +
  geom_vline(xintercept=0, color="grey40", linewidth=0.4) +
  geom_pointrange(aes(xmin=slope-1.96*se, xmax=slope+1.96*se), linewidth=0.4, size=0.28) +
  facet_wrap(~outcome, nrow=1) +
  scale_color_manual(values=OKABE) +
  labs(x="Adjusted within-country slope for democratic-rights endorsement", y=NULL) +
  base_theme + theme(axis.text.y=element_text(size=7),
                     strip.background=element_rect(fill="grey92", color=NA))
ggsave("figures/country_adjusted_democratic_rights_slopes.png", figSI,
       width=10.5, height=7.2, dpi=240, bg="white")

cat("wrote fig1_moderation.png, fig2_random_slopes.png, country_adjusted_democratic_rights_slopes.png\n")
cat("r(slope, content) =", round(cor(anti$cm_ascriptive_membership, anti$slope),3),
    "| r(slope, liberal) =", round(cor(anti$v2x_liberal, anti$slope),3), "\n")
