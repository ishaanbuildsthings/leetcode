// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/pointGet-rangeMex/fast.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: pointGet rangeMex
// @data-structure-type: persistent
// @complexities:
//   pointGet: 1
//   rangeMex: log(N)
//   build: N*log(N)
// @memory:
//   layout: none
//   node: ML[1*N*log(N)] MR[1*N*log(N)] MN[1*N*log(N)]
//   tags: none
//   other: root[1*N] arr[1*N]
//   note: persistent seg tree over the values 0..N+1; version p holds each value's last index before p, and the mex of a[l..r] is the first value whose last index is < l

// Static array; rangeMex(l, r) = smallest integer >= 0 not in a[l..r] (0-indexed, inclusive), online.
// rangeMex: a persistent seg tree over the values 0..N+1; version p holds, per value, its last index before p (-1 if
// none). The mex of a[l..r] is the first value whose last index in version r + 1 is < l.
// T: int, long long, ...
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
struct PersistentMex {
    int n;
    HotVector<T> arr;
    HotVector<int> root;
    struct MexNode {  // a node's fields side by side: a walk reads them together (faster than one array per field)
        int ML = 0;
        int MR = 0;
        int MN = -1;
    };
    HotVector<MexNode> mnd;  // node 0 = the empty tree

    // O(N log N) -- arr: the initial array, 0-indexed
    explicit PersistentMex(const vector<T>& a) : n((int)a.size()), arr(a) { buildMex(); }

    // O(1) -- a[i]; needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE T pointGet(int i) const {
        if (i < 0 || i >= n) throw out_of_range("pointGet: needs 0 <= i < n");
        return arr[i];
    }

    // O(logN) -- smallest integer >= 0 that is not in a[l..r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE int rangeMex(int l, int r) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeMex: needs 0 <= l <= r < n");
        return mexFrom(l, r, 0);
    }

    // persistent seg tree over the values 0..n+1: version p holds, per value, its last index before p (-1: none)
    LEETCODE_NO_SANITIZE void buildMex() {
        mnd.assign(1, MexNode{});  // node 0 = the empty tree (every last index -1)
        root.assign(n + 1, 0);
        for (int i = 0; i < n; i++)
            root[i + 1] = T(0) <= arr[i] && arr[i] <= T(n + 1) ? mexSet(root[i], 0, n + 1, int(arr[i]), i) : root[i];
    }

    // copy of node with value v's last index set to i
    LEETCODE_NO_SANITIZE int mexSet(int node, int nl, int nh, int v, int i) {
        int l = mnd[node].ML, r = mnd[node].MR, x;
        if (nl == nh) x = i;
        else {
            int mid = (nl + nh) >> 1;
            if (v <= mid) l = mexSet(l, nl, mid, v, i);
            else r = mexSet(r, mid + 1, nh, v, i);
            x = min(mnd[l].MN, mnd[r].MN);
        }
        MexNode n;
        n.ML = nl == nh ? 0 : l, n.MR = nl == nh ? 0 : r, n.MN = x;
        mnd.push_back(n);
        return (int)mnd.size() - 1;
    }

    // smallest value >= s that is not in a[l..r]: the leftmost value >= s whose last index (as of r) is < l
    LEETCODE_NO_SANITIZE int mexFrom(int l, int r, int s) const {
        auto go = [&](auto&& self, int t, int nl, int nh) -> int {
            if (nh < s || mnd[t].MN >= l) return -1;  // nothing allowed here, or every value here is in a[l..r]
            if (!t) return max(nl, s);            // no value here was ever seen
            if (nl == nh) return nl;
            int mid = (nl + nh) >> 1, res = self(self, mnd[t].ML, nl, mid);
            return res >= 0 ? res : self(self, mnd[t].MR, mid + 1, nh);
        };
        return go(go, root[r + 1], 0, n + 1);
    }
};
