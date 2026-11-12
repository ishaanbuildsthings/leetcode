// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/doAllElementsAppearEvenFrequency-pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAssign/fast.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: doAllElementsAppearEvenFrequency getAll pointAdd pointAssign pointChmax pointChmin pointGet rangeAssign
// @data-structure-type: lazy-seg-tree
// @letters: same
// @complexities:
//   doAllElementsAppearEvenFrequency: log(N)
//   getAll: N
//   pointAdd: log(N)
//   pointAssign: log(N)
//   pointChmax: log(N)
//   pointChmin: log(N)
//   pointGet: log(N)
//   rangeAssign: log(N)
//   build: N
// @memory:
//   layout: 2n-iterative
//   node: xr[2*N]
//   tags: asg[1*N] hasAsg[1*N]
//   other: vals[1*N]
//   note: xr holds the xor of value tags; a value's tag is splitmix64(value ^ seed), a keyed hash with a random per-run seed, so there is no value -> tag table; vals holds each leaf's value

// Range "does every value appear an even number of times?" via xor hashing, with range assign. All indices 0-based,
// ranges inclusive [l, r].
// Each distinct value gets a 64-bit tag, splitmix64(value ^ seed): a bijection on 64-bit ints keyed by a random per-run
// seed, so equal values share a tag and distinct integers never collide. Xor over a range cancels tags in pairs, so an
// all-even range hashes to 0; false positives (unequal tags whose xor cancels) have probability ~q / 2^64.
// Lazy segment tree (2N iterative) over the tags: a node assigned value v holds tag(v) if it covers an odd number of
// leaves, else 0. Leaves tree[n..2n); a node used by a query or update is a perfect subtree of 2^s leaves (s = its
// level), and every internal node holds its pending assign: an update pushes the tags on its two boundary leaf paths,
// tags the covering nodes, then rebuilds both paths.
// T: an integer type (or anything std::hash takes).
// FAST MODE drawbacks compared with template.cpp:
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
struct XorEvenAssign {
    int n, h;
    unsigned long long seed;
    HotVector<unsigned long long> xr;  // xor of the tags under each node; leaves are xr[n + i]
    HotVector<T> vals;                 // vals[i] = the value at leaf i (once the assigns above it are pushed)
    HotVector<T> asg;                  // pending assign of each internal node
    HotVector<char> hasAsg;

    // O(N). Seeded from the clock: a fixed seed is hackable, since tags could be precomputed to collide.
    explicit XorEvenAssign(const vector<T>& arr)
        : n((int)arr.size()), h(n ? 32 - __builtin_clz(n) : 0),
          seed(mt19937_64(chrono::steady_clock::now().time_since_epoch().count())()), xr(2 * arr.size()), vals(arr),
          asg(arr.size()), hasAsg(arr.size(), 0) {
        for (int i = 0; i < n; i++) xr[n + i] = tagOf(arr[i]);
        for (int x = n - 1; x > 0; x--) xr[x] = xr[2 * x] ^ xr[2 * x + 1];
    }

    // O(1) -- the value's tag: splitmix64(v ^ seed)
    LEETCODE_NO_SANITIZE unsigned long long tagOf(const T& v) const {
        unsigned long long z;
        if constexpr (is_integral_v<T>) z = (unsigned long long)v;
        else z = hash<T>{}(v);
        z ^= seed;
        z += 0x9e3779b97f4a7c15ULL;
        z = (z ^ (z >> 30)) * 0xbf58476d1ce4e5b9ULL;
        z = (z ^ (z >> 27)) * 0x94d049bb133111ebULL;
        return z ^ (z >> 31);
    }

    // O(logN) -- true iff every value in a[l..r] appears an even number of times; needs 0 <= l <= r < n, else throws
    // out_of_range
    LEETCODE_NO_SANITIZE bool doAllElementsAppearEvenFrequency(int l, int r) {
        if (l < 0 || l > r || r >= n) throw out_of_range("doAllElementsAppearEvenFrequency: needs 0 <= l <= r < n");
        pushPath(l + n), pushPath(r + n);
        unsigned long long res = 0;
        for (int lo = l + n, hi = r + n + 1; lo < hi; lo >>= 1, hi >>= 1) {
            if (lo & 1) res ^= xr[lo++];
            if (hi & 1) res ^= xr[--hi];
        }
        return res == 0;
    }

    // O(logN) -- a[i] = v for i in [l, r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void rangeAssign(int l, int r, const T& v) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeAssign: needs 0 <= l <= r < n");
        unsigned long long t = tagOf(v);
        pushPath(l + n), pushPath(r + n);
        for (int lo = l + n, hi = r + n + 1; lo < hi; lo >>= 1, hi >>= 1) {
            if (lo & 1) apply(lo++, v, t);
            if (hi & 1) apply(--hi, v, t);
        }
        rebuild(l + n), rebuild(r + n);
    }

    // O(logN) -- a[i] = v; needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAssign(int i, const T& v) {
        if (i < 0 || i >= n) throw out_of_range("pointAssign: needs 0 <= i < n");
        int p = i + n;
        pushPath(p);
        vals[i] = v, xr[p] = tagOf(v);
        rebuild(p);
    }

    // O(logN) -- a[i]; needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE T pointGet(int i) {
        if (i < 0 || i >= n) throw out_of_range("pointGet: needs 0 <= i < n");
        pushPath(i + n);
        return vals[i];
    }

    // O(N) -- the whole array, every pending assign pushed down on the way
    LEETCODE_NO_SANITIZE vector<T> getAll() {
        for (int x = 1; x < n; x++) push(x);  // (parents before children)
        return vals;
    }

    // O(logN) -- a[i] += delta; needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAdd(int i, const T& delta) {
        if (i < 0 || i >= n) throw out_of_range("pointAdd: needs 0 <= i < n");
        pointAssign(i, T(pointGet(i) + delta));
    }

    // O(logN) -- a[i] = max(a[i], v); needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointChmax(int i, const T& v) {
        if (i < 0 || i >= n) throw out_of_range("pointChmax: needs 0 <= i < n");
        if (v > pointGet(i)) pointAssign(i, v);
    }

    // O(logN) -- a[i] = min(a[i], v); needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointChmin(int i, const T& v) {
        if (i < 0 || i >= n) throw out_of_range("pointChmin: needs 0 <= i < n");
        if (v < pointGet(i)) pointAssign(i, v);
    }

    // ---- internals ----

    LEETCODE_NO_SANITIZE void apply(int x, const T& v, unsigned long long t) {
        // every value under node x becomes v, whose tag is t
        if (x >= n) {
            vals[x - n] = v, xr[x] = t;
        } else {
            xr[x] = 0;  // (an assigned internal node is a perfect subtree of 2^s >= 2 leaves: an even count)
            asg[x] = v, hasAsg[x] = 1;
        }
    }

    LEETCODE_NO_SANITIZE void push(int x) {  // hand node x's pending assign to its children
        if (!hasAsg[x]) return;
        unsigned long long t = tagOf(asg[x]);
        apply(2 * x, asg[x], t), apply(2 * x + 1, asg[x], t);
        hasAsg[x] = 0;
    }

    LEETCODE_NO_SANITIZE void pushPath(int p) {  // hand down every pending assign on the path from the root to leaf p
        for (int s = h; s > 0; s--) push(p >> s);
    }

    LEETCODE_NO_SANITIZE void rebuild(int p) {
        // recompute every ancestor of leaf p (an assigned node keeps its own value)
        for (p >>= 1; p; p >>= 1)
            if (!hasAsg[p]) xr[p] = xr[2 * p] ^ xr[2 * p + 1];
    }
};
