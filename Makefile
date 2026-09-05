# ---------------------------------------------------------------------------
# Project build.  See MANUSCRIPT.md for what the three editions are and where
# an update belongs; see README.md for first-time setup.
#
#   make init        name the project (rewrites the SCAFFOLD/scaffold placeholders)
#   make all         the six PDFs, then every consistency check
#   make check       the consistency checks alone (needs the PDFs)
#   make tools       build the C++ toolkit
#   make audit       run the fast computational self-checks
#   make formal      lake build (opt-in; see README.md)
#   make clean       remove build products
# ---------------------------------------------------------------------------
SLUG    := scaffold
LATEXMK ?= latexmk
PYTHON  ?= python3
LATEX_FLAGS := -pdf -interaction=nonstopmode -halt-on-error -file-line-error

TEX_SOURCES := $(shell find tex -type f -name '*.tex' -not -path 'tex/standalone/*' -print)

# Each of the three editions is built twice.  The plain variant links the first
# use of a glossary term in each module; the linked variant links every safe
# occurrence, and is built from a generated copy of tex/ so that the real
# sources carry no extra markup.  See MANUSCRIPT.md.
LINKED_SRC   := build/linked-src
LINKED_STAMP := $(LINKED_SRC)/.generated

EDITIONS := results routes full
PLAIN    := $(foreach e,$(EDITIONS),output/pdf/plain/$(SLUG)-$(e).pdf)
LINKED   := $(foreach e,$(EDITIONS),output/pdf/linked/$(SLUG)-$(e).pdf)

.PHONY: all plain linked results routes full formal check tools audit init clean

all: plain linked check

plain:  $(PLAIN)
linked: $(LINKED)

results: output/pdf/plain/$(SLUG)-results.pdf output/pdf/linked/$(SLUG)-results.pdf
routes:  output/pdf/plain/$(SLUG)-routes.pdf  output/pdf/linked/$(SLUG)-routes.pdf
full:    output/pdf/plain/$(SLUG)-full.pdf    output/pdf/linked/$(SLUG)-full.pdf

# ---------------------------------------------------------------------------
# Plain variants.  The routes edition imports labels from the results auxiliary
# through xr-hyper, so it must be built after it.
# ---------------------------------------------------------------------------
build/plain/results/$(SLUG)-results.pdf: tex/editions/$(SLUG)-results.tex $(TEX_SOURCES)
	mkdir -p build/plain/results
	$(LATEXMK) $(LATEX_FLAGS) -outdir=build/plain/results tex/editions/$(SLUG)-results.tex

build/plain/routes/$(SLUG)-routes.pdf: tex/editions/$(SLUG)-routes.tex $(TEX_SOURCES) \
                                       build/plain/results/$(SLUG)-results.pdf
	mkdir -p build/plain/routes
	$(LATEXMK) $(LATEX_FLAGS) -outdir=build/plain/routes tex/editions/$(SLUG)-routes.tex

build/plain/full/$(SLUG)-full.pdf: tex/editions/$(SLUG)-full.tex $(TEX_SOURCES)
	mkdir -p build/plain/full
	$(LATEXMK) $(LATEX_FLAGS) -outdir=build/plain/full tex/editions/$(SLUG)-full.tex

# ---------------------------------------------------------------------------
# Linked variants.  link_all.py writes a marked-up copy of tex/ into
# $(LINKED_SRC); TEXINPUTS puts it ahead of the real tree, so \input{tex/...}
# resolves there.  The working directory stays the repository root, which keeps
# the \externaldocument path in the preamble valid.
# ---------------------------------------------------------------------------
$(LINKED_STAMP): $(TEX_SOURCES) tools/link-all-terms.txt tools/python/link_all.py
	$(PYTHON) tools/python/link_all.py $(LINKED_SRC)
	touch $@

build/linked/results/$(SLUG)-results-linked.pdf: tex/editions/$(SLUG)-results-linked.tex \
                                                 tex/editions/$(SLUG)-results.tex $(LINKED_STAMP)
	mkdir -p build/linked/results
	TEXINPUTS=$(LINKED_SRC):$$TEXINPUTS $(LATEXMK) $(LATEX_FLAGS) \
	    -outdir=build/linked/results tex/editions/$(SLUG)-results-linked.tex

