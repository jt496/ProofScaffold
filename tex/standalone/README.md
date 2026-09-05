# Standalone documents

Documents that are **not** views of the manuscript: a self-contained paper for
a referee, an extended abstract, a talk handout.  Each has its own preamble and
class and shares no source with the three editions — that is the point, and it
is why they are kept apart from `tex/results/`, `tex/routes/` and
`tex/archive/`, which `make check` treats as the mathematical record.

A standalone document gets its own rule in the Makefile (there is a commented
example there), and is deliberately outside `make all`, so its PDF changes only
when you rebuild it on purpose.  Its output goes to `output/standalone/`, which
unlike `output/pdf/` **is** tracked: that is the artefact you send to a person,
and it should be the same bytes they received.
