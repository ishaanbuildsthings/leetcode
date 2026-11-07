// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/sqrt-strided-static-min-max-or/fast.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: stridedMax stridedMin stridedOrQuery
// @data-structure-type: sqrt
// @complexities:
//   stridedMax: N*log(N)
//   stridedMin: N*log(N)
//   stridedOrQuery: N*log(N)
//   build: N
// @memory:
//   layout: none
//   node: minTable[1*N*log(N)] maxTable[1*N*log(N)] orTable[1*N*log(N)]
//   tags: none
//   other: A[1*N]
//   note: the listed cost is a rebuild. Each op keeps one table, for the last step it saw; a repeat of that step is O(1) and a step above sqrt(N) walks, so sorting queries by step offline costs one rebuild per distinct step

// Static strided queries in linear memory: each query covers a[l], a[l + step], a[l + 2 * step], ... up to at most r
// (the last position used may be below r). Each op keeps a single table for the last step it saw, rebuilt when the
// step changes, so the expected use is offline: sort the queries by step, then ask them in that order. All indices
// 0-based, ranges inclusive.
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
struct StridedQueries {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    int n, levels = 1;
    HotVector<T> A;
    HotVector<T> minTable;
    int minStep = 0;  // the step minTable was built for
    HotVector<T> maxTable;
    int maxStep = 0;  // the step maxTable was built for
    HotVector<T> orTable;
    int orStep = 0;  // the step orTable was built for

    // O(build) -- arr: the initial array
    explicit StridedQueries(const vector<T>& arr) {
        n = (int)arr.size();
        A = arr;
        while ((1 << levels) <= n) levels++;
        minTable.assign((size_t)levels * n, T(0));
        copy(A.begin(), A.end(), minTable.begin());
        maxTable.assign((size_t)levels * n, T(0));
        copy(A.begin(), A.end(), maxTable.begin());
        orTable.assign((size_t)levels * n, T(0));
        copy(A.begin(), A.end(), orTable.begin());
    }

    // min of a[l], a[l + step], ..., up to at most r. O(1) when step is the last step this op built for, so ask queries grouped by
    // step; needs 0 <= l <= r < n and step >= 1, else throws out_of_range
    LEETCODE_NO_SANITIZE T stridedMin(int l, int r, int step) {
        if (l < 0 || l > r || r >= n) throw out_of_range("stridedMin: needs 0 <= l <= r < n");
        if (step < 1) throw out_of_range("stridedMin: needs step >= 1");
        int last = l + (r - l) / step * step, count = (r - l) / step + 1;
        if (step != minStep && (count <= 32 || (long long)step * step > n)) {
            T res = A[l];
            for (int i = l + step; i <= last; i += step) res = min(res, A[i]);
            return res;
        }
        if (step != minStep) rebuildMin(step);
        int level = 31 - __builtin_clz(count);
        size_t base = (size_t)level * n;
        return min(minTable[base + l], minTable[base + last - ((1 << level) - 1) * step]);
    }

    // max of a[l], a[l + step], ..., up to at most r. O(1) when step is the last step this op built for, so ask queries grouped by
    // step; needs 0 <= l <= r < n and step >= 1, else throws out_of_range
    LEETCODE_NO_SANITIZE T stridedMax(int l, int r, int step) {
        if (l < 0 || l > r || r >= n) throw out_of_range("stridedMax: needs 0 <= l <= r < n");
        if (step < 1) throw out_of_range("stridedMax: needs step >= 1");
        int last = l + (r - l) / step * step, count = (r - l) / step + 1;
        if (step != maxStep && (count <= 32 || (long long)step * step > n)) {
            T res = A[l];
            for (int i = l + step; i <= last; i += step) res = max(res, A[i]);
            return res;
        }
        if (step != maxStep) rebuildMax(step);
        int level = 31 - __builtin_clz(count);
        size_t base = (size_t)level * n;
        return max(maxTable[base + l], maxTable[base + last - ((1 << level) - 1) * step]);
    }

    // a[l] | a[l + step] | ..., up to at most r. O(1) when step is the last step this op built for, so ask queries grouped by
    // step; needs 0 <= l <= r < n and step >= 1, else throws out_of_range
    LEETCODE_NO_SANITIZE T stridedOrQuery(int l, int r, int step) {
        if (l < 0 || l > r || r >= n) throw out_of_range("stridedOrQuery: needs 0 <= l <= r < n");
        if (step < 1) throw out_of_range("stridedOrQuery: needs step >= 1");
        int last = l + (r - l) / step * step, count = (r - l) / step + 1;
        if (step != orStep && (count <= 32 || (long long)step * step > n)) {
            T res = A[l];
            for (int i = l + step; i <= last; i += step) res = (res | A[i]);
            return res;
        }
        if (step != orStep) rebuildOr(step);
        int level = 31 - __builtin_clz(count);
        size_t base = (size_t)level * n;
        return (orTable[base + l] | orTable[base + last - ((1 << level) - 1) * step]);
    }

    // ---- internals ----

    LEETCODE_NO_SANITIZE void rebuildMin(int step) {
        minStep = step;
        for (int level = 1; level < levels; level++) {
            long long jump = (long long)step << (level - 1);
            if (jump >= n) break;
            const T* previous = minTable.data() + (size_t)(level - 1) * n;
            T* current = minTable.data() + (size_t)level * n;
            for (int i = 0; i < n; i++) current[i] = i + jump < n ? min(previous[i], previous[i + jump]) : previous[i];
        }
    }

    LEETCODE_NO_SANITIZE void rebuildMax(int step) {
        maxStep = step;
        for (int level = 1; level < levels; level++) {
            long long jump = (long long)step << (level - 1);
            if (jump >= n) break;
            const T* previous = maxTable.data() + (size_t)(level - 1) * n;
            T* current = maxTable.data() + (size_t)level * n;
            for (int i = 0; i < n; i++) current[i] = i + jump < n ? max(previous[i], previous[i + jump]) : previous[i];
        }
    }

    LEETCODE_NO_SANITIZE void rebuildOr(int step) {
        orStep = step;
        for (int level = 1; level < levels; level++) {
            long long jump = (long long)step << (level - 1);
            if (jump >= n) break;
            const T* previous = orTable.data() + (size_t)(level - 1) * n;
            T* current = orTable.data() + (size_t)level * n;
            for (int i = 0; i < n; i++) current[i] = i + jump < n ? (previous[i] | previous[i + jump]) : previous[i];
        }
    }
};
