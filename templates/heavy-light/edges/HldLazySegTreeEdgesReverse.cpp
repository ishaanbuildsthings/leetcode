#include <bits/stdc++.h>
using namespace std;

// =============================================================================
// 0-INDEXED HLD WITH EDGE-WEIGHTED VARIANT, LAZY PROPAGATION + NON-COMMUTATIVE COMBINE
// =============================================================================
// N = number of nodes, root is node 0
// edges = vector of TUPLES like {a, b, edgeVal}, ... where edgeVal is the edge's value
// base(rawVal) -> stored data
// combine(data1, data2) -> aggregated data (NON-commutative; data1 is to the LEFT of data2 on the path)
// applyLazy(lazy, data, segLen) -> data after applying lazy over segLen positions
//   segLen is # of underlying positions covered by data, I just exposed it here
// composeLazies(oldLazy, newLazy) -> combined lazy
// reversal(data) -> data as if the underlying segment were reversed (for non-commutative path queries)
//
// Each edge's value is pushed onto its DEEPER endpoint (the child).
// The root has no edge above it, so its slot is unused (nullopt).
// Path/subtree updates and queries always SKIP the relevant LCA / root slot,
// so applyLazy is never invoked on a nullopt data slot.
//
//
// METHODS
// -------
// pointSet(node, newEdgeVal)            no-op if node is the root
// pointApply(node, lazyVal)             no-op if node is the root
// edgeSet(a, b, newEdgeVal)             a and b must be adjacent
// edgeApply(a, b, lazyVal)              a and b must be adjacent
// pathApply(a, b, lazyVal)              applies to all EDGES on path a..b (direction-agnostic)
// subtreeApply(node, lazyVal)           applies to edges from node down to all descendants (NOT the edge above node)
// pathQuery(a, b)                       in path order from a to b. CALLER MUST ENSURE a != b
// subtreeQuery(node)                    edges in subtree, NOT the edge above node. CALLER MUST ENSURE node has a descendant
//
// we don't need a baseLazy() or anything like that, because initially all lazy tags are nullopt,
// and if we apply a lazy to that it just uses the new lazy entirely
//
//
// LazyHLDEdge<RawT, EdgeData, LazyTag> hld(n, edges, base, combine, applyLazy, composeLazies, reversal);
// =============================================================================

template <typename RawT, typename EdgeData, typename LazyT>
struct LazyHLDEdge {
    int n;
    function<EdgeData(RawT)> base;
    function<EdgeData(EdgeData, EdgeData)> combine;
    function<EdgeData(LazyT, EdgeData, int)> applyLazy;
    function<LazyT(LazyT, LazyT)> composeLazies;
    function<EdgeData(EdgeData)> reverse;
    vector<vector<pair<int,RawT>>> adj;
    vector<int> par, depth, sz, heavy, head, pos;
    vector<optional<RawT>> edgeAbove;
    int segN, LOG;
    vector<optional<EdgeData>> tree;
    vector<optional<LazyT>> lazy;

