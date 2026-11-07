// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/pointAdd-pointAssign-pointGet-rangeAddArithSeqMod-rangeAddMod/sparse-fast.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

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

// Range add of an arithmetic sequence (and plain range add), point get, all % MOD. Adding start + (i - l) * step on [l,
// r] is adding the line c0 + c1 * x (x = i - lo), so a[x] = C(x) + x * S(x) with C, S prefix sums of two difference
// arrays. Over any index range [lo, hi] (huge or negative is fine); every position starts at 0. Sparse: a dynamic
// prefix-sum tree over offsets x = i - lo in [0, n), in a pool the tree owns; node 0 is the all-zeros block. T: int,
// long long, ...
// FAST MODE drawbacks compared with sparse.cpp:
//   - sanitizers are skipped inside this template, so a bad access in it goes unreported
// Same public operations and answers, same limits; it needs GCC or Clang and C++17.
#ifdef __SSE2__
#include <immintrin.h>
#endif

// LEETCODE_NO_SANITIZE skips sanitizers in a function. It only changes anything where sanitizers run, like LeetCode: on
// Codeforces it compiles and does nothing.
// This template already uses it. To go further, put it on the one function with your hot loop:
//   LEETCODE_NO_SANITIZE long long maxSum(vector<int>& nums, int k) {
// A lambda needs its own: [&](int x) LEETCODE_NO_SANITIZE { ... }. It does not carry into anything that function calls.
// Inside a marked function use raw pointers and plain comparisons, not vector[] and min / max, or it can get slower.
// Bad memory accesses in a marked function go unreported.
#ifndef LEETCODE_NO_SANITIZE
#define LEETCODE_NO_SANITIZE __attribute__((no_sanitize("address"), no_sanitize("undefined")))
#endif
#define LEETCODE_NO_SANITIZE_INLINE LEETCODE_NO_SANITIZE __attribute__((always_inline)) inline

// A vector whose [] and size() always inline, even with sanitizers skipped (libstdc++ only; elsewhere a plain vector)
template <typename U>
struct HotVector : vector<U> {
    using vector<U>::vector;
    HotVector() = default;
    HotVector(const vector<U>& other) : vector<U>(other) {}
    HotVector(vector<U>&& other) : vector<U>(move(other)) {}
#ifdef __GLIBCXX__
    LEETCODE_NO_SANITIZE_INLINE typename vector<U>::reference operator[](size_t i) { return this->_M_impl._M_start[i]; }
    LEETCODE_NO_SANITIZE_INLINE typename vector<U>::const_reference operator[](size_t i) const { return this->_M_impl._M_start[i]; }
    LEETCODE_NO_SANITIZE_INLINE size_t size() const { return size_t(this->_M_impl._M_finish - this->_M_impl._M_start); }
#endif
};

template <typename T>
struct SparseArithSeqBITMod {
    using W = conditional_t<sizeof(T) <= 4, long long, __int128>;
    using F = array<T, 2>;
    struct Node { F f; int l, r; };  // f: totals of the point changes under the node
    HotVector<Node> pool{Node{}};  // node 0: all zeros, its children are itself
    long long lo, hi, n;
    int root = 0;
    T mod;

    // O(1) -- all zeros over [lo, hi]; any long long range works (lo <= hi)
    SparseArithSeqBITMod(long long lo, long long hi, T mod = 1000000007) : lo(lo), hi(hi), n(hi - lo + 1), mod(mod) {}


    // optional -- reserve room for this many nodes up front
    LEETCODE_NO_SANITIZE void reservePool(size_t nodes) { pool.reserve(nodes); }

    LEETCODE_NO_SANITIZE int make() {
        pool.push_back(Node{});
        return (int)pool.size() - 1;
    }

    // O(logU) -- adds v at offset x: to every node on its root path
    LEETCODE_NO_SANITIZE void add(long long x, const F& v) {
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
    LEETCODE_NO_SANITIZE F prefix(long long x) const {
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

    LEETCODE_NO_SANITIZE T norm(W x) const { return T((x % mod + mod) % mod); }

    // O(logU) -- a[l + j] += start + j * step (% MOD) for j in [0, r - l]; needs lo <= l <= r <= hi, else throws
    // out_of_range
    LEETCODE_NO_SANITIZE void rangeAddArithSeqMod(long long l, long long r, T start, T step) {
        if (l < lo || l > r || r > hi) throw out_of_range("rangeAddArithSeqMod: needs lo <= l <= r <= hi");
        if (l > r) return;
        l -= lo, r -= lo;
        T c1 = norm(step), c0 = norm(W(start) - W(c1) * norm(l));
        add(l, F{c0, c1});
        if (r + 1 < n) add(r + 1, F{norm(-W(c0)), norm(-W(c1))});
    }

    // O(logU) -- a[i] += v (% MOD) for i in [l, r]; needs lo <= l <= r <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE void rangeAddMod(long long l, long long r, T v) {
        if (l < lo || l > r || r > hi) throw out_of_range("rangeAddMod: needs lo <= l <= r <= hi");
        rangeAddArithSeqMod(l, r, v, 0);
    }

    // O(logU) -- a[i], in [0, mod); needs lo <= i <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE T pointGet(long long i) const {
        if (i < lo || i > hi) throw out_of_range("pointGet: needs lo <= i <= hi");
        F s = prefix(i - lo);
        return norm(s[0] + W(s[1]) * norm(i - lo));
    }

    // O(logU) -- a[i] += delta; needs lo <= i <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAdd(long long i, T delta) {
        if (i < lo || i > hi) throw out_of_range("pointAdd: needs lo <= i <= hi");
        rangeAddMod(i, i, delta);
    }

    // O(logU) -- a[i] = v; needs lo <= i <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAssign(long long i, T v) {
        if (i < lo || i > hi) throw out_of_range("pointAssign: needs lo <= i <= hi");
        rangeAddMod(i, i, v - pointGet(i));
    }
};
