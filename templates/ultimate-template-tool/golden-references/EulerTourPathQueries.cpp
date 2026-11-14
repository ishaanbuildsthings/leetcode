// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/golden-references/EulerTourPathQueries.cpp
// Path queries with an Euler tour, as a full solution to CSES "Path Queries" (https://cses.fi/problemset/task/1138).
// The part to read is main(), at the bottom.
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// ========================================================================
// IGNORE THIS PART IS JUST FOR LCA
static int lg(int x) {
    return 31 - __builtin_clz(x);
}
struct LCA {
    // Build: O(n log n) time/space. Query: O(1).
    // Takes 0-indexed edges of a tree with n nodes. root defaults to 0.
    int n, LOG;
    vector<int> depth, parent, pre;
    vector<vector<int>> sp;

    LCA(int n, const vector<pair<int, int>>& edges, int root = 0)
        : n(n), depth(n, 0), parent(n, -1), pre(n) {
        vector<vector<int>> g(n);
        for (auto& [a, b] : edges) {
            g[a].push_back(b);
            g[b].push_back(a);
        }

        // iterative DFS so deep trees can't overflow the stack
        vector<int> preOrder;
        preOrder.reserve(n);
        vector<int> stk = {root};
        while (!stk.empty()) {
            int node = stk.back();
            stk.pop_back();
            pre[node] = preOrder.size();
            preOrder.push_back(node);
            for (int adjN : g[node]) {
                if (adjN == parent[node]) continue;
                parent[adjN] = node;
                depth[adjN] = depth[node] + 1;
                stk.push_back(adjN);
            }
        }

        LOG = lg(n) + 1;
        sp.assign(LOG, vector<int>(n));
        sp[0] = preOrder;
        for (int k = 1; k < LOG; k++) {
            for (int i = 0; i + (1 << k) <= n; i++) {
                sp[k][i] = shallower(sp[k - 1][i], sp[k - 1][i + (1 << (k - 1))]);
            }
        }
    }

    int shallower(int node1, int node2) {
        return depth[node1] < depth[node2] ? node1 : node2;
    }

    // Returns the lowest common ancestor of node1 and node2. O(1).
    int query(int node1, int node2) {
        if (node1 == node2) return node1;
        int l = pre[node1];
        int r = pre[node2];
        if (l > r) swap(l, r);
        l++;
        int k = lg(r - l + 1);
        return parent[shallower(sp[k][l], sp[k][r - (1 << k) + 1])];
    }

    // Number of edges between node1 and node2. O(1).
    int dist(int node1, int node2) {
        return depth[node1] + depth[node2] - 2 * depth[query(node1, node2)];
    }
};

struct SumSeg {
    struct Node {
        ll tot = 0;
    };

    vector<Node> tree;
    int n;

    SumSeg(const vector<int>& A) {
        n = A.size();
        tree.resize(4 * n);
        _build(1, 0, n - 1, A);
    }

    void _build(int nodeI, int tl, int tr, const vector<int>& A) {
        if (tl == tr) {
            tree[nodeI] = {A[tl]};
            return;
        }
        int tm = (tl + tr) / 2;
        _build(2 * nodeI, tl, tm, A);
        _build(2 * nodeI + 1, tm + 1, tr, A);
        _pull(nodeI);
    }

    void _pull(int nodeI) {
        tree[nodeI] = agg(tree[2 * nodeI], tree[2 * nodeI + 1]);
    }

    Node agg(Node& a, Node& b) {
        return {a.tot + b.tot};
    }

    ll rangeSum(int l, int r) {
        return _rangeSum(1, 0, n - 1, l, r).tot;
    }

    Node _rangeSum(int nodeI, int tl, int tr, int ql, int qr) {
        if (tr < ql || tl > qr) return {0};
        if (ql <= tl && qr >= tr) return tree[nodeI];
        int tm = (tl + tr) / 2;
        Node left = _rangeSum(2 * nodeI, tl, tm, ql, qr);
        Node right = _rangeSum(2 * nodeI + 1, tm + 1, tr, ql, qr);
        return agg(left, right);
    }

    void pointSet(int idx, int newV) {
        _pointSet(1, 0, n - 1, idx, newV);
    }

    void _pointSet(int nodeI, int tl, int tr, int idx, int newV) {
        if (tl == tr) {
            tree[nodeI] = {newV};
            return;
        }
        int tm = (tl + tr) / 2;
        if (idx <= tm) {
            _pointSet(2 * nodeI, tl, tm, idx, newV);
        } else {
            _pointSet(2 * nodeI + 1, tm + 1, tr, idx, newV);
        }
        _pull(nodeI);
    }
};
// ========================================================================

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, q; cin >> n >> q;
    vector<int> A(n); for (int i = 0; i < n; i++) cin >> A[i];
    vector<vector<int>> g(n);
    vector<pair<int,int>> edges;
    for (int i = 0; i < n - 1; i++) {
        int a, b; cin >> a >> b; a--; b--;
        g[a].push_back(b);
        g[b].push_back(a);
        edges.push_back({a, b});
    }
    LCA lca(n, edges);

    vector<int> order;
    vector<int> tin(n);
    vector<int> tout(n);
    int timer = 0;
    auto dfs = [&](auto&& self, int node, int par) -> void {
        tin[node] = timer++;
        order.push_back(node);
        for (auto adjN : g[node]) {
            if (adjN == par) continue;
            self(self, adjN, node);
        }
        tout[node] = timer++;
        order.push_back(node);
    };
    dfs(dfs, 0, -1);

    auto isAncestor = [&](int a, int b) -> bool {
        return tin[a] <= tin[b] && tout[a] >= tout[b];
    };

    vector<int> arr(2 * n, 0);
    for (int i = 0; i < n; i++) {
        arr[tin[i]] = A[i];
        arr[tout[i]] = -A[i];
    }

    SumSeg seg(arr);

    auto nodeUpdate = [&](int node, int newV) {
        seg.pointSet(tin[node], newV);
        seg.pointSet(tout[node], -newV);
    };

    auto pathSum = [&](int a, int b) -> ll {
        if (tin[b] < tin[a]) swap(a, b);
        if (isAncestor(a, b)) {
            return seg.rangeSum(tin[a], tin[b]);
        }
        ll tot = seg.rangeSum(tout[a], tin[b]);
        int lcaNode = lca.query(a, b);
        tot += seg.rangeSum(tin[lcaNode], tout[lcaNode]);
        return tot;
    };

    for (int i = 0; i < q; i++) {
        int qtype; cin >> qtype;
        if (qtype == 1) {
            int s, x; cin >> s >> x; s--;
            nodeUpdate(s, x);
        } else {
            int node; cin >> node; node--;
            cout << pathSum(node, 0) << '\n';
        }
    }



}
