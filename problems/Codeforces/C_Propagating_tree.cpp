#include <bits/stdc++.h>
using namespace std;

// 0-INDEXED, ALL INTERFACES OPERATE ON 0-indexed data, WORKS WITH ANY DATA TYPE
// N = number of nodes
// edges = vector of PAIRS like {a, b}, {c, d}, ...
// vals[node] -> raw value, like a letter or number
// base(rawVal) -> stored data (e.g. v -> {v, v} to track min and max)
// combine(data1, data2) -> aggregated data

// pointSet(node, rawVal) - overwrite the data in a point
// pointApply(node, delta) - apply an operation to a point, so for instance we XOR an old value with the delta, or add it
// pathQuery(a, b) -> aggregated data over path
// subtreeQuery(node) -> aggregated data over subtree

// using RawT = int;       // the input value at each node
// using NodeData = int;   // what we store in seg tree (just the max here)
//
// auto base = [](RawT v) -> NodeData {
//     return v;
// };
// auto combine = [](NodeData a, NodeData b) -> NodeData {
//     return max(a, b);
// };

// HLD<RawT, NodeData> hld(n, edges, arr, base, combine);
// NodeData mx = hld.pathQuery(u, v);

template <typename RawT, typename StoredT>
struct HLD {
    int n;
    function<StoredT(RawT, int)> base;
    function<StoredT(StoredT, StoredT)> combine;
    vector<vector<int>> adj;
    vector<int> par, depth, sz, heavy, head, pos;
    int segN;
    // use optional<StoredT> so we can represent "nothing here" without an identity
    vector<optional<StoredT>> seg;

    HLD(int n,
        const vector<pair<int,int>>& edges,
        const vector<RawT>& vals,
        function<StoredT(RawT, int)> base,
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
            seg[segN + pos[i]] = base(vals[i], depth[i]);
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
        seg[p] = base(rawVal, depth[node]);
        for (p >>= 1; p > 0; p >>= 1) {
            seg[p] = _combineOpt(seg[2*p], seg[2*p+1]);
        }
    }

    void pointApply(int node, RawT delta) {
        int p = pos[node] + segN;
        seg[p] = _combineOpt(seg[p], optional<StoredT>(base(delta, depth[node])));
        for (p >>= 1; p > 0; p >>= 1) {
            seg[p] = _combineOpt(seg[p], optional<StoredT>(base(delta, depth[node])));
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



#include <bits/stdc++.h>
using namespace std;
using ll = long long;

using RawT = int; // raw array data
struct NodeData {
    int evenDepthSum = 0;
    int oddDepthSum = 0;
};

auto base = [](RawT v, int depth) -> NodeData {
    NodeData out;
    if (depth % 2 == 0) {
        out.evenDepthSum = v;
    } else {
        out.oddDepthSum = v;
    }
    return out;
};
auto combine = [](NodeData a, NodeData b) -> NodeData {
    NodeData out;
    out.evenDepthSum = a.evenDepthSum + b.evenDepthSum;
    out.oddDepthSum = a.oddDepthSum + b.oddDepthSum;
    return out;
};


int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m; cin >> n >> m;
    vector<int> A(n); for (int i = 0; i < n; i++) cin >> A[i];
    vector<int> initial(n, 0);
    vector<pair<int,int>> edges;
    for (int i = 0; i < n - 1; i++) {
        int a, b; cin >> a >> b; a--; b--; edges.push_back({a, b});
    }
    HLD<RawT, NodeData> hld(n, edges, initial, base, combine);
    for (int i = 0; i < m; i++) {
        int qtype; cin >> qtype;
        if (qtype == 1) {
            int node, add; cin >> node >> add; node--;
            hld.pointApply(node, add); // add this delta to a single node
            // we have some leaf node there storing the odd depth and even depth sums, one gets pudated
        } else {
            int node; cin >> node; node--;
            // anything above me on the same depth parity gets added
            // anything above me on the same depth parity gets subtracted
            NodeData nodeVal = hld.pathQuery(node, 0);
            int nodeDepth = hld.depth[node];
            if (nodeDepth % 2 == 0) {
                int added = nodeVal.evenDepthSum;
                int lost = nodeVal.oddDepthSum;
                cout << A[node] + added - lost << '\n';
            } else {
                cout << A[node] + nodeVal.oddDepthSum - nodeVal.evenDepthSum << '\n';
            }
        }
    }
}