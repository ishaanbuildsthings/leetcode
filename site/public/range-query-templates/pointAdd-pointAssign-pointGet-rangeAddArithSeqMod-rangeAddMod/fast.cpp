// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/pointAdd-pointAssign-pointGet-rangeAddArithSeqMod-rangeAddMod/fast.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: getAll pointAdd pointAssign pointGet rangeAddArithSeqMod rangeAddMod
// @data-structure-type: BIT
// @complexities:
//   getAll: N
//   pointAdd: log(N)
//   pointAssign: log(N)
//   pointGet: log(N)
//   rangeAddArithSeqMod: log(N)
//   rangeAddMod: log(N)
//   build: N
// @memory:
//   layout: none
//   node: c[1*N] s[1*N]
//   tags: none
//   other: none
//   note: two Fenwick trees over differences, everything % MOD; a[i] = prefix(c, i) + i * prefix(s, i)

// Range add of an arithmetic sequence % MOD, point get. 0-based, inclusive. T: int, long long, ...
// Values are kept in [0, mod).
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
struct ArithSeqBITMod {
    using W = conditional_t<sizeof(T) <= 4, long long, __int128>;  // wide enough for a product of two residues
    int n;
    T mod;
    HotVector<T> c, s;  // a[i] = prefix(c, i) + i * prefix(s, i)  (% MOD)

    LEETCODE_NO_SANITIZE T norm(W x) const { x %= mod; return T(x < 0 ? x + mod : x); }

    // O(N)
    explicit ArithSeqBITMod(const vector<T>& a, T mod = 1000000007) : n((int)a.size()), mod(mod), c(n + 1), s(n + 1) {
        T prev = 0;
        for (int i = 1; i <= n; i++) {
            T v = norm(a[i - 1]);
            c[i] = norm(W(c[i]) + v - prev);
            prev = v;
            int j = i + (i & -i);
            if (j <= n) c[j] = norm(W(c[j]) + c[i]);
        }
    }

    LEETCODE_NO_SANITIZE void add(int i, T k, T step) {
        for (i++; i <= n; i += i & -i) c[i] = norm(W(c[i]) + k), s[i] = norm(W(s[i]) + step);
    }

    // O(logN) -- a[l + j] += start + j * step (% MOD) for j in [0, r - l]; needs 0 <= l <= r < n, else throws
    // out_of_range
    LEETCODE_NO_SANITIZE void rangeAddArithSeqMod(int l, int r, T start, T step) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeAddArithSeqMod: needs 0 <= l <= r < n");
        T st = norm(step), k = norm(W(start) - W(l) * st);
        add(l, k, st);
        if (r + 1 < n) add(r + 1, norm(-W(k)), norm(-W(st)));
    }

    // O(logN) -- a[i] += v (% MOD) for i in [l, r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void rangeAddMod(int l, int r, T v) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeAddMod: needs 0 <= l <= r < n");
        T x = norm(v), y = norm(-W(x));
        for (int i = l + 1; i <= n; i += i & -i) c[i] = norm(W(c[i]) + x);
        for (int i = r + 2; i <= n; i += i & -i) c[i] = norm(W(c[i]) + y);
    }

    // O(logN) -- a[i], in [0, mod); needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE T pointGet(int i) const {
        if (i < 0 || i >= n) throw out_of_range("pointGet: needs 0 <= i < n");
        W k = 0, coef = 0;
        for (int j = i + 1; j > 0; j &= j - 1) k += c[j], coef += s[j];
        return norm(k % mod + W(i) * (coef % mod));
    }

    // O(N) -- the whole array: undo the Fenwick sums on a copy (last index first: entry i was added into
    // i + lowbit(i) once complete), then one pass of running prefix sums
    LEETCODE_NO_SANITIZE vector<T> getAll() const {
        vector<T> C(c), D(s), out(n);
        for (int i = n; i > 0; i--) {
            int j = i + (i & -i);
            if (j <= n) C[j] = norm(W(C[j]) - C[i]), D[j] = norm(W(D[j]) - D[i]);
        }
        T k = 0, coef = 0;
        for (int i = 0; i < n; i++) {
            k = norm(W(k) + C[i + 1]), coef = norm(W(coef) + D[i + 1]);
            out[i] = norm(W(k) + W(i) * coef);
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
