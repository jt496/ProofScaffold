---
description: Report where the proof search stands, from the maintained sources only
---

Report the current state of the project. Use only the maintained sources, in
this order, and say plainly when they disagree:

1. `tex/routes/00-status-map.tex` — the route table. This is the only place
   status is asserted; treat it as authoritative.
2. `tex/manifests/results.tex` — what is actually proved, module by module.
3. `notes/MEMORY.md` and the notes it indexes — what is known to be dead.
4. `formal/BLUEPRINT.md` — the Coverage table, if `formal/` is in use.
5. `git log --oneline -20` — what has moved recently.

Then give:

- a one-paragraph statement of where the problem stands;
- the open routes in priority order, each with the single sentence that says
  what would close it;
- anything you noticed that is stale — a route table row contradicted by the
  results manifest, a note superseded by the paper, a Coverage row for a
  theorem that no longer exists.

Do not run a build and do not change any file.
