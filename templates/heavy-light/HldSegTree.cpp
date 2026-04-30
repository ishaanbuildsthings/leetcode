#include <bits/stdc++.h>
using namespace std;

// 0-INDEXED, ALL INTERFACES OPERATE ON 0-indexed data, WORKS WITH ANY DATA TYPE
// N = number of nodes
// edges = vector of PAIRS like {a, b}, {c, d}, ...
// vals[node] -> value, like a letter or number
// base(nodeValue) -> stored data
// combine(node1data, node2data) -> aggregate data

// pointSet(node, newValue) like a new letter
// pointApply(node, delta) adds +delta (used if we stored sums)
// pathQuery(a, b) -> gives us aggregated data
// subtreeQuery(a) -> gives us subtree data for that

// HLD<RawT, StoredT> hld(numNodes, edgeList, vals, baseFn, combineFn)

// EXAMPLE
// auto base = [](int v) { return v; };
// auto combine = [](int a, int b) { return max(a, b); };
// HLD<int,int> hld(n, edges, arr, base, combine);

template <typename RawT, typename StoredT>
struct HLD {
    int n;
    function<StoredT(RawT)> base;
    function<StoredT(StoredT, StoredT)> combine;
    vector<vector<int>> adj;
    vector<int> par, depth, sz, heavy, head, pos;
    int segN;
    // use optional<StoredT> so we can represent "nothing here" without an identity
    vector<optional<StoredT>> seg;

    HLD(int n,
        const vector<pair<int,int>>& edges,
        const vector<RawT>& vals,
        function<StoredT(RawT)> base,
        function<StoredT(StoredT, StoredT)> combine)
        : n(n), base(base), combine(combine),
          adj(n), par(n, -1), depth(n, 0), sz(n, 1),
          heavy(n, -1), head(n, 0), pos(n, 0)
    {
        for (auto& [u, v] : edges) {
            adj[u].push_back(v);
            adj[v].push_back(u);
        }
        _dfsInit();
        _dfsDecompose();
        // build seg tree
        segN = 1;
        while (segN < n) segN <<= 1;
        seg.assign(2 * segN, nullopt);
        for (int i = 0; i < n; i++) {
            seg[segN + pos[i]] = base(vals[i]);
        }
        for (int i = segN - 1; i >= 1; i--) {
            seg[i] = _combineOpt(seg[2*i], seg[2*i+1]);
        }
    }

    optional<StoredT> _combineOpt(const optional<StoredT>& a, const optional<StoredT>& b) {
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
            for (int nxt : adj[node]) {
                if (nxt != parent) stack.push_back({nxt, node, d + 1});
            }
        }
        // process in reverse order to compute sz and heavy
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
        vector<pair<int,int>> stack; // (node, chainHead)
        stack.push_back({0, 0});
        while (!stack.empty()) {
            auto [node, h] = stack.back();
            stack.pop_back();
            head[node] = h;
            pos[node] = timer++;
            // push light children first so they're processed AFTER heavy
            for (int nxt : adj[node]) {
                if (nxt == par[node] || nxt == heavy[node]) continue;
                stack.push_back({nxt, nxt});
            }
            if (heavy[node] != -1) {
                stack.push_back({heavy[node], h});
            }
        }
    }

    void pointSet(int node, RawT rawVal) {
        int p = pos[node] + segN;
        seg[p] = base(rawVal);
        for (p >>= 1; p > 0; p >>= 1) {
            seg[p] = _combineOpt(seg[2*p], seg[2*p+1]);
        }
    }

    void pointApply(int node, RawT rawDelta) {
        int p = pos[node] + segN;
        seg[p] = _combineOpt(seg[p], optional<StoredT>(base(rawDelta)));
        for (p >>= 1; p > 0; p >>= 1) {
            seg[p] = _combineOpt(seg[2*p], seg[2*p+1]);
        }
    }

    optional<StoredT> _rangeQuery(int ql, int qr) {
        // inclusive [ql, qr]
        optional<StoredT> res = nullopt;
        for (ql += segN, qr += segN + 1; ql < qr; ql >>= 1, qr >>= 1) {
            if (ql & 1) res = _combineOpt(res, seg[ql++]);
            if (qr & 1) res = _combineOpt(res, seg[--qr]);
        }
        return res;
    }

    StoredT pathQuery(int a, int b) {
        optional<StoredT> res = nullopt;
        while (head[a] != head[b]) {
            if (depth[head[a]] < depth[head[b]]) swap(a, b);
            auto chain = _rangeQuery(pos[head[a]], pos[a]);
            res = _combineOpt(res, chain);
            a = par[head[a]];
        }
        if (depth[a] > depth[b]) swap(a, b);
        auto last = _rangeQuery(pos[a], pos[b]);
        res = _combineOpt(res, last);
        return *res;
    }

    StoredT subtreeQuery(int node) {
        return *_rangeQuery(pos[node], pos[node] + sz[node] - 1);
    }
};