// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/segment-trees/generic/GenericSeg.cpp
#include <bits/stdc++.h>
using namespace std;

// one raw array element: long long, char, pair, or a struct
using RawVal = long long;

struct Node {
    // long long tot;
    // long long mn;
};

Node leaf(const RawVal& v, int i) {
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

struct Seg {
    int n, cap;
    vector<Node> t;
    vector<char> has; // has[k]: node k covers at least one real leaf (the padding past n has none)

    Seg(const vector<RawVal>& a) : n(a.size()), cap(1) {
        while (cap < n) cap *= 2;
        t.assign(2 * cap, Node());
        has.assign(2 * cap, 0);
        for (int i = 0; i < n; i++) t[cap + i] = leaf(a[i], i), has[cap + i] = 1;
        for (int k = cap - 1; k >= 1; k--) pull(k);
    }

    void pull(int k) {
        // the padding is a suffix, so a node with an empty right child is just its left child
        has[k] = has[2 * k];
        if (has[2 * k + 1]) t[k] = combine(t[2 * k], t[2 * k + 1]);
        else if (has[2 * k]) t[k] = t[2 * k];
    }

    // how many elements
    int size() { return n; }

    // the Node of a[i]; needs 0 <= i < n, else out_of_range
    Node pointGet(int i) {
        if (i < 0 || i >= n) throw out_of_range("pointGet: needs 0 <= i < n");
        return t[cap + i];
    }

    // a[i] = val; needs 0 <= i < n, else out_of_range
    void pointAssign(int i, const RawVal& val) {
        if (i < 0 || i >= n) throw out_of_range("pointAssign: needs 0 <= i < n");
        int k = cap + i;
        t[k] = leaf(val, i);
        for (k >>= 1; k >= 1; k >>= 1) pull(k);
    }

    // the Node of a[l..r]; needs 0 <= l <= r < n, else out_of_range
    Node rangeQuery(int l, int r) {
        if (l < 0 || r >= n || l > r) throw out_of_range("rangeQuery: needs 0 <= l <= r < n");
        Node sl, sr;
        bool hl = false, hr = false;
        for (l += cap, r += cap + 1; l < r; l >>= 1, r >>= 1) {
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
};
