// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/generic-seg-trees/GenericLazyDynamicSeg.fast.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// FAST MODE drawbacks compared with GenericLazyDynamicSeg.cpp:
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
    // long long len;
};

// a pending update to every element of a segment
// We never need to worry about initializing empty tags or anything, these tags come in via rangeUpdate(l, r, tag) calls
// or when pushed down from parents
struct Tag {
    // long long add;
};

LEETCODE_NO_SANITIZE Node leaf(const RawVal& v, long long i) {
    // Node res;
    // res.tot = v, res.mn = v, res.len = 1;
    // return res;
}

LEETCODE_NO_SANITIZE Node combine(const Node& left, const Node& right) {
    // Node res;
    // res.tot = left.tot + right.tot, res.mn = min(left.mn, right.mn);
    // res.len = left.len + right.len;
    // return res;
}

// the Node of lo..hi where nothing was ever set (every element the starting value, e.g. 0)
LEETCODE_NO_SANITIZE Node blank(long long lo, long long hi) {
    // Node res;
    // res.tot = 0, res.mn = 0, res.len = hi - lo + 1;
    // return res;
}

// return a new node: this node after tag is applied to it
// this function is never called with a tag that never existed, but tags can have things like pending false values or
// pending no-ops (for instance two lazy bools canceling) and we still need to check for this and no-op (could just
// return original node)
LEETCODE_NO_SANITIZE Node apply(Node node, const Tag& tag) {
    // This is NOT mutating since node is taken by value in the arg, we can also just make a new node if needed
    // node.tot += tag.add * node.len, node.mn += tag.add;
    // return node;
}

// a tag that is the old tag, then the new tag
LEETCODE_NO_SANITIZE Tag compose(Tag old, const Tag& newer) {
    // This is NOT mutating since old is taken by value in the arg, we can also just make a new tag if needed
    // old.add += newer.add;
    // return old;
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


struct LazyDynamicSeg {
    long long lo, hi;
    HotVector<Node> t;
    HotVector<int> L, R; // children; 0 = never touched, every element there still the starting value
    HotVector<Tag> lz;
    HotVector<char> tagged; // tagged[k]: lz[k] is pending for node k's children
    int root;

    // indices lo..hi (e.g. 0..1e18, negative is fine), every element starting as blank says; needs lo <= hi
    LEETCODE_NO_SANITIZE LazyDynamicSeg(long long lo, long long hi) : lo(lo), hi(hi) {
        if (lo > hi) throw out_of_range("LazyDynamicSeg: needs lo <= hi");
        t.push_back(Node()), L.push_back(0), R.push_back(0), lz.push_back(Tag()), tagged.push_back(0);
        root = make(lo, hi);
    }

    LEETCODE_NO_SANITIZE int make(long long nl, long long nr) {
        t.push_back(blank(nl, nr)), L.push_back(0), R.push_back(0), lz.push_back(Tag()), tagged.push_back(0);
        return t.size() - 1;
    }

    LEETCODE_NO_SANITIZE void applyAt(int k, const Tag& tag) {
        t[k] = apply(t[k], tag);
        if (tagged[k]) lz[k] = compose(lz[k], tag);
        else lz[k] = tag, tagged[k] = 1;
    }

    // hands node k's pending tag to its children (making them if they were never touched)
    LEETCODE_NO_SANITIZE void push(int k, long long nl, long long nr) {
        if (!tagged[k]) return;
        long long m = mid(nl, nr);
        if (!L[k]) { int c = make(nl, m); L[k] = c; }
        if (!R[k]) { int c = make(m + 1, nr); R[k] = c; }
        Tag g = lz[k];
        applyAt(L[k], g), applyAt(R[k], g);
        tagged[k] = 0;
    }

    LEETCODE_NO_SANITIZE void pull(int k, long long nl, long long nr) {
        long long m = mid(nl, nr);
        t[k] = combine(at(L[k], nl, m), at(R[k], m + 1, nr));
    }

    LEETCODE_NO_SANITIZE void updateRec(int k, long long nl, long long nr, long long l, long long r, const Tag& tag) {
        if (l <= nl && nr <= r) return applyAt(k, tag);
        push(k, nl, nr);
        long long m = mid(nl, nr);
        if (l <= m) {
            if (!L[k]) { int c = make(nl, m); L[k] = c; }
            updateRec(L[k], nl, m, l, r, tag);
        }
        if (r > m) {
            if (!R[k]) { int c = make(m + 1, nr); R[k] = c; }
            updateRec(R[k], m + 1, nr, l, r, tag);
        }
        pull(k, nl, nr);
    }

    LEETCODE_NO_SANITIZE Node at(int k, long long nl, long long nr) { return k ? t[k] : blank(nl, nr); }

    LEETCODE_NO_SANITIZE static long long mid(long long nl, long long nr) { return nl + (nr - nl) / 2; }

    LEETCODE_NO_SANITIZE void setRec(int k, long long nl, long long nr, long long i, const RawVal& v) {
        if (nl == nr) return void(t[k] = leaf(v, i));
        push(k, nl, nr);
        long long m = mid(nl, nr);
        if (i <= m) {
            if (!L[k]) { int c = make(nl, m); L[k] = c; }
            setRec(L[k], nl, m, i, v);
        } else {
            if (!R[k]) { int c = make(m + 1, nr); R[k] = c; }
            setRec(R[k], m + 1, nr, i, v);
        }
        pull(k, nl, nr);
    }

    LEETCODE_NO_SANITIZE Node queryRec(int k, long long nl, long long nr, long long l, long long r) {
        if (l <= nl && nr <= r) return at(k, nl, nr);
        if (!k) return blank((l > nl ? l : nl), (r < nr ? r : nr));
        push(k, nl, nr);
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

    // tag applied to every element of a[l..r]; needs lo <= l <= r <= hi, else out_of_range
    LEETCODE_NO_SANITIZE void rangeUpdate(long long l, long long r, const Tag& tag) {
        if (l < lo || r > hi || l > r) throw out_of_range("rangeUpdate: needs lo <= l <= r <= hi");
        updateRec(root, lo, hi, l, r, tag);
    }
};
