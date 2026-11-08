// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/matrices/LinearRecurrence.cpp
#include <bits/stdc++.h>
using namespace std;

// Linear recurrences mod MOD (default 1e9+7, any MOD < 2^32), terms 0-indexed:
//   a[i] = coeffs[0] * a[i-1] + coeffs[1] * a[i-2] + ... + coeffs[d-1] * a[i-d]   for i >= d
// The same thing as vec * M^n with a d x d companion matrix, but d^2 log n instead of d^3 log n
// nthTerm(coeffs, initial, n)              a[n], given coeffs and the first d terms
// nthTerm<998244353>(coeffs, initial, n)   another mod
// fib: nthTerm({1, 1}, {0, 1}, 10) -> 55

#pragma GCC push_options
#pragma GCC optimize("O3") // only this hot loop, so it vectorizes on GCC builds that skip that at -O2
template <uint32_t MOD>
vector<uint32_t> linRecPolyMul(const vector<uint32_t>& a, const vector<uint32_t>& b) {
    // products of two values < MOD that can pile onto a value < MOD before a uint64 overflows
    constexpr uint64_t BATCH = min<uint64_t>(1 << 20, (UINT64_MAX - MOD) / max<uint64_t>(1, (uint64_t)(MOD - 1) * (MOD - 1)));
    vector<uint64_t> acc(a.size() + b.size() - 1, 0);
    uint64_t pending = 0;
    for (size_t i = 0; i < a.size(); i++) {
        uint64_t x = a[i];
        if (!x) continue;
        uint64_t* out = acc.data() + i;
        for (size_t j = 0; j < b.size(); j++) out[j] += x * b[j];
        if (++pending == BATCH) {
            for (auto& v : acc) v %= MOD;
            pending = 0;
        }
    }
    vector<uint32_t> res(acc.size());
    for (size_t i = 0; i < acc.size(); i++) res[i] = acc[i] % MOD;
    return res;
}
#pragma GCC pop_options

// a[n] of the recurrence above, n >= 0, initial.size() == coeffs.size() == d >= 1
// O(d^2 log n)
template <uint32_t MOD = 1'000'000'007>
long long nthTerm(const vector<long long>& coeffs, const vector<long long>& initial, long long n) {
    int d = coeffs.size();
    if (d == 0 || (int)initial.size() != d) throw invalid_argument("nthTerm needs d >= 1 coeffs and exactly d initial terms");
    auto norm = [](long long x) { x %= (long long)MOD; return (uint32_t)(x < 0 ? x + MOD : x); };
    if (n < d) return norm(initial[n]);
    // a[n] = [x^n] P(x) / Q(x) with Q = 1 - coeffs[0] x - ... - coeffs[d-1] x^d and P = (initial * Q) mod x^d
    // Bostan-Mori: P/Q = P(x)Q(-x) / Q(x)Q(-x), the denominator is even, so keep the half of the numerator
    // matching n's parity and halve n
    vector<uint32_t> Q(d + 1), P(d);
    Q[0] = 1 % MOD;
    for (int i = 0; i < d; i++) Q[i + 1] = norm(-coeffs[i]);
    for (int i = 0; i < d; i++) P[i] = norm(initial[i]);
    P = linRecPolyMul<MOD>(P, Q);
    P.resize(d);
    vector<uint32_t> Qneg(d + 1);
    while (n) {
        for (int i = 0; i <= d; i++) Qneg[i] = (i % 2 == 0 || Q[i] == 0) ? Q[i] : MOD - Q[i];
        vector<uint32_t> U = linRecPolyMul<MOD>(P, Qneg), V = linRecPolyMul<MOD>(Q, Qneg);
        for (int i = 0; i < d; i++) P[i] = U[2 * i + (n & 1)];
        for (int i = 0; i <= d; i++) Q[i] = V[2 * i];
        n >>= 1;
    }
    return P[0]; // Q[0] stays 1
}
