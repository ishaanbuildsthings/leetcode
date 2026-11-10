// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/costMonoDecreasing-costMonoIncreasing-costStrictDecreasing-costStrictIncreasing-pointGet-rangeSum/fast.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: costMonoDecreasing costMonoIncreasing costStrictDecreasing costStrictIncreasing pointGet rangeSum sumAll
// @data-structure-type: sparse-table
// @complexities:
//   costMonoDecreasing: 1
//   costMonoIncreasing: 1
//   costStrictDecreasing: 1
//   costStrictIncreasing: 1
//   pointGet: 1
//   rangeSum: 1
//   sumAll: 1
//   build: N*log(N)
// @memory:
//   layout: none
//   node: sp[1*N*log(N)]
//   tags: none
//   other: arr[2*N] pf[2*N] suff[1*N]
//   note: per cost kind you call (shown for one): each kind builds its own MonoIncreaseCost view (a, reversed a, a[i] - i, reversed a[i] + i) on its first query, so kinds you never call cost nothing; rangeSum / pointGet need no view
// @original-file-url: https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/segment-trees/normal/costToMakeSubarrayMonoIncreasing.cpp

// Min increments to make a range non-decreasing (increments only). Static array, 0-indexed, ranges inclusive.
// Build O(N log N); every query O(1). T: int, long long, ...; sums accumulate in S (long long for small T).
template <typename T>
struct MonoIncreaseCost {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    int n;
    vector<T> arr;              // private copy of the input
    vector<S> pf, suff;         // suff[i] = sum of prefix maxes over [i, n), measured from i
    vector<vector<int>> sp;     // sparse table of argmax (leftmost on ties)

    explicit MonoIncreaseCost(const vector<T>& a) : n((int)a.size()), arr(a), pf(n + 1), suff(n + 1) {
        for (int i = 0; i < n; i++) pf[i + 1] = pf[i] + S(arr[i]);
        vector<int> st;
        for (int i = n - 1; i >= 0; i--) {
            while (!st.empty() && arr[st.back()] <= arr[i]) st.pop_back();
            int nxt = st.empty() ? n : st.back();
            suff[i] = S(arr[i]) * (nxt - i) + suff[nxt];
            st.push_back(i);
        }
        int levels = 1;
        while ((1 << levels) <= n) levels++;
        sp.assign(levels, {});
        sp[0].resize(n);
        iota(sp[0].begin(), sp[0].end(), 0);
        for (int j = 1; j < levels; j++) {
            int len = n - (1 << j) + 1, half = 1 << (j - 1);
            sp[j].resize(len);
            for (int i = 0; i < len; i++) {
                int x = sp[j - 1][i], y = sp[j - 1][i + half];
                sp[j][i] = arr[x] >= arr[y] ? x : y;
            }
        }
    }

    // O(1) -- a[l] + ... + a[r] (0 if l > r); needs 0 <= l <= r < n, else throws out_of_range
    S rangeSum(int l, int r) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeSum: needs 0 <= l <= r < n");
        return r >= l ? pf[r + 1] - pf[l] : S(0);
    }

    // O(1) -- index of the max of a[l..r], leftmost on ties
    int argMax(int l, int r) const {
        int j = 31 - __builtin_clz(r - l + 1);
        int x = sp[j][l], y = sp[j][r - (1 << j) + 1];
        return arr[x] >= arr[y] ? x : y;
    }

    // O(1) -- min total +1 increments to make a[l..r] non-decreasing; needs 0 <= l <= r < n, else throws out_of_range
    S costMonoIncreasing(int l, int r) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("costMonoIncreasing: needs 0 <= l <= r < n");
        int m = argMax(l, r);
        S endsAt = (suff[l] - suff[m]) + S(arr[m]) * (r - m + 1);
        return endsAt - rangeSum(l, r);
    }

    // O(1) -- a[i]; needs 0 <= i < n, else throws out_of_range
    T pointGet(int i) const {
        if (i < 0 || i >= n) throw out_of_range("pointGet: needs 0 <= i < n");
        return arr[i];
    }

    // O(1) -- sum of the whole array a[0..n-1] (rangeSum(0, n - 1)); needs n >= 1, else throws out_of_range
    auto sumAll() {
        if (n < 1) throw out_of_range("sumAll: needs n >= 1");
        return rangeSum(0, n - 1);
    }

};

