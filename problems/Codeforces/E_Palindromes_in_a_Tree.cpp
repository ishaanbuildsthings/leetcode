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
    string s; cin >> s;
    vector<int> vals(n);
    for (int i = 0; i < n; i++) {
        char c = s[i];
        int b = c - 'a';
        vals[i] = (1 << b);
    }
    vector<int> sz(n);
    vector<char> removed(n, 0);
    vector<int> cnt(1 << 20, 0); // maps bitmask -> count of it
    vector<int> touched; // masks we incremented, for cheap reset between centroids
    vector<ll> res(n, 1); // every vertex itself is a length-1 palindromic path

    auto sizes = [&](auto&& self, int node, int parent) -> void {
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
        int maxChildSize = 0;
        int heavyChild = -1;
        for (auto adjN : adj[node]) {
            if (adjN == parent) continue;
            if (removed[adjN]) continue;
            if (sz[adjN] > maxChildSize) {
                maxChildSize = sz[adjN];
                heavyChild = adjN;
            }
        }
        if (maxChildSize <= pieceSize / 2) {
            return node;
        }
        return self(self, heavyChild, node, pieceSize);
    };
    auto fillBranch = [&](auto&& self, int node, int parent, int mask) -> void {
        cnt[mask]++;
        touched.push_back(mask);
        for (auto adjN : adj[node]) {
            if (adjN == parent || removed[adjN]) continue;
            self(self, adjN, node, mask ^ vals[adjN]);
        }
    };
    auto unfillBranch = [&](auto&& self, int node, int parent, int mask) -> void {
        cnt[mask]--;
        for (auto adjN : adj[node]) {
            if (adjN == parent || removed[adjN]) continue;
            self(self, adjN, node, mask ^ vals[adjN]);
        }
    };
    // cross-branch palindromic paths through c, bubbles up sum, credits res[node]
    // returns total P over this branch (used for centroid's credit)
    auto scoreCross = [&](auto&& self, int node, int parent, int mask, int centroidMask) -> ll {
        ll paths = 0;
        for (auto adjN : adj[node]) {
            if (adjN == parent || removed[adjN]) continue;
            paths += self(self, adjN, node, mask ^ vals[adjN], centroidMask);
        }
        int key = mask ^ centroidMask;
        paths += cnt[key];
        for (int b = 0; b < 20; b++) {
            paths += cnt[key ^ (1 << b)];
        }
        res[node] += paths;
        return paths;
    };
    // paths that end at centroid, for each x in branch, palindrome iff (mask ^ centroidMask) is a target
    // bubbles up the count, credits res[node], returns total endpoint paths in this branch
    auto scoreEndpoint = [&](auto&& self, int node, int parent, int mask, int centroidMask) -> ll {
        ll paths = 0;
        for (auto adjN : adj[node]) {
            if (adjN == parent || removed[adjN]) continue;
            paths += self(self, adjN, node, mask ^ vals[adjN], centroidMask);
        }
        int pathXor = mask ^ centroidMask;
        bool palindrome = (pathXor == 0);
        for (int b = 0; b < 20 && !palindrome; b++) {
            if (pathXor == (1 << b)) palindrome = true;
        }
        if (palindrome) paths += 1;
        res[node] += paths;
        return paths;
    };
    auto decompose = [&](auto&& self, int node) -> void {
        // 1. set the sizes
        sizes(sizes, node, -1);
        int pieceSize = sz[node];

        // 2. find the centroid
        int centroid = findCentroid(findCentroid, node, -1, pieceSize);
        int centroidMask = vals[centroid];

        // 3. do some work
        // Pass A: fill cnt with all branches
        for (auto adjN : adj[centroid]) {
            if (removed[adjN]) continue;
            fillBranch(fillBranch, adjN, centroid, vals[adjN]);
        }

        // Pass B: per-branch unfill, score cross, fill back. track 2x cross paths
        ll totalCross2x = 0;
        for (auto adjN : adj[centroid]) {
            if (removed[adjN]) continue;
            unfillBranch(unfillBranch, adjN, centroid, vals[adjN]);
            totalCross2x += scoreCross(scoreCross, adjN, centroid, vals[adjN], centroidMask);
            fillBranch(fillBranch, adjN, centroid, vals[adjN]);
        }

        // Pass C: per-branch score paths ending at c. track total for c's credit
        ll totalEndpoint = 0;
        for (auto adjN : adj[centroid]) {
            if (removed[adjN]) continue;
            totalEndpoint += scoreEndpoint(scoreEndpoint, adjN, centroid, vals[adjN], centroidMask);
        }

        // centroid credit: cross paths counted twice (divide), endpoint counted once
        // the single-vertex c path was set in the result
        res[centroid] += totalCross2x / 2 + totalEndpoint;

        // cleanup everything by zeroing only the masks we touched
        for (int m : touched) cnt[m] = 0;
        touched.clear();

        // 4. remove the centroid
        removed[centroid] = true;

        // 5. decompose
        for (auto adjN : adj[centroid]) {
            if (removed[adjN]) continue;
            self(self, adjN);
        }
    };
    decompose(decompose, 0);
    for (int i = 0; i < n; i++) cout << res[i] << " \n"[i == n - 1];
}