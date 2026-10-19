// @operations: pointAdd pointAssign pointChmax pointChmin pointGet rangeAdd rangeGcd
// @data-structure-type: seg-tree
// @complexities:
//   pointAdd: log(U)*log(U) ?
//   pointAssign: log(U)*log(U) ?
//   pointChmax: log(U)*log(U) ?
//   pointChmin: log(U)*log(U) ?
//   pointGet: log(U)
//   rangeAdd: log(U)*log(U) ?
//   rangeGcd: log(U) ?
//   build: 1
// @memory:
//   layout: sparse
//   node: sum[2*log(U)] g[2*log(U)]
//   tags: none
//   other: links[4*log(U)]
//   note: per range add, the two root paths of the differences it changes; one tree over the differences keeps their sum (prefix sums are point values) and gcd; the gcd costs' second log is of the largest value. C++: one shared node pool (node 0 = all zeros), call resetPool() between test cases; Python: dicts keyed by heap index

// Range add + range gcd + point ops over any index range [lo, hi] (huge or negative is fine); every position
// starts at 0. gcd(a[l], ..., a[r]) == gcd(a[l], a[l+1] - a[l], ..., a[r] - a[r-1]), and a range add only changes
// two adjacent differences. One sparse tree over the differences d[i] = a[i] - a[i-1] (d[lo] = a[lo]) keeps their
// sum (a prefix sum is a point value) and the gcd of their absolute values. Sparse: nodes in one pool shared by
// every SparseRangeAddRangeGcd<T>; node 0 is the shared block of zero differences. T: int, long long, ...
template <typename T>
struct SparseRangeAddRangeGcd {
    struct Node { T sum, g; int l, r; };
    static inline vector<Node> pool{Node{0, 0, 0, 0}};  // node 0: all-zero differences, its children are itself
    long long lo, hi;
    int root = 0;

    // O(1) -- all zeros over [lo, hi]; any long long range works (lo <= hi)
    SparseRangeAddRangeGcd(long long lo, long long hi) : lo(lo), hi(hi) {}

    // O(1) -- forget every node of every SparseRangeAddRangeGcd<T>; call between test cases, then build new trees
    static void resetPool() { pool.resize(1); }

    // optional -- reserve room for this many nodes up front (about 2 logU per range add)
    static void reservePool(size_t nodes) { pool.reserve(nodes); }

    static int make() {
        pool.push_back(Node{0, 0, 0, 0});
        return (int)pool.size() - 1;
    }

    static T absT(T x) { return x < 0 ? -x : x; }

    // O(logU logV) -- d[i] += x
    void shiftDiff(long long i, T x) {
        if (!root) root = make();
        int path[130], d = 0, y = root;
        long long a = lo, b = hi;
        while (a < b) {
            path[d++] = y;
            long long m = a + (b - a) / 2;
            bool right = i > m;
            int c = right ? pool[y].r : pool[y].l;
            if (!c) {
                c = make();
                (right ? pool[y].r : pool[y].l) = c;
            }
            y = c;
            if (right) a = m + 1;
            else b = m;
        }
        pool[y].sum += x, pool[y].g = absT(pool[y].sum);
        while (d--) {
            Node& p = pool[path[d]];
            p.sum = pool[p.l].sum + pool[p.r].sum;
            p.g = std::gcd(pool[p.l].g, pool[p.r].g);
        }
    }

    // O(logU) -- d[lo] + ... + d[i], which is a[i]
    T prefix(long long i) const {
        T s = 0;
        int y = root;
        long long a = lo, b = hi;
        while (y) {
            if (a == b) { s += pool[y].sum; break; }
            long long m = a + (b - a) / 2;
            if (i <= m) y = pool[y].l, b = m;
            else s += pool[pool[y].l].sum, y = pool[y].r, a = m + 1;
        }
        return s;
    }

    // gcd of |d[max(l, a)..min(r, b)]|
    T gcdOf(int x, long long a, long long b, long long l, long long r) const {
        if (!x) return 0;
        if (l <= a && b <= r) return pool[x].g;
        long long m = a + (b - a) / 2;
        T res = 0;
        if (l <= m) res = gcdOf(pool[x].l, a, m, l, r);
        if (r > m) res = std::gcd(res, gcdOf(pool[x].r, m + 1, b, l, r));
        return res;
    }

    // O(logU logV) -- adds x to every a[l..r], x may be negative
    void rangeAdd(long long l, long long r, T x) {
        if (l > r) return;
        shiftDiff(l, x);
        if (r < hi) shiftDiff(r + 1, -x);
    }

    // O(logU) -- a[i]
    T pointGet(long long i) const { return prefix(i); }

    // O(logU + logV) -- gcd of a[l..r], always >= 0 (0 only if every value in the range is 0)
    T rangeGcd(long long l, long long r) const {
        T res = absT(prefix(l));
        if (l < r) res = std::gcd(res, gcdOf(root, lo, hi, l + 1, r));
        return res;
    }

    // O(logU logV) -- a[i] += delta
    void pointAdd(long long i, T delta) { rangeAdd(i, i, delta); }

    // O(logU logV) -- a[i] = v
    void pointAssign(long long i, T v) { rangeAdd(i, i, v - prefix(i)); }

    // O(logU logV) -- a[i] = max(a[i], v)
    void pointChmax(long long i, T v) { T cur = prefix(i); if (v > cur) rangeAdd(i, i, v - cur); }

    // O(logU logV) -- a[i] = min(a[i], v)
    void pointChmin(long long i, T v) { T cur = prefix(i); if (v < cur) rangeAdd(i, i, v - cur); }
};
