# Research notes

> **Status warning.**  These files are dated research snapshots, not the
> maintained account of what is open.  The canonical status is the table in
> `tex/routes/00-status-map.tex`, rendered at the front of
> `output/pdf/plain/scaffold-routes.pdf`.  Where a note and the manuscript
> disagree, the manuscript wins.

Working notes kept alongside the manuscript, one fact or route per file.  They
record *why* the paper is shaped the way it is: which reductions were tried,
which were proved, and which are dead.  Several will be obituaries for
approaches that provably cannot work — those are the most useful ones, since
they say what not to try again.

These are a mirror of the agent's persistent memory for this project.  For
Claude Code the live copy sits under

```sh
~/.claude/projects/<escaped-path-to-this-repo>/memory/
```

and is refreshed into the repository with

```sh
cp ~/.claude/projects/<escaped-path-to-this-repo>/memory/*.md notes/
```

Run that before a commit that ends a session's work, so the reasoning survives
outside one machine's home directory.  `MEMORY.md` is the index loaded at the
start of each session; links inside the files are double-bracket wiki style and
refer to each other by filename.

## What belongs here

A note earns its place when it records something **not recoverable from the
manuscript or the git history**:

* why an approach cannot work, stated sharply enough to stop a repeat attempt;
* what a computation ruled out, and over what range;
* that two formulations are equivalent, and which direction was the hard one;
* a judgement call about scope or notation, and the reason for it.

Not: a restatement of a published lemma, a summary of the paper, or a diary.

## Index

| note | what it says |
| --- | --- |
| [goldbach-distinct-refuted.md](goldbach-distinct-refuted.md) | The distinct-primes strengthening fails at 4 and 6 only, and no sieve-theoretic route could have seen it. |
