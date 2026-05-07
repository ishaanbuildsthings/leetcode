#include <bits/stdc++.h>
using namespace std;
#include <ext/pb_ds/assoc_container.hpp>
#include <ext/pb_ds/tree_policy.hpp>
using namespace __gnu_pbds;
template<class T> using oset = tree<T, null_type, less<T>, rb_tree_tag,
                                    tree_order_statistics_node_update>;

using ll = long long;

struct Node {
    int cand;
    int surplus;
};

struct Seg {
    int n;
    vector<Node> tree;
    Seg(const vector<int>& A) {
        n = A.size();
        tree.resize(4 * n);
        _build(1, 0, n - 1, A);
    }
    void _build(int nodeI, int tl, int tr, const vector<int>& A) {
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
        tree[nodeI] = _combine(tree[2 * nodeI], tree[2 * nodeI + 1]);
    }
    Node _combine(Node& a, Node& b) {
        Node out;
        if (a.cand == b.cand) {
            out.cand = a.cand;
            out.surplus = a.surplus + b.surplus;
            return out;
        }
        if (a.surplus >= b.surplus) {
            out.cand = a.cand;
            out.surplus = a.surplus - b.surplus;
            return out;
        }
        out.cand = b.cand;
        out.surplus = b.surplus - a.surplus;
        return out;
    }
    Node _query(int nodeI, int tl, int tr, int ql, int qr) {
        // fully inside
        if (ql <= tl && qr >= tr) {
            return tree[nodeI];
        }
        int tm = (tl + tr) / 2;
        // full left
        if (qr <= tm) {
            return _query(2 * nodeI, tl, tm, ql, qr);
        } // full right
        else if (ql >= tm + 1) {
            return _query(2 * nodeI + 1, tm + 1, tr, ql, qr);
        }
        Node left = _query(2 * nodeI, tl, tm, ql, qr);
        Node right =  _query(2 * nodeI + 1, tm + 1, tr, ql, qr);
        return _combine(left, right);
    }

    Node query(int l, int r) {
        return _query(1, 0, n - 1, l, r);
    }

    void _pointUpdate(int nodeI, int tl, int tr, int pos, int newVal) {
        if (tl == tr) {
            tree[nodeI] = {newVal, 1};
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

    void pointUpdate(int pos, int newVal) {
        _pointUpdate(1, 0, n - 1, pos, newVal);
    }
};

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, q; cin >> n >> q;
    vector<int> A(n); for (int i = 0; i < n; i++) cin >> A[i];
    Seg seg(A);
    // need a map of values -> positions of indices
    unordered_map<int, oset<int>> pos;
    for (int i = 0; i < n; i++) {
        pos[A[i]].insert(i);
    }

    auto cntInRange = [&](int num, int l, int r) -> int {
        return pos[num].order_of_key(r + 1) - pos[num].order_of_key(l);
    };

    while (q--) {
        int qtype; cin >> qtype;
        if (qtype == 0) {
            int p, newV; cin >> p >> newV;
            int oldV = A[p];
            pos[oldV].erase(p);
            seg.pointUpdate(p, newV);
            pos[newV].insert(p);
            A[p] = newV;
        } else {
            int l, r; cin >> l >> r; r--; // half open
            Node out = seg.query(l, r);
            int cnt = cntInRange(out.cand, l, r);
            int width = r - l + 1;
            if (cnt > width / 2) {
                cout << out.cand << endl;
            } else {
                cout << -1 << endl;
            }
        }
    }    
}