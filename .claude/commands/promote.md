---
description: Promote a proved statement from the routes companion to the results edition
argument-hint: <label>, e.g. reflect:lem
---

Promote the statement labelled `$1` from route ownership to result ownership.

Before moving anything, check that the proof really is complete: every step
either written out or a citation to a named published result. If it is not,
stop and say exactly which step is missing — a promotion is the one operation
in this repository that is expensive to reverse, because everything downstream
starts trusting the statement.

Then:

1. Move the statement and its proof into the appropriate module under
   `tex/results/`, creating the module if the material does not belong with
   anything already there. **Keep the label unchanged** so existing references
   keep working.
2. Remove it from `tex/routes/`, leaving behind whatever route context still
   makes sense without it.
3. Update `tex/manifests/results.tex` and `tex/manifests/archive.tex` if a
   module was added.
4. Check that the new results module refers to no route- or archive-owned
   label. If it does, either promote that too or restate what is needed.
5. Update the route table in `tex/routes/00-status-map.tex` — the row for the
   programme this came from, once. Do not add status prose anywhere else.
6. Move any glossary row that pointed at the old location, and ungate it if it
   was gated out of the results edition.
7. If it is formalized, update the Coverage row in `formal/BLUEPRINT.md`.

Finish with `make all` and report the result. If it fails, fix it; the checks
exist to catch exactly the mistakes this operation makes.
