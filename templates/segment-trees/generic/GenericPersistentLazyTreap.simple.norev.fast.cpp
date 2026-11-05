// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/segment-trees/generic/GenericPersistentLazyTreap.simple.norev.fast.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// FAST MODE drawbacks compared with GenericPersistentLazyTreap.simple.norev.cpp:
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


// Every op copies the nodes it changes instead of changing them, so a copy and its original never affect each other.
// copy(l, r) is O(log N) however long a[l..r] is, so lengths can get huge: they are long long.
struct PersistentLazyTreap {
    struct Item {
        Node self, agg; // a[i] alone, and its subtree
        int L = 0, R = 0;
        long long sz = 0;
        bool tagged = false;
        Tag lz; // pending for the children when tagged (self and agg already have it)
    };
    // one pool shared by every PersistentLazyTreap (item 0 = the empty tree); nodes are never freed
    static inline HotVector<Item> nd;
    int root = 0;

    LEETCODE_NO_SANITIZE static unsigned long long rnd() {
        static mt19937_64 g(chrono::steady_clock::now().time_since_epoch().count());
        return g();
    }

    LEETCODE_NO_SANITIZE static int newItem(const RawVal& val) {
        Item it;
        it.self = it.agg = leaf(val);
        it.sz = 1;
        nd.push_back(it);
        return nd.size() - 1;
    }

