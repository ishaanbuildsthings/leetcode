#include <bits/stdc++.h>
using namespace std;
using ll = long long;

struct Node {
    // we store 74 because the lazy tag is going to flip us
    int a44, a47, a74, a77; // longest subsequences with these properties, so start wtih 4 end with 4, start with 4 end with 7, etc
    int fours; // we also need individuals
    int sevens;
};

struct Tag {
    bool flipped = false;
};

struct Seg {
    int n;
    vector<Node> tree;
    vector<Tag> lazy;
    Node _combine(Node& L, Node& R) {
        Node out;
        out.a44 = L.fours + R.fours;
        out.a47 = max({L.a47 + R.sevens, L.fours + R.a47, L.fours + R.sevens});
        out.a74 = max({L.a74 + R.fours, L.sevens + R.a74, L.sevens + R.fours});
        out.a77 = L.sevens + R.sevens;
        out.fours = L.fours + R.fours;
        out.sevens = L.sevens + R.sevens;
        return out;
    }
    void _pull(int nodeI) {
        tree[nodeI] = _combine(tree[2 * nodeI], tree[2 * nodeI + 1]);
    }
    void _build(int nodeI, int tl, int tr, const vector<int>& A) {
        if (tl == tr) {
            if (A[tl] == 4) {
                tree[nodeI] = {1, 0, 0, 0, 1, 0};
            } else {
                tree[nodeI] = {0, 0, 0, 1, 0, 1};
            }
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
    Tag _compose(Tag& old, Tag& newT) {
        Tag out;
        out.flipped = old.flipped ^ newT.flipped;
        return out;
    }
    void _applyTagAndCompose(int nodeI, Tag t) {
        if (t.flipped) {
            Node out;
            Node& og = tree[nodeI];
            out.a44 = og.a77;
            out.a77 = og.a44;
            out.fours = og.sevens;
            out.sevens = og.fours;
            out.a47 = og.a74;
            out.a74 = og.a47;
            tree[nodeI] = out;
        }
        lazy[nodeI] = _compose(lazy[nodeI], t);
        return;
    }
    void _pushDownAndClear(int nodeI) {
        _applyTagAndCompose(2 * nodeI, lazy[nodeI]);
        _applyTagAndCompose(2 * nodeI + 1, lazy[nodeI]);
        lazy[nodeI] = {false};
    }
    void _rangeFlip(int nodeI, int tl, int tr, int ql, int qr) {
        // oob
        if (qr < tl || ql > tr) {
            return;
        }
        // fully inside
        if (ql <= tl && qr >= tr) {
            _applyTagAndCompose(nodeI, {true});
            return;
        }
        _pushDownAndClear(nodeI);
        int tm = (tl + tr) / 2;
        _rangeFlip(2 * nodeI, tl, tm, ql, qr);
        _rangeFlip(2 * nodeI + 1, tm + 1, tr, ql, qr);
        _pull(nodeI);
    }
    void rangeFlip(int l, int r) {
        _rangeFlip(1, 0, n - 1, l, r);
    }
    Node _query(int nodeI, int tl, int tr, int ql, int qr) {
        // oob
        if (qr < tl || ql > tr) {
            return {0, 0, 0, 0, 0, 0};
        }
        // fully inside
        if (ql <= tl && qr >= tr) {
            return tree[nodeI];
        }
        _pushDownAndClear(nodeI);
        int tm = (tl + tr) / 2;
        Node left = _query(2 * nodeI, tl, tm, ql, qr);
        Node right = _query(2 * nodeI + 1, tm + 1, tr, ql, qr);
        _pull(nodeI);
        return _combine(left, right);
    }
    Node query(int l, int r) {
        return _query(1, 0, n - 1, l, r);
    }
};

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m; cin >> n >> m;
    string s; cin >> s;
    vector<int> A(n);
    for (int i = 0; i < n; i++) {
        A[i] = s[i] - '0';
    }
    Seg seg(A);
    while (m--) {
        string qtype; cin >> qtype;
        if (qtype == "count") {
            Node total = seg.query(0, n - 1);
            int mx = max(max(total.a44, total.a47), total.a77);
            cout << mx << '\n';
        } else {
            int l, r; cin >> l >> r; l--; r--;
            seg.rangeFlip(l, r);
        }
    }
}