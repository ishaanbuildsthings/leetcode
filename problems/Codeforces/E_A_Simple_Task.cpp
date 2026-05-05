#include <bits/stdc++.h>
using namespace std;
using ll = long long;
constexpr int ALPHA = 26;

struct Node {
    int cnt[ALPHA] = {};
    int width = 0;
};

struct Tag {
    char lazyAssign = -1; // -1 is a sentinel, otherwise 0 means assign this range to A, 1 to B, etc
};

struct Seg {
    int n;
    vector<Node> tree;
    vector<Tag> lazy;
    void _build(int nodeI, int tl, int tr, string& s) {
        if (tl == tr) {
            char c = s[tl];
            int idx = c - 'a';
            tree[nodeI].cnt[idx]++;
            tree[nodeI].width = 1;
            return;
        }
        int tm = (tl + tr) / 2;
        _build(2 * nodeI, tl, tm, s);
        _build(2 * nodeI + 1, tm + 1 , tr, s);
        _pull(nodeI);
    }
    void _pull(int nodeI) {
        tree[nodeI] = _combine(tree[2*nodeI],tree[2*nodeI+1]);
    }
    Node _combine(Node& a, Node&b) {
        Node out;
        for (int i = 0; i < ALPHA; i++) {
            out.cnt[i] = a.cnt[i] + b.cnt[i];
        }
        out.width = a.width + b.width;
        return out;
    }
    Seg(string& s) {
        n = s.size();
        tree.resize(4 * n);
        lazy.resize(4 * n);
        _build(1, 0, n - 1, s);
    }
    Tag _compose(Tag& a, Tag& b) {
        return b;
    }
    void _applyTagAndCompose(int nodeI, Tag t) {
        if (t.lazyAssign == -1) return;
        Node& node = tree[nodeI];
        for (int i = 0; i < ALPHA; i++) {
            if (i == t.lazyAssign) {
                node.cnt[i] = node.width;
            } else {
                node.cnt[i] = 0;
            }
        }
        lazy[nodeI] = _compose(lazy[nodeI], t);
    }
    void _pushDownAndClear(int nodeI) {
        _applyTagAndCompose(2 * nodeI, lazy[nodeI]);
        _applyTagAndCompose(2 * nodeI + 1, lazy[nodeI]);
        lazy[nodeI] = {-1};
    }
    Node _query(int nodeI, int tl, int tr, int ql, int qr) {
        // fully inside
        if (ql <= tl && qr >= tr) {
            return tree[nodeI];
        }
        _pushDownAndClear(nodeI);
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
    void _rangeAssign(int nodeI, int tl, int tr, int ql, int qr, int newIdx) {
        // oob
        if (qr < tl || ql > tr) return;
        // fully inside
        if (ql <= tl && qr >= tr) {
            Tag t; t.lazyAssign = newIdx;
            _applyTagAndCompose(nodeI, t);
            return;
        }
        _pushDownAndClear(nodeI);
        int tm = (tl + tr) / 2;
        _rangeAssign(2 * nodeI, tl, tm, ql, qr, newIdx);
        _rangeAssign(2 * nodeI + 1, tm + 1, tr, ql, qr, newIdx);
        _pull(nodeI);
    }
    void rangeAssign(int l, int r, int idx) {
        _rangeAssign(1, 0, n - 1, l, r, idx);
    }
};

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, q; cin >> n >> q;
    string s; cin >> s;
    Seg seg(s);
    while (q--) {
        int l, r, qtype; cin >> l >> r >> qtype; l--; r--;
        Node counts = seg.query(l, r);
        int currL = l;
        if (qtype == 1) {
            for (int idx = 0; idx < ALPHA; idx++) {
                if (counts.cnt[idx] == 0) {
                    continue;
                }
                int right = currL + counts.cnt[idx] - 1;
                seg.rangeAssign(currL, right, idx);
                currL = right + 1;
            }
        } else {
            for (int idx = ALPHA - 1; idx >= 0; idx--) {
                if (counts.cnt[idx] == 0) {
                    continue;
                }
                int right = currL + counts.cnt[idx] - 1;
                seg.rangeAssign(currL, right, idx);
                currL = right + 1;
            }         
        }
    }
    string out(n, '?');
    for (int i = 0; i < n; i++) {
        Node leaf = seg.query(i, i);
        for (int c = 0; c < ALPHA; c++) {
            if (leaf.cnt[c]) {
                out[i] = 'a' + c; break;
            }
        }
    }
    cout << out << endl;

}