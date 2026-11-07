// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/pointAdd-pointAssign-pointGet-rangeAddMod-rangeSumMod/fast.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: getAll pointAdd pointAssign pointGet rangeAddMod rangeSumMod
// @data-structure-type: BIT
// @complexities:
//   getAll: N
//   pointAdd: log(N)
//   pointAssign: log(N)
//   pointGet: log(N)
//   rangeAddMod: log(N)
//   rangeSumMod: log(N)
//   build: N
// @memory:
//   layout: none
//   node: b1[1*N] b2[1*N]
//   tags: none
//   other: none
//   note: two Fenwick trees over the difference array d (d[i] = a[i] - a[i-1]): b1 over d[i], b2 over d[i] * i, all % MOD

// Range add + range sum, everything % MOD, with two Fenwick trees and no lazy tags. All indices 0-based, ranges
// inclusive [l, r]. a[0] + ... + a[x] = (x + 1) * sum(d[0..x]) - sum(d[i] * i for i in 0..x), d the difference array.
// Values are residues in [0, mod). T: int, long long, ...; products go through W (wide enough for two residues).
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
struct RangeAddSumBITMod {
    using W = conditional_t<sizeof(T) <= 4, long long, __int128>;
    int n;
    T mod;
    HotVector<T> b1, b2;  // 1-indexed

    LEETCODE_NO_SANITIZE T norm(W x) const { x %= mod; return T(x < 0 ? x + mod : x); }

    // O(N)
    explicit RangeAddSumBITMod(const vector<T>& a, T mod = 1000000007) : n((int)a.size()), mod(mod), b1(n + 1), b2(n + 1) {
        T prev = 0;
        for (int i = 0; i < n; i++) {
            T v = norm(a[i]), d = norm(W(v) - prev);
            prev = v;
            b1[i + 1] = d, b2[i + 1] = norm(W(d) * i);
        }
        for (int i = 1; i <= n; i++) {
            int j = i + (i & -i);
            if (j <= n) b1[j] = norm(W(b1[j]) + b1[i]), b2[j] = norm(W(b2[j]) + b2[i]);
        }
    }

    LEETCODE_NO_SANITIZE void addDiff(int i, T d) {
        d = norm(d);
        T di = norm(W(d) * i);
        for (i++; i <= n; i += i & -i) b1[i] = norm(W(b1[i]) + d), b2[i] = norm(W(b2[i]) + di);
    }

    // O(logN) -- (a[0] + ... + a[x]) % MOD (0 for x = -1)
    LEETCODE_NO_SANITIZE T prefix(int x) const {
        W s1 = 0, s2 = 0;
        for (int i = x + 1; i > 0; i &= i - 1) s1 += b1[i], s2 += b2[i];
        return norm(W(norm(s1)) * (x + 1) - norm(s2));
    }

    // O(logN) -- a[i] += v (% MOD) for i in [l, r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void rangeAddMod(int l, int r, T v) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeAddMod: needs 0 <= l <= r < n");
        if (l > r) return;
        addDiff(l, v);
        if (r + 1 < n) addDiff(r + 1, norm(-W(v)));
    }

    // O(logN) -- (a[l] + ... + a[r]) % MOD; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE T rangeSumMod(int l, int r) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeSumMod: needs 0 <= l <= r < n");
        return l <= r ? norm(W(prefix(r)) - prefix(l - 1)) : T(0);
    }

    // O(logN) -- a[i], in [0, mod); needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE T pointGet(int i) const {
        if (i < 0 || i >= n) throw out_of_range("pointGet: needs 0 <= i < n");
        return rangeSumMod(i, i);
    }

    // O(N) -- the whole array: undo the Fenwick sums on a copy (last index first: entry i was added into
    // i + lowbit(i) once complete), then one pass of running prefix sums
    LEETCODE_NO_SANITIZE vector<T> getAll() const {
        vector<T> B1(b1), B2(b2);
        for (int i = n; i > 0; i--) {
            int j = i + (i & -i);
            if (j <= n) B1[j] = norm(W(B1[j]) - B1[i]), B2[j] = norm(W(B2[j]) - B2[i]);
        }
        vector<T> out(n);
        T s1 = 0, s2 = 0, prev = 0;
        for (int x = 0; x < n; x++) {
            s1 = norm(W(s1) + B1[x + 1]), s2 = norm(W(s2) + B2[x + 1]);
            T p = norm(W(s1) * (x + 1) - s2);
            out[x] = norm(W(p) - prev), prev = p;
        }
        return out;
    }

    // O(logN) -- a[i] += delta (% MOD); needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAdd(int i, T delta) {
        if (i < 0 || i >= n) throw out_of_range("pointAdd: needs 0 <= i < n");
        rangeAddMod(i, i, delta);
    }

    // O(logN) -- a[i] = v (% MOD); needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAssign(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointAssign: needs 0 <= i < n");
        rangeAddMod(i, i, norm(W(v) - pointGet(i)));
    }
};
