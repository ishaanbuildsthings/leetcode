#include <bits/stdc++.h>
using namespace std;

// TEMPLATE BY ISHAAN AGRAWAL, github: ishaanbuildsthings
// edgeList = {{a, b}, {c, d}, ...}
// roots the tree at `root` (any node id) and returns `children`, sized to fit the largest label
// 0-indexed input -> children goes up to children[n-1]; 1-indexed -> up to children[n], children[0] empty and unused
vector<vector<int>> edgeListToTree(const vector<pair<int, int>>& edgeList, int root) {
    int size = 0;
    for (auto& [a, b] : edgeList) size = max({size, a + 1, b + 1});
    vector<vector<int>> edgeMap(size);
    for (auto& [a, b] : edgeList) {
        edgeMap[a].push_back(b);
        edgeMap[b].push_back(a);
    }
    vector<vector<int>> children(size);
    vector<int> parent(size, -1);
    vector<int> stk = {root};
    while (!stk.empty()) {
        int node = stk.back();
        stk.pop_back();
        for (int adj : edgeMap[node]) {
            if (adj == parent[node]) continue;
            parent[adj] = node;
            children[node].push_back(adj);
            stk.push_back(adj);
        }
    }
    return children;
}