#include <bits/stdc++.h>
using namespace std;

struct MinSeg {
    vector<int> A;
    int n;
    struct Node {
        int min;
    };

    vector<Node> tree;

    MinSeg(const vector<int>& _A) {
        A = _A;
        n = A.size();
        tree.resize(4 * n + 5);
        build();
    }

    void build() {
        _build(1, 0, n - 1);
    }

    void _build(int i, int tl, int tr) {
        if (tl == tr) {
            tree[i] = Node{A[tl]};
            return;
        }
        int tm = (tr+tl)/2;
        _build(2 * i, tl, tm);
        _build(2 * i + 1, tm + 1, tr);
        pull(i);
    }

    Node merge(const Node& left, const Node& right) {
        return Node{min(left.min, right.min)};
    }

    void pull(int i) {
        tree[i] = merge(tree[2 * i], tree[2 * i + 1]);
    }

    int queryMin(int l, int r) {
        return _queryMin(1, 0, n - 1, l, r);
    }

    int _queryMin(int i, int tl, int tr, int ql, int qr) {
        if (ql > tr || qr < tl) return INT_MAX;
        if (ql <= tl && qr >= tr) return tree[i].min;
        int tm = (tl + tr) / 2;
        return min(
            _queryMin(2*i, tl, tm, ql, qr),
            _queryMin(2*i + 1, tm + 1, tr, ql, qr)
        );
    }

    void pointUpdate(int pos, int newVal) {
        _pointUpdate(1, 0, n - 1, pos, newVal);
    }

    void _pointUpdate(int i, int tl, int tr, int pos, int newVal) {
        if (tl == tr) {
            tree[i] = Node{newVal};
            return;
        }
        int tm = (tr + tl) / 2;
        if (pos <= tm) {
            _pointUpdate(2 * i, tl, tm, pos, newVal);
        } else {
            _pointUpdate(2 * i + 1, tm + 1, tr, pos, newVal);
        }
        pull(i);
    }
};

int main() {
    cin.tie(nullptr);
    ios::sync_with_stdio(false);
    int n, q; cin >> n >> q;
    vector<int> A(n); for (int i = 0; i < n; i++) cin >> A[i];
    vector<int> nxt(n); // nxt[i] -> next index or N of the same occurence of the number

    unordered_map<int, set<int>> numToIndices;
    numToIndices.reserve(2 * n);
    for (int i = 0; i < n; i++) {
        int num = A[i];
        numToIndices[num].insert(i);
    }

    unordered_map<int,int> early;
    early.reserve(2 * n);

    for (int i = n - 1; i >= 0; --i) {
        int x = A[i];
        auto it = early.find(x);
        if (it == early.end()) {
            nxt[i] = n;
        } else {
            nxt[i] = it->second;
        }
        early[x] = i;
    }
    MinSeg st(nxt);

    auto prevIdx = [&](const set<int>& s, set<int>::iterator it) -> int {
        if (it == s.begin()) return -1;
        return *prev(it);
    };

    auto nextIdx = [&](const set<int>& s, set<int>::iterator it) -> int {
        if (next(it) == s.end()) return n;
        return *next(it);
    };

    for (int i = 0; i < q; i++) {
        int op; cin >> op;
        if (op == 2) {
            int l, r; cin >> l >> r; l--; r--;
            int minimum = st.queryMin(l, r);
            if (minimum > r) {
                cout << "YES" << "\n";
            } else {
                cout << "NO" << "\n";
            }
        } else {
            int j; int newVal; cin >> j >> newVal; j--;

            int oldVal = A[j];

            // re-wire the oldVal previous index -> oldVal next index
            auto& S = numToIndices[oldVal];
            auto it = S.find(j);
            auto prevId = prevIdx(S, it);
            auto nextId = nextIdx(S, it);
            if (prevId != -1) {
                nxt[prevId] = nextId;
                st.pointUpdate(prevId, nextId);
            }

            S.erase(j);

            auto& S2 = numToIndices[newVal];
            S2.insert(j);
            auto it2 = S2.find(j);
            auto prevId2 = prevIdx(S2, it2);
            auto nextId2 = nextIdx(S2, it2);
            if (prevId2 != -1) {
                nxt[prevId2] = j;
                st.pointUpdate(prevId2, j);
            }
            nxt[j] = nextId2;
            st.pointUpdate(j, nextId2);

            A[j] = newVal;
        }
    }
}