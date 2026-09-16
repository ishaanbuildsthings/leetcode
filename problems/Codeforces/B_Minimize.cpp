#include <bits/stdc++.h>
using namespace std;
using ll = long long;

const ll NEG_INF = -LLONG_MAX / 4;

struct Node {
    ll mx;
    ll mx2; // -inf if does not exist
    ll tot;
    ll cntMx;
    ll lazyChmin = -1; // -1 if no pending
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
        return Node{v, NEG_INF, v, 1};
    }

    void _recompute(int nodeI) {
        tree[nodeI] = _agg(tree[2 * nodeI], tree[2 * nodeI + 1]);
    }

    Node _agg(Node& left, Node& right) {
        ll mx1 = max(left.mx, right.mx);
        ll mx2 = NEG_INF;
        if (left.mx != mx1) {
            mx2 = left.mx;
        }
        if (right.mx != mx1) {
            mx2 = max(mx2, right.mx);
        }
        mx2 = max({mx2, left.mx2, right.mx2});
        int cmx = 0;
        if (left.mx == mx1) {
            cmx += left.cntMx;
        }
        if (right.mx == mx1) {
            cmx += right.cntMx;
        }
        ll ntot = left.tot + right.tot;
        return Node{mx1, mx2, ntot, cmx};
    }

    void _build(int nodeI, int tl, int tr, const vector<int>& arr) {
        if (tl == tr) {
            tree[nodeI] = _makeLeaf(arr[tl]);
            return;
        }
        int tm = (tl + tr) / 2;
        _build(2 * nodeI, tl, tm, arr);
        _build(2 * nodeI + 1, tm + 1, tr, arr);
        _recompute(nodeI);
    }

    ll _rangeSum(int nodeI, int tl, int tr, int ql, int qr) {
        if (qr < tl || ql > tr) return 0;
        if (ql <= tl && qr >= tr) return tree[nodeI].tot;
        _pushLazies(nodeI, tl, tr);
        int tm = (tl + tr) / 2;
        ll left = _rangeSum(2 * nodeI, tl, tm, ql, qr);
        ll right = _rangeSum(2 * nodeI + 1, tm + 1, tr, ql, qr);
        return left + right;
    }

    ll rangeSum(int l, int r) {
        return _rangeSum(1, 0, n - 1, l, r);
    }

    void _rangeChmin(int nodeI, int tl, int tr, int ql, int qr, int x) {
        // oob
        if (qr < tl || ql > tr) return;
        // fully inside
        if (ql <= tl && qr >= tr) {
            Node& node = tree[nodeI];
            // case 1, chmin doesn't drop anything
            if (x >= node.mx) return;
            // case 2, only max gets affected by the chmin
            if (x > node.mx2) {
                ll lost = node.cntMx * (node.mx - x);
                node.tot -= lost;
                node.mx = x;
                node.lazyChmin = x;
                return;
            }
            // case 3, multiple things get affected
            // remember we can only afford to do extra descends when potential actually drops
            // in rangeMod, potential drops if the max > mod so we can do extra descends there
            // here, potential only drops if max and max2 get glued together
            // (just let it enter the straddle code)
        }

        // lazyChmin technically always equals mx, and is > mx2, which is required for applyLazyAndCompose to recompute fast
        // if it is > mx2 here, it is greater than mx2 in the children
        _pushLazies(nodeI, tl, tr);
        int tm = (tl + tr) / 2;
        _rangeChmin(2 * nodeI, tl, tm, ql, qr, x);
        _rangeChmin(2 * nodeI + 1, tm + 1, tr, ql, qr, x);
        _recompute(nodeI);
    }

    void _pushLazies(int nodeI, int tl, int tr) {
        if (tl == tr) return;
        _applyLazyAndCompose(2 * nodeI, tree[nodeI].lazyChmin);
        _applyLazyAndCompose(2 * nodeI + 1, tree[nodeI].lazyChmin);
        tree[nodeI].lazyChmin = -1;
    }

    // applies a lazy update pushed from above to this node, then composes for future children
    void _applyLazyAndCompose(int nodeI, int lazy) {
        Node& node = tree[nodeI];
        if (lazy >= node.mx || lazy == -1) return;
        // lazy is certainly > mx2
        node.tot -= (node.mx - lazy) * node.cntMx;
        node.mx = lazy;
        node.lazyChmin = lazy;
    }

    void rangeChmin(int l, int r, int x) {
        _rangeChmin(1, 0, n - 1, l, r, x);
    }
};

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n; cin >> n;
    vector<int> arr(n); for (int i = 0; i < n; i++) cin >> arr[i];
    Seg seg(arr);
    int q; cin >> q;
    for (int i = 0; i < q; i++) {
        int qtype; cin >> qtype;
        if (qtype == 1) {
            int l, r, x; cin >> l >> r >> x; l--; r--;
            seg.rangeChmin(l, r, x);
        } else {
            int l, r; cin >> l >> r; l--; r--;
            cout << seg.rangeSum(l, r) << '\n';
        }
    }
}