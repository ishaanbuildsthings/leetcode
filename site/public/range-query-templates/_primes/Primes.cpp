// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/primes/Primes.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;
using u64 = unsigned long long;

// @if isPrime
// isPrime(97) -> true        isPrime(1000000000000000009ULL) -> true        isPrime(561) -> false
// @endif
// @if primeFactorize
// primeFactorize(360) -> {{2, 3}, {3, 2}, {5, 1}}        primeFactorize(1) -> {}
// @endif
// @if allFactors
// allFactors(12) -> {1, 2, 4, 3, 6, 12}               // unsorted
// @endif
// @if sieveIsPrime sieveSmallestPrimeFactor sieveFactorize sieveFactorizeUpToNSquared sieveAllFactors sievePrimes
// PrimeSieve sieve(1000000);                // build: O(N log(log N)); then x can be anything from 0 up to 1000000
// @endif
// @if sieveIsPrime
// sieve.isPrime(97) -> true                 // needs x <= N
// @endif
// @if sieveSmallestPrimeFactor
// sieve.smallestPrimeFactor(91) -> 7        // needs 2 <= x <= N
// @endif
// @if sieveFactorize
// sieve.primeFactorize(360) -> {{2, 3}, {3, 2}, {5, 1}}                     // needs 1 <= x <= N
// @endif
// @if sieveAllFactors
// sieve.allFactors(12) -> {1, 2, 4, 3, 6, 12}          // unsorted; needs 1 <= x <= N
// @endif
// @if sieveFactorizeUpToNSquared
// sieve.primeFactorizeUpToNSquared(999962000357) -> {{999979, 1}, {999983, 1}}    // needs 1 <= x <= N^2
// @endif
// @if sievePrimes
// sieve.primes -> {2, 3, 5, 7, ...}         // every prime <= N
// @endif
// @if primesUpTo
// primesUpTo(20) -> {2, 3, 5, 7, 11, 13, 17, 19}
// @endif
// @if primesInRange
// primesInRange(1000000000000, 1000000000100) -> {1000000000039, 1000000000061, 1000000000063, 1000000000091}
// @endif
// @if countPrimes
// countPrimes(100) -> 25                    countPrimes(1000000000) -> 50847534
// @endif

// @if isPrime primeFactorize allFactors
// ============================================================== ONE BIG NUMBER (no setup, any x < 2^64)
// @endif
// @if isPrime primeFactorize allFactors
u64 mulMod(u64 a, u64 b, u64 mod) { return (u64)((__uint128_t)a * b % mod); }

u64 powMod(u64 base, u64 exponent, u64 mod) {
    u64 result = 1 % mod;
    for (base %= mod; exponent; exponent >>= 1, base = mulMod(base, base, mod))
        if (exponent & 1) result = mulMod(result, base, mod);
    return result;
}

// O(log x) -- true if x is prime; deterministic Miller-Rabin, exact for every x < 2^64
bool isPrime(u64 x) {
    if (x < 2) return false;
    for (u64 p : {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37})
        if (x % p == 0) return x == p;
    u64 d = x - 1;
    int s = 0;
    while (d % 2 == 0) d /= 2, s++;
    for (u64 a : {2ULL, 325ULL, 9375ULL, 28178ULL, 450775ULL, 9780504ULL, 1795265022ULL}) {
        if (a % x == 0) continue;
        u64 y = powMod(a, d, x);
        if (y == 1 || y == x - 1) continue;
        bool composite = true;
        for (int i = 0; i < s - 1 && composite; i++) {
            y = mulMod(y, y, x);
            if (y == x - 1) composite = false;
        }
        if (composite) return false;
    }
    return true;
}

// @endif
// @if primeFactorize allFactors
u64 pollardRho(u64 n) {
    // a non-trivial factor of the composite n (randomized)
    if (n % 2 == 0) return 2;
    static mt19937_64 rng(chrono::steady_clock::now().time_since_epoch().count());
    while (true) {
        u64 c = rng() % (n - 1) + 1, x = rng() % n, y = x, d = 1;
        auto f = [&](u64 v) { return (mulMod(v, v, n) + c) % n; };
        while (d == 1) {
            x = f(x), y = f(f(y));
            d = gcd(x > y ? x - y : y - x, n);
        }
        if (d != n) return d;
    }
}

