// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/trees/weightedEdgeListToTree.cpp
#include <bits/stdc++.h>
using namespace std;

// TEMPLATE BY ISHAAN AGRAWAL, github: ishaanbuildsthings
// edgeList = {{a, b, w}, {c, d, w}, ...}
// roots the tree at `root` (any node id) and returns `children`, sized to fit the largest label
// 0-indexed input -> children goes up to children[n-1]; 1-indexed -> up to children[n], children[0] empty and unused
// children[node] = {{child, weight}, ...} where weight is the edge from node to child
vector<vector<pair<int, int>>> edgeListToTree(const vector<array<int, 3>>& edgeList, int root) {
    int size = root + 1;
    for (auto& [a, b, w] : edgeList) size = max({size, a + 1, b + 1});
    vector<vector<pair<int, int>>> edgeMap(size);
    for (auto& [a, b, w] : edgeList) {
        edgeMap[a].push_back({b, w});
        edgeMap[b].push_back({a, w});
    }
    vector<vector<pair<int, int>>> children(size);
    vector<int> parent(size, -1);
    vector<int> stk = {root};
    while (!stk.empty()) {
        int node = stk.back();
        stk.pop_back();
        for (auto& [adj, w] : edgeMap[node]) {
            if (adj == parent[node]) continue;
            parent[adj] = node;
            children[node].push_back({adj, w});
            stk.push_back(adj);
        }
    }
    return children;
}
