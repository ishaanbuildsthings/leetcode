// @operations: leftmostPrefixSumGtX leftmostPrefixSumGteX pointAdd pointAssign pointChmax pointChmin pointGet rangeSum
// @data-structure-type: BIT
// @complexities:
//   leftmostPrefixSumGtX: log(U)
//   leftmostPrefixSumGteX: log(U)
//   pointAdd: log(U)
//   pointAssign: log(U)
//   pointChmax: log(U)
//   pointChmin: log(U)
//   pointGet: log(U)
//   rangeSum: log(U)
//   build: 1
// @memory:
//   layout: sparse
//   node: tree[1*log(U)]
//   tags: none
//   other: links[2*log(U)]
//   note: per update, the O(logU) entries above each changed position; the prefix-sum searches need every a[i] >= 0; they return lo - 1 (-1 when lo = 0) when nothing qualifies. Python: a Fenwick tree in a dict (no links); C++: a dynamic prefix-sum tree in one shared node pool, call resetPool() between test cases

// Point add, range sum, and the first index where a running sum from l reaches x.
// Over any index range [lo, hi] (huge or negative is fine); every position starts at 0. Sparse: a dynamic
// prefix-sum tree over offsets x = i - lo in [0, n), in one pool shared by every SparseBIT<T>; node 0 is the
// shared all-zeros block. T: int, long long, ...
template <typename T>
struct SparseBIT {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    using F = array<S, 1>;
    struct Node { F f; int l, r; };  // f: totals of the point changes under the node
    static inline vector<Node> pool{Node{}};  // node 0: all zeros, its children are itself
    long long lo, hi, n;
    int root = 0;

    // O(1) -- all zeros over [lo, hi]; any long long range works (lo <= hi)
    SparseBIT(long long lo, long long hi) : lo(lo), hi(hi), n(hi - lo + 1) {}

    // O(1) -- forget every node of every SparseBIT<T>; call between test cases, then build new trees
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

    // O(logU) -- a[i] += delta
    void pointAdd(long long i, T delta) { add(i - lo, F{S(delta)}); }

    // O(logU) -- a[l] + ... + a[r]
    S rangeSum(long long l, long long r) const { return l <= r ? prefix(r - lo)[0] - prefix(l - 1 - lo)[0] : S(0); }

    // O(logU) -- a[i]
    T pointGet(long long i) const { return T(rangeSum(i, i)); }

    // O(logU) -- a[i] = v
    void pointAssign(long long i, T v) { pointAdd(i, v - pointGet(i)); }

    // O(logU) -- a[i] = max(a[i], v)
    void pointChmax(long long i, T v) { T cur = pointGet(i); if (v > cur) pointAdd(i, v - cur); }

    // O(logU) -- a[i] = min(a[i], v)
    void pointChmin(long long i, T v) { T cur = pointGet(i); if (v < cur) pointAdd(i, v - cur); }

    // O(logU) -- smallest offset x with prefix(x) >= target (> target if strict), or n. Needs every a[i] >= 0.
    long long lowerBound(S target, bool strict) const {
        auto reached = [&](S v) { return strict ? v > target : v >= target; };
        if (!reached(pool[root].f[0])) return n;
        int y = root;
        long long a = 0, b = n - 1;
        S acc = 0;
        while (a < b) {  // node 0 is a block of zeros: the answer is its first position
            long long m = a + (b - a) / 2;
            S left = acc + pool[pool[y].l].f[0];
            if (reached(left)) y = pool[y].l, b = m;
            else acc = left, y = pool[y].r, a = m + 1;
        }
        return a;
    }

    // O(logU) -- first i in [l, r] with a[l] + ... + a[i] >= x, or lo - 1. Needs every a[i] >= 0.
    long long leftmostPrefixSumGteX(long long l, long long r, T x) const {
        long long i = max(l, lo + lowerBound(prefix(l - 1 - lo)[0] + x, false));
        return i <= r ? i : lo - 1;
    }

    // O(logU) -- first i in [l, r] with a[l] + ... + a[i] > x, or lo - 1. Needs every a[i] >= 0.
    long long leftmostPrefixSumGtX(long long l, long long r, T x) const {
        long long i = max(l, lo + lowerBound(prefix(l - 1 - lo)[0] + x, true));
        return i <= r ? i : lo - 1;
    }
};
