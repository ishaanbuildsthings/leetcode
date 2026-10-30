// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/pointAdd-pointAssign-pointGet-rangeAddMod-rangeAffineMod-rangeAssignMod-rangeMultMod/sparse.cpp
// @operations: pointAdd pointAssign pointGet rangeAddMod rangeAffineMod rangeAssignMod rangeMultMod
// @data-structure-type: lazy-seg-tree
// @complexities:
//   pointAdd: log(U)
//   pointAssign: log(U)
//   pointGet: log(U)
//   rangeAddMod: log(U)
//   rangeAffineMod: log(U)
//   rangeAssignMod: log(U)
//   rangeMultMod: log(U)
//   build: 1
// @memory:
//   layout: sparse
//   node: sm[4*log(U)]
//   tags: mul[4*log(U)] add[4*log(U)]
//   other: children[8*log(U)]
//   note: per update, the nodes it visits (at most 4 per level, counting the children a push creates); queries create nothing. a leaf's value is sm (internal nodes keep no aggregate). A node pool per tree (node 0 = all zeros)

// Range affine maps mod p (add, mult and assign are special cases: x -> 1x + v, mx + 0, 0x + v), plus point ops. Values
// are residues in [0, mod). A tag is the map x -> mul * x + add; maps compose into the same form. Only leaves' values
// matter, so nothing is pulled. Over any index range [lo, hi] (huge or negative is fine); every position starts at 0.
// Updates push a node's tag into its children (creating them) before recursing past it; queries never push: they carry
// the ancestors' tags down and apply them to what they return, so they create no nodes. Sparse: nodes exist only where
// updates reached, in a pool the tree owns; node 0 is the all-zeros block. T: int, long long, ...
template <typename T>
struct SparseAffineTree {
    using W = conditional_t<sizeof(T) <= 4, long long, __int128>;
    struct Agg { T sm; };
    struct Tag { T mul, add; };  // x -> mul * x + add
    static constexpr Tag ID = Tag{1, 0};
    struct Node { Agg v; Tag t; int l, r; };
    vector<Node> pool{Node{Agg{}, ID, 0, 0}};  // node 0: all zeros, its children are itself
    long long lo, hi;
    int root;
    T mod;

    // O(1) -- all zeros over [lo, hi]; any long long range works (lo <= hi)
    SparseAffineTree(long long lo, long long hi, T mod = 1000000007) : lo(lo), hi(hi), mod(mod) { root = make(); }


    // optional -- reserve room for this many nodes up front
    void reservePool(size_t nodes) { pool.reserve(nodes); }

    int make() {
        pool.push_back(Node{Agg{}, ID, 0, 0});
        return (int)pool.size() - 1;
    }

    // child of x, creating it (as a block of zeros) if missing
    int kid(int x, bool right) {
        int y = right ? pool[x].r : pool[x].l;
        if (!y) {
            y = make();
            (right ? pool[x].r : pool[x].l) = y;
        }
        return y;
    }

    T norm(W x) const { return T((x % mod + mod) % mod); }

    static bool isId(const Tag& t) { return t.mul == 1 && t.add == 0; }

    // tag o, then tag t
    Tag compose(const Tag& o, const Tag& t) const { return Tag{T(W(t.mul) * o.mul % mod), T((W(t.mul) * o.add + t.add) % mod)}; }

    // the aggregate of k slots after tag t
    Agg applyTag(Agg v, long long k, const Tag& t) const {
        (void)k;
        v.sm = T((W(t.mul) * v.sm + t.add) % mod);
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

    // O(logU) -- a[i] = a[i] + v (mod p) for i in [l, r]
    void rangeAddMod(long long l, long long r, T v) {
        if (l <= r) update(root, lo, hi, l, r, Tag{1, norm(v)});
    }

    // O(logU) -- a[i] = a[i] * m (mod p) for i in [l, r]
    void rangeMultMod(long long l, long long r, T m) {
        if (l <= r) update(root, lo, hi, l, r, Tag{norm(m), 0});
    }

    // O(logU) -- a[i] = v (mod p) for i in [l, r]
    void rangeAssignMod(long long l, long long r, T v) {
        if (l <= r) update(root, lo, hi, l, r, Tag{0, norm(v)});
    }

    // O(logU) -- a[i] = a[i] * mult + add (mod p) for i in [l, r]
    void rangeAffineMod(long long l, long long r, T mult, T add) {
        if (l <= r) update(root, lo, hi, l, r, Tag{norm(mult), norm(add)});
    }

    // O(logU) -- a[i], in [0, mod)
    T pointGet(long long i) const {
        Agg res = query(root, lo, hi, i, i, ID);
        return res.sm;
    }

    // O(logU) -- a[i] = v (mod p)
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
        pool[y].v = Agg{norm(v)};
        (void)path;
    }

    // O(logU) -- a[i] += delta (mod p)
    void pointAdd(long long i, T delta) { pointAssign(i, norm(W(pointGet(i)) + delta)); }
};
