// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/doAllElementsAppearEvenFrequency-pointAdd-pointAssign-pointChmax-pointChmin-pointGet/sparse-fast.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: doAllElementsAppearEvenFrequency pointAdd pointAssign pointChmax pointChmin pointGet
// @data-structure-type: BIT
// @complexities:
//   doAllElementsAppearEvenFrequency: log(U)
//   pointAdd: log(U)
//   pointAssign: log(U)
//   pointChmax: log(U)
//   pointChmin: log(U)
//   pointGet: log(U)
//   build: 1
// @memory:
//   layout: sparse
//   node: h[1*log(U)]
//   tags: none
//   other: children[2*log(U)] vals[1]
//   note: per point write, the O(logU) entries above it; every value's 64-bit tag is splitmix64(value ^ seed) (a keyed hash with a random per-run seed, no table) and position i stores tag(a[i]) ^ tag(0), so untouched positions store nothing and a range adds tag(0) once per odd length. A dynamic prefix-xor tree in a node pool the tree owns

// Range "does every value appear an even number of times?" via xor hashing, with point updates, over any index range
// [lo, hi] (huge or negative is fine); every position starts at 0. Each distinct value's 64-bit tag is splitmix64(value
// ^ seed): a bijection on 64-bit ints keyed by a random per-run seed, so equal values share a tag, distinct integers
// never collide, and no table is needed. Xor over a range cancels tags in pairs, so an all-even range hashes to 0
// (false positives ~q / 2^64). A position's value lives in its tree leaf. Sparse: position i stores tag(a[i]) ^ tag(0)
// in a dynamic prefix-xor tree (nothing for the untouched), so the xor of the real tags over [l, r] is the stored xor,
// plus tag(0) when the length is odd. Nodes live in a pool the tree owns. T: an integer type (or anything std::hash
// takes).
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
    LEETCODE_NO_SANITIZE_INLINE typename vector<U>::const_reference operator[](size_t i) const {
        return this->_M_impl._M_start[i];
    }
    LEETCODE_NO_SANITIZE_INLINE size_t size() const { return size_t(this->_M_impl._M_finish - this->_M_impl._M_start); }
#endif
};

template <typename T>
struct SparseXorEven {
    using U64 = unsigned long long;
    struct Node { U64 f; T v; int l, r; };  // f: total of the stored changes under the node; v: a leaf's value
    HotVector<Node> pool{Node{}};  // node 0: all zeros, its children are itself
    long long lo, hi;
    int root = 0;


    // optional -- reserve room for this many nodes up front
    LEETCODE_NO_SANITIZE void reservePool(size_t nodes) { pool.reserve(nodes); }

    LEETCODE_NO_SANITIZE int make() {
        pool.push_back(Node{});
        return (int)pool.size() - 1;
    }

    // O(logU) -- the change v at position i, added into every node on its root path
    LEETCODE_NO_SANITIZE void add(long long i, U64 v) {
        if (!root) root = make();
        int y = root;
        long long a = lo, b = hi;
        while (true) {
            pool[y].f ^= v;
            if (a == b) return;
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
    }

    // O(logU) -- the leaf of position i, created with its root path if missing
    LEETCODE_NO_SANITIZE int leafOf(long long i) {
        if (!root) root = make();
        int y = root;
        long long a = lo, b = hi;
        while (a < b) {
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
        return y;
    }

    // O(logU) -- a[i]: its leaf's value (0 if never written)
    LEETCODE_NO_SANITIZE T valueAt(long long i) const {
        int y = root;
        long long a = lo, b = hi;
        while (y && a < b) {
            long long m = a + (b - a) / 2;
            if (i <= m) y = pool[y].l, b = m;
            else y = pool[y].r, a = m + 1;
        }
        return pool[y].v;
    }

    // O(logU) -- total of the changes at positions lo..i (0 for i < lo)
    LEETCODE_NO_SANITIZE U64 prefix(long long i) const {
        U64 s = 0;
        int y = i < lo ? 0 : root;
        long long a = lo, b = hi;
        while (y) {
            if (b <= i) { s ^= pool[y].f; break; }
            long long m = a + (b - a) / 2;
            if (i <= m) y = pool[y].l, b = m;
            else s ^= pool[pool[y].l].f, y = pool[y].r, a = m + 1;
        }
        return s;
    }

    U64 seed, zero;

    // O(1) -- all zeros over [lo, hi]. Seeded from the clock: a fixed seed is hackable.
    SparseXorEven(long long lo, long long hi) : lo(lo), hi(hi),
        seed(mt19937_64(chrono::steady_clock::now().time_since_epoch().count())()) {
        zero = tagOf(T(0));
    }

    // O(1) -- the value's tag: splitmix64(v ^ seed)
    LEETCODE_NO_SANITIZE U64 tagOf(const T& v) const {
        U64 z;
        if constexpr (is_integral_v<T>) z = (U64)v;
        else z = hash<T>{}(v);
        z ^= seed;
        z += 0x9e3779b97f4a7c15ULL;
        z = (z ^ (z >> 30)) * 0xbf58476d1ce4e5b9ULL;
        z = (z ^ (z >> 27)) * 0x94d049bb133111ebULL;
        return z ^ (z >> 31);
    }

    // O(logU) -- true iff every value in a[l..r] appears an even number of times; needs lo <= l <= r <= hi, else
    // throws out_of_range
    LEETCODE_NO_SANITIZE bool doAllElementsAppearEvenFrequency(long long l, long long r) const {
        if (l < lo || l > r || r > hi) throw out_of_range("doAllElementsAppearEvenFrequency: needs lo <= l <= r <= hi");
        U64 h = prefix(r) ^ prefix(l - 1);
        if ((r - l + 1) & 1) h ^= zero;
        return h == 0;
    }

    // O(logU) -- a[i] = v; needs lo <= i <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAssign(long long i, T v) {
        if (i < lo || i > hi) throw out_of_range("pointAssign: needs lo <= i <= hi");
        U64 d = tagOf(valueAt(i)) ^ tagOf(v);
        if (d) add(i, d);
        pool[leafOf(i)].v = v;
    }

    // a[i]; needs lo <= i <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE T pointGet(long long i) const {
        if (i < lo || i > hi) throw out_of_range("pointGet: needs lo <= i <= hi");
        return valueAt(i);
    }

    // a[i] += delta; needs lo <= i <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAdd(long long i, T delta) {
        if (i < lo || i > hi) throw out_of_range("pointAdd: needs lo <= i <= hi");
        pointAssign(i, pointGet(i) + delta);
    }

    // a[i] = max(a[i], v); needs lo <= i <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointChmax(long long i, T v) {
        if (i < lo || i > hi) throw out_of_range("pointChmax: needs lo <= i <= hi");
        if (v > pointGet(i)) pointAssign(i, v);
    }

    // a[i] = min(a[i], v); needs lo <= i <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointChmin(long long i, T v) {
        if (i < lo || i > hi) throw out_of_range("pointChmin: needs lo <= i <= hi");
        if (v < pointGet(i)) pointAssign(i, v);
    }
};