// about x^(1/4) expected (randomized) -- {{prime, exponent}, ...} sorted by prime, for any 1 <= x < 2^64
vector<pair<u64, int>> primeFactorize(u64 x) {
    if (x < 1) throw invalid_argument("primeFactorize: needs x >= 1");
    vector<u64> found;
    for (u64 p : {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37})
        while (x % p == 0) x /= p, found.push_back(p);
    vector<u64> stack;
    if (x > 1) stack.push_back(x);
    while (!stack.empty()) {
        u64 m = stack.back();
        stack.pop_back();
        if (isPrime(m)) {
            found.push_back(m);
        } else {
            u64 d = pollardRho(m);
            stack.push_back(d), stack.push_back(m / d);
        }
    }
    sort(found.begin(), found.end());
    vector<pair<u64, int>> res;
    for (u64 p : found) {
        if (!res.empty() && res.back().first == p) res.back().second++;
        else res.push_back({p, 1});
    }
    return res;
}

// @endif
// @if allFactors
// primeFactorize cost + D (D = number of divisors) -- every positive divisor of x, UNSORTED (sort it yourself if you
// need an order, D log D)
vector<u64> allFactors(u64 x) {
    vector<u64> res = {1};
    for (auto [p, e] : primeFactorize(x)) {
        int size = res.size();
        u64 power = 1;
        for (int k = 1; k <= e; k++) {
            power *= p;
            for (int i = 0; i < size; i++) res.push_back(res[i] * power);
        }
    }
    return res;
}

// @endif
// @if sieveIsPrime sieveSmallestPrimeFactor sieveFactorize sieveFactorizeUpToNSquared sieveAllFactors sievePrimes
// ============================================================== MANY SMALL NUMBERS (sieve once up to N)
// @endif
// @if sieveIsPrime sieveSmallestPrimeFactor sieveFactorize sieveFactorizeUpToNSquared sieveAllFactors sievePrimes
struct PrimeSieve {
    int n;
    vector<int> spf;     // spf[x] = smallest prime factor of x (0 for x < 2)
    vector<int> primes;  // every prime <= N, increasing

    // O(N log(log N)), memory about 4N bytes -- sieves every number from 0 up to N (N = 10^8 takes ~0.65s)
    explicit PrimeSieve(int n) : n(n), spf(n + 1, 0) {
        for (int p = 2; p <= n; p++) {
            if (spf[p]) continue;
            spf[p] = p, primes.push_back(p);
            for (ll j = (ll)p * p; j <= n; j += p)
                if (!spf[j]) spf[j] = p;
        }
    }

    // @if sieveIsPrime
    // O(1) -- true if x is prime; needs 0 <= x <= N
    bool isPrime(int x) const { return x >= 2 && spf[x] == x; }

    // @endif
    // @if sieveSmallestPrimeFactor
    // O(1) -- the smallest prime dividing x; needs 2 <= x <= N, else invalid_argument
    int smallestPrimeFactor(int x) const {
        if (x < 2) throw invalid_argument("smallestPrimeFactor: needs x >= 2");
        return spf[x];
    }

    // @endif
    // @if sieveFactorize sieveFactorizeUpToNSquared sieveAllFactors
    // O(log x) -- {{prime, exponent}, ...} sorted by prime; needs 1 <= x <= N
    vector<pair<ll, int>> primeFactorize(ll x) const {
        vector<pair<ll, int>> res;
        while (x > 1) {
            int p = spf[x], e = 0;
            while (x % p == 0) x /= p, e++;
            res.push_back({p, e});
        }
        return res;
    }

    // @endif
    // @if sieveAllFactors
    // O(log x + D) (D = number of divisors) -- every positive divisor of x, UNSORTED; needs 1 <= x <= N
    vector<ll> allFactors(ll x) const {
        vector<ll> res = {1};
        for (auto [p, e] : primeFactorize(x)) {
            int size = res.size();
            ll power = 1;
            for (int k = 1; k <= e; k++) {
                power *= p;
                for (int i = 0; i < size; i++) res.push_back(res[i] * power);
            }
        }
        return res;
    }

    // @endif
    // @if sieveFactorizeUpToNSquared
    // O(number of primes <= sqrt(x)) -- like primeFactorize, but x can go up to N^2: trial division by the sieved
    // primes; whatever is left after the primes up to sqrt(x) is 1 or a single prime above sqrt(x)
    vector<pair<ll, int>> primeFactorizeUpToNSquared(ll x) const {
        if (x <= n) return primeFactorize(x);
        if (x > (ll)n * n) throw invalid_argument("primeFactorizeUpToNSquared: needs x <= N^2");
        vector<pair<ll, int>> res;
        for (int p : primes) {
            if ((ll)p * p > x) break;
            if (x % p == 0) {
                int e = 0;
                while (x % p == 0) x /= p, e++;
                res.push_back({p, e});
            }
        }
        if (x > 1) res.push_back({x, 1});
        return res;
    }
    // @endif
};

