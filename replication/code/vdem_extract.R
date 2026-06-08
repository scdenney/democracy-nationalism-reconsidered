#!/usr/bin/env Rscript
# Extract V-Dem indices for the 29 ISSP 2023 countries, year 2023.
# Theoretically central contrast: liberal component (v2x_liberal) vs electoral
# component (v2x_polyarchy) as moderators of the democratic-rights <-> nationalism slope.
suppressMessages(library(vdemdata))

iso3 <- c("AUS","AUT","CAN","TWN","HRV","DNK","FIN","FRA","DEU","GRC","HUN","IND",
          "ISR","ITA","KOR","LTU","MEX","NLD","NZL","NOR","PHL","RUS","SVK","SVN",
          "ZAF","SWE","CHE","THA","USA")
# ISSP numeric country codes, aligned to iso3 above
issp_code <- c(36,40,124,158,191,208,246,250,276,300,348,356,
               376,380,410,440,484,528,554,578,608,643,703,705,
               710,752,756,764,840)

cat("vdemdata version of bundled dataset; max year:", max(vdem$year), "\n")
vars <- c("country_name","country_text_id","year",
          "v2x_polyarchy","v2x_liberal","v2x_libdem","v2x_partipdem",
          "v2x_regime","v2x_regime_amb")
have <- vars[vars %in% names(vdem)]
miss <- setdiff(vars, names(vdem))
if (length(miss)) cat("MISSING vars:", paste(miss, collapse=", "), "\n")

d <- vdem[vdem$year == 2023 & vdem$country_text_id %in% iso3, have]
# order to match iso3 and attach ISSP code
d <- d[match(iso3, d$country_text_id), ]
d$issp_code <- issp_code
# any country not matched?
cat("Unmatched ISO3:", paste(iso3[is.na(d$country_name)], collapse=", "), "\n\n")

# RoW labels
row_lab <- c("0"="Closed autocracy","1"="Electoral autocracy",
             "2"="Electoral democracy","3"="Liberal democracy")
d$row_2023 <- row_lab[as.character(d$v2x_regime)]

num <- sapply(d[,c("v2x_polyarchy","v2x_liberal","v2x_libdem","v2x_partipdem")], as.numeric)
d[,c("v2x_polyarchy","v2x_liberal","v2x_libdem","v2x_partipdem")] <- round(num, 3)

d <- d[order(-d$v2x_libdem), c("issp_code","country_name","country_text_id",
        "v2x_regime","row_2023","v2x_polyarchy","v2x_liberal","v2x_libdem","v2x_partipdem")]
print(d, row.names = FALSE)

write.csv(d, "outputs/vdem_2023_issp.csv", row.names = FALSE)
cat("\nwrote outputs/vdem_2023_issp.csv (n=", nrow(d), ")\n", sep="")
# quick: correlation of the two component indices across these 29 (collinearity check)
cat("cor(polyarchy, liberal) across 29:",
    round(cor(d$v2x_polyarchy, d$v2x_liberal, use="complete.obs"), 3), "\n")
