// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAssign-rangeMin-rangeSum/letters-fast.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: getAll pointAssign pointChmax pointChmin pointGet rangeAssign rangeMin
// @data-structure-type: lazy-seg-tree
// @complexities:
//   getAll: N
//   pointAssign: log(N)
//   pointChmax: log(N)
//   pointChmin: log(N)
//   pointGet: log(N)
//   rangeAssign: log(N)
//   rangeMin: log(N)
//   build: N
// @memory:
//   layout: 2n-iterative
//   node: sm[2*N] mn[2*N]
//   tags: asg[1*N] hasAsg[1*N]
//   other: none
//   note: tags live on the N internal nodes only; each holds a pending assign

// Letters version: the values are characters (Python: a list of characters, e.g. list(s); C++: T = char), and only the
// operations that make sense on characters are listed.
// Range assign with range sum / min queries, plus point ops. All indices 0-based, ranges inclusive [l, r].
// Iterative 2N lazy tree: values on the leaves, and on each internal node a pending assign, meaning "applied here, not
// yet pushed to my children". An update pushes the tags on its two boundary paths, tags the covering nodes, then
// rebuilds the two paths. A covering node at level s is a perfect subtree of 2^s leaves, so its length is 1 << s.
// T: int, long long, ...; sums are kept in S (long long for small T).
// FAST MODE drawbacks compared with letters.cpp:
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
struct AssignSumMinTree {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    static constexpr T INF = numeric_limits<T>::max(), NEG = numeric_limits<T>::lowest();
    int n, h;
    HotVector<S> sm;  // 2N: leaves are sm[n..2n)
    HotVector<T> mn;
    HotVector<T> asg;  // N: tags on internal nodes
    HotVector<char> hasAsg;

    // O(N)
    explicit AssignSumMinTree(const vector<T>& a) : n((int)a.size()), h(a.empty() ? 0 : 32 - __builtin_clz((unsigned)a.size())) {
        sm.assign(2 * n, 0);
        mn.assign(2 * n, INF);
        for (int i = 0; i < n; i++) {
            sm[n + i] = a[i];
            mn[n + i] = a[i];
        }
        for (int x = n - 1; x > 0; x--) {
            sm[x] = sm[2 * x] + sm[2 * x + 1];
            mn[x] = std::min(mn[2 * x], mn[2 * x + 1]);
        }
        asg.assign(n, 0), hasAsg.assign(n, 0);
    }

    // set every slot of node x (k slots) to v
    LEETCODE_NO_SANITIZE void applyAssign(int x, int k, T v) {
        sm[x] = S(v) * k;
        mn[x] = v;
        if (x < n) hasAsg[x] = 1, asg[x] = v;
    }

    // push every tag on the root-to-leaf path of leaf p down one level
    LEETCODE_NO_SANITIZE void push(int p) {
        for (int s = h; s > 0; s--) {
            int x = p >> s, k = 1 << (s - 1);
            if (hasAsg[x]) applyAssign(2 * x, k, asg[x]), applyAssign(2 * x + 1, k, asg[x]), hasAsg[x] = 0;
        }
    }

    // recompute the ancestors of leaf p; each keeps the effect of its own pending tag
    LEETCODE_NO_SANITIZE void rebuild(int p) {
        for (int k = 2; p > 1; k <<= 1) {
            p >>= 1;
            if (hasAsg[p]) {
                sm[p] = S(asg[p]) * k;
                mn[p] = asg[p];
                continue;
            }
            sm[p] = sm[2 * p] + sm[2 * p + 1];
            mn[p] = std::min(mn[2 * p], mn[2 * p + 1]);
        }
    }

    // O(logN) -- a[i] = v for i in [l, r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void rangeAssign(int l, int r, T v) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeAssign: needs 0 <= l <= r < n");
        if (l > r) return;
        int l0 = l + n, r0 = r + n;
        push(l0), push(r0);
        for (int i = l0, j = r0 + 1, k = 1; i < j; i >>= 1, j >>= 1, k <<= 1) {
            if (i & 1) applyAssign(i++, k, v);
            if (j & 1) applyAssign(--j, k, v);
        }
        rebuild(l0), rebuild(r0);
    }

    // O(logN) -- a[l] + ... + a[r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE S rangeSum(int l, int r) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeSum: needs 0 <= l <= r < n");
        if (l > r) return 0;
        l += n, r += n;
        push(l), push(r);
        S res = 0;
        for (r++; l < r; l >>= 1, r >>= 1) {
            if (l & 1) res += sm[l++];
            if (r & 1) res += sm[--r];
        }
        return res;
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

    // O(N) -- the whole array: push every tag down one level at a time from the root (the nodes s levels above
    // the leaves are (n >> s) .. ((2n - 1) >> s); their children cover k = 1 << (s - 1) leaves), then read the leaves
    LEETCODE_NO_SANITIZE vector<T> getAll() {
        for (int s = h; s > 0; s--) {
            int k = 1 << (s - 1);
            for (int x = max(1, n >> s); x <= (2 * n - 1) >> s; x++) {
                if (hasAsg[x]) applyAssign(2 * x, k, asg[x]), applyAssign(2 * x + 1, k, asg[x]), hasAsg[x] = 0;
            }
        }
        return vector<T>(sm.begin() + n, sm.end());
    }

    // O(logN) -- a[i]; needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE T pointGet(int i) {
        if (i < 0 || i >= n) throw out_of_range("pointGet: needs 0 <= i < n");
        push(i + n);
        return T(sm[i + n]);
    }

    // O(logN) -- a[i] = v; needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAssign(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointAssign: needs 0 <= i < n");
        int p = i + n;
        push(p);
        sm[p] = v;
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
};
