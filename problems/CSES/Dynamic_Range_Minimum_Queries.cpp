#include <bits/stdc++.h>
using namespace std;

struct Seg {

    struct Node {
        int min;
    };

    vector<int> A; // original array
    vector<Node> tree;

    Seg(vector<int> _A) {
        A = _A;
        tree.resize(A.size() * 4);
        build();
    }

    void build() {
        _build(1, 0, A.size() - 1);
    }

    void _build(int i, int tl, int tr) {
        if (tl == tr) {
            tree[i] = leaf(A[tl]);
            return;
        }
        int tm = (tl + tr) / 2;
        _build(2 * i, tl, tm);
        _build(2 * i + 1, tm + 1, tr);
        Node left = tree[2 * i];
        Node right = tree[2 * i + 1];
        tree[i] = merge(left, right);
    }

    Node leaf(int v) {
        return Node{v};
    };

    Node merge(Node l, Node r) {
        return Node{min(l.min, r.min)};
    };

    void update(int pos, int v) {
        _update(1, 0, A.size() - 1, pos, v);
    }

    void _update(int i, int tl, int tr, int pos, int v) {
        if (tl == tr) {
            tree[i] = leaf(v);
            return;
        }
        int tm = (tr + tl) / 2;
        if (pos <= tm) {
            _update(2 * i, tl, tm, pos, v);
        } else {
            _update(2 * i + 1, tm + 1, tr, pos, v);
        }

        Node left = tree[2 * i];
        Node right = tree[2 * i + 1];
        tree[i] = merge(left, right);
    }

    int query(int l, int r) {
        return _query(1, l, r, 0, A.size() - 1);
    }

    int _query(int i, int ql, int qr, int tl, int tr) {
        if (tl == tr) {
            return tree[i].min;
        }
        // If we are fully in range, return our own minimum
        if (tl >= ql && tr <= qr) {
            return tree[i].min;
        }
        int tm = (tr + tl) / 2;

        // If only left is in range
        if (qr <= tm) {
            return _query(2 * i, ql, qr, tl, tm);
        }

        // If only right is in range
        if (ql >= tm + 1) {
            return _query(2 * i + 1, ql, qr, tm + 1, tr);
        }

        int leftResult = _query(2 * i, ql, qr, tl, tm);
        int rightResult = _query(2 * i + 1, ql, qr, tm + 1, tr);
        return min(leftResult, rightResult);
    }  
};

int main() {
    int n, q; cin >> n >> q;
    vector<int> A(n);
    for (int i = 0; i < n; i++) cin >> A[i];
    Seg st = Seg(A);
    for (int i = 0; i < q; i++) {
        int op; cin >> op;
        if (op == 1) {
            int k, u; cin >> k >> u;
            k--;
            st.update(k, u);
        } else {
            int a, b; cin >> a >> b;
            a--; b--;
            cout << st.query(a, b) << endl;
        }
    }
}