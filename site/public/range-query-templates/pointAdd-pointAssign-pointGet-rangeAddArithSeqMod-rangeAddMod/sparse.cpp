// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/pointAdd-pointAssign-pointGet-rangeAddArithSeqMod-rangeAddMod/sparse.cpp
// @operations: pointAdd pointAssign pointGet rangeAddArithSeqMod rangeAddMod
// @data-structure-type: BIT
// @complexities:
//   pointAdd: log(U)
//   pointAssign: log(U)
//   pointGet: log(U)
//   rangeAddArithSeqMod: log(U)
//   rangeAddMod: log(U)
//   build: 1
// @memory:
//   layout: sparse
//   node: c[2*log(U)] s[2*log(U)]
//   tags: none
//   other: children[4*log(U)]
//   note: per update, the O(logU) entries above each changed position; an arithmetic-sequence add changes two points of c and s. A dynamic prefix-sum tree in a node pool the tree owns

// Range add of an arithmetic sequence (and plain range add), point get, all mod p. Adding start + (i - l) * step on [l,
// r] is adding the line c0 + c1 * x (x = i - lo), so a[x] = C(x) + x * S(x) with C, S prefix sums of two difference
// arrays. Over any index range [lo, hi] (huge or negative is fine); every position starts at 0. Sparse: a dynamic
// prefix-sum tree over offsets x = i - lo in [0, n), in a pool the tree owns; node 0 is the all-zeros block. T: int,
// long long, ...
template <typename T>
struct SparseArithSeqBITMod {
    using W = conditional_t<sizeof(T) <= 4, long long, __int128>;
    using F = array<T, 2>;
    struct Node { F f; int l, r; };  // f: totals of the point changes under the node
    vector<Node> pool{Node{}};  // node 0: all zeros, its children are itself
    long long lo, hi, n;
    int root = 0;
    T mod;

    // O(1) -- all zeros over [lo, hi]; any long long range works (lo <= hi)
    SparseArithSeqBITMod(long long lo, long long hi, T mod = 1000000007) : lo(lo), hi(hi), n(hi - lo + 1), mod(mod) {}


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

    // O(logU) -- a[l + j] += start + j * step (mod p) for j in [0, r - l]
    void rangeAddArithSeqMod(long long l, long long r, T start, T step) {
        if (l > r) return;
        l -= lo, r -= lo;
        T c1 = norm(step), c0 = norm(W(start) - W(c1) * norm(l));
        add(l, F{c0, c1});
        if (r + 1 < n) add(r + 1, F{norm(-W(c0)), norm(-W(c1))});
    }

    // O(logU) -- a[i] += v (mod p) for i in [l, r]
    void rangeAddMod(long long l, long long r, T v) { rangeAddArithSeqMod(l, r, v, 0); }

    // O(logU) -- a[i], in [0, mod)
    T pointGet(long long i) const {
        F s = prefix(i - lo);
        return norm(s[0] + W(s[1]) * norm(i - lo));
    }

    // O(logU) -- a[i] += delta
    void pointAdd(long long i, T delta) { rangeAddMod(i, i, delta); }

    // O(logU) -- a[i] = v
    void pointAssign(long long i, T v) { rangeAddMod(i, i, v - pointGet(i)); }
};
