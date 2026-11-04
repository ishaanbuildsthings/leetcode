// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/segment-trees/generic/GenericTreap.complex.norev.cpp
#include <bits/stdc++.h>
using namespace std;

// e.g. long long, char, pair, struct, ...
using RawVal = char;

struct Node {
    // int cnt[26];  // how many of each letter
    // Node() {  // can make an empty constructor which runs every time a Node is made
    //     for (int c = 0; c < 26; c++) cnt[c] = 0;  // (the other fields are always set before they're read)
    // }
};

Node leaf(const RawVal& v) {
    // Node res;
    // res.cnt[v - 'a'] = 1;
    // return res;
}

Node combine(const Node& left, const Node& right) {
    // Node res;
    // for (int c = 0; c < 26; c++) res.cnt[c] = left.cnt[c] + right.cnt[c];
    // return res;
}

struct Treap {
    struct Item {
        Node self, agg; // a[i] alone, and its subtree
        int L = 0, R = 0, sz = 0;
        unsigned long long pr = 0;
    };
    // one pool shared by every Treap, so cut / paste move nodes between them (item 0 = the empty tree)
    static inline vector<Item> nd;
    int root = 0;

    static unsigned long long rnd() {
        static mt19937_64 g(chrono::steady_clock::now().time_since_epoch().count());
        return g();
    }

