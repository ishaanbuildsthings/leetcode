#include <bits/stdc++.h>
using namespace std;
// TEMPLATE BY ISHAANBUILDSTHINGS on github
// in:  edgeList  = {{1,2}, {1,3}, {2,4}, {2,5}}   // unrooted, labels can be 0- or 1-indexed
// out: centroids = {2} or {1, 2}   // 1 or 2 nodes, sorted; deleting one leaves every piece <= n/2
// O(n) time, O(n) space
vector<int> findCentroids(const vector<pair<int, int>>& edgeList) {
    int n = (int)edgeList.size() + 1;
    int size = 0;
    for (auto& [a, b] : edgeList) size = max({size, a + 1, b + 1});
    int start = edgeList[0].first;
    vector<vector<int>> edgeMap(size);
    for (auto& [a, b] : edgeList) {
        edgeMap[a].push_back(b);
        edgeMap[b].push_back(a);
    }
    vector<int> order;
    order.reserve(n);
    vector<int> parent(size, -1);
    vector<int> stk = {start};
    while (!stk.empty()) {
        int node = stk.back();
        stk.pop_back();
        order.push_back(node);
        for (int adj : edgeMap[node]) {
            if (adj == parent[node]) continue;
            parent[adj] = node;
            stk.push_back(adj);
        }
    }
    vector<int> subtreeSize(size, 0);
    vector<int> maxComponent(size, 0);
    for (int i = (int)order.size() - 1; i >= 0; i--) {
        int node = order[i];
        subtreeSize[node] += 1;
        maxComponent[node] = max(maxComponent[node], n - subtreeSize[node]);
        if (parent[node] != -1) {
            subtreeSize[parent[node]] += subtreeSize[node];
            maxComponent[parent[node]] = max(maxComponent[parent[node]], subtreeSize[node]);
        }
    }
    int best = n;
    for (int node : order) best = min(best, maxComponent[node]);
    vector<int> centroids;
    for (int node : order) {
        if (maxComponent[node] == best) centroids.push_back(node);
    }
    sort(centroids.begin(), centroids.end());
    return centroids;
}