    LazyHLDEdge(int n,
        const vector<tuple<int,int,RawT>>& edges,
        function<EdgeData(RawT)> base,
        function<EdgeData(EdgeData, EdgeData)> combine,
        function<EdgeData(LazyT, EdgeData, int)> applyLazy,
        function<LazyT(LazyT, LazyT)> composeLazies,
        function<EdgeData(EdgeData)> reverse)
        : n(n), base(base), combine(combine), applyLazy(applyLazy), composeLazies(composeLazies), reverse(reverse),
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
        segN = 1;
        while (segN < max(n, 1)) segN <<= 1;
        LOG = max(1, __lg(segN));
        tree.assign(2 * segN, nullopt);
        lazy.assign(segN, nullopt);
        for (int i = 0; i < n; i++) {
            if (edgeAbove[i].has_value()) {
                tree[segN + pos[i]] = base(*edgeAbove[i]);
            }
        }
        for (int i = segN - 1; i >= 1; i--) {
            tree[i] = _combineOpt(tree[2*i], tree[2*i+1]);
        }
    }

    optional<EdgeData> _combineOpt(const optional<EdgeData>& a, const optional<EdgeData>& b) {
        if (!a.has_value()) return b;
        if (!b.has_value()) return a;
        return combine(*a, *b);
    }

    void _dfsInit() {
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
                    edgeAbove[nxt] = edgeVal;
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
        vector<pair<int,int>> stack;
        stack.push_back({0, 0});
        while (!stack.empty()) {
            auto [node, h] = stack.back();
            stack.pop_back();
            head[node] = h;
            pos[node] = timer++;
            for (auto& [nxt, edgeVal] : adj[node]) {
                if (nxt == par[node] || nxt == heavy[node]) continue;
                stack.push_back({nxt, nxt});
            }
            if (heavy[node] != -1) {
                stack.push_back({heavy[node], h});
            }
        }
    }

    int _segLenAt(int p) {
        return segN >> (__lg(p));
    }

    void _apply(int p, const LazyT& lazyVal, int segLen) {
        tree[p] = applyLazy(lazyVal, *tree[p], segLen);
        if (p < segN) {
            if (!lazy[p].has_value()) lazy[p] = lazyVal;
            else lazy[p] = composeLazies(*lazy[p], lazyVal);
        }
    }

    void _push(int p) {
        if (p < segN && lazy[p].has_value()) {
            int childSegLen = _segLenAt(2*p);
            _apply(2*p, *lazy[p], childSegLen);
            _apply(2*p+1, *lazy[p], childSegLen);
            lazy[p] = nullopt;
        }
    }

    void _pushTo(int p) {
        for (int s = LOG; s >= 1; s--) _push(p >> s);
    }

    void _pullFrom(int p) {
        for (p >>= 1; p > 0; p >>= 1) {
            auto newVal = _combineOpt(tree[2*p], tree[2*p+1]);
            if (lazy[p].has_value() && newVal.has_value()) {
                newVal = applyLazy(*lazy[p], *newVal, _segLenAt(p));
            }
            tree[p] = newVal;
        }
    }

    void _segUpdate(int l, int r, const LazyT& lazyVal) {
        if (l > r) return;
        l += segN;
        r += segN + 1;
        int l0 = l, r0 = r;
        _pushTo(l0);
        _pushTo(r0 - 1);
        int segLen = 1;
        int ll = l, rr = r;
        while (ll < rr) {
            if (ll & 1) { _apply(ll, lazyVal, segLen); ll++; }
            if (rr & 1) { rr--; _apply(rr, lazyVal, segLen); }
            ll >>= 1; rr >>= 1;
            segLen <<= 1;
        }
        _pullFrom(l0);
        _pullFrom(r0 - 1);
    }

    optional<EdgeData> _segQuery(int l, int r) {
        // combined data over [l, r] in DFS-position order (left-to-right)
        if (l > r) return nullopt;
        l += segN;
        r += segN + 1;
        _pushTo(l);
        _pushTo(r - 1);
        optional<EdgeData> resL = nullopt, resR = nullopt;
        while (l < r) {
            if (l & 1) { resL = _combineOpt(resL, tree[l]); l++; }
            if (r & 1) { r--; resR = _combineOpt(tree[r], resR); }
            l >>= 1; r >>= 1;
        }
        return _combineOpt(resL, resR);
    }

    void _segPointSet(int idx, const EdgeData& newData) {
        int p = idx + segN;
        _pushTo(p);
        tree[p] = newData;
        for (p >>= 1; p > 0; p >>= 1) {
            auto newVal = _combineOpt(tree[2*p], tree[2*p+1]);
            if (lazy[p].has_value() && newVal.has_value()) {
                newVal = applyLazy(*lazy[p], *newVal, _segLenAt(p));
            }
            tree[p] = newVal;
        }
    }

    void pointSet(int node, RawT newEdgeVal) {
        if (node == 0) return; // root has no edge above
        _segPointSet(pos[node], base(newEdgeVal));
    }

    void pointApply(int node, LazyT lazyVal) {
        if (node == 0) return;
        int p = pos[node];
        _segUpdate(p, p, lazyVal);
    }

    // a and b must be adjacent in the tree; the deeper one is the child whose slot stores this edge
    void edgeSet(int a, int b, RawT newEdgeVal) {
        int child = depth[a] > depth[b] ? a : b;
        pointSet(child, newEdgeVal);
    }

    void edgeApply(int a, int b, LazyT lazyVal) {
        int child = depth[a] > depth[b] ? a : b;
        pointApply(child, lazyVal);
    }

    void pathApply(int a, int b, LazyT lazyVal) {
        while (head[a] != head[b]) {
            if (depth[head[a]] < depth[head[b]]) swap(a, b);
            _segUpdate(pos[head[a]], pos[a], lazyVal);
            a = par[head[a]];
        }
        if (depth[a] > depth[b]) swap(a, b);
        // a is the LCA; skip its slot by updating [pos[a]+1, pos[b]]
        _segUpdate(pos[a] + 1, pos[b], lazyVal);
    }

    void subtreeApply(int node, LazyT lazyVal) {
        _segUpdate(pos[node] + 1, pos[node] + sz[node] - 1, lazyVal);
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
                auto chunk = _segQuery(pos[head[a]], pos[a]);
                leftPieces.push_back(reverse(*chunk));
                a = par[head[a]];
            } else {
                auto chunk = _segQuery(pos[head[b]], pos[b]);
                rightPieces.push_back(reverse(*chunk));
                b = par[head[b]];
            }
        }
        if (depth[a] >= depth[b]) {
            // b is the LCA (or a == b); skip its slot by querying [pos[b]+1, pos[a]]
            auto chunk = _segQuery(pos[b] + 1, pos[a]);
            if (chunk.has_value()) leftPieces.push_back(reverse(*chunk));
        } else {
            // a is the LCA; skip its slot by querying [pos[a]+1, pos[b]]
            auto chunk = _segQuery(pos[a] + 1, pos[b]);
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

    EdgeData subtreeQuery(int node) {
        return *_segQuery(pos[node] + 1, pos[node] + sz[node] - 1);
    }
};
