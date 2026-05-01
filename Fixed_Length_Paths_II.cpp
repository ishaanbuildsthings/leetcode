#include <bits/stdc++.h>
#include <ext/pb_ds/assoc_container.hpp>
#include <ext/pb_ds/tree_policy.hpp>
using namespace std;
using namespace __gnu_pbds;

typedef tree<pair<int,int>, null_type, less<pair<int,int>>,
             rb_tree_tag, tree_order_statistics_node_update> OrderedSet;

int n, k1, k2;
vector<vector<int>> adj;
vector<int> par;
vector<int> sz;
vector<int> heavy;
long long ans = 0;
int uniqueCounter = 0;

OrderedSet S;  // global set of (absoluteDepth, uniqueId)

// count entries with absolute depth in [lo, hi]
long long countAbsRange(int lo, int hi) {
    if (lo > hi) return 0;
    return (long long)(S.order_of_key({hi, INT_MAX}) - S.order_of_key({lo, INT_MIN}));
}

vector<int> absDepth;

// BFS-like topo order so we can iterate subtrees iteratively
vector<int> tin, tout;
vector<int> dfsOrder;  // nodes in DFS order

void buildTree(int root) {
    // iterative DFS to set par, absDepth, sz, heavy, tin, tout, dfsOrder
    par[root] = -1;
    absDepth[root] = 0;
    
    // first pass: compute order, par, depth
    stack<pair<int,int>> stk;
    stk.push({root, 0});  // (node, child_idx)
    vector<int> order;
    vector<int> childIdx(n, 0);
    par[root] = -1;
    int timer = 0;
    
    // iterative DFS
    {
        stack<pair<int,int>> s;
        s.push({root, -1});
        vector<int> visitOrder;
        while (!s.empty()) {
            auto [u, p] = s.top(); s.pop();
            par[u] = p;
            absDepth[u] = (p == -1 ? 0 : absDepth[p] + 1);
            visitOrder.push_back(u);
            for (int v : adj[u]) {
                if (v != p) s.push({v, u});
            }
        }
        // visitOrder is preorder-ish. Use it (in reverse) for size/heavy computation.
        for (int i = (int)visitOrder.size() - 1; i >= 0; i--) {
            int u = visitOrder[i];
            sz[u] = 1;
            heavy[u] = -1;
            int maxSz = 0;
            for (int v : adj[u]) {
                if (v == par[u]) continue;
                sz[u] += sz[v];
                if (sz[v] > maxSz) { maxSz = sz[v]; heavy[u] = v; }
            }
        }
    }
    
    // proper preorder DFS for tin/tout
    {
        stack<tuple<int,int,int>> s;  // (node, parent, state) state 0 = enter, 1 = exit
        s.push({root, -1, 0});
        while (!s.empty()) {
            auto [u, p, state] = s.top(); s.pop();
            if (state == 0) {
                tin[u] = timer++;
                dfsOrder.push_back(u);
                s.push({u, p, 1});
                for (int v : adj[u]) {
                    if (v != p) s.push({v, u, 0});
                }
            } else {
                tout[u] = timer;
            }
        }
    }
}

// add all nodes in subtree of u to S (absDepth[u]'s)
void addSubtree(int u) {
    for (int t = tin[u]; t < tout[u]; t++) {
        int x = dfsOrder[t];
        S.insert({absDepth[x], uniqueCounter++});
    }
}

// for each node x in subtree of u, count cross-pairs with S, where v is the LCA
// query: depth_v(x) + depth_v(y) in [k1, k2] for y in S
//   depth_v(x) = absDepth[x] - absDepth[v]
//   depth_v(y) = absDepth[y] - absDepth[v]
//   absDepth[y] in [absDepth[v] + k1 - (absDepth[x] - absDepth[v]),
//                   absDepth[v] + k2 - (absDepth[x] - absDepth[v])]
//                = [2*absDepth[v] + k1 - absDepth[x], 2*absDepth[v] + k2 - absDepth[x]]
void queryAndAddSubtree(int u, int v) {
    // first query
    for (int t = tin[u]; t < tout[u]; t++) {
        int x = dfsOrder[t];
        int lo = 2 * absDepth[v] + k1 - absDepth[x];
        int hi = 2 * absDepth[v] + k2 - absDepth[x];
        ans += countAbsRange(lo, hi);
    }
    // then add
    for (int t = tin[u]; t < tout[u]; t++) {
        int x = dfsOrder[t];
        S.insert({absDepth[x], uniqueCounter++});
    }
}

// remove all nodes in subtree of u from S
void removeSubtree(int u) {
    for (int t = tin[u]; t < tout[u]; t++) {
        int x = dfsOrder[t];
        // remove one entry with absDepth[x]; since uniqueIds differ, find any one
        auto it = S.lower_bound({absDepth[x], INT_MIN});
        if (it != S.end() && it->first == absDepth[x]) {
            S.erase(it);
        }
    }
}

// recursive solve: process LCA = v
// returns with S containing exactly v's subtree's absDepths
void solve(int v) {
    // 1. solve light children, clearing each one's contribution after
    for (int c : adj[v]) {
        if (c == par[v] || c == heavy[v]) continue;
        solve(c);
        removeSubtree(c);
    }
    // 2. solve heavy child (keep its contribution in S)
    if (heavy[v] != -1) solve(heavy[v]);
    
    // 3. for each light child: query its subtree against S, then add to S
    for (int c : adj[v]) {
        if (c == par[v] || c == heavy[v]) continue;
        queryAndAddSubtree(c, v);
    }
    
    // 4. count paths from v to anything in S (paths from v as endpoint)
    // depth_v(v) = 0, depth_v(y) needs to be in [k1, k2]
    // i.e., absDepth[y] in [absDepth[v] + k1, absDepth[v] + k2]
    ans += countAbsRange(absDepth[v] + k1, absDepth[v] + k2);
    
    // 5. add v itself to S
    S.insert({absDepth[v], uniqueCounter++});
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    cin >> n >> k1 >> k2;
    adj.assign(n, {});
    par.assign(n, -1);
    sz.assign(n, 0);
    heavy.assign(n, -1);
    absDepth.assign(n, 0);
    tin.assign(n, 0);
    tout.assign(n, 0);
    dfsOrder.reserve(n);
    
    for (int i = 0; i < n - 1; i++) {
        int a, b; cin >> a >> b; a--; b--;
        adj[a].push_back(b);
        adj[b].push_back(a);
    }
    
    buildTree(0);
    solve(0);
    cout << ans << '\n';
}