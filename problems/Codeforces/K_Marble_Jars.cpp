#include <bits/stdc++.h>
using namespace std;
using ll = long long;

struct Node {
    bitset<1001> bs;
};

struct Tag {
    bitset<1001> added;
};

struct Seg {
    int n;
    vector<Node> tree;
    vector<Tag> lazy;

    Node _combine(Node& a, Node& b) {
        return {a.bs & b.bs};
    }

    Tag _compose(Tag old, Tag newT) {
        return {old.added | newT.added};
    }

    void _applyTagToNodeAndCompose(int nodeI, Tag t) {
        Node& node = tree[nodeI];
        node.bs |= t.added;
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
            tree[nodeI] = {bitset<1001>()};
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
};

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m; cin >> n >> m;
    vector<int> A(n);
    Seg seg(A);
    while (m--) {
        int qtype; cin >> qtype;
        if (qtype == 1) {
            int l, r, x; cin >> l >> r >> x; l--; r--;
            Tag t;
            t.added.set(x);
            seg.rangeUpdate(l, r, t);
        } else {
            int l, r; cin >> l >> r; l--; r--;
            Node out = seg.query(l, r);
            cout << out.bs.count() << endl;
        }
    }
    
}