    static int newItem(const RawVal& v) {
        Item it;
        it.self = it.agg = leaf(v);
        it.sz = 1, it.pr = rnd();
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

    // a = the first k items of t, b = the rest
    static void splitAt(int t, int k, int& a, int& b) {
        if (!t) return void(a = b = 0);
        if (nd[nd[t].L].sz < k) splitAt(nd[t].R, k - nd[nd[t].L].sz - 1, nd[t].R, b), a = t;
        else splitAt(nd[t].L, k, a, nd[t].L), b = t;
        pull(t);
    }

    static int join(int a, int b) {
        if (!a || !b) return a ? a : b;
        if (nd[a].pr > nd[b].pr) {
            nd[a].R = join(nd[a].R, b);
            pull(a);
            return a;
        }
        nd[b].L = join(a, nd[b].L);
        pull(b);
        return b;
    }

    // the Node of items l..r of t: walks down and combines the pieces that cover them (no split / merge)
    static Node rq(int t, int l, int r) {
        if (l <= 0 && r >= nd[t].sz - 1) return nd[t].agg;
        int ls = nd[nd[t].L].sz;
        if (r < ls) return rq(nd[t].L, l, r);
        if (l > ls) return rq(nd[t].R, l - ls - 1, r - ls - 1);
        Node res = nd[t].self;
        if (l < ls) res = combine(rq(nd[t].L, l, ls - 1), res);
        if (r > ls) res = combine(res, rq(nd[t].R, 0, r - ls - 1));
        return res;
    }

    // a[i] = val in t's subtree, recomputing the nodes on the way back up
    static void setAt(int t, int i, const RawVal& val) {
        int ls = nd[nd[t].L].sz;
        if (i < ls) setAt(nd[t].L, i, val);
        else if (i > ls) setAt(nd[t].R, i - ls - 1, val);
        else nd[t].self = leaf(val);
        pull(t);
    }

    // O(n)
    Treap(const vector<RawVal>& a = {}) {
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

    static Treap wrap(int t) {
        Treap res;
        res.root = t;
        return res;
    }

    // how many elements
    int size() { return nd[root].sz; }

    // the Node of a[i]; needs 0 <= i < size(), else out_of_range
    Node pointGet(int i) {
        if (i < 0 || i >= size()) throw out_of_range("pointGet: needs 0 <= i < size()");
        int t = root;
        while (true) {
            int ls = nd[nd[t].L].sz;
            if (i < ls) t = nd[t].L;
            else if (i == ls) return nd[t].self;
            else i -= ls + 1, t = nd[t].R;
        }
    }

    // a[i] = val; needs 0 <= i < size(), else out_of_range
    void pointAssign(int i, const RawVal& val) {
        if (i < 0 || i >= size()) throw out_of_range("pointAssign: needs 0 <= i < size()");
        setAt(root, i, val);
    }

    // insert val so it becomes a[i] (i = size() appends); needs 0 <= i <= size(), else out_of_range
    void insertAt(int i, const RawVal& val) {
        if (i < 0 || i > size()) throw out_of_range("insertAt: needs 0 <= i <= size()");
        int a, b;
        splitAt(root, i, a, b);
        root = join(join(a, newItem(val)), b);
    }

    void append(const RawVal& val) { root = join(root, newItem(val)); }

    // remove a[i]; needs 0 <= i < size(), else out_of_range
    void eraseAt(int i) {
        if (i < 0 || i >= size()) throw out_of_range("eraseAt: needs 0 <= i < size()");
        int a, b, c;
        splitAt(root, i, a, b);
        splitAt(b, 1, b, c);
        root = join(a, c);
    }

    // the Node of a[l..r]; needs 0 <= l <= r < size(), else out_of_range
    Node rangeQuery(int l, int r) {
        if (l < 0 || r >= size() || l > r) throw out_of_range("rangeQuery: needs 0 <= l <= r < size()");
        return rq(root, l, r);
    }

    // the Node of the whole array; needs size() >= 1, else out_of_range
    Node rangeQueryAll() {
        if (!root) throw out_of_range("rangeQueryAll: needs size() >= 1");
        return nd[root].agg;
    }

    // remove a[l..r] and get it back as a Treap of its own; needs 0 <= l <= r < size(), else out_of_range
    Treap cut(int l, int r) {
        if (l < 0 || r >= size() || l > r) throw out_of_range("cut: needs 0 <= l <= r < size()");
        int a, b, c;
        splitAt(root, l, a, b);
        splitAt(b, r - l + 1, b, c);
        root = join(a, c);
        return wrap(b);
    }

    // insert all of other so it starts at a[i] (other ends up empty); needs 0 <= i <= size(), else out_of_range
    void paste(int i, Treap& other) {
        if (i < 0 || i > size()) throw out_of_range("paste: needs 0 <= i <= size()");
        int a, b;
        splitAt(root, i, a, b);
        root = join(join(a, other.root), b);
        other.root = 0;
    }
    void paste(int i, Treap&& other) { paste(i, other); }

    // append all of other (other ends up empty)
    void merge(Treap& other) {
        root = join(root, other.root);
        other.root = 0;
    }
    void merge(Treap&& other) { merge(other); }

    // split into a[0..k-1] and a[k..] (this one ends up empty); needs 0 <= k <= size(), else out_of_range
    pair<Treap, Treap> split(int k) {
        if (k < 0 || k > size()) throw out_of_range("split: needs 0 <= k <= size()");
        int a, b;
        splitAt(root, k, a, b);
        root = 0;
        return {wrap(a), wrap(b)};
    }

    // split into a[0..l-1], a[l..r], a[r+1..] (this one ends up empty); needs 0 <= l <= r < size(), else out_of_range
    tuple<Treap, Treap, Treap> trisect(int l, int r) {
        if (l < 0 || r >= size() || l > r) throw out_of_range("trisect: needs 0 <= l <= r < size()");
        int a, b, c;
        splitAt(root, l, a, b);
        splitAt(b, r - l + 1, b, c);
        root = 0;
        return {wrap(a), wrap(b), wrap(c)};
    }

    // cyclic shift a[l..r] left by k (a[l+k] moves to l; any k, taken mod r - l + 1); needs 0 <= l <= r < size(), else
    // out_of_range
    void rangeRotateLeft(int l, int r, long long k) {
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
    void rangeRotateRight(int l, int r, long long k) {
        if (l < 0 || r >= size() || l > r) throw out_of_range("rangeRotateRight: needs 0 <= l <= r < size()");
        rangeRotateLeft(l, r, -k);
    }
};
