#include <bits/stdc++.h>
using namespace std;

const int maxN = 50001;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n, m;
    cin >> n >> m;
    vector<vector<int>> g(n);
    vector<int> indeg(n, 0);
    vector<pair<int,int>> edges;
    edges.reserve(m);

    for (int _ = 0; _ < m; _++) {
        int a, b;
        cin >> a >> b;
        a -= 1;
        b -= 1;
        edges.push_back({a, b});
    }
    for (auto [a, b] : edges) {
        g[b].push_back(a);
        indeg[a] += 1;
    }

    deque<int> tails;
    for (int node = 0; node < n; node++) {
        if (indeg[node] == 0) tails.push_back(node);
    }

    static bitset<maxN> dp[maxN]; // stores bitset of reachable nodes
    for (int i = 0; i < n; i++) dp[i].set(i);

    while (!tails.empty()) {
        int node = tails.front();
        tails.pop_front();
        for (int adj : g[node]) {
            indeg[adj] -= 1;
            dp[adj] |= dp[node];
            if (indeg[adj] == 0) tails.push_back(adj);
        }
    }

    vector<int> res;
    res.reserve(n);
    for (int node = 0; node < n; node++) {
        res.push_back((int)dp[node].count());
    }
    for (int i = 0; i < n; i++) {
        cout << res[i] << (i + 1 == n ? '\n' : ' ');
    }

    /*
         B
         v
      A->C

    We should start at C which has 1 reachable node, so invert the edges:

        B
        ^
     A<-C

     # Once C is finished we remove a "downstream" dependency from A and B, they're both ready as all their "children" are ready
     # Their answer would already be set as the bitmask of their "downstream" reachable nodes
    */

    return 0;
}



// O(n^2 / W) python version TLE (bottom up toposort + dp + bitset)
// from collections import deque
// n, m = map(int, input().split())
// g = [[] for _ in range(n)]
// indeg = [0] * n
// edges = []
// for _ in range(m):
//     a, b = map(int, input().split())
//     a -= 1
//     b -= 1
//     edges.append([a, b])
// for a, b in edges:
//     g[b].append(a)
//     indeg[a] += 1

// tails = deque([node for node in range(n) if indeg[node] == 0])
// dp = [(1 << i) for i in range(n)] # stores bitset of reachable nodes
// while tails:
//     node = tails.popleft()
//     for adj in g[node]:
//         indeg[adj] -= 1
//         dp[adj] |= dp[node]
//         if indeg[adj] == 0:
//             tails.append(adj)

// res = []
// for node in range(n):
//     res.append(bin(dp[node]).count('1'))
// print(*res)

// """
//      B
//      v
//   A->C

// We should start at C which has 1 reachable node, so invert the edges:

//     B
//     ^
//  A<-C

//  # Once C is finished we remove a "downstream" dependency from A and B, they're both ready as all their "children" are ready
//  # Their answer would already be set as the bitmask of their "downstream" reachable nodes
// """
