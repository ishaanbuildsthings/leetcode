// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/golden-references/DeBruijnSequence.cpp
// Euler circuit (Hierholzer) on a directed graph, as a full solution to CSES "De Bruijn Sequence"
// (https://cses.fi/problemset/task/1692).
// Nodes are the (n-1)-bit strings, and each n-bit string is an edge from its prefix to its suffix. Every node has
// 2 edges in and 2 out, so an Euler circuit exists and visits every n-bit string once.
// The part to read is the dfs: take any unused edge, recurse, and push a node to the front only once all its edges
// are used, so a dead end lands at the end of the path and later loops are spliced in front of it.
// O(2^n) time and space.
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n; cin >> n;

    if (n == 1) {
        cout << "01";
        return 0;
    }

    int smallN = n - 1;
    int maxNum = (1 << smallN) - 1;

    vector<vector<int>> g(maxNum + 1);
    for (int num = 0; num <= maxNum; num++) {
        int lastPart = num & ((1 << (smallN - 1)) - 1);
        g[num].push_back(lastPart << 1);
        g[num].push_back((lastPart << 1) + 1);
    }

    deque<int> path;

    auto dfs = [&](auto&& self, int node) -> void {
        while (g[node].size()) {
            int nxt = g[node].back(); g[node].pop_back();
            self(self, nxt);
        }
        path.push_front(node);
    };

    dfs(dfs, 0);

    string res = "";
    for (int i = 0; i < smallN; i++) res.push_back('0');
    for (int i = 1; i < path.size(); i++) {
        int num = path[i];
        res.push_back(num & 1 ? '1' : '0');
    }
    cout << res;
}