// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/graphs/scc.cpp
#include <bits/stdc++.h>
using namespace std;

// Scc scc = buildScc(edges, numNodes, oneIndexed);
//   A strongly connected component is a group of nodes that can all reach each other
//   edges is a list of directed edges {{from, to}, ...}; repeated edges and self-loops are fine
//   numNodes is how many nodes there are (it has to be passed since a node with no edges never shows up otherwise)
//   oneIndexed is true when the nodes are 1..numNodes, false when they're 0..numNodes-1
//   For example: buildScc({{1, 2}, {2, 3}, {3, 1}, {4, 3}}, 5, true)   (node 5 has no edges)
//
// scc.numComponents -> how many components there are, e.g. 3
//
// scc.nodeToComponentId[node] -> which component node is in, e.g. {-1, 0, 0, 0, 1, 2}
//   Component ids go from 0 to numComponents - 1. With oneIndexed, slot 0 isn't a node and is -1
//
// scc.componentNodes[componentId] -> that component's nodes, increasing, e.g. {{1, 2, 3}, {4}, {5}}
//
// scc.componentAdj[componentId] -> the components it has edges into, e.g. {{}, {0}, {}}
//   Here component 1 (node 4) has an edge into component 0 (nodes 1, 2, 3). Edges inside a component are
//   dropped, repeats are kept, and following these never loops back
//
//   Ids come out in reverse topological order: every edge goes from a bigger id to a smaller one,
//   so going through ids 0, 1, 2, ... handles a component only after everything it can reach
//
// O(V + E) time and space
struct Scc {
    vector<int> nodeToComponentId;
    vector<vector<int>> componentNodes;
    vector<vector<int>> componentAdj;
    int numComponents;
};

Scc buildScc(const vector<pair<int, int>>& edges, int numNodes, bool oneIndexed) {
    if (numNodes < 0) throw invalid_argument("buildScc: needs numNodes >= 0");
    int firstNode = oneIndexed ? 1 : 0, lastNode = firstNode + numNodes - 1;
    int size = lastNode + 1;
    vector<vector<int>> adj(size);
    for (auto [a, b] : edges) {
        if (a < firstNode || a > lastNode || b < firstNode || b > lastNode)
            throw out_of_range("buildScc: an edge is outside the nodes 0..numNodes-1 (or 1..numNodes)");
        adj[a].push_back(b);
    }
    vector<int> num(size, 0), low(size, 0), nodeToComponentId(size, -1), stk;
    vector<char> onStk(size, 0);
    vector<pair<int, int>> callStack;
    int timer = 0, numComponents = 0;
    for (int start = firstNode; start < size; start++) {
        if (num[start]) continue;
        num[start] = low[start] = ++timer;
        stk.push_back(start);
        onStk[start] = 1;
        callStack.push_back({start, 0});
        while (!callStack.empty()) {
            auto& [node1, ei] = callStack.back();
            if (ei < (int)adj[node1].size()) {
                int node2 = adj[node1][ei++];
                if (!num[node2]) {
                    num[node2] = low[node2] = ++timer;
                    stk.push_back(node2);
                    onStk[node2] = 1;
                    callStack.push_back({node2, 0});
                } else if (onStk[node2]) {
                    low[node1] = min(low[node1], num[node2]);
                }
            } else {
                if (low[node1] == num[node1]) {
                    while (true) {
                        int node3 = stk.back();
                        stk.pop_back();
                        onStk[node3] = 0;
                        nodeToComponentId[node3] = numComponents;
                        if (node3 == node1) break;
                    }
                    numComponents++;
                }
                int finished = node1;
                callStack.pop_back();
                if (!callStack.empty()) {
                    int parent = callStack.back().first;
                    low[parent] = min(low[parent], low[finished]);
                }
            }
        }
    }
    vector<vector<int>> componentNodes(numComponents), componentAdj(numComponents);
    for (int node1 = firstNode; node1 < size; node1++) {
        int compId = nodeToComponentId[node1];
        componentNodes[compId].push_back(node1);
        for (int node2 : adj[node1])
            if (compId != nodeToComponentId[node2]) componentAdj[compId].push_back(nodeToComponentId[node2]);
    }
    return {nodeToComponentId, componentNodes, componentAdj, numComponents};
}
