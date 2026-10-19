// @operations: pointAdd pointAssign pointChmax pointChmin pointGet rangeAdd
// @data-structure-type: BIT
// @complexities:
//   pointAdd: log(U)
//   pointAssign: log(U)
//   pointChmax: log(U)
//   pointChmin: log(U)
//   pointGet: log(U)
//   rangeAdd: log(U)
//   build: 1
// @memory:
//   layout: sparse
//   node: d[2*log(U)]
//   tags: none
//   other: links[4*log(U)]
//   note: per update, the O(logU) entries above each changed position; a range add changes two differences. Python: a Fenwick tree in a dict (no links); C++: a dynamic prefix-sum tree in one shared node pool, call resetPool() between test cases

// Range add, point get: prefix sums of the difference array d[i] = a[i] - a[i - 1].
// Over any index range [lo, hi] (huge or negative is fine); every position starts at 0. Sparse: a dynamic
// prefix-sum tree over offsets x = i - lo in [0, n), in one pool shared by every SparseRangeAddBIT<T>; node 0 is the
// shared all-zeros block. T: int, long long, ...
template <typename T>
struct SparseRangeAddBIT {
    using W = unsigned long long;  // wraps mod 2^64: results are exact whenever they fit in long long
    using F = array<W, 1>;
    struct Node { F f; int l, r; };  // f: totals of the point changes under the node
    static inline vector<Node> pool{Node{}};  // node 0: all zeros, its children are itself
    long long lo, hi, n;
    int root = 0;

    // O(1) -- all zeros over [lo, hi]; any long long range works (lo <= hi)
    SparseRangeAddBIT(long long lo, long long hi) : lo(lo), hi(hi), n(hi - lo + 1) {}

    // O(1) -- forget every node of every SparseRangeAddBIT<T>; call between test cases, then build new trees
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
            for (int j = 0; j < 1; j++) f[j] += v[j];
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
                for (int j = 0; j < 1; j++) s[j] += f[j];
                break;
            }
            long long m = a + (b - a) / 2;
            if (x <= m) y = pool[y].l, b = m;
            else {
                const F& f = pool[pool[y].l].f;
                for (int j = 0; j < 1; j++) s[j] += f[j];
                y = pool[y].r, a = m + 1;
            }
        }
        return s;
    }

    // O(logU) -- a[i] += v for i in [l, r]
    void rangeAdd(long long l, long long r, T v) {
        if (l > r) return;
        add(l - lo, F{W(v)});
        if (r < hi) add(r + 1 - lo, F{W(0) - W(v)});
    }

    // O(logU) -- a[i]
    T pointGet(long long i) const { return T(prefix(i - lo)[0]); }

    // O(logU) -- a[i] += delta
    void pointAdd(long long i, T delta) { rangeAdd(i, i, delta); }

    // O(logU) -- a[i] = v
    void pointAssign(long long i, T v) { rangeAdd(i, i, v - pointGet(i)); }

    // O(logU) -- a[i] = max(a[i], v)
    void pointChmax(long long i, T v) { T cur = pointGet(i); if (v > cur) rangeAdd(i, i, v - cur); }

    // O(logU) -- a[i] = min(a[i], v)
    void pointChmin(long long i, T v) { T cur = pointGet(i); if (v < cur) rangeAdd(i, i, v - cur); }
};
