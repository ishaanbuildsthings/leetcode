// goal is to support point updates and path maxes
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

const int NINF = INT_MIN;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, q;
    cin >> n >> q;
    vector<int> A(n); for (int i = 0; i < n; i++) cin >> A[i];
    vector<vector<int>> adj(n);
    for (int i = 0; i < n; i++) {
        int a, b; cin >> a >> b; a--; b--;
        adj[a].push_back(b);
        adj[b].push_back(a);
    }
    vector<vector<int>> children(n);
    auto makeChildren = [&](auto&& self, int node, int parent) -> void {
        for (auto adjN : adj[node]) {
            if (adjN == parent) continue;
            children[node].push_back(adjN);
            self(self, adjN, node);
        }
    };
    makeChildren(makeChildren, 0, -1);

    vector<int> sz(n, 1);
    vector<int> depth(n);
    vector<int> heavy(n, -1);
    vector<int> par(n, -1);

    auto init = [&](auto&& self, int node, int currDepth) -> void {
        depth[node] = currDepth;
        int mxChild = 0;
        int heavyHere = -1;
        for (auto child : children[node]){
            par[child] = node;
            self(self, child, currDepth + 1);
            if (sz[child] > mxChild) {
                mxChild = sz[child];
                heavyHere = child;
            }
            sz[node] += sz[child];
        }
        heavy[node] = heavyHere;
    };
    init(init, 0, 0);

    vector<int> posInOrderedArray(n); // order[node] -> the time it occurred at
    vector<int> head(n);
    vector<int> orderedNodes;
    int timer = 0;
    auto decompose = [&](auto&& self, int node, int chainHead) -> void {
        posInOrderedArray[node] = timer++;
        orderedNodes.push_back(node);
        head[node] = chainHead;
        if (heavy[node] != -1) {
            self(self, heavy[node], chainHead);
        }
        for (auto child : children[node]) {
            if (child != heavy[node]) self(self, child, child);
        }
    };
    decompose(decompose, 0, 0);

    struct Node {
        int mx;
    };
    vector<Node> tree(4 * n);

    auto _combine = [&](Node& a, Node& b) -> Node {
        return {max(a.mx, b.mx)};
    };

    auto _pull = [&](int nodeI) -> void {
        Node& left = tree[2 * nodeI];
        Node& right = tree[2 * nodeI + 1];
        tree[nodeI] = _combine(left, right);
    };

    auto _build = [&](auto&& self, int nodeI, int tl, int tr) -> void {
        if (tl == tr) {
            int nodeVal = A[orderedNodes[tl]];
            tree[nodeI] = {nodeVal};
            return;
        }
        int tm = (tl + tr) / 2;
        self(self, 2 * nodeI, tl, tm);
        self(self, 2 * nodeI + 1, tm + 1, tr);
        _pull(nodeI);
    };
    _build(_build, 1, 0, n);

    auto _query = [&](auto&& self, int nodeI, int tl, int tr, int ql, int qr) -> Node {
        // disjoint
        if (qr < tl || ql > tr) return {NINF};
        // fully inside
        if (ql <= tl && qr >= tr) return tree[nodeI];
        int tm = (tl + tr) / 2;
        Node left = self(self, 2 * nodeI, tl, tm, ql, qr);
        Node right = self(self, 2 * nodeI + 1, tm + 1, tr, ql, qr);
        return _combine(left, right);
    };

    auto _pointUpdate = [&](auto&& self, int nodeI, int tl, int tr, int idx, int newVal) -> void {
        if (tl == tr) {
            tree[nodeI] = {newVal};
            return;
        }
        int tm = (tl + tr) / 2;
        if (idx <= tm) {
            self(self, 2 * nodeI, tl, tm, idx, newVal);
        } else {
            self(self, 2 * nodeI + 1, tm + 1, tr, idx, newVal);
        }
        _pull(nodeI);
    };

    auto query = [&](int l, int r) -> int {
        Node out = _query(_query, 1, 0, n - 1, l, r);
        return out.mx;
    };

    auto pointUpdate = [&](int idx, int newVal) -> void {
        _pointUpdate(_pointUpdate, 1, 0, n - 1, idx, newVal);
    };

    auto pathQuery = [&](int a, int b) -> int {
        int out = INT_MIN;
        while (head[a] != head[b]) {
            if (depth[head[a]] < depth[head[b]]) swap(a, b);
            int aPos = posInOrderedArray[a];
            int aHeadPos = posInOrderedArray[head[a]];
            int upA = query(aHeadPos, aPos);
            out = max(out, upA);
            a = head[a];
        }
        // they lie on the same heavy chain now
        if (depth[a] < depth[b]) swap(a, b);
        int aPos = posInOrderedArray[a];
        int bPos = posInOrderedArray[b];
        out = max(out, query(bPos, aPos));
        return out;
    };

    for (int i = 0; i < q; i++) {
        int qtype; cin >> qtype;
        if (qtype == 1) {
            int idx, newVal; cin >> idx >> newVal; idx--;
            pointUpdate(idx, newVal);
        } else {
            int a, b; cin >> a >> b; a--; b--;
            cout << pathQuery(a, b) << '\n';
        }
    }
}