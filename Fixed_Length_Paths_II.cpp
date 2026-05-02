// SOLUTION 0, O(n log^2 n) centroid decomp with Fenwick tree
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

static inline int read_int() {
    int x = 0, c = getchar_unlocked();
    while (c < '0' || c > '9') c = getchar_unlocked();
    while (c >= '0' && c <= '9') { x = x * 10 + (c - '0'); c = getchar_unlocked(); }
    return x;
}

struct BIT {
    int n;
    vector<int> t;
    BIT(int n_) : n(n_), t(n_ + 2, 0) {}
    void add(int i, int v) { for (++i; i <= n + 1; i += i & -i) t[i] += v; }
    int prefix(int i) const { int s = 0; for (++i; i > 0; i -= i & -i) s += t[i]; return s; }
    int range(int l, int r) const {
        if (l > r || r < 0) return 0;
        l = max(l, 0); r = min(r, n);
        return prefix(r) - (l > 0 ? prefix(l - 1) : 0);
    }
};

int main() {
    int n = read_int(), k1 = read_int(), k2 = read_int();
    vector<vector<int>> adj(n);
    for (int i = 0; i < n - 1; i++) {
        int a = read_int() - 1, b = read_int() - 1;
        adj[a].push_back(b);
        adj[b].push_back(a);
    }
    vector<int> sz(n);
    vector<char> removed(n, 0);
    BIT distances(n + 1); // lets us hold distances->count of that many distances, and do range queries l...r counts faster constant than an OrderedSet
    vector<int> touchedDistances; // distances we incremented, for cheap reset
    vector<int> branchDepths; // depths of nodes in current branch, collected during query, replayed during fold
    // we want to know how many distances are currently in the range l...r
    auto countInRange = [&](int lo, int hi) -> ll {
        if (lo > hi) return 0;
        if (hi < 0) return 0;
        lo = max(lo, 0);
        return (ll)distances.range(lo, hi);
    };
    // gives us the size of a piece
    // can't walk back to the passed in parent
    // can't walk over removed centroids
    auto computeSize = [&](auto&& self, int node, int parent) -> void {
        int sizeHere = 1;
        for (auto adjN : adj[node]) {
            if (adjN == parent) continue;
            if (removed[adjN]) continue;
            self(self, adjN, node);
            sizeHere += sz[adjN];
        }
        sz[node] = sizeHere;
    };
    auto findCentroid = [&](auto&& self, int node, int parent, int pieceSize) -> int {
        int maxChildPiece = 0;
        int maxChild = -1;
        for (auto adjN : adj[node]) {
            if (adjN == parent) continue;
            if (removed[adjN]) continue;
            if (sz[adjN] > maxChildPiece) {
                maxChildPiece = sz[adjN];
                maxChild = adjN;
            }
        }
        int sizeAbove = pieceSize - sz[node];
        int largestPiece = max(sizeAbove, maxChildPiece);
        if (largestPiece <= pieceSize / 2) {
            return node;
        }
        return self(self, maxChild, node, pieceSize);
    };
    ll out = 0;
    // walks one branch of the centroid, querying distances against the BIT
    // and collecting depths into branchDepths for the fold pass
    auto dfsQuery = [&](auto&& self, int node, int parent, int dist) -> void {
        if (dist > k2) return;
        out += countInRange(k1 - dist, k2 - dist);
        branchDepths.push_back(dist);
        for (auto adjN : adj[node]) {
            if (removed[adjN]) continue;
            if (adjN == parent) continue;
            self(self, adjN, node, dist + 1);
        }
    };
    auto decompose = [&](auto&& self, int entry) -> void {
        // 1. compute the size of this piece
        computeSize(computeSize, entry, -1);
        int pieceSize = sz[entry];

        // 2. find the centroid
        int centroid = findCentroid(findCentroid, entry, -1, pieceSize);

        // 3. count paths of length in [k1, k2] passing through centroid
        // initialize the distance with the centroid
        distances.add(0, 1);
        touchedDistances.push_back(0);
        for (auto adjN : adj[centroid]) {
            if (removed[adjN]) continue;
            // single DFS: query against BIT and collect depths
            dfsQuery(dfsQuery, adjN, centroid, 1);
            // fold: replay collected depths into BIT
            for (int d : branchDepths) {
                distances.add(d, 1);
                touchedDistances.push_back(d);
            }
            branchDepths.clear();
        }
        for (int d : touchedDistances) distances.add(d, -1);
        touchedDistances.clear();

        // 4. remove the centroid
        removed[centroid] = true;

        // 5. recurse on non removed neighbors
        for (auto adjN : adj[centroid]) {
            if (removed[adjN]) continue;
            self(self, adjN);
        }
    };
    decompose(decompose, 0);
    printf("%lld\n", out);
}


