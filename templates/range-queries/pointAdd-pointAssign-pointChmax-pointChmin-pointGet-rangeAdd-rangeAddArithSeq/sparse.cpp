// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAdd-rangeAddArithSeq/sparse.cpp
// @operations: pointAdd pointAssign pointChmax pointChmin pointGet rangeAdd rangeAddArithSeq
// @data-structure-type: BIT
// @complexities:
//   pointAdd: log(U)
//   pointAssign: log(U)
//   pointChmax: log(U)
//   pointChmin: log(U)
//   pointGet: log(U)
//   rangeAdd: log(U)
//   rangeAddArithSeq: log(U)
//   build: 1
// @memory:
//   layout: sparse
//   node: c[2*log(U)] s[2*log(U)]
//   tags: none
//   other: children[4*log(U)]
//   note: per update, the O(logU) entries above each changed position; an arithmetic-sequence add changes two points of c and s. A dynamic prefix-sum tree in one shared node pool, call resetPool() between test cases

// Range add of an arithmetic sequence (and plain range add), point get. Adding start + (i - l) * step on
// [l, r] is adding the line c0 + c1 * x (x = i - lo), so a[x] = C(x) + x * S(x) with C, S prefix sums of
// two difference arrays.
// Over any index range [lo, hi] (huge or negative is fine); every position starts at 0. Sparse: a dynamic
// prefix-sum tree over offsets x = i - lo in [0, n), in one pool shared by every SparseArithSeqBIT<T>; node 0 is the
// shared all-zeros block. T: int, long long, ...
template <typename T>
struct SparseArithSeqBIT {
    using W = unsigned long long;  // wraps mod 2^64: results are exact whenever they fit in long long
    using F = array<W, 2>;
    struct Node { F f; int l, r; };  // f: totals of the point changes under the node
    static inline vector<Node> pool{Node{}};  // node 0: all zeros, its children are itself
    long long lo, hi, n;
    int root = 0;

    // O(1) -- all zeros over [lo, hi]; any long long range works (lo <= hi)
    SparseArithSeqBIT(long long lo, long long hi) : lo(lo), hi(hi), n(hi - lo + 1) {}

    // O(1) -- forget every node of every SparseArithSeqBIT<T>; call between test cases, then build new trees
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

    // O(logU) -- a[l + j] += start + j * step for j in [0, r - l]
    void rangeAddArithSeq(long long l, long long r, T start, T step) {
        if (l > r) return;
        l -= lo, r -= lo;
        W c1 = W(step), c0 = W(start) - c1 * W(l);
        add(l, F{c0, c1});
        if (r + 1 < n) add(r + 1, F{W(0) - c0, W(0) - c1});
    }

    // O(logU) -- a[i] += v for i in [l, r]
    void rangeAdd(long long l, long long r, T v) { rangeAddArithSeq(l, r, v, 0); }

    // O(logU) -- a[i]
    T pointGet(long long i) const {
        F s = prefix(i - lo);
        return T(s[0] + s[1] * W(i - lo));
    }

    // O(logU) -- a[i] += delta
    void pointAdd(long long i, T delta) { rangeAdd(i, i, delta); }

    // O(logU) -- a[i] = v
    void pointAssign(long long i, T v) { rangeAdd(i, i, v - pointGet(i)); }

    // O(logU) -- a[i] = max(a[i], v)
    void pointChmax(long long i, T v) { T cur = pointGet(i); if (v > cur) rangeAdd(i, i, v - cur); }

    // O(logU) -- a[i] = min(a[i], v)
    void pointChmin(long long i, T v) { T cur = pointGet(i); if (v < cur) rangeAdd(i, i, v - cur); }
};
