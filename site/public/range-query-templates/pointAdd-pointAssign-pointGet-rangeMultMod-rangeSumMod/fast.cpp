// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/pointAdd-pointAssign-pointGet-rangeMultMod-rangeSumMod/fast.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: getAll pointAdd pointAssign pointGet rangeMultMod rangeSumMod
// @data-structure-type: lazy-seg-tree
// @complexities:
//   getAll: N
//   pointAdd: log(N)
//   pointAssign: log(N)
//   pointGet: log(N)
//   rangeMultMod: log(N)
//   rangeSumMod: log(N)
//   build: N
// @memory:
//   layout: 2n-iterative
//   node: tot[2*N]
//   tags: mul[1*N]
//   other: none
//   note: tags live on the N internal nodes only; each is a pending multiplier (% MOD)

// Range multiply + range sum, all % MOD, plus point ops. All indices 0-based, ranges inclusive [l, r].
// One tag per internal node: a pending multiplier ("applied here, not yet pushed"). Multipliers compose by
// multiplying, and v -> v * m turns a node's sum into sum * m. Leaner than the affine tree: one tag instead of two.
// Values are residues in [0, mod). T: int, long long, ...
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
#ifdef __GLIBCXX__
    LEETCODE_NO_SANITIZE_INLINE typename vector<U>::reference operator[](size_t i) { return this->_M_impl._M_start[i]; }
    LEETCODE_NO_SANITIZE_INLINE typename vector<U>::const_reference operator[](size_t i) const { return this->_M_impl._M_start[i]; }
    LEETCODE_NO_SANITIZE_INLINE size_t size() const { return size_t(this->_M_impl._M_finish - this->_M_impl._M_start); }
#endif
};

template <typename T>
struct MultSumTree {
    using W = conditional_t<sizeof(T) <= 4, long long, __int128>;  // wide enough for a product of two residues
    int n, h;
    T mod;
    HotVector<T> tot;  // 2N: leaves are tot[n..2n)
    HotVector<T> mul;  // N: tags on internal nodes

    LEETCODE_NO_SANITIZE T norm(W x) const { x %= mod; return T(x < 0 ? x + mod : x); }

    // O(N)
    explicit MultSumTree(const vector<T>& a, T mod = 1000000007)
        : n((int)a.size()), h(a.empty() ? 0 : 32 - __builtin_clz((unsigned)a.size())), mod(mod), tot(2 * a.size()) {
        for (int i = 0; i < n; i++) tot[n + i] = norm(a[i]);
        for (int x = n - 1; x > 0; x--) tot[x] = norm(W(tot[2 * x]) + tot[2 * x + 1]);
        mul.assign(n, 1);
    }

    // v -> v * m on node x (k is unused: a product doesn't care how many slots the node covers)
    LEETCODE_NO_SANITIZE void apply(int x, int, T m) {
        tot[x] = norm(W(tot[x]) * m);
        if (x < n) mul[x] = norm(W(mul[x]) * m);
    }

    // push every tag on the root-to-leaf path of leaf p down one level
    LEETCODE_NO_SANITIZE void push(int p) {
        for (int s = h; s > 0; s--) {
            int x = p >> s, k = 1 << (s - 1);
            if (mul[x] != 1) apply(2 * x, k, mul[x]), apply(2 * x + 1, k, mul[x]), mul[x] = 1;
        }
    }

    // recompute the ancestors of leaf p; each keeps the effect of its own pending tag
    LEETCODE_NO_SANITIZE void rebuild(int p) {
        for (int k = 2; p > 1; k <<= 1) {
            p >>= 1;
            tot[p] = norm((W(tot[2 * p]) + tot[2 * p + 1]) * mul[p]);
        }
    }

    LEETCODE_NO_SANITIZE void update(int l, int r, T m) {
        if (l > r) return;
        int l0 = l + n, r0 = r + n;
        push(l0), push(r0);
        for (int i = l0, j = r0 + 1, k = 1; i < j; i >>= 1, j >>= 1, k <<= 1) {
            if (i & 1) apply(i++, k, m);
            if (j & 1) apply(--j, k, m);
        }
        rebuild(l0), rebuild(r0);
    }

    // O(logN) -- (a[l] + ... + a[r]) % MOD; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE T rangeSumMod(int l, int r) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeSumMod: needs 0 <= l <= r < n");
        if (l > r) return 0;
        l += n, r += n;
        push(l), push(r);
        W res = 0;
        for (r++; l < r; l >>= 1, r >>= 1) {
            if (l & 1) res += tot[l++];
            if (r & 1) res += tot[--r];
        }
        return norm(res);
    }

    // O(logN) -- a[i], in [0, mod); needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE T pointGet(int i) {
        if (i < 0 || i >= n) throw out_of_range("pointGet: needs 0 <= i < n");
        push(i + n);
        return tot[i + n];
    }

    // O(N) -- the whole array: push every tag down one level at a time from the root (the nodes s levels above
    // the leaves are (n >> s) .. ((2n - 1) >> s); their children cover k = 1 << (s - 1) leaves), then read the leaves
    LEETCODE_NO_SANITIZE vector<T> getAll() {
        for (int s = h; s > 0; s--) {
            int k = 1 << (s - 1);
            for (int x = max(1, n >> s); x <= (2 * n - 1) >> s; x++)
                if (mul[x] != 1) apply(2 * x, k, mul[x]), apply(2 * x + 1, k, mul[x]), mul[x] = 1;
        }
        return vector<T>(tot.begin() + n, tot.end());
    }

    // O(logN) -- a[i] *= m (% MOD) for i in [l, r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void rangeMultMod(int l, int r, T m) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeMultMod: needs 0 <= l <= r < n");
        update(l, r, norm(m));
    }

    // O(logN) -- a[i] = v (% MOD); needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAssign(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointAssign: needs 0 <= i < n");
        int p = i + n;
        push(p);
        tot[p] = norm(v);
        rebuild(p);
    }

    // O(logN) -- a[i] += delta (% MOD); needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAdd(int i, T delta) {
        if (i < 0 || i >= n) throw out_of_range("pointAdd: needs 0 <= i < n");
        pointAssign(i, norm(W(pointGet(i)) + delta));
    }
};
