#include <bits/stdc++.h>
using namespace std;
using ll = long long;

struct Node {
    int deliverLeft = 0;
    int deliverRight = 0;
    int length = 1;
};

struct Seg {
    int n;
    vector<Node> tree;
    Seg(const vector<int>& A) {
        n = A.size();
        tree.resize(4 * n);
        _build(1, 0, n - 1, A);
    }
    Node agg(Node& a, Node& b) {
        int newDeliverLeft = min(a.deliverLeft, a.length + b.deliverLeft);
        int newDeliverRight = min(b.deliverRight, b.length + a.deliverRight);
        int newLength = a.length + b.length;
        return {newDeliverLeft, newDeliverRight, newLength};
    }
    void _pull(int nodeI) {
        Node& left = tree[2 * nodeI];
        Node& right = tree[2 * nodeI + 1];
        tree[nodeI] = agg(left, right);
    }
    void _build(int nodeI, int tl, int tr, const vector<int>& A) {
        if (tl == tr) {
            tree[nodeI] = {A[tl], A[tr], 1};
            return;
        }
        int tm = (tl + tr) / 2;
        _build(2 * nodeI, tl, tm, A);
        _build(2 * nodeI + 1, tm + 1, tr, A);
        _pull(nodeI);
    }
    void _pointUpdate(int nodeI, int tl, int tr, int i, int newVal) {
        if (tl == tr) {
            tree[nodeI] = {newVal, newVal, 1};
            return;
        }
        int tm = (tl + tr) / 2;
        if (i <= tm) _pointUpdate(2 * nodeI, tl, tm, i, newVal);
        else _pointUpdate(2 * nodeI + 1, tm + 1, tr, i, newVal);
        _pull(nodeI);
    }
    void pointUpdate(int i, int newVal) {
        _pointUpdate(1, 0, n - 1, i, newVal);
    };
    Node _query(int nodeI, int tl, int tr, int ql, int qr) {
        if (tl == tr) return tree[nodeI];
        if (ql <= tl && qr >= tr) return tree[nodeI];
        int tm = (tl + tr) / 2;
        if (qr <= tm) return _query(2 * nodeI, tl, tm, ql, qr);
        if (ql >= tm + 1) return _query(2 *nodeI + 1, tm + 1, tr, ql, qr);
        Node left = _query(2 * nodeI, tl, tm, ql, qr);
        Node right = _query(2 *nodeI + 1, tm + 1, tr, ql, qr);
        return agg(left, right);
        
    }
    Node query(int l, int r) {
        return _query(1, 0, n - 1, l, r);
    }

};

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, q; cin >> n >> q;
    vector<int> A(n); for (int i = 0; i < n; i++) cin >> A[i];
    Seg st(A);
    for (int i = 0; i < q; i++) {
        int qtype; cin >> qtype;
        if (qtype == 1) {
            int pos, newPrice; cin >> pos >> newPrice; pos--;
            st.pointUpdate(pos, newPrice);
        } else {
            int pos; cin >> pos; pos--; // find min price to deliver here
            Node ans1 = st.query(pos, n - 1);
            Node ans2 = st.query(0, pos);
            cout << min(ans1.deliverLeft, ans2.deliverRight) << '\n';
        }
    }
    
}