#include <bits/stdc++.h>
using namespace std;

// 0-INDEXED, ALL INTERFACES OPERATE ON 0-indexed data, WORKS WITH ANY DATA TYPE
// N = number of nodes
// edges = vector of PAIRS like {a, b}, {c, d}, ...
// vals[node] -> raw value, like a letter or number
// base(rawVal) -> stored data (e.g. v -> {v, v} to track min and max)
// combine(data1, data2) -> aggregated data (NON-commutative; data1 is to the LEFT of data2 on the path)
// applyLazy(lazy, data, segLen) -> data after applying lazy over segLen positions
//   segLen is # of underlying positions covered by data, I just exposed it here
// composeLazies(oldLazy, newLazy) -> combined lazy
// reversal(data) -> data as if the underlying segment were reversed (for non-commutative path queries)

// pointSet(node, rawVal)
// pointApply(node, lazyVal)
// pathApply(a, b, lazyVal) - applies lazyVal to all nodes on path a..b
// subtreeApply(node, lazyVal) - applies lazyVal to entire subtree rooted at node
// pathQuery(a, b) -> aggregated data over path
// subtreeQuery(node) -> aggregated data over subtree
// we don't need a baseLazy() or anything like that, because initially all lazy tags are nullopt, and if we apply a lazy to that it just uses the new lazy entirely

// using RawT = long long;       // the input value at each node
// using NodeData = long long;   // what we store in seg tree (just the max)
// or can do struct NodeData {...};
// using LazyTag = long long;    // pending +d to add to every position
//
// auto base = [](RawT v) -> NodeData {
//     return v;
// };
// auto combine = [](NodeData a, NodeData b) -> NodeData {
//     return max(a, b);
// };

// we expose segLen in the class so it's used in the apply lazy
// auto applyLazy = [](LazyTag lz, NodeData d, int segLen) -> NodeData {
//     // adding lz to every element shifts the max by lz (segLen unused for max)
//     return d + lz;
// };

// auto composeLazies = [](LazyTag oldL, LazyTag newL) -> LazyTag {
//     // pending +oldL then +newL collapses to +(oldL+newL)
//     return oldL + newL;
// };

// reverse for non-commutative aggregates: returns NodeData as if the underlying segment were reversed
// auto reversal = [](NodeData d) -> NodeData {
//     // for max it's symmetric, so identity
//     return d;
// };
//
// LazyHLD<RawT, NodeData, LazyTag> hld(n, edges, arr, base, combine, applyLazy, composeLazies, reversal);
// hld.pathApply(u, v, 5);          // add 5 to every node on path u..v
// NodeData mx = hld.pathQuery(u, v);  // max along path

template <typename RawT, typename StoredT, typename LazyT>
struct LazyHLD {
    int n;
    function<StoredT(RawT)> base;
    function<StoredT(StoredT, StoredT)> combine;
    function<StoredT(LazyT, StoredT, int)> applyLazy;
    function<LazyT(LazyT, LazyT)> composeLazies;
    function<StoredT(StoredT)> reverse;
    vector<vector<int>> adj;
    vector<int> par, depth, sz, heavy, head, pos;
    int segN, LOG;
    vector<optional<StoredT>> tree;
    vector<optional<LazyT>> lazy;

    LazyHLD(int n,
        const vector<pair<int,int>>& edges,
        const vector<RawT>& vals,
        function<StoredT(RawT)> base,
        function<StoredT(StoredT, StoredT)> combine,
        function<StoredT(LazyT, StoredT, int)> applyLazy,
        function<LazyT(LazyT, LazyT)> composeLazies,
        function<StoredT(StoredT)> reverse)
        : n(n), base(base), combine(combine), applyLazy(applyLazy), composeLazies(composeLazies), reverse(reverse),
          adj(n), par(n, -1), depth(n, 0), sz(n, 1),
          heavy(n, -1), head(n, 0), pos(n, 0)
    {
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
        lazy.assign(segN, nullopt);
        for (int i = 0; i < n; i++) {
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
        stack.push_back({0, -1, 0});
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
        stack.push_back({0, 0});
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

    optional<StoredT> _segQuery(int l, int r) {
        // combined data over [l, r] in DFS-position order (left-to-right)
        if (l > r) return nullopt;
        l += segN;
        r += segN + 1;
        _pushTo(l);
        _pushTo(r - 1);
        optional<StoredT> resL = nullopt, resR = nullopt;
        while (l < r) {
            if (l & 1) { resL = _combineOpt(resL, tree[l]); l++; }
            if (r & 1) { r--; resR = _combineOpt(tree[r], resR); }
            l >>= 1; r >>= 1;
        }
        return _combineOpt(resL, resR);
    }

    void _segPointSet(int idx, const StoredT& newData) {
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

    void pointSet(int node, RawT rawVal) {
        _segPointSet(pos[node], base(rawVal));
    }

    void pointApply(int node, LazyT lazyVal) {
        int p = pos[node];
        _segUpdate(p, p, lazyVal);
    }

    void pathApply(int a, int b, LazyT lazyVal) {
        while (head[a] != head[b]) {
            if (depth[head[a]] < depth[head[b]]) swap(a, b);
            _segUpdate(pos[head[a]], pos[a], lazyVal);
            a = par[head[a]];
        }
        if (depth[a] > depth[b]) swap(a, b);
        _segUpdate(pos[a], pos[b], lazyVal);
    }

    void subtreeApply(int node, LazyT lazyVal) {
        _segUpdate(pos[node], pos[node] + sz[node] - 1, lazyVal);
    }

    // Non-commutative path query.
    // Each chain segment from seg comes in DFS order (chain top first, chain bottom last).
    // Path a -> LCA -> b. Collect chunks in path order:
    //   leftPieces: from a moving up, each chunk reversed so it reads "deep first" (a-side)
    //   rightPieces: from b moving up, each chunk reversed so it reads "deep first" (b-side)
    // Final: combine(leftAcc, rightAcc) where rightAcc is built from b inward to LCA,
    // then reversed piece-by-piece so it reads LCA-side first.
    StoredT pathQuery(int a, int b) {
        vector<StoredT> leftPieces, rightPieces;
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
            auto chunk = _segQuery(pos[b], pos[a]);
            leftPieces.push_back(reverse(*chunk));
        } else {
            auto chunk = _segQuery(pos[a], pos[b]);
            rightPieces.push_back(reverse(*chunk));
        }
        optional<StoredT> leftAcc = nullopt, rightAcc = nullopt;
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

    StoredT subtreeQuery(int node) {
        return *_segQuery(pos[node], pos[node] + sz[node] - 1);
    }
};