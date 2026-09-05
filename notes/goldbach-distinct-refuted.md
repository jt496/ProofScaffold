---
name: goldbach-distinct-refuted
description: The two-distinct-primes strengthening of Goldbach fails exactly at n = 4 and 6, for a reason no sieve can see.
metadata:
  type: project
---

Every even `n` with `8 <= n <= 10^6` is a sum of two **distinct** primes; `n = 4`
and `n = 6` are not, and they are the only failures in that range.  Verified by
`python3 tools/python/distinct_goldbach.py 1000000`, retained as
`tools/logs/distinct-primes-1e6.log`.  Written up as Proposition
`distinct:counter` in `tex/routes/20-distinct-primes.tex`.

**Why:** the obstruction is the diagonal pair `n = (n/2) + (n/2)`, available
exactly when `n/2` is prime.  For `n` in `{4, 6}` it is the *only* pair, so
removing it empties the set.  From 8 onwards there is always a second pair.

**How to apply:** do not reach for the distinct-primes form as a lemma without
the `n >= 8` hypothesis.  More usefully, the failure is invisible to the
sifted-count machinery of `sifted:def`, which is insensitive to the diagonal —
so a strengthening that *looks* sieve-accessible can still fail for a reason
sieves cannot express.  Check small cases by hand before building a route on a
strengthening, however plausible.  Related: [[goldbach-density-route]].
