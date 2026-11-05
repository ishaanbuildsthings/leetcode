// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAdd-rangeChmin/template.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: getAll pointAdd pointAssign pointChmax pointChmin pointGet rangeAdd rangeChmin
// @data-structure-type: lazy-seg-tree
// @complexities:
//   getAll: N
//   pointAdd: log(N)
//   pointAssign: log(N)
//   pointChmax: log(N)
//   pointChmin: log(N)
//   pointGet: log(N)
//   rangeAdd: log(N)
//   rangeChmin: log(N)
//   build: N
// @memory:
//   layout: 2n-iterative
//   node: val[1*N]
//   tags: A[1*N] C[1*N]
//   other: none
//   note: each internal node holds one pending clamp x -> min(A, x + C); val holds the leaf values

// Range add / chmin + point ops, no range aggregates. All indices 0-based, ranges inclusive.
// Every update is a clamp x -> min(A, x + C); clamps compose into a clamp, but not commutatively, so before tagging
// the covering nodes we push the tags on the paths to l and r (the standard 2N trick for point reads).
// T: int, long long, ...; values must stay strictly inside (min(T), max(T)), which are the sentinels.
template <typename T>
struct AddChminTree {
    static constexpr T INF = numeric_limits<T>::max(), NINF = numeric_limits<T>::lowest();
    int n;
    vector<T> A, C;  // internal nodes 1 .. n-1: pending clamp x -> min(A, x + C)
    vector<T> val;  // leaf values

    // O(N)
    explicit AddChminTree(const vector<T>& a) : n((int)a.size()), A(a.size(), INF), C(a.size(), T(0)), val(a) {}

    // apply clamp (a, c) on top of whatever node x already holds
    void apply(int x, T a, T c) {
        if (x >= n) { val[x - n] = min(a, val[x - n] + c); return; }
        A[x] = min(a, A[x] == INF ? INF : A[x] + c);
        C[x] += c;
    }

    // O(logN) -- push every pending tag on leaf p's root-to-leaf path down to its children
    void push(int p) {
        for (int h = 31 - __builtin_clz(p); h > 0; h--) {
            int x = p >> h;
            if (A[x] != INF || C[x] != T(0)) apply(2 * x, A[x], C[x]), apply(2 * x + 1, A[x], C[x]), A[x] = INF, C[x] = T(0);
        }
    }

    void update(int l, int r, T a, T c) {
        l += n, r += n;
        push(l), push(r);
        for (r++; l < r; l >>= 1, r >>= 1) {
            if (l & 1) apply(l++, a, c);
            if (r & 1) apply(--r, a, c);
        }
    }

    // O(logN) -- a[i] += v for i in [l, r]; needs 0 <= l <= r < n, else throws out_of_range
    void rangeAdd(int l, int r, T v) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeAdd: needs 0 <= l <= r < n");
        update(l, r, INF, v);
    }

    // O(logN) -- a[i] = min(a[i], v) for i in [l, r]; needs 0 <= l <= r < n, else throws out_of_range
    void rangeChmin(int l, int r, T v) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeChmin: needs 0 <= l <= r < n");
        update(l, r, v, T(0));
    }

    // O(logN) -- a[i]: start from the leaf and apply ancestors' clamps bottom-up (deeper tags are older); needs
    // 0 <= i < n, else throws out_of_range
    T pointGet(int i) const {
        if (i < 0 || i >= n) throw out_of_range("pointGet: needs 0 <= i < n");
        T v = val[i];
        for (int p = (i + n) >> 1; p; p >>= 1) v = min(A[p], v + C[p]);
        return v;
    }

    // O(N) -- the whole array: push every tag down (a parent's index is below its children's, so in index order
    // each node's tag is complete when it is pushed), then read the leaves
    vector<T> getAll() {
        for (int x = 1; x < n; x++)
            if (A[x] != INF || C[x] != T(0)) apply(2 * x, A[x], C[x]), apply(2 * x + 1, A[x], C[x]), A[x] = INF, C[x] = T(0);
        return val;
    }

    // O(logN) -- a[i] = v; needs 0 <= i < n, else throws out_of_range
    void pointAssign(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointAssign: needs 0 <= i < n");
        push(i + n); val[i] = v;
    }

    // O(logN) -- a[i] += delta; needs 0 <= i < n, else throws out_of_range
    void pointAdd(int i, T delta) {
        if (i < 0 || i >= n) throw out_of_range("pointAdd: needs 0 <= i < n");
        push(i + n); val[i] = val[i] + delta;
    }

    // O(logN) -- a[i] = max(a[i], v); needs 0 <= i < n, else throws out_of_range
    void pointChmax(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointChmax: needs 0 <= i < n");
        push(i + n); if (v > val[i]) val[i] = v;
    }

    // O(logN) -- a[i] = min(a[i], v); needs 0 <= i < n, else throws out_of_range
    void pointChmin(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointChmin: needs 0 <= i < n");
        push(i + n); if (v < val[i]) val[i] = v;
    }
};
