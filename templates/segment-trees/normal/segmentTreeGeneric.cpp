#include <bits/stdc++.h>
using namespace std;
using ll = long long;

struct Node {
    // TODO: fill in
};

struct Seg {
    int n;
    vector<Node> tree;

    void _pull(int nodeI) {
        Node& left = tree[2*nodeI];
        Node& right = tree[2*nodeI + 1];
        tree[nodeI] = _combine(left, right);
    }

    Node _combine(Node& a, Node& b) {
        // TODO: fill in
    }

    void _build(int nodeI, int tl, int tr, vector<int>& A) {
        if (tl == tr) {
            tree[nodeI] = // TODO: fill in base function
            return;
        }
        int tm = (tl + tr) / 2;
        _build(2 * nodeI, tl, tm, A);
        _build(2 * nodeI + 1, tm + 1, tr, A);
        _pull(nodeI);
    }

    Seg(vector<int>& A) {
        n = A.size();
        tree.resize(4 * n);
        _build(1, 0, n - 1, A);
    }

    Node query(int l, int r) {
        return _query(1, 0, n - 1, l, r);
    }

    Node _query(int nodeI, int tl, int tr, int ql, int qr) {
        if (tl == tr) return tree[nodeI];
        if (ql <= tl && qr >= tr) return tree[nodeI];
        int tm = (tl + tr) / 2;
        if (qr <= tm) {
            Node left = _query(2*nodeI, tl, tm, ql, qr);
            return left;
        } else if (ql >= tm + 1) {
            Node right = _query(2*nodeI + 1, tm + 1, tr, ql, qr);
            return right;
        }
        Node left = _query(2*nodeI, tl, tm, ql, qr);
        Node right = _query(2*nodeI + 1, tm + 1, tr, ql, qr);
        return _combine(left, right);
    }

    void pointUpdate(int pos, int newVal) {
        _pointUpdate(1, 0, n - 1, pos, newVal);
    }

    void _pointUpdate(int nodeI, int tl, int tr, int pos, int newVal) {
        if (tl == tr) {
            tree[nodeI] = // TODO: fill in base function
            return;
        }
        int tm = (tl + tr) / 2;
        if (pos <= tm) {
            _pointUpdate(2 * nodeI, tl, tm, pos, newVal);
        } else {
            _pointUpdate(2 * nodeI + 1, tm + 1, tr, pos, newVal);
        }
        _pull(nodeI);
    }
};