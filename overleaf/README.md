# Democracy and Nationalism, Reconsidered — manuscript source

LaTeX source for the JOP short article. This folder is a git submodule of the
research repository and is linked to the Overleaf project, so edits sync both
ways: locally via the helper scripts below, and in the Overleaf web editor.

## Documents

This project holds three compilable documents. In the Overleaf web editor, set
the **Main document** selector to whichever one you are compiling.

- `main.tex` — main text (`\input`s `preamble.tex` and `note_body.tex`)
- `si.tex` — supplementary information (`\input`s `preamble.tex` and `si_body.tex`)
- `title_page.tex` — non-anonymous title page (compile on its own)

`references.bib` is the shared bibliography; figures live in `figures/`.

## Local build

    make all        # -> out/main.pdf, out/si.pdf   (latexmk + bibtex, apsr style)
    make main       # main text only
    make si         # SI only
    make clean

## Sync (run from the research-repo root, one level up)

    ./push-overleaf.sh   # commit local edits and push them to Overleaf
    ./pull-overleaf.sh   # pull Overleaf edits back into this folder

Build artifacts (`out/`, `*.aux`, `*.pdf`, …) are gitignored and never pushed.
