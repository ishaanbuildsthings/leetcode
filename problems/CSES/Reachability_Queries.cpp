#include <bits/stdc++.h>
using namespace std;
using ll = long long;

const int MAX_N = 50000;

#include <bits/stdc++.h>
using namespace std;

// Template by ishaanbuildsthings (github.com/ishaanbuildsthings)
//
// adj is a vector of out-neighbor lists, indexed by node id in [0, n), directed.
// Every index is a real node — convert 1-indexed input before calling.
//   adj = {{1}, {2}, {0}, {2}}         // edges 0->1, 1->2, 2->0, 3->2
// Scc scc = buildScc(adj);                // O(n + m) time and space
//
// A component is a maximal group of nodes that can all reach each other. Here
// {0,1,2} is one (the cycle 0->1->2->0) and {3} is the other.
//
// scc.numComponents      int, the number of components C
//   2
//
// scc.nodeToComponentId  vector<int>, indexed by node id -> its component id, O(1)
//   {0, 0, 0, 1}                       // nodes 0,1,2 -> comp 0;  node 3 -> comp 1
//
// scc.componentNodes     vector<vector<int>>, indexed by component id -> its nodes, O(1)
//   {{0, 1, 2}, {3}}
//
// scc.componentAdj       vector<vector<int>>, indexed by component id -> out-neighbor
//                        component ids. Always acyclic. Intra-component edges dropped;
//                        duplicates kept when several edges cross the same pair. O(1)
//   {{}, {0}}                          // original edge 3->2 became comp 1 -> comp 0
//
// Component ids come out in reverse topological order: every edge compA -> compB has
// compA > compB, so looping ids 0..C-1 visits a component only after all it can reach.
struct Scc {
    vector<int> nodeToComponentId;
    vector<vector<int>> componentNodes;
    vector<vector<int>> componentAdj;
    int numComponents;
};

Scc buildScc(const vector<vector<int>>& adj) {
    int n = adj.size();
    vector<int> num(n, 0), low(n, 0), nodeToComponentId(n, -1), stk;
    vector<char> onStk(n, 0);
    vector<pair<int, int>> callStack;
    callStack.reserve(n);
    int timer = 0, numComponents = 0;

    for (int start = 0; start < n; start++) {
        if (num[start]) continue;
        num[start] = low[start] = ++timer;
        stk.push_back(start);
        onStk[start] = 1;
        callStack.push_back({start, 0});
        while (!callStack.empty()) {
            auto& [node1, ei] = callStack.back();
            if (ei < (int)adj[node1].size()) {
                int node2 = adj[node1][ei++];
                if (!num[node2]) {
                    num[node2] = low[node2] = ++timer;
                    stk.push_back(node2);
                    onStk[node2] = 1;
                    callStack.push_back({node2, 0});
                } else if (onStk[node2]) {
                    low[node1] = min(low[node1], num[node2]);
                }
            } else {
                if (low[node1] == num[node1]) {
                    while (true) {
                        int node3 = stk.back();
                        stk.pop_back();
                        onStk[node3] = 0;
                        nodeToComponentId[node3] = numComponents;
                        if (node3 == node1) break;
                    }
                    numComponents++;
                }
                int finished = node1;
                callStack.pop_back();
                if (!callStack.empty()) {
                    int parent = callStack.back().first;
                    low[parent] = min(low[parent], low[finished]);
                }
            }
        }
    }

    vector<vector<int>> componentNodes(numComponents);
    vector<vector<int>> componentAdj(numComponents);
    for (int node1 = 0; node1 < n; node1++) {
        componentNodes[nodeToComponentId[node1]].push_back(node1);
        for (int node2 : adj[node1]) {
            if (nodeToComponentId[node1] != nodeToComponentId[node2]) {
                componentAdj[nodeToComponentId[node1]].push_back(nodeToComponentId[node2]);
            }
        }
    }
    return {nodeToComponentId, componentNodes, componentAdj, numComponents};
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m, q; cin >> n >> m >> q;
    vector<vector<int>> adj(n);
    for (int i = 0; i < m; i++) {
        int a, b; cin >> a >> b; a--; b--;
        adj[a].push_back(b);
    }

    Scc scc = buildScc(adj);
    int numComponents = scc.numComponents;

    auto nodeToCompId = scc.nodeToComponentId;

    vector<bitset<MAX_N>> memo(numComponents);
    vector<char> done(numComponents, 0);
    for (int node = 0; node < n; node++) {
        int comp = nodeToCompId[node];
        memo[comp].set(node);
    }

    auto reach = [&](auto&& self, int comp) -> bitset<MAX_N>& {
        if (done[comp]) {
            return memo[comp];
        }
        auto& here = memo[comp];
        for (auto adjN : scc.componentAdj[comp]) {
            auto& adjBs = self(self, adjN);
            here |= adjBs;
        }
        done[comp] = 1;
        return memo[comp];
    };
    for (int comp = 0; comp < numComponents; comp++) reach(reach, comp);

    for (int i = 0; i < q; i++) {
        int a, b; cin >> a >> b; a--; b--;
        auto& bs = memo[nodeToCompId[a]];
        if (bs[b]) {
            cout << "YES" << '\n';
        } else {
            cout << "NO" << '\n';
        }
    }
}