#include <bits/stdc++.h>
using namespace std;
int n;
vector<vector<int>> g;
int main() {
    cin.tie(nullptr);
    ios::sync_with_stdio(false);
    cin >> n;
    g.resize(n);
    for (int i = 0; i < n - 1; i++) {
        int a, b; cin >> a >> b;
        a--; b--;
        g[a].push_back(b);
        g[b].push_back(a);
    }

    vector<long long> distBelow(n);
    vector<int> childrenCount(n);

    // compute the sum of distances to all nodes below us, rooted at 0
    auto dfs = [&](auto&& self, int node, int parent) -> void {
        int childrenHere = 0;
        long long distHere = 0;
        for (auto adj : g[node]) {
            if (adj == parent) continue;
            self(self, adj, node);
            childrenHere += 1 + childrenCount[adj];
            distHere += childrenCount[adj] + 1 + distBelow[adj];
        }
        childrenCount[node] = childrenHere;
        distBelow[node] = distHere;
    };
    dfs(dfs, 0, -1);

    vector<long long> ans(n);
    ans[0] = distBelow[0];

    auto dfs2 = [&](auto&& self, int node, int parent) -> void {
        for (auto adj : g[node]) {
            if (adj == parent) continue;
            // the dist from this node to every other node
            // is the dist above us
            // but all nodes in our tree are one closer
            // all nodes not in our tree are one further
            long long newDist = ans[node];
            int nodesInThistree = childrenCount[adj] + 1;
            newDist -= nodesInThistree;
            newDist += n - nodesInThistree;
            ans[adj] = newDist;
            self(self, adj, node);
        }
    };

    dfs2(dfs2, 0, -1);

    for (auto x : ans) cout << x << " ";
}