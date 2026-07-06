#include <bits/stdc++.h>
using namespace std;
using ll = long long;


// EXAMPLE
// using RawVal = ll; // the raw node value input, could also be a struct

// // Accumulated node data
// struct NodeData {
//     ll total;
// };

// // Maps the raw node value to our NodeData
// auto base = [](RawVal v) -> NodeData {
//     return NodeData{v};
// };

// // How to aggregate two NodeData nodes
// auto mergeFn = [](NodeData A, NodeData B) -> NodeData {
//     return NodeData{A.total + B.total};
// };


// TO CREATE THE HLD (O(n) build time)
// RawVal, NodeData are the types
// edges should be vector<pair<int,int>> with node labels (either 0...n-1, or 1...n)
// vals[node] is the value AT that node, if the nodes are 1...n then vals[0] can be whatever dummy value
// 1 at the end is the root, it can be any value in the tree, separate from if the nodes are 0...n-1 or 1...n
// last param is `zeroIndexed`, so false means the nodes are 1...n
// HldSegTree<RawVal, NodeData> hld(edges, vals, base, mergeFn, 1, false);


// METHODS

// O(logN)
// pointSet(nodeLabel, RawVal), overwrites the value at `nodeLabel` with this new raw value

// O(logN)
// pointApply(nodeLabel, RawVal), combines this raw value into `nodeLabel`

// O(log^2 N)
// pathQuery(a, b) -> NodeData, gives us the aggregated data on the path a...b, includes both endpoints

// O(log N)
// subtreeQuery(nodeLabel) -> NodeData, aggregated data of all nodes in the subtree, includes nodeLabel itself


template <typename RawT, typename StoredT>
struct HldSegTree {
    int n, root, arrSize;
    bool zeroIndexed;
    function<StoredT(RawT)> base;
    function<StoredT(StoredT, StoredT)> combine;
    vector<vector<int>> adj;
    vector<int> par, depth, sz, heavy, head, pos;
    int segN, LOG;
    vector<optional<StoredT>> tree;

    HldSegTree(
        const vector<pair<int,int>>& edges,
        const vector<RawT>& vals,
        function<StoredT(RawT)> base,
        function<StoredT(StoredT, StoredT)> combine,
        int root,
        bool zeroIndexed)
        : n((int)edges.size() + 1), root(root),
          arrSize(zeroIndexed ? (int)edges.size() + 1 : (int)edges.size() + 2), zeroIndexed(zeroIndexed),
          base(base), combine(combine),
          adj(arrSize), par(arrSize, -1), depth(arrSize, 0), sz(arrSize, 1),
          heavy(arrSize, -1), head(arrSize, 0), pos(arrSize, 0)
    {
        assert(zeroIndexed ? (root >= 0 && root < n) : (root >= 1 && root <= n));
        for (auto& [u, v] : edges) {
            adj[u].push_back(v);
            adj[v].push_back(u);
        }
        _dfsInit();
        _dfsDecompose();
        segN = 1;
        while (segN < max(n, 1)) segN <<= 1;
        LOG = max(1, __lg(segN));
        tree.assign(2 * segN, nullopt);
        int lo = zeroIndexed ? 0 : 1;
        int hi = zeroIndexed ? n : n + 1;
        for (int i = lo; i < hi; i++) {
            tree[segN + pos[i]] = base(vals[i]);
        }
        for (int i = segN - 1; i >= 1; i--) {
            tree[i] = _combineOpt(tree[2*i], tree[2*i+1]);
        }
    }

    optional<StoredT> _combineOpt(const optional<StoredT>& a, const optional<StoredT>& b) {
        if (!a.has_value()) return b;
        if (!b.has_value()) return a;
        return combine(*a, *b);
    }

    void _dfsInit() {
        vector<int> order;
        order.reserve(n);
        vector<tuple<int,int,int>> stack;
        stack.push_back({root, -1, 0});
        while (!stack.empty()) {
            auto [node, parent, d] = stack.back();
            stack.pop_back();
            par[node] = parent;
            depth[node] = d;
            order.push_back(node);
            for (int nxt : adj[node]) {
                if (nxt != parent) stack.push_back({nxt, node, d + 1});
            }
        }
        for (int i = (int)order.size() - 1; i >= 0; i--) {
            int node = order[i];
            int best = 0;
            for (int nxt : adj[node]) {
                if (nxt == par[node]) continue;
                sz[node] += sz[nxt];
                if (sz[nxt] > best) {
                    best = sz[nxt];
                    heavy[node] = nxt;
                }
            }
        }
    }

    void _dfsDecompose() {
        int timer = 0;
        vector<pair<int,int>> stack;
        stack.push_back({root, root});
        while (!stack.empty()) {
            auto [node, h] = stack.back();
            stack.pop_back();
            head[node] = h;
            pos[node] = timer++;
            for (int nxt : adj[node]) {
                if (nxt == par[node] || nxt == heavy[node]) continue;
                stack.push_back({nxt, nxt});
            }
            if (heavy[node] != -1) {
                stack.push_back({heavy[node], h});
            }
        }
    }

    optional<StoredT> _segQuery(int l, int r) {
        if (l > r) return nullopt;
        l += segN;
        r += segN + 1;
        optional<StoredT> resL = nullopt, resR = nullopt;
        while (l < r) {
            if (l & 1) { resL = _combineOpt(resL, tree[l]); l++; }
            if (r & 1) { r--; resR = _combineOpt(tree[r], resR); }
            l >>= 1; r >>= 1;
        }
        return _combineOpt(resL, resR);
    }

    void _segPointSet(int idx, const optional<StoredT>& newData) {
        int p = idx + segN;
        tree[p] = newData;
        for (p >>= 1; p > 0; p >>= 1) {
            tree[p] = _combineOpt(tree[2*p], tree[2*p+1]);
        }
    }

    void pointSet(int node, RawT rawVal) {
        _segPointSet(pos[node], base(rawVal));
    }

    void pointApply(int node, RawT rawVal) {
        _segPointSet(pos[node], _combineOpt(tree[pos[node] + segN], optional<StoredT>(base(rawVal))));
    }

    StoredT pathQuery(int a, int b) {
        optional<StoredT> res = nullopt;
        while (head[a] != head[b]) {
            if (depth[head[a]] < depth[head[b]]) swap(a, b);
            res = _combineOpt(res, _segQuery(pos[head[a]], pos[a]));
            a = par[head[a]];
        }
        if (depth[a] > depth[b]) swap(a, b);
        res = _combineOpt(res, _segQuery(pos[a], pos[b]));
        return *res;
    }

    StoredT subtreeQuery(int node) {
        return *_segQuery(pos[node], pos[node] + sz[node] - 1);
    }
};