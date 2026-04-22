#include <bits/stdc++.h>
using namespace std;

struct Info {
    unordered_map<int,int> frq; // color -> frequency
    int maxFreq; // biggest frequency
    long long sumDominating;
};

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n; cin >> n;
    vector<int> C(n + 1); for (int i = 0; i < n; i++) {
        cin >> C[i + 1];
    }
    vector<vector<int>> adj(n + 1);
    for (int i = 0; i < n - 1; i++) {
        int a, b; cin >> a >> b; adj[a].push_back(b); adj[b].push_back(a);
    }

    vector<vector<int>> children(n + 1);
    auto makeChildren = [&](auto&& self, int node, int parent) -> void {
        for (auto adjN : adj[node]) {
            if (adjN == parent) continue;
            children[node].push_back(adjN);
            self(self, adjN, node);
        }
    };
    makeChildren(makeChildren, 1, 0);

    vector<long long> res(n + 1);

    auto dfs = [&](auto&& self, int node) -> Info {
        if (children[node].size() == 0) {
            Info i;
            i.frq[C[node]] = 1;
            i.sumDominating = C[node];
            i.maxFreq = 1;
            res[node] = i.sumDominating;
            return i;
        }
        vector<Info> childs;
        for (auto child : children[node]) {
            childs.push_back(self(self, child));
        }

        // sort putting largest maps first
        sort(childs.begin(), childs.end(), [](const Info& a, const Info& b) {
            return a.frq.size() > b.frq.size();
        });

        Info big = move(childs[0]);
        for (int i = 1; i < childs.size(); i++) {
            Info& small = childs[i];
            for (auto& [color, count] : small.frq) {
                big.frq[color] += count;
                if (big.frq[color] == big.maxFreq) {
                    big.sumDominating += color;
                } else if (big.frq[color] > big.maxFreq) {
                    big.maxFreq = big.frq[color];
                    big.sumDominating = color;
                }
            }
        }
        big.frq[C[node]] += 1;
        if (big.frq[C[node]] > big.maxFreq) {
            big.maxFreq += 1;
            big.sumDominating = C[node];
        } else if (big.frq[C[node]] == big.maxFreq) {
            big.sumDominating += C[node];
        }
        res[node] = big.sumDominating;
        return big;
    };

    dfs(dfs, 1);

    for (int i = 1; i <= n; i++) cout << res[i] << " ";


}