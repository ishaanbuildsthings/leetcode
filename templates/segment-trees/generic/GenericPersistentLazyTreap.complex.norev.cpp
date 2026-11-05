// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/segment-trees/generic/GenericPersistentLazyTreap.complex.norev.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// e.g. long long, char, pair, struct, ...
using RawVal = char;

struct Node {
    // int cnt[26];  // how many of each letter
    // int len;
    // Node() {  // can make an empty constructor which runs every time a Node is made
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

Node leaf(const RawVal& v) {
    // Node res;
    // res.cnt[v - 'a'] = 1;
    // res.len = 1;
    // return res;
}

Node combine(const Node& left, const Node& right) {
    // Node res;
    // for (int c = 0; c < 26; c++) res.cnt[c] = left.cnt[c] + right.cnt[c];
    // res.len = left.len + right.len;
    // return res;
}

// return a new node: this node after tag is applied to it
// this function is never called with a tag that never existed, but tags can have things like pending false values or
// pending no-ops (for instance two lazy bools canceling) and we still need to check for this and no-op (could just
// return original node)
Node apply(Node node, const Tag& tag) {
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
Tag compose(Tag old, const Tag& newer) {
    // This is NOT mutating since old is taken by value in the arg, we can also just make a new tag if needed
    // if (newer.assign) return newer;  // (a later assign wipes out everything before it)
    // old.shift = (old.shift + newer.shift) % 26;  // (shifts add up, still after old's assign if it had one)
    // return old;
}

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
    static inline vector<Item> nd;
    int root = 0;

    static unsigned long long rnd() {
        static mt19937_64 g(chrono::steady_clock::now().time_since_epoch().count());
        return g();
    }

    static int newItem(const RawVal& val) {
        Item it;
        it.self = it.agg = leaf(val);
        it.sz = 1;
        nd.push_back(it);
        return nd.size() - 1;
    }

    static int clone(int t) {
        Item it = nd[t]; // (a copy first: push_back may move nd)
        nd.push_back(it);
        return nd.size() - 1;
    }

    static void pull(int t) {
        Item& x = nd[t];
        x.sz = 1 + nd[x.L].sz + nd[x.R].sz;
        x.agg = x.self;
        if (x.L) x.agg = combine(nd[x.L].agg, x.agg);
        if (x.R) x.agg = combine(x.agg, nd[x.R].agg);
    }

    // t is a copy no other tree sees
    static void applyTag(int t, const Tag& g) {
        nd[t].self = apply(nd[t].self, g);
        nd[t].agg = apply(nd[t].agg, g);
        if (nd[t].tagged) nd[t].lz = compose(nd[t].lz, g);
        else nd[t].lz = g, nd[t].tagged = true;
    }

    // hands t's pending tag to copies of its children (t is a copy no other tree sees)
    static void push(int t) {
        if (!nd[t].tagged) return;
        int l = nd[t].L, r = nd[t].R;
        Tag g = nd[t].lz;
        if (l) l = clone(l), applyTag(l, g);
        if (r) r = clone(r), applyTag(r, g);
        nd[t].L = l, nd[t].R = r, nd[t].tagged = false;
    }

    // a = the first k items of t, b = the rest (t itself unchanged)
    static void splitAt(int t, long long k, int& a, int& b) {
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
    static int join(int a, int b) {
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

    static int build(const vector<RawVal>& a, int lo, int hi) {
        if (lo >= hi) return 0;
        int mid = (lo + hi) / 2, t = newItem(a[mid]);
        int l = build(a, lo, mid), r = build(a, mid + 1, hi);
        nd[t].L = l, nd[t].R = r;
        pull(t);
        return t;
    }

    // the Node of items l..r of t, read with a tag (g, or none) pending from above (makes no copies)
    static Node rq(int t, long long l, long long r, const Tag* g) {
        const Item& x = nd[t];
        if (l <= 0 && r >= x.sz - 1) return g ? apply(x.agg, *g) : x.agg;
        // the children's pending: x's own tag, then the one from above
        Tag both;
        const Tag* cg = g;
        if (x.tagged) cg = g ? &(both = compose(x.lz, *g)) : &x.lz;
        long long ls = nd[x.L].sz;
        Node res;
        bool has = false;
        if (l < ls) res = rq(x.L, l, min(r, ls - 1), cg), has = true;
        if (l <= ls && ls <= r) {
            Node self = g ? apply(x.self, *g) : x.self;
            res = has ? combine(res, self) : self, has = true;
        }
        if (r > ls) {
            Node s = rq(x.R, max(l - ls - 1, 0LL), r - ls - 1, cg);
            res = has ? combine(res, s) : s;
        }
        return res;
    }

    static int setAt(int t, long long i, const RawVal& val) {
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

    static PersistentLazyTreap wrap(int t) {
        PersistentLazyTreap res;
        res.root = t;
        return res;
    }

    // O(n)
    PersistentLazyTreap(const vector<RawVal>& a = {}) {
        if (nd.empty()) nd.emplace_back();
        root = build(a, 0, a.size());
    }

    // how many elements
    long long size() { return nd[root].sz; }

    // the Node of a[i]; needs 0 <= i < size(), else out_of_range
    Node pointGet(long long i) {
        if (i < 0 || i >= size()) throw out_of_range("pointGet: needs 0 <= i < size()");
        return rq(root, i, i, nullptr);
    }

    // a[i] = val; needs 0 <= i < size(), else out_of_range
    void pointAssign(long long i, const RawVal& val) {
        if (i < 0 || i >= size()) throw out_of_range("pointAssign: needs 0 <= i < size()");
        root = setAt(root, i, val);
    }

    // insert val so it becomes a[i] (i = size() appends); needs 0 <= i <= size(), else out_of_range
    void insertAt(long long i, const RawVal& val) {
        if (i < 0 || i > size()) throw out_of_range("insertAt: needs 0 <= i <= size()");
        int a, b;
        splitAt(root, i, a, b);
        root = join(join(a, newItem(val)), b);
    }

    void append(const RawVal& val) { root = join(root, newItem(val)); }

    // remove a[i]; needs 0 <= i < size(), else out_of_range
    void eraseAt(long long i) {
        if (i < 0 || i >= size()) throw out_of_range("eraseAt: needs 0 <= i < size()");
        int a, b, c;
        splitAt(root, i, a, b);
        splitAt(b, 1, b, c);
        root = join(a, c);
    }

    // the Node of a[l..r]; needs 0 <= l <= r < size(), else out_of_range
    Node rangeQuery(long long l, long long r) {
        if (l < 0 || r >= size() || l > r) throw out_of_range("rangeQuery: needs 0 <= l <= r < size()");
        return rq(root, l, r, nullptr);
    }

    // the Node of the whole array; needs size() >= 1, else out_of_range
    Node rangeQueryAll() {
        if (!root) throw out_of_range("rangeQueryAll: needs size() >= 1");
        return nd[root].agg;
    }

    // tag applied to every element of a[l..r]; needs 0 <= l <= r < size(), else out_of_range
    void rangeUpdate(long long l, long long r, const Tag& tag) {
        if (l < 0 || r >= size() || l > r) throw out_of_range("rangeUpdate: needs 0 <= l <= r < size()");
        int a, b, c;
        splitAt(root, l, a, b);
        splitAt(b, r - l + 1, b, c);
        applyTag(b, tag); // (b is a fresh copy: splitAt copies every node it returns)
        root = join(join(a, b), c);
    }

    // cyclic shift a[l..r] left by k (a[l+k] moves to l; any k, taken mod r - l + 1); needs 0 <= l <= r < size(), else
    // out_of_range
    void rangeRotateLeft(long long l, long long r, long long k) {
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
    void rangeRotateRight(long long l, long long r, long long k) {
        if (l < 0 || r >= size() || l > r) throw out_of_range("rangeRotateRight: needs 0 <= l <= r < size()");
        rangeRotateLeft(l, r, -(k % (r - l + 1)));
    }

    // the whole array as a PersistentLazyTreap of its own, O(1) (this one is unchanged)
    PersistentLazyTreap copy() { return wrap(root); }

    // a[l..r] as a PersistentLazyTreap of its own, O(log N) however long (this one is unchanged); needs
    // 0 <= l <= r < size(), else out_of_range
    PersistentLazyTreap copy(long long l, long long r) {
        if (l < 0 || r >= size() || l > r) throw out_of_range("copy: needs 0 <= l <= r < size()");
        int a, b, c;
        splitAt(root, l, a, b);
        splitAt(b, r - l + 1, b, c);
        return wrap(b);
    }

    // remove a[l..r] and get it back as a PersistentLazyTreap of its own; needs 0 <= l <= r < size(), else out_of_range
    PersistentLazyTreap cut(long long l, long long r) {
        if (l < 0 || r >= size() || l > r) throw out_of_range("cut: needs 0 <= l <= r < size()");
        int a, b, c;
        splitAt(root, l, a, b);
        splitAt(b, r - l + 1, b, c);
        root = join(a, c);
        return wrap(b);
    }

    // insert all of other so it starts at a[i] (other ends up empty); needs 0 <= i <= size(), else out_of_range
    void paste(long long i, PersistentLazyTreap& other) {
        if (i < 0 || i > size()) throw out_of_range("paste: needs 0 <= i <= size()");
        int a, b;
        splitAt(root, i, a, b);
        root = join(join(a, other.root), b);
        other.root = 0;
    }
    void paste(long long i, PersistentLazyTreap&& other) { paste(i, other); }

    // append all of other (other ends up empty)
    void merge(PersistentLazyTreap& other) {
        root = join(root, other.root);
        other.root = 0;
    }
    void merge(PersistentLazyTreap&& other) { merge(other); }

    // split into a[0..k-1] and a[k..] (this one ends up empty); needs 0 <= k <= size(), else out_of_range
    pair<PersistentLazyTreap, PersistentLazyTreap> split(long long k) {
        if (k < 0 || k > size()) throw out_of_range("split: needs 0 <= k <= size()");
        int a, b;
        splitAt(root, k, a, b);
        root = 0;
        return {wrap(a), wrap(b)};
    }

    // split into a[0..l-1], a[l..r], a[r+1..] (this one ends up empty); needs 0 <= l <= r < size(), else out_of_range
    tuple<PersistentLazyTreap, PersistentLazyTreap, PersistentLazyTreap> trisect(long long l, long long r) {
        if (l < 0 || r >= size() || l > r) throw out_of_range("trisect: needs 0 <= l <= r < size()");
        int a, b, c;
        splitAt(root, l, a, b);
        splitAt(b, r - l + 1, b, c);
        root = 0;
        return {wrap(a), wrap(b), wrap(c)};
    }
};
