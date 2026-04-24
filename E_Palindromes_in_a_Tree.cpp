#include<bits/stdc++.h>
using namespace std;

struct Info {
    unordered_map<int,int> frq; // maps bitmask -> count
    int offset = 0;

    void shift(int x) {
        offset ^= x;
    }

    void add(int val, int cnt) {
        frq[val ^ offset] += cnt;
    }

    int get(int realMask) {
        auto it = frq.find(realMask ^ offset);
        return it == frq.end() ? 0 : it->second;
    }
};

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n; cin >> n;
    vector<vector<int>> adj(n + 1);
    for (int i = 0; i < n - 1; i++) {
        int a, b; cin >> a >> b;
        adj[a].push_back(b);
        adj[b].push_back(a);
    }
    vector<char> v(n + 1);
    for (int i = 0; i < n; i++) {
        char c; cin >> c;
        v[i + 1] = c;
    }
    vector<vector<int>> children(n + 1);
    auto make = [&](auto&& self, int node, int parent) -> void {
        for (auto adjN : adj[node]) {
            if (adjN == parent) continue;
            children[node].push_back(adjN);
            self(self, adjN, node);
        }
    };
    make(make, 1, 0);

    vector<long long> res(n + 1);

    auto dfs = [&](auto&& self, int node) -> Info {
        char c = v[node];
        int idx = c - 'a';
        int bit = (1 << idx);
        if (!children[node].size()) {
            Info info;
            info.add(bit, 1);
            res[node] = 1; // single path
            return info;
        }

        vector<Info> childs;
        for (auto child : children[node]) {
            childs.push_back(move(self(self, child)));
        }
        // heavy map first
        sort(childs.begin(), childs.end(),
        [](const Info& a, const Info& b) { return a.frq.size() > b.frq.size(); });

        Info& heavy = childs[0];
        heavy.shift(bit);
        for (int i = 1; i < childs.size(); i++) {
            Info& light = childs[i];
            for (auto& [k, v] : light.frq) {
                int nk = k ^ light.offset;
                res[node] += (long long)v * heavy.get(nk); // xor with itself
                for (int b = 0; b < 20; b++) {
                    int nbit = (1 << b);
                    res[node] += (long long)v * heavy.get(nk ^ nbit); // xor with a 1 off mask
                }
            }
            // fold in
            for (auto& [k, v] : light.frq) {
                heavy.add(k ^ light.offset, v);
            }
        }

        heavy.add(bit, 1); // add root
        // add paths ending at root
        res[node] += heavy.get(0);
        for (int b = 0; b < 20; b++) {
            res[node] += heavy.get(1 << b);
        }

        return move(heavy);
    };

    dfs(dfs, 1);

    for (int i = 1; i <= n; i++) cout << res[i] << " ";

    
}