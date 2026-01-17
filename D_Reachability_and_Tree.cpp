#include <bits/stdc++.h>
using namespace std;

int main() {
    cin.tie(nullptr);
    ios::sync_with_stdio(false);
    int t; cin >> t;
    while (t--) {
        // cout << "==========" << endl;


        int n; cin >> n;
        vector<vector<int>> g(n + 1);
        for (int i = 0; i < n - 1; i++) {
            int a, b; cin >> a >> b;
            g[a].push_back(b);
            g[b].push_back(a);
        }

        // If a node has 2 adjacent nodes, at least one with only 1 adj, make the other one the root
        int root = -1;
        int middle = -1;
        for (int node = 1; node <= n; node++) {
            if (g[node].size() != 2) continue;
            int adj1 = g[node][0];
            int adj2 = g[node][1];
            root = adj2;
            middle = node;
            break;
            // if (g[adj1].size() == 1) {
            //     root = adj2;
            //     middle = node;
            //     break;
            // } else if (g[adj2].size() == 1) {
            //     root = adj1;
            //     middle = node;
            //     break;
            // }
        }

        if (root == -1) {
            cout << "NO" << endl;
            continue;
        }

        // we are going down from the root

        cout << "YES" << endl;

        // cout << "root is:" << root << endl;
        // cout << "middle is:" << middle << endl;

        auto dfs = [&](auto&& self, int node, int parent, bool down) -> void {
            // cout << "dfs called on node:" << node << endl;
            for (auto adj : g[node]) {
                if (adj == parent) {
                    continue;
                }
                if (node == middle) {
                    cout << node << " " << adj << endl;
                    self(self, adj, node, false);
                } else {
                    if (down) {
                        cout << node << " " << adj << endl;
                    } else {
                        cout << adj << " " << node << endl;
                    }
                    self(self, adj, node, !down);
                }

                
            }
        };
        dfs(dfs, root, -1, true);



    }
}

// 1->2->4
// v
// 3<5

// 4>5
// ^
// 1->2
// v
// 3


// 2>1>3
// v
// 4


// A<>B<>c
//    |
//    D


// A>B<C
//   v
//   d