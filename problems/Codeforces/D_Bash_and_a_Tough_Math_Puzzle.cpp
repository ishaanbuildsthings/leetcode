#include <bits/stdc++.h>
using namespace std;
using ll = long long;

struct GCDSeg {
    int n;
    vector<ll> tree;

    void _build(int nodeI, int tl, int tr, const vector<ll>& A) {
        if (tl == tr) {
            tree[nodeI] = A[tl];
            return;
        }
        int tm = (tl + tr) / 2;
        _build(2 * nodeI, tl, tm, A);
        _build(2 * nodeI + 1, tm + 1, tr, A);
        tree[nodeI] = gcd(tree[2*nodeI], tree[2*nodeI + 1]);
    }

    
    GCDSeg(const vector<ll>& A) {
        n = A.size();
        tree.resize(4 * n);
        _build(1, 0, n - 1, A);
    }

    void _pointSet(int nodeI, int tl, int tr, int pos, int newVal) {
        if (tl == tr) {
            tree[nodeI] = newVal;
            return;
        }
        int tm = (tl + tr) / 2;
        if (pos <= tm) {
            _pointSet(2 * nodeI, tl, tm, pos, newVal);
        } else {
            _pointSet(2 * nodeI + 1, tm + 1, tr, pos, newVal);
        }
        tree[nodeI] = gcd(tree[2*nodeI], tree[2*nodeI + 1]);
    };

    void pointSet(int pos, int newVal) {
        _pointSet(1, 0, n - 1, pos, newVal);
    }

    ll _query(int nodeI, int tl, int tr, int ql, int qr) {
        // fully contained
        if (ql <= tl and qr >= tr) {
            return tree[nodeI];
        }
        // oob
        if (qr < tl or ql > tr) {
            return 0;
        }
        int tm = (tl + tr) / 2;
        ll left = _query(2 * nodeI, tl, tm, ql, qr);
        ll right = _query(2 * nodeI + 1, tm + 1, tr, ql, qr);
        return gcd(left, right);
    }

    ll query(int l, int r) {
        return _query(1, 0, n - 1, l, r);
    }

    int _countOffenders(int nodeI, int tl, int tr, int ql, int qr, int x) {
        // if out of bounds, stop
        if (qr < tl or ql > tr) return 0;
        if (tl == tr) {
            if (tree[nodeI] % x == 0) {
                return 0;
            }
            return 1;
        }
        if (tree[nodeI] % x == 0) return 0;
        // now there is at least 1 bad element in the segment, we want to find how many exactly so recurse down
        int tm = (tl + tr) / 2;
        int left = _countOffenders(2 * nodeI, tl, tm, ql, qr, x);
        if (left >= 2) return 2;
        int right = _countOffenders(2 * nodeI + 1, tm + 1, tr, ql, qr, x);
        return left + right;
    }

    int countOffenders(int l, int r, int x) {
        return _countOffenders(1, 0, n - 1, l, r, x);
    }
};

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n; cin >> n;
    vector<ll> A(n); for (int i = 0; i < n; i++) cin >> A[i];
    GCDSeg st(A);
    int q; cin >> q;
    for (int i = 0; i < q; i++) {
        int qtype; cin >> qtype;
        if (qtype == 1) {
            int l, r, x; cin >> l >> r >> x;
            l--; r--;
            // specifically counts the # of array elements not a multiple of X
            int offenders = st.countOffenders(l, r, x);
            // offenders = 0 means everything was a multiple of X, we can set any element to X to make that the GCD
            // offenders = 1 means we can change that single element
            cout << (offenders <= 1 ? "YES" : "NO") << '\n';
        } else {
            int idx, newVal; cin >> idx >> newVal; idx--;
            st.pointSet(idx, newVal);
        }
    }
}