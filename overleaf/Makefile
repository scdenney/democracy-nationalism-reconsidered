# Build. `make all` -> de-anonymized working paper (out/). `make anon` -> anonymous
# JOP submission (out-anon/manuscript_with_SI.pdf). latexmk runs pdflatex + bibtex
# (apsr) and reruns until references resolve.
LATEXMK = latexmk -pdf -bibtex -interaction=nonstopmode -halt-on-error -outdir=out

.PHONY: all main si anon clean
all: main si

# De-anonymized build (default): ensure the anon sentinel is absent.
main:
	rm -f .anon
	$(LATEXMK) main.tex

si:
	rm -f .anon
	$(LATEXMK) si.tex

# Anonymous JOP build: the .anon sentinel flips \anontrue in preamble.tex, masking
# author, self-citation, and the replication URL. Outputs to out-anon/ so the
# de-anon out/ is never clobbered. The sentinel is always removed afterward.
anon:
	touch .anon
	-latexmk -pdf -bibtex -interaction=nonstopmode -halt-on-error -outdir=out-anon main.tex
	-latexmk -pdf -bibtex -interaction=nonstopmode -halt-on-error -outdir=out-anon si.tex
	rm -f .anon
	pdfunite out-anon/main.pdf out-anon/si.pdf out-anon/manuscript_with_SI.pdf
	@echo "Anonymous JOP build -> out-anon/manuscript_with_SI.pdf"

clean:
	rm -f .anon
	latexmk -C -outdir=out main.tex si.tex 2>/dev/null || true
	latexmk -C -outdir=out-anon main.tex si.tex 2>/dev/null || true
	rm -f out/*.bbl out/*.aux out/*.blg out-anon/*.bbl out-anon/*.aux out-anon/*.blg
