// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAndQuery-rangeOrQuery-rangeSum-rangeXorApply/fast.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: getAll pointAdd pointAssign pointChmax pointChmin pointGet rangeAndQuery rangeOrQuery rangeSum rangeXorApply
// @data-structure-type: lazy-seg-tree
// @complexities:
//   getAll: N*log(U)
//   pointAdd: log(N)*log(U)
//   pointAssign: log(N)*log(U)
//   pointChmax: log(N)*log(U)
//   pointChmin: log(N)*log(U)
//   pointGet: log(N)*log(U)
//   rangeAndQuery: log(N)*log(U)
//   rangeOrQuery: log(N)*log(U)
//   rangeSum: log(N)*log(U)
//   rangeXorApply: log(N)*log(U)
//   build: N*log(U)
// @memory:
//   layout: 2n-iterative
//   node: cnt[2*N*log(U)]
//   tags: xorTag[1*N]
//   other: none
//   note: cnt keeps, per node and per bit, how many values below have that bit set (bits = log U, 20 by default); tags live on internal nodes only

// Range xor= with range sum / and / or queries, plus point ops. All indices 0-based, ranges inclusive.
// Values live in [0, 2^bits). Each node counts, for every bit, how many of its values have that bit set. A xor X
// flips the bits set in X: per bit, a flip turns the count c into length - c, so the tag is just the mask to
// flip (this is BitCountTree without the AND tag that only and= / or= need).
// So every update is an ordinary lazy tag, a true O(log N * bits) with no amortization (unlike bitwise beats,
// which cannot apply xor to a node whose values disagree on a bit). Sum = sum over bits of count * 2^bit.
// Iterative 2N lazy tree; a covering node at level s is a perfect subtree of 2^s leaves.
// T: int, long long, ...; sums accumulate in S (long long for small T).
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
    LEETCODE_NO_SANITIZE_INLINE typename vector<U>::const_reference operator[](size_t i) const { return this->_M_impl._M_start[i]; }
    LEETCODE_NO_SANITIZE_INLINE size_t size() const { return size_t(this->_M_impl._M_finish - this->_M_impl._M_start); }
#endif
};

template <typename T>
struct BitCountTree {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    int n, h, bits;
    T full;
    HotVector<int> cnt;          // cnt[x * bits + b] = # of values under node x with bit b set (2N nodes)
    HotVector<T> xorTag;  // N: tags on internal nodes

    // O(N * bits)
    explicit BitCountTree(const vector<T>& a, int bits = 20)
        : n((int)a.size()), h(a.empty() ? 0 : 32 - __builtin_clz((unsigned)a.size())), bits(bits), full(T((T(1) << bits) - 1)),
          cnt(2 * a.size() * bits), xorTag(a.size(), 0) {
        for (int i = 0; i < n; i++)
            for (int b = 0; b < bits; b++) cnt[(n + i) * bits + b] = a[i] >> b & 1;
        for (int x = n - 1; x > 0; x--)
            for (int b = 0; b < bits; b++) cnt[x * bits + b] = cnt[2 * x * bits + b] + cnt[(2 * x + 1) * bits + b];
    }

    // v -> v ^ xr on node x, which covers k slots
    LEETCODE_NO_SANITIZE void apply(int x, int k, T xr) {
        int* c = &cnt[x * bits];
        for (int b = 0; b < bits; b++) {
            if (xr >> b & 1) c[b] = k - c[b];
        }
        if (x < n) xorTag[x] ^= xr;
    }

    LEETCODE_NO_SANITIZE void push(int p) {
        for (int s = h; s > 0; s--) {
            int x = p >> s;
            if (xorTag[x]) {
                int k = 1 << (s - 1);
                apply(2 * x, k, xorTag[x]), apply(2 * x + 1, k, xorTag[x]);
                xorTag[x] = 0;
            }
        }
    }

    LEETCODE_NO_SANITIZE void rebuild(int p) {
        for (int k = 2; p > 1; k <<= 1) {
            p >>= 1;
            for (int b = 0; b < bits; b++) {
                int v = cnt[2 * p * bits + b] + cnt[(2 * p + 1) * bits + b];
                if (xorTag[p] >> b & 1) v = k - v;
                cnt[p * bits + b] = v;
            }
        }
    }

