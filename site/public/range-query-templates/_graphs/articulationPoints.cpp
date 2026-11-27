// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/graphs/articulationPoints.cpp
#include <bits/stdc++.h>
using namespace std;

// vector<int> cutNodes = articulationPoints(edges);
//   edges is a list of undirected edges {{node1, node2}, ...}; repeated edges and
//   self-loops are fine
//   The nodes are 0..n-1 or 1..n, sized from the largest label, so nothing else has to be passed
//   (a node with no edges can't affect the answer, so how many nodes there are doesn't matter)
//   For example: articulationPoints({{1, 2}, {2, 3}, {3, 1}, {3, 4}, {4, 5}})
//
// cutNodes -> every node that, if removed with its edges, splits its component into two or more
//   pieces, increasing, e.g. {3, 4}
//
//   Here removing 3 separates the triangle's 1 and 2 from 4 and 5, and removing 4 cuts 5 off.
//   Removing 1 or 2 leaves everything else connected
//
//   articulationPoints({{1, 2}, {1, 3}, {1, 4}}) -> {1}    (removing the center leaves three pieces)
//
// O(V + E) time and space, V = number of nodes, E = number of edges

vector<int> articulationPoints(const vector<pair<int, int>>& edges) {
    int size = 0;
    for (auto [node1, node2] : edges) {
        if (node1 < 0 || node2 < 0) throw invalid_argument("articulationPoints: an edge has a negative label");
        size = max({size, node1 + 1, node2 + 1});
    }
    vector<vector<pair<int, int>>> adj(size);  // (neighbor, edge id)
    for (int edgeId = 0; edgeId < (int)edges.size(); edgeId++) {
        auto [node1, node2] = edges[edgeId];
        adj[node1].push_back({node2, edgeId});
        adj[node2].push_back({node1, edgeId});
    }

    // depth-first search: low[node] = the earliest entry time reachable from node's subtree using one back edge.
    // A non-root node cuts the graph when some child's subtree can't reach above it; the root cuts it when it has
    // two or more children in the search
    vector<int> tin(size, -1), low(size, 0), nextIdx(size, 0), parentEdge(size, -1);
    vector<char> isCut(size, 0);
    int timer = 0;
    vector<int> stack;
    for (int root = 0; root < size; root++) {
        if (tin[root] != -1) continue;
        tin[root] = low[root] = timer++;
        int rootChildren = 0;
        stack.push_back(root);
        while (!stack.empty()) {
            int node = stack.back();
            if (nextIdx[node] < (int)adj[node].size()) {
                auto [nxt, edgeId] = adj[node][nextIdx[node]++];
                if (edgeId == parentEdge[node]) continue;
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
                    if (par == root) rootChildren++;
                    else if (low[node] >= tin[par]) isCut[par] = 1;
                }
            }
        }
        if (rootChildren >= 2) isCut[root] = 1;
    }
    vector<int> result;
    for (int node = 0; node < size; node++)
        if (isCut[node]) result.push_back(node);
    return result;
}
