// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/graphs/bipartiteSplit.cpp
#include <bits/stdc++.h>
using namespace std;

// BipartiteSplit split = bipartiteSplit(edges, numNodes, oneIndexed);
//   edges is a list of undirected edges {{node1, node2}, ...}; repeated edges are fine
//   numNodes is how many nodes there are (it has to be passed since a node with no edges never shows up otherwise)
//   oneIndexed is true when the nodes are 1..numNodes, false when they're 0..numNodes-1
//   For example: bipartiteSplit({{1, 2}, {2, 3}, {3, 4}}, 5, true)   (node 5 has no edges)
//
// split.possible -> true if the nodes can be split into two sides with every edge going between
//   the sides (none inside a side), e.g. true
//
// split.side1, split.side2 -> the two sides, each increasing, e.g. {1, 3, 5} and {2, 4}
//   Empty when it's not possible.
//   Each component's smallest node goes on side1. A node with no edges is on side1 too (it could go
//   on either side)
//
//   split.possible is false if it's impossible: that happens exactly when there's a loop with an odd
//   number of edges, like a triangle. A self-loop always makes it impossible
//
//   bipartiteSplit({{1, 2}, {2, 3}, {3, 1}}, 3, true) -> {false, {}, {}}
//
// O(V + E) time and space

struct BipartiteSplit {
    bool possible;
    vector<int> side1, side2;
};

BipartiteSplit bipartiteSplit(const vector<pair<int, int>>& edges, int numNodes, bool oneIndexed) {
    int firstNode = oneIndexed ? 1 : 0, size = firstNode + numNodes;
    vector<vector<int>> adj(size);
    for (auto [node1, node2] : edges) {
        if (node1 < firstNode || node1 >= size || node2 < firstNode || node2 >= size)
            throw out_of_range("bipartiteSplit: an edge is outside the nodes 0..numNodes-1 (or 1..numNodes)");
        adj[node1].push_back(node2);
        adj[node2].push_back(node1);
    }

    // color each component starting from its smallest node (side 0); every edge has to join different sides
    vector<int> side(size, -1), stack;
    for (int start = firstNode; start < size; start++) {
        if (side[start] != -1) continue;
        side[start] = 0;
        stack.push_back(start);
        while (!stack.empty()) {
            int node = stack.back();
            stack.pop_back();
            for (int nxt : adj[node]) {
                if (side[nxt] == -1) {
                    side[nxt] = 1 - side[node];
                    stack.push_back(nxt);
                } else if (side[nxt] == side[node]) {
                    return {false, {}, {}};
                }
            }
        }
    }
    BipartiteSplit result{true, {}, {}};
    for (int node = firstNode; node < size; node++) (side[node] == 0 ? result.side1 : result.side2).push_back(node);
    return result;
}
