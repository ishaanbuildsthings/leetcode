#include <bits/stdc++.h>
using namespace std;
using ll = long long;

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
    
    vector<int> sz(n);
    vector<bool> removed(n);
    vector<int> distCounts(n);
    vector<int> touchedDistances;

    // gives us the size of a piece
    // can't walk back to the passed in parent
    // can't walk over removed centroids
    auto computeSize = [&](auto&& self, int node, int parent) -> void {
        int sizeHere = 1;
        for (auto adjN : adj[node]) {
            if (adjN == parent) continue;
            if (removed[adjN]) continue;
            self(self, adjN, node);
            sizeHere += sz[adjN];
        }
        sz[node] = sizeHere;
    };

    auto findCentroid = [&](auto&& self, int node, int parent, int pieceSize) -> int {
        int maxChildPiece = 0;
        int maxChild = -1;
        for (auto adjN : adj[node]) {
            if (adjN == parent) continue;
            if (removed[adjN]) continue;
            if (sz[adjN] > maxChildPiece) {
                maxChildPiece = sz[adjN];
                maxChild = adjN;
            }
        }
        int sizeAbove = pieceSize - sz[node];
        int largestPiece = max(sizeAbove, maxChildPiece);
        if (largestPiece <= pieceSize / 2) {
            return node;
        }
        return self(self, maxChild, node, pieceSize);
    };

    ll out = 0;

    auto dfs = [&](auto&& self, int node, int parent, int dist, bool collect) -> void {
        if (collect) {
            distCounts[dist]++;
            touchedDistances.push_back(dist);
        } else {
            int req = k - dist;
            if (req >= 0 && req < distCounts.size()) {
                out += distCounts[req];
            }
        }
        for (auto adjN : adj[node]) {
            if (removed[adjN]) continue;
            if (adjN == parent) continue;
            self(self, adjN, node, dist + 1, collect);
        }
    };

    auto decompose = [&](auto&& self, int entry) -> void {
        // 1. compute the size of this piece
        computeSize(computeSize, entry, -1);
        int pieceSize = sz[entry];

        // 2. find the centroid
        int centroid = findCentroid(findCentroid, entry, -1, pieceSize);

        // 3. do some work

        distCounts[0] = 1;
        touchedDistances.push_back(0);

        for (auto adjN : adj[centroid]) {
            if (removed[adjN]) continue;
            dfs(dfs, adjN, centroid, 1, false);
            dfs(dfs, adjN, centroid, 1, true);
        }
        for (auto dist : touchedDistances) {
            distCounts[dist] = 0;
        }
        touchedDistances.clear();


        // 4. remove the centroid
        removed[centroid] = true;


        // 5. recurse on non removed neighbors
        for (auto adjN : adj[centroid]) {
            if (removed[adjN]) continue;
            self(self, adjN);
        }
    };

    decompose(decompose, 0);
    cout << out << '\n';
}