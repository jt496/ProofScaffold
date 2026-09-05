---
description: Record a refuted route with its counterexample, keeping it searchable
argument-hint: <label or route name>
---

Record that the route `$1` is dead. Do not delete it — a deleted route gets
attempted again.

1. Keep the material in `tex/routes/`, and rewrite its section so that the
   heading says it is closed and the first paragraph says what killed it.
2. State the counterexample as a `prop` with an exact, checkable witness. If
   the witness came from a computation, it needs a program under `tools/` that
   reproduces it, an exact command, a retained log in `tools/logs/`, and a
   non-zero exit status on failure. Add all four; a witness that only exists in
   the conversation is not a record.
3. Say, in one paragraph, *why* it fails — the structural reason, not the
   arithmetic of the example — and what survives: the corrected hypothesis, the
   narrower range, or nothing.
4. Update the row in `tex/routes/00-status-map.tex` to `closed by
   Proposition~\ref{...}`. Once, and nowhere else.
5. Write a note in `notes/` if the failure rules out more than this one route:
   one file, frontmatter as in the existing notes, `**Why:**` and
   `**How to apply:**` lines, and an index line in `notes/MEMORY.md`. This is
   the most valuable artefact of a dead route.

Finish with `make all` and, if you added a program, `make audit`.