// Min +1 increments to make a[l..r] non-decreasing / non-increasing / strictly increasing / strictly decreasing.
// One structure answers "non-decreasing"; the other three reduce to it:
//   non-increasing on a        == non-decreasing on a reversed
//   strictly increasing on a   == non-decreasing on b[i] = a[i] - i      (a[i] < a[i+1]  <=>  b[i] <= b[i+1])
//   strictly decreasing on a   == non-increasing on c[i] = a[i] + i
// Adding +1 to a[i] adds it to b[i] / c[i] too, so the costs carry over. Each view is built on its first query, so
// you only pay for the cost kinds you call.
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
struct MonoCosts {
    using Cost = MonoIncreaseCost<T>;
    using S = typename Cost::S;
    int n;
    HotVector<T> arr;
    HotVector<S> pf;
    unique_ptr<Cost> inc, dec, sinc, sdec;

    // O(N); each cost kind builds its own O(N log N) view on its first query
    explicit MonoCosts(const vector<T>& a) : n((int)a.size()), arr(a), pf(n + 1) {
        for (int i = 0; i < n; i++) pf[i + 1] = pf[i] + S(arr[i]);
    }

    // O(1) -- min +1 increments to make a[l..r] non-decreasing; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE S costMonoIncreasing(int l, int r) {
        if (l < 0 || l > r || r >= n) throw out_of_range("costMonoIncreasing: needs 0 <= l <= r < n");
        if (!inc) inc = make_unique<Cost>(arr);
        return inc->costMonoIncreasing(l, r);
    }

    // O(1) -- min +1 increments to make a[l..r] non-increasing; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE S costMonoDecreasing(int l, int r) {
        if (l < 0 || l > r || r >= n) throw out_of_range("costMonoDecreasing: needs 0 <= l <= r < n");
        if (!dec) dec = make_unique<Cost>(vector<T>(arr.rbegin(), arr.rend()));
        return dec->costMonoIncreasing(n - 1 - r, n - 1 - l);
    }

    // O(1) -- min +1 increments to make a[l..r] strictly increasing; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE S costStrictIncreasing(int l, int r) {
        if (l < 0 || l > r || r >= n) throw out_of_range("costStrictIncreasing: needs 0 <= l <= r < n");
        if (!sinc) {
            vector<T> b(n);
            for (int i = 0; i < n; i++) b[i] = arr[i] - T(i);
            sinc = make_unique<Cost>(b);
        }
        return sinc->costMonoIncreasing(l, r);
    }

    // O(1) -- min +1 increments to make a[l..r] strictly decreasing; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE S costStrictDecreasing(int l, int r) {
        if (l < 0 || l > r || r >= n) throw out_of_range("costStrictDecreasing: needs 0 <= l <= r < n");
        if (!sdec) {
            vector<T> c(n);
            for (int i = 0; i < n; i++) c[n - 1 - i] = arr[i] + T(i);
            sdec = make_unique<Cost>(c);
        }
        return sdec->costMonoIncreasing(n - 1 - r, n - 1 - l);
    }

    // O(1) -- a[l] + ... + a[r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE S rangeSum(int l, int r) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeSum: needs 0 <= l <= r < n");
        return r >= l ? pf[r + 1] - pf[l] : S(0);
    }

    // O(1) -- a[i]; needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE T pointGet(int i) const {
        if (i < 0 || i >= n) throw out_of_range("pointGet: needs 0 <= i < n");
        return arr[i];
    }

    // O(1) -- sum of the whole array a[0..n-1] (rangeSum(0, n - 1)); needs n >= 1, else throws out_of_range
    LEETCODE_NO_SANITIZE auto sumAll() {
        if (n < 1) throw out_of_range("sumAll: needs n >= 1");
        return rangeSum(0, n - 1);
    }

};
