// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/pointAdd-rangeAdd-rangeAddArithSeq/template.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: getAll pointAdd rangeAdd rangeAddArithSeq
// @data-structure-type: difference-array
// @complexities:
//   getAll: N
//   pointAdd: 1
//   rangeAdd: 1
//   rangeAddArithSeq: 1
//   build: N
// @memory:
//   layout: none
//   node: dk[1*N] ds[1*N]
//   tags: none
//   other: a[1*N]
//   note: every add is a line k + s * i over [l, r]; dk and ds are difference arrays of k and s, and getAll sweeps both

// Range add and arithmetic sequence add, then read the array: two difference arrays (a double sweep line). An add of
// start, start + step, ... over [l, r] is the line k + step * i with k = start - l * step, so it is O(1): k and step go
// into one difference array each, and getAll sweeps both and adds k + step * i at every i, O(N). getAll can be called
// again later (the adds are kept). Nothing reads a single value in between: for that, use a BIT or seg tree. All
// indices 0-based, ranges inclusive [l, r].
// T: int, long long, ...
template <typename T>
struct DiffArrayArith {
    int n;
    vector<T> a, dk, ds;

    // O(N) -- arr: the initial array (can be empty)
    explicit DiffArrayArith(const vector<T>& arr) : n((int)arr.size()), a(arr), dk(n + 1), ds(n + 1) {}

    // O(1) -- a[l + j] += start + j * step for j in [0, r - l]; needs 0 <= l <= r < n, else throws out_of_range
    void rangeAddArithSeq(int l, int r, T start, T step) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeAddArithSeq: needs 0 <= l <= r < n");
        T k = start - T(l) * step;
        dk[l] += k;
        dk[r + 1] -= k;
        ds[l] += step;
        ds[r + 1] -= step;
    }

    // O(1) -- a[i] += v for i in [l, r]; needs 0 <= l <= r < n, else throws out_of_range
    void rangeAdd(int l, int r, T v) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeAdd: needs 0 <= l <= r < n");
        dk[l] += v;
        dk[r + 1] -= v;
    }

    // O(1) -- a[i] += v; needs 0 <= i < n, else throws out_of_range
    void pointAdd(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointAdd: needs 0 <= i < n");
        dk[i] += v;
        dk[i + 1] -= v;
    }

    // O(N) -- the whole array with every add so far applied (a new vector)
    vector<T> getAll() const {
        vector<T> out(a);
        T k = 0, s = 0;
        for (int i = 0; i < n; i++) {
            k += dk[i];
            s += ds[i];
            out[i] += k + s * T(i);
        }
        return out;
    }
};
