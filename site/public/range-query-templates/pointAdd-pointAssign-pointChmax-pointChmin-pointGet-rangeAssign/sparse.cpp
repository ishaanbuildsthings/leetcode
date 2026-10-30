// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAssign/sparse.cpp
// @operations: pointAdd pointAssign pointChmax pointChmin pointGet rangeAssign
// @data-structure-type: seg-tree
// @complexities:
//   pointAdd: log(U)
//   pointAssign: log(U)
//   pointChmax: log(U)
//   pointChmin: log(U)
//   pointGet: log(U)
//   rangeAssign: log(U)
//   build: 1
// @memory:
//   layout: sparse
//   node: none
//   tags: stamp[4*log(U)] val[4*log(U)]
//   other: children[8*log(U)]
//   note: per update, the nodes a range update visits (at most 4 per level), each remembering the newest assignment covering it. A node pool per tree

// Range assign + point ops over any index range [lo, hi] (huge or negative is fine); every position starts at 0. No
// pushing anywhere: assignments are stamped with an increasing counter, every node remembers the newest one covering
// it, and pointGet returns the newest on the leaf's root path. Sparse: nodes exist only where updates reached, in a
// pool the tree owns. T: int, long long, ...
template <typename T>
struct SparseRangeAssignTree {
    struct Node { int stamp; T v; int l, r; };  // the newest assignment covering the node (stamp 0: none)
    vector<Node> pool{Node{}};  // node 0 is never used: a 0 link means "not created yet"
    long long lo, hi;
    int root, clock = 0;

    // O(1) -- all zeros over [lo, hi]; any long long range works (lo <= hi)
    SparseRangeAssignTree(long long lo, long long hi) : lo(lo), hi(hi) { root = make(); }


    // optional -- reserve room for this many nodes up front
    void reservePool(size_t nodes) { pool.reserve(nodes); }

    int make() {
        pool.push_back(Node{0, T(0), 0, 0});
        return (int)pool.size() - 1;
    }

    // child of x, creating it if missing
    int kid(int x, bool right) {
        int y = right ? pool[x].r : pool[x].l;
        if (!y) {
            y = make();
            (right ? pool[x].r : pool[x].l) = y;
        }
        return y;
    }

    void update(int x, long long a, long long b, long long l, long long r, int c, T v) {
        if (l <= a && b <= r) { pool[x].stamp = c, pool[x].v = v; return; }
        long long m = a + (b - a) / 2;
        if (l <= m) update(kid(x, false), a, m, l, r, c, v);
        if (r > m) update(kid(x, true), m + 1, b, l, r, c, v);
    }

    // O(logU) -- a[i] = v for i in [l, r]
    void rangeAssign(long long l, long long r, T v) {
        if (l <= r) update(root, lo, hi, l, r, ++clock, v);
    }

    // O(logU) -- a[i]
    T pointGet(long long i) const {
        int y = root, best = 0;
        T res = 0;
        long long a = lo, b = hi;
        while (y) {
            if (pool[y].stamp > best) best = pool[y].stamp, res = pool[y].v;
            if (a == b) break;
            long long m = a + (b - a) / 2;
            if (i <= m) y = pool[y].l, b = m;
            else y = pool[y].r, a = m + 1;
        }
        return res;
    }

    // O(logU) -- a[i] = v
    void pointAssign(long long i, T v) {
        int y = root;
        long long a = lo, b = hi;
        while (a < b) {
            long long m = a + (b - a) / 2;
            if (i <= m) y = kid(y, false), b = m;
            else y = kid(y, true), a = m + 1;
        }
        pool[y].stamp = ++clock, pool[y].v = v;
    }

    // O(logU) -- a[i] += delta
    void pointAdd(long long i, T delta) { pointAssign(i, pointGet(i) + delta); }

    // O(logU) -- a[i] = max(a[i], v)
    void pointChmax(long long i, T v) { if (v > pointGet(i)) pointAssign(i, v); }

    // O(logU) -- a[i] = min(a[i], v)
    void pointChmin(long long i, T v) { if (v < pointGet(i)) pointAssign(i, v); }
};
