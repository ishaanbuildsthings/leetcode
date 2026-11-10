// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAdd-rangeMin/fast.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: getAll minAll pointAdd pointAssign pointChmax pointChmin pointGet rangeAdd rangeMin
// @data-structure-type: lazy-seg-tree
// @complexities:
//   getAll: N
//   pointAdd: log(N)
//   pointAssign: log(N)
//   pointChmax: log(N)
//   pointChmin: log(N)
//   pointGet: log(N)
//   rangeAdd: log(N)
//   rangeMin: log(N)
//   minAll: log(N)
//   build: N
// @memory:
//   layout: 2n-iterative
//   node: mn[2*N]
//   tags: add[1*N]
//   other: none
//   note: tags live on the N internal nodes only; each holds one clamp tag x -> x + add

// Range add with range min queries, plus point ops. All indices 0-based, ranges inclusive [l, r].
// Iterative 2N lazy tree: values on the leaves, a tag on each internal node meaning "applied here, not yet pushed
// to my children". The tag is the map x -> x + add; these maps compose into the same form, and each is
// monotone, so it sends a node's min / max straight to the new min / max.
// An update pushes the tags on its two boundary paths, tags the covering nodes, then rebuilds the two paths.
// T: int, long long, ...; the INF / NEG sentinels in the tags are never shifted.
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
struct AddMinTree {
    static constexpr T INF = numeric_limits<T>::max(), NEG = numeric_limits<T>::lowest();
    int n, h;
    HotVector<T> mn;  // 2N: leaves are tree[n..2n)
    HotVector<T> add;  // N: tags on internal nodes

    // O(N)
    explicit AddMinTree(const vector<T>& a) : n((int)a.size()),
        h(a.empty() ? 0 : 32 - __builtin_clz((unsigned)a.size())) {
        mn.assign(2 * n, INF);
        for (int i = 0; i < n; i++) mn[n + i] = a[i];
        for (int x = n - 1; x > 0; x--) mn[x] = std::min(mn[2 * x], mn[2 * x + 1]);
        add.assign(n, 0);
    }

    LEETCODE_NO_SANITIZE static T clampValue(T v, T c) { v += c; return v; }

    // apply the map to node x: to its values now, and (if internal) on top of its pending tag
    LEETCODE_NO_SANITIZE void apply(int x, T c) {
        mn[x] = clampValue(mn[x], c);
        if (x < n) {
            add[x] += c;
        }
    }

    // push every tag on the root-to-leaf path of leaf p down one level
    LEETCODE_NO_SANITIZE void push(int p) {
        for (int s = h; s > 0; s--) {
            int x = p >> s;
            if (add[x] != 0) {
                apply(2 * x, add[x]), apply(2 * x + 1, add[x]);
                add[x] = 0;
            }
        }
    }

    // recompute the ancestors of leaf p; each keeps the effect of its own pending tag
    LEETCODE_NO_SANITIZE void rebuild(int p) {
        while (p > 1) {
            p >>= 1;
            mn[p] = clampValue(std::min(mn[2 * p], mn[2 * p + 1]), add[p]);
        }
    }

    LEETCODE_NO_SANITIZE void update(int l, int r, T c) {
        if (l > r) return;
        int l0 = l + n, r0 = r + n;
        push(l0), push(r0);
        for (int i = l0, j = r0 + 1; i < j; i >>= 1, j >>= 1) {
            if (i & 1) apply(i++, c);
            if (j & 1) apply(--j, c);
        }
        rebuild(l0), rebuild(r0);
    }

    // O(logN) -- a[i] += v for i in [l, r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void rangeAdd(int l, int r, T v) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeAdd: needs 0 <= l <= r < n");
        update(l, r, v);
    }

    // O(logN) -- min of a[l..r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE T rangeMin(int l, int r) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeMin: needs 0 <= l <= r < n");
        l += n, r += n;
        push(l), push(r);
        T res = INF;
        for (r++; l < r; l >>= 1, r >>= 1) {
            if (l & 1) res = std::min(res, mn[l++]);
            if (r & 1) res = std::min(res, mn[--r]);
        }
        return res;
    }

    // O(N) -- the whole array: push every tag down (a parent's index is below its children's, so in index order
    // each node's tag is complete when it is pushed), then read the leaves
    LEETCODE_NO_SANITIZE vector<T> getAll() {
        for (int x = 1; x < n; x++)
            if (add[x] != 0) {
                apply(2 * x, add[x]), apply(2 * x + 1, add[x]);
                add[x] = 0;
            }
        return vector<T>(mn.begin() + n, mn.end());
    }

    // O(logN) -- a[i]; needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE T pointGet(int i) {
        if (i < 0 || i >= n) throw out_of_range("pointGet: needs 0 <= i < n");
        push(i + n);
        return mn[i + n];
    }

    // O(logN) -- a[i] = v; needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAssign(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointAssign: needs 0 <= i < n");
        int p = i + n;
        push(p);
        mn[p] = v;
        rebuild(p);
    }

    // O(logN) -- a[i] += delta; needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAdd(int i, T delta) {
        if (i < 0 || i >= n) throw out_of_range("pointAdd: needs 0 <= i < n");
        pointAssign(i, pointGet(i) + delta);
    }

    // O(logN) -- a[i] = max(a[i], v); needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointChmax(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointChmax: needs 0 <= i < n");
        if (v > pointGet(i)) pointAssign(i, v);
    }

    // O(logN) -- a[i] = min(a[i], v); needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointChmin(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointChmin: needs 0 <= i < n");
        if (v < pointGet(i)) pointAssign(i, v);
    }

    // O(log(N)) -- min of the whole array a[0..n-1] (rangeMin(0, n - 1)); needs n >= 1, else throws out_of_range
    LEETCODE_NO_SANITIZE auto minAll() {
        if (n < 1) throw out_of_range("minAll: needs n >= 1");
        return rangeMin(0, n - 1);
    }

};
