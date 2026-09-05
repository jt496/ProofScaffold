# Computational toolkit

Programs supporting the manuscript.  Everything a computational claim in the
paper rests on was produced here, and every such claim names the program, the
exact command, and the retained log.

Layout:

* `cpp/`    — exhaustive and large-scale searches (C++17).  `make` builds all.
* `python/` — exploratory scripts and small audits.  Standard library only.
* `logs/`   — retained output of the runs the manuscript cites.

## Conventions

`cpp/core.hpp` holds the shared representation, so that a decision about how
the objects are encoded is made once:

| symbol | meaning |
| --- | --- |
| `Sieve` | primes below `N` as a byte per integer, built once per run |
| `Sieve::goldbach_count(n)` | `g(n)`, counting ordered pairs |
| `Sieve::least_summand(n)` | the least prime `p` with `n − p` prime, or `0` |

A program that supports a manuscript claim must:

1. print a final line that is either `ALL ... ASSERTIONS PASSED` or a failure,
   and exit non-zero on failure, so it can be run in CI without a human
   reading the output;
2. be deterministic, or take an explicit seed;
3. be named, with its exact arguments, in the statement it supports.

## cpp/

| program | arguments | what it does |
| --- | --- | --- |
| `goldbach` | `N [--counts M]` | verifies Conjecture `goldbach:conj` for every even `n` in `[4,N]` by the reflection of Lemma `reflect:lem`, stopping at the first witness, and reports the largest least summand needed.  `--counts M` additionally computes the exact Goldbach count for `n ≤ M`, which is quadratic and so kept to a short range.  This is the evidence for Theorem `verify:thm`. |

## python/

| script | what it does |
| --- | --- |
| `distinct_goldbach.py` | the refuted strengthening: even `n` with no representation as a sum of two *distinct* primes.  The answer is exactly `{4, 6}`; the evidence for Proposition `distinct:counter`. |
| `goldbach_counts.py` | exploratory: `g(n)(log n)²/n` over dyadic blocks, the quantity Problem `density:prob` asks to bound below.  Not tied to any claim. |
| `link_all.py` | build-time: writes the marked-up copy of `tex/` for the densely linked editions.  Never edit its output. |
| `undefined_terms.py` | sweeps for coined vocabulary the manuscript never defines.  Produces candidates, not a verdict; see `MANUSCRIPT.md`. |

## Results reproduced

```
make -C tools/cpp
tools/cpp/goldbach 100000000                 # Theorem verify:thm; logs/goldbach-1e8.log
tools/cpp/goldbach 1000000 --counts 20000    # min g(n) = 1 on [4,20000], at n = 4, 6
python3 tools/python/distinct_goldbach.py 1000000   # Prop distinct:counter; logs/distinct-primes-1e6.log
```

`make audit` runs the fast subset of these; CI runs the same target.
