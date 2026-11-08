// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/matrices/LinearRecurrence.cpp
#include <bits/stdc++.h>
using namespace std;

// Linear recurrences mod MOD (default 1e9+7, any MOD < 2^32; berlekampMassey / guessNthTerm need it prime), terms 0-indexed:
//   a[i] = coeffs[0] * a[i-1] + coeffs[1] * a[i-2] + ... + coeffs[d-1] * a[i-d]   for i >= d
// The same thing as vec * M^n with a d x d companion matrix, but d^2 log n instead of d^3 log n
// nthTerm(coeffs, initial, n)              a[n], given coeffs and the first d terms
// berlekampMassey(seq)                     the shortest coeffs that generate seq
// guessNthTerm(seq, n)                     a[n], given enough first terms (2d of them suffice) and no recurrence
// nthTerm<998244353>(coeffs, initial, n)   another mod
// fib: nthTerm({1, 1}, {0, 1}, 10) -> 55
//      berlekampMassey({0, 1, 1, 2, 3, 5}) -> {1, 1}
//      guessNthTerm({0, 1, 1, 2, 3, 5}, 10) -> 55

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

// shortest coeffs (same convention as nthTerm) with seq[i] = sum coeffs[j] * seq[i-1-j] for all i >= coeffs.size()
// O(seq.size()^2)
template <uint32_t MOD = 1'000'000'007>
vector<long long> berlekampMassey(const vector<long long>& input) {
    auto modPow = [](uint64_t b, uint64_t e) {
        uint64_t r = 1 % MOD;
        for (b %= MOD; e; e >>= 1, b = b * b % MOD) {
            if (e & 1) r = r * b % MOD;
        }
        return r;
    };
    vector<uint64_t> seq(input.size());
    for (size_t i = 0; i < input.size(); i++) {
        long long x = input[i] % (long long)MOD;
        seq[i] = x < 0 ? x + MOD : x;
    }
    vector<uint64_t> cur{1}, prev{1}; // connection polynomial: sum cur[j] * seq[i-j] = 0
    int length = 0, gap = 1;
    uint64_t prevDisc = 1;
    for (int i = 0; i < (int)seq.size(); i++) {
        uint64_t disc = seq[i];
        for (int j = 1; j <= length; j++) disc = (disc + cur[j] * seq[i - j]) % MOD;
        if (disc == 0) {
            gap++;
            continue;
        }
        uint64_t factor = disc * modPow(prevDisc, MOD - 2) % MOD;
        vector<uint64_t> nxt = cur;
        if (nxt.size() < prev.size() + gap) nxt.resize(prev.size() + gap, 0);
        for (size_t j = 0; j < prev.size(); j++) nxt[j + gap] = (nxt[j + gap] + MOD - factor * prev[j] % MOD) % MOD;
        if (2 * length <= i) {
            prev = cur;
            length = i + 1 - length;
            prevDisc = disc;
            gap = 1;
        } else {
            gap++;
        }
        cur = nxt;
    }
    cur.resize(length + 1, 0);
    vector<long long> coeffs(length);
    for (int j = 0; j < length; j++) coeffs[j] = (MOD - cur[j + 1]) % MOD;
    return coeffs;
}

// a[n] of the shortest recurrence that fits seq, n >= 0 (for a recurrence of order d, give at least 2d terms)
// O(seq.size()^2 + d^2 log n)
template <uint32_t MOD = 1'000'000'007>
long long guessNthTerm(const vector<long long>& seq, long long n) {
    if (n < (long long)seq.size()) {
        long long x = seq[n] % (long long)MOD;
        return x < 0 ? x + MOD : x;
    }
    vector<long long> coeffs = berlekampMassey<MOD>(seq);
    if (coeffs.empty()) return 0;
    return nthTerm<MOD>(coeffs, vector<long long>(seq.begin(), seq.begin() + coeffs.size()), n);
}
