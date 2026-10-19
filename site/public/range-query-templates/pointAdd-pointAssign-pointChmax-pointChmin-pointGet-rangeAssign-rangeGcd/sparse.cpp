// @operations: pointAdd pointAssign pointChmax pointChmin pointGet rangeAssign rangeGcd
// @data-structure-type: lazy-seg-tree
// @complexities:
//   pointAdd: log(U)*log(U) ?
//   pointAssign: log(U)*log(U) ?
//   pointChmax: log(U)*log(U) ?
//   pointChmin: log(U)*log(U) ?
//   pointGet: log(U)
//   rangeAssign: log(U)*log(U) ?
//   rangeGcd: log(U) ?
//   build: 1
// @memory:
//   layout: sparse
//   node: g[4*log(U)]
//   tags: asg[4*log(U)] hasAsg[4*log(U)]
//   other: links[8*log(U)]
//   note: per update, the nodes it visits (at most 4 per level, counting the children a push creates); queries create nothing. the gcd costs' second log is of the largest value. C++: one shared node pool (node 0 = all zeros), call resetPool() between test cases; Python: lists of nodes

// Range assign + range gcd, plus point ops. Gcds are of |values|. A leaf keeps its value, an internal node
// the gcd of |values| below it, and a node assigned v has gcd |v|, so assign is an ordinary lazy tag.
// Over any index range [lo, hi] (huge or negative is fine); every position starts at 0. Updates push a node's
// tag into its children (creating them) before recursing past it; queries never push: they carry the
// ancestors' tags down and apply them to what they return, so they create no nodes. Sparse: nodes exist only
// where updates reached, in one pool shared by every SparseAssignGcdTree<T>; node 0 is the shared all-zeros block.
// T: int, long long, ...
template <typename T>
struct SparseAssignGcdTree {
    struct Agg { T g; };  // a leaf: its value; internal: gcd of |values| below
    struct Tag { T asg; bool has; };
    static constexpr Tag ID = Tag{0, false};
    struct Node { Agg v; Tag t; int l, r; };
    static inline vector<Node> pool{Node{Agg{}, ID, 0, 0}};  // node 0: all zeros, its children are itself
    long long lo, hi;
    int root;

    // O(1) -- all zeros over [lo, hi]; any long long range works (lo <= hi)
    SparseAssignGcdTree(long long lo, long long hi) : lo(lo), hi(hi) { root = make(); }

    // O(1) -- forget every node of every SparseAssignGcdTree<T>; call between test cases, then build new trees
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

    static T absT(T x) { return x < 0 ? -x : x; }

    static bool isId(const Tag& t) { return !t.has; }

    // tag o, then tag t
    static Tag compose(const Tag& o, const Tag& t) { return t.has ? t : o; }

    // the aggregate of k slots after tag t
    static Agg applyTag(Agg v, long long k, const Tag& t) {
        if (t.has) v.g = k == 1 ? t.asg : absT(t.asg);
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

    void pull(int x) { pool[x].v = merge(pool[pool[x].l].v, pool[pool[x].r].v); }

    static Agg merge(const Agg& a, const Agg& b) { return Agg{std::gcd(absT(a.g), absT(b.g))}; }

    void update(int x, long long a, long long b, long long l, long long r, const Tag& t) {
        if (l <= a && b <= r) { applyNode(x, b - a + 1, t); return; }
        push(x, a, b);
        long long m = a + (b - a) / 2;
        if (l <= m) update(kid(x, false), a, m, l, r, t);
        if (r > m) update(kid(x, true), m + 1, b, l, r, t);
        pull(x);
    }

    // aggregate of a[max(l, a)..min(r, b)] under node x (covering [a, b]), with t, the ancestors' pending tags, on top
    Agg query(int x, long long a, long long b, long long l, long long r, const Tag& t) const {
        if (!x) return applyTag(Agg{}, std::min(r, b) - std::max(l, a) + 1, t);
        if (l <= a && b <= r) return applyTag(pool[x].v, b - a + 1, t);
        Tag down = compose(pool[x].t, t);
        long long m = a + (b - a) / 2;
        if (r <= m) return query(pool[x].l, a, m, l, r, down);
        if (l > m) return query(pool[x].r, m + 1, b, l, r, down);
        return merge(query(pool[x].l, a, m, l, r, down), query(pool[x].r, m + 1, b, l, r, down));
    }

    // O(logU) -- a[i] = v for i in [l, r]
    void rangeAssign(long long l, long long r, T v) {
        if (l <= r) update(root, lo, hi, l, r, Tag{v, true});
    }

    // O(logU) -- gcd of |a[l]|, ..., |a[r]| (0 only if all are 0)
    T rangeGcd(long long l, long long r) const {
        Agg res = query(root, lo, hi, l, r, ID);
        return absT(res.g);
    }

    // O(logU) -- a[i]
    T pointGet(long long i) const {
        Agg res = query(root, lo, hi, i, i, ID);
        return res.g;
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
        while (d--) pull(path[d]);
    }

    // O(logU) -- a[i] += delta
    void pointAdd(long long i, T delta) { pointAssign(i, pointGet(i) + delta); }

    // O(logU) -- a[i] = max(a[i], v)
    void pointChmax(long long i, T v) { if (v > pointGet(i)) pointAssign(i, v); }

    // O(logU) -- a[i] = min(a[i], v)
    void pointChmin(long long i, T v) { if (v < pointGet(i)) pointAssign(i, v); }
};
