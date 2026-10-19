// @operations: longestEqualRun pointAdd pointAssign pointChmax pointChmin pointGet
// @data-structure-type: seg-tree
// @complexities:
//   longestEqualRun: log(U)
//   pointAdd: log(U)
//   pointAssign: log(U)
//   pointChmax: log(U)
//   pointChmin: log(U)
//   pointGet: log(U)
//   build: 1
// @memory:
//   layout: sparse
//   node: ln[1*log(U)] pre[1*log(U)] suf[1*log(U)] best[1*log(U)] lv[1*log(U)] rv[1*log(U)]
//   tags: none
//   other: links[2*log(U)]
//   note: per update, one node per level of the touched path; a block of k zeros is one run of length k, so missing nodes are summarized from their length; C++: one shared node pool (node 0 = all zeros), call resetPool() between test cases; Python: a dict keyed by heap index, a missing key is a block of zeros

// Longest run of equal adjacent values with point updates, over any index range [lo, hi] (huge or negative is fine); every position starts at 0.
// Sparse: only the nodes on updated paths exist, in one pool shared by every SparseEqualRunTree; a missing child is a block
// of zeros. Each node keeps the summary (ln, pre, suf, best, lv, rv); merging is not commutative, so queries combine left to right.
// T: int, long long, ...; sums are kept in S (long long for small T).
template <typename T>
struct SparseEqualRunTree {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    static constexpr S NEG = numeric_limits<S>::lowest() / 4;  // an impossible (first sign, last sign) pair
    struct Agg { long long ln; long long pre; long long suf; long long best; T lv; T rv; };
    struct Node { Agg v; int l, r; };
    static inline vector<Node> pool{Node{Agg{}, 0, 0}};  // node 0: the shared all-zeros block
    long long lo, hi;
    int root = 0;

    // O(1) -- an all-zero array over [lo, hi]; any long long range works
    SparseEqualRunTree(long long lo, long long hi) : lo(lo), hi(hi) {}

    // O(1) -- forget every node of every SparseEqualRunTree; call once per test case, then build new trees
    static void resetPool() { pool.resize(1); }

    // optional: reserve room for this many nodes up front (about log U per update)
    static void reservePool(size_t nodes) { pool.reserve(nodes); }

    static int make() {
        pool.push_back(Node{Agg{}, 0, 0});
        return (int)pool.size() - 1;
    }

    // walk from the root to leaf i, creating missing nodes; fills path[] with the nodes above the leaf and
    // returns the leaf. len[] / starts[] (when given) receive each path node's range.
    int descend(long long i, int* path, int& depth, long long* starts = nullptr, long long* ends = nullptr) {
        if (!root) root = make();
        int x = root;
        long long a = lo, b = hi;
        depth = 0;
        while (a < b) {
            if (starts) starts[depth] = a, ends[depth] = b;
            path[depth++] = x;
            long long m = a + (b - a) / 2;
            if (i <= m) {
                if (!pool[x].l) { int y = make(); pool[x].l = y; }
                x = pool[x].l, b = m;
            } else {
                if (!pool[x].r) { int y = make(); pool[x].r = y; }
                x = pool[x].r, a = m + 1;
            }
        }
        return x;
    }

    // O(logU) -- the leaf for i, or 0 if no update has touched it
    int find(long long i) const {
        int x = root;
        long long a = lo, b = hi;
        while (x && a < b) {
            long long m = a + (b - a) / 2;
            if (i <= m) x = pool[x].l, b = m;
            else x = pool[x].r, a = m + 1;
        }
        return x;
    }

    static Agg merge(const Agg& a, const Agg& b) { return Agg{a.ln + b.ln, (a.rv == b.lv && a.pre == a.ln) ? a.ln + b.pre : a.pre, (a.rv == b.lv && b.suf == b.ln) ? b.ln + a.suf : b.suf, max({a.best, b.best, a.rv == b.lv ? a.suf + b.pre : 0LL}), a.lv, b.rv}; }
    static Agg leaf(T v) { return Agg{1, 1, 1, 1, v, v}; }
    static Agg zero(long long len) { (void)len; return Agg{len, len, len, len, T(0), T(0)}; }  // a block of len zeros
    static Agg agg(int x, long long len) { return x ? pool[x].v : zero(len); }

    // O(logU) -- a[i] = v
    void pointAssign(long long i, T v) {
        int path[130], depth;
        long long starts[130], ends[130];
        int x = descend(i, path, depth, starts, ends);
        pool[x].v = leaf(v);
        while (depth) {
            --depth;
            int y = path[depth];
            long long a = starts[depth], b = ends[depth], m = a + (b - a) / 2;
            pool[y].v = merge(agg(pool[y].l, m - a + 1), agg(pool[y].r, b - m));
        }
    }

    // summary of a[max(l, a)..min(r, b)]; [a, b] must overlap [l, r]
    Agg query(int x, long long a, long long b, long long l, long long r) const {
        if (!x) return zero(min(r, b) - max(l, a) + 1);
        if (l <= a && b <= r) return pool[x].v;
        long long m = a + (b - a) / 2;
        if (r <= m) return query(pool[x].l, a, m, l, r);
        if (l > m) return query(pool[x].r, m + 1, b, l, r);
        return merge(query(pool[x].l, a, m, l, r), query(pool[x].r, m + 1, b, l, r));
    }

    // O(logU)
    auto longestEqualRun(long long l, long long r) const {
        Agg res = query(root, lo, hi, l, r);
        return res.best;
    }

    // O(logU) -- a[i]
    T pointGet(long long i) const {
        int x = find(i);
        return x ? pool[x].v.lv : T(0);
    }

    // O(logU) -- a[i] += delta
    void pointAdd(long long i, T delta) { pointAssign(i, pointGet(i) + delta); }

    // O(logU) -- a[i] = max(a[i], v)
    void pointChmax(long long i, T v) { if (v > pointGet(i)) pointAssign(i, v); }

    // O(logU) -- a[i] = min(a[i], v)
    void pointChmin(long long i, T v) { if (v < pointGet(i)) pointAssign(i, v); }
};
