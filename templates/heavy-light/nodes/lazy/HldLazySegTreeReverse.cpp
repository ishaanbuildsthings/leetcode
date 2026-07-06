#include <bits/stdc++.h>
using namespace std;
using ll = long long;


// EXAMPLE
// using RawVal = ll; // the raw node value input, could also be a struct

// // Accumulated node data
// struct NodeData {
//     ll total, pref, suf, best;
//     int len;
// };

// // Maps the raw node value to our NodeData
// auto base = [](RawVal v) -> NodeData {
//     return NodeData{v, v, v, v, 1};
// };

// // How to aggregate two NodeData nodes, order matters
// auto mergeFn = [](NodeData A, NodeData B) -> NodeData {
//     return NodeData{
//         A.total + B.total,
//         max(A.pref, A.total + B.pref),
//         max(B.suf,  B.total + A.suf),
//         max({A.best, B.best, A.suf + B.pref}),
//         A.len + B.len
//     };
// };

// // The lazy data each node stores, could be a `using` too
// struct LazyTag {
//     ll assignVal;
// };

// // How to apply a lazy update to a NodeData
// auto applyLazy = [](LazyTag lazy, NodeData nodeData) -> NodeData {
//     ll whole = lazy.assignVal * nodeData.len;
//     ll bestOne = max(lazy.assignVal, whole);
//     return NodeData{whole, bestOne, bestOne, bestOne, nodeData.len};
// };

// // How to combine two lazies
// auto composeLazies = [](LazyTag a, LazyTag b) -> LazyTag {
//     return b;
// };

// How to reverse a NodeData
// auto reverseFn = [](NodeData nodeData) -> NodeData {
//     return NodeData{nodeData.total, nodeData.suf, nodeData.pref, nodeData.best, nodeData.len};
// };


// TO CREATE THE HLD (O(n) build time)
// RawVal, NodeData, LazyTag are the types
// edges should be vector<pair<int,int>> with node labels (either 0...n-1, or 1...n)
// vals[node] is the value AT that node, if the nodes are 1...n then vals[0] can be whatever dummy value
// 1 at the end is the root, it can be any value in the tree, separate from if the nodes are 0...n-1 or 1...n
// last param is `zeroIndexed`, so false means the nodes are 1...n
// HldLazySegTreeReverse<RawVal, NodeData, LazyTag> hld(edges, vals, base, mergeFn, applyLazy, composeLazies, reverseFn, 1, false);


// METHODS

// O(logN)
// pointSet(nodeLabel, RawVal), overwrites the value at `nodeLabel` with this new raw value

// O(logN)
// pointApply(nodeLabel, LazyTag), directly apply a lazy update to `nodeLabel`

// O(log^2 N)
// pathApply(a, b, LazyTag), applies this lazy update to the entire path a...b, not an ordered update or anything, since the same LazyTag is just going on the whole path

// O(log^2 N)
// pathQuery(a, b) -> NodeData, gives us the aggregated data on the path a->b, includes both endpoints

// O(log N)
// subtreeApply(nodeLabel, LazyTag), applies this update to all nodes in the subtree of nodeLabel, includes nodeLabel itself

// O(log N)
// subtreeQuery(nodeLabel) -> NodeData, aggregated data of all nodes in the subtree (orientation is unspecified / not ordered), includes nodeLabel itself


template <typename RawT, typename StoredT, typename LazyT>
struct HldLazySegTreeReverse {
    int n, root, arrSize;
    bool zeroIndexed;
    function<StoredT(RawT)> base;
    function<StoredT(StoredT, StoredT)> combine;
    function<StoredT(LazyT, StoredT)> applyLazy;
    function<LazyT(LazyT, LazyT)> composeLazies;
    function<StoredT(StoredT)> reverse_;
    vector<vector<int>> adj;
    vector<int> par, depth, sz, heavy, head, pos;
    int segN, LOG;
    vector<optional<StoredT>> tree;
    vector<optional<LazyT>> lazy;

