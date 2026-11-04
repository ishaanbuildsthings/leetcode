// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/segment-trees/generic/GenericPersistentTreap.norev.cpp
#include <bits/stdc++.h>
using namespace std;

// e.g. long long, char, pair, struct, ...
using RawVal = long long;

struct Node {
    // long long tot;
    // long long mn;
};

Node leaf(const RawVal& v) {
    // Node res;
    // res.tot = v, res.mn = v;
    // return res;
}

Node combine(const Node& left, const Node& right) {
    // Node res;
    // res.tot = left.tot + right.tot;
    // res.mn = min(left.mn, right.mn);
    // return res;
}

// Every op copies the nodes it changes instead of changing them, so a copy and its original never affect each other.
// copy(l, r) is O(log N) however long a[l..r] is, so lengths can get huge: they are long long.
struct PersistentTreap {
    struct Item {
        Node self, agg; // a[i] alone, and its subtree
        int L = 0, R = 0;
        long long sz = 0;
    };
    // one pool shared by every PersistentTreap (item 0 = the empty tree); nodes are never freed
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

    // a = the first k items of t, b = the rest (t itself unchanged)
    static void splitAt(int t, long long k, int& a, int& b) {
        if (!t) return void(a = b = 0);
        t = clone(t);
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
            int x = join(nd[a].R, b);
            nd[a].R = x;
            pull(a);
            return a;
        }
        b = clone(b);
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

    // the Node of items l..r of t (makes no copies)
    static Node rq(int t, long long l, long long r) {
        const Item& x = nd[t];
        if (l <= 0 && r >= x.sz - 1) return x.agg;
        long long ls = nd[x.L].sz;
        Node res;
        bool has = false;
        if (l < ls) res = rq(x.L, l, min(r, ls - 1)), has = true;
        if (l <= ls && ls <= r) res = has ? combine(res, x.self) : x.self, has = true;
        if (r > ls) {
            Node s = rq(x.R, max(l - ls - 1, 0LL), r - ls - 1);
            res = has ? combine(res, s) : s;
        }
        return res;
    }

    static int setAt(int t, long long i, const RawVal& val) {
        t = clone(t);
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

    static PersistentTreap wrap(int t) {
        PersistentTreap res;
        res.root = t;
        return res;
    }

    // O(n)
    PersistentTreap(const vector<RawVal>& a = {}) {
        if (nd.empty()) nd.emplace_back();
        root = build(a, 0, a.size());
    }

    // how many elements
    long long size() { return nd[root].sz; }

    // the Node of a[i]; needs 0 <= i < size(), else out_of_range
    Node pointGet(long long i) {
        if (i < 0 || i >= size()) throw out_of_range("pointGet: needs 0 <= i < size()");
        return rq(root, i, i);
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
        return rq(root, l, r);
    }

    // the Node of the whole array; needs size() >= 1, else out_of_range
    Node rangeQueryAll() {
        if (!root) throw out_of_range("rangeQueryAll: needs size() >= 1");
        return nd[root].agg;
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

    // the whole array as a PersistentTreap of its own, O(1) (this one is unchanged)
    PersistentTreap copy() { return wrap(root); }

    // a[l..r] as a PersistentTreap of its own, O(log N) however long (this one is unchanged); needs
    // 0 <= l <= r < size(), else out_of_range
    PersistentTreap copy(long long l, long long r) {
        if (l < 0 || r >= size() || l > r) throw out_of_range("copy: needs 0 <= l <= r < size()");
        int a, b, c;
        splitAt(root, l, a, b);
        splitAt(b, r - l + 1, b, c);
        return wrap(b);
    }

    // remove a[l..r] and get it back as a PersistentTreap of its own; needs 0 <= l <= r < size(), else out_of_range
    PersistentTreap cut(long long l, long long r) {
        if (l < 0 || r >= size() || l > r) throw out_of_range("cut: needs 0 <= l <= r < size()");
        int a, b, c;
        splitAt(root, l, a, b);
        splitAt(b, r - l + 1, b, c);
        root = join(a, c);
        return wrap(b);
    }

    // insert all of other so it starts at a[i] (other ends up empty); needs 0 <= i <= size(), else out_of_range
    void paste(long long i, PersistentTreap& other) {
        if (i < 0 || i > size()) throw out_of_range("paste: needs 0 <= i <= size()");
        int a, b;
        splitAt(root, i, a, b);
        root = join(join(a, other.root), b);
        other.root = 0;
    }
    void paste(long long i, PersistentTreap&& other) { paste(i, other); }

    // append all of other (other ends up empty)
    void merge(PersistentTreap& other) {
        root = join(root, other.root);
        other.root = 0;
    }
    void merge(PersistentTreap&& other) { merge(other); }

    // split into a[0..k-1] and a[k..] (this one ends up empty); needs 0 <= k <= size(), else out_of_range
    pair<PersistentTreap, PersistentTreap> split(long long k) {
        if (k < 0 || k > size()) throw out_of_range("split: needs 0 <= k <= size()");
        int a, b;
        splitAt(root, k, a, b);
        root = 0;
        return {wrap(a), wrap(b)};
    }

    // split into a[0..l-1], a[l..r], a[r+1..] (this one ends up empty); needs 0 <= l <= r < size(), else out_of_range
    tuple<PersistentTreap, PersistentTreap, PersistentTreap> trisect(long long l, long long r) {
        if (l < 0 || r >= size() || l > r) throw out_of_range("trisect: needs 0 <= l <= r < size()");
        int a, b, c;
        splitAt(root, l, a, b);
        splitAt(b, r - l + 1, b, c);
        root = 0;
        return {wrap(a), wrap(b), wrap(c)};
    }
};
