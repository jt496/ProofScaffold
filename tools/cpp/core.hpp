// ---------------------------------------------------------------------------
// Shared machinery for the C++ toolkit.  Every program in this directory
// includes this header, so a representation decision is made once.
//
// The convention for this project: the primes below a bound N are held as a
// bitmap `Sieve::is_prime` of length N+1.  Replace this header wholesale when
// you start a project of your own -- what matters is that there IS one shared
// representation, named in tools/README.md, rather than one per program.
// ---------------------------------------------------------------------------
#pragma once
#include <cstdint>
#include <cstdio>
#include <vector>

struct Sieve {
    long long N;
    std::vector<uint8_t> is_prime;   // is_prime[k] for 0 <= k <= N

    explicit Sieve(long long N_) : N(N_), is_prime(N_ + 1, 1) {
        is_prime[0] = 0;
        if (N >= 1) is_prime[1] = 0;
        for (long long p = 2; p * p <= N; ++p)
            if (is_prime[p])
                for (long long m = p * p; m <= N; m += p) is_prime[m] = 0;
    }

    // The Goldbach count g(n) = |P n (n - P)|, counting ORDERED pairs, so that
    // g(8) = 2 for (3,5) and (5,3).  See Lemma reflect:lem.
    long long goldbach_count(long long n) const {
        long long c = 0;
        for (long long p = 2; p <= n - 2; ++p)
            if (is_prime[p] && is_prime[n - p]) ++c;
        return c;
    }

    // The least prime p with n - p prime, or 0 when there is none.
    long long least_summand(long long n) const {
        for (long long p = 2; p <= n - 2; ++p)
            if (is_prime[p] && is_prime[n - p]) return p;
        return 0;
    }
};
