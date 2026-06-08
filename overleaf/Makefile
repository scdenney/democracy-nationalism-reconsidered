# JOP submission build. `make` builds both PDFs into out/.
# latexmk runs pdflatex + bibtex (apsr) + reruns until references resolve.
LATEXMK = latexmk -pdf -bibtex -interaction=nonstopmode -halt-on-error -outdir=out

.PHONY: all main si clean
all: main si

main:
	$(LATEXMK) main.tex

si:
	$(LATEXMK) si.tex

clean:
	latexmk -C -outdir=out main.tex si.tex 2>/dev/null || true
	rm -f out/*.bbl out/*.aux out/*.blg