    HldLazySegTreeReverse(
        const vector<pair<int,int>>& edges,
        const vector<RawT>& vals,
        function<StoredT(RawT)> base,
        function<StoredT(StoredT, StoredT)> combine,
        function<StoredT(LazyT, StoredT)> applyLazy,
        function<LazyT(LazyT, LazyT)> composeLazies,
        function<StoredT(StoredT)> reverse_,
        int root,
        bool zeroIndexed)
        : n((int)edges.size() + 1), root(root),
          arrSize(zeroIndexed ? (int)edges.size() + 1 : (int)edges.size() + 2), zeroIndexed(zeroIndexed),
          base(base), combine(combine), applyLazy(applyLazy), composeLazies(composeLazies), reverse_(reverse_),
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
        lazy.assign(segN, nullopt);
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

    optional<StoredT> _reverseOpt(const optional<StoredT>& a) {
        if (!a.has_value()) return a;
        return reverse_(*a);
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

    void _apply(int p, const LazyT& lazyVal) {
        if (!tree[p].has_value()) return;
        tree[p] = applyLazy(lazyVal, *tree[p]);
        if (p < segN) {
            if (!lazy[p].has_value()) lazy[p] = lazyVal;
            else lazy[p] = composeLazies(*lazy[p], lazyVal);
        }
    }

    void _push(int p) {
        if (p < segN && lazy[p].has_value()) {
            _apply(2*p, *lazy[p]);
            _apply(2*p+1, *lazy[p]);
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
                newVal = applyLazy(*lazy[p], *newVal);
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
        int ll = l, rr = r;
        while (ll < rr) {
            if (ll & 1) { _apply(ll, lazyVal); ll++; }
            if (rr & 1) { rr--; _apply(rr, lazyVal); }
            ll >>= 1; rr >>= 1;
        }
        _pullFrom(l0);
        _pullFrom(r0 - 1);
    }

    optional<StoredT> _segQuery(int l, int r) {
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

    void _segPointSet(int idx, const optional<StoredT>& newData) {
        int p = idx + segN;
        _pushTo(p);
        tree[p] = newData;
        for (p >>= 1; p > 0; p >>= 1) {
            auto newVal = _combineOpt(tree[2*p], tree[2*p+1]);
            if (lazy[p].has_value() && newVal.has_value()) {
                newVal = applyLazy(*lazy[p], *newVal);
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

    // ORDERED path query a -> b, includes both endpoints.
    // Each _segQuery chunk is stored ancestor->descendant (pos-increasing). We split the
    // path at the LCA, giving the LCA node to the b-side. As we climb, each newly fetched
    // chunk is higher up, so we PREPEND it (_combineOpt(chunk, acc)) to keep each side
    // ordered top->bottom (ancestor->descendant). The b-side in that orientation is already
    // the correct forward order (lca->b). The a-side's real traversal is a->lca (exclusive
    // of lca), i.e. bottom->top, the reverse of how it's stored, so we reverse it first.
    StoredT pathQuery(int a, int b) {
        optional<StoredT> accA = nullopt;   // a-side nodes below the LCA, ancestor->descendant
        optional<StoredT> accB = nullopt;   // b-side nodes plus the LCA, ancestor->descendant
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
        // same chain: shallower endpoint is the LCA; the LCA node goes to the b-side
        if (depth[ca] > depth[cb]) {
            accA = _combineOpt(_segQuery(pos[cb] + 1, pos[ca]), accA);
            accB = _combineOpt(_segQuery(pos[cb], pos[cb]), accB);
        } else {
            accB = _combineOpt(_segQuery(pos[ca], pos[cb]), accB);
        }
        return *_combineOpt(_reverseOpt(accA), accB);
    }

    StoredT subtreeQuery(int node) {
        return *_segQuery(pos[node], pos[node] + sz[node] - 1);
    }
};