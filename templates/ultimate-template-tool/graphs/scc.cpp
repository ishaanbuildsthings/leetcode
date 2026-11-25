// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/graphs/scc.cpp
#include <bits/stdc++.h>
using namespace std;

// Strongly connected components of a directed graph (iterative Tarjan): groups of nodes that can all reach each other.
// edges: {{a, b}, ...} meaning a -> b; repeated edges and self-loops are fine.
// n, oneIndexed (both required): the nodes are 0..n-1, or 1..n when oneIndexed is true. The edges alone can't say this:
// a node with no edges never shows up in them, yet it's still a component by itself, so leaving it out would give
// the wrong count. And whether labels start at 0 or 1 decides which node is the missing one. Every edge must stay in
// that range, else out_of_range.
//   Scc scc = buildScc({{1, 2}, {2, 3}, {3, 1}, {4, 3}}, 5, true);    // nodes 1..5; node 5 has no edges
//   Scc scc = buildScc({{0, 1}, {1, 0}}, 3, false);                    // nodes 0..2; node 2 has no edges
// The returned fields (node ids are your labels, component ids are 0..numComponents-1):
//   scc.numComponents       3
//   scc.nodeToComponentId   {-1, 0, 0, 0, 1, 2}       indexed by node (oneIndexed: slot 0 is unused, -1)
//   scc.componentNodes      {{1, 2, 3}, {4}, {5}}     indexed by component id, nodes increasing
//   scc.componentAdj        {{}, {0}, {}}             indexed by component id: out-neighbor components (always
//                                                     acyclic); edges inside a component dropped, repeats kept
// Component ids come out in reverse topological order: every edge compA -> compB has compA > compB, so looping ids
// 0..numComponents-1 visits a component only after everything it can reach.
// O(V + E) time and space, V = n, E = number of edges
struct Scc {
    vector<int> nodeToComponentId;
    vector<vector<int>> componentNodes;
    vector<vector<int>> componentAdj;
    int numComponents;
};

Scc buildScc(const vector<pair<int, int>>& edges, int n, bool oneIndexed) {
    if (n < 0) throw invalid_argument("buildScc: needs n >= 0");
    int firstNode = oneIndexed ? 1 : 0, lastNode = firstNode + n - 1;
    int size = lastNode + 1;
    vector<vector<int>> adj(size);
    for (auto [a, b] : edges) {
        if (a < firstNode || a > lastNode || b < firstNode || b > lastNode)
            throw out_of_range("buildScc: an edge is outside the nodes 0..n-1 (or 1..n)");
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