    LEETCODE_NO_SANITIZE void update(int l, int r, T xr) {
        if (l > r) return;
        int l0 = l + n, r0 = r + n;
        push(l0), push(r0);
        for (int i = l0, j = r0 + 1, k = 1; i < j; i >>= 1, j >>= 1, k <<= 1) {
            if (i & 1) apply(i++, k, xr);
            if (j & 1) apply(--j, k, xr);
        }
        rebuild(l0), rebuild(r0);
    }

    // the canonical nodes of [l, r] with their lengths, after pushing the two boundary paths
    LEETCODE_NO_SANITIZE vector<pair<int, int>> nodes(int l, int r) {
        vector<pair<int, int>> out;
        l += n, r += n;
        push(l), push(r);
        for (int k = 1, rr = r + 1; l < rr; l >>= 1, rr >>= 1, k <<= 1) {
            if (l & 1) out.push_back({l++, k});
            if (rr & 1) out.push_back({--rr, k});
        }
        return out;
    }

    // O(logN * bits) -- a[i] ^= X for i in [l, r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void rangeXorApply(int l, int r, T X) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeXorApply: needs 0 <= l <= r < n");
        update(l, r, X & full);
    }

    // O(logN * bits) -- a[l] + ... + a[r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE S rangeSum(int l, int r) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeSum: needs 0 <= l <= r < n");
        if (l > r) return 0;
        S res = 0;
        for (auto [x, k] : nodes(l, r))
            for (int b = 0; b < bits; b++) res += S(cnt[x * bits + b]) << b;
        return res;
    }

    // O(logN * bits) -- a[l] & ... & a[r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE T rangeAndQuery(int l, int r) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeAndQuery: needs 0 <= l <= r < n");
        T res = full;
        for (auto [x, k] : nodes(l, r))
            for (int b = 0; b < bits; b++)
                if (cnt[x * bits + b] != k) res &= ~(T(1) << b);
        return res;
    }

    // O(logN * bits) -- a[l] | ... | a[r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE T rangeOrQuery(int l, int r) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeOrQuery: needs 0 <= l <= r < n");
        T res = 0;
        for (auto [x, k] : nodes(l, r))
            for (int b = 0; b < bits; b++)
                if (cnt[x * bits + b]) res |= T(1) << b;
        return res;
    }

    // O(logN * bits) -- a[i]; needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE T pointGet(int i) {
        if (i < 0 || i >= n) throw out_of_range("pointGet: needs 0 <= i < n");
        int p = i + n;
        push(p);
        T v = 0;
        for (int b = 0; b < bits; b++) v |= T(cnt[p * bits + b]) << b;
        return v;
    }

    // O(N) -- the whole array: push every tag down one level at a time from the root (the nodes s levels above
    // the leaves are (n >> s) .. ((2n - 1) >> s); their children cover k = 1 << (s - 1) leaves), then read the leaves
    LEETCODE_NO_SANITIZE vector<T> getAll() {
        for (int s = h; s > 0; s--) {
            int k = 1 << (s - 1);
            for (int x = max(1, n >> s); x <= (2 * n - 1) >> s; x++)
                if (xorTag[x]) {
                    apply(2 * x, k, xorTag[x]), apply(2 * x + 1, k, xorTag[x]);
                    xorTag[x] = 0;
                }
        }
        vector<T> out(n, 0);
        for (int i = 0; i < n; i++)
            for (int b = 0; b < bits; b++) out[i] |= T(cnt[(n + i) * bits + b]) << b;
        return out;
    }

    // O(logN * bits) -- a[i] = v & FULL; needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAssign(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointAssign: needs 0 <= i < n");
        int p = i + n;
        push(p);
        v &= full;
        for (int b = 0; b < bits; b++) cnt[p * bits + b] = v >> b & 1;
        rebuild(p);
    }

    // O(logN * bits) -- a[i] = (a[i] + delta) & FULL; needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAdd(int i, T delta) {
        if (i < 0 || i >= n) throw out_of_range("pointAdd: needs 0 <= i < n");
        pointAssign(i, pointGet(i) + delta);
    }

    // O(logN * bits) -- a[i] = max(a[i], v); needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointChmax(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointChmax: needs 0 <= i < n");
        if (v > pointGet(i)) pointAssign(i, v);
    }

    // O(logN * bits) -- a[i] = min(a[i], v); needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointChmin(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointChmin: needs 0 <= i < n");
        if (v < pointGet(i)) pointAssign(i, v);
    }
};
