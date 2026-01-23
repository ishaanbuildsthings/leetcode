
#include <bits/stdc++.h>
using namespace std;

struct ContiguousSeg {
    struct Node {
        int maxRange = 0;
        int leftNum;
        int rightNum;
        int prefConsec;
        int suffConsec;
        int width;
    };
    vector<int> A;
    vector<Node> tree;
    int n;
    ContiguousSeg(const vector<int>& _A) {
        A = _A;
        n = A.size();
        tree.resize(4 * n + 5);
        build();
    }
    void build() {
        _build(1, 0, n - 1);
    }
    Node makeLeaf(int val) {
        return Node{1, val, val, 1, 1, 1};
    }
    void _build(int i, int tl, int tr) {
        if (tl == tr) {
            tree[i] = makeLeaf(A[tl]);
            return;
        }
        int tm = (tr + tl) / 2;
        _build(2 * i, tl, tm);
        _build(2 * i + 1, tm + 1, tr);
        pull(i);
    }
    Node merge(Node& left, Node& right) {
        int nmax = max(left.maxRange, right.maxRange);
        if (left.rightNum == right.leftNum) {
            nmax = max(nmax, left.suffConsec + right.prefConsec);
        }
        int nleft = left.leftNum;
        int nright = right.rightNum;
        int nwidth = left.width + right.width;
        int npref = left.prefConsec;
        if (npref == left.width && right.leftNum == left.rightNum) {
            npref += right.prefConsec;
        }
        int nsuff = right.suffConsec;
        if (nsuff == right.width && right.leftNum == left.rightNum) {
            nsuff += left.suffConsec;
        }
        return Node{nmax, nleft, nright, npref, nsuff, nwidth};
    }
    void pull(int i) {
        tree[i] = merge(tree[2*i],tree[2*i+1]);
    }
    Node query(int l, int r) {
        auto Node = _query(1, 0, n - 1, l, r);
        return Node;
    }
    Node queryAll() {
        return tree[1];
    }
    Node _query(int i, int tl, int tr, int ql, int qr) {
        // fully contained
        if (ql <= tl && qr >= tr) {
            return tree[i];
        }
        int tm = (tr + tl) / 2;
        // only left
        if (qr <= tm) {
            return _query(2 * i, tl, tm, ql, qr);
        }
        // only right
        if (ql >= tm + 1) {
            return _query(2 * i + 1, tm + 1, tr, ql, qr);
        }
        // both
        Node left =_query(2 * i, tl, tm, ql, qr);
        Node right = _query(2 * i + 1, tm + 1, tr, ql, qr);
        return merge(left, right);
    }
    void pointAssign(int pos, int newV) {
        _pointAssign(1, 0, n - 1, pos, newV);
    }
    void _pointAssign(int i, int tl, int tr, int pos, int newV) {
        if (tl == tr) {
            tree[i] = makeLeaf(newV);
            return;
        }
        int tm = (tr + tl) / 2;
        if (pos <= tm) {
            _pointAssign(2 * i, tl, tm, pos, newV);
        } else {
            _pointAssign(2 * i + 1, tm + 1, tr, pos, newV);
        }
        pull(i);
    }
};

int main() {
    cin.tie(nullptr);
    ios::sync_with_stdio(false);
    string s; cin >> s;
    vector<int> arr;
    for (int i = 0; i < s.size(); i++) {
        if (s[i] == '1') {
            arr.push_back(1);
        } else {
            arr.push_back(0);
        }
    }
    ContiguousSeg seg = ContiguousSeg(arr);
    int m; cin >> m;
    for (int i = 0; i < m; i++) {
        int x; cin >> x; x--;
        int old = seg.query(x, x).leftNum;
        int newBit = old ^ 1;
        seg.pointAssign(x, newBit);
        cout << seg.queryAll().maxRange << " ";
    }
}