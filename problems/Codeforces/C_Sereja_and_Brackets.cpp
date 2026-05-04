#include <bits/stdc++.h>
using namespace std;
using ll = long long;

struct Node {
    int rbs = 0;
    int prefClosed = 0;
    int suffOpen = 0;
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
        int used = min(a.suffOpen, b.prefClosed);
        int nrbs = a.rbs + b.rbs + 2 * used;
        int nprefClosed = a.prefClosed + b.prefClosed - used;
        int nsuffOpen = a.suffOpen + b.suffOpen - used;
        Node out = {nrbs, nprefClosed, nsuffOpen};
        return out;
    }
    void _build(int nodeI, int tl, int tr, string& s) {
        if (tl == tr) {
            tree[nodeI] = {0, s[tl] == '(' ? 0 : 1, s[tl] == ')' ? 0 : 1};
            return;
        }
        int tm = (tl + tr) / 2;
        _build(2 * nodeI, tl, tm, s);
        _build(2 * nodeI + 1, tm + 1, tr, s);
        _pull(nodeI);
    }
    Seg(string& s) {
        n = s.size();
        tree.resize(4 * n);
        _build(1, 0, n - 1, s);
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
};

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    string s; cin >> s;
    Seg seg(s);
    int q; cin >> q;
    while (q--) {
        int l, r; cin >> l >> r; l--; r--;
        cout << seg.query(l, r).rbs << '\n';
    }
}