// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAssign/template.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: getAll pointAdd pointAssign pointChmax pointChmin pointGet rangeAssign
// @data-structure-type: seg-tree
// @letters: same
// @complexities:
//   getAll: N
//   pointAdd: log(N)
//   pointAssign: 1
//   pointChmax: log(N)
//   pointChmin: log(N)
//   pointGet: log(N)
//   rangeAssign: log(N)
//   build: N
// @memory:
//   layout: 2n-iterative
//   node: stamp[1*N] val[1*N]
//   tags: stamp[1*N] val[1*N]
//   other: none
//   note: every node remembers the last assignment that covered it and when; a point takes the newest one on its path; leaves count as node data, internal nodes as tags

// Range assign + point ops, no pushing anywhere. All indices 0-based, ranges inclusive [l, r].
// Assignments are stamped with an increasing counter; pointGet returns the value with the largest stamp
// among the leaf and its ancestors. A point write is just a newer stamp on the leaf, so it is O(1).
// T: int, long long, ...
template <typename T>
struct RangeAssignTree {
    int n, clock = 0;
    vector<int> stamp;  // stamp[x] = when node x was last assigned (-1 never, leaves start at 0)
    vector<T> val;      // val[x] = what it was assigned to; val[n + i] starts as a[i]

    // O(N)
    explicit RangeAssignTree(const vector<T>& a) : n((int)a.size()), stamp(2 * a.size(), -1), val(2 * a.size()) {
        for (int i = 0; i < n; i++) stamp[n + i] = 0, val[n + i] = a[i];
    }

    // O(logN) -- a[i] = v for i in [l, r]; needs 0 <= l <= r < n, else throws out_of_range
    void rangeAssign(int l, int r, T v) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeAssign: needs 0 <= l <= r < n");
        int c = ++clock;
        for (l += n, r += n + 1; l < r; l >>= 1, r >>= 1) {
            if (l & 1) stamp[l] = c, val[l] = v, l++;
            if (r & 1) --r, stamp[r] = c, val[r] = v;
        }
    }

    // O(logN) -- a[i]; needs 0 <= i < n, else throws out_of_range
    T pointGet(int i) const {
        if (i < 0 || i >= n) throw out_of_range("pointGet: needs 0 <= i < n");
        int p = i + n, best = stamp[p];
        T res = val[p];
        for (p >>= 1; p; p >>= 1)
            if (stamp[p] > best) best = stamp[p], res = val[p];
        return res;
    }

    // O(N) -- the whole array: hand each node's assign to its children when it is newer than theirs (a parent's
    // index is below its children's, so in index order each node already holds the newest assign on its path)
    vector<T> getAll() {
        for (int x = 2; x < 2 * n; x++)
            if (stamp[x >> 1] > stamp[x]) stamp[x] = stamp[x >> 1], val[x] = val[x >> 1];
        return vector<T>(val.begin() + n, val.end());
    }

    // O(1) -- a[i] = v; needs 0 <= i < n, else throws out_of_range
    void pointAssign(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointAssign: needs 0 <= i < n");
        stamp[i + n] = ++clock, val[i + n] = v;
    }

    // O(logN) -- a[i] += delta; needs 0 <= i < n, else throws out_of_range
    void pointAdd(int i, T delta) {
        if (i < 0 || i >= n) throw out_of_range("pointAdd: needs 0 <= i < n");
        pointAssign(i, pointGet(i) + delta);
    }

    // O(logN) -- a[i] = max(a[i], v); needs 0 <= i < n, else throws out_of_range
    void pointChmax(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointChmax: needs 0 <= i < n");
        if (v > pointGet(i)) pointAssign(i, v);
    }

    // O(logN) -- a[i] = min(a[i], v); needs 0 <= i < n, else throws out_of_range
    void pointChmin(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointChmin: needs 0 <= i < n");
        if (v < pointGet(i)) pointAssign(i, v);
    }
};
