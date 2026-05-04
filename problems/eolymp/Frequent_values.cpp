#include <bits/stdc++.h>
using namespace std;
using ll = long long;

struct Node {
    int longestBlock = 0;
    int suffVal = 0;
    int prefVal = 0;
    int suffContiguous = 0;
    int prefContiguous = 0;
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
        int nblock = max(a.longestBlock, b.longestBlock);
        if (a.suffVal == b.prefVal) {
            int opt = a.suffContiguous + b.prefContiguous;
            nblock = max(nblock, opt);
        }
        int npref = a.prefVal;
        int nsuff = b.suffVal;
        int nsuffcont = b.suffContiguous;
        if (a.suffVal == b.suffVal) {
            nsuffcont += a.suffContiguous;
        }
        int nprefcont = a.prefContiguous;
        if (a.prefVal == b.prefVal) {
            nprefcont += b.prefContiguous;
        }
        return {nblock, nsuff, npref, nsuffcont, nprefcont};
    }

    void _build(int nodeI, int tl, int tr, vector<int>& A) {
        if (tl == tr) {
            tree[nodeI] = {1, A[tl], A[tl], 1, 1};
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
            tree[nodeI] = {1, newVal, newVal, 1, 1};
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

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n;
    while (cin >> n && n != 0) {
        int q; cin >> q;
        vector<int> A(n);
        for (int i = 0; i < n; i++) cin >> A[i];
        Seg seg(A);
        for (int i = 0; i < q; i++) {
            int l, r; cin >> l >> r; l--; r--;
            cout << seg.query(l, r).longestBlock << '\n';
        }
    }
}