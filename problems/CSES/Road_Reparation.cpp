#include <bits/stdc++.h>
using namespace std;
using ll = long long;

struct DSU {
    vector<int> parents;
    vector<int> sz;
    DSU(int n) {
        parents.resize(n + 1);
        for (int node = 1; node <= n; node++) {
            parents[node] = node;
        }
        sz.assign(n + 1, 1);
    }

    bool unite(int a, int b) {
        int upA = find(a);
        int upB = find(b);
        if (upA == upB) return false;
        int sizeA = sz[upA];
        int sizeB = sz[upB];
        if (sizeA > sizeB) {
            swap(a, b);
        }
        // join A under B
        sz[upB] += sizeA;
        parents[upA] = upB;
        return true;
    }

    int find(int node) {
        if (parents[node] == node) return node;
        int root = find(parents[node]);
        parents[node] = root;
        return root;
    }
};

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m; cin >> n >> m;
    vector<tuple<ll,int,int>> edges; // (w, a, b)
    for (int i = 0; i < m; i++) {
        int a, b, w; cin >> a >> b >> w;
        edges.push_back({w, a, b});
    }
    DSU dsu(n);
    sort(edges.begin(), edges.end());
    ll out = 0;
    for (auto [w, a, b] : edges) {
        if (dsu.unite(a, b)) {
            out += w;
        }
    }
    for (int node = 2; node <= n; node++) {
        if (dsu.find(node) != dsu.find(1)) {
            cout << "IMPOSSIBLE";
            return 0;
        }
    }
    cout << out;
}