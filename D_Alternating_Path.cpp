#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int t; cin >> t;
    while (t--) {
        int n, m; cin >> n >> m;
        vector<vector<int>> g(n + 1);
        for (int i = 0; i < m; i++) {
            int a, b; cin >> a >> b;
            g[a].push_back(b);
            g[b].push_back(a);
        }

        vector<int> color(n + 1, -1);
        auto dfs = [&](auto&& self, int node, int reqColor, vector<int>& carry, bool& fail) -> void {
            carry[reqColor]++;
            color[node] = reqColor;
            for (auto adjN : g[node]) {
                // if adj color is opposite we are good
                if (color[adjN] == (reqColor ^ 1)) continue;
                // if color is same we fail
                if (color[adjN] == reqColor) {
                    fail = true;
                    continue;
                }
                // if color is unset we explore
                self(self,adjN,reqColor^1,carry,fail);
            }

        };
        long long out = 0;
        for (int node = 1; node <= n; node++) {
            if (color[node] != -1) continue;
            bool failFound = false;
            vector<int> carry = {0, 0}; // tracks count of each color
            dfs(dfs,node, 1, carry, failFound);
            if (!failFound) {
                out += max(carry[0],carry[1]);
            }
        }

        cout << out << '\n';
    }
}