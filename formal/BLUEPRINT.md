# Lean blueprint

## Status and purpose

This document is the bridge between the manuscript and the Lean development.
It exists so that two questions always have an answer in one place:

* for a labelled statement in `tex/manifests/results.tex`, is it formalized,
  deliberately out of scope, or open?
* for a Lean name, which manuscript statement is it, and does it say the same
  thing?

Formalization is **not** the gate for a result entering the results edition; a
complete, checkable LaTeX proof is.  Lean is used where a proof is fiddly,
where a computation has to be trusted, or where a statement is load-bearing
enough that its exact form should be pinned against later edits.  The Coverage
table below is honest about what has not been done.

The current scope is the elementary theory of `tex/results/` and the initial
range of Theorem `verify:thm`.

## Conventions

* One `Results/` module per manuscript module, named after it.  One `Tests/`
  module per `Results/` module.
* The implementation is source-faithful but need not copy the order or
  packaging of the manuscript proof.  Where it departs, the departure is
  recorded under Deviations, not left for a reader to discover.
* Statements use subtraction-free natural-number forms internally where the
  manuscript divides or subtracts, and expose the manuscript's form at the
  boundary.  `isGoldbachNumber_iff` is the example.
* Every public theorem carries a docstring naming its manuscript label.
* `Tests/` modules pin statements, never prove new mathematics.  Their job is
  to break the build when a definition is weakened or a hypothesis is quietly
  added.
* `formal/Scaffold.lean` imports every module, so `lake build` builds all of it
  and nothing can be orphaned.

## Coverage

Every labelled result of `tex/manifests/results.tex`, and what has become of it.

| manuscript | statement | Lean | status |
| --- | --- | --- | --- |
| `pair:def` | Goldbach pair, Goldbach number, Goldbach count | `Scaffold.IsGoldbachPair`, `Scaffold.IsGoldbachNumber` | formalized (the count is not; nothing yet needs it) |
| `lower:lem` | a Goldbach number is at least 4 | `Scaffold.four_le_of_isGoldbachNumber` | formalized |
| `reflect:lem` | existence of a pair as a reflection condition | `Scaffold.isGoldbachNumber_iff` | formalized in the existence half; the count identity `g(n) = |P ∩ (n−P)|` is **open** |
| `even:cor` | the form the computations evaluate | — | open; immediate from `isGoldbachNumber_iff`, not yet written |
| `small:lem` | every even `n` with `4 ≤ n ≤ 12` | `Scaffold.Results.goldbach_small` | formalized |
| `verify:thm` | every even `n ≤ 10^8` | — | **non-goal.** The evidence is `tools/cpp/goldbach.cpp`; reproducing a 5·10^7-case search in the kernel is not a good use of the tool, and the manuscript says which range is machine-checked and which is not |
| `goldbach:conj` | the conjecture itself | — | open, obviously |

## Deviations

Departures from the manuscript, in full.

* **`reflect:lem` is split.**  The manuscript states the equivalence and the
  count identity together.  Lean has only the equivalence, because the count
  identity needs a bijection of finite types that nothing downstream uses yet.
  The manuscript statement is therefore *stronger* than what is formalized;
  the Coverage row says so.
* **`isGoldbachNumber_iff` uses truncated subtraction.**  `n - p` is `ℕ`
  subtraction, so the statement carries the hypothesis `p ≤ n` explicitly
  where the manuscript leaves it implicit in `n - \mathbb{P}`.  The two agree
  because `p ≤ n` is forced by primality of `n - p` in the intended range.
* **`goldbach_small` takes `Even n` as a hypothesis** rather than deriving the
  even case from a parity argument; the manuscript's proof is a table, and the
  Lean proof is the same table.

## Adding to this development

0. **Ask first.**  Formalising a statement is expensive, and which statements
   are worth it is a decision for the supervisor.  Propose a candidate with a
   reason and an estimate; do not start because a result looks formalisable.
   This applies to new work only --- repairing what is already here is
   maintenance.
1. Write the LaTeX proof first, and get it into `tex/results/`.
2. Add the `Results/` module and the `Tests/` module together.
3. Add the Coverage row and, if the Lean statement is not literally the
   manuscript's, the Deviations entry, in the same commit.
4. `lake build` must be clean: no `sorry`, no errors, no new axioms.  Check the
   last with `#print axioms` on the top-level theorem.