// SOLUTION 1, O(n log^2 n) small to large with global array
// NOTE: I DID NOT WRITE THIS MYSELF
// THIS IS AI CODE (which I essentially never store in this repo)
// But I'm leaving it here to reference if I need at some point
// #include <bits/stdc++.h>
// #include <ext/pb_ds/assoc_container.hpp>
// #include <ext/pb_ds/tree_policy.hpp>
// using namespace std;
// using namespace __gnu_pbds;

// typedef tree<pair<int,int>, null_type, less<pair<int,int>>,
//              rb_tree_tag, tree_order_statistics_node_update> OrderedSet;

// int n, k1, k2;
// vector<vector<int>> adj;
// vector<int> par;
// vector<int> sz;
// vector<int> heavy;
// long long ans = 0;
// int uniqueCounter = 0;

// OrderedSet S;  // global set of (absoluteDepth, uniqueId)

// // count entries with absolute depth in [lo, hi]
// long long countAbsRange(int lo, int hi) {
//     if (lo > hi) return 0;
//     return (long long)(S.order_of_key({hi, INT_MAX}) - S.order_of_key({lo, INT_MIN}));
// }

// vector<int> absDepth;

// // BFS-like topo order so we can iterate subtrees iteratively
// vector<int> tin, tout;
// vector<int> dfsOrder;  // nodes in DFS order

// void buildTree(int root) {
//     // iterative DFS to set par, absDepth, sz, heavy, tin, tout, dfsOrder
//     par[root] = -1;
//     absDepth[root] = 0;
    
//     // first pass: compute order, par, depth
//     stack<pair<int,int>> stk;
//     stk.push({root, 0});  // (node, child_idx)
//     vector<int> order;
//     vector<int> childIdx(n, 0);
//     par[root] = -1;
//     int timer = 0;
    
//     // iterative DFS
//     {
//         stack<pair<int,int>> s;
//         s.push({root, -1});
//         vector<int> visitOrder;
//         while (!s.empty()) {
//             auto [u, p] = s.top(); s.pop();
//             par[u] = p;
//             absDepth[u] = (p == -1 ? 0 : absDepth[p] + 1);
//             visitOrder.push_back(u);
//             for (int v : adj[u]) {
//                 if (v != p) s.push({v, u});
//             }
//         }
//         // visitOrder is preorder-ish. Use it (in reverse) for size/heavy computation.
//         for (int i = (int)visitOrder.size() - 1; i >= 0; i--) {
//             int u = visitOrder[i];
//             sz[u] = 1;
//             heavy[u] = -1;
//             int maxSz = 0;
//             for (int v : adj[u]) {
//                 if (v == par[u]) continue;
//                 sz[u] += sz[v];
//                 if (sz[v] > maxSz) { maxSz = sz[v]; heavy[u] = v; }
//             }
//         }
//     }
    
//     // proper preorder DFS for tin/tout
//     {
//         stack<tuple<int,int,int>> s;  // (node, parent, state) state 0 = enter, 1 = exit
//         s.push({root, -1, 0});
//         while (!s.empty()) {
//             auto [u, p, state] = s.top(); s.pop();
//             if (state == 0) {
//                 tin[u] = timer++;
//                 dfsOrder.push_back(u);
//                 s.push({u, p, 1});
//                 for (int v : adj[u]) {
//                     if (v != p) s.push({v, u, 0});
//                 }
//             } else {
//                 tout[u] = timer;
//             }
//         }
//     }
// }

