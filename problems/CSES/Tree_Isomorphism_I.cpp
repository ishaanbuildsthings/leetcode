#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// TEMPLATE BY ISHAAN AGRAWAL, github: ishaanbuildsthings

// edgeList = {{a, b}, {c, d}, ...}
// if zeroIndex is true, assumes the root is 0, returns a vector `children` that goes up to `children[n-1]` (n-1 is inferred from the edgeList)
// if zeroIndex is false, assumes the root is 1, returns a vector `children` that goes up to `children[n]`, children[0] is empty and unused
vector<vector<int>> edgeListToTree(const vector<pair<int, int>>& edgeList, bool zeroIndexed = true) {
    int n = (int)edgeList.size() + 1;
    int size = zeroIndexed ? n : n + 1;
    int root = zeroIndexed ? 0 : 1;
    vector<vector<int>> edgeMap(size);
    for (auto& [a, b] : edgeList) {
        edgeMap[a].push_back(b);
        edgeMap[b].push_back(a);
    }
    vector<vector<int>> children(size);
    vector<int> parent(size, -1);
    vector<int> stk = {root};
    while (!stk.empty()) {
        int node = stk.back();
        stk.pop_back();
        for (int adj : edgeMap[node]) {
            if (adj == parent[node]) continue;
            parent[adj] = node;
            children[node].push_back(adj);
            stk.push_back(adj);
        }
    }
    return children;
}

uint64_t FIXED = chrono::steady_clock::now().time_since_epoch().count();

uint64_t mix(uint64_t x) {
    x += 0x9e3779b97f4a7c15 + FIXED;
    x = (x ^ (x >> 30)) * 0xbf58476d1ce4e5b9;
    x = (x ^ (x >> 27)) * 0x94d049bb133111eb;
    return x ^ (x >> 31);
}

void solve() {
    int n; cin >> n;
    vector<pair<int,int>> edges1;
    for (int i = 0; i < n - 1; i++) {
        int a, b; cin >> a >> b;
        edges1.push_back({a, b});
    }

    vector<pair<int,int>> edges2;
    for (int i = 0; i < n - 1; i++) {
        int a, b; cin >> a >> b;
        edges2.push_back({a, b});
    }

    auto children1 = edgeListToTree(edges1, false);
    auto children2 = edgeListToTree(edges2, false);

    auto dfs = [&](auto&& self, auto& children, int node) -> uint64_t {
        if (children[node].size() == 0) {
            return mix(1);
        }
        vector<uint64_t> childHashes;
        for (auto child : children[node]) {
            auto childHash = self(self, children, child);
            childHashes.push_back(childHash);
        }
        uint64_t h = 1;
        sort(childHashes.begin(), childHashes.end());
        for (auto childHash : childHashes) {
            h *= 1000000007;
            h += childHash;
        }
        return mix(h);
    };

    auto h1 = dfs(dfs, children1, 1);
    auto h2 = dfs(dfs, children2, 1);

    cout << (h1 == h2 ? "YES" : "NO") << '\n';

}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int t; cin >> t;
    while (t--) solve();
}