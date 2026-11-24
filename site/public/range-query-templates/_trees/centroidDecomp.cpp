// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/trees/centroidDecomp.cpp
#include <bits/stdc++.h>
using namespace std;
// O(n log n)
// pass in a list of edges [(a, b), (c, d), ...]
// get out a list of [(subtreeRoot, { node1 : node1Children, node2 : node2Children, ...}), ...]
// with edges == [] it returns [(0, {0: []})]
// auto trees = centroidDecomp(vector<pair<int,int>>{{0,1},{1,2},{1,3},{3,4}});
// children maps hash with a per-run random seed (splitmix64), so anti-hash tests can't force collisions

struct SplitHash {
    static uint64_t splitmix64(uint64_t x) {
        x += 0x9e3779b97f4a7c15ULL;
        x = (x ^ (x >> 30)) * 0xbf58476d1ce4e5b9ULL;
        x = (x ^ (x >> 27)) * 0x94d049bb133111ebULL;
        return x ^ (x >> 31);
    }
    size_t operator()(uint64_t x) const {
        static const uint64_t FIXED = chrono::steady_clock::now().time_since_epoch().count();
        return splitmix64(x + FIXED);
    }
};
using ChildrenMap = unordered_map<int, vector<int>, SplitHash>;

vector<pair<int, ChildrenMap>> centroidDecomp(const vector<pair<int,int>>& edges) {
    int arrSize = 1;
    for (auto& e : edges) {
        if (e.first >= arrSize) arrSize = e.first + 1;
        if (e.second >= arrSize) arrSize = e.second + 1;
    }
    vector<int> start(arrSize + 1, 0), to(2 * edges.size());
    for (auto& e : edges) { start[e.first + 1]++; start[e.second + 1]++; }
    for (int i = 0; i < arrSize; i++) start[i + 1] += start[i];
    {
        vector<int> pos(start.begin(), start.end() - 1);
        for (auto& e : edges) { to[pos[e.first]++] = e.second; to[pos[e.second]++] = e.first; }
    }
    vector<char> removed(arrSize, 0);
    vector<int> sz(arrSize, 0);
    vector<pair<int, ChildrenMap>> res;
    res.reserve(arrSize);

    auto calcSz = [&](auto&& self, int node, int p) -> int {
        sz[node] = 1;
        for (int i = start[node]; i < start[node + 1]; i++) {
            int nxt = to[i];
            if (nxt != p && !removed[nxt]) sz[node] += self(self, nxt, node);
        }
        return sz[node];
    };
    auto findCentroid = [&](auto&& self, int node, int p, int total) -> int {
        for (int i = start[node]; i < start[node + 1]; i++) {
            int nxt = to[i];
            if (nxt != p && !removed[nxt] && sz[nxt] * 2 > total) return self(self, nxt, node, total);
        }
        return node;
    };
    auto decomp = [&](auto&& self, int s) -> void {
        int total = calcSz(calcSz, s, -1);
        int centroid = findCentroid(findCentroid, s, -1, total);
        res.emplace_back();
        res.back().first = centroid;
        auto& children = res.back().second;
        children.reserve(total);
        auto build = [&](auto&& bSelf, int node, int p) -> void {
            auto& kids = children[node];
            for (int i = start[node]; i < start[node + 1]; i++) {
                int nxt = to[i];
                if (nxt != p && !removed[nxt]) kids.push_back(nxt);
            }
            for (int i = start[node]; i < start[node + 1]; i++) {
                int nxt = to[i];
                if (nxt != p && !removed[nxt]) bSelf(bSelf, nxt, node);
            }
        };
        build(build, centroid, -1);
        removed[centroid] = 1;
        for (int i = start[centroid]; i < start[centroid + 1]; i++) {
            int nxt = to[i];
            if (!removed[nxt]) self(self, nxt);
        }
    };
    decomp(decomp, edges.empty() ? 0 : edges[0].first);
    return res;
}