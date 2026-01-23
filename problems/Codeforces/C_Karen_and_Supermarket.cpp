// #include <bits/stdc++.h>
// using namespace std;

// int main() {
//     ios::sync_with_stdio(false);
//     cin.tie(nullptr);
//     int n; cin >> n;
//     long long b; cin >> b;

//     vector<long long> costs;
//     vector<long long> discounts; // discounted cost
//     costs.push_back(0);
//     discounts.push_back(0); // 1-indexed

//     vector<vector<int>> g(n + 1);
//     for (int i = 0; i < n; i++) {
//         int c, d; cin >> c >> d;
//         costs.push_back(c);
//         discounts.push_back(c - d);
//         if (i != 0) {
//             int adj; cin >> adj;
//             g[i + 1].push_back(adj);
//             g[adj].push_back(i + 1);
//         }
//     }

//     vector<vector<int>> children(n + 1);
//     // vector<int> sizes(n + 1);
//     // vector<int> heavyChild(n + 1);
//     auto dfs = [&](auto&& self, int node, int parent) -> void {
//         // sizes[node] = 1;
//         // int heavy = 0;
//         for (auto adj : g[node]) {
//             if (adj == parent) continue;
//             children[node].push_back(adj);
//             self(self, adj, node);
//             // sizes[node] += sizes[adj];
//             // if (sizes[adj] > heavy) {
//                 // heavy = sizes[adj];
//                 // heavyChild[node] = adj;
//             // }
//         }
//     };
//     dfs(dfs, 1, 0);
    
//     // // PRINTING
//     // cout << "Costs: " << endl;
//     // for (auto c : costs) cout << c << " ";
//     // cout << endl;

//     // cout << "Discounts:" << endl;
//     // for (auto d : discounts) cout << d << " ";
//     // cout << endl;

//     // cout << "Children:" << endl;
//     // for (int node = 1; node <= n; node++) {
//     //     cout << "node: " << node << endl;
//     //     for (auto child : children[node]) cout << child << " ";
//     //     cout << endl;
//     // }

//     // cout << "Sizes:" << endl;
//     // for (int node = 1; node <= n; node++) {
//     //     cout << node << ": " << sizes[node] << endl;
//     // }

//     // cout << "Heavy child:" << endl;
//     // for (int node = 1; node <= n; node++) {
//     //     cout << node << ": " << heavyChild[node] << endl;
//     // }

//     long long INF = 1000000000000000;
//     vector<vector<long long>> coupon(n + 1, vector<long long>(n + 1, INF)); // coupon[node][attained] is the minimum we spend in the subtree of node if we coupon the root
//     vector<vector<long long>> noCoupon(n + 1, vector<long long>(n + 1, INF)); // noCoupon[node][attained] is the minimum we need to spend in the subtree of node if we do not coupon node
//     for (int node = 1; node <= n; node++) {
//         noCoupon[node][0] = 0;
//     }

//     auto merge = [&](vector<long long>& left, vector<long long>& right) -> vector<long long> {
//         vector<long long> result(n + 1, INF);
//         for (int takeLeft = 0; takeLeft <= n; takeLeft++) {
//             if (left[takeLeft] == INF) continue; // prevent overflow
//             for (int takeRight = 0; takeRight <= n; takeRight++) {
//                 if (right[takeRight] == INF) continue; // prevent overflow
//                 int tot = takeLeft + takeRight;
//                 if (tot > n) break;
//                 result[tot] = min({left[takeLeft] + right[takeRight], result[tot]});
//             }
//         }
//         return result;
//     };

//     auto dfs2 = [&](auto&& self, int node) -> void {
//         // base case, at a leaf
//         if (!children[node].size()) {
//             coupon[node][1] = discounts[node];
//             noCoupon[node][1] = costs[node];
//             return;
//         }

//         // resolve children first
//         for (auto child : children[node]) {
//             self(self, child);
//         }

//         vector<long long> oldCoupon(n + 1, INF);
//         oldCoupon[1] = discounts[node];
//         vector<long long> oldNoCoupon(n + 1, INF);
//         oldNoCoupon[0] = 0;
//         oldNoCoupon[1] = costs[node];

//         for (auto child : children[node]) {
//             // With no coupon at node, we can only use children with no coupon
//             auto& childNoCoupon = noCoupon[child];
//             auto newNoCoupon = merge(oldNoCoupon, childNoCoupon);
//             oldNoCoupon = move(newNoCoupon);

//             // If we coupon node, we could coupon or not coupon children
//             vector<long long> bestChild(n + 1, INF);
//             for (int i = 0; i <= n; i++) {
//                 bestChild[i] = min(coupon[child][i], noCoupon[child][i]);
//             }
//             auto newCoupon = merge(oldCoupon, bestChild);
//             oldCoupon = move(newCoupon);
//         }

