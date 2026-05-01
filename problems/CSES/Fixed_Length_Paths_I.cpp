#include <bits/stdc++.h>
using namespace std;

struct Info {
    unordered_map<int,int> c; // c[edge count] -> # of paths with that
    int offset = 0; // what everything is implicitly increased by
    void shift() {
        offset++;
    }
    void add (int realSize, int amt) {
        c[realSize - offset] += amt;
    }
    int get (int realSize) {
        int target = realSize - offset;
        if (c.find(target) == c.end()) return 0;
        return c[target];
    }
};

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, k; cin >> n >> k;
    vector<vector<int>> adj(n);
    for (int i = 0; i < n - 1; i++) {
        int a, b; cin >> a >> b; a--; b--;
        adj[a].push_back(b);
        adj[b].push_back(a);
    }
    vector<vector<int>> children(n);
    auto dfsInit = [&](auto&& self, int node, int parent) -> void {
        for (auto adjN : adj[node]) {
            if (adjN == parent) continue;
            children[node].push_back(adjN);
            self(self, adjN, node);
        }
    };
    dfsInit(dfsInit, 0, -1);

    long long out = 0;

    auto dfs = [&](auto&& self, int node) -> Info {
        if (!children[node].size()) {
            Info info;
            info.add(0, 1);
            info.shift();
            return info;
        }
        vector<Info> childs;
        for (auto child : children[node]) {
            childs.push_back(move(self(self, child)));
        }
        sort(childs.begin(), childs.end(), [](const Info& a, const Info& b) {
            return a.c.size() > b.c.size();
        });
        Info& heavy = childs[0];
        out += heavy.get(k); // paths leading directly to the node
        for (int i = 1; i < childs.size(); i++) {
            Info& light = childs[i];
            // also anything that directly hits the node
            out += light.get(k);
            for (auto& [key, val] : light.c) {
                int realSz = key + light.offset;
                int targetReq = k - realSz;
                int cnt = heavy.get(targetReq);
                out += (long long)cnt * val;
            }
            // fold in
            for (auto& [key, val] : light.c) {
                int realSz = key + light.offset;
                heavy.add(realSz, val);
            }
        }
        heavy.add(0, 1);
        heavy.shift();
        return move(heavy);
    };
    dfs(dfs, 0);
    cout << out << '\n';
}