// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeOrApply/template.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: getAll pointAdd pointAssign pointChmax pointChmin pointGet rangeOrApply
// @data-structure-type: seg-tree
// @complexities:
//   getAll: N
//   pointAdd: log(N)
//   pointAssign: log(N)
//   pointChmax: log(N)
//   pointChmin: log(N)
//   pointGet: log(N)
//   rangeOrApply: log(N)
//   build: N
// @memory:
//   layout: 2n-iterative
//   node: tree[1*N]
//   tags: tree[1*N]
//   other: none
//   note: tree[n:] holds the values, tree[1:n] holds each node's pending rangeOrApply tag (no aggregates); leaves count as node data, internal nodes as tags

// rangeOrApply + point ops with no range aggregates. All indices 0-based, ranges inclusive [l, r].
// rangeOrApply composes with itself in any order, so a range update only tags the O(logN) covering nodes and
// pointGet folds the tags on the leaf-to-root path. Only overwrites (pointAssign etc.) push those tags off
// the path first, so they aren't re-applied to the new value. T: int, long long, ...
template <typename T>
struct RangeOrTree {
    int n;
    vector<T> tree;  // tree[n + i] = a[i]; tree[1 .. n-1] = pending tag (identity T(0))

    // O(N)
    explicit RangeOrTree(const vector<T>& a) : n((int)a.size()), tree(2 * a.size(), T(0)) {
        for (int i = 0; i < n; i++) tree[n + i] = a[i];
    }

    // O(logN) -- a[i] |= x for i in [l, r]; needs 0 <= l <= r < n, else throws out_of_range
    void rangeOrApply(int l, int r, T x) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeOrApply: needs 0 <= l <= r < n");
        for (l += n, r += n + 1; l < r; l >>= 1, r >>= 1) {
            if (l & 1) { tree[l] = (tree[l] | x); l++; }
            if (r & 1) { --r; tree[r] = (tree[r] | x); }
        }
    }

    // O(logN) -- move the tags on leaf p's root-to-leaf path down, so nothing above p is pending
    void push(int p) {
        for (int h = 31 - __builtin_clz(p); h > 0; h--) {
            int x = p >> h;
            T t = tree[x];
            if (t != T(0)) {
                tree[2 * x] = (tree[2 * x] | t);
                tree[2 * x + 1] = (tree[2 * x + 1] | t);
                tree[x] = T(0);
            }
        }
    }

    // O(logN) -- a[i]; needs 0 <= i < n, else throws out_of_range
    T pointGet(int i) const {
        if (i < 0 || i >= n) throw out_of_range("pointGet: needs 0 <= i < n");
        int p = i + n;
        T a = tree[p];
        for (p >>= 1; p; p >>= 1) a = (a | tree[p]);
        return a;
    }

    // O(N) -- the whole array: push every tag down (a parent's index is below its children's, so in index order
    // each node's tag is complete when it is pushed), then read the leaves
    vector<T> getAll() {
        for (int x = 1; x < n; x++) {
            T t = tree[x];
            if (t != T(0)) {
                tree[2 * x] = (tree[2 * x] | t);
                tree[2 * x + 1] = (tree[2 * x + 1] | t);
                tree[x] = T(0);
            }
        }
        return vector<T>(tree.begin() + n, tree.end());
    }

    // O(logN) -- a[i] = val; needs 0 <= i < n, else throws out_of_range
    void pointAssign(int i, T val) {
        if (i < 0 || i >= n) throw out_of_range("pointAssign: needs 0 <= i < n");
        int p = i + n;
        push(p);
        tree[p] = val;
    }

    // O(logN) -- a[i] += delta; needs 0 <= i < n, else throws out_of_range
    void pointAdd(int i, T delta) {
        if (i < 0 || i >= n) throw out_of_range("pointAdd: needs 0 <= i < n");
        int p = i + n;
        push(p);
        tree[p] = tree[p] + delta;
    }

    // O(logN) -- a[i] = max(a[i], v); needs 0 <= i < n, else throws out_of_range
    void pointChmax(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointChmax: needs 0 <= i < n");
        int p = i + n;
        push(p);
        if (v > tree[p]) tree[p] = v;
    }

    // O(logN) -- a[i] = min(a[i], v); needs 0 <= i < n, else throws out_of_range
    void pointChmin(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointChmin: needs 0 <= i < n");
        int p = i + n;
        push(p);
        if (v < tree[p]) tree[p] = v;
    }
};
