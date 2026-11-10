// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/pointAdd-rangeAdd/template.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: getAll pointAdd rangeAdd
// @data-structure-type: difference-array
// @complexities:
//   getAll: N
//   pointAdd: 1
//   rangeAdd: 1
//   build: N
// @memory:
//   layout: none
//   node: d[1*N]
//   tags: none
//   other: a[1*N]
//   note: d is the difference array of every add so far (d[l] += v, d[r+1] -= v); getAll sweeps it once

// Range add, then read the array: a difference array (a sweep line). Every add is O(1); getAll is one O(N) prefix sum
// pass over the adds, and it can be called again later (the adds are kept). Nothing reads a single value in between:
// for that, use a BIT or seg tree. All indices 0-based, ranges inclusive [l, r].
// T: int, long long, ...
template <typename T>
struct DiffArray {
    int n;
    vector<T> a, d;

    // O(N) -- arr: the initial array (can be empty)
    explicit DiffArray(const vector<T>& arr) : n((int)arr.size()), a(arr), d(n + 1) {}

    // O(1) -- a[i] += v for i in [l, r]; needs 0 <= l <= r < n, else throws out_of_range
    void rangeAdd(int l, int r, T v) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeAdd: needs 0 <= l <= r < n");
        d[l] += v;
        d[r + 1] -= v;
    }

    // O(1) -- a[i] += v; needs 0 <= i < n, else throws out_of_range
    void pointAdd(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointAdd: needs 0 <= i < n");
        d[i] += v;
        d[i + 1] -= v;
    }

    // O(N) -- the whole array with every add so far applied (a new vector)
    vector<T> getAll() const {
        vector<T> out(a);
        T run = 0;
        for (int i = 0; i < n; i++) {
            run += d[i];
            out[i] += run;
        }
        return out;
    }
};
