// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/generic-seg-trees/GenericDynamicSeg.fast.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// FAST MODE drawbacks compared with GenericDynamicSeg.cpp:
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
    // long long tot;
    // long long mn;
};

LEETCODE_NO_SANITIZE Node leaf(const RawVal& v, long long i) {
    // Node res;
    // res.tot = v, res.mn = v;
    // return res;
}

LEETCODE_NO_SANITIZE Node combine(const Node& left, const Node& right) {
    // Node res;
    // res.tot = left.tot + right.tot;
    // res.mn = min(left.mn, right.mn);
    // return res;
}

// the Node of lo..hi where nothing was ever set (every element the starting value, e.g. 0)
LEETCODE_NO_SANITIZE Node blank(long long lo, long long hi) {
    // Node res;
    // res.tot = 0, res.mn = 0;
    // return res;
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
    LEETCODE_NO_SANITIZE_INLINE typename vector<U>::const_reference operator[](size_t i) const { return this->_M_impl._M_start[i]; }
    LEETCODE_NO_SANITIZE_INLINE size_t size() const { return size_t(this->_M_impl._M_finish - this->_M_impl._M_start); }
#endif
};


struct DynamicSeg {
    long long lo, hi;
    HotVector<Node> t;
    HotVector<int> L, R; // children; 0 = never touched, every element there still the starting value
    int root;

    // indices lo..hi (e.g. 0..1e18, negative is fine), every element starting as blank says; needs lo <= hi
    LEETCODE_NO_SANITIZE DynamicSeg(long long lo, long long hi) : lo(lo), hi(hi) {
        if (lo > hi) throw out_of_range("DynamicSeg: needs lo <= hi");
        t.push_back(Node()), L.push_back(0), R.push_back(0);
        root = make(lo, hi);
    }

    LEETCODE_NO_SANITIZE int make(long long nl, long long nr) {
        t.push_back(blank(nl, nr)), L.push_back(0), R.push_back(0);
        return t.size() - 1;
    }

    LEETCODE_NO_SANITIZE Node at(int k, long long nl, long long nr) { return k ? t[k] : blank(nl, nr); }

    LEETCODE_NO_SANITIZE static long long mid(long long nl, long long nr) { return nl + (nr - nl) / 2; }

    LEETCODE_NO_SANITIZE void setRec(int k, long long nl, long long nr, long long i, const RawVal& v) {
        if (nl == nr) return void(t[k] = leaf(v, i));
        long long m = mid(nl, nr);
        if (i <= m) {
            if (!L[k]) { int c = make(nl, m); L[k] = c; }
            setRec(L[k], nl, m, i, v);
        } else {
            if (!R[k]) { int c = make(m + 1, nr); R[k] = c; }
            setRec(R[k], m + 1, nr, i, v);
        }
        t[k] = combine(at(L[k], nl, m), at(R[k], m + 1, nr));
    }

    LEETCODE_NO_SANITIZE Node queryRec(int k, long long nl, long long nr, long long l, long long r) {
        if (l <= nl && nr <= r) return at(k, nl, nr);
        if (!k) return blank((l > nl ? l : nl), (r < nr ? r : nr));
        long long m = mid(nl, nr);
        if (r <= m) return queryRec(L[k], nl, m, l, r);
        if (l > m) return queryRec(R[k], m + 1, nr, l, r);
        return combine(queryRec(L[k], nl, m, l, r), queryRec(R[k], m + 1, nr, l, r));
    }

    // a[i] = val; needs lo <= i <= hi, else out_of_range
    LEETCODE_NO_SANITIZE void pointAssign(long long i, const RawVal& val) {
        if (i < lo || i > hi) throw out_of_range("pointAssign: needs lo <= i <= hi");
        setRec(root, lo, hi, i, val);
    }

    // the Node of a[i]; needs lo <= i <= hi, else out_of_range
    LEETCODE_NO_SANITIZE Node pointGet(long long i) {
        if (i < lo || i > hi) throw out_of_range("pointGet: needs lo <= i <= hi");
        return queryRec(root, lo, hi, i, i);
    }

    // the Node of a[l..r]; needs lo <= l <= r <= hi, else out_of_range
    LEETCODE_NO_SANITIZE Node rangeQuery(long long l, long long r) {
        if (l < lo || r > hi || l > r) throw out_of_range("rangeQuery: needs lo <= l <= r <= hi");
        return queryRec(root, lo, hi, l, r);
    }

    // the Node of the whole array
    LEETCODE_NO_SANITIZE Node rangeQueryAll() { return t[root]; }
};
