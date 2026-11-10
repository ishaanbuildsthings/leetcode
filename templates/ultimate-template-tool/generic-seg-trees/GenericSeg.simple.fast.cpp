// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/generic-seg-trees/GenericSeg.simple.fast.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// FAST MODE drawbacks compared with GenericSeg.simple.cpp:
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

// e.g. long long, char, ...
using RawVal = long long;

// a plain type: here the max of the segment
using Node = long long;

LEETCODE_NO_SANITIZE Node leaf(const RawVal& v, int i) {
    // return v;
}

LEETCODE_NO_SANITIZE Node combine(const Node& left, const Node& right) {
    // return max(left, right);
}

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


struct Seg {
    int n, cap;
    HotVector<Node> t;
    HotVector<char> has; // has[k]: node k covers at least one real leaf (the padding past n has none)

    LEETCODE_NO_SANITIZE Seg(const vector<RawVal>& a) : n(a.size()), cap(1) {
        while (cap < n) cap *= 2;
        t.assign(2 * cap, Node());
        has.assign(2 * cap, 0);
        for (int i = 0; i < n; i++) t[cap + i] = leaf(a[i], i), has[cap + i] = 1;
        for (int k = cap - 1; k >= 1; k--) pull(k);
    }

    LEETCODE_NO_SANITIZE void pull(int k) {
        // the padding is a suffix, so a node with an empty right child is just its left child
        has[k] = has[2 * k];
        if (has[2 * k + 1]) t[k] = combine(t[2 * k], t[2 * k + 1]);
        else if (has[2 * k]) t[k] = t[2 * k];
    }

    // how many elements
    LEETCODE_NO_SANITIZE int size() { return n; }

    // the Node of a[i]; needs 0 <= i < n, else out_of_range
    LEETCODE_NO_SANITIZE Node pointGet(int i) {
        if (i < 0 || i >= n) throw out_of_range("pointGet: needs 0 <= i < n");
        return t[cap + i];
    }

    // a[i] = val; needs 0 <= i < n, else out_of_range
    LEETCODE_NO_SANITIZE void pointAssign(int i, const RawVal& val) {
        if (i < 0 || i >= n) throw out_of_range("pointAssign: needs 0 <= i < n");
        int k = cap + i;
        t[k] = leaf(val, i);
        for (k >>= 1; k >= 1; k >>= 1) pull(k);
    }

    // the Node of a[l..r]; needs 0 <= l <= r < n, else out_of_range
    LEETCODE_NO_SANITIZE Node rangeQuery(int l, int r) {
        if (l < 0 || r >= n || l > r) throw out_of_range("rangeQuery: needs 0 <= l <= r < n");
        Node sl, sr;
        bool hl = false, hr = false;
        for (l += cap, r += cap + 1; l < r; l >>= 1, r >>= 1) {
            if (l & 1) sl = hl ? combine(sl, t[l]) : t[l], hl = true, l++;
            if (r & 1) --r, sr = hr ? combine(t[r], sr) : t[r], hr = true;
        }
        if (!hl) return sr;
        if (!hr) return sl;
        return combine(sl, sr);
    }

    // the Node of the whole array; needs n >= 1, else out_of_range
    LEETCODE_NO_SANITIZE Node rangeQueryAll() {
        if (n == 0) throw out_of_range("rangeQueryAll: needs n >= 1");
        return t[1];
    }
};
