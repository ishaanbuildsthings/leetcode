#include <bits/stdc++.h>
using namespace std;
using ll = long long;

struct Data {
    ll total = 0;
    int width = 1;
};

struct Tag {
    ll add = 0;
    ll assign = -1; // -1 means no pending assignment
    // if we have an assignment and an add, it means assign first
};

struct Seg {
    int n;
    vector<Data> tree;
    vector<Tag> lazy;

    Seg(const vector<ll>& A) {
        n = A.size();
        tree.resize(4 * n);
        lazy.resize(4 * n);
        _build(1, 0, n - 1, A);
    }

    void _build(int nodeI, int tl, int tr, const vector<ll>& A) {
        if (tl == tr) {
            tree[nodeI] = {A[tl], 1};
            return;
        }
        int tm = (tl + tr) / 2;
        _build(2 * nodeI, tl, tm, A);
        _build(2 * nodeI + 1, tm + 1, tr, A);
        _pull(nodeI);
    }

    void _pull(int nodeI) {
        Data& left = tree[2 * nodeI];
        Data& right = tree[2 * nodeI + 1];
        Data newData = _combine(left, right);
        tree[nodeI] = newData;
    }

    Data _combine(Data a, Data b) {
        return {a.total + b.total, a.width + b.width};
    }

    Tag _compose(Tag oldT, Tag newT) {
        if (newT.assign != -1) {
            return newT;
        }
        oldT.add += newT.add;
        return oldT;
    }

    void _applyAndUpdateLazy(int nodeI, Tag t) {
        Data& d = tree[nodeI];
        // if our incoming tag doesn't have an assign, we can just add on the range value
        if (t.assign == -1) {
            ll gain = (ll)d.width * t.add;
            d.total += gain;
            lazy[nodeI] = _compose(lazy[nodeI], t);
            return;
        }
        // if we had an assign (and potentially an add, we can compute a new total)
        ll assignedTotal = (ll)d.width * t.assign;
        ll incTotal = (ll)d.width * t.add;
        d.total = assignedTotal + incTotal;
        lazy[nodeI] = _compose(lazy[nodeI], t);
    }

    void _pushTagDownAndClear(int nodeI) {
        Tag t = lazy[nodeI];
        if (2 * nodeI < 4 * n) {
            _applyAndUpdateLazy(2 * nodeI, t);
        }
        if (2 * nodeI + 1 < 4 * n) {
            _applyAndUpdateLazy(2 * nodeI + 1, t);
        }
        lazy[nodeI] = {0, -1};
    }

    void _rangeInc(int nodeI, int tl, int tr, int ql, int qr, ll diff) {
        // if out of bounds, return
        if (qr < tl || ql > tr) {
            return;
        }
        Tag incoming = {diff, -1};
        // if fully contained, operate now
        if (tl >= ql && tr <= qr) {
            _applyAndUpdateLazy(nodeI, incoming);
            return;
        }
        _pushTagDownAndClear(nodeI);
        int tm = (tl + tr) / 2;
        _rangeInc(2 * nodeI, tl, tm, ql, qr, diff);
        _rangeInc(2 * nodeI + 1, tm + 1, tr, ql, qr, diff);
        _pull(nodeI);
    }

    void _rangeAssign(int nodeI, int tl, int tr, int ql, int qr, ll newVal) {
        // if out of bounds, return
        if (qr < tl || ql > tr) {
            return;
        }
        Tag incoming = {0, newVal};
        // if fully contained, operate now
        if (tl >= ql && tr <= qr) {
            _applyAndUpdateLazy(nodeI, incoming);
            return;
        }
        _pushTagDownAndClear(nodeI);
        int tm = (tl + tr) / 2;
        _rangeAssign(2 * nodeI, tl, tm, ql, qr, newVal);
        _rangeAssign(2 * nodeI + 1, tm + 1, tr, ql, qr, newVal);
        _pull(nodeI);
    }

    Data _query(int nodeI, int tl, int tr, int ql, int qr) {
        // fully contained
        if (tl >= ql && tr <= qr) {
            return tree[nodeI];
        }
        _pushTagDownAndClear(nodeI);
        int tm = (tl + tr) / 2;
        if (qr <= tm) {
            Data left = _query(2 * nodeI, tl, tm, ql, qr);
            return left;
        }
        if (ql >= tm + 1) {
            Data right = _query(2 * nodeI + 1, tm + 1, tr, ql, qr);
            return right;
        }
        Data left = _query(2 * nodeI, tl, tm, ql, qr);
        Data right = _query(2 * nodeI + 1, tm + 1, tr, ql, qr);
        return _combine(left, right);
    }

    // ========== PUBLIC API ==========

    void rangeInc(int l, int r, ll diff) {
        _rangeInc(1, 0, n - 1, l, r, diff);
    }

    void rangeAssign(int l, int r, ll newVal) {
        _rangeAssign(1, 0, n - 1, l, r, newVal);
    }

    Data query(int l, int r) {
        return _query(1, 0, n - 1, l, r);
    }
};

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, q; cin >> n >> q;
    vector<ll> A(n); for (int i = 0; i < n; i++) cin >> A[i];
    Seg seg(A);
    for (int i = 0; i < q; i++) {
        int opType; cin >> opType;
        if (opType == 1) {
            int a, b, gain; cin >> a >> b >> gain; a--; b--; 
            seg.rangeInc(a, b, gain);
        } else if (opType == 2) {
            int a, b, assigned; cin >> a >> b >> assigned; a--; b--;
            seg.rangeAssign(a, b, assigned);
        } else {
            int a, b; cin >> a >> b; a--; b--;
            cout << seg.query(a, b).total << '\n';
        }
    }
}