// @endif
// @if primesUpTo primesInRange countPrimes
// ============================================================== LISTING AND COUNTING PRIMES
// @endif
// @if primesUpTo
// O(N log(log N)) time, O(sqrt(N)) extra memory besides the result -- every prime <= N, increasing, for
// N up to 2^31 - 1. A segmented sieve over the odd numbers, one cache-sized block at a time: 10^9 takes ~1s, and its
// 50,847,534 primes take ~200 MB
vector<int> primesUpTo(ll n) {
    vector<int> res;
    if (n < 2) return res;
    if (n > INT_MAX) throw invalid_argument("primesUpTo: needs N <= 2^31 - 1");
    res.reserve(n / max(1.0, log((double)n) - 1.1) + 10);
    res.push_back(2);
    ll r = sqrtl(n);
    while (r * r > n) r--;
    while ((r + 1) * (r + 1) <= n) r++;
    vector<char> small(r + 1, 1);
    vector<ll> base, next;  // odd sieving primes, and the next odd multiple of each still to cross off
    for (ll i = 3; i <= r; i += 2)
        if (small[i]) {
            base.push_back(i), next.push_back(i * i);
            for (ll j = i * i; j <= r; j += 2 * i) small[j] = 0;
        }
    const ll SIZE = 1 << 18;  // odd numbers per block
    vector<char> block(SIZE);
    for (ll lo = 3; lo <= n; lo += 2 * SIZE) {
        ll hi = min(n, lo + 2 * (SIZE - 1));
        fill(block.begin(), block.end(), 1);
        for (size_t k = 0; k < base.size() && base[k] * base[k] <= hi; k++) {
            ll j = next[k];
            for (; j <= hi; j += 2 * base[k]) block[(j - lo) / 2] = 0;
            next[k] = j;
        }
        for (ll i = 0; lo + 2 * i <= hi; i++)
            if (block[i]) res.push_back(lo + 2 * i);
    }
    return res;
}

// @endif
// @if primesInRange
// O((hi - lo) log(log hi) + sqrt(hi)) -- every prime p with lo <= p <= hi, increasing. A segmented
// sieve: it crosses off multiples of the primes up to sqrt(hi) inside just that window, so hi can be ~10^12 as long as
// hi - lo is about 10^7 or less
vector<ll> primesInRange(ll lo, ll hi) {
    lo = max(lo, 2LL);
    if (lo > hi) return {};
    ll r = sqrtl(hi);
    while (r * r > hi) r--;
    while ((r + 1) * (r + 1) <= hi) r++;
    vector<char> small(r + 1, 1), block(hi - lo + 1, 1);
    for (ll p = 2; p <= r; p++) {
        if (!small[p]) continue;
        for (ll j = p * p; j <= r; j += p) small[j] = 0;
        for (ll j = max(p * p, (lo + p - 1) / p * p); j <= hi; j += p) block[j - lo] = 0;
    }
    vector<ll> res;
    for (ll x = lo; x <= hi; x++)
        if (block[x - lo]) res.push_back(x);
    return res;
}

// @endif
// @if countPrimes
// O(n^(3/4)) time, O(sqrt(n)) memory (Lucy_Hedgehog) -- how many primes are <= n, without listing them; n = 10^12
// takes ~0.2s, 10^13 ~1s
ll countPrimes(ll n) {
    if (n < 2) return 0;
    ll r = sqrtl(n);
    while (r * r > n) r--;
    while ((r + 1) * (r + 1) <= n) r++;
    // "numbers in 2..v not yet crossed off" for every distinct v = n / k: small v at lowCount[v], v = n / k at
    // highCount[k]
    vector<ll> lowCount(r + 1), highCount(r + 1);
    for (ll v = 1; v <= r; v++) lowCount[v] = v - 1, highCount[v] = n / v - 1;
    for (ll p = 2; p <= r; p++) {
        if (lowCount[p] == lowCount[p - 1]) continue;  // p was crossed off: not a prime
        ll before = lowCount[p - 1], p2 = p * p, kEnd = min(r, n / p2);
        for (ll k = 1; k <= kEnd; k++) {
            ll kp = k * p;
            highCount[k] -= (kp <= r ? highCount[kp] : lowCount[n / kp]) - before;
        }
        for (ll v = r; v >= p2; v--) lowCount[v] -= lowCount[v / p] - before;
    }
    return highCount[1];
}
// @endif
