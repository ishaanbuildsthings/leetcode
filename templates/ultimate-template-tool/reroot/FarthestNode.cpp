// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/reroot/FarthestNode.cpp
#include <bits/stdc++.h>
using namespace std;

// For every node, the farthest OTHER node (by edge count) and its distance
// edges = {{a, b}, {c, d}, ...}: an unrooted tree with at least 2 nodes
// labels can be 0..n-1 or 1..n, no flag needed: the output is sized to the largest label
//   0-indexed -> size n
//   1-indexed -> size n + 1, index 0 is an unused dummy holding {-1, -1}
// auto res = farthestNodes(edges);   res[i] = {distance, farthest node}
//   edges {{0, 1}, {1, 2}, {1, 3}} -> res {{2, 2}, {1, 0}, {2, 0}, {2, 0}}
// ties go to the smallest node id
// O(n) time and space, iterative
vector<pair<int, int>> farthestNodes(const vector<vector<int>>& edges) {
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
    vector<int> fill(start.begin(), start.end() - 1);
    for (auto& e : edges) {
        adj[fill[e[0]]++] = e[1];
        adj[fill[e[1]]++] = e[0];
    }

    int root = edges[0][0];
    vector<int> parent(size, -1);
    vector<int> order;
    order.reserve(size);
    order.push_back(root);
    for (int i = 0; i < (int)order.size(); i++) {
        int cur = order[i];
        for (int k = start[cur]; k < start[cur + 1]; k++) {
            int nxt = adj[k];
            if (nxt != parent[cur]) {
                parent[nxt] = cur;
                order.push_back(nxt);
            }
        }
    }

    // does (candD, candN) beat (curD, curN)? curN == -1 means nothing yet
    auto beats = [](int candD, int candN, int curD, int curN) {
        return curN == -1 || candD > curD || (candD == curD && candN < curN);
    };

    // best and second best (dist, node) strictly inside each subtree, through different children
    vector<int> best1D(size, -1), best1N(size, -1), best1C(size, -1), best2D(size, -1), best2N(size, -1);
    for (int i = (int)order.size() - 1; i > 0; i--) {
        int cur = order[i];
        int par = parent[cur];
        int d = 1;
        int nd = cur;
        if (best1N[cur] != -1) {
            d = best1D[cur] + 1;
            nd = best1N[cur];
        }
        if (beats(d, nd, best1D[par], best1N[par])) {
            best2D[par] = best1D[par];
            best2N[par] = best1N[par];
            best1D[par] = d;
            best1N[par] = nd;
            best1C[par] = cur;
        } else if (beats(d, nd, best2D[par], best2N[par])) {
            best2D[par] = d;
            best2N[par] = nd;
        }
    }

    // best (dist, node) reached by first stepping to the parent
    vector<int> upD(size, -1), upN(size, -1);
    for (int i = 1; i < (int)order.size(); i++) {
        int cur = order[i];
        int par = parent[cur];
        int d = 1;
        int nd = par;
        if (upN[par] != -1 && beats(upD[par] + 1, upN[par], d, nd)) {
            d = upD[par] + 1;
            nd = upN[par];
        }
        int sd = best1C[par] == cur ? best2D[par] : best1D[par];
        int sn = best1C[par] == cur ? best2N[par] : best1N[par];
        if (sn != -1 && beats(sd + 1, sn, d, nd)) {
            d = sd + 1;
            nd = sn;
        }
        upD[cur] = d;
        upN[cur] = nd;
    }

    vector<pair<int, int>> res(size, {-1, -1});
    for (int cur : order) {
        int d = upD[cur];
        int nd = upN[cur];
        if (best1N[cur] != -1 && beats(best1D[cur], best1N[cur], d, nd)) {
            d = best1D[cur];
            nd = best1N[cur];
        }
        res[cur] = {d, nd};
    }
    return res;
}
