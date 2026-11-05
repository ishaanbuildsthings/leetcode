// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/pointAdd-pointAssign-pointGet-rangeAddMod-rangeAffineMod-rangeAssignMod-rangeMultMod-rangeSumMod/fast.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: getAll pointAdd pointAssign pointGet rangeAddMod rangeAffineMod rangeAssignMod rangeMultMod rangeSumMod
// @data-structure-type: lazy-seg-tree
// @complexities:
//   getAll: N
//   pointAdd: log(N)
//   pointAssign: log(N)
//   pointGet: log(N)
//   rangeAddMod: log(N)
//   rangeAffineMod: log(N)
//   rangeAssignMod: log(N)
//   rangeMultMod: log(N)
//   rangeSumMod: log(N)
//   build: N
// @memory:
//   layout: 2n-iterative
//   node: tot[2*N]
//   tags: mul[1*N] add[1*N]
//   other: none
//   note: tags live on the N internal nodes only; each is one affine map x -> x*mul + add (% MOD)

// Range affine (a[i] = a[i] * mult + add), add, mult, assign, and range sum, all % MOD, plus point ops.
// All indices 0-based, ranges inclusive [l, r]. Every update is one affine tag (mult, add):
//   add x -> (1, x)   mult m -> (m, 0)   assign x -> (0, x)
// Composing f = (m1, a1) then g = (m2, a2) gives (m1 * m2, a1 * m2 + a2): the OLD add is scaled by the NEW mult.
// Iterative 2N lazy tree: values on the leaves, a tag on each internal node ("applied here, not yet pushed"). A
// covering node at level s is a perfect subtree of 2^s leaves, so v -> v * m + a turns its sum into sum * m + a * 2^s.
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
struct AffineSumTree {
    using W = conditional_t<sizeof(T) <= 4, long long, __int128>;  // wide enough for a product of two residues
    int n, h;
    T mod;
    HotVector<T> tot;  // 2N: leaves are tot[n..2n)
    HotVector<T> mul, add;  // N: tags on internal nodes

    LEETCODE_NO_SANITIZE T norm(W x) const { x %= mod; return T(x < 0 ? x + mod : x); }

    // O(N)
    explicit AffineSumTree(const vector<T>& a, T mod = 1000000007)
        : n((int)a.size()), h(a.empty() ? 0 : 32 - __builtin_clz((unsigned)a.size())), mod(mod), tot(2 * a.size()) {
        for (int i = 0; i < n; i++) tot[n + i] = norm(a[i]);
        for (int x = n - 1; x > 0; x--) tot[x] = norm(W(tot[2 * x]) + tot[2 * x + 1]);
        mul.assign(n, 1), add.assign(n, 0);
    }

    // v -> v * m + a on node x, which covers k slots
    LEETCODE_NO_SANITIZE void apply(int x, int k, T m, T a) {
        tot[x] = norm(W(tot[x]) * m + W(a) * k % mod);
        if (x < n) mul[x] = norm(W(mul[x]) * m), add[x] = norm(W(add[x]) * m + a);
    }

    // push every tag on the root-to-leaf path of leaf p down one level
    LEETCODE_NO_SANITIZE void push(int p) {
        for (int s = h; s > 0; s--) {
            int x = p >> s, k = 1 << (s - 1);
            if (mul[x] != 1 || add[x]) apply(2 * x, k, mul[x], add[x]), apply(2 * x + 1, k, mul[x], add[x]), mul[x] = 1, add[x] = 0;
        }
    }

    // recompute the ancestors of leaf p; each keeps the effect of its own pending tag
    LEETCODE_NO_SANITIZE void rebuild(int p) {
        for (int k = 2; p > 1; k <<= 1) {
            p >>= 1;
            tot[p] = norm((W(tot[2 * p]) + tot[2 * p + 1]) * mul[p] + W(add[p]) * k % mod);
        }
    }

    LEETCODE_NO_SANITIZE void update(int l, int r, T m, T a) {
        if (l > r) return;
        int l0 = l + n, r0 = r + n;
        push(l0), push(r0);
        for (int i = l0, j = r0 + 1, k = 1; i < j; i >>= 1, j >>= 1, k <<= 1) {
            if (i & 1) apply(i++, k, m, a);
            if (j & 1) apply(--j, k, m, a);
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
                if (mul[x] != 1 || add[x]) apply(2 * x, k, mul[x], add[x]), apply(2 * x + 1, k, mul[x], add[x]), mul[x] = 1, add[x] = 0;
        }
        return vector<T>(tot.begin() + n, tot.end());
    }

    // O(logN) -- a[i] = a[i] * mult + add (% MOD) for i in [l, r]; every other update is this one; needs
    // 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void rangeAffineMod(int l, int r, T mult, T add) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeAffineMod: needs 0 <= l <= r < n");
        update(l, r, norm(mult), norm(add));
    }

    // O(logN) -- a[i] += v (% MOD) for i in [l, r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void rangeAddMod(int l, int r, T v) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeAddMod: needs 0 <= l <= r < n");
        update(l, r, 1, norm(v));
    }

    // O(logN) -- a[i] *= m (% MOD) for i in [l, r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void rangeMultMod(int l, int r, T m) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeMultMod: needs 0 <= l <= r < n");
        update(l, r, norm(m), 0);
    }

    // O(logN) -- a[i] = v for i in [l, r]: multiply by 0, then add v; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void rangeAssignMod(int l, int r, T v) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeAssignMod: needs 0 <= l <= r < n");
        update(l, r, 0, norm(v));
    }

    // O(logN) -- a[i] = v (% MOD); needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAssign(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointAssign: needs 0 <= i < n");
        update(i, i, 0, norm(v));
    }

    // O(logN) -- a[i] += delta (% MOD); needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAdd(int i, T delta) {
        if (i < 0 || i >= n) throw out_of_range("pointAdd: needs 0 <= i < n");
        update(i, i, 1, norm(delta));
    }
};
