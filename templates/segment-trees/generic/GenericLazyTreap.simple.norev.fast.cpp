// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/segment-trees/generic/GenericLazyTreap.simple.norev.fast.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// FAST MODE drawbacks compared with GenericLazyTreap.simple.norev.cpp:
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

// a pending update to every element of a segment: here add this much
// We never need to worry about initializing empty tags or anything, these tags come in via rangeUpdate(l, r, tag) calls
// or when pushed down from parents
using Tag = long long;

LEETCODE_NO_SANITIZE Node leaf(const RawVal& v) {
    // return v;
}

LEETCODE_NO_SANITIZE Node combine(const Node& left, const Node& right) {
    // return max(left, right);
}

// return a new node: this node after tag is applied to it
// this function is never called with a tag that never existed, but tags can have things like pending false values or
// pending no-ops (for instance two lazy bools canceling) and we still need to check for this and no-op (could just
// return original node)
LEETCODE_NO_SANITIZE Node apply(Node node, const Tag& tag) {
    // return node + tag;  // (adding to every element raises the max by as much)
}

// a tag that is the old tag, then the new tag
LEETCODE_NO_SANITIZE Tag compose(Tag old, const Tag& newer) {
    // return old + newer;
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


struct LazyTreap {
    struct Item {
        Node self, agg; // a[i] alone, and its subtree
        int L = 0, R = 0, sz = 0;
        unsigned long long pr = 0;
        bool tagged = false;
        Tag lz; // pending for the children when tagged
    };
    // one pool shared by every LazyTreap, so cut / paste move nodes between them (item 0 = the empty tree)
    static inline HotVector<Item> nd;
    int root = 0;

    LEETCODE_NO_SANITIZE static unsigned long long rnd() {
        static mt19937_64 g(chrono::steady_clock::now().time_since_epoch().count());
        return g();
    }

    LEETCODE_NO_SANITIZE static int newItem(const RawVal& v) {
        Item it;
        it.self = it.agg = leaf(v);
        it.sz = 1, it.pr = rnd();
        nd.push_back(it);
        return nd.size() - 1;
    }

    LEETCODE_NO_SANITIZE static void pull(int t) {
        Item& x = nd[t];
        x.sz = 1 + nd[x.L].sz + nd[x.R].sz;
        x.agg = x.self;
        if (x.L) x.agg = combine(nd[x.L].agg, x.agg);
        if (x.R) x.agg = combine(x.agg, nd[x.R].agg);
    }

    LEETCODE_NO_SANITIZE static void applyTag(int t, const Tag& g) {
        if (!t) return;
        nd[t].self = apply(nd[t].self, g);
        nd[t].agg = apply(nd[t].agg, g);
        if (nd[t].tagged) nd[t].lz = compose(nd[t].lz, g);
        else nd[t].lz = g, nd[t].tagged = true;
    }

    LEETCODE_NO_SANITIZE static void push(int t) {
        if (nd[t].tagged) applyTag(nd[t].L, nd[t].lz), applyTag(nd[t].R, nd[t].lz), nd[t].tagged = false;
    }

    // a = the first k items of t, b = the rest
    LEETCODE_NO_SANITIZE static void splitAt(int t, int k, int& a, int& b) {
        if (!t) return void(a = b = 0);
        push(t);
        if (nd[nd[t].L].sz < k) splitAt(nd[t].R, k - nd[nd[t].L].sz - 1, nd[t].R, b), a = t;
        else splitAt(nd[t].L, k, a, nd[t].L), b = t;
        pull(t);
    }

    LEETCODE_NO_SANITIZE static int join(int a, int b) {
        if (!a || !b) return a ? a : b;
        if (nd[a].pr > nd[b].pr) {
            push(a);
            nd[a].R = join(nd[a].R, b);
            pull(a);
            return a;
        }
        push(b);
        nd[b].L = join(a, nd[b].L);
        pull(b);
        return b;
    }

    // the Node of items l..r of t: walks down and combines the pieces that cover them (no split / merge)
    LEETCODE_NO_SANITIZE static Node rq(int t, int l, int r) {
        if (l <= 0 && r >= nd[t].sz - 1) return nd[t].agg;
        push(t);
        int ls = nd[nd[t].L].sz;
        if (r < ls) return rq(nd[t].L, l, r);
        if (l > ls) return rq(nd[t].R, l - ls - 1, r - ls - 1);
        Node res = nd[t].self;
        if (l < ls) res = combine(rq(nd[t].L, l, ls - 1), res);
        if (r > ls) res = combine(res, rq(nd[t].R, 0, r - ls - 1));
        return res;
    }

    // a[i] = val in t's subtree, recomputing the nodes on the way back up
    LEETCODE_NO_SANITIZE static void setAt(int t, int i, const RawVal& val) {
        push(t);
        int ls = nd[nd[t].L].sz;
        if (i < ls) setAt(nd[t].L, i, val);
        else if (i > ls) setAt(nd[t].R, i - ls - 1, val);
        else nd[t].self = leaf(val);
        pull(t);
    }

    // tag applied to items l..r of t: tags the subtrees that cover them (no split / merge)
    LEETCODE_NO_SANITIZE static void updateRange(int t, int l, int r, const Tag& tag) {
        if (!t || r < 0 || l >= nd[t].sz) return;
        if (l <= 0 && r >= nd[t].sz - 1) return applyTag(t, tag);
        push(t);
        int ls = nd[nd[t].L].sz;
        updateRange(nd[t].L, l, r, tag);
        if (l <= ls && ls <= r) nd[t].self = apply(nd[t].self, tag);
        updateRange(nd[t].R, l - ls - 1, r - ls - 1, tag);
        pull(t);
    }

    // O(n)
    LEETCODE_NO_SANITIZE LazyTreap(const vector<RawVal>& a = {}) {
        if (nd.empty()) nd.emplace_back();
        vector<int> st, order;
        for (const RawVal& v : a) {
            int x = newItem(v), last = 0;
            while (!st.empty() && nd[st.back()].pr < nd[x].pr) last = st.back(), st.pop_back();
            nd[x].L = last;
            if (!st.empty()) nd[st.back()].R = x;
            st.push_back(x);
        }
        root = st.empty() ? 0 : st[0];
        // pull children before parents: the reverse of a preorder
        if (root) order.push_back(root);
        for (size_t i = 0; i < order.size(); i++) {
            if (nd[order[i]].L) order.push_back(nd[order[i]].L);
            if (nd[order[i]].R) order.push_back(nd[order[i]].R);
        }
        for (int i = order.size() - 1; i >= 0; i--) pull(order[i]);
    }

    LEETCODE_NO_SANITIZE static LazyTreap wrap(int t) {
        LazyTreap res;
        res.root = t;
        return res;
    }

    // how many elements
    LEETCODE_NO_SANITIZE int size() { return nd[root].sz; }

    // the Node of a[i]; needs 0 <= i < size(), else out_of_range
    LEETCODE_NO_SANITIZE Node pointGet(int i) {
        if (i < 0 || i >= size()) throw out_of_range("pointGet: needs 0 <= i < size()");
        int t = root;
        while (true) {
            push(t);
            int ls = nd[nd[t].L].sz;
            if (i < ls) t = nd[t].L;
            else if (i == ls) return nd[t].self;
            else i -= ls + 1, t = nd[t].R;
        }
    }

    // a[i] = val; needs 0 <= i < size(), else out_of_range
    LEETCODE_NO_SANITIZE void pointAssign(int i, const RawVal& val) {
        if (i < 0 || i >= size()) throw out_of_range("pointAssign: needs 0 <= i < size()");
        setAt(root, i, val);
    }

    // insert val so it becomes a[i] (i = size() appends); needs 0 <= i <= size(), else out_of_range
    LEETCODE_NO_SANITIZE void insertAt(int i, const RawVal& val) {
        if (i < 0 || i > size()) throw out_of_range("insertAt: needs 0 <= i <= size()");
        int a, b;
        splitAt(root, i, a, b);
        root = join(join(a, newItem(val)), b);
    }

    LEETCODE_NO_SANITIZE void append(const RawVal& val) { root = join(root, newItem(val)); }

    // remove a[i]; needs 0 <= i < size(), else out_of_range
    LEETCODE_NO_SANITIZE void eraseAt(int i) {
        if (i < 0 || i >= size()) throw out_of_range("eraseAt: needs 0 <= i < size()");
        int a, b, c;
        splitAt(root, i, a, b);
        splitAt(b, 1, b, c);
        root = join(a, c);
    }

    // the Node of a[l..r]; needs 0 <= l <= r < size(), else out_of_range
    LEETCODE_NO_SANITIZE Node rangeQuery(int l, int r) {
        if (l < 0 || r >= size() || l > r) throw out_of_range("rangeQuery: needs 0 <= l <= r < size()");
        return rq(root, l, r);
    }

    // the Node of the whole array; needs size() >= 1, else out_of_range
    LEETCODE_NO_SANITIZE Node rangeQueryAll() {
        if (!root) throw out_of_range("rangeQueryAll: needs size() >= 1");
        return nd[root].agg;
    }

    // tag applied to every element of a[l..r]; needs 0 <= l <= r < size(), else out_of_range
    LEETCODE_NO_SANITIZE void rangeUpdate(int l, int r, const Tag& tag) {
        if (l < 0 || r >= size() || l > r) throw out_of_range("rangeUpdate: needs 0 <= l <= r < size()");
        updateRange(root, l, r, tag);
    }

    // remove a[l..r] and get it back as a LazyTreap of its own; needs 0 <= l <= r < size(), else out_of_range
    LEETCODE_NO_SANITIZE LazyTreap cut(int l, int r) {
        if (l < 0 || r >= size() || l > r) throw out_of_range("cut: needs 0 <= l <= r < size()");
        int a, b, c;
        splitAt(root, l, a, b);
        splitAt(b, r - l + 1, b, c);
        root = join(a, c);
        return wrap(b);
    }

    // insert all of other so it starts at a[i] (other ends up empty); needs 0 <= i <= size(), else out_of_range
    LEETCODE_NO_SANITIZE void paste(int i, LazyTreap& other) {
        if (i < 0 || i > size()) throw out_of_range("paste: needs 0 <= i <= size()");
        int a, b;
        splitAt(root, i, a, b);
        root = join(join(a, other.root), b);
        other.root = 0;
    }
    LEETCODE_NO_SANITIZE void paste(int i, LazyTreap&& other) { paste(i, other); }

    // append all of other (other ends up empty)
    LEETCODE_NO_SANITIZE void merge(LazyTreap& other) {
        root = join(root, other.root);
        other.root = 0;
    }
    LEETCODE_NO_SANITIZE void merge(LazyTreap&& other) { merge(other); }

    // split into a[0..k-1] and a[k..] (this one ends up empty); needs 0 <= k <= size(), else out_of_range
    LEETCODE_NO_SANITIZE pair<LazyTreap, LazyTreap> split(int k) {
        if (k < 0 || k > size()) throw out_of_range("split: needs 0 <= k <= size()");
        int a, b;
        splitAt(root, k, a, b);
        root = 0;
        return {wrap(a), wrap(b)};
    }

    // split into a[0..l-1], a[l..r], a[r+1..] (this one ends up empty); needs 0 <= l <= r < size(), else out_of_range
    LEETCODE_NO_SANITIZE tuple<LazyTreap, LazyTreap, LazyTreap> trisect(int l, int r) {
        if (l < 0 || r >= size() || l > r) throw out_of_range("trisect: needs 0 <= l <= r < size()");
        int a, b, c;
        splitAt(root, l, a, b);
        splitAt(b, r - l + 1, b, c);
        root = 0;
        return {wrap(a), wrap(b), wrap(c)};
    }

    // cyclic shift a[l..r] left by k (a[l+k] moves to l; any k, taken mod r - l + 1); needs 0 <= l <= r < size(), else
    // out_of_range
    LEETCODE_NO_SANITIZE void rangeRotateLeft(int l, int r, long long k) {
        if (l < 0 || r >= size() || l > r) throw out_of_range("rangeRotateLeft: needs 0 <= l <= r < size()");
        int len = r - l + 1, a, b, c, b1, b2;
        k = ((k % len) + len) % len;
        splitAt(root, l, a, b);
        splitAt(b, len, b, c);
        splitAt(b, k, b1, b2);
        root = join(join(a, join(b2, b1)), c);
    }

    // cyclic shift a[l..r] right by k (a[r-k+1..r] move to the front; any k, taken mod r - l + 1); needs
    // 0 <= l <= r < size(), else out_of_range
    LEETCODE_NO_SANITIZE void rangeRotateRight(int l, int r, long long k) {
        if (l < 0 || r >= size() || l > r) throw out_of_range("rangeRotateRight: needs 0 <= l <= r < size()");
        rangeRotateLeft(l, r, -k);
    }
};
