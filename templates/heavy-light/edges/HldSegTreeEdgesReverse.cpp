#include <bits/stdc++.h>
using namespace std;

// =============================================================================
// 0-INDEXED HLD WITH EDGE-WEIGHTED VARIANT, NON-COMMUTATIVE COMBINE
// =============================================================================
// N = number of nodes, root is node 0
// edges = vector of TUPLES like {a, b, edgeVal}, ... where edgeVal is the edge's value
// base(val) -> stored data
// combine(data1, data2) -> aggregated data (NON-commutative; data1 is to the LEFT of data2 on the path)
// reversal(data) -> data as if the underlying segment were reversed (for non-commutative path queries)
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
//   Aggregated data over the EDGES on path a..b, in path order from a to b.
//   CALLER MUST ENSURE a != b (empty path is undefined behavior).
//
// subtreeQuery(node) -> EdgeData
//   Aggregated data over edges from node down to all its descendants, in DFS order.
//   The edge ABOVE node itself is NOT included.
//   CALLER MUST ENSURE node has at least one descendant (leaf is undefined behavior).
//
//
// EXAMPLE: path concatenation over edge labels
// --------------------------------------------
//   using RawT     = string;
//   using EdgeData = string;
//
//   auto base = [](RawT v) -> EdgeData {
//       return v;
//   };
//   auto combine = [](EdgeData a, EdgeData b) -> EdgeData {
//       return a + b;
//   };
//   auto reversal = [](EdgeData d) -> EdgeData {
//       reverse(d.begin(), d.end());
//       return d;
//   };
//
//   // edges shape: each entry is {nodeA, nodeB, rawT}
//   vector<tuple<int,int,RawT>> edges = {
//       {0, 1, "a"},
//       {1, 2, "b"},
//       {0, 3, "c"},
//   };
//
//   HLDEdge<RawT, EdgeData> hld(n, edges, base, combine, reversal);
//
//   EdgeData answer = hld.pathQuery(2, 3);
//   cout << answer << "\n";
// =============================================================================

template <typename RawT, typename EdgeData>
struct HLDEdge {
    int n;
    function<EdgeData(RawT)> base;
    function<EdgeData(EdgeData, EdgeData)> combine;
    function<EdgeData(EdgeData)> reverse;
    vector<vector<pair<int,RawT>>> adj; // adj[u] = list of (neighbor, edgeVal)
    vector<int> par, depth, sz, heavy, head, pos;
    vector<optional<RawT>> edgeAbove; // edge value above each node; nullopt for root
    int segN;
    // use optional<EdgeData> internally so we can represent "nothing here" without an identity
    vector<optional<EdgeData>> seg;

    HLDEdge(int n,
        const vector<tuple<int,int,RawT>>& edges,
        function<EdgeData(RawT)> base,
        function<EdgeData(EdgeData, EdgeData)> combine,
        function<EdgeData(EdgeData)> reverse)
        : n(n), base(base), combine(combine), reverse(reverse),
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
        // inclusive [ql, qr], combined in left-to-right order
        if (ql > qr) return nullopt;
        optional<EdgeData> resL = nullopt, resR = nullopt;
        for (ql += segN, qr += segN + 1; ql < qr; ql >>= 1, qr >>= 1) {
            if (ql & 1) { resL = _combineOpt(resL, seg[ql]); ql++; }
            if (qr & 1) { qr--; resR = _combineOpt(seg[qr], resR); }
        }
        return _combineOpt(resL, resR);
    }

    // Non-commutative path query over EDGES.
    // Each chain segment from seg comes in DFS order (chain top first, chain bottom last).
    // Path a -> LCA -> b. Collect chunks in path order:
    //   leftPieces: from a moving up, each chunk reversed so it reads "deep first" (a-side)
    //   rightPieces: from b moving up, each chunk reversed so it reads "deep first" (b-side)
    // The LCA's own slot is SKIPPED (it represents the edge ABOVE the LCA, not on the path).
    // Final: combine(leftAcc, rightAcc) where rightAcc is built from b inward to LCA,
    // then reversed piece-by-piece so it reads LCA-side first.
    // Caller must ensure a != b.
    EdgeData pathQuery(int a, int b) {
        vector<EdgeData> leftPieces, rightPieces;
        while (head[a] != head[b]) {
            if (depth[head[a]] >= depth[head[b]]) {
                auto chunk = _rangeQuery(pos[head[a]], pos[a]);
                leftPieces.push_back(reverse(*chunk));
                a = par[head[a]];
            } else {
                auto chunk = _rangeQuery(pos[head[b]], pos[b]);
                rightPieces.push_back(reverse(*chunk));
                b = par[head[b]];
            }
        }
        if (depth[a] >= depth[b]) {
            // b is the LCA (or a == b); skip its slot by querying [pos[b]+1, pos[a]]
            auto chunk = _rangeQuery(pos[b] + 1, pos[a]);
            if (chunk.has_value()) leftPieces.push_back(reverse(*chunk));
        } else {
            // a is the LCA; skip its slot by querying [pos[a]+1, pos[b]]
            auto chunk = _rangeQuery(pos[a] + 1, pos[b]);
            if (chunk.has_value()) rightPieces.push_back(reverse(*chunk));
        }
        optional<EdgeData> leftAcc = nullopt, rightAcc = nullopt;
        for (auto& p : leftPieces) {
            leftAcc = leftAcc.has_value() ? combine(*leftAcc, p) : p;
        }
        for (auto it = rightPieces.rbegin(); it != rightPieces.rend(); ++it) {
            auto rev = reverse(*it);
            rightAcc = rightAcc.has_value() ? combine(*rightAcc, rev) : rev;
        }
        if (!leftAcc.has_value()) return *rightAcc;
        if (!rightAcc.has_value()) return *leftAcc;
        return combine(*leftAcc, *rightAcc);
    }

    // subtree edge query: edges from node down to all its descendants
    // = all stored slots in subtree EXCEPT node's own (which is the edge above node, not in subtree)
    // Caller must ensure node has at least one descendant.
    EdgeData subtreeQuery(int node) {
        return *_rangeQuery(pos[node] + 1, pos[node] + sz[node] - 1);
    }
};
