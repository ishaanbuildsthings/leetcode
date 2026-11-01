#include <bits/stdc++.h>
using namespace std;

struct Node {
    Node* l;
    Node* r;
};

void insert(Node* node, int i, int tl, int tr) {
    if (tl == tr) return;
    int tm = (tl + tr) / 2;
    bool goLeft = i <= tm;
    if (goLeft && !node->l) {
        node->l = new Node();
    }
    if (!goLeft && !node->r) {
        node->r = new Node();
    }
    if (i <= tm) {
        insert(node->l, i, tl, tm);
    } else {
        insert(node->r, i, tm + 1, tr);
    }
}

Node* merge(Node* a, Node* b) {
    if (!a) return b;
    if (!b) return a;
    Node* left = merge(a->l, b->l);
    Node* right = merge(a->r, b->r);
    a->l = left;
    a->r = right;
    return a;
}

// takes the original node, returns a dupe of the non-covered ones and a cut of the fully convered ones
Node* cutAndCopy(Node* orig, Node* parent, int l, int r, int tl, int tr) {
    if (!orig) return nullptr;
    // out of bounds
    if (tr < l || tl > r) return nullptr;
    // fully inside
    if (l <= tl && r >= tr) {
        if (parent) {
            if (parent->r == orig) parent->r = nullptr;
            if (parent->l == orig) parent->l = nullptr;
        }
        return orig;
    }
    // partial
    Node* dupe = new Node();
    int tm = (tl + tr) / 2;
    dupe->l = cutAndCopy(orig->l, orig, l, r, tl, tm);
    dupe->r = cutAndCopy(orig->r, orig, l, r, tm + 1, tr);
    return dupe;
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n; cin >> n;
    vector<int> A(n); for (int i = 0; i < n; i++) cin >> A[i];
    unordered_map<int,vector<int>> vToI;
    unordered_map<int, Node*> vToSeg;
    for (int i = 0; i < n; i++) {
        int v = A[i];
        vToI[v].push_back(i);
        if (vToI[v].size() == 1) {
            vToSeg[v] = new Node();
        }
        insert(vToSeg[v], i, 0, n - 1);
    }
    int q; cin >> q;
    for (int i = 0; i < q; i++) {
        int l, r, x, y; cin >> l >> r >> x >> y; l--; r--;
        if (x == y) continue; // needed to avoid tle, this won't reduce entropy
        Node* seg1 = vToSeg[x];
        Node* seg2 = vToSeg[y];
        Node* cutOut = cutAndCopy(seg1, nullptr, l, r, 0, n - 1);
        // entire tree moved, since I didn't have a dummy parent we do this
        if (cutOut == seg1) {
            vToSeg[x] = nullptr;
        }
        Node* merged = merge(seg2, cutOut);
        vToSeg[y] = merged;
    }
    vector<int> res(n, 0);
    auto dfs = [&](auto&& self, Node* node, int tl, int tr, int v) {
        if (!node) return;
        if (tl == tr) {
            res[tl] = v;
            return;
        }
        int tm = (tl + tr) / 2;
        self(self, node->l, tl, tm, v);
        self(self, node->r, tm + 1, tr, v);
    };
    for (auto [v, seg] : vToSeg) {
        dfs(dfs, seg, 0, n - 1, v);
    }
    for (auto x : res) cout << x << " ";

}