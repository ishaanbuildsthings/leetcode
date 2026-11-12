// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/sqrt-strided-add/fast.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: getAll pointAdd pointAssign pointChmax pointChmin pointGet stridedAdd
// @data-structure-type: sqrt
// @complexities:
//   getAll: N*sqrt(NlogN)
//   pointAdd: 1
//   pointAssign: sqrt(NlogN)
//   pointChmax: sqrt(NlogN)
//   pointChmin: sqrt(NlogN)
//   pointGet: sqrt(NlogN)
//   stridedAdd: sqrt(NlogN)
//   build: N*sqrt(N/logN)
// @memory:
//   layout: none
//   node: diffs[1*N*sqrt(N/logN)]
//   tags: none
//   other: A[1*N] offsets[1*N]
//   note: a small step is a range add on that step's Fenwick tree of differences, a big step walks its positions, and a point read adds up every small step

// Strided add with point reads and writes: stridedAdd(l, r, step, v) adds v to a[l], a[l + step], ... up to at most r
// (the last position used may be below r). A strided sum on top of this has no good bound: two different steps
// overlap in a pattern that depends on both. All indices 0-based, ranges inclusive.
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
struct StridedQueries {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    int n, strides;
    HotVector<S> A;
    // offsets[step * (step - 1) / 2 + residue]: where that residue class starts in that stride's list
    HotVector<int> offsets;
    HotVector<S> diffs;  // one Fenwick tree of differences per kept step, n + 2 slots each

    // O(build) -- arr: the initial array. cutoff: a Fenwick tree is kept for steps up to it (more memory and slower
    // reads, faster big-step adds); leave it out for sqrt(n / log n)
    explicit StridedQueries(const vector<T>& arr, int cutoff = -1) {
        n = (int)arr.size();
        A.assign(arr.begin(), arr.end());
        strides = cutoff != -1 ? cutoff : min(n, max(1, (int)sqrt(n / max(1.0, log2(n + 1.0)))));
        if (strides < 0 || strides > n) throw out_of_range("StridedQueries: needs 0 <= cutoff <= n");
        offsets.assign((size_t)strides * (strides + 1) / 2, 0);
        for (int step = 1; step <= strides; step++) {
            int used = 0;
            for (int residue = 0; residue < step; residue++) {
                offsets[step * (step - 1) / 2 + residue] = used;
                if (residue < n) used += (n - residue + step - 1) / step;
            }
        }
        diffs.assign((size_t)strides * (n + 2), 0);
    }

    // O(sqrt(N logN)) -- a[l] += v, a[l + step] += v, ... up to at most r; needs 0 <= l <= r < n and step >= 1, else
    // throws out_of_range
    LEETCODE_NO_SANITIZE void stridedAdd(int l, int r, int step, T v) {
        if (l < 0 || l > r || r >= n) throw out_of_range("stridedAdd: needs 0 <= l <= r < n");
        if (step < 1) throw out_of_range("stridedAdd: needs step >= 1");
        int last = l + (r - l) / step * step;
        if (step > strides) {
            for (int i = l; i <= last; i += step) A[i] += v;
            return;
        }
        addDiff(step, listIndex(step, l), S(v));
        addDiff(step, listIndex(step, last) + 1, -S(v));
    }

    // O(sqrt(N logN)) -- the current a[i]; needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE S pointGet(int i) const {
        if (i < 0 || i >= n) throw out_of_range("pointGet: needs 0 <= i < n");
        S res = A[i];
        for (int step = 1; step <= strides; step++) {
            const S* tree = diffs.data() + (size_t)(step - 1) * (n + 2);
            for (int node = listIndex(step, i) + 1; node > 0; node -= node & -node) res += tree[node];
        }
        return res;
    }

    // O(1) -- a[i] += v; needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAdd(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointAdd: needs 0 <= i < n");
        A[i] += v;
    }

    // O(sqrt(N logN)) -- a[i] = v (overwrite); needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAssign(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointAssign: needs 0 <= i < n");
        A[i] += S(v) - pointGet(i);
    }

    // O(sqrt(N logN)) -- a[i] = max(a[i], v); needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointChmax(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointChmax: needs 0 <= i < n");
        S current = pointGet(i);
        if (S(v) > current) A[i] += S(v) - current;
    }

    // O(sqrt(N logN)) -- a[i] = min(a[i], v); needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointChmin(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointChmin: needs 0 <= i < n");
        S current = pointGet(i);
        if (S(v) < current) A[i] += S(v) - current;
    }

    // O(N * sqrt NlogN) -- the whole array
    LEETCODE_NO_SANITIZE vector<S> getAll() const {
        vector<S> out(n);
        for (int i = 0; i < n; i++) out[i] = pointGet(i);
        return out;
    }

    // ---- internals ----

    LEETCODE_NO_SANITIZE int listIndex(int step, int i) const {
        return offsets[step * (step - 1) / 2 + i % step] + i / step;
    }

    LEETCODE_NO_SANITIZE void addDiff(int step, int index, S v) {
        S* tree = diffs.data() + (size_t)(step - 1) * (n + 2);
        for (int node = index + 1; node <= n + 1; node += node & -node) tree[node] += v;
    }
};
