// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/maxPrefixSum-maxSubarraySum-maxSuffixSum-pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAssign-rangeSum/sparse.cpp
// @operations: maxPrefixSum maxSubarraySum maxSuffixSum pointAdd pointAssign pointChmax pointChmin pointGet rangeAssign rangeSum
// @data-structure-type: lazy-seg-tree
// @complexities:
//   maxPrefixSum: log(U)
//   maxSubarraySum: log(U)
//   maxSuffixSum: log(U)
//   pointAdd: log(U)
//   pointAssign: log(U)
//   pointChmax: log(U)
//   pointChmin: log(U)
//   pointGet: log(U)
//   rangeAssign: log(U)
//   rangeSum: log(U)
//   build: 1
// @memory:
//   layout: sparse
//   node: sm[4*log(U)] pre[4*log(U)] suf[4*log(U)] best[4*log(U)]
//   tags: asg[4*log(U)] hasAsg[4*log(U)]
//   other: children[8*log(U)]
//   note: per update, the nodes it visits (at most 4 per level, counting the children a push creates); queries create nothing. A node pool per tree (node 0 = all zeros)

// Range assign with range sum and max prefix / suffix / subarray sum (non-empty pieces), plus point ops. A node
// assigned v over k slots is fully known: sum v * k, and its best prefix / suffix / subarray are v * k if v > 0, else
// v. A block of zeros summarizes to all zeros. Merging is not commutative. Over any index range [lo, hi] (huge or
// negative is fine); every position starts at 0. Updates push a node's tag into its children (creating them) before
// recursing past it; queries never push: they carry the ancestors' tags down and apply them to what they return, so
// they create no nodes. Sparse: nodes exist only where updates reached, in a pool the tree owns; node 0 is the
// all-zeros block. T: int, long long, ...
template <typename T>
struct SparseMaxSubarrayAssignTree {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    struct Agg { S sm, pre, suf, best; };
    struct Tag { T asg; bool has; };
    static constexpr Tag ID = Tag{0, false};
    struct Node { Agg v; Tag t; int l, r; };
    vector<Node> pool{Node{Agg{}, ID, 0, 0}};  // node 0: all zeros, its children are itself
    long long lo, hi;
    int root;

    // O(1) -- all zeros over [lo, hi]; any long long range works (lo <= hi)
    SparseMaxSubarrayAssignTree(long long lo, long long hi) : lo(lo), hi(hi) { root = make(); }


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

    static bool isId(const Tag& t) { return !t.has; }

    // tag o, then tag t
    static Tag compose(const Tag& o, const Tag& t) { return t.has ? t : o; }

    // the aggregate of k slots after tag t
    static Agg applyTag(Agg v, long long k, const Tag& t) {
        if (t.has) {
            v.sm = S(t.asg) * k;
            v.pre = v.suf = v.best = t.asg > 0 ? v.sm : S(t.asg);
        }
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

    static Agg merge(const Agg& a, const Agg& b) { return Agg{a.sm + b.sm, max(a.pre, a.sm + b.pre), max(b.suf, b.sm + a.suf), max({a.best, b.best, a.suf + b.pre})}; }

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

    // O(logU) -- a[l] + ... + a[r]
    S rangeSum(long long l, long long r) const {
        Agg res = query(root, lo, hi, l, r, ID);
        return res.sm;
    }

    // O(logU) -- best sum of a non-empty prefix of a[l..r]
    S maxPrefixSum(long long l, long long r) const {
        Agg res = query(root, lo, hi, l, r, ID);
        return res.pre;
    }

    // O(logU) -- best sum of a non-empty suffix of a[l..r]
    S maxSuffixSum(long long l, long long r) const {
        Agg res = query(root, lo, hi, l, r, ID);
        return res.suf;
    }

    // O(logU) -- best sum of a non-empty subarray of a[l..r]
    S maxSubarraySum(long long l, long long r) const {
        Agg res = query(root, lo, hi, l, r, ID);
        return res.best;
    }

    // O(logU) -- a[i]
    T pointGet(long long i) const {
        Agg res = query(root, lo, hi, i, i, ID);
        return T(res.sm);
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
        pool[y].v = Agg{S(v), S(v), S(v), S(v)};
        while (d--) pull(path[d]);
    }

    // O(logU) -- a[i] += delta
    void pointAdd(long long i, T delta) { pointAssign(i, pointGet(i) + delta); }

    // O(logU) -- a[i] = max(a[i], v)
    void pointChmax(long long i, T v) { if (v > pointGet(i)) pointAssign(i, v); }

    // O(logU) -- a[i] = min(a[i], v)
    void pointChmin(long long i, T v) { if (v < pointGet(i)) pointAssign(i, v); }
};
