// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/graphs/bridges.cpp
#include <bits/stdc++.h>
using namespace std;

// vector<pair<int, int>> bridgeEdges = bridges(edges);
//   edges is a list of undirected edges {{node1, node2}, ...}; repeated edges and
//   self-loops are fine
//   The nodes are 0..n-1 or 1..n, sized from the largest label, so nothing else has to be passed
//   (a node with no edges can't affect the answer, so how many nodes there are doesn't matter)
//   For example: bridges({{1, 2}, {2, 3}, {3, 1}, {3, 4}, {4, 5}, {4, 5}})
//
// bridgeEdges -> every edge that, if removed, splits its component in two, e.g. {{3, 4}}
//   Each edge is written exactly as you gave it, in the order you gave them
//
//   Here 1, 2, 3 form a triangle, so removing any one of those edges still leaves another way
//   around. Removing 3 - 4 cuts 4 and 5 off. 4 - 5 is listed twice, so neither copy is a bridge:
//   the other copy still connects them
//
//   bridges({{1, 2}, {2, 3}}) -> {{1, 2}, {2, 3}}    (in a tree, every edge is a bridge)
//
// O(V + E) time and space, V = number of nodes, E = number of edges

vector<pair<int, int>> bridges(const vector<pair<int, int>>& edges) {
    int size = 0;
    for (auto [node1, node2] : edges) {
        if (node1 < 0 || node2 < 0) throw invalid_argument("bridges: an edge has a negative label");
        size = max({size, node1 + 1, node2 + 1});
    }
    vector<vector<pair<int, int>>> adj(size);  // (neighbor, edge id)
    for (int edgeId = 0; edgeId < (int)edges.size(); edgeId++) {
        auto [node1, node2] = edges[edgeId];
        adj[node1].push_back({node2, edgeId});
        adj[node2].push_back({node1, edgeId});
    }

    // depth-first search: low[node] = the earliest entry time reachable from node's subtree using one back edge.
    // The edge into a child is a bridge when nothing below the child reaches back above it
    vector<int> tin(size, -1), low(size, 0), nextIdx(size, 0), parentEdge(size, -1);
    vector<char> isBridge(edges.size(), 0);
    int timer = 0;
    vector<int> stack;
    for (int root = 0; root < size; root++) {
        if (tin[root] != -1) continue;
        tin[root] = low[root] = timer++;
        stack.push_back(root);
        while (!stack.empty()) {
            int node = stack.back();
            if (nextIdx[node] < (int)adj[node].size()) {
                auto [nxt, edgeId] = adj[node][nextIdx[node]++];
                if (edgeId == parentEdge[node]) continue;  // skip only that one edge, so a repeated edge counts as a way back
                if (tin[nxt] == -1) {
                    parentEdge[nxt] = edgeId;
                    tin[nxt] = low[nxt] = timer++;
                    stack.push_back(nxt);
                } else {
                    low[node] = min(low[node], tin[nxt]);
                }
            } else {
                stack.pop_back();
                if (!stack.empty()) {
                    int par = stack.back();
                    low[par] = min(low[par], low[node]);
                    if (low[node] > tin[par]) isBridge[parentEdge[node]] = 1;
                }
            }
        }
    }
    vector<pair<int, int>> result;
    for (int i = 0; i < (int)edges.size(); i++)
        if (isBridge[i]) result.push_back(edges[i]);
    return result;
}