    LEETCODE_NO_SANITIZE static int clone(int t) {
        Item it = nd[t]; // (a copy first: push_back may move nd)
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

    // t is a copy no other tree sees
    LEETCODE_NO_SANITIZE static void applyTag(int t, const Tag& g) {
        nd[t].self = apply(nd[t].self, g);
        nd[t].agg = apply(nd[t].agg, g);
        if (nd[t].tagged) nd[t].lz = compose(nd[t].lz, g);
        else nd[t].lz = g, nd[t].tagged = true;
    }

    // hands t's pending tag to copies of its children (t is a copy no other tree sees)
    LEETCODE_NO_SANITIZE static void push(int t) {
        if (!nd[t].tagged) return;
        int l = nd[t].L, r = nd[t].R;
        Tag g = nd[t].lz;
        if (l) l = clone(l), applyTag(l, g);
        if (r) r = clone(r), applyTag(r, g);
        nd[t].L = l, nd[t].R = r, nd[t].tagged = false;
    }

    // a = the first k items of t, b = the rest (t itself unchanged)
    LEETCODE_NO_SANITIZE static void splitAt(int t, long long k, int& a, int& b) {
        if (!t) return void(a = b = 0);
        t = clone(t);
        push(t);
        int x, y;
        if (nd[nd[t].L].sz < k) splitAt(nd[t].R, k - nd[nd[t].L].sz - 1, x, y), nd[t].R = x, a = t, b = y;
        else splitAt(nd[t].L, k, x, y), nd[t].L = y, a = x, b = t;
        pull(t);
    }

    // a's items, then b's; the root is a's with probability |a| / (|a| + |b|) (no priorities: a copy can hold the
    // same node many times)
    LEETCODE_NO_SANITIZE static int join(int a, int b) {
        if (!a || !b) return a ? a : b;
        if (rnd() % ((unsigned long long)nd[a].sz + nd[b].sz) < (unsigned long long)nd[a].sz) {
            a = clone(a);
            push(a);
            int x = join(nd[a].R, b);
            nd[a].R = x;
            pull(a);
            return a;
        }
        b = clone(b);
        push(b);
        int x = join(a, nd[b].L);
        nd[b].L = x;
        pull(b);
        return b;
    }

    LEETCODE_NO_SANITIZE static int build(const vector<RawVal>& a, int lo, int hi) {
        if (lo >= hi) return 0;
        int mid = (lo + hi) / 2, t = newItem(a[mid]);
        int l = build(a, lo, mid), r = build(a, mid + 1, hi);
        nd[t].L = l, nd[t].R = r;
        pull(t);
        return t;
    }

    // the Node of items l..r of t, read with a tag (g, or none) pending from above (makes no copies)
    LEETCODE_NO_SANITIZE static Node rq(int t, long long l, long long r, const Tag* g) {
        const Item& x = nd[t];
        if (l <= 0 && r >= x.sz - 1) return g ? apply(x.agg, *g) : x.agg;
        // the children's pending: x's own tag, then the one from above
        Tag both;
        const Tag* cg = g;
        if (x.tagged) cg = g ? &(both = compose(x.lz, *g)) : &x.lz;
        long long ls = nd[x.L].sz;
        Node res;
        bool has = false;
        if (l < ls) res = rq(x.L, l, (r < ls - 1 ? r : ls - 1), cg), has = true;
        if (l <= ls && ls <= r) {
            Node self = g ? apply(x.self, *g) : x.self;
            res = has ? combine(res, self) : self, has = true;
        }
        if (r > ls) {
            Node s = rq(x.R, (l - ls - 1 > 0LL ? l - ls - 1 : 0LL), r - ls - 1, cg);
            res = has ? combine(res, s) : s;
        }
        return res;
    }

    LEETCODE_NO_SANITIZE static int setAt(int t, long long i, const RawVal& val) {
        t = clone(t);
        push(t);
        long long ls = nd[nd[t].L].sz;
        if (i < ls) {
            int c = setAt(nd[t].L, i, val);
            nd[t].L = c;
        } else if (i > ls) {
            int c = setAt(nd[t].R, i - ls - 1, val);
            nd[t].R = c;
        } else {
            nd[t].self = leaf(val);
        }
        pull(t);
        return t;
    }

    LEETCODE_NO_SANITIZE static PersistentLazyTreap wrap(int t) {
        PersistentLazyTreap res;
        res.root = t;
        return res;
    }

    // O(n)
    LEETCODE_NO_SANITIZE PersistentLazyTreap(const vector<RawVal>& a = {}) {
        if (nd.empty()) nd.emplace_back();
        root = build(a, 0, a.size());
    }

    // how many elements
    LEETCODE_NO_SANITIZE long long size() { return nd[root].sz; }

    // the Node of a[i]; needs 0 <= i < size(), else out_of_range
    LEETCODE_NO_SANITIZE Node pointGet(long long i) {
        if (i < 0 || i >= size()) throw out_of_range("pointGet: needs 0 <= i < size()");
        return rq(root, i, i, nullptr);
    }

    // a[i] = val; needs 0 <= i < size(), else out_of_range
    LEETCODE_NO_SANITIZE void pointAssign(long long i, const RawVal& val) {
        if (i < 0 || i >= size()) throw out_of_range("pointAssign: needs 0 <= i < size()");
        root = setAt(root, i, val);
    }

    // insert val so it becomes a[i] (i = size() appends); needs 0 <= i <= size(), else out_of_range
    LEETCODE_NO_SANITIZE void insertAt(long long i, const RawVal& val) {
        if (i < 0 || i > size()) throw out_of_range("insertAt: needs 0 <= i <= size()");
        int a, b;
        splitAt(root, i, a, b);
        root = join(join(a, newItem(val)), b);
    }

    LEETCODE_NO_SANITIZE void append(const RawVal& val) { root = join(root, newItem(val)); }

    // remove a[i]; needs 0 <= i < size(), else out_of_range
    LEETCODE_NO_SANITIZE void eraseAt(long long i) {
        if (i < 0 || i >= size()) throw out_of_range("eraseAt: needs 0 <= i < size()");
        int a, b, c;
        splitAt(root, i, a, b);
        splitAt(b, 1, b, c);
        root = join(a, c);
    }

    // the Node of a[l..r]; needs 0 <= l <= r < size(), else out_of_range
    LEETCODE_NO_SANITIZE Node rangeQuery(long long l, long long r) {
        if (l < 0 || r >= size() || l > r) throw out_of_range("rangeQuery: needs 0 <= l <= r < size()");
        return rq(root, l, r, nullptr);
    }

    // the Node of the whole array; needs size() >= 1, else out_of_range
    LEETCODE_NO_SANITIZE Node rangeQueryAll() {
        if (!root) throw out_of_range("rangeQueryAll: needs size() >= 1");
        return nd[root].agg;
    }

    // tag applied to every element of a[l..r]; needs 0 <= l <= r < size(), else out_of_range
    LEETCODE_NO_SANITIZE void rangeUpdate(long long l, long long r, const Tag& tag) {
        if (l < 0 || r >= size() || l > r) throw out_of_range("rangeUpdate: needs 0 <= l <= r < size()");
        int a, b, c;
        splitAt(root, l, a, b);
        splitAt(b, r - l + 1, b, c);
        applyTag(b, tag); // (b is a fresh copy: splitAt copies every node it returns)
        root = join(join(a, b), c);
    }

    // cyclic shift a[l..r] left by k (a[l+k] moves to l; any k, taken mod r - l + 1); needs 0 <= l <= r < size(), else
    // out_of_range
    LEETCODE_NO_SANITIZE void rangeRotateLeft(long long l, long long r, long long k) {
        if (l < 0 || r >= size() || l > r) throw out_of_range("rangeRotateLeft: needs 0 <= l <= r < size()");
        long long len = r - l + 1;
        int a, b, c, b1, b2;
        k = ((k % len) + len) % len;
        splitAt(root, l, a, b);
        splitAt(b, len, b, c);
        splitAt(b, k, b1, b2);
        root = join(join(a, join(b2, b1)), c);
    }

    // cyclic shift a[l..r] right by k (a[r-k+1..r] move to the front; any k, taken mod r - l + 1); needs
    // 0 <= l <= r < size(), else out_of_range
    LEETCODE_NO_SANITIZE void rangeRotateRight(long long l, long long r, long long k) {
        if (l < 0 || r >= size() || l > r) throw out_of_range("rangeRotateRight: needs 0 <= l <= r < size()");
        rangeRotateLeft(l, r, -(k % (r - l + 1)));
    }

    // the whole array as a PersistentLazyTreap of its own, O(1) (this one is unchanged)
    LEETCODE_NO_SANITIZE PersistentLazyTreap copy() { return wrap(root); }

    // a[l..r] as a PersistentLazyTreap of its own, O(log N) however long (this one is unchanged); needs
    // 0 <= l <= r < size(), else out_of_range
    LEETCODE_NO_SANITIZE PersistentLazyTreap copy(long long l, long long r) {
        if (l < 0 || r >= size() || l > r) throw out_of_range("copy: needs 0 <= l <= r < size()");
        int a, b, c;
        splitAt(root, l, a, b);
        splitAt(b, r - l + 1, b, c);
        return wrap(b);
    }

    // remove a[l..r] and get it back as a PersistentLazyTreap of its own; needs 0 <= l <= r < size(), else out_of_range
    LEETCODE_NO_SANITIZE PersistentLazyTreap cut(long long l, long long r) {
        if (l < 0 || r >= size() || l > r) throw out_of_range("cut: needs 0 <= l <= r < size()");
        int a, b, c;
        splitAt(root, l, a, b);
        splitAt(b, r - l + 1, b, c);
        root = join(a, c);
        return wrap(b);
    }

    // insert all of other so it starts at a[i] (other ends up empty); needs 0 <= i <= size(), else out_of_range
    LEETCODE_NO_SANITIZE void paste(long long i, PersistentLazyTreap& other) {
        if (i < 0 || i > size()) throw out_of_range("paste: needs 0 <= i <= size()");
        int a, b;
        splitAt(root, i, a, b);
        root = join(join(a, other.root), b);
        other.root = 0;
    }
    LEETCODE_NO_SANITIZE void paste(long long i, PersistentLazyTreap&& other) { paste(i, other); }

    // append all of other (other ends up empty)
    LEETCODE_NO_SANITIZE void merge(PersistentLazyTreap& other) {
        root = join(root, other.root);
        other.root = 0;
    }
    LEETCODE_NO_SANITIZE void merge(PersistentLazyTreap&& other) { merge(other); }

    // split into a[0..k-1] and a[k..] (this one ends up empty); needs 0 <= k <= size(), else out_of_range
    LEETCODE_NO_SANITIZE pair<PersistentLazyTreap, PersistentLazyTreap> split(long long k) {
        if (k < 0 || k > size()) throw out_of_range("split: needs 0 <= k <= size()");
        int a, b;
        splitAt(root, k, a, b);
        root = 0;
        return {wrap(a), wrap(b)};
    }

    // split into a[0..l-1], a[l..r], a[r+1..] (this one ends up empty); needs 0 <= l <= r < size(), else out_of_range
    LEETCODE_NO_SANITIZE tuple<PersistentLazyTreap, PersistentLazyTreap, PersistentLazyTreap> trisect(long long l, long long r) {
        if (l < 0 || r >= size() || l > r) throw out_of_range("trisect: needs 0 <= l <= r < size()");
        int a, b, c;
        splitAt(root, l, a, b);
        splitAt(b, r - l + 1, b, c);
        root = 0;
        return {wrap(a), wrap(b), wrap(c)};
    }
};
