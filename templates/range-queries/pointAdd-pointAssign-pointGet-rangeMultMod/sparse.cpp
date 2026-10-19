// @operations: pointAdd pointAssign pointGet rangeMultMod
// @data-structure-type: seg-tree
// @complexities:
//   pointAdd: log(U)
//   pointAssign: log(U)
//   pointGet: log(U)
//   rangeMultMod: log(U)
//   build: 1
// @memory:
//   layout: sparse
//   node: none
//   tags: tag[4*log(U)]
//   other: links[8*log(U)]
//   note: per update, the nodes a range update visits (at most 4 per level; a point write creates its path and the path's siblings); a node's one field is its pending tag, or at a leaf its value. C++: one shared node pool, call resetPool() between test cases; Python: a dict keyed by heap index

// rangeMultMod + point ops (values in [0, mod)), over any index range [lo, hi] (huge or negative is fine); every position starts at 0.
// Internal nodes hold a pending tag, leaves hold values. The tags commute, so a range update just tags its
// O(logU) covering nodes and pointGet folds the tags on the leaf's root path. A point write first pushes the tags
// on its path down, so they stop applying to it. Sparse: nodes exist only where updates reached, in one pool
// shared by every SparseRangeMultModTree<T>. T: int, long long, ...
template <typename T>
struct SparseRangeMultModTree {
    struct Node { T v; int l, r; };  // internal node: pending tag (T(1) = none); leaf: value
    static inline vector<Node> pool{Node{}};  // node 0 is never used: a 0 link means "not created yet"
    long long lo, hi;
    int root;
    T mod;

    // O(1) -- all zeros over [lo, hi]; any long long range works (lo <= hi)
    SparseRangeMultModTree(long long lo, long long hi, T mod = 1000000007) : lo(lo), hi(hi), mod(mod) { root = make(lo == hi); }

    // O(1) -- forget every node of every SparseRangeMultModTree<T>; call between test cases, then build new trees
    static void resetPool() { pool.resize(1); }

    // optional -- reserve room for this many nodes up front
    static void reservePool(size_t nodes) { pool.reserve(nodes); }

    static int make(bool leaf) {
        pool.push_back(Node{leaf ? T(0) : T(1), 0, 0});
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

    using W = conditional_t<sizeof(T) <= 4, long long, __int128>;
    T norm(W x) const { return T((x % mod + mod) % mod); }

    T compose(T a, T v) const { return T(W(a) * v % mod); }  // tag a, then tag v
    T leaf(T a, T v) const { return T(W(a) * v % mod); }  // value a after tag v

    void apply(int x, bool isLeaf, T v) { pool[x].v = isLeaf ? leaf(pool[x].v, v) : compose(pool[x].v, v); }

    void update(int x, long long a, long long b, long long l, long long r, T v) {
        if (l <= a && b <= r) { apply(x, a == b, v); return; }
        long long m = a + (b - a) / 2;
        if (l <= m) update(kid(x, false, a == m), a, m, l, r, v);
        if (r > m) update(kid(x, true, m + 1 == b), m + 1, b, l, r, v);
    }

    // O(logU) -- a[i] = a[i] * v (mod p) for i in [l, r]
    void rangeMultMod(long long l, long long r, T v) {
        v = norm(v);
        if (l <= r) update(root, lo, hi, l, r, v);
    }

    // O(logU) -- move the tags on i's root path down (creating the path's siblings); returns i's leaf
    int push(long long i) {
        int y = root;
        long long a = lo, b = hi;
        while (a < b) {
            long long m = a + (b - a) / 2;
            T t = pool[y].v;
            if (t != T(1)) {
                apply(kid(y, false, a == m), a == m, t);
                apply(kid(y, true, m + 1 == b), m + 1 == b, t);
                pool[y].v = T(1);
            }
            if (i <= m) y = kid(y, false, a == m), b = m;
            else y = kid(y, true, m + 1 == b), a = m + 1;
        }
        return y;
    }

    // O(logU) -- a[i]
    T pointGet(long long i) const {
        T t = T(1), x = 0;
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
        pool[p].v = norm(v);
    }

    // O(logU) -- a[i] += delta
    void pointAdd(long long i, T delta) {
        int p = push(i);
        pool[p].v = norm(W(pool[p].v) + delta);
    }
};
