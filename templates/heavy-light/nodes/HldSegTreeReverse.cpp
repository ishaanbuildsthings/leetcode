#include <bits/stdc++.h>
using namespace std;

// 0-INDEXED, ALL INTERFACES OPERATE ON 0-indexed data, WORKS WITH ANY DATA TYPE
// N = number of nodes
// edges = vector of PAIRS like {a, b}, {c, d}, ...
// vals[node] -> raw value, like a letter or number
// base(rawVal) -> stored data (e.g. v -> {v, v} to track min and max)
// combine(data1, data2) -> aggregated data (NON-commutative; data1 is to the LEFT of data2 on the path)
// reversal(data) -> data as if the underlying segment were reversed (for non-commutative path queries)

// pointSet(node, val) - overwrites the point with a new value, like a letter
// pointApply(node, delta) - applies a delta to the old value, like we can XOR or add
// pathQuery(a, b) -> aggregated data over path
// subtreeQuery(node) -> aggregated data over subtree

// using RawT = int;                                // the input value at each node (e.g. 1 = black, 0 = white)
// using NodeData = tuple<int,int,int,int,int,int>; // (len, B, prefW, sufW, ww, badT)
// or can do struct NodeData {...};
//
// auto base = [](RawT v) -> NodeData {
//     return v == 1 ? make_tuple(1, 1, 0, 0, 0, 0) : make_tuple(1, 0, 1, 1, 0, 0);
// };
// auto combine = [](NodeData a, NodeData b) -> NodeData {
//     // ... aggregate left + right, taking ordering into account ...
// };
// auto reversal = [](NodeData d) -> NodeData {
//     // swap prefW <-> sufW, other fields stay the same
//     auto [length, B, prefW, sufW, ww, badT] = d;
//     return make_tuple(length, B, sufW, prefW, ww, badT);
// };
//
// HLD<RawT, NodeData> hld(n, edges, arr, base, combine, reversal);
// NodeData res = hld.pathQuery(u, v);

template <typename RawT, typename StoredT>
struct HLD {
    int n;
    function<StoredT(RawT)> base;
    function<StoredT(StoredT, StoredT)> combine;
    function<StoredT(StoredT)> reverse;
    vector<vector<int>> adj;
    vector<int> par, depth, sz, heavy, head, pos;
    int segN;
    // use optional<StoredT> so we can represent "nothing here" without an identity
    vector<optional<StoredT>> seg;

    HLD(int n,
        const vector<pair<int,int>>& edges,
        const vector<RawT>& vals,
        function<StoredT(RawT)> base,
        function<StoredT(StoredT, StoredT)> combine,
        function<StoredT(StoredT)> reverse)
        : n(n), base(base), combine(combine), reverse(reverse),
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

    void pointApply(int node, RawT delta) {
        int p = pos[node] + segN;
        seg[p] = _combineOpt(seg[p], optional<StoredT>(base(delta)));
        for (p >>= 1; p > 0; p >>= 1) {
            seg[p] = _combineOpt(seg[2*p], seg[2*p+1]);
        }
    }

    optional<StoredT> _rangeQuery(int ql, int qr) {
        // inclusive [ql, qr], combined in left-to-right order
        optional<StoredT> resL = nullopt, resR = nullopt;
        for (ql += segN, qr += segN + 1; ql < qr; ql >>= 1, qr >>= 1) {
            if (ql & 1) { resL = _combineOpt(resL, seg[ql]); ql++; }
            if (qr & 1) { qr--; resR = _combineOpt(seg[qr], resR); }
        }
        return _combineOpt(resL, resR);
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
            auto chunk = _rangeQuery(pos[b], pos[a]);
            leftPieces.push_back(reverse(*chunk));
        } else {
            auto chunk = _rangeQuery(pos[a], pos[b]);
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
        return *_rangeQuery(pos[node], pos[node] + sz[node] - 1);
    }
};