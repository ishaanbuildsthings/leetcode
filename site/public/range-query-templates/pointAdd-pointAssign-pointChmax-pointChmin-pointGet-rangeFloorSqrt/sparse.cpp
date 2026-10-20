// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeFloorSqrt/sparse.cpp
// @operations: pointAdd pointAssign pointChmax pointChmin pointGet rangeFloorSqrt
// @data-structure-type: seg-tree
// @complexities:
//   pointAdd: log(U)
//   pointAssign: log(U)
//   pointChmax: log(U)
//   pointChmin: log(U)
//   pointGet: log(U)
//   rangeFloorSqrt: log(U)
//   build: 1
// @memory:
//   layout: sparse
//   node: none
//   tags: tag[4*log(U)]
//   other: children[8*log(U)]
//   note: a pending tag counts floor-sqrts (at most 6 isqrts per point op); per update, the nodes a range update visits (at most 4 per level; a point write creates its path and the path's siblings); a node's one field is its pending tag, or at a leaf its value. One shared node pool, call resetPool() between test cases

// Range floor-sqrt + point ops (values >= 0), over any index range [lo, hi] (huge or negative is fine); every position starts at 0.
// Internal nodes hold a pending tag, leaves hold values. The tags commute, so a range update just tags its
// O(logU) covering nodes and pointGet folds the tags on the leaf's root path. A point write first pushes the tags
// on its path down, so they stop applying to it. Sparse: nodes exist only where updates reached, in one pool
// shared by every SparseRangeFloorSqrtTree<T>.
// A pending tag counts floor-sqrts, capped at 6 (six take any value below 2^64 to 0 or 1, fixed points). T: int, long long, ...
template <typename T>
struct SparseRangeFloorSqrtTree {
    struct Node { T v; int l, r; };  // internal node: pending tag (T(0) = none); leaf: value
    static inline vector<Node> pool{Node{}};  // node 0 is never used: a 0 link means "not created yet"
    long long lo, hi;
    int root;

    // O(1) -- all zeros over [lo, hi]; any long long range works (lo <= hi)
    SparseRangeFloorSqrtTree(long long lo, long long hi) : lo(lo), hi(hi) { root = make(lo == hi); }

    // O(1) -- forget every node of every SparseRangeFloorSqrtTree<T>; call between test cases, then build new trees
    static void resetPool() { pool.resize(1); }

    // optional -- reserve room for this many nodes up front
    static void reservePool(size_t nodes) { pool.reserve(nodes); }

    static int make(bool leaf) {
        pool.push_back(Node{leaf ? T(0) : T(0), 0, 0});
        return (int)pool.size() - 1;
    }

    // child of x (creating it if missing); leaf: whether the child is a single position
    static int kid(int x, bool right, bool leaf) {
        int y = right ? pool[x].r : pool[x].l;
        if (!y) {
            y = make(leaf);
            (right ? pool[x].r : pool[x].l) = y;
        }
        return y;
    }

    static constexpr T MAX_SQRTS = 6;
    static T isqrt(T x) {
        T r = (T)sqrtl((long double)x);
        while ((__int128)r * r > x) r--;
        while ((__int128)(r + 1) * (r + 1) <= x) r++;
        return r;
    }
    static T sqrtTimes(T v, T k) {
        for (; k > 0 && v > 1; k--) v = isqrt(v);
        return v;
    }

    T compose(T a, T v) const { return min(a + v, MAX_SQRTS); }  // tag a, then tag v
    T leaf(T a, T v) const { return sqrtTimes(a, v); }  // value a after tag v

    void apply(int x, bool isLeaf, T v) { pool[x].v = isLeaf ? leaf(pool[x].v, v) : compose(pool[x].v, v); }

    void update(int x, long long a, long long b, long long l, long long r, T v) {
        if (l <= a && b <= r) { apply(x, a == b, v); return; }
        long long m = a + (b - a) / 2;
        if (l <= m) update(kid(x, false, a == m), a, m, l, r, v);
        if (r > m) update(kid(x, true, m + 1 == b), m + 1, b, l, r, v);
    }

    // O(logU) -- a[i] = floor(sqrt(a[i])) for i in [l, r]
    void rangeFloorSqrt(long long l, long long r) {
        if (l <= r) update(root, lo, hi, l, r, T(1));
    }

    // O(logU) -- move the tags on i's root path down (creating the path's siblings); returns i's leaf
    int push(long long i) {
        int y = root;
        long long a = lo, b = hi;
        while (a < b) {
            long long m = a + (b - a) / 2;
            T t = pool[y].v;
            if (t != T(0)) {
                apply(kid(y, false, a == m), a == m, t);
                apply(kid(y, true, m + 1 == b), m + 1 == b, t);
                pool[y].v = T(0);
            }
            if (i <= m) y = kid(y, false, a == m), b = m;
            else y = kid(y, true, m + 1 == b), a = m + 1;
        }
        return y;
    }

    // O(logU) -- a[i]
    T pointGet(long long i) const {
        T t = T(0), x = 0;
        int y = root;
        long long a = lo, b = hi;
        while (y) {
            if (a == b) { x = pool[y].v; break; }
            t = compose(t, pool[y].v);
            long long m = a + (b - a) / 2;
            if (i <= m) y = pool[y].l, b = m;
            else y = pool[y].r, a = m + 1;
        }
        return leaf(x, t);
    }

    // O(logU) -- a[i] = v
    void pointAssign(long long i, T v) {
        int p = push(i);
        pool[p].v = v;
    }

    // O(logU) -- a[i] += delta
    void pointAdd(long long i, T delta) {
        int p = push(i);
        pool[p].v = pool[p].v + delta;
    }

    // O(logU) -- a[i] = max(a[i], v)
    void pointChmax(long long i, T v) {
        int p = push(i);
        if (v > pool[p].v) pool[p].v = v;
    }

    // O(logU) -- a[i] = min(a[i], v)
    void pointChmin(long long i, T v) {
        int p = push(i);
        if (v < pool[p].v) pool[p].v = v;
    }
};
