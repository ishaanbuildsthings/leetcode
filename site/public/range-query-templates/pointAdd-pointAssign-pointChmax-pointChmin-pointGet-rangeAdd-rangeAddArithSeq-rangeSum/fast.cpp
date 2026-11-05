// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAdd-rangeAddArithSeq-rangeSum/fast.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: getAll pointAdd pointAssign pointChmax pointChmin pointGet rangeAdd rangeAddArithSeq rangeSum
// @data-structure-type: BIT
// @complexities:
//   getAll: N
//   pointAdd: log(N)
//   pointAssign: log(N)
//   pointChmax: log(N)
//   pointChmin: log(N)
//   pointGet: log(N)
//   rangeAdd: log(N)
//   rangeAddArithSeq: log(N)
//   rangeSum: log(N)
//   build: N
// @memory:
//   layout: none
//   node: bA[1*N] bB[1*N] bC[1*N]
//   tags: none
//   other: none
//   note: prefix sums are kept as A(x) + B(x) * x + C(x) * x(x+1)/2 with A, B, C three Fenwick trees

// Range add of an arithmetic sequence (and plain range add) + range sum with three Fenwick trees, no lazy tags.
// All indices 0-based, ranges inclusive [l, r].
// Adding c0 + c1 * i to every i in [l, r] changes the prefix sum P(x) = a[0] + ... + a[x] by
//   x in [l, r]:  c0 * (x - l + 1) + c1 * (T(x) - T(l - 1))        T(k) = k * (k + 1) / 2
//   x > r:        the whole added total
// so keep P(x) = A(x) + B(x) * x + C(x) * T(x), where A, B, C are prefix sums of point updates made at l and r + 1.
// Using T(x) instead of x^2 keeps every coefficient an integer (no division by 2).
// T: int, long long, ...; sums are kept in S (long long for small T).
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
struct ArithSeqSumBIT {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    int n;
    HotVector<S> bA, bB, bC;  // 1-indexed

    LEETCODE_NO_SANITIZE static S tri(S k) { return k * (k + 1) / 2; }

    // O(N)
    explicit ArithSeqSumBIT(const vector<T>& a) : n((int)a.size()), bA(n + 1), bB(n + 1), bC(n + 1) {
        for (int i = 0; i < n; i++) bA[i + 1] = a[i];  // a[i] alone adds a[i] to every P(x) with x >= i
        for (int i = 1; i <= n; i++) {
            int j = i + (i & -i);
            if (j <= n) bA[j] += bA[i];
        }
    }

    LEETCODE_NO_SANITIZE void point(int i, S a, S b, S c) {
        for (i++; i <= n; i += i & -i) bA[i] += a, bB[i] += b, bC[i] += c;
    }

    // O(logN) -- a[0] + ... + a[x] (0 for x = -1)
    LEETCODE_NO_SANITIZE S prefix(int x) const {
        S sa = 0, sb = 0, sc = 0;
        for (int i = x + 1; i > 0; i &= i - 1) sa += bA[i], sb += bB[i], sc += bC[i];
        return sa + sb * x + sc * tri(x);
    }

    // O(logN) -- a[l + j] += start + j * step for j in [0, r - l]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void rangeAddArithSeq(int l, int r, T start, T step) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeAddArithSeq: needs 0 <= l <= r < n");
        if (l > r) return;
        S c0 = S(start) - S(step) * l, c1 = step;  // adding c0 + c1 * i at index i
        S a = c0 * (1 - l) - c1 * tri(l - 1);
        point(l, a, c0, c1);
        if (r + 1 < n) {
            S total = c0 * (r - l + 1) + c1 * (tri(r) - tri(l - 1));
            point(r + 1, total - a, -c0, -c1);
        }
    }

    // O(logN) -- a[i] += v for i in [l, r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void rangeAdd(int l, int r, T v) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeAdd: needs 0 <= l <= r < n");
        rangeAddArithSeq(l, r, v, 0);
    }

    // O(logN) -- a[l] + ... + a[r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE S rangeSum(int l, int r) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeSum: needs 0 <= l <= r < n");
        return l <= r ? prefix(r) - prefix(l - 1) : S(0);
    }

    // O(logN) -- a[i]; needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE T pointGet(int i) const {
        if (i < 0 || i >= n) throw out_of_range("pointGet: needs 0 <= i < n");
        return T(rangeSum(i, i));
    }

    // O(N) -- the whole array: undo the Fenwick sums on a copy (last index first: entry i was added into
    // i + lowbit(i) once complete), then one pass of running prefix sums
    LEETCODE_NO_SANITIZE vector<T> getAll() const {
        vector<S> A(bA), B(bB), C(bC);
        for (int i = n; i > 0; i--) {
            int j = i + (i & -i);
            if (j <= n) A[j] -= A[i], B[j] -= B[i], C[j] -= C[i];
        }
        vector<T> out(n);
        S sa = 0, sb = 0, sc = 0, prev = 0;
        for (int x = 0; x < n; x++) {
            sa += A[x + 1], sb += B[x + 1], sc += C[x + 1];
            S p = sa + sb * x + sc * tri(x);
            out[x] = T(p - prev), prev = p;
        }
        return out;
    }

    // O(logN) -- a[i] += delta; needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAdd(int i, T delta) {
        if (i < 0 || i >= n) throw out_of_range("pointAdd: needs 0 <= i < n");
        rangeAdd(i, i, delta);
    }

    // O(logN) -- a[i] = v; needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAssign(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointAssign: needs 0 <= i < n");
        rangeAdd(i, i, v - pointGet(i));
    }

    // O(logN) -- a[i] = max(a[i], v); needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointChmax(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointChmax: needs 0 <= i < n");
        T cur = pointGet(i);
        if (v > cur) rangeAdd(i, i, v - cur);
    }

    // O(logN) -- a[i] = min(a[i], v); needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointChmin(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointChmin: needs 0 <= i < n");
        T cur = pointGet(i);
        if (v < cur) rangeAdd(i, i, v - cur);
    }
};
