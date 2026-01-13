#include <bits/stdc++.h>
using namespace std;

struct Seg {
    vector<int> A;

    struct Node {
        long long sum = 0;
        int lazyUpdates = 0;
    };
    vector<Node> tree;

    Seg(vector<int> _A) {
        A = _A;
        tree.resize(4 * A.size() + 5);
        build();
    }

    void build() {
        _build(1, 0, A.size() - 1);
    }

    Node leaf(int v) {
        return Node{v, 0};
    }

    void pull(int i) {
        Node left = tree[2 * i];
        Node right = tree[2 * i + 1];
        tree[i] = merge(left, right);
    }

    Node merge(Node left, Node right) {
        return Node{left.sum + right.sum, 0};
    }

    void _build(int i, int tl, int tr) {
        if (tl == tr) {
            tree[i] = leaf(A[tl]);
            return;
        }
        int tm = (tr + tl) / 2;
        _build(2 * i, tl, tm);
        _build(2 * i + 1, tm + 1, tr);
        pull(i);
    }

    void applyLazyUpdatesAndComposeLazies(int i, int adds) {
        long long curr = tree[i].sum;
        int usedAdds = adds;
        while (usedAdds-- > 0) {
            long long tempCurr = 0;
            while (curr > 0) {
                int lostDigit = curr % 10;
                tempCurr += lostDigit;
                curr /= 10;
            }
            curr = tempCurr;
            if (curr < 10) break;
        }
        tree[i].sum = curr;
        tree[i].lazyUpdates += adds;
    }

    void pushDownLaziesAndClearLaziesHere(int i, int tl, int tr) {
        if (tl == tr) return;
        applyLazyUpdatesAndComposeLazies(2 * i, tree[i].lazyUpdates);
        applyLazyUpdatesAndComposeLazies(2 * i + 1, tree[i].lazyUpdates);
        tree[i].lazyUpdates = 0;
    }

    long long queryTot(int l, int r) {
        return _queryTot(1, 0, A.size() - 1, l, r);
    }

    long long _queryTot(int i, int tl, int tr, int ql, int qr) {
        // cerr << "range query tot called on i, tl, tr, ql, qr: " << i << " " << tl << " " << tr << " " << ql << " " << qr << " " << endl;
        pushDownLaziesAndClearLaziesHere(i, tl, tr);

        if (ql <= tl && qr >= tr) {
            return tree[i].sum;
        }

        if (ql > tr || qr < tl) {
            return 0;
        }
        int tm = (tr + tl) / 2;
        long long left = _queryTot(2 * i, tl, tm, ql, qr);
        long long right = _queryTot(2 * i + 1, tm + 1, tr, ql, qr);
        return left + right;
    }

    void rangeUpdate(int l, int r) {
        _rangeUpdate(1, 0, A.size() - 1, l, r);
    }

    void _rangeUpdate(int i, int tl, int tr, int ql, int qr) {
        // cerr << "range update called on i, tl, tr, ql, qr " << i << tl << tr << ql << qr << endl;
        pushDownLaziesAndClearLaziesHere(i, tl, tr);

        // out of bounds
        if (ql > tr || qr < tl) {
            return;
        }

        // fully contained
        if (ql <= tl && qr >= tr) {
            applyLazyUpdatesAndComposeLazies(i, 1);
            return;
        }
        int tm = (tr + tl) / 2;
        _rangeUpdate(2 * i, tl, tm, ql, qr);
        _rangeUpdate(2 * i + 1, tm + 1, tr, ql, qr);
        pull(i);
    }

};

int main() {
    cin.tie(nullptr);
    ios::sync_with_stdio(false);
    int t; cin >> t;
    while (t--) {
        int n, q; cin >> n >> q;
        vector<int> A(n);
        for (int i = 0; i < n; i++) cin >> A[i];
        Seg st(A);
        for (int i = 0; i < q; i++) {
            int op; cin >> op;
            if (op == 1) {
                int l, r; cin >> l >> r;
                l--; r--;
                st.rangeUpdate(l, r);
            } else {
                int x; cin >> x; x--;
                cout << st.queryTot(x, x) << endl;
            }
        }
    }
}