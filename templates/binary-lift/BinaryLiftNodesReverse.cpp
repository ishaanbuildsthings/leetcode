#include <bits/stdc++.h>
using namespace std;

// TEMPLATE BY ISHAANBUILDSTHINGS  (NON-COMMUTATIVE path queries via a reverse hook)
// EXAMPLE  (max-subsegment sum along a path)
// struct Sub { long long total, best, pref, suf; };
// auto base = [&](long long v) -> Sub {
//     long long e = max(0LL, v);
//     return {v, e, e, e};
// };
// auto mergeFn = [&](Sub L, Sub R) -> Sub {          // L is the LEFT part (closer to A) on the path
//     return { L.total + R.total,
//              max({L.best, R.best, L.suf + R.pref}),
//              max(L.pref, L.total + R.pref),
//              max(R.suf, R.total + L.suf) };
// };
// auto reverse = [&](Sub d) -> Sub { return {d.total, d.best, d.suf, d.pref}; };  // swap pref<->suf
// auto lifter = makeLift(0, edges, vals, base, mergeFn, reverse, false);
// lifter.pathQuery(a, b).best   ->  max subsegment sum reading A -> B

// root = the root node (usually 0 or 1), separate from if the nodes are 0...n-1 or 1...n
// edges = {{a, b}, {c, d}, ...}
// vals = list of raw node values, if zeroIndexed=false, then vals[0] can be any dummy value
// base = (rawVal) -> mapped val
// mergeFn(leftData, rightData) -> data   (NON-commutative; left is closer to A on the path)
// reverse(data) -> data as if its underlying segment were traversed the other way
//   (max-subsegment: swap pref<->suf ; plain sum/min/max: return data unchanged)
// zeroIndexed=true means nodes are from 0...n-1, otherwise 1...n
template<typename T, typename V, typename BaseFn, typename MergeFn, typename ReverseFn>
struct Lift {
    int n, LOG;
    vector<int> dep;
    vector<vector<int>> up;
    vector<vector<optional<T>>> upData;
    BaseFn baseFn;
    MergeFn mergeFn;
    ReverseFn reverseFn;
    vector<V> vals;

    optional<T> mergeOpt(optional<T> a, optional<T> b) {   // a is LEFT of b
        if (!a) return b;
        if (!b) return a;
        return mergeFn(*a, *b);
    }

    // build lifting + node-monoid tables.  O(n log n) time & space
    Lift(int root, vector<pair<int,int>>& edges, vector<V>& vals,
         BaseFn baseFn, MergeFn mergeFn, ReverseFn reverseFn, bool zeroIndexed)
        : baseFn(baseFn), mergeFn(mergeFn), reverseFn(reverseFn), vals(vals) {
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
                upData[0][u] = baseFn(vals[u]);          // node's OWN value (directional keying)
                q.push(u);
            }
        }
        for (int k = 1; k < LOG; k++)
            for (int v = 0; v < n; v++) {
                up[k][v] = up[k-1][up[k-1][v]];
                // shallower half (up[k-1][v]) is LEFT of deeper half (v): top-down order
                upData[k][v] = mergeOpt(upData[k-1][up[k-1][v]], upData[k-1][v]);
            }
    }

    T applyBase(int v) { return baseFn(vals[v]); }

    // kth steps above `node`; returns root if k shoots past the root.  O(log N)
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

    // unweighted path distance from A<>B.  O(log N)
    int pathDist(int a, int b) { return dep[a] + dep[b] - 2 * dep[lca(a, b)]; }

    // the median node, on all three paths A<>B, B<>C, A<>C.  O(log N)
    int median(int a, int b, int c) { return lca(a, b) ^ lca(a, c) ^ lca(b, c); }

    // k-th node on the A->B path, 1-indexed, -1 if OOB.  O(log N)
    int kthOnPath(int a, int b, int kth) {
        int l = lca(a, b);
        int da = dep[a] - dep[l], db = dep[b] - dep[l];
        if (kth < 1 || kth > da + db + 1) return -1;
        if (kth <= da + 1) return kthAncestor(a, kth - 1);
        return kthAncestor(b, db - (kth - da - 1));
    }

    // edge distance from `node` to the A<>B path.  O(log N)
    int distToPath(int a, int b, int node) { return pathDist(median(a, b, node), node); }

    // is `node` on the path A<>B.  O(log N)
    bool inPath(int a, int b, int node) { return median(a, b, node) == node; }

    // lca of a and b if the tree were rooted at r.  O(log N)
    int lcaUnderR(int r, int a, int b) { return median(a, b, r); }

    // intersection of path a<>b and path x<>y; {p,q} endpoints (p==q single), {-1,-1} disjoint. O(log N)
    pair<int,int> pathIntersection(int a, int b, int x, int y) {
        int cand[4] = { median(a, b, x), median(a, b, y), median(x, y, a), median(x, y, b) };
        int onBoth[4], m = 0;
        for (int i = 0; i < 4; i++)
            if (inPath(a, b, cand[i]) && inPath(x, y, cand[i])) onBoth[m++] = cand[i];
        if (m == 0) return {-1, -1};
        int p = onBoth[0], q = onBoth[0], best = -1;
        for (int i = 0; i < m; i++)
            for (int j = i; j < m; j++) {
                int d = pathDist(onBoth[i], onBoth[j]);
                if (d > best) { best = d; p = onBoth[i]; q = onBoth[j]; }
            }
        return {p, q};
    }

    // data over the k nodes from `node` going up (node included), in TOP-DOWN
    // path order (shallow -> deep).  nullopt if k == 0.  O(log N)
    optional<T> liftQuery(int node, int k) {
        optional<T> acc = nullopt;
        int rem = k;
        for (int i = LOG - 1; i >= 0; i--)
            if (rem >= (1 << i)) {
                acc = mergeOpt(upData[i][node], acc);   // new block is shallower -> LEFT of acc
                node = up[i][node];
                rem -= (1 << i);
            }
        return acc;
    }

    // aggregated data over the path A -> B, read in that direction (NON-commutative).  O(log N)
    T pathQuery(int a, int b) {
        int l = lca(a, b);
        int da = dep[a] - dep[l], db = dep[b] - dep[l];
        T res = applyBase(l);
        if (da > 0) res = mergeFn(reverseFn(*liftQuery(a, da)), res);  // a-arm reversed -> a..childOfL
        if (db > 0) res = mergeFn(res, *liftQuery(b, db));             // b-arm already childOfL..b
        return res;
    }
};

template<typename V, typename BaseFn, typename MergeFn, typename ReverseFn>
auto makeLift(int root, vector<pair<int,int>>& edges, vector<V>& vals,
              BaseFn base, MergeFn merge, ReverseFn reverse, bool zeroIndexed = true) {
    using T = invoke_result_t<BaseFn, V>;
    return Lift<T, V, BaseFn, MergeFn, ReverseFn>(root, edges, vals, base, merge, reverse, zeroIndexed);
}