// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/reroot/SumOfDistances.weighted.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// For every node, the sum of its distances (by total edge weight) to all other nodes
// edges = {{a, b, w}, {c, d, w}, ...}: an unrooted tree with at least 2 nodes, any int weights
// labels can be 0..n-1 or 1..n, no flag needed: the output is sized to the largest label
//   0-indexed -> size n
//   1-indexed -> size n + 1, index 0 is an unused dummy holding -1
// auto res = sumOfDistances(edges);   res[i] = sum of distances from i to every other node
//   edges {{0, 1, 5}, {1, 2, 3}, {1, 3, 4}} -> res {22, 12, 18, 20}
// sums are long long: overflows only if n^2 * max |w| passes about 9e18
// O(n) time and space, iterative
vector<long long> sumOfDistances(const vector<vector<int>>& edges) {
    int size = 0;
    for (auto& e : edges) {
        size = max({size, e[0] + 1, e[1] + 1});
    }

    vector<int> start(size + 1, 0);
    for (auto& e : edges) {
        start[e[0] + 1]++;
        start[e[1] + 1]++;
    }
    for (int i = 0; i < size; i++) {
        start[i + 1] += start[i];
    }
    vector<int> adj(2 * edges.size());
    vector<long long> adjW(2 * edges.size());
    vector<int> fill(start.begin(), start.end() - 1);
    for (auto& e : edges) {
        adjW[fill[e[0]]] = e[2];
        adj[fill[e[0]]++] = e[1];
        adjW[fill[e[1]]] = e[2];
        adj[fill[e[1]]++] = e[0];
    }

    int root = edges[0][0];
    vector<int> parent(size, -1);
    vector<long long> parentW(size, 0);
    vector<int> order;
    order.reserve(size);
    order.push_back(root);
    for (int i = 0; i < (int)order.size(); i++) {
        int cur = order[i];
        for (int k = start[cur]; k < start[cur + 1]; k++) {
            int nxt = adj[k];
            if (nxt != parent[cur]) {
                parent[nxt] = cur;
                parentW[nxt] = adjW[k];
                order.push_back(nxt);
            }
        }
    }

    long long n = edges.size() + 1;
    vector<long long> subSize(size, 1);
    vector<long long> down(size, 0); // sum of distances from a node into its own subtree
    for (int i = (int)order.size() - 1; i > 0; i--) {
        int cur = order[i];
        int par = parent[cur];
        subSize[par] += subSize[cur];
        down[par] += down[cur] + subSize[cur] * parentW[cur];
    }

    // moving across an edge of weight w: cur's subtree gets w closer, everything else w farther
    vector<long long> res(size, -1);
    res[root] = down[root];
    for (int i = 1; i < (int)order.size(); i++) {
        int cur = order[i];
        res[cur] = res[parent[cur]] + parentW[cur] * (n - 2 * subSize[cur]);
    }
    return res;
}
