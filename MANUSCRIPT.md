# Manuscript workflow

This file is the contract for how work is recorded.  It is the first thing to
read after `README.md`, and the thing to re-read when you are unsure where
something belongs.

The manuscript is the single source of truth.  There is no notes directory and
no separate memory store: a fact worth keeping is written into `tex/`, where
the checks can see it and a reader can find it.  If a fact fits nowhere below,
that is a sign it is not yet a fact.

## The three editions

The project has one mathematical source of truth and three reader views:

| entry point | purpose | drafting keys |
| --- | --- | --- |
| `tex/editions/scaffold-results.tex` | established statements and their proofs | hidden |
| `tex/editions/scaffold-routes.tex` | live targets, partial route lemmas, failures, and audit | shown |
| `tex/editions/scaffold-full.tex` | complete working record, including the archive | shown |

Each is built in two variants, so there are six PDFs:

| | |
| --- | --- |
| `output/pdf/plain/` | the first use of each term in each module is linked |
| `output/pdf/linked/` | every safe occurrence is linked |

The file names are the same in both directories, so a reader switches variant
by changing one directory in the path, and the cross-document links follow: a
link in `plain/scaffold-routes.pdf` opens `plain/scaffold-results.pdf`, and the
same link in `linked/scaffold-routes.pdf` opens `linked/scaffold-results.pdf`.

The three `*-linked.tex` wrappers exist only to set `\SCAFFOLDLinkAll` before
inputting the entry point of the same name; they are not separate manuscripts.
These six are the only supported entry points.  Every path inside them is
relative to the repository root, and `latexmk` runs from there, so an entry
point may be moved only together with the Makefile rule that names it.

`tex/standalone/` is for documents that are *not* views of the manuscript — a
self-contained paper for a referee, an extended abstract — with their own
preamble, sharing no source with the editions.  They are built by their own
Makefile rule, deliberately outside `make all`, and their PDFs go in
`output/standalone/`, which unlike `output/pdf/` is tracked: that is the
artefact you send to a person.

## Where an update belongs

1. A statement with a complete proof goes in `tex/results/`.
2. A sufficient but unproved target, or machinery developed specifically for
   one, goes in `tex/routes/`.
3. A refuted target **stays in `tex/routes/`**, marked closed, so that its
   counterexample and its precise failure mode remain next to the programme
   they belong to and remain searchable.
4. A superseded proof, or a detailed record no longer worth a reader's time,
   goes in `tex/archive/`.  The archive appears only in the full edition.
5. Update the route table in `tex/routes/00-status-map.tex` — once.  Do not
   repeat status prose in abstracts, introductions and computation notes; when
   status lives in four places, three of them go stale.
6. Add the module to the appropriate manifest.  The full manifest must include
   every mathematical module exactly once, and `make check` enforces it.

A result is **promoted** by moving its source from route ownership to result
ownership and updating the manifests; its label should normally stay unchanged,
so that everything already pointing at it keeps working.

The results edition may not refer to route- or archive-owned labels.  The
routes edition imports established labels from the results auxiliary file.
This acyclic dependency is checked automatically, and it is the reason the
Makefile builds the results edition first.

### What "proved" means here

A statement may sit in `tex/results/` when its proof is complete and checkable
by a reader — every step either written out or a citation to a named published
result.  Formalization in Lean is not required for that, and a Lean proof is
not a substitute for a readable one.

A computational claim is complete when it names the program, the exact command
that reproduces it, and the retained log; and when the program exits non-zero
on failure so that the claim can be re-checked without a human reading output.
`tools/README.md` states this as a rule for the toolkit.

Anything short of that belongs in `tex/routes/`, phrased as a `prob`
environment, not as a theorem with a gap.

## Terminology and notation

`tex/glossary.tex` is the single source of truth for terminology, and all three
editions include it after the table of contents.  It holds two tables: terms,
and notation.  Every row states the meaning in one line and points at the place
the term is properly defined, by an ordinary `\ref`, so that in the companion
editions the pointer links into the results PDF through `xr-hyper`.

Marking up a term takes two macros.  Write `\dfn{goldbach-pair}` at the single
place the term is defined; it typesets exactly as the `\emph` it replaces, and
plants the anchor.  Write `\term{goldbach-pair}` at the first use in every
*other* module; it renders as a link to the glossary row.  Use
`\dfnas`/`\termas` when the printed form differs from the key (plurals,
symbols, inflections).  Marking every occurrence is not wanted: one link per
module is enough to get the reader to the definition, and more turns the prose
blue.

