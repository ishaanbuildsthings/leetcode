// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeMod/sparse.cpp
// @operations: pointAdd pointAssign pointChmax pointChmin pointGet rangeMod
// @data-structure-type: seg-tree
// @complexities:
//   pointAdd: log(U)
//   pointAssign: log(U)
//   pointChmax: log(U)
//   pointChmin: log(U)
//   pointGet: log(U)
//   rangeMod: log(U)*log(U) amortized
//   build: 1
// @memory:
//   layout: sparse
//   node: mx[1*log(U)]
//   tags: none
//   other: children[2*log(U)]
//   note: per point write, one node per level of its path (rangeMod creates nothing); rangeMod's second log is of the largest value. A node pool per tree (node 0 = all zeros)

// Range mod + point ops over any index range [lo, hi] (huge or negative is fine); every position starts at 0. Requires
// a[i] >= 0, mod >= 1. Mods don't compose into one tag, so rangeMod descends into every node in range whose max is
// still >= mod; each value that changes at least halves, so the work is amortized. Sparse: nodes in a pool the tree
// owns; node 0 is the all-zeros block, which rangeMod never enters. T: int, long long, ...
template <typename T>
struct SparseRangeModTree {
    struct Node { T mx; int l, r; };  // max of the subtree
    vector<Node> pool{Node{}};  // node 0: all zeros, its children are itself
    long long lo, hi;
    int root = 0;
    int path[130];

    // O(1) -- all zeros over [lo, hi]; any long long range works (lo <= hi)
    SparseRangeModTree(long long lo, long long hi) : lo(lo), hi(hi) {}


    // optional -- reserve room for this many nodes up front
    void reservePool(size_t nodes) { pool.reserve(nodes); }

    int make() {
        pool.push_back(Node{T(0), 0, 0});
        return (int)pool.size() - 1;
    }

    void pull(int x) { pool[x].mx = max(pool[pool[x].l].mx, pool[pool[x].r].mx); }

    void modRec(int x, long long a, long long b, long long l, long long r, T mod) {
        if (pool[x].mx < mod) return;  // includes node 0
        if (a == b) { pool[x].mx %= mod; return; }
        long long m = a + (b - a) / 2;
        if (l <= m) modRec(pool[x].l, a, m, l, r, mod);
        if (r > m) modRec(pool[x].r, m + 1, b, l, r, mod);
        pull(x);
    }

    // amortized O(logU logV) -- a[i] %= mod for i in [l, r]
    void rangeMod(long long l, long long r, T mod) {
        if (l <= r) modRec(root, lo, hi, l, r, mod);
    }

    // O(logU) -- a[i]
    T pointGet(long long i) const {
        int y = root;
        long long a = lo, b = hi;
        while (y && a < b) {
            long long m = a + (b - a) / 2;
            if (i <= m) y = pool[y].l, b = m;
            else y = pool[y].r, a = m + 1;
        }
        return pool[y].mx;
    }

    // O(logU) -- create i's path (path[0] = root), returns its depth
    int descend(long long i) {
        if (!root) root = make();
        int y = root, d = 0;
        path[0] = y;
        long long a = lo, b = hi;
        while (a < b) {
            long long m = a + (b - a) / 2;
            bool right = i > m;
            int c = right ? pool[y].r : pool[y].l;
            if (!c) {
                c = make();
                (right ? pool[y].r : pool[y].l) = c;
            }
            y = path[++d] = c;
            if (right) a = m + 1;
            else b = m;
        }
        return d;
    }

    // O(logU) -- a[i] = v
    void pointAssign(long long i, T v) {
        int d = descend(i);
        pool[path[d]].mx = v;
        while (d--) pull(path[d]);
    }

    // O(logU) -- a[i] += delta
    void pointAdd(long long i, T delta) { pointAssign(i, pointGet(i) + delta); }

    // O(logU) -- a[i] = max(a[i], v)
    void pointChmax(long long i, T v) { if (v > pointGet(i)) pointAssign(i, v); }

    // O(logU) -- a[i] = min(a[i], v)
    void pointChmin(long long i, T v) { if (v < pointGet(i)) pointAssign(i, v); }
};
