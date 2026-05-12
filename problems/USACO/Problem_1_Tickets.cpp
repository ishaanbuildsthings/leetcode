#include <bits/stdc++.h>
using namespace std;
using ll = long long;

const ll INF = LLONG_MAX / 4;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, k; cin >> n >> k;

    vector<int> leafId(n + 1); // leafId[leafValue] is the position in the 4*n tree we use

    auto getLeafIds = [&](auto&& self, int nodeI, int tl, int tr) -> void {
        if (tl == tr) {
            leafId[tl] = nodeI;
            return;
        }
        int tm = (tl + tr) / 2;
        self(self, 2 * nodeI, tl, tm);
        self(self, 2 * nodeI + 1, tm + 1, tr);
    };

    getLeafIds(getLeafIds, 1, 1, n);


    auto decompose = [&](auto&& self, int nodeI, int tl, int tr, int ql, int qr,vector<int>& ids) -> void {
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

    int maxId = *max_element(leafId.begin(), leafId.end());

    // ids 1...maxId are already taken
    int totalNodes = maxId + k; // each ticket gets its own node

    vector<vector<pair<int,ll>>> adjRev(totalNodes + 1); // nodeId -> [(adjId, adjW), ...]

    auto addDownEdges = [&](auto&& self, int nodeI, int tl, int tr) -> void {
        if (tl == tr) return;
        int tm = (tl + tr) / 2;
        int idLeft = 2 * nodeI;
        int idRight = 2 * nodeI + 1;
        adjRev[idLeft].push_back({nodeI, 0});
        adjRev[idRight].push_back({nodeI, 0});
        self(self, 2 * nodeI, tl, tm);
        self(self, 2 * nodeI + 1, tm + 1, tr);
    };

    addDownEdges(addDownEdges, 1, 1, n);

    for (int i = 0; i < k; i++) {
        int c, p, a, b; cin >> c >> p >> a >> b;
        int outId = leafId[c];
        vector<int> ids;
        int ticketNodeId = maxId + 1 + i;
        adjRev[ticketNodeId].push_back({outId, p});
        decompose(decompose, 1, 1, n, a, b, ids);
        for (auto inId : ids) {
            adjRev[inId].push_back({ticketNodeId, 0});
        }
    }

    // given sources (node, startingWeight) gets a minimum distance map to all other nodes
    auto dijkstra = [&](vector<pair<int,ll>>& sources) -> vector<ll> {
        priority_queue<pair<ll,int>, vector<pair<ll,int>>, greater<>> heap; // holds (cost, nodeId)
        for (auto [node, startWeight] : sources) {
            heap.push({startWeight, node});
        }
        vector<ll> minD(maxId + k + 1, INF);
        while (heap.size()) {
            auto [cost, nodeId] = heap.top(); heap.pop();
            if (minD[nodeId] <= cost) continue;
            minD[nodeId] = cost;
            for (auto [adjN, adjW] : adjRev[nodeId]) {
                ll ncost = cost + adjW;
                if (minD[adjN] <= ncost) continue;
                heap.push({ncost, adjN});
            }
        }
        return minD;
    };

    vector<pair<int,ll>> src1 = {{leafId[1], 0}};
    auto from1 = dijkstra(src1);

    vector<pair<int,ll>> srcN = {{leafId[n], 0}};
    auto from2 = dijkstra(srcN);

    vector<pair<int,ll>> srcBoth;
    for (int node = 1; node <= maxId + k; node++) {
        ll meetCost = from1[node] + from2[node];
        srcBoth.push_back({node, min(INF, meetCost)});

    }
    auto final = dijkstra(srcBoth);

    for (int leafNode = 1; leafNode <= n; leafNode++) {
        int id = leafId[leafNode];
        ll ans = final[id];
        if (ans >= INF) {
            cout << -1 << '\n';
        } else {
            cout << ans << '\n';
        }
    }
}