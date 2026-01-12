#include <bits/stdc++.h>
using namespace std;

struct SegSum {

    struct Node {
        long long tot;
    };

    vector<long long> A;
    vector<Node> tree;

    SegSum(vector<long long> _A) {
        A = _A;
        tree.resize(4 * A.size());
        build();
    }

    void build() {
        _build(1, 0, A.size() - 1);
    }

    void _build(int i, int tl, int tr) {
        if (tl == tr) {
            tree[i] = Node{A[tl]};
            return;
        }
        int tm = (tr + tl) / 2;
        _build(2 * i, tl, tm);
        _build(2 * i + 1, tm + 1, tr);
        tree[i] = merge(tree[2*i], tree[2*i + 1]);
    }

    Node merge(Node a, Node b) {
        return Node{a.tot + b.tot};
    }

    long long sumQuery(int l, int r) {
        return _query(1, 0, A.size() - 1, l, r);
    }

    long long _query(int i, int tl, int tr, int ql, int qr) {
        if (ql > tr || qr < tl) {
            return 0;
        }
        if (ql <= tl && qr >= tr) {
            return tree[i].tot;
        }
        int tm = (tl + tr) / 2;
        return _query(2 * i, tl, tm, ql, qr) + _query(2 * i + 1, tm + 1, tr, ql, qr);
    }

    void update(int pos, int diff) {
        _update(1, pos, diff, 0, A.size() - 1);
    }

    void _update(int i, int pos, int diff, int tl, int tr) {
        if (tl == tr) {
            tree[i] = Node{diff + tree[i].tot};
            return;
        }
        int tm = (tr + tl) / 2;
        if (pos <= tm) {
            _update(2 * i, pos, diff, tl, tm);
        } else {
            _update(2 * i + 1, pos, diff, tm + 1, tr);
        }
        tree[i] = merge(tree[2*i], tree[2*i + 1]);
    }
};

int main() {
    cin.tie(nullptr);
    ios::sync_with_stdio(false);
    int n, q; cin >> n >> q;
    vector<int> A(n);
    for (int i = 0; i < n; i++) cin >> A[i];
    vector<long long> diff(n);
    SegSum st = SegSum(diff);
    for (int i = 0; i < q; i++) {
        int op; cin >> op;
        if (op == 1) {
            int a, b, u; cin >> a >> b >> u;
            a--; b--;
            st.update(a, u);
            if (b < n - 1) {
                st.update(b + 1, -u);
            }
        } else {
            int k; cin >> k; k--;
            cout << st.sumQuery(0, k) + A[k] << endl;
        }
    }
}