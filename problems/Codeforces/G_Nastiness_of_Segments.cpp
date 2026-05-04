#include <bits/stdc++.h>
using namespace std;
using ll = long long;

struct Node {
    int mn = 0;
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
        return {min(a.mn, b.mn)};
    }

    void _build(int nodeI, int tl, int tr, vector<int>& A) {
        if (tl == tr) {
            tree[nodeI] = {A[tl]};
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
            tree[nodeI] = {newVal};
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

#include <bits/stdc++.h>
using namespace std;
using ll = long long;

void solve() {
    int n, q; cin >> n >> q;
    vector<int> A(n); for (int i = 0; i < n; i++) cin >> A[i];
    Seg seg(A);
    while (q--) {
        int qtype; cin >> qtype;
        if (qtype == 1) {
            int i, newVal; cin >> i >> newVal; i--;
            seg.pointUpdate(i, newVal);
        } else {
            int l, r; cin >> l >> r; l--; r--;
            // we need to locate the leftmost prefix in l...r where the min equals width minus one
            int LEFT = l;
            int RIGHT = r;
            int LEFT_RES = -1;
            while (LEFT <= RIGHT) {
                int m = (LEFT + RIGHT) / 2;
                // pf is l...m
                int min = seg.query(l, m).mn;
                int width = m - l + 1;
                if (min == width - 1) {
                    LEFT_RES = m;
                    RIGHT = m - 1;
                } else if (min < width - 1) {
                    RIGHT = m - 1;
                } else {
                    LEFT = m + 1;
                }
            }
            if (LEFT_RES == -1) {
                cout << 0 << '\n';
                continue;
            }
            LEFT = LEFT_RES;
            RIGHT = r;
            int RIGHT_RES = -1;
            while (LEFT <= RIGHT) {
                int m = (LEFT + RIGHT) / 2;
                // pf is l...m
                int min = seg.query(l, m).mn;
                int width = m - l + 1;
                if (min == width - 1) {
                    RIGHT_RES = m;
                    LEFT = m + 1;
                } else if (min < width - 1) {
                    RIGHT = m - 1;
                } else {
                    LEFT = m + 1;
                }
            }
            cout << RIGHT_RES - LEFT_RES + 1 << '\n';
        }
    }
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int t; cin >> t;
    while (t--) solve();
}