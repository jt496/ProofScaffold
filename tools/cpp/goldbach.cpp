// Exhaustive verification of Conjecture goldbach:conj up to a bound.
//
//   goldbach N [--counts M]
//
// Sieves [0,N] once, then evaluates the intersection of Lemma reflect:lem for
// every even n in [4,N], stopping at the first witness.  Reports any n with an
// empty intersection, and the largest least prime summand encountered, which
// is the statistic that bounds the search cost.
//
// With --counts M it additionally computes the exact Goldbach count g(n) for
// every even n <= min(M,N) and reports its minimum with the attaining n.  That
// pass is quadratic, so M is kept well below N.
//
// Exit status 0 on success, 1 if a counterexample is found.
// This program is the evidence behind Theorem verify:thm.
#include "core.hpp"
#include <cstdlib>
#include <cstring>

int main(int argc, char** argv) {
    long long N = (argc > 1) ? atoll(argv[1]) : 1000000;
    long long M = 0;
    for (int i = 2; i + 1 < argc; ++i)
        if (!strcmp(argv[i], "--counts")) M = atoll(argv[i + 1]);
    if (N < 4) { fprintf(stderr, "N must be at least 4\n"); return 2; }

    Sieve S(N);

    long long failures = 0, worst = 0, worst_n = 0;
    for (long long n = 4; n <= N; n += 2) {
        long long p = S.least_summand(n);
        if (p == 0) { printf("COUNTEREXAMPLE n=%lld\n", n); ++failures; continue; }
        if (p > worst) { worst = p; worst_n = n; }
    }
    printf("N=%lld  even n in [4,N]: %lld  failures: %lld\n",
           N, (N - 2) / 2, failures);
    printf("largest least prime summand: %lld, at n=%lld\n", worst, worst_n);

    if (M > 0) {
        long long lim = (M < N) ? M : N, best = -1;
        std::vector<long long> minimisers;
        for (long long n = 4; n <= lim; n += 2) {
            long long g = S.goldbach_count(n);
            if (best < 0 || g < best) { best = g; minimisers.clear(); }
            if (g == best) minimisers.push_back(n);
        }
        printf("min g(n) over even n in [4,%lld]: %lld, attained at:", lim, best);
        for (size_t i = 0; i < minimisers.size() && i < 20; ++i)
            printf(" %lld", minimisers[i]);
        if (minimisers.size() > 20) printf(" ... (%zu total)", minimisers.size());
        printf("\n");
    }

    printf(failures ? "GOLDBACH VERIFICATION FAILED\n"
                    : "ALL GOLDBACH VERIFICATION ASSERTIONS PASSED\n");
    return failures ? 1 : 0;
}
