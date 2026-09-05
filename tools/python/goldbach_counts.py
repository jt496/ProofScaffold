#!/usr/bin/env python3
"""Exploratory: how the Goldbach count grows.

    python3 tools/python/goldbach_counts.py [N]        (default 20000)

Prints min, mean and max of g(n)*(log n)^2/n over dyadic blocks, which is the
quantity Problem density:prob asks to bound below.  Numerical support only --
nothing in the manuscript rests on it.  This is the kind of throwaway check
that belongs in tools/python/ rather than in the manuscript.
"""
import sys
import math
from distinct_goldbach import sieve


def main():
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 20000
    prime = sieve(N)
    print(f'{"range":>16} {"min":>8} {"mean":>8} {"max":>8}')
    lo = 4
    while lo <= N:
        hi = min(2 * lo, N)
        vals = []
        for n in range(lo if lo % 2 == 0 else lo + 1, hi + 1, 2):
            g = sum(1 for p in range(2, n - 1) if prime[p] and prime[n - p])
            vals.append(g * math.log(n) ** 2 / n)
        if vals:
            print(f'{f"[{lo},{hi}]":>16} {min(vals):8.3f} '
                  f'{sum(vals)/len(vals):8.3f} {max(vals):8.3f}')
        lo = hi + 1 if hi == N else 2 * lo


if __name__ == '__main__':
    main()
