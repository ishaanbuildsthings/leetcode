// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/pointAdd-pointAssign-pointGet-rangeAddMod/sparse.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: pointAdd pointAssign pointGet rangeAddMod
// @data-structure-type: BIT
// @complexities:
//   pointAdd: log(U)
//   pointAssign: log(U)
//   pointGet: log(U)
//   rangeAddMod: log(U)
//   build: 1
// @memory:
//   layout: sparse
//   node: d[2*log(U)]
//   tags: none
//   other: children[4*log(U)]
//   note: per update, the O(logU) entries above each changed position; a range add changes two differences. A dynamic prefix-sum tree in a node pool the tree owns

// Range add, point get, all % MOD: prefix sums of the difference array d[i] = a[i] - a[i - 1]. Over any index range
// [lo, hi] (huge or negative is fine); every position starts at 0. Sparse: a dynamic prefix-sum tree over offsets x = i
// - lo in [0, n), in a pool the tree owns; node 0 is the all-zeros block. T: int, long long, ...
template <typename T>
struct SparseRangeAddBITMod {
    using W = conditional_t<sizeof(T) <= 4, long long, __int128>;
    using F = array<T, 1>;
    struct Node { F f; int l, r; };  // f: totals of the point changes under the node
    vector<Node> pool{Node{}};  // node 0: all zeros, its children are itself
    long long lo, hi, n;
    int root = 0;
    T mod;

    // O(1) -- all zeros over [lo, hi]; any long long range works (lo <= hi)
    SparseRangeAddBITMod(long long lo, long long hi, T mod = 1000000007) : lo(lo), hi(hi), n(hi - lo + 1), mod(mod) {}


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
            for (int j = 0; j < 1; j++) f[j] = T((W(f[j]) + v[j]) % mod);
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
                for (int j = 0; j < 1; j++) s[j] = T((W(s[j]) + f[j]) % mod);
                break;
            }
            long long m = a + (b - a) / 2;
            if (x <= m) y = pool[y].l, b = m;
            else {
                const F& f = pool[pool[y].l].f;
                for (int j = 0; j < 1; j++) s[j] = T((W(s[j]) + f[j]) % mod);
                y = pool[y].r, a = m + 1;
            }
        }
        return s;
    }

    T norm(W x) const { return T((x % mod + mod) % mod); }

    // O(logU) -- a[i] += v (% MOD) for i in [l, r]; needs lo <= l <= r <= hi, else throws out_of_range
    void rangeAddMod(long long l, long long r, T v) {
        if (l < lo || l > r || r > hi) throw out_of_range("rangeAddMod: needs lo <= l <= r <= hi");
        if (l > r) return;
        T x = norm(v);
        add(l - lo, F{x});
        if (r < hi) add(r + 1 - lo, F{norm(-W(x))});
    }

    // O(logU) -- a[i], in [0, mod); needs lo <= i <= hi, else throws out_of_range
    T pointGet(long long i) const {
        if (i < lo || i > hi) throw out_of_range("pointGet: needs lo <= i <= hi");
        return norm(prefix(i - lo)[0]);
    }

    // O(logU) -- a[i] += delta; needs lo <= i <= hi, else throws out_of_range
    void pointAdd(long long i, T delta) {
        if (i < lo || i > hi) throw out_of_range("pointAdd: needs lo <= i <= hi");
        rangeAddMod(i, i, delta);
    }

    // O(logU) -- a[i] = v; needs lo <= i <= hi, else throws out_of_range
    void pointAssign(long long i, T v) {
        if (i < lo || i > hi) throw out_of_range("pointAssign: needs lo <= i <= hi");
        rangeAddMod(i, i, v - pointGet(i));
    }
};