build/linked/routes/$(SLUG)-routes-linked.pdf: tex/editions/$(SLUG)-routes-linked.tex \
        tex/editions/$(SLUG)-routes.tex $(LINKED_STAMP) \
        build/linked/results/$(SLUG)-results-linked.pdf
	mkdir -p build/linked/routes
	TEXINPUTS=$(LINKED_SRC):$$TEXINPUTS $(LATEXMK) $(LATEX_FLAGS) \
	    -outdir=build/linked/routes tex/editions/$(SLUG)-routes-linked.tex

build/linked/full/$(SLUG)-full-linked.pdf: tex/editions/$(SLUG)-full-linked.tex \
                                           tex/editions/$(SLUG)-full.tex $(LINKED_STAMP)
	mkdir -p build/linked/full
	TEXINPUTS=$(LINKED_SRC):$$TEXINPUTS $(LATEXMK) $(LATEX_FLAGS) \
	    -outdir=build/linked/full tex/editions/$(SLUG)-full-linked.tex

# ---------------------------------------------------------------------------
# Release copies.  Both variants keep the same file names, so a reader switches
# between them by changing one directory in the path, and cross-document links
# follow.
# ---------------------------------------------------------------------------
# One pair of rules per edition.  Written out rather than generated, so that
# `make -n` and an error message both name real files.
define release_rules
output/pdf/plain/$(SLUG)-$(1).pdf: build/plain/$(1)/$(SLUG)-$(1).pdf
	mkdir -p output/pdf/plain
	cp $$< $$@

output/pdf/linked/$(SLUG)-$(1).pdf: build/linked/$(1)/$(SLUG)-$(1)-linked.pdf
	mkdir -p output/pdf/linked
	cp $$< $$@
endef
$(foreach e,$(EDITIONS),$(eval $(call release_rules,$(e))))

# ---------------------------------------------------------------------------
# Checks.  `check` needs the PDFs, because it greps the LaTeX logs for
# unresolved references that latexmk itself reports only as a warning.
# ---------------------------------------------------------------------------
check: $(PLAIN) $(LINKED)
	perl tools/check_manuscript.pl
	@if grep -nE "undefined references|multiply defined|There were undefined" \
	      build/plain/*/*.log build/linked/*/*.log; then \
		echo "LaTeX reference check failed"; exit 1; \
	fi
	@echo "LaTeX reference check passes"

# ---------------------------------------------------------------------------
# Standalone documents.  Not views of the manuscript: own preamble, own class,
# no shared source.  Deliberately outside `make all`, and their PDFs ARE
# tracked, so they change only when rebuilt on purpose.  Uncomment and rename
# when you add one; see tex/standalone/README.md.
#
# .PHONY: extract
# extract: output/standalone/$(SLUG)-extract.pdf
#
# build/standalone/$(SLUG)-extract.pdf: tex/standalone/$(SLUG)-extract.tex
# 	mkdir -p build/standalone
# 	$(LATEXMK) $(LATEX_FLAGS) -outdir=build/standalone $<
#
# output/standalone/$(SLUG)-extract.pdf: build/standalone/$(SLUG)-extract.pdf
# 	mkdir -p output/standalone
# 	cp $< $@
# ---------------------------------------------------------------------------

tools:
	$(MAKE) -C tools/cpp

audit: tools
	tools/cpp/goldbach 100000
	$(PYTHON) tools/python/distinct_goldbach.py 100000
	$(PYTHON) tools/python/goldbach_counts.py 20000

formal:
	lake build

init:
	$(PYTHON) tools/init_project.py

clean:
	$(LATEXMK) -C -outdir=build/plain/results tex/editions/$(SLUG)-results.tex
	$(LATEXMK) -C -outdir=build/plain/routes  tex/editions/$(SLUG)-routes.tex
	$(LATEXMK) -C -outdir=build/plain/full    tex/editions/$(SLUG)-full.tex
	$(LATEXMK) -C -outdir=build/linked/results tex/editions/$(SLUG)-results-linked.tex
	$(LATEXMK) -C -outdir=build/linked/routes  tex/editions/$(SLUG)-routes-linked.tex
	$(LATEXMK) -C -outdir=build/linked/full    tex/editions/$(SLUG)-full-linked.tex
	$(MAKE) -C tools/cpp clean
	rm -rf build
