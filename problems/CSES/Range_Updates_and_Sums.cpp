#include <bits/stdc++.h>
using namespace std;

struct LazySeg {
    vector<int> A;
    
    struct Node {
        long long sum = 0;
        int width;
        long long lazyAdd = 0;
        long long lazyAssign = 0; // sentinel value, no assignment set
    };

    vector<Node> tree;

    void build() {
        _build(1, 0, A.size() - 1);
    }
    // Updates our nodes values only based on childrens values
    void pull(int i) {
        Node left = tree[2 * i];
        Node right = tree[2 * i + 1];
        tree[i].sum = left.sum + right.sum;;
        tree[i].width = left.width + right.width;
    }

    // Pushes down lazies and clears out current lazies, no updates applied to this node
    void pushDownLaziesAndClearCurrentLazies(int i, int tl, int tr) {
        if (tl == tr) return; // don't need to do anything at a leaf or even clear lazies since it is implied the lazies are already applied
        applyUpdatesAndComposeLazies(2 * i, tree[i].lazyAdd, tree[i].lazyAssign);
        applyUpdatesAndComposeLazies(2 * i + 1, tree[i].lazyAdd, tree[i].lazyAssign);
        tree[i].lazyAdd = 0;
        tree[i].lazyAssign = 0;
    }

    // Updates a nodes values based on new updates, and composes lazies for future children
    void applyUpdatesAndComposeLazies(int i, long long add, long long assign) {
        // only lazy add set
        if (assign == 0) {
            tree[i].sum += add * tree[i].width;
        } // only lazy assign is set
        else if (add == 0) {
            tree[i].sum = assign * (tree[i].width);
        }
        // both are set, implicitly it is assign first then add
        else {
            tree[i].sum = assign * (tree[i].width);
            tree[i].sum += add * tree[i].width;
        }

        // My node had previous lazy tags for its children, now receiving new lazy tags, compose them
        if (assign != 0) {
            tree[i].lazyAssign = assign;
            tree[i].lazyAdd = add;
        } else {
            tree[i].lazyAdd += add;
        }
    }

    void _build(int i, int tl, int tr) {
        if (tl == tr) {
            tree[i] = Node{A[tl], 1, 0, 0};
            return;
        }
        int tm = (tr + tl) / 2;
        _build(2 * i, tl, tm);
        _build(2 * i + 1, tm + 1, tr);
        pull(i);
    }

    LazySeg(vector<int> _A) {
        A = _A;
        tree.resize(A.size() * 4 + 5);
        build();
    }

    void rangeAssign(int l, int r, int assigned) {
        _rangeAssign(1, 0, A.size() - 1, l, r, assigned);
    }

    void _rangeAssign(int i, int tl, int tr, int ql, int qr, int assigned) {
        pushDownLaziesAndClearCurrentLazies(i, tl, tr);
        
        // If no overlap, no need to update
        if (qr < tl || ql > tr) return;

        // If we are fully inside, we can update immediately
        if (ql <= tl && qr >= tr) {
            applyUpdatesAndComposeLazies(i, 0, assigned);
            return;
        }

        // Otherwise propagate to both
        int tm = (tr + tl) / 2;
        _rangeAssign(2 * i, tl, tm, ql, qr, assigned);
        _rangeAssign(2 * i + 1, tm + 1, tr, ql, qr, assigned);
        pull(i);
    }

    void rangeAdd(int l, int r, int added) {
        _rangeAdd(1, 0, A.size() - 1, l, r, added);
    }

    void _rangeAdd(int i, int tl, int tr, int ql, int qr, int added) {
        pushDownLaziesAndClearCurrentLazies(i, tl, tr);

        // If no overlap, no need to update
        if (qr < tl || ql > tr) return;

        // If we are fully inside, we can update immediately
        if (ql <= tl && qr >= tr) {
            applyUpdatesAndComposeLazies(i, added, 0);
            return;
        }

        int tm = (tr + tl) / 2;
        _rangeAdd(2 * i, tl, tm, ql, qr, added);
        _rangeAdd(2 * i + 1, tm + 1, tr, ql, qr, added);
        pull(i);
    }

    long long querySum(int l, int r) {
        return _querySum(1, 0, A.size() - 1, l, r);
    }

    long long _querySum(int i, int tl, int tr, int ql, int qr) {
        pushDownLaziesAndClearCurrentLazies(i, tl, tr);
        // If we are fully inside, we can use the current sum
        if (ql <= tl && qr >= tr) {
            return tree[i].sum;
        }
        // OOB, used identity
        if (ql > tr || qr < tl) {
            return 0;
        }
        int tm = (tr + tl) / 2;
        long long left = _querySum(2 * i, tl, tm, ql, qr);
        long long right = _querySum(2 * i + 1, tm + 1, tr, ql, qr);
        return left + right;
    }
};

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, q; cin >> n >> q;
    vector<int> A(n);
    for (int i = 0; i < n; i++) cin >> A[i];
    LazySeg st = LazySeg(A);
    for (int i = 0; i < q; i++) {
        int op, a, b; cin >> op >> a >> b;
        a--; b--;
        if (op == 1) {
            int x; cin >> x;
            st.rangeAdd(a, b, x);
        } else if (op == 2) {
            int x; cin >> x;
            st.rangeAssign(a, b, x);
        } else {
            cout << st.querySum(a, b) << endl;
        }
    }
}