A term earns a glossary row when a second module starts using it.  Terminology
confined to one module stays where it is, its definition always a few lines
from every use, and is recorded in `tools/local-terms.txt` instead.  Promote it
by adding the row and turning the `\emph` into a `\dfn`.

Rows come in two kinds.  `\gkey` names a term the body defines, and must be
matched by exactly one `\dfn`.  `\gkeyx` names one the glossary itself defines,
for the synonyms, method names and imported notions the text uses without ever
stopping to introduce them; it must have no `\dfn`.  Reach for `\gkeyx` rather
than forcing an italic definition into the middle of a proof.

"Standard" is a property of an audience, not of a term.  Decide who the readers
are and give a row to everything outside *their* everyday vocabulary, including
notions that are textbook somewhere else.

A row whose pointer is a companion-owned label must be gated, or the results
edition fails on an undefined reference:

| where the pointer's label lives | wrapper |
| --- | --- |
| `tex/results/` | none |
| `tex/routes/` or `tex/archive/` | `\ifdefined\SCAFFOLDResultsView\else` … `\fi` |

A gated row must not be `\term`-linked from a results module: `\hyperlink` to a
missing target fails silently, so nothing but `make check` would catch it.

Notation rows need no `\dfn`, because a symbol has nowhere to carry an anchor.
Add the row at the same time as the notation; this is the one part of the
convention that nothing can check for you.

`make check` enforces the rest:

- every `\term` lands on a glossary row, and every `\dfn` has one;
- no term is defined twice, and no row is duplicated;
- a `\gkey` row has a `\dfn`, and a `\gkeyx` row does not;
- a gated row is not linked from the results edition;
- every `\emph` in a content module is either a `\dfn` or listed in
  `tools/local-terms.txt`.

That last check is what keeps the glossary honest as the manuscript grows: a
newly emphasised term fails the build until it is either given a row or
acknowledged as local.  Run-in paragraph headers and `\emph` containing a
`\ref` are exempt automatically.

### The densely linked edition

`make linked` builds a second variant of each edition, in which *every* safe
occurrence of a term is clickable rather than just the first in each module.
It exists because a reader deep in a proof should not have to hunt backwards
for the one linked occurrence.

Nothing under `tex/` changes.  `tools/python/link_all.py` writes a marked-up
copy of the tree into `build/linked-src/`, and the Makefile puts that ahead of
the real one on `TEXINPUTS`, so the sources stay readable and no occurrence has
to be maintained by hand.  Re-running the script is the only way to refresh it;
never write `\termx` yourself.

Two things make this safe rather than noisy:

* **Subsequent occurrences are linked but not coloured.**  `\termx` sets
  `linkcolor=.`, the current colour, so only first uses show as blue.  The
  linked pages are pixel-identical to their plain counterparts; they simply
  carry more link annotations.
* **Eligibility is deny-by-default.**  `tools/link-all-terms.txt` lists the
  terms whose every occurrence may be linked.  A term earns a place only when
  nearly all its occurrences really are the technical sense; sample them first.
  An ordinary English word pressed into technical service — *support*, *full*,
  *side*, *free* — should stay out.  `make check` verifies every key in that
  file has a glossary row.

What the checks cannot do is find vocabulary that was never emphasised in the
first place.  `python3 tools/python/undefined_terms.py` sweeps for exactly
that: coined compounds, and modifiers of the project's own nouns, that no
sentence in any edition defines.  Its output is candidates rather than a
verdict, so read the matches; then either add the glossary row, or record the
judgement in `tools/terms-reviewed.txt`, which the sweep excludes on later
runs.

## Build and verify

```sh
make all       # all six PDFs, then the reference, ownership and glossary checks
make plain     # the three first-use-linked PDFs
make linked    # the three densely linked PDFs
make results   # both variants of one edition
make routes    # both variants; builds the results edition first
make full
make check     # the checks alone (needs the PDFs)
make tools     # build the C++ toolkit
make audit     # the fast computational self-checks
make formal    # lake build (opt-in; see README.md)
```

Release PDFs are copied to `output/pdf/plain/` and `output/pdf/linked/`;
intermediate files stay under `build/`, with the generated marked-up sources in
`build/linked-src/`.  None of that is tracked: the six edition PDFs are build
products, and a fresh checkout has no `output/pdf/` until you run `make all`.
Tracking them costs roughly a megabyte of history per rebuild, which will
dominate a text repository within months.
