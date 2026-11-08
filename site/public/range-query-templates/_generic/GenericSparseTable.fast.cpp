// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/generic-seg-trees/GenericSparseTable.fast.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// FAST MODE drawbacks compared with GenericSparseTable.cpp:
//   - sanitizers are skipped in this template and in what you fill in, so a bad access in it goes unreported
// Same public operations and answers, same limits; it needs GCC or Clang and C++17.

// LEETCODE_NO_SANITIZE skips sanitizers in a function. It only changes anything where sanitizers run, like LeetCode: on
// Codeforces it compiles and does nothing.
// This template already uses it. To go further, put it on the one function with your hot loop:
//   LEETCODE_NO_SANITIZE long long maxSum(vector<int>& nums, int k) {
// A lambda needs its own: [&](int x) LEETCODE_NO_SANITIZE { ... }. It does not carry into anything that function calls.
// Bad memory accesses in a marked function go unreported.
#ifndef LEETCODE_NO_SANITIZE
#define LEETCODE_NO_SANITIZE __attribute__((no_sanitize("address"), no_sanitize("undefined")))
#endif
#define LEETCODE_NO_SANITIZE_INLINE LEETCODE_NO_SANITIZE __attribute__((always_inline)) inline

// Any helper these functions call needs LEETCODE_NO_SANITIZE too, and so does a Node or Tag constructor.

// e.g. long long, char, pair, struct, ...
using RawVal = long long;

struct Node {
    // long long mn;
    // long long mx;
};

LEETCODE_NO_SANITIZE Node baseFn(const RawVal& v, int i) {
    // Node res;
    // res.mn = v, res.mx = v;
    // return res;
}

// combine MUST be idempotent: combine(x, x) == x (min, max, gcd, lcm, AND, OR, ... but NOT sum or count)
LEETCODE_NO_SANITIZE Node combine(const Node& left, const Node& right) {
    // Node res;
    // res.mn = min(left.mn, right.mn);
    // res.mx = max(left.mx, right.mx);
    // return res;
}

// A static array (no updates): O(N log N) build, O(1) rangeQuery (one combine call), O(N log N) Nodes of memory
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


struct SparseTable {
    int n, levels;
    HotVector<Node> t; // t[j * n + i]: the Node of a[i..i + 2^j - 1], for every i with i + 2^j <= n

    LEETCODE_NO_SANITIZE SparseTable(const vector<RawVal>& a) : n(a.size()), levels(n ? 32 - __builtin_clz(n) : 0) {
        t.resize((size_t)levels * n);
        for (int i = 0; i < n; i++) t[i] = baseFn(a[i], i);
        for (int j = 1; j < levels; j++)
            for (int i = 0; i + (1 << j) <= n; i++) t[j * n + i] = combine(t[(j - 1) * n + i], t[(j - 1) * n + i + (1 << (j - 1))]);
    }

    // how many elements
    LEETCODE_NO_SANITIZE int size() { return n; }

    // the Node of a[i]; needs 0 <= i < n, else out_of_range
    LEETCODE_NO_SANITIZE Node pointGet(int i) {
        if (i < 0 || i >= n) throw out_of_range("pointGet: needs 0 <= i < n");
        return t[i];
    }

    // the Node of a[l..r]: the combine of the two largest power-of-two blocks starting at l and ending at r (they
    // overlap, which is why combine must be idempotent); needs 0 <= l <= r < n, else out_of_range
    LEETCODE_NO_SANITIZE Node rangeQuery(int l, int r) {
        if (l < 0 || r >= n || l > r) throw out_of_range("rangeQuery: needs 0 <= l <= r < n");
        int j = 31 - __builtin_clz(r - l + 1);
        if (l + (1 << j) - 1 == r) return t[j * n + l];
        return combine(t[j * n + l], t[j * n + r - (1 << j) + 1]);
    }

    // the Node of the whole array; needs n >= 1, else out_of_range
    LEETCODE_NO_SANITIZE Node rangeQueryAll() {
        if (n == 0) throw out_of_range("rangeQueryAll: needs n >= 1");
        return rangeQuery(0, n - 1);
    }
};
