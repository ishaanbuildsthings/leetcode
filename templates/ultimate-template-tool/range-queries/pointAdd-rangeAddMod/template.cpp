// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/pointAdd-rangeAddMod/template.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: getAll pointAdd rangeAddMod
// @data-structure-type: difference-array
// @complexities:
//   getAll: N
//   pointAdd: 1
//   rangeAddMod: 1
//   build: N
// @memory:
//   layout: none
//   node: d[1*N]
//   tags: none
//   other: a[1*N]
//   note: d is the difference array of every add so far, % MOD (d[l] += v, d[r+1] -= v); getAll sweeps it once

// Range add % MOD, then read the array: a difference array (a sweep line). Every add is O(1); getAll is one O(N) prefix
// sum pass over the adds, and it can be called again later (the adds are kept). Nothing reads a single value in
// between: for that, use a BIT or seg tree. Values are kept in [0, mod). All indices 0-based, ranges inclusive [l, r].
// T: int, long long, ...
template <typename T>
struct DiffArrayMod {
    using W = conditional_t<sizeof(T) <= 4, long long, __int128>;  // wide enough for a sum of two residues
    int n;
    T mod;
    vector<T> a, d;

    T norm(W x) const { x %= mod; return T(x < 0 ? x + mod : x); }

    // O(N) -- arr: the initial array (can be empty)
    explicit DiffArrayMod(const vector<T>& arr, T mod = 1000000007) : n((int)arr.size()), mod(mod), a(n), d(n + 1) {
        for (int i = 0; i < n; i++) a[i] = norm(arr[i]);
    }

    // O(1) -- a[i] += v (% MOD) for i in [l, r]; needs 0 <= l <= r < n, else throws out_of_range
    void rangeAddMod(int l, int r, T v) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeAddMod: needs 0 <= l <= r < n");
        T x = norm(v);
        d[l] = norm(W(d[l]) + x);
        d[r + 1] = norm(W(d[r + 1]) - x);
    }

    // O(1) -- a[i] += v (% MOD); needs 0 <= i < n, else throws out_of_range
    void pointAdd(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointAdd: needs 0 <= i < n");
        rangeAddMod(i, i, v);
    }

    // O(N) -- the whole array with every add so far applied, each value in [0, mod) (a new vector)
    vector<T> getAll() const {
        vector<T> out(a);
        T run = 0;
        for (int i = 0; i < n; i++) {
            run = norm(W(run) + d[i]);
            out[i] = norm(W(out[i]) + run);
        }
        return out;
    }
};
