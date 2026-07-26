#include <bits/stdc++.h>
using namespace std;
using ll = long long;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n, m; cin >> n >> m;
    vector<pair<int, int>> edges;
    vector<vector<int>> adj(n + 1);
    for (int i = 0; i < m; i++) {
        int a, b; cin >> a >> b;
        edges.push_back({a, b});
        adj[a].push_back(b);
        adj[b].push_back(a);
    }
    
    vector<bool> vis(n + 1, false);
    vector<bool> path(n + 1, false);
    vector<int> ans;

    auto explore = [&](auto&& self, int node, vector<int>& pathStack, int cameFrom) -> void {
        vis[node] = true;
        path[node] = true;
        pathStack.push_back(node);
        for (auto adjN : adj[node]) {
            if (adjN == cameFrom) continue;
            // if not in path, just go there
            if (!path[adjN]) {
                // if we already visited this before we don't need to explore again
                if (vis[adjN]) continue;
                self(self, adjN, pathStack, node);
                if (ans.size()) return;
            } else {
                // found an answer
                int i = 0;
                while (i < pathStack.size()) {
                    if (pathStack[i] != adjN) {
                        i++;
                    } else {
                        break;
                    }
                }
                for (int j = i; j < pathStack.size(); j++) {
                    ans.push_back(pathStack[j]);
                }
                ans.push_back(adjN);
                return;
            }
        }
        path[node] = false;
        pathStack.pop_back();
    };

    for (int node = 1; node <= n; node++) {
        if (vis[node]) continue;
        vector<int> pathStack;
        explore(explore, node, pathStack, -1);
        if (ans.size()) {
            break;
        }
    }

    if (ans.size() == 0) {
        cout << "IMPOSSIBLE";
        return 0;
    }
    cout << ans.size() << '\n';
    for (auto x : ans) {
        cout << x << " ";
    }

}