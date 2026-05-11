#include <bits/stdc++.h>
using namespace std;
using ll = long long;

const ll INF = LLONG_MAX / 2;

struct Node {
    int l, r;
    int nodeId;
};

struct PairHash {
    size_t operator()(const pair<int,int>& p) const {
        return hash<long long>()((long long)p.first << 32 | (unsigned int)p.second);
    }
};

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, q, s; cin >> n >> q >> s; s--;

    auto decompose = [&](auto&& self, int tl, int tr, int ql, int qr, vector<pair<int,int>>& bucket) -> void {
        // disjoint
        if (qr < tl || ql > tr) {
            return;
        }
        // fully inside
        if (ql <= tl && qr >= tr) {
            bucket.push_back({tl, tr});
            return;
        }
        int tm = (tl + tr) / 2;
        self(self, tl, tm, ql, qr, bucket);
        self(self, tm + 1, tr, ql, qr, bucket);
    };

    // we wish to decompose [0, 6]
    // decompose(decompose, 0, 10, 0, 6, b);


    auto getAll = [&](auto&& self, int tl, int tr, vector<pair<int,int>>& bucket) -> void {
        if (tl == tr) {
            bucket.push_back({tl, tr});
            return;
        }
        bucket.push_back({tl, tr});
        int tm = (tl + tr) / 2;
        self(self, tl, tm, bucket);
        self(self, tm + 1, tr, bucket);
    };
    vector<pair<int,int>> initBucket;
    getAll(getAll, 0, n - 1, initBucket);

    for (auto& [l, r] : initBucket) {
        cout << "L: " << l << " R: " << r << '\n';
    }

    // make a map of (l, r) -> node id

    unordered_map<pair<int,int>, int, PairHash> rangeToId;

    vector<Node> nodes;
    for (int idx = 0; idx < initBucket.size(); idx++) {
        auto [l, r] = initBucket[idx];
        Node node = {l, r, idx};
        nodes.push_back(node);
        rangeToId[{l, r}] = idx;
    }

    vector<vector<pair<int,ll>>> adj(initBucket.size()); // maps nodeId -> [(adjN, adjW), ...]
    for (auto [l, r] : initBucket) {
        if (l == r) continue;
        int m = (l + r) / 2;
        int idUp = rangeToId[{l, r}];
        int leftId = rangeToId[{l, m}];
        int rightId = rangeToId[{m + 1, r}];
        adj[idUp].push_back({leftId, 0});
        adj[idUp].push_back({rightId, 0});
    }

    // [0, 2] id=0
    // [0, 1] id=1
    // [0, 0] id=2
    // [1, 1] id=3
    // [2, 2] id=4



    // [0, 3] id=0
    // [0, 1] id=1
    // [0, 0] id=2
    // [1, 1] id=3
    // [2, 3] id=4
    // [2, 2] id=5
    // [3, 3] id=6
 
    
    for (int i = 0; i < q; i++) {
        int planType; cin >> planType;
        if (planType == 1) {
            cout << "plan type is 1" << endl;
            int v, u; ll w; cin >> v >> u >> w; v--; u--;
            cout << "can go from node: " << v << " to node: " << u << endl;
            int id1 = rangeToId[{v, v}];
            int id2 = rangeToId[{u, u}];
            adj[id1].push_back({id2, w});
            cout << "id1: " << id1 << " id2: " << id2 << '\n';
        } else if (planType == 2) {
            cout << "plan type is 2" << endl;
            int v, l, r; ll w; cin >> v >> l >> r >> w; v--; l--; r--;
            cout << "can go from node v: " << v << " to any node in: " << l << "..." << r << endl;
            int id1 = rangeToId[{v, v}];

            vector<pair<int,int>> bucket;
            decompose(decompose, 0, n - 1, l, r, bucket);
            for (auto [l, r] : bucket) {
                int idx = rangeToId[{l, r}];
                adj[id1].push_back({idx, w});
            }

        } else {
            cout << "plan type is 3" << endl;
            int v, l, r; ll w; cin >> v >> l >> r >> w; l--; r--; v--;
            cout << "can go from any node in" << l << "..." << r << " to node: " << v << endl;
            cout << "and weight is: " << w << endl;
            int outId = rangeToId[{v, v}];
            cout << "target idx: " << outId << endl;
            vector<pair<int,int>> bucket;
            decompose(decompose, 0, n - 1, l, r, bucket);
            for (auto [l, r] : bucket) {
                int idx = rangeToId[{l, r}];
                cout << "entry idx: " << idx << endl;
                adj[idx].push_back({outId, w});
            }
            for (auto [left, right] : bucket) {
                cout << "left: " << left << " right: " << right << endl;
            }
        }
    }

    // we start at node s
    // there is a node [s, s]
    // at most logN nodes that CONTAIN s in the range l...r
    // run dijkstra from each of those starting points to v
    vector<ll> out(n, INF);

    auto dijkstra = [&](int startId) -> void {
        vector<ll> minD(initBucket.size(), INF);
        priority_queue<pair<ll,int>, vector<pair<ll,int>>, greater<>> heap; // holds (cost, nodeId)
        heap.push({0, startId});
    
        while (heap.size()) {
            auto [cost, nodeId] = heap.top(); heap.pop();
            if (minD[nodeId] <= cost) continue;
            minD[nodeId] = cost;
            for (auto [adjN, adjW] : adj[nodeId]) {
                ll ncost = cost + adjW;
                if (minD[adjN] <= ncost) continue;
                heap.push({ncost, adjN});
            }
        }
        for (int node = 0; node < n; node++) {
            out[node] = min(out[node], minD[rangeToId[{node, node}]]);
        }
    };


    // [0, 3] id=0
    // [0, 1] id=1
    // [0, 0] id=2
    // [1, 1] id=3
    // [2, 3] id=4
    // [2, 2] id=5
    // [3, 3] id=6

    cout << "==========" << endl;

    for (auto [l, r] : initBucket) {
        cout << "l is: " << l << " r is: " << r << " s is: " << s << endl;
        if (l <= s && s <= r) {
            cout << "inrange" << endl;
            int nodeId = rangeToId[{l, r}];
            cout << "starting a dijkstra from id: " << nodeId << endl;
            dijkstra(nodeId);
        }
    }

    for (auto x : out) cout << x << " ";
}