#include <bits/stdc++.h>
using namespace std;
#include <climits>
long long NINF = -(1LL << 60);

struct AltSeg {
    struct Node {
        long long pp; // both ends have plus sign before them
        long long pn; // plus before first element, negative before last element
        long long nn;
        long long np;
    };
    vector<int> A;
    vector<Node> tree;
    int n;
    AltSeg(const vector<int>& _A) {
        A = _A;
        n = A.size();
        tree.resize(4 * n + 5);
        build();
    }
    void build() {
        _build(1, 0, n - 1);
    }
    Node makeLeaf(int val) {
        return Node{val, NINF, -val, NINF};
    }
    void _build(int i, int tl, int tr) {
        if (tl == tr) {
            tree[i] = makeLeaf(A[tl]);
            return;
        }
        int tm = (tr + tl) / 2;
        _build(2 * i, tl, tm);
        _build(2 * i + 1, tm + 1, tr);
        pull(i);
    }
    Node merge(Node& left, Node& right) {
        long long newPP = max({left.pp, right.pp, left.pp + right.np, left.pn + right.pp}); // pp then np, or existing pps, or pn then pp
        long long newPN = max({left.pp + right.nn, left.pn + right.pn, left.pn, right.pn}); // PN can be PP then NN, existing PNs, or PN PN
        long long newNN = max({left.nn, right.nn, left.nn + right.pn, left.np + right.nn}); // NN can be existing NN, NN then PN, or NP then NN
        long long newNP = max({left.np, right.np, left.nn + right.pp, left.np + right.np}); // NP can be existing, or NN then PP, or NP then NP
        return Node{newPP, newPN, newNN, newNP};
    }
    void pull(int i) {
        tree[i] = merge(tree[2*i],tree[2*i+1]);
    }
    long long query(int l, int r) {
        auto Node = _query(1, 0, n - 1, l, r);
        return Node.pp;
    }
    long long queryAll() {
        return tree[1].pp;
    }
    Node _query(int i, int tl, int tr, int ql, int qr) {
        // fully contained
        if (ql <= tl && qr >= tr) {
            return tree[i];
        }
        int tm = (tr + tl) / 2;
        // only left
        if (qr <= tm) {
            return _query(2 * i, tl, tm, ql, qr);
        }
        // only right
        if (ql >= tm + 1) {
            return _query(2 * i + 1, tm + 1, tr, ql, qr);
        }
        // both
        Node left =_query(2 * i, tl, tm, ql, qr);
        Node right = _query(2 * i + 1, tm + 1, tr, ql, qr);
        return merge(left, right);
    }
    void pointAssign(int pos, int newV) {
        _pointAssign(1, 0, n - 1, pos, newV);
    }
    void _pointAssign(int i, int tl, int tr, int pos, int newV) {
        if (tl == tr) {
            tree[i] = makeLeaf(newV);
            return;
        }
        int tm = (tr + tl) / 2;
        if (pos <= tm) {
            _pointAssign(2 * i, tl, tm, pos, newV);
        } else {
            _pointAssign(2 * i + 1, tm + 1, tr, pos, newV);
        }
        pull(i);
    }
};

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int t; cin >> t;
    while (t--) {
        int n, q; cin >> n >> q;
        vector<int> A(n); for (int i = 0; i < n; i++) cin >> A[i];
        AltSeg seg(A);
        cout << seg.queryAll() << endl;
        for (int i = 0; i < q; i++) {
            int l, r; cin >> l >> r;
            l--; r--;
            int currL = A[l];
            int currR = A[r];
            seg.pointAssign(l, currR);
            seg.pointAssign(r, currL);
            A[l] = currR;
            A[r] = currL;
            cout << seg.queryAll() << endl;
        }
    }
}