#include <bits/stdc++.h>
using namespace std;

// =============================================================================
// 0-INDEXED HLD WITH EDGE-WEIGHTED VARIANT
// =============================================================================
// N = number of nodes, root is node 0
// edges = vector of TUPLES like {a, b, edgeVal}, ... where edgeVal is the edge's value
// base(val) -> stored data
// combine(data1, data2) -> aggregated data
//
// Each edge's value is pushed onto its DEEPER endpoint (the child).
// The root has no edge above it, so its slot is unused (nullopt).
//
//
// METHODS
// -------
// pointSet(node, newEdgeVal)
//   Sets the value of the edge ABOVE `node`. No-op if node is the root.
//
// pointApply(node, delta)
//   Applies delta to the edge above `node` via combine.
//   E.g. for XOR: existing ^ delta. For sum: existing + delta. No-op if root.
//
// edgeSet(a, b, newEdgeVal)
//   Sets the value of the edge between adjacent nodes a and b.
//   a and b MUST be adjacent (one is parent of the other).
//
// edgeApply(a, b, delta)
//   Applies delta to the edge between adjacent nodes a and b.
//
// pathQuery(a, b) -> EdgeData
//   Aggregated data over the EDGES on path a..b.
//   CALLER MUST ENSURE a != b (empty path is undefined behavior).
//
// subtreeQuery(node) -> EdgeData
//   Aggregated data over edges from node down to all its descendants.
//   The edge ABOVE node itself is NOT included.
//   CALLER MUST ENSURE node has at least one descendant (leaf is undefined behavior).
//
//
// EXAMPLE: path XOR over edge weights
// -----------------------------------
//   using RawT     = int;   // raw type of an edge's weight
//   using EdgeData = int;   // what we store at each slot in the seg tree
//
//   auto base = [](RawT v) -> EdgeData {
//       return v;
//   };
//   auto combine = [](EdgeData a, EdgeData b) -> EdgeData {
//       return a ^ b;
//   };
//
//   // edges shape: each entry is {nodeA, nodeB, rawT}
//   vector<tuple<int,int,RawT>> edges = {
//       {0, 1, 5},   // edge from node 0 to node 1 with weight 5
//       {1, 2, 3},
//       {0, 3, 7}
//   };
//
//   HLDEdge<RawT, EdgeData> hld(n, edges, base, combine);
//
//   EdgeData answer = hld.pathQuery(2, 3);
//   cout << answer << "\n";
// =============================================================================

template <typename RawT, typename EdgeData>
struct HLDEdge {
    int n;
    function<EdgeData(RawT)> base;
    function<EdgeData(EdgeData, EdgeData)> combine;
    vector<vector<pair<int,RawT>>> adj; // adj[u] = list of (neighbor, edgeVal)
    vector<int> par, depth, sz, heavy, head, pos;
    vector<optional<RawT>> edgeAbove; // edge value above each node; nullopt for root
    int segN;
    // use optional<EdgeData> internally so we can represent "nothing here" without an identity
    vector<optional<EdgeData>> seg;

    HLDEdge(int n,
        const vector<tuple<int,int,RawT>>& edges,
        function<EdgeData(RawT)> base,
        function<EdgeData(EdgeData, EdgeData)> combine)
        : n(n), base(base), combine(combine),
          adj(n), par(n, -1), depth(n, 0), sz(n, 1),
          heavy(n, -1), head(n, 0), pos(n, 0),
          edgeAbove(n, nullopt)
    {
        for (auto& [a, b, edgeVal] : edges) {
            adj[a].push_back({b, edgeVal});
            adj[b].push_back({a, edgeVal});
        }
        _dfsInit();
        _dfsDecompose();
        // build seg tree
        segN = 1;
        while (segN < n) segN <<= 1;
        seg.assign(2 * segN, nullopt);
        for (int i = 0; i < n; i++) {
            if (edgeAbove[i].has_value()) {
                seg[segN + pos[i]] = base(*edgeAbove[i]);
            }
        }
        for (int i = segN - 1; i >= 1; i--) {
            seg[i] = _combineOpt(seg[2*i], seg[2*i+1]);
        }
    }

    optional<EdgeData> _combineOpt(const optional<EdgeData>& a, const optional<EdgeData>& b) {
        if (!a.has_value()) return b;
        if (!b.has_value()) return a;
        return combine(*a, *b);
    }

