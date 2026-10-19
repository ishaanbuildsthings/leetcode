// @operations: pointAdd pointAssign pointGet rangeAddArithSeqMod rangeAddMod rangeSumMod
// @data-structure-type: BIT
// @complexities:
//   pointAdd: log(U)
//   pointAssign: log(U)
//   pointGet: log(U)
//   rangeAddArithSeqMod: log(U)
//   rangeAddMod: log(U)
//   rangeSumMod: log(U)
//   build: 1
// @memory:
//   layout: sparse
//   node: A[2*log(U)] B[2*log(U)] C[2*log(U)]
//   tags: none
//   other: links[4*log(U)]
//   note: per update, the O(logU) entries above each changed position; an arithmetic-sequence add changes two points of A, B and C. Python: a Fenwick tree in a dict (no links); C++: a dynamic prefix-sum tree in one shared node pool, call resetPool() between test cases

// Range add of an arithmetic sequence (and plain range add) + range sum, all mod p. Adding c0 + c1 * x (x = i - lo)
// on [l, r] changes the prefix sum P(x) = a[lo] + ... + a[lo + x] by c0 * (x - l + 1) + c1 * (tri(x) - tri(l - 1))
// for x in [l, r] (tri(k) = k(k+1)/2), and by the whole added total past r. So P(x) = A(x) + B(x) * x +
// C(x) * tri(x) with A, B, C prefix sums of point changes; tri keeps every coefficient an integer.
// Over any index range [lo, hi] (huge or negative is fine); every position starts at 0. Sparse: a dynamic
// prefix-sum tree over offsets x = i - lo in [0, n), in one pool shared by every SparseArithSeqSumBITMod<T>; node 0 is the
// shared all-zeros block. T: int, long long, ...
template <typename T>
struct SparseArithSeqSumBITMod {
    using W = conditional_t<sizeof(T) <= 4, long long, __int128>;
    using F = array<T, 3>;
    struct Node { F f; int l, r; };  // f: totals of the point changes under the node
    static inline vector<Node> pool{Node{}};  // node 0: all zeros, its children are itself
    long long lo, hi, n;
    int root = 0;
    T mod;

    // O(1) -- all zeros over [lo, hi]; any long long range works (lo <= hi)
    SparseArithSeqSumBITMod(long long lo, long long hi, T mod = 1000000007) : lo(lo), hi(hi), n(hi - lo + 1), mod(mod) {}

    // O(1) -- forget every node of every SparseArithSeqSumBITMod<T>; call between test cases, then build new trees
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
            for (int j = 0; j < 3; j++) f[j] = T((W(f[j]) + v[j]) % mod);
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
                for (int j = 0; j < 3; j++) s[j] = T((W(s[j]) + f[j]) % mod);
                break;
            }
            long long m = a + (b - a) / 2;
            if (x <= m) y = pool[y].l, b = m;
            else {
                const F& f = pool[pool[y].l].f;
                for (int j = 0; j < 3; j++) s[j] = T((W(s[j]) + f[j]) % mod);
                y = pool[y].r, a = m + 1;
            }
        }
        return s;
    }

    T norm(W x) const { return T((x % mod + mod) % mod); }
    T tri(long long k) const { return norm(W((__int128)k * (k + 1) / 2 % mod)); }

    // O(logU) -- a[l + j] += start + j * step (mod p) for j in [0, r - l]
    void rangeAddArithSeqMod(long long l, long long r, T start, T step) {
        if (l > r) return;
        l -= lo, r -= lo;
        T c1 = norm(step), c0 = norm(W(start) - W(c1) * norm(l));  // adding c0 + c1 * x at offset x
        T a = norm(W(c0) * norm(1 - l) - W(c1) * tri(l - 1));
        add(l, F{a, c0, c1});
        if (r + 1 < n) {
            T total = norm(W(c0) * norm(r - l + 1) + W(c1) * norm(W(tri(r)) - tri(l - 1)));
            add(r + 1, F{norm(W(total) - a), norm(-W(c0)), norm(-W(c1))});
        }
    }

    // O(logU) -- a[i] += v (mod p) for i in [l, r]
    void rangeAddMod(long long l, long long r, T v) { rangeAddArithSeqMod(l, r, v, 0); }

    // O(logU) -- (a[lo] + ... + a[lo + x]) mod p (0 for x = -1)
    T sum(long long x) const {
        F s = prefix(x);
        return norm(s[0] + W(s[1]) * norm(x) % mod + W(s[2]) * tri(x) % mod);
    }

    // O(logU) -- (a[l] + ... + a[r]) mod p
    T rangeSumMod(long long l, long long r) const { return l <= r ? norm(W(sum(r - lo)) - sum(l - 1 - lo)) : T(0); }

    // O(logU) -- a[i], in [0, mod)
    T pointGet(long long i) const { return rangeSumMod(i, i); }

    // O(logU) -- a[i] += delta
    void pointAdd(long long i, T delta) { rangeAddMod(i, i, delta); }

    // O(logU) -- a[i] = v
    void pointAssign(long long i, T v) { rangeAddMod(i, i, v - pointGet(i)); }
};
