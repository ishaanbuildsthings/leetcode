// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/generic-seg-trees/GenericLazySeg.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// e.g. long long, char, pair, struct, ...
using RawVal = long long;

struct Node {
    // long long tot;
    // long long mn;
    // int len;
};

// a pending update to every element of a segment
// We never need to worry about initializing empty tags or anything, these tags come in via rangeUpdate(l, r, tag) calls
// or when pushed down from parents
struct Tag {
    // long long add;
};

Node leaf(const RawVal& v, int i) {
    // Node res;
    // res.tot = v, res.mn = v, res.len = 1;
    // return res;
}

Node combine(const Node& left, const Node& right) {
    // Node res;
    // res.tot = left.tot + right.tot, res.mn = min(left.mn, right.mn);
    // res.len = left.len + right.len;
    // return res;
}

// return a new node: this node after tag is applied to it
// this function is never called with a tag that never existed, but tags can have things like pending false values or
// pending no-ops (for instance two lazy bools canceling) and we still need to check for this and no-op (could just
// return original node)
Node apply(Node node, const Tag& tag) {
    // This is NOT mutating since node is taken by value in the arg, we can also just make a new node if needed
    // node.tot += tag.add * node.len, node.mn += tag.add;
    // return node;
}

// a tag that is the old tag, then the new tag
Tag compose(Tag old, const Tag& newer) {
    // This is NOT mutating since old is taken by value in the arg, we can also just make a new tag if needed
    // old.add += newer.add;
    // return old;
}

struct LazySeg {
    int n, cap, lg;
    vector<Node> t;
    vector<Tag> lz;
    // has[k]: node k covers at least one real leaf; tagged[k]: lz[k] is pending for node k's children
    vector<char> has, tagged;

    LazySeg(const vector<RawVal>& a) : n(a.size()), cap(1), lg(0) {
        while (cap < n) cap *= 2, lg++;
        t.assign(2 * cap, Node());
        lz.assign(cap, Tag());
        has.assign(2 * cap, 0);
        tagged.assign(cap, 0);
        for (int i = 0; i < n; i++) t[cap + i] = leaf(a[i], i), has[cap + i] = 1;
        for (int k = cap - 1; k >= 1; k--) pull(k);
    }

    void pull(int k) {
        // the padding is a suffix, so a node with an empty right child is just its left child
        has[k] = has[2 * k];
        if (has[2 * k + 1]) t[k] = combine(t[2 * k], t[2 * k + 1]);
        else if (has[2 * k]) t[k] = t[2 * k];
    }

    void applyAt(int k, const Tag& tag) {
        if (!has[k]) return;
        t[k] = apply(t[k], tag);
        if (k < cap) {
            if (tagged[k]) lz[k] = compose(lz[k], tag);
            else lz[k] = tag, tagged[k] = 1;
        }
    }

    void push(int k) {
        if (!tagged[k]) return;
        applyAt(2 * k, lz[k]);
        applyAt(2 * k + 1, lz[k]);
        tagged[k] = 0;
    }

    // pushes the tags above the leaf range [l, r) (l and r already offset by cap)
    void pushAbove(int l, int r) {
        for (int i = lg; i >= 1; i--) {
            if (((l >> i) << i) != l) push(l >> i);
            if (((r >> i) << i) != r) push((r - 1) >> i);
        }
    }

    // how many elements
    int size() { return n; }

    // the Node of a[i]; needs 0 <= i < n, else out_of_range
    Node pointGet(int i) {
        if (i < 0 || i >= n) throw out_of_range("pointGet: needs 0 <= i < n");
        int k = cap + i;
        for (int j = lg; j >= 1; j--) push(k >> j);
        return t[k];
    }

    // a[i] = val; needs 0 <= i < n, else out_of_range
    void pointAssign(int i, const RawVal& val) {
        if (i < 0 || i >= n) throw out_of_range("pointAssign: needs 0 <= i < n");
        int k = cap + i;
        for (int j = lg; j >= 1; j--) push(k >> j);
        t[k] = leaf(val, i);
        for (int j = 1; j <= lg; j++) pull(k >> j);
    }

    // the Node of a[l..r]; needs 0 <= l <= r < n, else out_of_range
    Node rangeQuery(int l, int r) {
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
    Node rangeQueryAll() {
        if (n == 0) throw out_of_range("rangeQueryAll: needs n >= 1");
        return t[1];
    }

    // tag applied to every element of a[l..r]; needs 0 <= l <= r < n, else out_of_range
    void rangeUpdate(int l, int r, const Tag& tag) {
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