    void _dfsInit() {
        // iterative, compute sz, par, depth, heavy
        vector<int> order;
        order.reserve(n);
        vector<tuple<int,int,int>> stack;
        stack.push_back({0, -1, 0});
        while (!stack.empty()) {
            auto [node, parent, d] = stack.back();
            stack.pop_back();
            par[node] = parent;
            depth[node] = d;
            order.push_back(node);
            for (auto& [nxt, edgeVal] : adj[node]) {
                if (nxt != parent) {
                    edgeAbove[nxt] = edgeVal; // push edge value onto child
                    stack.push_back({nxt, node, d + 1});
                }
            }
        }
        // process in reverse order to compute sz and heavy
        for (int i = (int)order.size() - 1; i >= 0; i--) {
            int node = order[i];
            int best = 0;
            for (auto& [nxt, edgeVal] : adj[node]) {
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
        vector<pair<int,int>> stack; // (node, chainHead)
        stack.push_back({0, 0});
        while (!stack.empty()) {
            auto [node, h] = stack.back();
            stack.pop_back();
            head[node] = h;
            pos[node] = timer++;
            // push light children first so they're processed AFTER heavy
            for (auto& [nxt, edgeVal] : adj[node]) {
                if (nxt == par[node] || nxt == heavy[node]) continue;
                stack.push_back({nxt, nxt});
            }
            if (heavy[node] != -1) {
                stack.push_back({heavy[node], h});
            }
        }
    }

    void pointSet(int node, RawT newEdgeVal) {
        if (node == 0) return; // root has no edge above
        int p = pos[node] + segN;
        seg[p] = base(newEdgeVal);
        for (p >>= 1; p > 0; p >>= 1) {
            seg[p] = _combineOpt(seg[2*p], seg[2*p+1]);
        }
    }

    void pointApply(int node, RawT delta) {
        if (node == 0) return;
        int p = pos[node] + segN;
        seg[p] = _combineOpt(seg[p], optional<EdgeData>(base(delta)));
        for (p >>= 1; p > 0; p >>= 1) {
            seg[p] = _combineOpt(seg[2*p], seg[2*p+1]);
        }
    }

    // a and b must be adjacent in the tree; the deeper one is the child whose slot stores this edge
    void edgeSet(int a, int b, RawT newEdgeVal) {
        int child = depth[a] > depth[b] ? a : b;
        pointSet(child, newEdgeVal);
    }

    void edgeApply(int a, int b, RawT delta) {
        int child = depth[a] > depth[b] ? a : b;
        pointApply(child, delta);
    }

    optional<EdgeData> _rangeQuery(int ql, int qr) {
        // inclusive [ql, qr]
        if (ql > qr) return nullopt;
        optional<EdgeData> res = nullopt;
        for (ql += segN, qr += segN + 1; ql < qr; ql >>= 1, qr >>= 1) {
            if (ql & 1) res = _combineOpt(res, seg[ql++]);
            if (qr & 1) res = _combineOpt(res, seg[--qr]);
        }
        return res;
    }

    // Path query over EDGES from a to b. Skips the LCA's slot since that represents
    // the edge ABOVE the LCA, which is not on the a-b path.
    // Caller must ensure a != b.
    EdgeData pathQuery(int a, int b) {
        optional<EdgeData> res = nullopt;
        while (head[a] != head[b]) {
            if (depth[head[a]] < depth[head[b]]) swap(a, b);
            auto chain = _rangeQuery(pos[head[a]], pos[a]);
            res = _combineOpt(res, chain);
            a = par[head[a]];
        }
        if (depth[a] > depth[b]) swap(a, b);
        // a is the LCA; skip its slot by querying [pos[a]+1, pos[b]]
        auto last = _rangeQuery(pos[a] + 1, pos[b]);
        return *_combineOpt(res, last);
    }

    // subtree edge query: edges from node down to all its descendants
    // = all stored slots in subtree EXCEPT node's own (which is the edge above node, not in subtree)
    // Caller must ensure node has at least one descendant.
    EdgeData subtreeQuery(int node) {
        return *_rangeQuery(pos[node] + 1, pos[node] + sz[node] - 1);
    }
};