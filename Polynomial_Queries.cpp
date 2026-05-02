#include <bits/stdc++.h>
using namespace std;
using ll = long long;

struct Data {
    long long total = 0;
    int l; // endpoints of the segment
    int r;
};

struct Tag {
    ll constant = 0; // everything in this node must add +constant
    ll coeff = 0; // every index i in this node gains coeff*i
};

// NOTES:
// To get a proper lazy segment tree, use these abstractions.

// struct Data { ... };
// struct Tag { ... };

// A tag means it has already been applied to that node, and is pending for children.

// We want these utilities:

// Tag _compose(Tag old, Tag new) // combines 2 lazies
// Data _combine(Data left, Data right) // gives us aggregate data, used in _pull, but also _query

// // When we hit a fully contained ST node in a range application, we want to in O(1) apply the incoming tag to this node's data
// // So we do that, and then also _compose this incoming tag with the existing tag
// void _applyAndUpdateLazy(int nodeI, Tag t)

// // As we range apply or range query, if we stop at a given node (the node is fully contained), we are safe- we don't need to push any data down
// // because the current lazy tag is considered already applied to our data
// // but if we do need to keep dropping, push this tag down, meaning take the existing tag for our node, _applyAndUpdateLazy for both children
// // then RESET our existing lazy tag
// void _pushTagDownAndClear(int nodeI)

// // Used to pull up data from below, used in _build, or when we range apply, we need to pull up new values
// void _pull(nodeI)

// // just builds out the data and _pull's up
// void _build(...)

// // We descend down the tree, if we need to go further down, _pushTagDownAndClear the lazy tag first
// // As we get left and right results, _combine them
// Data _query(l, r)

// // We descend down the tree, _pushTagDownAndClear as we need
// // If we are fully contained, _applyAndUpdateLazy, otherwise _pushTagDownAndClear and descend down to both directions
// // before we terminate, _pull to recompute fresh values
// void _rangeAdd(l, r)

struct APSeg {
    int n;
    vector<Data> tree;
    vector<Tag> lazy;

    APSeg(const vector<ll>& A) {
        n = A.size();
        tree.resize(4 * n);
        lazy.resize(4 * n);
        _build(1, 0, n - 1, A);
    }

    // utils
    Tag _compose(Tag oldT, Tag newT) {
        Tag composed;
        composed.constant = oldT.constant + newT.constant;
        composed.coeff = oldT.coeff + newT.coeff;
        return composed;
    };

    // apply the tag to the nodes data and update lazy
    void _applyAndUpdateLazy(int nodeI, Tag t) {
        Data& d = tree[nodeI];
        int width = d.r - d.l + 1;
        d.total += (ll)width * t.constant;
        ll sumOfIndices = (long long)d.r * (d.r + 1) / 2;
        if (d.l) {
            sumOfIndices -= (long long)(d.l - 1) * (d.l) / 2;
        }
        d.total += sumOfIndices * t.coeff;
        lazy[nodeI] = _compose(lazy[nodeI], t);
    }

    // push this tag down to children, but first apply to them
    void _pushTagDownAndClear(int nodeI) {
        Tag& t = lazy[nodeI];
        if (2 * nodeI < 4 * n) {
            _applyAndUpdateLazy(2 * nodeI, t);
        }
        if (2 * nodeI + 1 < 4 * n) {
            _applyAndUpdateLazy(2 * nodeI + 1, t);
        }
        Tag empty; empty.constant = 0; empty.coeff = 0;
        lazy[nodeI] = empty;
    }

    Data _combine(Data left, Data right) {
        Data newData = {left.total + right.total, left.l, right.r};
        return newData;
    }

    void _pull(int nodeI) {
        Data left = tree[2 * nodeI];
        Data right = tree[2 * nodeI + 1];
        tree[nodeI] = _combine(left, right);
    }

    void _build(int nodeI, int tl, int tr, const vector<ll>& A) {
        if (tl == tr) {
            tree[nodeI] = {A[tl], tl, tr};
            return;
        }
        int tm = (tl + tr) / 2;
        _build(2 * nodeI, tl, tm, A);
        _build(2 * nodeI + 1, tm + 1, tr, A);
        _pull(nodeI);
    }

    Data _query(int nodeI, int tl, int tr, int ql, int qr) {
        // fully contained
        if (ql <= tl && qr >= tr) {
            return tree[nodeI];
        }
        _pushTagDownAndClear(nodeI);
        int tm = (tl + tr) / 2;
        // if only left is in range
        if (qr <= tm) {
            return _query(2 * nodeI, tl, tm, ql, qr);
        }
        // only right is in range
        if (ql >= tm + 1) {
            return _query(2 * nodeI + 1, tm + 1, tr, ql, qr);
        }
        Data left = _query(2 * nodeI, tl, tm, ql, qr);
        Data right = _query(2 * nodeI + 1, tm + 1, tr, ql, qr);
        return _combine(left, right);
    }

    void _rangeAdd(int nodeI, int tl, int tr, int ql, int qr, int constantAdd) {
        // out of bounds
        if (qr < tl || ql > tr) return;

        // fully contained, we put the tag here now
        if (ql <= tl && qr >= tr) {
            Tag t;
            t.constant = constantAdd;
            t.coeff = 1;
            _applyAndUpdateLazy(nodeI, t);
            return;
        }

        _pushTagDownAndClear(nodeI);

        int tm = (tl + tr) / 2;
        _rangeAdd(2 * nodeI, tl, tm, ql, qr, constantAdd);
        _rangeAdd(2 * nodeI + 1, tm + 1, tr, ql, qr, constantAdd);
        _pull(nodeI);


    }

    // ========== PUBLIC API ==========

    Data query(int l, int r) {
        return _query(1, 0, n - 1, l, r);
    }

    void rangeAdd(int l, int r) {
        // index l needs to gain 1
        // so we add -l + 1 to everything
        // and 1 * index to everything
        // so L gains 1, L+1 gains 2, etc
        _rangeAdd(1, 0, n - 1, l, r, 1 - l);
    }

};

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, q; cin >> n >> q;
    vector<ll> A(n); for (int i = 0; i < n; i++) cin >> A[i];
    APSeg seg = APSeg(A);
    for (int i = 0; i < q; i++) {
        int qtype; cin >> qtype;
        int a, b; cin >> a >> b; a--; b--;
        if (qtype == 1) {
            seg.rangeAdd(a, b);
        } else {
            cout << seg.query(a, b).total << '\n';
        }
    }
}