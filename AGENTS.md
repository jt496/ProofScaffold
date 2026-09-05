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
2. the closed routes in `tex/routes/`, and the computational audit in
   `tex/archive/` — the obituaries for approaches that provably cannot work.
   These are the most valuable prose in the project.  Reading them is what
   stops the search from cycling.
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
the structural reason to `tex/archive/40-computations.tex` when the failure
rules out more than the one route.

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

## The manuscript is the single source of truth

There is no notes directory, no scratch file, and no parallel memory store in
this repository, and you should not create one.  When you learn something worth
keeping — why an approach cannot work, what a computation ruled out, which
reformulation turned out to be equivalent — write it into the manuscript: a
closed route in `tex/routes/`, or the computational audit in
`tex/archive/40-computations.tex`.

This is not tidiness.  A side store always begins as the convenient place to
put a fact that does not yet fit, and ends as a stale copy that contradicts the
paper without anything noticing: `make check` cannot see it, a reader will not
find it, and the version in the paper and the version in the note drift until
nobody knows which is current.  If a fact does not fit anywhere in `tex/`, that
is evidence it is not yet a fact — say so in the session summary instead.

Your own cross-session memory, if you have one, is a different thing and is
yours to keep.  Do not mirror it into the repository.

## Committing and pushing

You may be left running for hours or days with nobody watching. The commit
history is how your supervisor follows that from somewhere else, so it has to
be readable *as it happens*, not reconstructed at the end.

**Commit when a unit of work is complete and the checks pass** — not on a
timer, and not once at the end of a long session. A unit is one of:

* a statement written up with its proof, and the manifests updated;
* a route advanced, a target restated, or a reduction recorded;
* a refutation, together with its witness, its program and its retained log;
* a Lean module and its `Tests/` module, building clean, with the blueprint
  row;
* a tool, together with the log of the run it was written for.

**Push after every commit.** Work that has not left the machine does not exist
as far as anyone else is concerned, and the point of pushing continuously is
that the run can be followed, and picked up, from somewhere else. If a push
fails, stop and say so in your next message: do not keep piling commits on top
of work that is not leaving the machine.

**Never commit a tree that does not build.** Run `make all` first. The
`pre-push` hook runs it again and refuses the push if it fails, but do not use
the hook as the check — by then you have already written the commit message.

**There are no work-in-progress commits here, and you never need one.**
Incomplete work has a legitimate home: an argument that is not finished is a
route, not a broken result. Write the partial argument into `tex/routes/`,
honestly labelled as far as it goes, and commit that. It is a real
contribution, it builds, and it says something true. Committing a half-written
proof into `tex/results/` to save progress is the one thing that corrupts the
record, because the results edition is meant to be the part a reader can trust
without checking.

**Before a long computation, commit first.** Commit the program and the exact
command you are about to run, then commit the log when it finishes. If the run
dies, or you do, the record of what was attempted survives.

**Commit before switching approach.** When you abandon a line of attack, that
is a commit — even when the outcome is negative, and especially then.

**Do not batch a day's work into one commit.** The order in which things were
tried, and what was known when, is part of the record. A single enormous commit
at the end throws it away.

Write the message so it says what changed and why, not which files changed —
`git diff` already knows the files. Do not rewrite published history.
