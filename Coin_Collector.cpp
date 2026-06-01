#include <bits/stdc++.h>
using namespace std;
using ll = long long;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m; cin >> n >> m;
    vector<int> coins(n + 1); for (int i = 0; i < n; i++) cin >> coins[i + 1];

    vector<int> parents(n + 1);
    for (int node = 1; node <= n; node++) parents[node] = node;

    auto find = [&](auto&& self, int node) -> int {
        if (parents[node] == node) return node;
        int par = parents[node];
        int parpar = parents[par];
        parents[node] = parpar;
        return self(self, parpar);
    };

    auto unite = [&](int a, int b) -> bool {
        int upA = find(find, a);
        int upB = find(find, b);
        if (upA == upB) return false;
        parents[upA] = upB;
        coins[upB] += coins[upA];
        return true;
    };

    for (int i = 0; i < m; i++) {
        int a, b; cin >> a >> b;
        unite(a, b);
    }

    int res = 0;
    for (int node = 1; node <= n; node++) {
        res = max(res, coins[find(find, node)]);
    }
    cout << res;
    

}