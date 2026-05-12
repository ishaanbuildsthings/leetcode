#include <bits/stdc++.h>
using namespace std;
using ll = long long;
const int INF = INT_MAX / 4;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n; cin >> n;
    vector<int> A(n + 1); for (int i = 0; i < n; i++) cin >> A[i + 1]; // we can jump this high, i meters below the ground
    vector<int> B(n + 1); for (int i = 0; i < n; i++) cin >> B[i + 1]; // slip down

    vector<int> slipIds(n + 1); // slipIds[position] -> id of that slippery node

    auto makeSlipIds = [&](auto&& self, int nodeI, int tl, int tr) -> void {
        if (tl == tr) {
            slipIds[tl] = nodeI;
            return;
        }
        int tm = (tl + tr) / 2;
        self(self, 2 * nodeI, tl, tm);
        self(self, 2 * nodeI + 1, tm + 1, tr);
    };
    makeSlipIds(makeSlipIds, 1, 0, n);

    int maxSlipId = *max_element(slipIds.begin(), slipIds.end());

    vector<int> stableIds(n + 1);
    for (int node = 0; node <= n; node++) {
        stableIds[node] = maxSlipId + 1 + node;
    }

    int maxStableId = *max_element(stableIds.begin(), stableIds.end());
    int maxId = maxStableId + n;

    vector<vector<pair<int,int>>> adj(maxId + 1); // adj[node] -> [(adjN, adjW), ...]

    auto trickle = [&](auto&& self, int nodeI, int tl, int tr) -> void {
        if (tl == tr) return;

        int leftId = 2 * nodeI;
        int rightId = 2 * nodeI + 1;
        adj[nodeI].push_back({leftId, 0});
        adj[nodeI].push_back({rightId, 0});
        int tm = (tl + tr) / 2;
        self(self, 2 * nodeI, tl, tm);
        self(self, 2 * nodeI + 1, tm + 1, tr);
    };
    trickle(trickle, 1, 0, n);

    // for every slip node, connect it to its drained node
    for (int node = 0; node <= n; node++) {
        int slipId = slipIds[node];
        int slipTo = B[node] + node;
        int stableId = stableIds[slipTo];
        adj[slipId].push_back({stableId, 0});
    }


    auto decompose = [&](auto&& self, int nodeI, int tl, int tr, int ql, int qr, vector<int>& bucket) -> void {
        // disjoint
        if (qr < tl || ql > tr) return;
        // fully inside
        if (ql <= tl && qr >= tr) {
            bucket.push_back(nodeI);
            return;
        }
        int tm = (tl + tr) / 2;
        self(self, 2 * nodeI, tl, tm, ql, qr, bucket);
        self(self, 2 * nodeI + 1, tm + 1, tr, ql, qr, bucket);
    };

    // now for each edge, we go stable -> decomposition node, and the decomposition node trickles down

    // and ids for the ranges
    // these start at maxSlipId + N + 1

    for (int node = 1; node <= n; node++) {
        int R = node;
        int L = max(0, node - A[node]);

        int stableId = stableIds[node];
        int rangeId = maxStableId + node;
        adj[stableId].push_back({rangeId, 1});
        vector<int> bucket;
        decompose(decompose, 1, 0, n, L, R, bucket);
        // we go from node -> [L...R]
        for (auto id : bucket) {
            adj[rangeId].push_back({id, 0});
        }
    }

    vector<int> minD(maxId + 1, INF);
    vector<int> parent(maxId + 1, -1);
    priority_queue<pair<ll,int>, vector<pair<ll,int>>, greater<>> heap; // holds (cost, node)
    heap.push({0, stableIds[n]});
    minD[stableIds[n]] = 0;
    while (heap.size()) {
        auto [cost, nodeId] = heap.top(); heap.pop();
        if (minD[nodeId] != cost) continue;
        for (auto [adjN, adjW] : adj[nodeId]) {
            int ncost = cost + adjW;
            if (minD[adjN] <= ncost) continue;
            minD[adjN] = ncost;
            parent[adjN] = nodeId;
            heap.push({ncost, adjN});
        }
    }

    int goal = slipIds[0];
    if (minD[goal] >= INF) {
        cout << -1 << '\n';
        return 0;
    }

    vector<int> slipNodeToDepth(maxId + 1, -1);
    for (int d = 0; d <= n; d++) slipNodeToDepth[slipIds[d]] = d;

    vector<int> depths;
    int cur = goal;
    while (cur != -1) {
        if (slipNodeToDepth[cur] != -1) depths.push_back(slipNodeToDepth[cur]);
        cur = parent[cur];
    }
    reverse(depths.begin(), depths.end());

    if (!depths.empty() && depths.front() == n) depths.erase(depths.begin());

    cout << minD[goal] << '\n';
    for (int d : depths) cout << d << ' ';
    cout << '\n';
}