// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/golden-references/PersistentSegTree.cpp
#include<bits/stdc++.h>
using namespace std;
using ll = long long;

struct Node {
    Node* l;
    Node* r;
    ll tot;
};

struct Seg {
    int n;
    Node* root;
    Seg(const vector<int>& A) {
        n = A.size();
        root = _build(0, n - 1, A);
    }

    Node* leaf(ll v) {
        return new Node{nullptr,nullptr,v};
    }

    Node* agg(Node* left, Node* right) {
        return new Node({left, right, left->tot + right->tot});
    }

    Node* _build(int tl, int tr, const vector<int>& A) {
        if (tl == tr) {
            return leaf(A[tl]);
        }
        int tm = (tl + tr) / 2;
        Node* left = _build(tl, tm, A);
        Node* right = _build(tm + 1, tr, A);
        return agg(left, right);
    }

    void pointUpdate(int i, ll newV) {
        root = _pointUpdate(i, newV, root, 0, n - 1);
    }

    Node* _pointUpdate(int i, ll newV, Node* node, int tl, int tr) {
        if (tl == tr) {
            return leaf(newV);
        }
        Node* left = node->l;
        Node* right = node->r;
        int tm = (tl + tr) / 2;
        if (i <= tm) {
            left = _pointUpdate(i, newV, node->l, tl, tm);
        } else {
            right = _pointUpdate(i, newV, node->r, tm + 1, tr);
        }
        return agg(left, right);
    }

    ll rangeSum(int l, int r) {
        return _rangeSum(l, r, 0, n - 1, root);
    }

    ll _rangeSum(int l, int r, int tl, int tr, Node* node) {
        if (l > tr || r < tl) return 0;
        if (l <= tl && r >= tr) return node->tot;
        int tm = (tl + tr) / 2;
        return _rangeSum(l, r, tl, tm, node->l) + _rangeSum(l, r, tm + 1, tr, node->r);
    }
};

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, q; cin >> n >> q;
    vector<int> A(n); for (int i = 0; i < n; i++) cin >> A[i];
    vector<Seg> segs = {Seg(A)};
    for (int i = 0; i < q; i++) {
        int qtype; cin >> qtype;
        if (qtype == 1) {
            int k, a, x; cin >> k >> a >> x;
            segs[k - 1].pointUpdate(a - 1, x);
        } else if (qtype == 2) {
            int k, a, b; cin >> k >> a >> b;
            cout << segs[k - 1].rangeSum(a - 1, b - 1) << '\n';
        } else {
            int k; cin >> k;
            Seg copy = segs[k - 1];
            segs.push_back(copy);
        }
    }
}
