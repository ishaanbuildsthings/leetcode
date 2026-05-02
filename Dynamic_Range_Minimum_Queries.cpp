#include <bits/stdc++.h>
using namespace std;
using ll = long long;

struct MinSeg {
    int n;
    vector<ll> tree;

    MinSeg(const vector<ll>& A) {
        n = A.size();
        tree.resize(4 * n);
        _build(1, 0, n - 1, A);
    }

    void _build(int nodeI, int tl, int tr, const vector<ll>& A) {
        if (tl == tr) {
            tree[nodeI] = A[tl];
            return;
        }
        int tm = (tl + tr) / 2;
        _build(2 * nodeI, tl, tm, A);
        _build(2 * nodeI + 1, tm + 1, tr, A);
        tree[nodeI] = min(tree[2*nodeI], tree[2*nodeI + 1]);
    }

    void _pointUpdate(int nodeI, int tl, int tr, int pos, int newVal) {
        if (tl == tr) {
            tree[nodeI] = newVal;
            return;
        }
        int tm = (tl + tr) / 2;
        if (pos <= tm) {
            _pointUpdate(2 * nodeI, tl, tm, pos, newVal);
        } else {
            _pointUpdate(2 * nodeI + 1, tm + 1, tr, pos, newVal);
        }
        tree[nodeI] = min(tree[2*nodeI], tree[2*nodeI + 1]);
    }

    void pointUpdate(int pos, int newVal) {
        _pointUpdate(1, 0, n - 1, pos, newVal);
    }

    ll _query(int nodeI, int tl, int tr, int ql, int qr) {
        if (ql <= tl && qr >= tr) {
            return tree[nodeI];
        }
        int tm = (tl + tr) / 2;
        if (qr <= tm) {
            return _query(2 * nodeI, tl, tm, ql, qr);
        } else if (ql >= tm + 1) {
            return _query(2 * nodeI + 1, tm + 1, tr, ql, qr);
        }
        ll left = _query(2 * nodeI, tl, tm, ql, qr);
        ll right = _query(2 * nodeI + 1, tm + 1, tr, ql, qr);
        return min(left, right);
    }

    ll query(int l, int r) {
        return _query(1, 0, n - 1, l, r);
    }
};

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, q; cin >> n >> q;
    vector<ll> A(n); for (int i = 0; i < n; i++) cin >> A[i];
    MinSeg seg(A);
    for (int i = 0; i < q; i++) {
        int qtype, a, b; cin >> qtype >> a >> b;
        if (qtype == 1) {
            seg.pointUpdate(a - 1, b);
        } else {
            cout << seg.query(a - 1, b - 1) << '\n';
        }
    }
}