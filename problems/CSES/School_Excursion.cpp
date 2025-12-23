#include <bits/stdc++.h>
using namespace std;

int MAXN = 100000;

int n, m;
vector<vector<int>> adj;
vector<int> seen;

int dfs(int node) {
    seen[node] = 1;
    int cnt = 1;
    for (int nextNode : adj[node]) {
        if (!seen[nextNode]) cnt += dfs(nextNode);
    }
    return cnt;
}

// O(n^2 / W) complexity
// Supposedly NTT can be n log^2 n but I don't understand it
int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    cin >> n >> m;
    adj.assign(n + 1, {});
    for (int i = 0; i < m; i++) {
        int a, b;
        cin >> a >> b;
        adj[a].push_back(b);
        adj[b].push_back(a);
    }

    seen.assign(n + 1, 0);
    vector<int> components;
    for (int node = 1; node <= n; node++) {
        if (!seen[node]) components.push_back(dfs(node));
    }

    bitset<MAXN + 1> bs;
    bs[0] = 1;
    for (int sz : components) bs |= (bs << sz);

    for (int i = 1; i <= n; i++) cout << (bs[i] ? '1' : '0');
    cout << "\n";
    return 0;
}

// Python version (TLE on cses)
// from collections import defaultdict
// n, m = map(int, input().split())
// adjMap = defaultdict(list)
// for _ in range(m):
//     a, b = map(int, input().split())
//     adjMap[a].append(b)
//     adjMap[b].append(a)

// components = []
// seen = set()
// def dfs(node, bucket):
//     seen.add(node)
//     bucket.append(node)
//     for adj in adjMap[node]:
//         if adj in seen:
//             continue
//         dfs(adj, bucket)
// for node in range(1, n + 1):
//     if node in seen: continue
//     bucket = []
//     dfs(node, bucket)
//     components.append(len(bucket))

// bs = 1 # 0 is doable
// for sz in components:
//     nbs = bs << sz
//     bs |= nbs

// print(bin(bs)[3:])