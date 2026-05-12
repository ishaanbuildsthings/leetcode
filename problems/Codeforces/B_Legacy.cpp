#include <bits/stdc++.h>
using namespace std;
using ll = long long;

const ll INF = LLONG_MAX / 4;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int N, PLANS, start; cin >> N >> PLANS >> start;

    // leaf IDs for the top half, where we broadcast and trick down
    vector<int> leafIdsA(N + 1);

    // IDs in tree 1 = 4 * n
    // IDs in tree 2 = 4 * n
    // IDs from plans = PLANS

    // total IDs  = 8 * n + PLANS

    int MAX_ID = 8 * N + PLANS;
    vector<vector<pair<int,ll>>> adj(MAX_ID + 1); // adj -> [(adjN, adjW), ...]

    // tree A IDs go from [1...4*N]
    // tree B IDs go from [4*N + 1 ... 8*N]
    // plan IDs go from [8*N + 1 ... 8*N + PLANS]

    auto buildA = [&](auto&& self, int nodeI, int tl, int tr) -> void {
        if (tl == tr) {
            leafIdsA[tl] = nodeI;
            return;
        }
        int tm = (tl + tr) / 2;
        int leftId = 2 * nodeI;
        int rightId = 2 * nodeI + 1;
        // cout << "Internal ID for node=[" << tl << "..." << tr << "] is: " << nodeI << endl;
        adj[nodeI].push_back({leftId, 0});
        adj[nodeI].push_back({rightId, 0});
        self(self, 2 * nodeI, tl, tm);
        self(self, 2 * nodeI + 1, tm + 1, tr);
    };
    buildA(buildA, 1, 1, N);

    for (int node = 1; node <= N; node++) {
        // cout << "Leaf ID for node=" << node << " is: " << leafIdsA[node] << endl;
    }

    vector<int> leafIdsB(N + 1);
    int OFFSET = 4 * N;
    auto buildB = [&](auto&& self, int nodeI, int tl, int tr) -> void {
        int realId = nodeI + OFFSET;
        if (tl == tr) {
            leafIdsB[tl] = realId;
            return;
        }
        int tm = (tl + tr) / 2;
        int leftId = 2 * nodeI + OFFSET;
        int rightId = 2 * nodeI + 1 + OFFSET;
        adj[leftId].push_back({nodeI + OFFSET, 0});
        adj[rightId].push_back({nodeI + OFFSET, 0});
        self(self, 2 * nodeI, tl, tm);
        self(self, 2 * nodeI + 1, tm + 1, tr);
    };
    buildB(buildB, 1, 1, N);

    auto decompose = [&](auto&& self, int nodeI, int tl, int tr, int ql, int qr, vector<int>& ids) -> void {
        // disjoint
        if (qr < tl || ql > tr) return;
        // fully inside
        if (ql <= tl && qr >= tr) {
            ids.push_back(nodeI);
            return;
        }
        int tm = (tl + tr) / 2;
        self(self, 2 * nodeI, tl, tm, ql, qr, ids);
        self(self, 2 * nodeI + 1, tm + 1, tr, ql, qr, ids);
    };

    // now wire in A->B leaf flow downs
    for (int node = 1; node <= N; node++) {
        int leafA = leafIdsA[node];
        int leafB = leafIdsB[node];
        adj[leafA].push_back({leafB, 0});
    }

    for (int i = 0; i < PLANS; i++) {
        int planType; cin >> planType;
        if (planType == 1) {
            int v, u; cin >> v >> u; // go from V->U directly
            ll cost; cin >> cost;
            int leafV = leafIdsA[v];
            int leafU = leafIdsA[u];
            adj[leafV].push_back({leafU, cost});
        } else if (planType == 2) {
            int v, l, r; cin >> v >> l >> r;
            ll cost; cin >> cost;
            // go from v -> [L...R]
            int leafId = leafIdsA[v];
            vector<int> ids;
            decompose(decompose, 1, 1, N, l, r, ids);
            for (auto id : ids) {
                adj[leafId].push_back({id, cost});
            }
        } else {
            int v, l, r; cin >> v >> l >> r;
            ll cost; cin >> cost;
            vector<int> ids;
            int leafId = leafIdsA[v];
            decompose(decompose, 1, 1, N, l, r, ids);
            for (auto id : ids) {
                adj[id + OFFSET].push_back({leafId, cost});
            }
        }
    }

    priority_queue<pair<long long, int>, vector<pair<long long, int>>, greater<>> heap; // holds (cost, node)
    heap.push({0,leafIdsA[start]});
    vector<ll> minD(8 * N + PLANS + 1, INF);
    while (heap.size()) {
        auto [cost, node] = heap.top(); heap.pop();
        if (minD[node] <= cost) continue;
        minD[node] = cost;
        for (auto [adjN, adjW] : adj[node]) {
            ll ncost = cost + adjW;
            if (minD[adjN] <= ncost) continue;
            heap.push({ncost, adjN});
        }
    }

    for (int node = 1; node <= N; node++) {
        int id = leafIdsB[node];
        ll minDist = minD[id];
        if (minDist >= INF) {
            cout << -1 << " ";
        } else {
            cout << minDist << " ";
        }
    }
}