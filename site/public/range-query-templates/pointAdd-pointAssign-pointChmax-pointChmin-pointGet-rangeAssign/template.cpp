// @operations: pointAdd pointAssign pointChmax pointChmin pointGet rangeAssign
// @data-structure-type: seg-tree
// @complexities:
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

    // O(logN) -- a[i] = v for i in [l, r]
    void rangeAssign(int l, int r, T v) {
        int c = ++clock;
        for (l += n, r += n + 1; l < r; l >>= 1, r >>= 1) {
            if (l & 1) stamp[l] = c, val[l] = v, l++;
            if (r & 1) --r, stamp[r] = c, val[r] = v;
        }
    }

    // O(logN) -- a[i]
    T pointGet(int i) const {
        int p = i + n, best = stamp[p];
        T res = val[p];
        for (p >>= 1; p; p >>= 1)
            if (stamp[p] > best) best = stamp[p], res = val[p];
        return res;
    }

    // O(1) -- a[i] = v
    void pointAssign(int i, T v) { stamp[i + n] = ++clock, val[i + n] = v; }

    // O(logN) -- a[i] += delta
    void pointAdd(int i, T delta) { pointAssign(i, pointGet(i) + delta); }

    // O(logN) -- a[i] = max(a[i], v)
    void pointChmax(int i, T v) { if (v > pointGet(i)) pointAssign(i, v); }

    // O(logN) -- a[i] = min(a[i], v)
    void pointChmin(int i, T v) { if (v < pointGet(i)) pointAssign(i, v); }
};
