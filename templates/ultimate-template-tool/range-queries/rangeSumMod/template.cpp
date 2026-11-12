// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/rangeSumMod/template.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: rangeSumMod
// @data-structure-type: prefix-sum
// @complexities:
//   rangeSumMod: 1
//   build: N
// @memory:
//   layout: none
//   node: P[1*N]
//   tags: none
//   other: none
//   note: P[i] = (a[0] + ... + a[i-1]) % MOD, one more entry than the array

// Static range sum % MOD with a prefix sum array: O(N) build, O(1) per query, no updates. All indices 0-based, ranges
// inclusive [l, r].
// T: int, long long, ...
template <typename T>
struct PrefixSumsMod {
    using W = conditional_t<sizeof(T) <= 4, long long, __int128>;  // wide enough for a sum of two residues
    int n;
    T mod;
    vector<T> P;  // P[i] = (a[0] + ... + a[i-1]) % MOD

    T norm(W x) const { x %= mod; return T(x < 0 ? x + mod : x); }

    // O(N) -- a: the array (can be empty)
    explicit PrefixSumsMod(const vector<T>& a, T mod = 1000000007) : n((int)a.size()), mod(mod), P(n + 1) {
        for (int i = 0; i < n; i++) P[i + 1] = norm(W(P[i]) + a[i]);
    }

    // O(1) -- (a[l] + ... + a[r]) % MOD, in [0, mod); needs 0 <= l <= r < n, else throws out_of_range
    T rangeSumMod(int l, int r) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeSumMod: needs 0 <= l <= r < n");
        return norm(W(P[r + 1]) - P[l]);
    }
};
