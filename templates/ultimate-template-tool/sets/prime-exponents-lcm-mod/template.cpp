// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/sets/prime-exponents-lcm-mod/template.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: add clear count lcmAllMod remove size
// @data-structure-type: prime-exponents
// @values: online
// @keys: numbers
// @tracks: none
// @complexities:
//   add: log(U)+U^(1/4) expected
//   clear: N
//   count: 1
//   lcmAllMod: 1
//   remove: log(U)
//   size: 1
//   build: 1
// @memory:
//   layout: none
//   node: cnt[1*N] factors[1*N*log(U)]
//   tags: none
//   other: none
//   note: N = distinct values present; each keeps its factorization (at most log2 U primes). The sieve below SIEVE_LIMIT is shared by every multiset in the run and grows only as far as the values seen need

// The exact LCM of a multiset, however huge, mod a prime MOD, with adds and removes in any order (values >= 0).
// The LCM is the product of p^(the largest exponent of p in any value), so each prime keeps how many of the values
// present have each exponent, and the product of p^top % MOD is kept current: an add multiplies in the primes whose
// top exponent grew, a remove the inverse of the ones whose top fell (that's why MOD must be prime). Only the first
// copy of a value and the removal of its last copy touch the primes: copies don't change the LCM.
// Empty multiset: lcmAllMod() is 1 (the LCM of nothing); a 0 present makes it 0; so does a value divisible by MOD.
//
// Factorizing: values below SIEVE_LIMIT come from a smallest-prime-factor table that grows (by doubling) only as far
// as the values seen so far need, shared by every multiset in the run, so test case after test case never rebuilds it;
// bigger values never touch it and go to Miller-Rabin + Pollard rho instead (about U^(1/4) steps, no memory), so huge
// values are fine too. Growing the table costs O(its new size) once (at most SIEVE_LIMIT), and by doubling all of the
// growth over a run adds up to O(SIEVE_LIMIT): an add that triggers it pays that, every other add just its own cost.
//
// LcmModMultiset<long long> s;              // mod 1e9+7
// LcmModMultiset<long long> s(998244353);   // another prime
namespace factorizer {
// values below this use the sieve (up to 16 MB); raise it for many mid-size values
const long long SIEVE_LIMIT = 1 << 22;
inline vector<int> spf = {0, 1};  // spf[v] = smallest prime factor of v, for every v < spf.size()

inline void sieveTo(long long n) {  // the table covering every value <= n (n < SIEVE_LIMIT), grown by doubling
    if (n < (long long)spf.size()) return;
    long long size = min(SIEVE_LIMIT, max(n + 1, 2 * (long long)spf.size()));
    spf.assign(size, 0);
    vector<int> primes;
    for (long long i = 2; i < size; i++) {  // a linear sieve
        if (!spf[i]) spf[i] = (int)i, primes.push_back((int)i);
        for (int p : primes) {
            if (p > spf[i] || i * p >= size) break;
            spf[i * p] = p;
        }
    }
    spf[1] = 1;
}

inline unsigned long long mulMod(unsigned long long a, unsigned long long b, unsigned long long m) {
    return (unsigned long long)((__uint128_t)a * b % m);
}

inline unsigned long long powMod(unsigned long long a, unsigned long long e, unsigned long long m) {
    unsigned long long r = 1 % m;
    for (a %= m; e; e >>= 1, a = mulMod(a, a, m))
        if (e & 1) r = mulMod(r, a, m);
    return r;
}

inline bool isPrime(unsigned long long n) {  // deterministic Miller-Rabin for every 64-bit n
    if (n < 2) return false;
    for (unsigned long long p : {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37})
        if (n % p == 0) return n == p;
    unsigned long long d = n - 1;
    int s = 0;
    while (!(d & 1)) d >>= 1, s++;
    for (unsigned long long a : {2, 325, 9375, 28178, 450775, 9780504, 1795265022}) {
        unsigned long long x = powMod(a, d, n);
        if (x == 0 || x == 1 || x == n - 1) continue;
        bool composite = true;
        for (int r = 1; r < s && composite; r++) {
            x = mulMod(x, x, n);
            if (x == n - 1) composite = false;
        }
        if (composite) return false;
    }
    return true;
}

inline unsigned long long rho(unsigned long long n) {  // a factor of the odd composite n other than 1 and n (Brent)
    static mt19937_64 rng(chrono::steady_clock::now().time_since_epoch().count());
    while (true) {
        unsigned long long y = rng() % (n - 1) + 1, c = rng() % (n - 1) + 1, g = 1, q = 1, x = 0, ys = 0;
        const unsigned long long m = 128;
        for (unsigned long long r = 1; g == 1; r <<= 1) {
            x = y;
            for (unsigned long long i = 0; i < r; i++) y = (mulMod(y, y, n) + c) % n;
            for (unsigned long long k = 0; k < r && g == 1; k += m) {
                ys = y;
                for (unsigned long long i = 0; i < min(m, r - k); i++) {
                    y = (mulMod(y, y, n) + c) % n;
                    q = mulMod(q, x > y ? x - y : y - x, n);
                }
                g = gcd(q, n);
            }
        }
        if (g == n) {
            g = 1;
            while (g == 1) {
                ys = (mulMod(ys, ys, n) + c) % n;
                g = gcd(x > ys ? x - ys : ys - x, n);
            }
        }
        if (g != n) return g;
    }
}

// (prime, exponent) pairs of x >= 1: the sieve below SIEVE_LIMIT, else small primes, then Miller-Rabin + Pollard rho
// O(log x) below SIEVE_LIMIT, about x^(1/4) expected above
inline vector<pair<long long, int>> factorize(long long x) {
    map<long long, int> res;
    vector<unsigned long long> stack = {(unsigned long long)x};
    while (!stack.empty()) {
        unsigned long long n = stack.back();
        stack.pop_back();
        if (n == 1) continue;
        if ((long long)n < SIEVE_LIMIT) {
            sieveTo((long long)n);
            while (n > 1) {
                int p = spf[n];
                n /= p;
                res[p]++;
            }
            continue;
        }
        for (unsigned long long p : {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37})
            while (n % p == 0) n /= p, res[(long long)p]++;
        if (n == 1) continue;
        if ((long long)n < SIEVE_LIMIT) stack.push_back(n);
        else if (isPrime(n)) res[(long long)n]++;
        else {
            unsigned long long d = rho(n);
            stack.push_back(d);
            stack.push_back(n / d);
        }
    }
    return vector<pair<long long, int>>(res.begin(), res.end());
}
}  // namespace factorizer