//         noCoupon[node] = move(oldNoCoupon);
//         coupon[node] = move(oldCoupon);
//     };

//     dfs2(dfs2, 1);

//     int res = 0;
//     for (int obtained = 0; obtained <= n; obtained++) {
//         if (coupon[1][obtained] <= b) {
//             res = obtained;
//         }
//         if (noCoupon[1][obtained] <= b) {
//             res = obtained;
//         }
//     }
//     cout << res;

// }

#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n; cin >> n;
    long long b; cin >> b;

    vector<long long> costs;
    vector<long long> discounts; // discounted cost
    costs.push_back(0);
    discounts.push_back(0); // 1-indexed

    vector<vector<int>> g(n + 1);
    for (int i = 0; i < n; i++) {
        int c, d; cin >> c >> d;
        costs.push_back(c);
        discounts.push_back(c - d);
        if (i != 0) {
            int adj; cin >> adj;
            g[i + 1].push_back(adj);
            g[adj].push_back(i + 1);
        }
    }

    vector<vector<int>> children(n + 1);
    vector<int> subtreeSize(n + 1, 0);

    auto dfs = [&](auto&& self, int node, int parent) -> void {
        subtreeSize[node] = 1;
        for (auto adj : g[node]) {
            if (adj == parent) continue;
            children[node].push_back(adj);
            self(self, adj, node);
            subtreeSize[node] += subtreeSize[adj];
        }
    };
    dfs(dfs, 1, 0);

    long long INF = 1000000000000000;
    vector<vector<long long>> coupon(n + 1, vector<long long>(n + 1, INF)); // coupon[node][attained] is the minimum we spend in the subtree of node if we coupon the root
    vector<vector<long long>> noCoupon(n + 1, vector<long long>(n + 1, INF)); // noCoupon[node][attained] is the minimum we need to spend in the subtree of node if we do not coupon node
    for (int node = 1; node <= n; node++) {
        noCoupon[node][0] = 0;
    }

    auto merge = [&](vector<long long>& left, vector<long long>& right, int leftSize, int rightSize) -> vector<long long> {
        vector<long long> result(n + 1, INF);
        int maxTot = min(n, leftSize + rightSize);
        for (int takeLeft = 0; takeLeft <= leftSize; takeLeft++) {
            if (left[takeLeft] == INF) continue; // prevent overflow
            for (int takeRight = 0; takeRight <= rightSize; takeRight++) {
                if (right[takeRight] == INF) continue; // prevent overflow
                int tot = takeLeft + takeRight;
                if (tot > maxTot) break;
                result[tot] = min(result[tot], left[takeLeft] + right[takeRight]);
            }
        }
        return result;
    };

    auto dfs2 = [&](auto&& self, int node) -> void {
        // base case, at a leaf
        if (!children[node].size()) {
            coupon[node][1] = discounts[node];
            noCoupon[node][1] = costs[node];
            return;
        }

        // resolve children first
        for (auto child : children[node]) {
            self(self, child);
        }

        vector<long long> oldCoupon(n + 1, INF);
        oldCoupon[1] = discounts[node];
        int oldCouponSize = 1; // max attainable items so far in oldCoupon

        vector<long long> oldNoCoupon(n + 1, INF);
        oldNoCoupon[0] = 0;
        oldNoCoupon[1] = costs[node];
        int oldNoSize = 1; // max attainable items so far in oldNoCoupon

        for (auto child : children[node]) {
            int childSize = subtreeSize[child];

            // With no coupon at node, we can only use children with no coupon
            auto& childNoCoupon = noCoupon[child];
            auto newNoCoupon = merge(oldNoCoupon, childNoCoupon, oldNoSize, childSize);
            oldNoCoupon = move(newNoCoupon);
            oldNoSize = min(n, oldNoSize + childSize);

            // If we coupon node, we could coupon or not coupon children
            vector<long long> bestChild(n + 1, INF);
            for (int i = 0; i <= childSize; i++) {
                bestChild[i] = min(coupon[child][i], noCoupon[child][i]);
            }
            auto newCoupon = merge(oldCoupon, bestChild, oldCouponSize, childSize);
            oldCoupon = move(newCoupon);
            oldCouponSize = min(n, oldCouponSize + childSize);
        }

        noCoupon[node] = move(oldNoCoupon);
        coupon[node] = move(oldCoupon);
    };

    dfs2(dfs2, 1);

    int res = 0;
    for (int obtained = 0; obtained <= n; obtained++) {
        if (coupon[1][obtained] <= b) {
            res = obtained;
        }
        if (noCoupon[1][obtained] <= b) {
            res = obtained;
        }
    }
    cout << res;
}
