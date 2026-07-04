#include <bits/stdc++.h>
using namespace std;
 
// struct EdgeData {
//     long long sum;
//     long long mx;
// };
// vector<pair<int,int>> edges = {{0,1},{0,2},{1,3}};

// vals[node] stores the raw edge data above that node
// vector<long long> vals = {0, 5, 7, 3};  // vals[0]=dummy(root); edge(1->0)=5, edge(2->0)=7, edge(3->1)=3
// auto base = [&](long long w) -> EdgeData {
//     return {w, w};
// };
// auto merge = [&](EdgeData a, EdgeData b) -> EdgeData {
//     return {a.sum + b.sum, max(a.mx, b.mx)};
// };
// auto lifter  = makeLiftEdge(0, edges, vals, base, merge);          // 0-indexed nodes
// auto lifter1 = makeLiftEdge(1, edges, vals, base, merge, false);   // 1-indexed nodes
// lifter.pathQuery(3, 2)  ->  optional<EdgeData>{ sum=15, mx=7 }     // edges 3 + 5 + 7
 
// root = the root node (usually 0 or 1), separate from if the nodes are 0...n-1 or 1...n
// edges = {{a, b}, {c, d}, ...}
// vals = raw data for the edge ABOVE each node (the edge from that node to its parent)
// vals[root] is a dummy and is never read
// if zeroIndexed=false then vals[0] is also a dummy (padding; no node has id 0)
// base = (rawEdge) -> mapped val
// merge(edgeVal1, edgeVal2) -> edgeVal3
// zeroIndexed=true means nodes are from 0...n-1, otherwise 1...n
template<typename T, typename V, typename BaseFn, typename MergeFn>
struct LiftEdge {
    int n, LOG;
    vector<int> dep;
    vector<vector<int>> up;
    vector<vector<optional<T>>> upData;
    BaseFn baseFn;
    MergeFn mergeFn;
    vector<V> vals;

    optional<T> mergeOpt(optional<T> a, optional<T> b) {
        if (!a) return b;
        if (!b) return a;
        return mergeFn(*a, *b);
    }

    // O(n log n) build time and space
    LiftEdge(int root, vector<pair<int,int>>& edges, vector<V>& vals,
             BaseFn baseFn, MergeFn mergeFn, bool zeroIndexed = true)
        : baseFn(baseFn), mergeFn(mergeFn), vals(vals) {
        n = edges.size() + (zeroIndexed ? 1 : 2);
        LOG = max(1, __lg(n) + 1);
        dep.assign(n, 0);
        up.assign(LOG, vector<int>(n));
        upData.assign(LOG, vector<optional<T>>(n, nullopt));
        vector<vector<int>> g(n);
        for (auto [u, v] : edges) {
            g[u].push_back(v);
            g[v].push_back(u);
        }
        vector<bool> vis(n, false);
        queue<int> q;
        q.push(root);
        vis[root] = true;
        up[0][root] = root;
        while (!q.empty()) {
            int v = q.front(); q.pop();
            for (int u : g[v]) {
                if (vis[u]) continue;
                vis[u] = true;
                dep[u] = dep[v] + 1;
                up[0][u] = v;
                upData[0][u] = baseFn(vals[u]);   // edge above u
                q.push(u);
            }
        }
        for (int k = 1; k < LOG; k++)
            for (int v = 0; v < n; v++) {
                up[k][v] = up[k-1][up[k-1][v]];
                upData[k][v] = mergeOpt(upData[k-1][v], upData[k-1][up[k-1][v]]);
            }
    }

    // kth steps above `node`
    // always returns root if k steps shoots past the root
    // O(log N)
    int kthAncestor(int node, int kth) {
        for (int k = 0; k < LOG; k++)
            if ((kth >> k) & 1) node = up[k][node];
        return node;
    }

    // O(log N)
    int lca(int a, int b) {
        if (dep[a] < dep[b]) swap(a, b);
        a = kthAncestor(a, dep[a] - dep[b]);
        if (a == b) return a;
        for (int k = LOG - 1; k >= 0; k--)
            if (up[k][a] != up[k][b]) { a = up[k][a]; b = up[k][b]; }
        return up[0][a];
    }

    // unweighted path distance from A<>B
    // O(log N)
    int pathDist(int a, int b) {
        return dep[a] + dep[b] - 2 * dep[lca(a, b)];
    }

    // the median node, which is the only node on all three paths: A<>B, B<>C, A<>C
    // O(log N)
    int median(int a, int b, int c) {
        return lca(a, b) ^ lca(a, c) ^ lca(b, c);
    }

    // k-th node on the A->B path, 1-indexed
    // -1 if OOB
    // O(log N)
    int kthOnPath(int a, int b, int kth) {
        int l = lca(a, b);
        int da = dep[a] - dep[l], db = dep[b] - dep[l];
        if (kth < 1 || kth > da + db + 1) return -1;
        if (kth <= da + 1) return kthAncestor(a, kth - 1);
        return kthAncestor(b, db - (kth - da - 1));
    }

    // how many edges to cross to get from `node` onto any node on the A<>B path
    // O(log N)
    int distToPath(int a, int b, int node) {
        return pathDist(median(a, b, node), node);
    }

    // returns a bool if `node` is on the path A<>B
    // O(log N)
    bool inPath(int a, int b, int node) {
        return median(a, b, node) == node;
    }

    // aggregated edgeValue for the k edges going up from `node` (edge above node first), nullopt if k==0
    // O(log N)
    optional<T> liftQuery(int node, int k) {
        optional<T> acc = nullopt;
        int rem = k;
        for (int i = LOG - 1; i >= 0; i--)
            if (rem >= (1 << i)) {
                acc = mergeOpt(acc, upData[i][node]);
                node = up[i][node];
                rem -= (1 << i);
            }
        return acc;
    }

    // aggregated edgeValue for the A<>B path (edge above the LCA is NOT on the path); nullopt if A==B
    // O(log N)
    optional<T> pathQuery(int a, int b) {
        int l = lca(a, b);
        int da = dep[a] - dep[l], db = dep[b] - dep[l];
        optional<T> left  = da > 0 ? liftQuery(a, da) : nullopt;
        optional<T> right = db > 0 ? liftQuery(b, db) : nullopt;
        return mergeOpt(left, right);
    }

    // lca of a and b if the tree were rooted at r instead of the build root
    // O(log N)
    int lcaUnderR(int r, int a, int b) {
        return median(a, b, r);
    }
};

template<typename V, typename BaseFn, typename MergeFn>
auto makeLiftEdge(int root, vector<pair<int,int>>& edges, vector<V>& vals,
                  BaseFn base, MergeFn merge, bool zeroIndexed = true) {
    using T = invoke_result_t<BaseFn, V>;
    return LiftEdge<T, V, BaseFn, MergeFn>(root, edges, vals, base, merge, zeroIndexed);
}