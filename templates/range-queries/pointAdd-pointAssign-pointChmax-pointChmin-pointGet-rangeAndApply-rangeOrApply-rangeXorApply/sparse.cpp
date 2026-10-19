// @operations: pointAdd pointAssign pointChmax pointChmin pointGet rangeAndApply rangeOrApply rangeXorApply
// @data-structure-type: lazy-seg-tree
// @complexities:
//   pointAdd: log(U)
//   pointAssign: log(U)
//   pointChmax: log(U)
//   pointChmin: log(U)
//   pointGet: log(U)
//   rangeAndApply: log(U)
//   rangeOrApply: log(U)
//   rangeXorApply: log(U)
//   build: 1
// @memory:
//   layout: sparse
//   node: v[4*log(U)]
//   tags: a[4*log(U)] x[4*log(U)]
//   other: links[8*log(U)]
//   note: per update, the nodes it visits (at most 4 per level, counting the children a push creates); queries create nothing. a leaf's value is v (internal nodes keep no aggregate). C++: one shared node pool (node 0 = all zeros), call resetPool() between test cases; Python: lists of nodes

// Range and= / or= / xor= + point ops. Every update is a bit map v -> (v & a) ^ x (and X = (X, 0),
// or X = (~X, X), xor X = (all ones, X)), and these maps compose into the same form. Only leaves' values
// matter, so nothing is pulled.
// Over any index range [lo, hi] (huge or negative is fine); every position starts at 0. Updates push a node's
// tag into its children (creating them) before recursing past it; queries never push: they carry the
// ancestors' tags down and apply them to what they return, so they create no nodes. Sparse: nodes exist only
// where updates reached, in one pool shared by every SparseBitOpTree<T>; node 0 is the shared all-zeros block.
// T: int, long long, ...
template <typename T>
struct SparseBitOpTree {
    struct Agg { T v; };
    struct Tag { T a, x; };  // v -> (v & a) ^ x
    static constexpr Tag ID = Tag{T(-1), 0};
    struct Node { Agg v; Tag t; int l, r; };
    static inline vector<Node> pool{Node{Agg{}, ID, 0, 0}};  // node 0: all zeros, its children are itself
    long long lo, hi;
    int root;

    // O(1) -- all zeros over [lo, hi]; any long long range works (lo <= hi)
    SparseBitOpTree(long long lo, long long hi) : lo(lo), hi(hi) { root = make(); }

    // O(1) -- forget every node of every SparseBitOpTree<T>; call between test cases, then build new trees
    static void resetPool() { pool.resize(1); }

    // optional -- reserve room for this many nodes up front
    static void reservePool(size_t nodes) { pool.reserve(nodes); }

    static int make() {
        pool.push_back(Node{Agg{}, ID, 0, 0});
        return (int)pool.size() - 1;
    }

    // child of x, creating it (as a block of zeros) if missing
    static int kid(int x, bool right) {
        int y = right ? pool[x].r : pool[x].l;
        if (!y) {
            y = make();
            (right ? pool[x].r : pool[x].l) = y;
        }
        return y;
    }

    static bool isId(const Tag& t) { return t.a == T(-1) && t.x == 0; }

    // tag o, then tag t
    static Tag compose(const Tag& o, const Tag& t) { return Tag{T(o.a & t.a), T((o.x & t.a) ^ t.x)}; }

    // the aggregate of k slots after tag t
    static Agg applyTag(Agg v, long long k, const Tag& t) {
        (void)k;
        v.v = (v.v & t.a) ^ t.x;
        return v;
    }

    // node x (k slots) takes tag t: its aggregate now, its children later
    void applyNode(int x, long long k, const Tag& t) {
        pool[x].v = applyTag(pool[x].v, k, t);
        pool[x].t = compose(pool[x].t, t);
    }

    // move x's tag (x covers [a, b]) into its children, creating them
    void push(int x, long long a, long long b) {
        if (isId(pool[x].t)) return;
        Tag t = pool[x].t;
        long long m = a + (b - a) / 2;
        applyNode(kid(x, false), m - a + 1, t);
        applyNode(kid(x, true), b - m, t);
        pool[x].t = ID;
    }

    void update(int x, long long a, long long b, long long l, long long r, const Tag& t) {
        if (l <= a && b <= r) { applyNode(x, b - a + 1, t); return; }
        push(x, a, b);
        long long m = a + (b - a) / 2;
        if (l <= m) update(kid(x, false), a, m, l, r, t);
        if (r > m) update(kid(x, true), m + 1, b, l, r, t);
    }

    // aggregate of a[max(l, a)..min(r, b)] under node x (covering [a, b]), with t, the ancestors' pending tags, on top
    Agg query(int x, long long a, long long b, long long l, long long r, const Tag& t) const {
        if (!x) return applyTag(Agg{}, std::min(r, b) - std::max(l, a) + 1, t);
        if (l <= a && b <= r) return applyTag(pool[x].v, b - a + 1, t);
        Tag down = compose(pool[x].t, t);
        long long m = a + (b - a) / 2;
        if (r <= m) return query(pool[x].l, a, m, l, r, down);
        return query(pool[x].r, m + 1, b, l, r, down);
    }

    // O(logU) -- a[i] &= X for i in [l, r]
    void rangeAndApply(long long l, long long r, T X) {
        if (l <= r) update(root, lo, hi, l, r, Tag{X, 0});
    }

    // O(logU) -- a[i] |= X for i in [l, r]
    void rangeOrApply(long long l, long long r, T X) {
        if (l <= r) update(root, lo, hi, l, r, Tag{T(~X), X});
    }

    // O(logU) -- a[i] ^= X for i in [l, r]
    void rangeXorApply(long long l, long long r, T X) {
        if (l <= r) update(root, lo, hi, l, r, Tag{T(-1), X});
    }

    // O(logU) -- a[i]
    T pointGet(long long i) const {
        Agg res = query(root, lo, hi, i, i, ID);
        return res.v;
    }

    // O(logU) -- a[i] = v
    void pointAssign(long long i, T v) {
        int path[130], d = 0, y = root;
        long long a = lo, b = hi;
        while (a < b) {
            push(y, a, b);
            path[d++] = y;
            long long m = a + (b - a) / 2;
            if (i <= m) y = kid(y, false), b = m;
            else y = kid(y, true), a = m + 1;
        }
        pool[y].v = Agg{v};
        (void)path;
    }

    // O(logU) -- a[i] += delta
    void pointAdd(long long i, T delta) { pointAssign(i, pointGet(i) + delta); }

    // O(logU) -- a[i] = max(a[i], v)
    void pointChmax(long long i, T v) { if (v > pointGet(i)) pointAssign(i, v); }

    // O(logU) -- a[i] = min(a[i], v)
    void pointChmin(long long i, T v) { if (v < pointGet(i)) pointAssign(i, v); }
};
