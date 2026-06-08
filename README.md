# Democracy and Nationalism, Reconsidered

Public working-paper and replication repository for the short article *"Democracy and Nationalism, Reconsidered."*

The paper disaggregates "democracy" and "nationalism" and asks when commitment to democracy is actually antagonistic to nationalism. Using the 2023 ISSP National Identity module (29 countries) and V-Dem v15, it shows that endorsement of liberal-democratic *rights* restrains *exclusionary* nationalism but leaves national pride alone, and — the central claim — that this restraint is conditioned by the civic-versus-ethnic **content of nationhood**, not by the liberal quality of institutions. The relationship is strong where the nation is imagined in largely civic terms and disappears in East Asian democracies that are institutionally liberal yet ethnically defined.

**Manuscript status:** Working paper under review.

## Repository layout

```
democracy_nationalism_reconsidered/
├── README.md                              # this file
├── paper/                                 # compiled public-facing PDFs
│   ├── democracy-nationalism-reconsidered.pdf
│   ├── democracy-nationalism-reconsidered-si.pdf
│   └── democracy-nationalism-reconsidered-with-si.pdf
├── overleaf/                              # manuscript LaTeX source
│   ├── main.tex, note_body.tex            # main text
│   ├── si.tex, si_body.tex                # supplementary information
│   ├── preamble.tex, references.bib       # shared preamble + bibliography
│   ├── figures/                           # manuscript figures (PNG)
│   └── Makefile                           # `make all` -> out/main.pdf, out/si.pdf
├── replication/                           # self-contained replication package
│   ├── master.sh                          # one-command pipeline (9 steps)
│   ├── code/                              # Python + R analysis scripts
│   ├── outputs/                           # generated CSVs
│   ├── figures/                           # generated PNGs
│   ├── docs/crosswalk.md, codebook.md     # figure/table -> script map; variable defs
│   └── data/README.md                     # data-access instructions (not redistributed)
├── literature_evidence_map.md             # literature / evidence map
└── substack_post_democracy_nationalism.md # public-facing write-up
```

## Data

Neither input is redistributed here.

- **ISSP 2023 — National Identity & Citizenship**, GESIS `ZA10010` v1.0.0 (and earlier waves `ZA2880`/`ZA3910`/`ZA5950` for the longitudinal appendix). Free after GESIS registration.
- **V-Dem v15** via the `vdemdata` R package.

The ISSP microdata are not stored in this project. Point the scripts at your local copy by setting `ISSP_DIR` to the absolute path of the `ISSP (1995-2023)/` folder, e.g.

```bash
export ISSP_DIR="/Users/scdenney/Documents/github/research/sandbox/national_identity_survey_data/ISSP (1995-2023)"
```

See `replication/data/README.md` for the expected per-wave layout.

## Build

```bash
# manuscript
cd overleaf && make all                 # -> out/main.pdf (15 pp), out/si.pdf (23 pp)

# reproduce every CSV and figure (needs ISSP_DIR set; see above)
cd replication && bash master.sh
```

## License

Code is released for replication (`replication/LICENSE`). The ISSP and V-Dem inputs are governed by their providers' terms.
