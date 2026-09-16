// TEMPLATE BY https://github.com/agrawalishaan

// ========================
// COMPLEXITIES

// O(n) build
// SegTree_PERFORMANT seg(arr);

// C = largest value in the array
// O(logN):         pointSet(pos, newVal)
// O(logN * logC):  rangeMod(l, r, mod)
// O(logN * logC):  rangeDiv(l, r, div) (floor division)
// O(logN * log(logC)):  rangeSqrt(l, r) (floor sqrt)

// O(logN):         rangeSum(l, r)


// ========================
/**
HOW DO POTENTIALS WORK? (rangeMod example)

First when we do A%B with A>=B, A always falls by at least half. If B is < half of A, then obviously A is halved. If it is bigger, it is obviously halved too.

Consider all the values in the array. Each one can be halved at most logC times. There are N of them, so we have NlogC halvings.

There are 3 types of nodes in a seg tree:

1) STRADDLES THE QUERY RANGE (always recurses)
at most 2*logN visited per query

2) DEAD-END NODE (does not recurse)
always comes from one of the other nodes so these are free

3) FULLY COVERED NODES THAT DO RECURSE
in a normal segment tree we stop as soon as we hit one, here we do not
We must show the # of fully covered nodes we visit is bounded, as the others are bounded, then our total visits is bounded

When we visit a fully covered node and the max is < our mod, we terminate immediately (this falls into case 2)
If it is not, there is at least one value in this range that is going to halve. We recurse to the children.

Eventually that leaf gets halved, we can do NlogC halvings in total, and each time we do a halving,
we visit logN nodes that contain that leaf.

So at most we visit O(N logN logC) nodes in our rangeMod.

POINT SET:
This increases the potential of a node by adding up to logC halvings. Since we can call pointSet at most Q times, we increase potential
by QlogC which is fine as that adds Q*logN*logC total work to rangeMod.


*/

// ========================


# include<bits/stdc++.h>
using namespace std;


template <typename T>
struct SegTree_PERFORMANT {
    static_assert(std::is_integral_v<T>, "values must be integral: %, / and isqrt assume it");
    using SumT = long long;

    struct Node {
        T mx;
        SumT tot;
    };

    int n;
    std::vector<Node> tree;

    // O(n)
    explicit SegTree_PERFORMANT(const std::vector<T>& arr) {
        n = (int)arr.size();
        tree.resize(4 * std::max(1, n));
        if (n) _build(1, 0, n - 1, arr);
    }

    Node _makeLeaf(T v) { return Node{v, (SumT)v}; }

    Node _agg(const Node& left, const Node& right) {
        return Node{std::max(left.mx, right.mx), left.tot + right.tot};
    }

    void _build(int nodeI, int tl, int tr, const std::vector<T>& arr) {
        if (tl == tr) { tree[nodeI] = _makeLeaf(arr[tl]); return; }
        int tm = (tl + tr) / 2;
        _build(2 * nodeI, tl, tm, arr);
        _build(2 * nodeI + 1, tm + 1, tr, arr);
        tree[nodeI] = _agg(tree[2 * nodeI], tree[2 * nodeI + 1]);
    }

    // floor of the square root, exact for every integral T (sqrtl alone drifts near 2^63)
    static T _isqrt(T v) {
        if (v <= 0) return 0;
        T r = (T)::sqrtl((long double)v);
        while (r > 0 && r > v / r) r--;
        while ((r + 1) <= v / (r + 1)) r++;
        return r;
    }

