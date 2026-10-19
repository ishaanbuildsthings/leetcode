// @operations: pointAdd pointAssign pointChmax pointChmin pointGet rangeAdd rangeSum
// @data-structure-type: BIT
// @complexities:
//   pointAdd: log(U)
//   pointAssign: log(U)
//   pointChmax: log(U)
//   pointChmin: log(U)
//   pointGet: log(U)
//   rangeAdd: log(U)
//   rangeSum: log(U)
//   build: 1
// @memory:
//   layout: sparse
//   node: A[2*log(U)] B[2*log(U)]
//   tags: none
//   other: links[4*log(U)]
//   note: per update, the O(logU) entries above each changed position; a range add changes two points of A and B. Python: a Fenwick tree in a dict (no links); C++: a dynamic prefix-sum tree in one shared node pool, call resetPool() between test cases

// Range add + range sum: adding v on [l, r] changes the prefix sum P(x) = a[lo] + ... + a[x] by
//   v * (x - l + 1) for x in [l, r], and the whole v * (r - l + 1) past r,
// so P(x) = A(x) + B(x) * x with A, B prefix sums of two arrays of point changes.
// Over any index range [lo, hi] (huge or negative is fine); every position starts at 0. Sparse: a dynamic
// prefix-sum tree over offsets x = i - lo in [0, n), in one pool shared by every SparseRangeAddSumBIT<T>; node 0 is the
// shared all-zeros block. T: int, long long, ...
template <typename T>
struct SparseRangeAddSumBIT {
    using W = unsigned long long;  // wraps mod 2^64: results are exact whenever they fit in long long
    using F = array<W, 2>;
    struct Node { F f; int l, r; };  // f: totals of the point changes under the node
    static inline vector<Node> pool{Node{}};  // node 0: all zeros, its children are itself
    long long lo, hi, n;
    int root = 0;

    // O(1) -- all zeros over [lo, hi]; any long long range works (lo <= hi)
    SparseRangeAddSumBIT(long long lo, long long hi) : lo(lo), hi(hi), n(hi - lo + 1) {}

    // O(1) -- forget every node of every SparseRangeAddSumBIT<T>; call between test cases, then build new trees
    static void resetPool() { pool.resize(1); }

    // optional -- reserve room for this many nodes up front
    static void reservePool(size_t nodes) { pool.reserve(nodes); }

    static int make() {
        pool.push_back(Node{});
        return (int)pool.size() - 1;
    }

    // O(logU) -- adds v at offset x: to every node on its root path
    void add(long long x, const F& v) {
        if (!root) root = make();
        int y = root;
        long long a = 0, b = n - 1;
        while (true) {
            F& f = pool[y].f;
            for (int j = 0; j < 2; j++) f[j] += v[j];
            if (a == b) return;
            long long m = a + (b - a) / 2;
            bool right = x > m;
            int c = right ? pool[y].r : pool[y].l;
            if (!c) {
                c = make();
                (right ? pool[y].r : pool[y].l) = c;
            }
            y = c;
            if (right) a = m + 1;
            else b = m;
        }
    }

    // O(logU) -- totals of the point changes at offsets 0..x (zeros for x < 0)
    F prefix(long long x) const {
        F s{};
        int y = x < 0 ? 0 : root;
        long long a = 0, b = n - 1;
        while (y) {
            if (b <= x) {  // the whole node is inside the prefix
                const F& f = pool[y].f;
                for (int j = 0; j < 2; j++) s[j] += f[j];
                break;
            }
            long long m = a + (b - a) / 2;
            if (x <= m) y = pool[y].l, b = m;
            else {
                const F& f = pool[pool[y].l].f;
                for (int j = 0; j < 2; j++) s[j] += f[j];
                y = pool[y].r, a = m + 1;
            }
        }
        return s;
    }

    // O(logU) -- a[i] += v for i in [l, r]
    void rangeAdd(long long l, long long r, T v) {
        if (l > r) return;
        l -= lo, r -= lo;
        W c = W(v), a = c * W(1 - l);
        add(l, F{a, c});
        if (r + 1 < n) add(r + 1, F{c * W(r - l + 1) - a, W(0) - c});
    }

    // O(logU) -- a[lo] + ... + a[lo + x] (0 for x = -1)
    W sum(long long x) const {
        F s = prefix(x);
        return s[0] + s[1] * W(x);
    }

    // O(logU) -- a[l] + ... + a[r]
    long long rangeSum(long long l, long long r) const { return l <= r ? (long long)(sum(r - lo) - sum(l - 1 - lo)) : 0; }

    // O(logU) -- a[i]
    T pointGet(long long i) const { return T(rangeSum(i, i)); }

    // O(logU) -- a[i] += delta
    void pointAdd(long long i, T delta) { rangeAdd(i, i, delta); }

    // O(logU) -- a[i] = v
    void pointAssign(long long i, T v) { rangeAdd(i, i, v - pointGet(i)); }

    // O(logU) -- a[i] = max(a[i], v)
    void pointChmax(long long i, T v) { T cur = pointGet(i); if (v > cur) rangeAdd(i, i, v - cur); }

    // O(logU) -- a[i] = min(a[i], v)
    void pointChmin(long long i, T v) { T cur = pointGet(i); if (v < cur) rangeAdd(i, i, v - cur); }
};
