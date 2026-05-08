#include <bits/stdc++.h>
using namespace std;
 
// TEMPLATE BY ISHAAN AGRAWAL, github: ishaanbuildsthings
// takes nodes from 0 to n-1 and constructs a children map rooted at 0
int numNodes;
vector<vector<int>> edgeListToTree(const vector<pair<int, int>>& edgeList) {
    vector<vector<int>> edgeMap(numNodes + 1);
    for (auto [a, b] : edgeList) {
        edgeMap[a].push_back(b);
        edgeMap[b].push_back(a);
    }
 
    vector<vector<int>> children(numNodes + 1); // maps a node to its children
 
    function<void(int, int)> buildTree = [&](int node, int parent) {
        for (int adj : edgeMap[node]) {
            if (adj == parent) continue;
            children[node].push_back(adj);
            buildTree(adj, node);
        }
    };
    buildTree(1, -1); // root at 1
    return children;
}
 
int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
 
    cin >> numNodes;
    vector<int> nodeColors(numNodes);
    for (int i = 0; i < numNodes; ++i) cin >> nodeColors[i];
 
    vector<pair<int, int>> edgeList;
    edgeList.reserve(numNodes - 1);
    for (int i = 0; i < numNodes - 1; ++i) {
        int nodeA, nodeB;
        cin >> nodeA >> nodeB;
        edgeList.emplace_back(nodeA, nodeB);
    }
 
    auto children = edgeListToTree(edgeList);
 
    vector<int> res(numNodes);
    function<unordered_set<int>(int)> dfs = [&](int node) -> unordered_set<int> {
        unordered_set<int> currColors;
        currColors.insert(nodeColors[node - 1]);
        for (int child : children[node]) {
            auto childColors = dfs(child);
            if (childColors.size() > currColors.size()) swap(currColors, childColors);
            currColors.insert(childColors.begin(), childColors.end());
            // for color in childColors:
            //     currColors.add(color)
        }
        res[node - 1] = static_cast<int>(currColors.size());
        return currColors;
    };
 
    dfs(1);
 
    for (int i = 0; i < numNodes; ++i) {
        if (i) cout << ' ';
        cout << res[i];
    }
    cout << '\n';
    return 0;
}