// // add all nodes in subtree of u to S (absDepth[u]'s)
// void addSubtree(int u) {
//     for (int t = tin[u]; t < tout[u]; t++) {
//         int x = dfsOrder[t];
//         S.insert({absDepth[x], uniqueCounter++});
//     }
// }

// // for each node x in subtree of u, count cross-pairs with S, where v is the LCA
// // query: depth_v(x) + depth_v(y) in [k1, k2] for y in S
// //   depth_v(x) = absDepth[x] - absDepth[v]
// //   depth_v(y) = absDepth[y] - absDepth[v]
// //   absDepth[y] in [absDepth[v] + k1 - (absDepth[x] - absDepth[v]),
// //                   absDepth[v] + k2 - (absDepth[x] - absDepth[v])]
// //                = [2*absDepth[v] + k1 - absDepth[x], 2*absDepth[v] + k2 - absDepth[x]]
// void queryAndAddSubtree(int u, int v) {
//     // first query
//     for (int t = tin[u]; t < tout[u]; t++) {
//         int x = dfsOrder[t];
//         int lo = 2 * absDepth[v] + k1 - absDepth[x];
//         int hi = 2 * absDepth[v] + k2 - absDepth[x];
//         ans += countAbsRange(lo, hi);
//     }
//     // then add
//     for (int t = tin[u]; t < tout[u]; t++) {
//         int x = dfsOrder[t];
//         S.insert({absDepth[x], uniqueCounter++});
//     }
// }

// // remove all nodes in subtree of u from S
// void removeSubtree(int u) {
//     for (int t = tin[u]; t < tout[u]; t++) {
//         int x = dfsOrder[t];
//         // remove one entry with absDepth[x]; since uniqueIds differ, find any one
//         auto it = S.lower_bound({absDepth[x], INT_MIN});
//         if (it != S.end() && it->first == absDepth[x]) {
//             S.erase(it);
//         }
//     }
// }

// // recursive solve: process LCA = v
// // returns with S containing exactly v's subtree's absDepths
// void solve(int v) {
//     // 1. solve light children, clearing each one's contribution after
//     for (int c : adj[v]) {
//         if (c == par[v] || c == heavy[v]) continue;
//         solve(c);
//         removeSubtree(c);
//     }
//     // 2. solve heavy child (keep its contribution in S)
//     if (heavy[v] != -1) solve(heavy[v]);
    
//     // 3. for each light child: query its subtree against S, then add to S
//     for (int c : adj[v]) {
//         if (c == par[v] || c == heavy[v]) continue;
//         queryAndAddSubtree(c, v);
//     }
    
//     // 4. count paths from v to anything in S (paths from v as endpoint)
//     // depth_v(v) = 0, depth_v(y) needs to be in [k1, k2]
//     // i.e., absDepth[y] in [absDepth[v] + k1, absDepth[v] + k2]
//     ans += countAbsRange(absDepth[v] + k1, absDepth[v] + k2);
    
//     // 5. add v itself to S
//     S.insert({absDepth[v], uniqueCounter++});
// }

// int main() {
//     ios::sync_with_stdio(false);
//     cin.tie(nullptr);
//     cin >> n >> k1 >> k2;
//     adj.assign(n, {});
//     par.assign(n, -1);
//     sz.assign(n, 0);
//     heavy.assign(n, -1);
//     absDepth.assign(n, 0);
//     tin.assign(n, 0);
//     tout.assign(n, 0);
//     dfsOrder.reserve(n);
    
//     for (int i = 0; i < n - 1; i++) {
//         int a, b; cin >> a >> b; a--; b--;
//         adj[a].push_back(b);
//         adj[b].push_back(a);
//     }
    
//     buildTree(0);
//     solve(0);
//     cout << ans << '\n';
// }