    // shared driver: descend to leaves, pruning any subtree whose max says nothing can change.
    // leafOp maps one value to its new value, cutoff is the max below which nothing changes.
    template <class LeafOp>
    void _rangeShrink(int nodeI, int tl, int tr, int ql, int qr, T cutoff, LeafOp leafOp) {
        // oob
        if (qr < tl || ql > tr) return;
        // nothing under here can change
        if (tree[nodeI].mx < cutoff) return;
        // leaf, this is where the op actually happens
        if (tl == tr) { tree[nodeI] = _makeLeaf(leafOp(tree[nodeI].mx)); return; }
        int tm = (tl + tr) / 2;
        _rangeShrink(2 * nodeI, tl, tm, ql, qr, cutoff, leafOp);
        _rangeShrink(2 * nodeI + 1, tm + 1, tr, ql, qr, cutoff, leafOp);
        tree[nodeI] = _agg(tree[2 * nodeI], tree[2 * nodeI + 1]);
    }

    void _pointSet(int nodeI, int tl, int tr, int pos, T val) {
        if (tl == tr) { tree[nodeI] = _makeLeaf(val); return; }
        int tm = (tl + tr) / 2;
        if (pos <= tm) _pointSet(2 * nodeI, tl, tm, pos, val);
        else _pointSet(2 * nodeI + 1, tm + 1, tr, pos, val);
        tree[nodeI] = _agg(tree[2 * nodeI], tree[2 * nodeI + 1]);
    }

    SumT _rangeSum(int nodeI, int tl, int tr, int ql, int qr) {
        if (ql > tr || qr < tl) return 0;
        if (ql <= tl && qr >= tr) return tree[nodeI].tot;
        int tm = (tl + tr) / 2;
        return _rangeSum(2 * nodeI, tl, tm, ql, qr) + _rangeSum(2 * nodeI + 1, tm + 1, tr, ql, qr);
    }

    T _rangeMax(int nodeI, int tl, int tr, int ql, int qr) {
        if (ql > tr || qr < tl) return std::numeric_limits<T>::lowest();
        if (ql <= tl && qr >= tr) return tree[nodeI].mx;
        int tm = (tl + tr) / 2;
        return std::max(_rangeMax(2 * nodeI, tl, tm, ql, qr),
                        _rangeMax(2 * nodeI + 1, tm + 1, tr, ql, qr));
    }

    //////////////// PUBLIC METHODS START HERE ////////////////

    // amortized O(log n * log C) -- a[i] %= x for every i in l...r
    // prune at mx < x: everything there is already below x, so a % x == a
    void rangeMod(int l, int r, T x) {
        if (l > r || n == 0) return;
        _rangeShrink(1, 0, n - 1, l, r, x, [x](T v) { return v % x; });
    }

    // amortized O(log n * log C) -- a[i] /= x for every i in l...r. requires x >= 2
    // prune at mx < 1: only zeros left, and 0 / x == 0
    void rangeDiv(int l, int r, T x) {
        if (l > r || n == 0 || x < 2) return;
        _rangeShrink(1, 0, n - 1, l, r, (T)1, [x](T v) { return v / x; });
    }

    // amortized O(log n * log log C) -- a[i] = floor(sqrt(a[i])) for every i in l...r
    // prune at mx < 2: 0 and 1 are fixed points
    void rangeSqrt(int l, int r) {
        if (l > r || n == 0) return;
        _rangeShrink(1, 0, n - 1, l, r, (T)2, [](T v) { return _isqrt(v); });
    }

    // O(log n) -- a[pos] = val. an OVERWRITE, it may RAISE the value
    void pointSet(int pos, T val) { _pointSet(1, 0, n - 1, pos, val); }

    // O(log n)
    T pointGet(int pos) { return _rangeMax(1, 0, n - 1, pos, pos); }

    // O(log n) -- sum of l...r
    SumT rangeSum(int l, int r) {
        if (l > r || n == 0) return 0;
        return _rangeSum(1, 0, n - 1, l, r);
    }

    // O(log n) -- max of l...r
    T rangeMax(int l, int r) {
        if (l > r || n == 0) return std::numeric_limits<T>::lowest();
        return _rangeMax(1, 0, n - 1, l, r);
    }
};

template <typename T>
SegTree_PERFORMANT(const std::vector<T>&) -> SegTree_PERFORMANT<T>;