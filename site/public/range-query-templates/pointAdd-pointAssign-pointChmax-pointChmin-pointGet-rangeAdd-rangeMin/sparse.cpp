// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAdd-rangeMin/sparse.cpp
// @operations: pointAdd pointAssign pointChmax pointChmin pointGet rangeAdd rangeMin
// @data-structure-type: lazy-seg-tree
// @complexities:
//   pointAdd: log(U)
//   pointAssign: log(U)
//   pointChmax: log(U)
//   pointChmin: log(U)
//   pointGet: log(U)
//   rangeAdd: log(U)
//   rangeMin: log(U)
//   build: 1
// @memory:
//   layout: sparse
//   node: mn[4*log(U)]
//   tags: add[4*log(U)]
//   other: children[8*log(U)]
//   note: per update, the nodes it visits (at most 4 per level); queries create nothing. One shared node pool (node 0 = all zeros), call resetPool() between test cases

// Range add with range min queries, plus point ops, over any index range [lo, hi] (huge or negative is fine); every position starts at 0.
// The tag is the map x -> x + c; these maps compose into the same form, and each
// is monotone, so it sends a node's min / max straight to the new min / max.
// Adds commute, so nothing is ever pushed: a node's own add stays folded into its aggregate, and
// queries and point writes add up the adds of the ancestors on the way down.
// Sparse: nodes exist only where updates reached, in one pool shared by every SparseAddMinTree<T>; node 0 is the shared
// all-zeros block (its sum, min and max are 0 at any length). T: int, long long, ...
template <typename T>
struct SparseAddMinTree {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    static constexpr T INF = numeric_limits<T>::max(), NEG = numeric_limits<T>::lowest();
    struct Agg { T mn; };
    struct Tag { T c; };  // x -> x + c
    static constexpr Tag ID = Tag{0};
    struct Node { Agg v; Tag t; int l, r; };
    static inline vector<Node> pool{Node{Agg{}, ID, 0, 0}};  // node 0: all zeros, its children are itself
    long long lo, hi;
    int root;

    // O(1) -- all zeros over [lo, hi]; any long long range works (lo <= hi)
    SparseAddMinTree(long long lo, long long hi) : lo(lo), hi(hi) { root = make(); }

    // O(1) -- forget every node of every SparseAddMinTree<T>; call between test cases, then build new trees
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

    static bool isId(const Tag& t) { return t.c == 0; }
    static T val(T v, const Tag& t) { v += t.c; return v; }
    // tag o, then tag t; these maps compose into the same form
    static Tag compose(const Tag& o, const Tag& t) {
        return Tag{o.c + t.c};
    }

    // the aggregate of k slots after tag t
    static Agg applyTag(Agg v, long long, const Tag& t) {
        v.mn = val(v.mn, t);
        return v;
    }

    static Agg merge(const Agg& a, const Agg& b) { return Agg{std::min(a.mn, b.mn)}; }

    // node x (k slots) takes tag t: its aggregate now, its children later
    void applyNode(int x, long long k, const Tag& t) {
        pool[x].v = applyTag(pool[x].v, k, t);
        pool[x].t = compose(pool[x].t, t);
    }

    void pull(int x, long long k) {
        Agg v = merge(pool[pool[x].l].v, pool[pool[x].r].v);
        v = applyTag(v, k, pool[x].t);  // the node's own add, never pushed
        pool[x].v = v;
    }

    void update(int x, long long a, long long b, long long l, long long r, const Tag& t) {
        if (l <= a && b <= r) { applyNode(x, b - a + 1, t); return; }
        long long m = a + (b - a) / 2;
        if (l <= m) update(kid(x, false), a, m, l, r, t);
        if (r > m) update(kid(x, true), m + 1, b, l, r, t);
        pull(x, b - a + 1);
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

    // O(logU) -- a[i] += v for i in [l, r]
    void rangeAdd(long long l, long long r, T v) {
        if (l <= r) update(root, lo, hi, l, r, Tag{v});
    }

    // O(logU) -- min of a[l..r]
    T rangeMin(long long l, long long r) const { return query(root, lo, hi, l, r, ID).mn; }

    // O(logU) -- a[i]
    T pointGet(long long i) const { return T(query(root, lo, hi, i, i, ID).mn); }

    // O(logU) -- a[i] = v
    void pointAssign(long long i, T v) {
        int path[130], d = 0, y = root;
        long long len[130], a = lo, b = hi;
        T acc = 0;  // the adds above i
        while (a < b) {
            acc += pool[y].t.c;
            path[d] = y, len[d++] = b - a + 1;
            long long m = a + (b - a) / 2;
            if (i <= m) y = kid(y, false), b = m;
            else y = kid(y, true), a = m + 1;
        }
        v -= acc;
        pool[y].v = Agg{v};
        while (d--) pull(path[d], len[d]);
    }

    // O(logU) -- a[i] += delta
    void pointAdd(long long i, T delta) { pointAssign(i, pointGet(i) + delta); }

    // O(logU) -- a[i] = max(a[i], v)
    void pointChmax(long long i, T v) { if (v > pointGet(i)) pointAssign(i, v); }

    // O(logU) -- a[i] = min(a[i], v)
    void pointChmin(long long i, T v) { if (v < pointGet(i)) pointAssign(i, v); }
};
