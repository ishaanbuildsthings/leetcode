#include <bits/stdc++.h>
using namespace std;

void solve() {
    int n; cin >> n;
    vector<int> A(n); for (int i = 0; i < n; i++) cin >> A[i];
    vector<vector<int>> g(n + 1);
    for (int i = 0; i < n - 1; i++) {
        int a, b; cin >> a >> b;
        g[a].push_back(b);
        g[b].push_back(a);
    }
    long long out = 0;

    vector<unordered_map<int,int>> below(n + 1); // below[node] holds a map of colors -> frequency that can go up to this root with no blocker
    auto dfs = [&](auto&& self, int node, int parent) -> void {
        // cerr << "dfs called on: " << node << endl;
        // cerr << "graph adj size: " << g[node].size() << endl;
        int color = A[node - 1];
        // cerr << "color: " << color << endl;
        if (node != 1 && g[node].size() == 1) {
            // cerr << "node is a base case, setting and returning" << endl;
            below[node] = {{color, 1}};
            return;
        }
        
        // process children
        for (auto adjN : g[node]) {
            if (adjN != parent) {
                self(self, adjN, node);
            }
        }

        unordered_map<int,int> currMap = {{color, 1}};
        for (auto adjN : g[node]) {
            if (adjN == parent) continue;
            auto& childMp = below[adjN];
            if (childMp.size() > currMap.size()) {
                swap(childMp, currMap);
            }
            for (const auto &kv : childMp) {
                auto childColor = kv.first;
                auto childFrq = kv.second;
                if (childColor != color) {
                    if (currMap.find(childColor) != currMap.end()) out += 1LL * childFrq * currMap[childColor];
                }
                currMap[kv.first] += childMp[kv.first];
            }
        }
        out += currMap[color] - 1;
        currMap[color] = 1;
        below[node] = move(currMap);
    };
    dfs(dfs, 1, 0);
    cout << out << '\n';
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int t; cin >> t;
    while (t--) {
        solve();
    }
}


// (1) [2]
// (3)
// [4]
// (5)