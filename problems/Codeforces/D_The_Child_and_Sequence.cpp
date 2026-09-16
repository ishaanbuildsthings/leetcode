#include <bits/stdc++.h>
using namespace std;
using ll = long long;

struct Node {
    int mx;
    ll tot;
};

struct Seg {
  vector<Node> tree;
  int n;
  
  Seg(const vector<int>& arr) {
    n = arr.size();
    tree.resize(4 * n);
    _build(1, 0, n - 1, arr);
  }

  Node _makeLeaf(int v) {
    return Node{v, v};
  }

  Node _agg(Node left, Node right) {
    return Node{max(left.mx, right.mx), left.tot + right.tot};
  }

  void _build(int nodeI, int tl, int tr, const vector<int>& arr) {
    if (tl == tr) {
        tree[nodeI] = _makeLeaf(arr[tl]);
        return;
    }
    int tm = (tl + tr) / 2;
    _build(2 * nodeI, tl, tm, arr);
    _build(2 * nodeI + 1, tm + 1, tr, arr);
    tree[nodeI] = _agg(tree[2 * nodeI], tree[2 * nodeI + 1]);
  }

  void _rangeMod(int nodeI, int tl, int tr, int ql, int qr, int mod) {
    // oob
    if (qr < tl || ql > tr) return;

    // leaf
    if (tl == tr) {
        int oldVal = tree[nodeI].mx;
        int newVal = oldVal % mod;
        tree[nodeI] = _makeLeaf(newVal);
        return;
    }

    Node& node = tree[nodeI];
    int tm = (tl + tr) / 2;

    // fully inside
    if (ql <= tl && qr >= tr) {
        if (node.mx < mod) return;
        _rangeMod(2 * nodeI, tl, tm, ql, qr, mod);
        _rangeMod(2 * nodeI + 1, tm + 1, tr, ql, qr, mod);
        tree[nodeI] = _agg(tree[2 * nodeI], tree[2 * nodeI + 1]);
        return;
    }

    // partial
    _rangeMod(2 * nodeI, tl, tm, ql, qr, mod);
    _rangeMod(2 * nodeI + 1, tm + 1, tr, ql, qr, mod);
    tree[nodeI] = _agg(tree[2 * nodeI], tree[2 * nodeI + 1]);
  }

  void rangeMod(int l, int r, int mod) {
    _rangeMod(1, 0, n - 1, l, r, mod);
  }

  void _pointSet(int nodeI, int tl, int tr, int pos, int val) {
    if (tl == tr) {
        tree[nodeI] = _makeLeaf(val);
        return;
    }
    int tm = (tl + tr) / 2;
    if (pos <= tm) {
        _pointSet(2 * nodeI, tl, tm, pos, val);
    } else {
        _pointSet(2 * nodeI + 1, tm + 1, tr, pos, val);
    }
    tree[nodeI] = _agg(tree[2 * nodeI], tree[2 * nodeI + 1]);
  }

  void pointSet(int pos, int val) {
    _pointSet(1, 0, n - 1, pos, val);
  }

  ll _rangeSum(int nodeI, int tl, int tr, int ql, int qr) {
    // oob
    if (ql > tr || qr < tl) return 0;
    // full
    if (ql <= tl && qr >= tr) {
        return tree[nodeI].tot;
    }
    int tm = (tl + tr) / 2;
    ll left = _rangeSum(2 * nodeI, tl, tm, ql, qr);
    ll right = _rangeSum(2 * nodeI + 1, tm + 1, tr, ql, qr);
    return left + right;
  }

  ll rangeSum(int l, int r) {
    return _rangeSum(1, 0, n - 1, l, r);
  }
};

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m; cin >> n >> m;
    vector<int> arr(n); for (int i = 0; i < n; i++) cin >> arr[i];
    Seg seg(arr);
    for (int i = 0; i < m; i++) {
        int qtype; cin >> qtype;
        if (qtype == 1) {
            int l, r; cin >> l >> r; l--; r--;
            cout << seg.rangeSum(l, r) << '\n';
        } else if (qtype == 2) {
            int l, r, x; cin >> l >> r >> x; l--; r--;
            seg.rangeMod(l, r, x);
        } else {
            int pos, newVal; cin >> pos >> newVal; pos--;
            seg.pointSet(pos, newVal);
        }
    }
}