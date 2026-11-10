// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/reroot/FarthestNode.weighted.cpp
#include <bits/stdc++.h>
using namespace std;

// For every node, the farthest OTHER node (by total edge weight) and its distance
// edges = {{a, b, w}, {c, d, w}, ...}: an unrooted tree with at least 2 nodes, any int weights (negative and 0 ok)
// labels can be 0..n-1 or 1..n, no flag needed: the output is sized to the largest label
//   0-indexed -> size n
//   1-indexed -> size n + 1, index 0 is an unused dummy holding {-1, -1}
// auto res = farthestNodes(edges);   res[i] = {distance, farthest node}
//   edges {{0, 1, 5}, {1, 2, 3}, {1, 3, 4}} -> res {{9, 3}, {5, 0}, {8, 0}, {9, 0}}
// ties go to the smallest node id
// O(n) time and space, iterative
vector<pair<long long, int>> farthestNodes(const vector<vector<int>>& edges) {
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

    // does (candD, candN) beat (curD, curN)? curN == -1 means nothing yet
    auto beats = [](long long candD, int candN, long long curD, int curN) {
        return curN == -1 || candD > curD || (candD == curD && candN < curN);
    };

    // best and second best (dist, node) strictly inside each subtree, through different children
    vector<long long> best1D(size, 0), best2D(size, 0);
    vector<int> best1N(size, -1), best1C(size, -1), best2N(size, -1);
    for (int i = (int)order.size() - 1; i > 0; i--) {
        int cur = order[i];
        int par = parent[cur];
        // stop at cur itself, or keep going down into its subtree
        long long d = 0;
        int nd = cur;
        if (best1N[cur] != -1 && beats(best1D[cur], best1N[cur], d, nd)) {
            d = best1D[cur];
            nd = best1N[cur];
        }
        d += parentW[cur];
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
    vector<long long> upD(size, 0);
    vector<int> upN(size, -1);
    for (int i = 1; i < (int)order.size(); i++) {
        int cur = order[i];
        int par = parent[cur];
        long long w = parentW[cur];
        long long d = w;
        int nd = par;
        if (upN[par] != -1 && beats(upD[par] + w, upN[par], d, nd)) {
            d = upD[par] + w;
            nd = upN[par];
        }
        long long sd = best1C[par] == cur ? best2D[par] : best1D[par];
        int sn = best1C[par] == cur ? best2N[par] : best1N[par];
        if (sn != -1 && beats(sd + w, sn, d, nd)) {
            d = sd + w;
            nd = sn;
        }
        upD[cur] = d;
        upN[cur] = nd;
    }

    vector<pair<long long, int>> res(size, {-1, -1});
    for (int cur : order) {
        long long d = upD[cur];
        int nd = upN[cur];
        if (best1N[cur] != -1 && beats(best1D[cur], best1N[cur], d, nd)) {
            d = best1D[cur];
            nd = best1N[cur];
        }
        res[cur] = {d, nd};
    }
    return res;
}
