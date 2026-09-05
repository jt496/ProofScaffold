#!/usr/bin/env python3
"""The refuted strengthening: a sum of two DISTINCT primes.

    python3 tools/python/distinct_goldbach.py [N]      (default 1000000)

Applies Lemma reflect:lem with the diagonal p = n/2 removed, and reports every
even n in [4,N] with no representation.  This is the evidence behind
Proposition distinct:counter in tex/archive/10-distinct-primes.tex: the answer
is exactly {4, 6}, and the strengthening is true from 8 onwards.
"""
import sys


def sieve(n):
    flags = bytearray([1]) * (n + 1)
    flags[0:2] = b'\x00\x00'
    p = 2
    while p * p <= n:
        if flags[p]:
            flags[p * p::p] = bytearray(len(flags[p * p::p]))
        p += 1
    return flags


def main():
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 1000000
    prime = sieve(N)
    failures = []
    for n in range(4, N + 1, 2):
        if not any(prime[p] and prime[n - p] for p in range(2, n // 2)):
            failures.append(n)
    print(f'N={N}  even n with no distinct-prime representation: {failures}')
    expected = [4, 6]
    ok = failures == expected
    print('ALL DISTINCT-PRIME AUDIT ASSERTIONS PASSED' if ok
          else f'AUDIT FAILED: expected {expected}')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
