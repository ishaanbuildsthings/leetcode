#include <bits/stdc++.h>
using namespace std;
using ll = long long;

const int LOG = 20;

struct Node {
    int cnt[LOG] = {}; // count[b] is how many bits of that size are in this range
    int width = 1; // how big we are
};

struct Tag {
    bool flipped[LOG] = {}; // if every one of these bits is actually flipped
};

struct Seg {
    int n;
    vector<Node> tree;
    vector<Tag> lazy;

    Node _combine(Node& a, Node& b) {
        Node out;
        for (int bit = 0; bit < LOG; bit++) {
            out.cnt[bit] = a.cnt[bit] + b.cnt[bit]; 
        }
        out.width = a.width + b.width;
        return out;
    }
    void _pull(int nodeI) {
        tree[nodeI] = _combine(tree[2 * nodeI], tree[2 * nodeI + 1]);
    }
    void _build(int nodeI, int tl, int tr, const vector<int>& A) {
        if (tl == tr) {
            for (int b = 0; b < LOG; b++) {
                if ((1 << b) & A[tl]) {
                    tree[nodeI].cnt[b]++;
                }
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

    void _pushDownAndClear(int nodeI, Tag& t) {
        _applyTagToNodeAndCompose(2 * nodeI, t);
        _applyTagToNodeAndCompose(2 * nodeI + 1, t);
        Tag empty;
        lazy[nodeI] = empty;
    }

    Node _query(int nodeI, int tl, int tr, int ql, int qr) {
        // fully contained
        if (ql <= tl && qr >= tr) {
            return tree[nodeI];
        }
        _pushDownAndClear(nodeI, lazy[nodeI]);
        int tm = (tl + tr) / 2;
        if (qr <= tm) {
            Node left = _query(2 * nodeI, tl, tm, ql, qr);
            return left;
        } else if (ql >= tm + 1) {
            Node right = _query(2 * nodeI + 1, tm + 1, tr, ql, qr);
            return right;
        }
        Node left = _query(2 * nodeI, tl, tm, ql, qr);
        Node right = _query(2 * nodeI + 1, tm + 1, tr, ql, qr);
        return _combine(left, right);
    }

    Node query(int l, int r) {
        return _query(1, 0, n - 1, l, r);
    }

    Tag _compose(Tag old, Tag newT) {
        Tag out;
        for (int b = 0; b < LOG; b++) {
            out.flipped[b] = old.flipped[b] ^ newT.flipped[b];
        }
        return out;
    }

    void _applyTagToNodeAndCompose(int nodeI, Tag t) {
        Node& node = tree[nodeI];
        for (int b = 0; b < LOG; b++) {
            if (t.flipped[b]) {
                node.cnt[b] = node.width - node.cnt[b];
            }
        }
        lazy[nodeI] = _compose(lazy[nodeI], t);
    }

    void _rangeDiff(int nodeI, int tl, int tr, int ql, int qr, int xorNum) {
        // oob
        if (qr < tl || ql > tr) {
            return;
        }
        // fully inside, put tag
        if (ql <= tl && qr >= tr) {
            Tag t;
            for (int b = 0; b < LOG; b++) {
                if ((1 << b) & xorNum) {
                    t.flipped[b] = true;
                }
            }
            _applyTagToNodeAndCompose(nodeI, t);
            return;
        }
        _pushDownAndClear(nodeI, lazy[nodeI]);
        int tm = (tl + tr) / 2;
        _rangeDiff(2 * nodeI, tl, tm, ql, qr, xorNum);
        _rangeDiff(2 * nodeI + 1, tm + 1, tr, ql, qr, xorNum);
        _pull(nodeI);
    }

    void rangeDiff(int l, int r, int xorNum) {
        _rangeDiff(1, 0, n - 1, l, r, xorNum);
    }
};

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n; cin >> n;
    vector<int> A(n); for (int i = 0; i < n; i++) cin >> A[i];
    Seg seg(A);
    int m; cin >> m;
    while (m--) {
        int qtype; cin >> qtype;
        if (qtype == 1) {
            int l, r; cin >> l >> r; l--; r--;
            Node agg = seg.query(l, r);
            ll out = 0;
            for (int b = 0; b < LOG; b++) {
                out += (ll)(1 << b) * agg.cnt[b];
            }
            cout << out << endl;
        } else {
            int l, r, x; cin >> l >> r >> x; l--; r--;
            seg.rangeDiff(l, r, x);
        }
    }

}