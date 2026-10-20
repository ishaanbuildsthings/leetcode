// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/maxSuffixSum-pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeSum/sparse.cpp
// @operations: maxSuffixSum pointAdd pointAssign pointChmax pointChmin pointGet rangeSum
// @data-structure-type: seg-tree
// @complexities:
//   maxSuffixSum: log(U)
//   pointAdd: log(U)
//   pointAssign: log(U)
//   pointChmax: log(U)
//   pointChmin: log(U)
//   pointGet: log(U)
//   rangeSum: log(U)
//   build: 1
// @memory:
//   layout: sparse
//   node: sm[1*log(U)] suf[1*log(U)]
//   tags: none
//   other: children[2*log(U)]
//   note: per update, one node per level of the touched path; pieces are non-empty, so a block of zeros summarizes to all zeros; one shared node pool (node 0 = all zeros), call resetPool() between test cases

// Max suffix sum + range sum with point updates, over any index range [lo, hi] (huge or negative is fine); every position starts at 0.
// Sparse: only the nodes on updated paths exist, in one pool shared by every SparseMaxSuffixSumTree; a missing child is a block
// of zeros. Each node keeps the summary (sm, suf); merging is not commutative, so queries combine left to right.
// T: int, long long, ...; sums are kept in S (long long for small T).
template <typename T>
struct SparseMaxSuffixSumTree {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    static constexpr S NEG = numeric_limits<S>::lowest() / 4;  // an impossible (first sign, last sign) pair
    struct Agg { S sm; S suf; };
    struct Node { Agg v; int l, r; };
    static inline vector<Node> pool{Node{Agg{0, 0}, 0, 0}};  // node 0: the shared all-zeros block
    long long lo, hi;
    int root = 0;

    // O(1) -- an all-zero array over [lo, hi]; any long long range works
    SparseMaxSuffixSumTree(long long lo, long long hi) : lo(lo), hi(hi) {}

    // O(1) -- forget every node of every SparseMaxSuffixSumTree; call once per test case, then build new trees
    static void resetPool() { pool.resize(1); }

    // optional: reserve room for this many nodes up front (about log U per update)
    static void reservePool(size_t nodes) { pool.reserve(nodes); }

    static int make() {
        pool.push_back(Node{Agg{0, 0}, 0, 0});
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

    static Agg merge(const Agg& a, const Agg& b) { return Agg{a.sm + b.sm, max(b.suf, b.sm + a.suf)}; }
    static Agg leaf(T v) { return Agg{S(v), S(v)}; }
    static Agg zero(long long len) { (void)len; return Agg{0, 0}; }  // a block of len zeros
    static Agg agg(int x, long long len) { return pool[x].v; }

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
    auto rangeSum(long long l, long long r) const {
        Agg res = query(root, lo, hi, l, r);
        return res.sm;
    }

    // O(logU)
    auto maxSuffixSum(long long l, long long r) const {
        Agg res = query(root, lo, hi, l, r);
        return res.suf;
    }

    // O(logU) -- a[i]
    T pointGet(long long i) const {
        int x = find(i);
        return x ? T(pool[x].v.sm) : T(0);
    }

    // O(logU) -- a[i] += delta
    void pointAdd(long long i, T delta) { pointAssign(i, pointGet(i) + delta); }

    // O(logU) -- a[i] = max(a[i], v)
    void pointChmax(long long i, T v) { if (v > pointGet(i)) pointAssign(i, v); }

    // O(logU) -- a[i] = min(a[i], v)
    void pointChmin(long long i, T v) { if (v < pointGet(i)) pointAssign(i, v); }
};
