#include <bits/stdc++.h>
using namespace std;

uint64_t FIXED = chrono::steady_clock::now().time_since_epoch().count();

uint64_t mix(uint64_t x) {
    x += 0x9e3779b97f4a7c15 + FIXED;
    x = (x ^ (x >> 30)) * 0xbf58476d1ce4e5b9;
    x = (x ^ (x >> 27)) * 0x94d049bb133111eb;
    return x ^ (x >> 31);
}

// TEMPLATE BY ISHAANBUILDSTHINGS on github
// in:  children = {{}, {2,3}, {4,5}, {}, {}, {}}   // children[v], parent excluded; root matches its indexing
// out: hashes   = {0, h1, h2, mix1, mix1, mix1}    // hashes[v] = 64-bit hash of v's subtree
// hashes[u] == hashes[v] iff those subtrees are isomorphic as rooted unordered trees
// O(n log n) time (sorting each node's child hashes), O(n) space
// auto hashes1 = subtreeHashes(edgeListToTree(edges1, false), 1);
// auto hashes2 = subtreeHashes(edgeListToTree(edges2, false), 1);
vector<uint64_t> subtreeHashes(const vector<vector<int>>& children, int root) {
    int size = (int)children.size();
    vector<uint64_t> hashes(size, 0);
    vector<int> order;
    order.reserve(size);
    vector<int> stk = {root};
    while (!stk.empty()) {
        int node = stk.back();
        stk.pop_back();
        order.push_back(node);
        for (int child : children[node]) {
            stk.push_back(child);
        }
    }
    for (int i = (int)order.size() - 1; i >= 0; i--) {
        int node = order[i];
        vector<uint64_t> childHashes;
        for (int child : children[node]) {
            childHashes.push_back(hashes[child]);
        }
        sort(childHashes.begin(), childHashes.end());
        uint64_t h = 1;
        for (uint64_t childHash : childHashes) {
            h *= 1000000007;
            h += childHash;
        }
        hashes[node] = mix(h);
    }
    return hashes;
}