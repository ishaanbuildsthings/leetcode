#include <bits/stdc++.h>
using namespace std;
using ll = long long;


// EXAMPLE
// using RawEdgeVal = ll; // the raw edge value input, could also be a struct

// // Accumulated edge data
// struct EdgeData {
//     ll total, pref, suf, best;
//     int len;
// };

// // Maps the raw edge value to our EdgeData
// auto base = [](RawEdgeVal v) -> EdgeData {
//     return EdgeData{v, v, v, v, 1};
// };

// // How to aggregate two EdgeData nodes, order matters
// auto mergeFn = [](EdgeData A, EdgeData B) -> EdgeData {
//     return EdgeData{
//         A.total + B.total,
//         max(A.pref, A.total + B.pref),
//         max(B.suf,  B.total + A.suf),
//         max({A.best, B.best, A.suf + B.pref}),
//         A.len + B.len
//     };
// };

// How to reverse an EdgeData
// auto reverseFn = [](EdgeData edgeData) -> EdgeData {
//     return EdgeData{edgeData.total, edgeData.suf, edgeData.pref, edgeData.best, edgeData.len};
// };


// TO CREATE THE HLD (O(n) build time)
// RawEdgeVal, EdgeData are the types
// edges should be vector<pair<int,int>> with node labels (either 0...n-1, or 1...n)
// vals[node] is the edge ABOVE that node, if we are using root=1, then vals[0] can be whatever dummy value
// 1 at the end is the root, it can be any value in the tree, separate from if the nodes are 0...n-1 or 1...n
// last param is `zeroIndexed`, so false means the nodes are 1...n
// HldSegTreeEdgesReverse<RawVal, EdgeData> hld(edges, vals, base, mergeFn, reverseFn, 1, false);


// METHODS

// O(logN)
// pointSet(nodeLabel, RawEdgeVal), overwrites the edge above `nodeLabel` with this new raw value

// O(logN)
// pointApply(nodeLabel, RawEdgeVal), combines this raw value into the edge above `nodeLabel`

// O(log^2 N)
// pathQuery(a, b) -> EdgeData, gives us the aggregated data on the path a->b, crashes if a==b

// O(log N)
// subtreeQuery(nodeLabel) -> EdgeData, aggregated data of all edges in the subtree (orientation is unspecified / not ordered), crashes if a leaf


template <typename RawT, typename StoredT>
struct HldSegTreeEdgesReverse {
    int n, root, arrSize;
    bool zeroIndexed;
    function<StoredT(RawT)> base;
    function<StoredT(StoredT, StoredT)> combine;
    function<StoredT(StoredT)> reverse_;    // reversed orientation of an edge-data chunk
    vector<vector<int>> adj;
    vector<int> par, depth, sz, heavy, head, pos;
    int segN, LOG;
    vector<optional<StoredT>> tree;

    HldSegTreeEdgesReverse(
        const vector<pair<int,int>>& edges,
        const vector<RawT>& vals,
        function<StoredT(RawT)> base,
        function<StoredT(StoredT, StoredT)> combine,
        function<StoredT(StoredT)> reverse_,
        int root,
        bool zeroIndexed)
        : n((int)edges.size() + 1), root(root),
          arrSize(zeroIndexed ? (int)edges.size() + 1 : (int)edges.size() + 2), zeroIndexed(zeroIndexed),
          base(base), combine(combine), reverse_(reverse_),
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
            if (i == root) tree[segN + pos[i]] = nullopt;
            else tree[segN + pos[i]] = base(vals[i]);
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

    optional<StoredT> _reverseOpt(const optional<StoredT>& a) {
        if (!a.has_value()) return a;
        return reverse_(*a);
    }

    void pointSet(int node, RawT rawVal) {
        _segPointSet(pos[node], base(rawVal));
    }

    void pointApply(int node, RawT rawVal) {
        _segPointSet(pos[node], _combineOpt(tree[pos[node] + segN], optional<StoredT>(base(rawVal))));
    }

    // ORDERED path query a -> b. precondition: a != b.
    // Each _segQuery chunk is stored ancestor->descendant (pos-increasing). We split the
    // path at the LCA and accumulate the two sides separately. As we climb, each newly
    // fetched chunk is higher up, so we PREPEND it (_combineOpt(chunk, acc)) to keep each
    // side ordered top->bottom (ancestor->descendant). The b-side in that orientation is
    // already the correct forward order (lca->b). The a-side's real traversal is a->lca,
    // i.e. bottom->top, the reverse of how it's stored, so we reverse it before joining.
    StoredT pathQuery(int a, int b) {
        optional<StoredT> accA = nullopt;   // a-side edges, stored ancestor->descendant
        optional<StoredT> accB = nullopt;   // b-side edges, stored ancestor->descendant
        int ca = a, cb = b;
        while (head[ca] != head[cb]) {
            if (depth[head[ca]] > depth[head[cb]]) {
                accA = _combineOpt(_segQuery(pos[head[ca]], pos[ca]), accA);
                ca = par[head[ca]];
            } else {
                accB = _combineOpt(_segQuery(pos[head[cb]], pos[cb]), accB);
                cb = par[head[cb]];
            }
        }
        // same chain: shallower endpoint is the LCA; remaining edges belong to the deeper side
        if (depth[ca] > depth[cb])
            accA = _combineOpt(_segQuery(pos[cb] + 1, pos[ca]), accA);
        else if (depth[cb] > depth[ca])
            accB = _combineOpt(_segQuery(pos[ca] + 1, pos[cb]), accB);
        return *_combineOpt(_reverseOpt(accA), accB);   // reverse a-side, then lca->b
    }

    StoredT subtreeQuery(int node) {
        return *_segQuery(pos[node] + 1, pos[node] + sz[node] - 1);
    }
};