#include <bits/stdc++.h>
using namespace std;
#include <unordered_map>
#include <utility>
#include <cstdint>

struct PairHash {
    size_t operator()(const std::pair<int,int>& p) const noexcept {
        return (uint64_t)(uint32_t)p.first << 32 ^ (uint32_t)p.second;
    }
};

int main() {
    cin.tie(nullptr);
    ios::sync_with_stdio(false);
    int n, t; cin >> n >> t;
    vector<vector<int>> g(n + 1);
    unordered_map<pair<int,int>,int, PairHash> cache; // maps (cameFrom, arrivedAt) -> result. -1 means not set, 0 means lose, 1 means win
    for (int i = 0; i < n - 1; i++) {
        int a, b; cin >> a >> b;
        g[a].push_back(b);
        g[b].push_back(a);
        cache[{a, b}] = -1;
        cache[{b, a}] = -1;
    }

    // dp[cameFrom][arrivedAt] is the answer from our perspective, we cannot move into cameFrom
    // -1 = no memo, 0 = lose, 1 = win
    // if banned is -1

    auto dp = [&](auto&& self, int cameFrom, int arrivedAt) -> int {
        if (cameFrom != arrivedAt && cache[{cameFrom, arrivedAt}] != -1) {
            return cache[{cameFrom, arrivedAt}];
        }

        bool canWin = false;
        for (auto adjN : g[arrivedAt]) {
            if (adjN == cameFrom) continue;
            if (!self(self, arrivedAt, adjN)) {
                canWin = true;
                break;
            }
        }
        if (canWin) {
            cache[{cameFrom, arrivedAt}] = 1;
        } else {
            cache[{cameFrom, arrivedAt}] = 0;
        }
        return cache[{cameFrom, arrivedAt}];
    };
    for (int i = 0; i < t; i++) {
        int loc; cin >> loc;
        int result = dp(dp, loc, loc);
        if (result) {
            cout << "Ron" << endl;
        } else {
            cout << "Hermione" << endl;
        }
    }
}