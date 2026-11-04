// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/segment-trees/generic/GenericDynamicSeg.complex.cpp
#include <bits/stdc++.h>
using namespace std;

// e.g. long long, char, pair, struct, ...
using RawVal = char;

struct Node {
    // long long cnt[26];  // how many of each letter
    // Node() {  // can make an empty constructor which runs every time a Node is made
    //     for (int c = 0; c < 26; c++) cnt[c] = 0;  // (the other fields are always set before they're read)
    // }
};

Node leaf(const RawVal& v, long long i) {
    // Node res;
    // res.cnt[v - 'a'] = 1;
    // return res;
}

Node combine(const Node& left, const Node& right) {
    // Node res;
    // for (int c = 0; c < 26; c++) res.cnt[c] = left.cnt[c] + right.cnt[c];
    // return res;
}

// the Node of lo..hi where nothing was ever set (every element the starting value, e.g. 0)
Node blank(long long lo, long long hi) {
    // Node res;  // (no letters: every count 0)
    // return res;
}

struct DynamicSeg {
    long long lo, hi;
    vector<Node> t;
    vector<int> L, R; // children; 0 = never touched, every element there still the starting value
    int root;

    // indices lo..hi (e.g. 0..1e18, negative is fine), every element starting as blank says; needs lo <= hi
    DynamicSeg(long long lo, long long hi) : lo(lo), hi(hi) {
        if (lo > hi) throw out_of_range("DynamicSeg: needs lo <= hi");
        t.push_back(Node()), L.push_back(0), R.push_back(0);
        root = make(lo, hi);
    }

    int make(long long nl, long long nr) {
        t.push_back(blank(nl, nr)), L.push_back(0), R.push_back(0);
        return t.size() - 1;
    }

    Node at(int k, long long nl, long long nr) { return k ? t[k] : blank(nl, nr); }

    static long long mid(long long nl, long long nr) { return nl + (nr - nl) / 2; }

    void setRec(int k, long long nl, long long nr, long long i, const RawVal& v) {
        if (nl == nr) return void(t[k] = leaf(v, i));
        long long m = mid(nl, nr);
        if (i <= m) {
            if (!L[k]) { int c = make(nl, m); L[k] = c; }
            setRec(L[k], nl, m, i, v);
        } else {
            if (!R[k]) { int c = make(m + 1, nr); R[k] = c; }
            setRec(R[k], m + 1, nr, i, v);
        }
        t[k] = combine(at(L[k], nl, m), at(R[k], m + 1, nr));
    }

    Node queryRec(int k, long long nl, long long nr, long long l, long long r) {
        if (l <= nl && nr <= r) return at(k, nl, nr);
        if (!k) return blank(max(l, nl), min(r, nr));
        long long m = mid(nl, nr);
        if (r <= m) return queryRec(L[k], nl, m, l, r);
        if (l > m) return queryRec(R[k], m + 1, nr, l, r);
        return combine(queryRec(L[k], nl, m, l, r), queryRec(R[k], m + 1, nr, l, r));
    }

    // a[i] = val; needs lo <= i <= hi, else out_of_range
    void pointAssign(long long i, const RawVal& val) {
        if (i < lo || i > hi) throw out_of_range("pointAssign: needs lo <= i <= hi");
        setRec(root, lo, hi, i, val);
    }

    // the Node of a[i]; needs lo <= i <= hi, else out_of_range
    Node pointGet(long long i) {
        if (i < lo || i > hi) throw out_of_range("pointGet: needs lo <= i <= hi");
        return queryRec(root, lo, hi, i, i);
    }

    // the Node of a[l..r]; needs lo <= l <= r <= hi, else out_of_range
    Node rangeQuery(long long l, long long r) {
        if (l < lo || r > hi || l > r) throw out_of_range("rangeQuery: needs lo <= l <= r <= hi");
        return queryRec(root, lo, hi, l, r);
    }

    // the Node of the whole array
    Node rangeQueryAll() { return t[root]; }
};
