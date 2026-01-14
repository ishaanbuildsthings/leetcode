#include <bits/stdc++.h>
using namespace std;

struct MaxSeg {
    vector<int> A;
    int n;
    struct Node {
        int max;
    };
    vector<Node> tree;
    MaxSeg(const vector<int>& _A) {
        A = _A;
        n = A.size();
        tree.resize(4 * n + 5);
        build();
    }
    Node merge(Node& left, Node& right) {
        return Node{max(left.max, right.max)};
    }
    void build() {
        _build(1, 0, n - 1);
    }
    void _build(int i, int tl, int tr) {
        if (tl == tr) {
            tree[i] = Node{A[tl]};
            return;
        }
        int tm = (tr + tl) / 2;
        _build(2 * i, tl, tm);
        _build(2 * i + 1, tm + 1, tr);
        pull(i);
    }
    void pull(int i) {
        tree[i] = merge(tree[2 * i], tree[2 * i + 1]);
    }
    void pointSubtract(int pos, int diff) {
        _pointSubtract(1, 0, n - 1, pos, diff);
    }
    void _pointSubtract(int i, int tl, int tr, int pos, int diff) {
        if (tl == tr) {
            tree[i] = Node{tree[i].max - diff};
            return;
        }
        int tm = (tr + tl) / 2;
        if (pos <= tm) {
            _pointSubtract(2 * i, tl, tm, pos, diff);
        } else {
            _pointSubtract(2 * i + 1, tm + 1, tr, pos, diff);
        }
        pull(i);
    }
    int leftmostIdxGteX(int x) {
        return _leftmostIdxGteX(1, 0, n - 1, x);
    }
    int _leftmostIdxGteX(int i, int tl, int tr, int x) {
        if (tree[i].max < x) return -1;
        if (tl == tr) {
            return tl;
        }
        int tm = (tr + tl) / 2;
        if (tree[2 * i].max >= x) {
            return _leftmostIdxGteX(2 * i, tl, tm, x);
        } else {
            return _leftmostIdxGteX(2 * i + 1, tm + 1, tr, x);
        }
    }
};
int main() {
    int n, q; cin >> n >> q;
    vector<int> A(n); for (int i = 0; i < n; i++) cin >> A[i];
    MaxSeg st(A);
    for (int i = 0; i < q; i++) {
        int v; cin >> v;
        int leftmost = st.leftmostIdxGteX(v);
        cout << (leftmost == -1 ? 0 : leftmost + 1) << " ";
        if (leftmost != -1) {
            st.pointSubtract(leftmost, v);
        }
    }
}