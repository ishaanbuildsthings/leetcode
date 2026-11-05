// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/segment-trees/generic/GenericLazySeg.complex.fast.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// FAST MODE drawbacks compared with GenericLazySeg.complex.cpp:
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

// LEETCODE_NO_SANITIZE stays on every function you fill in below. It does not carry into what a function calls, so
// anything they call needs it too:
//   LEETCODE_NO_SANITIZE long long addMod(long long a, long long b) { ... }  // a helper of yours
//   LEETCODE_NO_SANITIZE Node() { ... }                                      // a Node or Tag constructor

// e.g. long long, char, pair, struct, ...
using RawVal = char;

struct Node {
    // int cnt[26];  // how many of each letter
    // int len;
    // LEETCODE_NO_SANITIZE Node() {  // can make an empty constructor which runs every time a Node is made
    //     for (int c = 0; c < 26; c++) cnt[c] = 0;  // (the other fields are always set before they're read)
    // }
};

// We never need to worry about initializing empty tags or anything, these tags come in via rangeUpdate(l, r, tag) calls
// or when pushed down from parents
struct Tag {
    // bool assign;  // every element becomes letter, if set
    // char letter;
    // int shift;  // then every letter moves this many places on, z wrapping to a (0..25; 0 = none)
};

LEETCODE_NO_SANITIZE Node leaf(const RawVal& v, int i) {
    // Node res;
    // res.cnt[v - 'a'] = 1;
    // res.len = 1;
    // return res;
}

LEETCODE_NO_SANITIZE Node combine(const Node& left, const Node& right) {
    // Node res;
    // for (int c = 0; c < 26; c++) res.cnt[c] = left.cnt[c] + right.cnt[c];
    // res.len = left.len + right.len;
    // return res;
}

// return a new node: this node after tag is applied to it
// this function is never called with a tag that never existed, but tags can have things like pending false values or
// pending no-ops (for instance two lazy bools canceling) and we still need to check for this and no-op (could just
// return original node)
LEETCODE_NO_SANITIZE Node apply(Node node, const Tag& tag) {
    // This is NOT mutating since node is taken by value in the arg, we can also just make a new node if needed
    // if (tag.assign) {
    //     for (int c = 0; c < 26; c++) node.cnt[c] = 0;
    //     node.cnt[tag.letter - 'a'] = node.len;
    // }
    // if (tag.shift) {
    //     rotate(node.cnt, node.cnt + 26 - tag.shift, node.cnt + 26);  // (letter c's count moves to c + shift)
    // }
    // return node;
}

// a tag that is the old tag, then the new tag
LEETCODE_NO_SANITIZE Tag compose(Tag old, const Tag& newer) {
    // This is NOT mutating since old is taken by value in the arg, we can also just make a new tag if needed
    // if (newer.assign) return newer;  // (a later assign wipes out everything before it)
    // old.shift = (old.shift + newer.shift) % 26;  // (shifts add up, still after old's assign if it had one)
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


struct LazySeg {
    int n, cap, lg;
    HotVector<Node> t;
    HotVector<Tag> lz;
    // has[k]: node k covers at least one real leaf; tagged[k]: lz[k] is pending for node k's children
    HotVector<char> has, tagged;

    LEETCODE_NO_SANITIZE LazySeg(const vector<RawVal>& a) : n(a.size()), cap(1), lg(0) {
        while (cap < n) cap *= 2, lg++;
        t.assign(2 * cap, Node());
        lz.assign(cap, Tag());
        has.assign(2 * cap, 0);
        tagged.assign(cap, 0);
        for (int i = 0; i < n; i++) t[cap + i] = leaf(a[i], i), has[cap + i] = 1;
        for (int k = cap - 1; k >= 1; k--) pull(k);
    }

    LEETCODE_NO_SANITIZE void pull(int k) {
        // the padding is a suffix, so a node with an empty right child is just its left child
        has[k] = has[2 * k];
        if (has[2 * k + 1]) t[k] = combine(t[2 * k], t[2 * k + 1]);
        else if (has[2 * k]) t[k] = t[2 * k];
    }

    LEETCODE_NO_SANITIZE void applyAt(int k, const Tag& tag) {
        if (!has[k]) return;
        t[k] = apply(t[k], tag);
        if (k < cap) {
            if (tagged[k]) lz[k] = compose(lz[k], tag);
            else lz[k] = tag, tagged[k] = 1;
        }
    }

    LEETCODE_NO_SANITIZE void push(int k) {
        if (!tagged[k]) return;
        applyAt(2 * k, lz[k]);
        applyAt(2 * k + 1, lz[k]);
        tagged[k] = 0;
    }

    // pushes the tags above the leaf range [l, r) (l and r already offset by cap)
    LEETCODE_NO_SANITIZE void pushAbove(int l, int r) {
        for (int i = lg; i >= 1; i--) {
            if (((l >> i) << i) != l) push(l >> i);
            if (((r >> i) << i) != r) push((r - 1) >> i);
        }
    }

    // how many elements
    LEETCODE_NO_SANITIZE int size() { return n; }

    // the Node of a[i]; needs 0 <= i < n, else out_of_range
    LEETCODE_NO_SANITIZE Node pointGet(int i) {
        if (i < 0 || i >= n) throw out_of_range("pointGet: needs 0 <= i < n");
        int k = cap + i;
        for (int j = lg; j >= 1; j--) push(k >> j);
        return t[k];
    }

    // a[i] = val; needs 0 <= i < n, else out_of_range
    LEETCODE_NO_SANITIZE void pointAssign(int i, const RawVal& val) {
        if (i < 0 || i >= n) throw out_of_range("pointAssign: needs 0 <= i < n");
        int k = cap + i;
        for (int j = lg; j >= 1; j--) push(k >> j);
        t[k] = leaf(val, i);
        for (int j = 1; j <= lg; j++) pull(k >> j);
    }

    // the Node of a[l..r]; needs 0 <= l <= r < n, else out_of_range
    LEETCODE_NO_SANITIZE Node rangeQuery(int l, int r) {
        if (l < 0 || r >= n || l > r) throw out_of_range("rangeQuery: needs 0 <= l <= r < n");
        l += cap, r += cap + 1;
        pushAbove(l, r);
        Node sl, sr;
        bool hl = false, hr = false;
        for (; l < r; l >>= 1, r >>= 1) {
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

    // tag applied to every element of a[l..r]; needs 0 <= l <= r < n, else out_of_range
    LEETCODE_NO_SANITIZE void rangeUpdate(int l, int r, const Tag& tag) {
        if (l < 0 || r >= n || l > r) throw out_of_range("rangeUpdate: needs 0 <= l <= r < n");
        l += cap, r += cap + 1;
        pushAbove(l, r);
        for (int a = l, b = r; a < b; a >>= 1, b >>= 1) {
            if (a & 1) applyAt(a++, tag);
            if (b & 1) applyAt(--b, tag);
        }
        for (int i = 1; i <= lg; i++) {
            if (((l >> i) << i) != l) pull(l >> i);
            if (((r >> i) << i) != r) pull((r - 1) >> i);
        }
    }
};
