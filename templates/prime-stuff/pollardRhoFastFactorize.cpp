#include <bits/stdc++.h>
using namespace std;

using u64 = uint64_t;
using u128 = __uint128_t;

// Modular multiplication that won't overflow for n up to 2^63
u64 mulMod(u64 a, u64 b, u64 mod) {
    return (u64)((u128)a * b % mod);
}

u64 powMod(u64 base, u64 exp, u64 mod) {
    u64 result = 1 % mod;
    base %= mod;
    while (exp > 0) {
        if (exp & 1) result = mulMod(result, base, mod);
        base = mulMod(base, base, mod);
        exp >>= 1;
    }
    return result;
}

// Deterministic Miller-Rabin for n < 2^64
// Witnesses {2, 325, 9375, 28178, 450775, 9780504, 1795265022} cover all u64
bool isPrime(u64 n) {
    if (n < 2) return false;
    for (u64 p : {2ULL, 3ULL, 5ULL, 7ULL, 11ULL, 13ULL, 17ULL, 19ULL, 23ULL, 29ULL, 31ULL, 37ULL}) {
        if (n % p == 0) return n == p;
    }

    u64 d = n - 1;
    int s = 0;
    while ((d & 1) == 0) {
        d >>= 1;
        s++;
    }

    for (u64 a : {2ULL, 325ULL, 9375ULL, 28178ULL, 450775ULL, 9780504ULL, 1795265022ULL}) {
        if (a % n == 0) continue;
        u64 x = powMod(a, d, n);
        if (x == 1 || x == n - 1) continue;
        bool composite = true;
        for (int i = 0; i < s - 1; i++) {
            x = mulMod(x, x, n);
            if (x == n - 1) {
                composite = false;
                break;
            }
        }
        if (composite) return false;
    }
    return true;
}

// Pollard's rho — finds a non-trivial factor of composite n
u64 pollardRho(u64 n) {
    if ((n & 1) == 0) return 2;
    if (n % 3 == 0) return 3;

    static mt19937_64 rng(chrono::steady_clock::now().time_since_epoch().count());
    while (true) {
        u64 c = rng() % (n - 1) + 1;
        auto f = [&](u64 x) { return (mulMod(x, x, n) + c) % n; };
        u64 x = rng() % n;
        u64 y = x;
        u64 d = 1;
        while (d == 1) {
            x = f(x);
            y = f(f(y));
            d = __gcd(x > y ? x - y : y - x, n);
        }
        if (d != n) return d;
    }
}

// Prime factorization
// Returns sorted vector of (prime, exponent) pairs where n = Π (p_i ^ e_i)
// Time: expected ~O(n^(1/4) * log n), randomized
// Supports: integers up to 2^64
vector<pair<u64, int>> primeFactorize(u64 n) {
    map<u64, int> factors;

    function<void(u64)> dfs = [&](u64 m) {
        if (m == 1) return;
        if (isPrime(m)) {
            factors[m]++;
            return;
        }
        u64 d = pollardRho(m);
        dfs(d);
        dfs(m / d);
    };

    for (u64 p : {2ULL, 3ULL, 5ULL, 7ULL, 11ULL, 13ULL, 17ULL, 19ULL, 23ULL, 29ULL, 31ULL, 37ULL}) {
        if (n % p == 0) {
            int e = 0;
            while (n % p == 0) { n /= p; e++; }
            factors[p] += e;
        }
    }

    if (n > 1) dfs(n);

    return vector<pair<u64, int>>(factors.begin(), factors.end());
}

// All positive divisors of n
// Time: expected ~O(n^(1/4) * log n + D), where D = number of divisors
vector<u64> allFactors(u64 n) {
    auto pf = primeFactorize(n);
    vector<u64> res = {1};
    for (auto [p, e] : pf) {
        vector<u64> cur;
        u64 mul = 1;
        for (int i = 0; i < e; i++) {
            mul *= p;
            for (u64 v : res) cur.push_back(v * mul);
        }
        for (u64 v : cur) res.push_back(v);
    }
    return res;
}