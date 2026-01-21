#include <bits/stdc++.h>
using namespace std;

struct DSU {
    vector<int> p; // parent[node] -> rep node
    vector<int> sz; // size[repNode] -> size
    int maxSize = 1;
    int numComponents = 0;

    DSU(int n) {
        numComponents = n;
        p.push_back(0);
        sz.push_back(0);
        for (int node = 1; node <= n; node++) {
            p.push_back(node);
            sz.push_back(1);
        }
    }

    int getMaxSize() {
        return maxSize;
    }

    int find(int node) {
        if (p[node] == node) return node;
        return p[node] = find(p[node]);
    }

    bool unite(int a, int b) {
        int pa = find(a);
        int pb = find(b);
        if (pa == pb) return false;
        numComponents--;
        int sa = sz[pa];
        int sb = sz[pb];
        if (sa <= sb) {
            sz[pb] += sz[pa];
            p[pa] = pb;
            maxSize = max(maxSize, sz[pb]);
        } else {
            sz[pa] += sz[pb];
            p[pb] = pa;
            maxSize = max(maxSize, sz[pa]);
        }
        return true;
    }

    int getNumComponents() {
        return numComponents;
    }
};

int main() {
    cin.tie(nullptr);
    ios::sync_with_stdio(false);
    int n, m; cin >> n >> m;
    DSU dsu = DSU(n);
    for (int i = 0; i < m; i++) {
        int a, b; cin >> a >> b;
        dsu.unite(a, b);
        cout << dsu.getNumComponents() << " " << dsu.getMaxSize() << endl;
    }
}