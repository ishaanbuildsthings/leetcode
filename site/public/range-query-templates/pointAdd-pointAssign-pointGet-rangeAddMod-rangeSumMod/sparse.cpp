// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/pointAdd-pointAssign-pointGet-rangeAddMod-rangeSumMod/sparse.cpp
// @operations: pointAdd pointAssign pointGet rangeAddMod rangeSumMod
// @data-structure-type: BIT
// @complexities:
//   pointAdd: log(U)
//   pointAssign: log(U)
//   pointGet: log(U)
//   rangeAddMod: log(U)
//   rangeSumMod: log(U)
//   build: 1
// @memory:
//   layout: sparse
//   node: A[2*log(U)] B[2*log(U)]
//   tags: none
//   other: children[4*log(U)]
//   note: per update, the O(logU) entries above each changed position; a range add changes two points of A and B. A dynamic prefix-sum tree in a node pool the tree owns

// Range add + range sum: adding v on [l, r] changes the prefix sum P(x) = a[lo] + ... + a[x] by
//   v * (x - l + 1) for x in [l, r], and the whole v * (r - l + 1) past r,
// so P(x) = A(x) + B(x) * x with A, B prefix sums of two arrays of point changes. All mod p. Over any index range [lo,
// hi] (huge or negative is fine); every position starts at 0. Sparse: a dynamic prefix-sum tree over offsets x = i - lo
// in [0, n), in a pool the tree owns; node 0 is the all-zeros block. T: int, long long, ...
template <typename T>
struct SparseRangeAddSumBITMod {
    using W = conditional_t<sizeof(T) <= 4, long long, __int128>;
    using F = array<T, 2>;
    struct Node { F f; int l, r; };  // f: totals of the point changes under the node
    vector<Node> pool{Node{}};  // node 0: all zeros, its children are itself
    long long lo, hi, n;
    int root = 0;
    T mod;

    // O(1) -- all zeros over [lo, hi]; any long long range works (lo <= hi)
    SparseRangeAddSumBITMod(long long lo, long long hi, T mod = 1000000007) : lo(lo), hi(hi), n(hi - lo + 1), mod(mod) {}


    // optional -- reserve room for this many nodes up front
    void reservePool(size_t nodes) { pool.reserve(nodes); }

    int make() {
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
            for (int j = 0; j < 2; j++) f[j] = T((W(f[j]) + v[j]) % mod);
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
                for (int j = 0; j < 2; j++) s[j] = T((W(s[j]) + f[j]) % mod);
                break;
            }
            long long m = a + (b - a) / 2;
            if (x <= m) y = pool[y].l, b = m;
            else {
                const F& f = pool[pool[y].l].f;
                for (int j = 0; j < 2; j++) s[j] = T((W(s[j]) + f[j]) % mod);
                y = pool[y].r, a = m + 1;
            }
        }
        return s;
    }

    T norm(W x) const { return T((x % mod + mod) % mod); }

    // O(logU) -- a[i] += v (mod p) for i in [l, r]
    void rangeAddMod(long long l, long long r, T v) {
        if (l > r) return;
        l -= lo, r -= lo;
        T c = norm(v), a = norm(W(c) * norm(1 - l));
        add(l, F{a, c});
        if (r + 1 < n) add(r + 1, F{norm(W(c) * norm(r - l + 1) - a), norm(-W(c))});
    }

    // O(logU) -- (a[lo] + ... + a[lo + x]) mod p (0 for x = -1)
    T sum(long long x) const {
        F s = prefix(x);
        return norm(s[0] + W(s[1]) * norm(x));
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