// T: the value type (int, long long, ...); values are handled as long long inside
template <typename T>
struct LcmModMultiset {
    struct SplitMix {  // (hashes values so no fixed input can make them collide)
        size_t operator()(long long x) const {
            static const unsigned long long salt = chrono::steady_clock::now().time_since_epoch().count();
            unsigned long long z = (unsigned long long)x + salt + 0x9e3779b97f4a7c15ULL;
            z = (z ^ (z >> 30)) * 0xbf58476d1ce4e5b9ULL;
            z = (z ^ (z >> 27)) * 0x94d049bb133111ebULL;
            return z ^ (z >> 31);
        }
    };
    long long mod;
    unordered_map<long long, long long, SplitMix> cnt;  // value -> copies
    unordered_map<long long, vector<pair<long long, int>>, SplitMix> fac;  // value present -> its factorization
    unordered_map<long long, map<int, int>, SplitMix> exps;  // prime -> {exponent: how many values present have it}
    long long n = 0, prod;  // prod: the product of prime^top over the primes other than mod, % mod

    // O(1) -- an empty multiset; mod must be prime (a remove divides by the primes whose top exponent fell)
    explicit LcmModMultiset(long long mod = 1000000007) : mod(mod), prod(1 % mod) {}

    // O(logU + U^(1/4) expected) -- add one copy of x (x >= 0); the first add needing a bigger shared sieve also pays
    // its one-time growth (all of it together O(SIEVE_LIMIT) per run)
    void add(T value) {
        long long x = (long long)value;
        if (x < 0) throw invalid_argument("LcmModMultiset::add: x is negative");
        n++;
        if (cnt[x]++ || x == 0) return;  // another copy (the LCM is unchanged), or a 0 (lcmAllMod checks for it)
        auto& f = fac[x] = factorizer::factorize(x);
        for (auto [p, e] : f) {
            auto& d = exps[p];
            int top = d.empty() ? 0 : d.rbegin()->first;
            d[e]++;
            if (e > top && p != mod) prod = (long long)factorizer::mulMod(prod, factorizer::powMod(p, e - top, mod),
                mod);
        }
    }

    // O(logU + log(MOD)) -- remove one copy of x if present; returns how many were removed (0 or 1)
    int remove(T value) {
        long long x = (long long)value;
        auto it = cnt.find(x);
        if (it == cnt.end()) return 0;
        n--;
        if (--it->second) return 1;
        cnt.erase(it);
        if (x == 0) return 1;
        auto fit = fac.find(x);
        for (auto [p, e] : fit->second) {
            auto pit = exps.find(p);
            auto& d = pit->second;
            int top = d.rbegin()->first;
            if (--d[e] == 0) d.erase(e);
            int now = d.empty() ? 0 : d.rbegin()->first;
            if (d.empty()) exps.erase(pit);
            if (now < top && p != mod) {
                long long down = (long long)factorizer::powMod(p, top - now, mod);
                prod = (long long)factorizer::mulMod(prod, factorizer::powMod(down, mod - 2, mod), mod);
            }
        }
        fac.erase(fit);
        return 1;
    }

    // O(1) -- the exact LCM of all values, however huge, % mod: 1 if empty (the LCM of nothing), 0 if a 0 is present
    // or some value is divisible by mod
    long long lcmAllMod() const {
        if (!n) return 1 % mod;
        if (cnt.count(0) || exps.count(mod)) return 0;
        return prod;
    }

    // O(1) -- how many copies of x (0 if none)
    long long count(T x) const {
        auto it = cnt.find((long long)x);
        return it == cnt.end() ? 0 : it->second;
    }

    // O(1) -- how many values (copies count; 0 if empty)
    long long size() const { return n; }

    // O(N) -- remove everything (the same mod; the shared sieve stays)
    void clear() {
        cnt.clear(), fac.clear(), exps.clear();
        n = 0;
        prod = 1 % mod;
    }
};
