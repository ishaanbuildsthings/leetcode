#include <bits/stdc++.h>
using namespace std;
using ll = long long;



struct LCA {
    int n, LOG;
    vector<int> dep;
    vector<vector<int>> up;
    
    LCA(int nNodes, vector<vector<int>>& adj, int root) {
        n = nNodes;
        LOG = max(1, __lg(n) + 1);
        dep.assign(n + 1, 0);
        up.assign(LOG, vector<int>(n + 1, root));
        
        // BFS to set up[0] (immediate parent) and depths
        vector<bool> vis(n + 1, false);
        queue<int> q;
        q.push(root);
        vis[root] = true;
        while (!q.empty()) {
            int v = q.front(); q.pop();
            for (int u : adj[v]) {
                if (vis[u]) continue;
                vis[u] = true;
                dep[u] = dep[v] + 1;
                up[0][u] = v;
                q.push(u);
            }
        }
        
        // Build sparse table
        for (int k = 1; k < LOG; k++)
            for (int v = 1; v <= n; v++)
                up[k][v] = up[k-1][up[k-1][v]];
    }
    
    int kthAncestor(int v, int k) {
        for (int i = LOG - 1; i >= 0; i--)
            if (k >> i & 1) v = up[i][v];
        return v;
    }
    
    int lca(int a, int b) {
        if (dep[a] < dep[b]) swap(a, b);
        a = kthAncestor(a, dep[a] - dep[b]);
        if (a == b) return a;
        for (int k = LOG - 1; k >= 0; k--)
            if (up[k][a] != up[k][b]) { a = up[k][a]; b = up[k][b]; }
        return up[0][a];
    }
    
    int pathDist(int a, int b) {
        return dep[a] + dep[b] - 2 * dep[lca(a, b)];
    }
};

void solve() {
    int n, d; cin >> n >> d;
    vector<vector<int>> adj(n + 1);
    vector<pair<int,int>> edges;
    for (int i = 0; i < n - 1; i++) {
        int a, b; cin >> a >> b;
        adj[a].push_back(b);
        adj[b].push_back(a);
        edges.push_back({a, b});
    }

    LCA lifter(n, adj, 1);

    vector<vector<int>> children(n + 1);
    auto makeChildren = [&](auto&& self, int node, int parent) -> void {
        for (auto adjN : adj[node]) {
            if (adjN == parent) continue;
            children[node].push_back(adjN);
            self(self, adjN, node);
        }
    };
    makeChildren(makeChildren, 1, 0);

    ll out = 0;

    // first, for every node, run a dfs that scores A-B-C
    auto chainScore = [&](int root) -> void {
        auto innerDfs = [&](auto&& self, int curNode, int distFromRoot) -> void {
            if (distFromRoot == d - 1) {
                int betweenOptions = distFromRoot - 1;
                out += betweenOptions;
            }
            for (auto child : children[curNode]) {
                self(self, child, distFromRoot + 1);
            }
        };
        innerDfs(innerDfs, root, 0);
    };

    for (int node = 1; node <= n; node++) {
        chainScore(node);
    }


    // now we solve for simple paths that are not chains, any two node, we find their LCA, we can pick a third node along it
    // but skip if the LCA happens to be one of those two nodes (that is just a chain)
    ll resFromPaths = 0;
    for (int node1 = 1; node1 <= n; node1++) {
        for (int node2 = node1 + 1; node2 <= n; node2++) {
            int lca = lifter.lca(node1, node2);
            if (lca == node1 || lca == node2) continue;
            int pathDist = lifter.pathDist(node1, node2);
            if (pathDist != d - 1) continue;
            int options = pathDist - 1;
            resFromPaths += options;
        }
    }

    out += resFromPaths;

    // now we solve for the case where one child node contains a pair, the other child node contains a single, using small to large

    struct Packet {
        unordered_map<int,int> single; // single[dist] = the # of single nodes in my subtree, with that many nodes in that path
        int offset = 0; // our virtual shifting
        unordered_map<int, ll> doubles; // pair[dist] is the # of safe pairs in this subtree with that many nodes in a pair, to reach a root

        void shift() {
            offset++;
        }

        void addSingle(int trueDist, int cnt = 1) {
            single[trueDist - offset] += cnt;
        }

        int getSingle(int trueDist) {
            auto it = single.find(trueDist - offset);
            if (it == single.end()) return 0;
            return it->second;
        }

        int getDouble(int truePairDist) {
            auto it = doubles.find(truePairDist - offset);
            if (it == doubles.end()) return 0;
            return it->second;
        }

        void addDouble(int trueDist, int cnt = 1) {
            doubles[trueDist - offset] += cnt;
        }

        vector<pair<int,int>> singleEntries() {
            vector<pair<int,int>> res;
            res.reserve(single.size());
            for (auto& [storedDist, cnt] : single) {
                res.push_back({storedDist + offset, cnt});
            }
            return res;
        }
        
        vector<pair<int,ll>> doubleEntries() {
            vector<pair<int,ll>> res;
            res.reserve(doubles.size());
            for (auto& [storedDist, cnt] : doubles) {
                res.push_back({storedDist + offset, cnt});
            }
            return res;
        }
    };

    ll type3 = 0; // the # of answers for this third variant, where there is some node which is the LCA of all 3 nodes

    auto dfs = [&](auto&& self, int node) -> Packet {
        if (children[node].size() == 0) {
            Packet p;
            p.addSingle(1);
            return p;
        }
        vector<Packet> childs;
        for (auto child : children[node]) {
            auto packet = self(self, child);
            childs.push_back(packet);
        }
        sort(childs.begin(), childs.end(), [](const Packet& a, const Packet& b) {
            return a.single.size() + a.doubles.size() > b.single.size() + b.doubles.size();
        });

        auto& heavy = childs[0];

        type3 += heavy.getDouble(d - 1); // any safe pair inside a child can use the root as a value

        for (int i = 1; i < childs.size(); i++) {
            auto& light = childs[i];
            for (auto& [lightNodeCnt, frq] : light.singleEntries()) {
                // for every single node in here, we can pair it with a previous safe pair
                int req = d - lightNodeCnt - 1;
                int prevSafe = heavy.getDouble(req);
                type3 += frq * prevSafe;
            }
            // every double can pair with a previous single
            for (auto& [lightNodeCnt, frq] : light.doubleEntries()) {
                int req = d - lightNodeCnt - 1;
                int prevSafe = heavy.getSingle(req);
                type3 += frq * prevSafe;
            }

            // any double can also connect with root
            type3 += light.getDouble(d - 1);

            // fold in new doubles that get formed via one single
            for (auto& [k, v] : light.singleEntries()) {
                for (auto& [kheavy, vheavy] : heavy.singleEntries()) {
                    int ndist = k + kheavy;
                    int nfrq = v * vheavy;
                    heavy.addDouble(ndist, nfrq);
                }
            }

            // fold in
            for (auto& [k, v] : light.singleEntries()) {
                heavy.addSingle(k, v);
            }
            // every double can pair with a previous single
            for (auto& [k, v] : light.doubleEntries()) {
                heavy.addDouble(k, v);
            }
        }
        heavy.shift();
        heavy.addSingle(1);
        return heavy;
    };

    dfs(dfs, 1);

    out += type3;

    cout << out << '\n';

}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int t; cin >> t;
    while (t--) {
        solve();
    }
}