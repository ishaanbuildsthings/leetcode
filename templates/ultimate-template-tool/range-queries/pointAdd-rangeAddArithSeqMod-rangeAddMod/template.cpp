// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/pointAdd-rangeAddArithSeqMod-rangeAddMod/template.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: getAll pointAdd rangeAddArithSeqMod rangeAddMod
// @data-structure-type: difference-array
// @complexities:
//   getAll: N
//   pointAdd: 1
//   rangeAddArithSeqMod: 1
//   rangeAddMod: 1
//   build: N
// @memory:
//   layout: none
//   node: dk[1*N] ds[1*N]
//   tags: none
//   other: a[1*N]
//   note: every add is a line k + s * i over [l, r], % MOD; dk and ds are difference arrays of k and s, and getAll sweeps both

// Range add and arithmetic sequence add % MOD, then read the array: two difference arrays (a double sweep line). An
// add of start, start + step, ... over [l, r] is the line k + step * i with k = start - l * step, so it is O(1): k and
// step go into one difference array each, and getAll sweeps both and adds k + step * i at every i, O(N). getAll can be
// called again later (the adds are kept). Nothing reads a single value in between: for that, use a BIT or seg tree.
// Values are kept in [0, mod). All indices 0-based, ranges inclusive [l, r].
// T: int, long long, ...
template <typename T>
struct DiffArrayArithMod {
    using W = conditional_t<sizeof(T) <= 4, long long, __int128>;  // wide enough for a product of two residues
    int n;
    T mod;
    vector<T> a, dk, ds;

    T norm(W x) const { x %= mod; return T(x < 0 ? x + mod : x); }

    // O(N) -- arr: the initial array (can be empty)
    explicit DiffArrayArithMod(const vector<T>& arr, T mod = 1000000007)
        : n((int)arr.size()), mod(mod), a(n), dk(n + 1), ds(n + 1) {
        for (int i = 0; i < n; i++) a[i] = norm(arr[i]);
    }

    // O(1) -- a[l + j] += start + j * step (% MOD) for j in [0, r - l]; needs 0 <= l <= r < n, else throws
    // out_of_range
    void rangeAddArithSeqMod(int l, int r, T start, T step) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeAddArithSeqMod: needs 0 <= l <= r < n");
        T st = norm(step), k = norm(W(start) - W(l) * st);
        dk[l] = norm(W(dk[l]) + k);
        dk[r + 1] = norm(W(dk[r + 1]) - k);
        ds[l] = norm(W(ds[l]) + st);
        ds[r + 1] = norm(W(ds[r + 1]) - st);
    }

    // O(1) -- a[i] += v (% MOD) for i in [l, r]; needs 0 <= l <= r < n, else throws out_of_range
    void rangeAddMod(int l, int r, T v) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeAddMod: needs 0 <= l <= r < n");
        T x = norm(v);
        dk[l] = norm(W(dk[l]) + x);
        dk[r + 1] = norm(W(dk[r + 1]) - x);
    }

    // O(1) -- a[i] += v (% MOD); needs 0 <= i < n, else throws out_of_range
    void pointAdd(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointAdd: needs 0 <= i < n");
        rangeAddMod(i, i, v);
    }

    // O(N) -- the whole array with every add so far applied, each value in [0, mod) (a new vector)
    vector<T> getAll() const {
        vector<T> out(a);
        T k = 0, s = 0;
        for (int i = 0; i < n; i++) {
            k = norm(W(k) + dk[i]);
            s = norm(W(s) + ds[i]);
            out[i] = norm(W(out[i]) + k + W(i) * s);
        }
        return out;
    }
};
