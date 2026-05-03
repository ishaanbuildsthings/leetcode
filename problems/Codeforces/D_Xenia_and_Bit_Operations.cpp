#include <bits/stdc++.h>
using namespace std;
using ll = long long;

struct Node {
    int val = 0;
};
struct Seg {
    int n;
    int height;
    vector<Node> tree;
    Seg(const vector<int>& A, int _height) {
        n = A.size();
        height = _height;
        tree.resize(4 * n);
        _build(1, 0, n - 1, 0, A);
    }
    void _pull(int nodeI, int depth) {
        Node& left = tree[2*nodeI];
        Node& right = tree[2*nodeI + 1];
        if ((height - depth) % 2) {
            tree[nodeI] = {left.val | right.val};
        } else {
            tree[nodeI] = {left.val ^ right.val};
        }
    }
    // if height is 3:
    //      1
    //   2   3
    // 4 5  7 8
    // at depth 2 we do ORs
    // so if height - depth % 2, we do an OR
    void _build(int nodeI, int tl, int tr, int depth, const vector<int>& A) {
        if (tl == tr) {
            tree[nodeI] = {A[tl]};
            return;
        }
        int tm = (tl + tr) / 2;
        _build(2 * nodeI, tl, tm, depth + 1, A);
        _build(2 * nodeI + 1, tm + 1, tr, depth + 1, A);
        _pull(nodeI, depth);
    }

    void pointUpdate(int pos, int newVal) {
        _pointUpdate(1, 0, n - 1, 0, pos, newVal);
    }

    void _pointUpdate(int nodeI, int tl, int tr, int depth, int pos, int newVal) {
        if (tl == tr) {
            tree[nodeI] = {newVal};
            return;
        }
        int tm = (tl + tr) / 2;
        if (pos <= tm) {
            _pointUpdate(2 * nodeI, tl, tm, depth + 1, pos, newVal);
        } else {
            _pointUpdate(2 * nodeI + 1, tm + 1, tr, depth + 1, pos, newVal);
        }
        _pull(nodeI, depth);
    };

    Node queryAll() {
        return tree[1];
    }
};

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m; cin >> n >> m;
    int N = 1 << n;
    vector<int> A(N); for (int i = 0; i < N; i++) cin >> A[i];
    Seg seg(A, n);
    for (int i = 0; i < m; i++) {
        int p, b; cin >> p >> b; p--;
        seg.pointUpdate(p, b);
        cout << seg.queryAll().val << '\n';
    }
}