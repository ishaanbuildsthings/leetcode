// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/segment-trees/generic/GenericTreap.cpp
#include <bits/stdc++.h>
using namespace std;

// one raw array element: long long, char, pair, or a struct
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

// combine two nodes
Node combine(const Node& left, const Node& right) {
    // Node res;
    // res.tot = left.tot + right.tot;
    // res.mn = min(left.mn, right.mn);
    // return res;
}

// node becomes the Node of its segment read backwards (only rangeReverse uses it; nothing to do for sums / mins)
void reverse(Node& node) {
    // swap(node.pre, node.suf);
}

struct Treap {
    struct Item {
        Node self, agg; // a[i] alone, and its subtree
        int L = 0, R = 0, sz = 0;
        unsigned long long pr = 0;
        bool rev = false;
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

    static void flip(int t) {
        if (!t) return;
        swap(nd[t].L, nd[t].R);
        reverse(nd[t].agg);
        nd[t].rev ^= 1;
    }

    static void push(int t) {
        if (nd[t].rev) flip(nd[t].L), flip(nd[t].R), nd[t].rev = false;
    }

    // a = the first k items of t, b = the rest
    static void split(int t, int k, int& a, int& b) {
        if (!t) return void(a = b = 0);
        push(t);
        if (nd[nd[t].L].sz < k) split(nd[t].R, k - nd[nd[t].L].sz - 1, nd[t].R, b), a = t;
        else split(nd[t].L, k, a, nd[t].L), b = t;
        pull(t);
    }

    static int merge(int a, int b) {
        if (!a || !b) return a ? a : b;
        if (nd[a].pr > nd[b].pr) {
            push(a);
            nd[a].R = merge(nd[a].R, b);
            pull(a);
            return a;
        }
        push(b);
        nd[b].L = merge(a, nd[b].L);
        pull(b);
        return b;
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

    // how many elements
    int size() { return nd[root].sz; }

    // the Node of a[i]; needs 0 <= i < size(), else out_of_range
    Node pointGet(int i) {
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
    void pointAssign(int i, const RawVal& val) {
        if (i < 0 || i >= size()) throw out_of_range("pointAssign: needs 0 <= i < size()");
        int a, b, c;
        split(root, i, a, b);
        split(b, 1, b, c);
        nd[b].self = leaf(val);
        pull(b);
        root = merge(merge(a, b), c);
    }

    // insert val so it becomes a[i] (i = size() appends); needs 0 <= i <= size(), else out_of_range
    void insertAt(int i, const RawVal& val) {
        if (i < 0 || i > size()) throw out_of_range("insertAt: needs 0 <= i <= size()");
        int a, b;
        split(root, i, a, b);
        root = merge(merge(a, newItem(val)), b);
    }

    void append(const RawVal& val) { root = merge(root, newItem(val)); }

    // remove a[i]; needs 0 <= i < size(), else out_of_range
    void eraseAt(int i) {
        if (i < 0 || i >= size()) throw out_of_range("eraseAt: needs 0 <= i < size()");
        int a, b, c;
        split(root, i, a, b);
        split(b, 1, b, c);
        root = merge(a, c);
    }

    // the Node of a[l..r]; needs 0 <= l <= r < size(), else out_of_range
    Node rangeQuery(int l, int r) {
        if (l < 0 || r >= size() || l > r) throw out_of_range("rangeQuery: needs 0 <= l <= r < size()");
        int a, b, c;
        split(root, l, a, b);
        split(b, r - l + 1, b, c);
        Node res = nd[b].agg;
        root = merge(merge(a, b), c);
        return res;
    }

    // the Node of the whole array; needs size() >= 1, else out_of_range
    Node rangeQueryAll() {
        if (!root) throw out_of_range("rangeQueryAll: needs size() >= 1");
        return nd[root].agg;
    }

    // reverse a[l..r]; needs 0 <= l <= r < size(), else out_of_range
    void rangeReverse(int l, int r) {
        if (l < 0 || r >= size() || l > r) throw out_of_range("rangeReverse: needs 0 <= l <= r < size()");
        int a, b, c;
        split(root, l, a, b);
        split(b, r - l + 1, b, c);
        flip(b);
        root = merge(merge(a, b), c);
    }

    // remove a[l..r] and get it back as a Treap of its own; needs 0 <= l <= r < size(), else out_of_range
    Treap cut(int l, int r) {
        if (l < 0 || r >= size() || l > r) throw out_of_range("cut: needs 0 <= l <= r < size()");
        int a, b, c;
        split(root, l, a, b);
        split(b, r - l + 1, b, c);
        root = merge(a, c);
        Treap piece;
        piece.root = b;
        return piece;
    }

    // insert all of other so it starts at a[i] (other ends up empty); needs 0 <= i <= size(), else out_of_range
    void paste(int i, Treap& other) {
        if (i < 0 || i > size()) throw out_of_range("paste: needs 0 <= i <= size()");
        int a, b;
        split(root, i, a, b);
        root = merge(merge(a, other.root), b);
        other.root = 0;
    }
    void paste(int i, Treap&& other) { paste(i, other); }
};
