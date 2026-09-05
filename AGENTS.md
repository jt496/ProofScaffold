# Working in this repository

This is a long-running proof search.  Most of the work is done by AI agents
under human supervision, so the value of the repository is not the text alone
but the *record*: what is proved, what is being attempted, and what has already
failed and why.  A change that improves the mathematics but degrades the record
is a bad change.

Read `MANUSCRIPT.md` before your first edit.  It is the contract; this file is
how to work within it.

## At the start of a session

1. `tex/routes/00-status-map.tex` — the only maintained statement of where the
   problem stands.  Everything else describing status is out of date by
   construction.
2. `notes/MEMORY.md` and the notes it indexes — the obituaries for approaches
   that provably cannot work.  These are the most valuable files here.  Reading
   them is what stops the search from cycling.
3. `formal/BLUEPRINT.md` if you will touch Lean.

## The rules that matter

**Never assert more than you have.**  A statement enters `tex/results/` only
when its proof is complete and a reader could check every step.  A target you
believe is a `prob` environment in `tex/routes/`, not a theorem with a gap and
not a lemma whose proof says "similarly".  If you are unsure which side of the
line something falls on, it is a route.

**A computational claim names its program, its exact command, and its log.**
The program exits non-zero on failure and prints a final pass/fail line.  A
claim backed by a computation you ran but did not commit is not a claim.
Numerical evidence for an unproved statement is evidence — say so in those
words, and keep it in the companion.

**A refuted route is not deleted.**  It stays in `tex/routes/`, marked closed,
with the exact counterexample and the reason it fails.  Deleting it guarantees
that someone — quite possibly you, three months from now — tries it again.  Add
a note in `notes/` too when the failure is structural rather than incidental.

**Status is asserted in exactly one place**, the route table.  Do not restate
it in an abstract, an introduction, or a computational remark.

**Do not edit generated files.**  `build/` and `build/linked-src/` are outputs;
never hand-write `\termx`.  Re-run `tools/python/link_all.py`.

**Do not recreate a retired entry point.**  The six editions are the only
supported manuscripts.  Old assembly or migration scripts under `tools/`, if
any, are historical aids and must never be used to regenerate one.

**Preserve labels when promoting.**  Moving a statement from routes to results
keeps its label, so everything already pointing at it keeps working.

## Before you say you are done

```sh
make all          # six PDFs + reference, ownership and glossary checks
make audit        # if you touched tools/
lake build        # if you touched formal/  (see README.md; opt-in)
```

`make all` failing is not a nuisance to be worked around: every check in it
exists because the corresponding mistake was made once and cost real time.  In
particular, a `\emph` that is neither a `\dfn` nor listed in
`tools/local-terms.txt` fails the build on purpose.

## Reporting back

The supervisor needs to know which of three things happened, and the words are
not interchangeable:

* **proved** — the proof is written out in `tex/results/` and it is complete;
* **verified** — a computation checked a finite range, and here is the command;
* **believed** — it looks true, the evidence is *X*, and it is in the companion
  as a `prob`.

Say which. If a proof has a gap, say where the gap is, in one sentence, rather
than presenting the argument as finished and leaving the gap to be discovered.
If a route died, say what killed it — that is a result, and it is often the
most useful thing a session produces.

## Notes and memory

`notes/` mirrors the agent's persistent memory: one fact or route per file,
linked by `[[wiki-style]]` name, indexed in `notes/MEMORY.md`.  Write a note
when you learn something that is *not* recoverable from the manuscript or the
git history — why an approach cannot work, what a computation ruled out, which
reformulation turned out to be equivalent.  Do not write notes that restate the
paper.

## Git

Small commits, one idea each.  Say what changed and why in the message, not
just which files.  Do not rewrite published history, and do not push unless
asked.
