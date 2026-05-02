#include <bits/stdc++.h>
using namespace std;
using ll = long long;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n; cin >> n;
    vector<vector<int>> adj(n);
    for (int i = 0; i < n - 1; i++) {
        int a, b; cin >> a >> b; a--; b--;
        adj[a].push_back(b);
        adj[b].push_back(a);
    }

    string abc = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";

    vector<int> sz(n);
    vector<char> removed(n, 0);
    
    auto computeSize = [&](auto&& self, int node, int parent) -> void {
        int szHere = 1;
        for (auto adjN : adj[node]) {
            if (adjN == parent) continue;
            if (removed[adjN]) continue;
            self(self, adjN, node);
            szHere += sz[adjN];
        }
        sz[node] = szHere;
    };

    auto findCentroid = [&](auto&& self, int node, int parent, int pieceSize) -> int {
        int maxChildSz = 0;
        int maxChild = -1;
        for (auto adjN : adj[node]) {
            if (adjN == parent) continue;
            if (removed[adjN]) continue;
            if (sz[adjN] > maxChildSz) {
                maxChildSz = sz[adjN];
                maxChild = adjN;
            }
        }
        if (maxChildSz <= (pieceSize / 2)) {
            return node;
        }
        return self(self, maxChild, node, pieceSize);
    };

    vector<char> res(n);

    auto decompose = [&](auto&& self, int entry, int letterI) -> void {
        // 1. get sizes
        computeSize(computeSize, entry, -1);
        int pieceSize = sz[entry];

        // cerr << "running" << endl;

        // 2. get centroid
        int centroid = findCentroid(findCentroid, entry, -1, pieceSize);

        // cerr << "centroid is: " << centroid << endl;

        // 3. do work
        res[centroid] = abc[letterI];

        // 4. remove centroid
        removed[centroid] = true;

        // 5. recurse
        for (auto adjN : adj[centroid]) {
            if (removed[adjN]) continue;
            self(self, adjN, letterI + 1);
        }
    };

    decompose(decompose, 0, 0);

    for (auto x : res) cout << x << " ";
}