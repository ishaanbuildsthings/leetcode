#include <bits/stdc++.h>
using namespace std;
using ll = long long;

struct Node {
    // TODO: fill in
};

struct Tag {
    // TODO: fill in (default ctor must be no-op)
};

struct Seg {
    int n;
    vector<Node> tree;
    vector<Tag> lazy;

    Node _combine(Node& a, Node& b) {
        // TODO: fill in
    }

    Tag _compose(Tag old, Tag newT) {
        // TODO: fill in (semantically: apply old first, then newT)
    }

    void _applyTagToNodeAndCompose(int nodeI, Tag t) {
        Node& node = tree[nodeI];
        // TODO: fill in (mutate node based on t)
        lazy[nodeI] = _compose(lazy[nodeI], t);
    }

    void _pull(int nodeI) {
        tree[nodeI] = _combine(tree[2 * nodeI], tree[2 * nodeI + 1]);
    }

    void _pushDownAndClear(int nodeI) {
        _applyTagToNodeAndCompose(2 * nodeI, lazy[nodeI]);
        _applyTagToNodeAndCompose(2 * nodeI + 1, lazy[nodeI]);
        Tag empty;
        lazy[nodeI] = empty;
    }

    void _build(int nodeI, int tl, int tr, const vector<int>& A) {
        if (tl == tr) {
            tree[nodeI] = // TODO: fill in base function
            return;
        }
        int tm = (tl + tr) / 2;
        _build(2 * nodeI, tl, tm, A);
        _build(2 * nodeI + 1, tm + 1, tr, A);
        _pull(nodeI);
    }

    Seg(const vector<int>& A) {
        n = A.size();
        tree.resize(4 * n);
        lazy.resize(4 * n);
        _build(1, 0, n - 1, A);
    }

    Node _query(int nodeI, int tl, int tr, int ql, int qr) {
        if (ql <= tl && qr >= tr) {
            return tree[nodeI];
        }
        _pushDownAndClear(nodeI);
        int tm = (tl + tr) / 2;
        if (qr <= tm) {
            return _query(2 * nodeI, tl, tm, ql, qr);
        } else if (ql >= tm + 1) {
            return _query(2 * nodeI + 1, tm + 1, tr, ql, qr);
        }
        Node left = _query(2 * nodeI, tl, tm, ql, qr);
        Node right = _query(2 * nodeI + 1, tm + 1, tr, ql, qr);
        return _combine(left, right);
    }

    Node query(int l, int r) {
        return _query(1, 0, n - 1, l, r);
    }

    void _rangeUpdate(int nodeI, int tl, int tr, int ql, int qr, Tag t) {
        if (qr < tl || ql > tr) return;
        if (ql <= tl && qr >= tr) {
            _applyTagToNodeAndCompose(nodeI, t);
            return;
        }
        _pushDownAndClear(nodeI);
        int tm = (tl + tr) / 2;
        _rangeUpdate(2 * nodeI, tl, tm, ql, qr, t);
        _rangeUpdate(2 * nodeI + 1, tm + 1, tr, ql, qr, t);
        _pull(nodeI);
    }

    void rangeUpdate(int l, int r, Tag t) {
        _rangeUpdate(1, 0, n - 1, l, r, t);
    }

    void _pointUpdate(int nodeI, int tl, int tr, int pos, int newVal) {
        if (tl == tr) {
            tree[nodeI] = // TODO: fill in base function
            return;
        }
        _pushDownAndClear(nodeI);
        int tm = (tl + tr) / 2;
        if (pos <= tm) {
            _pointUpdate(2 * nodeI, tl, tm, pos, newVal);
        } else {
            _pointUpdate(2 * nodeI + 1, tm + 1, tr, pos, newVal);
        }
        _pull(nodeI);
    }

    void pointUpdate(int pos, int newVal) {
        _pointUpdate(1, 0, n - 1, pos, newVal);
    }
};