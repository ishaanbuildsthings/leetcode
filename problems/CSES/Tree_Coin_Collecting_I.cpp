#include <bits/stdc++.h>
using namespace std;

struct Lift {
    int root;
    int n;
    vector<vector<int>> adj;
    vector<long long> val;
    int LOG;
    long long INF;

    vector<int> depth;
    vector<vector<int>> up;
    vector<vector<long long>> mn;

    Lift(int root_, int n_, const vector<vector<int>>& adj_, const vector<long long>& val_)
        : root(root_), n(n_), adj(adj_), val(val_) {

        LOG = max(1, 32 - __builtin_clz((unsigned)n));
        INF = (long long)4e18;

        depth.assign(n, 0);
        up.assign(LOG, vector<int>(n, 0));
        mn.assign(LOG, vector<long long>(n, INF));

        vector<int> parent(n, 0);
        parent[root] = root;

        vector<int> st;
        st.push_back(root);
        vector<int> order;
        order.reserve(n);

        while (!st.empty()) {
            int v = st.back();
            st.pop_back();
            order.push_back(v);
            for (int to : adj[v]) {
                if (to == parent[v]) continue;
                parent[to] = v;
                depth[to] = depth[v] + 1;
                st.push_back(to);
            }
        }

        for (int v = 0; v < n; v++) {
            int p = parent[v];
            up[0][v] = p;
            if (v == root) {
                mn[0][v] = val[v];
            } else {
                long long a = val[v];
                long long b = val[p];
                mn[0][v] = (a < b ? a : b);
            }
        }

        for (int k = 1; k < LOG; k++) {
            for (int v = 0; v < n; v++) {
                int mid = up[k - 1][v];
                up[k][v] = up[k - 1][mid];
                long long a = mn[k - 1][v];
                long long b = mn[k - 1][mid];
                mn[k][v] = (a < b ? a : b);
            }
        }
    }

    int lca(int a, int b) const {
        if (depth[a] < depth[b]) swap(a, b);
        int diff = depth[a] - depth[b];
        for (int k = 0; k < LOG; k++) {
            if ((diff >> k) & 1) a = up[k][a];
        }
        if (a == b) return a;
        for (int k = LOG - 1; k >= 0; k--) {
            if (up[k][a] != up[k][b]) {
                a = up[k][a];
                b = up[k][b];
            }
        }
        return up[0][a];
    }

    long long dist(int a, int b) const {
        int c = lca(a, b);
        return (long long)depth[a] + (long long)depth[b] - 2LL * (long long)depth[c];
    }

    long long mn_on_path(int a, int b) const {
        long long res = INF;
        if (depth[a] < depth[b]) swap(a, b);

        int diff = depth[a] - depth[b];
        for (int k = 0; k < LOG; k++) {
            if ((diff >> k) & 1) {
                long long v = mn[k][a];
                res = (v < res ? v : res);
                a = up[k][a];
            }
        }

        if (a == b) {
            long long v = val[a];
            res = (v < res ? v : res);
            return res;
        }

        for (int k = LOG - 1; k >= 0; k--) {
            if (up[k][a] != up[k][b]) {
                long long va = mn[k][a];
                long long vb = mn[k][b];
                res = (va < res ? va : res);
                res = (vb < res ? vb : res);
                a = up[k][a];
                b = up[k][b];
            }
        }

        long long va = mn[0][a];
        long long vb = mn[0][b];
        res = (va < res ? va : res);
        res = (vb < res ? vb : res);
        return res;
    }
};

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n, qs;
    cin >> n >> qs;

    vector<int> coins(n);
    for (int i = 0; i < n; i++) cin >> coins[i];

    vector<vector<int>> g(n);
    for (int i = 0; i < n - 1; i++) {
        int a, b;
        cin >> a >> b;
        a--; b--;
        g[a].push_back(b);
        g[b].push_back(a);
    }

    deque<int> q;
    vector<char> seen(n, 0);
    for (int i = 0; i < n; i++) {
        if (coins[i]) {
            q.push_back(i);
            seen[i] = 1;
        }
    }

    vector<long long> minDist(n, -1);
    long long steps = 0;
    while (!q.empty()) {
        int length = (int)q.size();
        for (int i = 0; i < length; i++) {
            int node = q.front();
            q.pop_front();
            minDist[node] = steps;
            for (int adj : g[node]) {
                if (seen[adj]) continue;
                seen[adj] = 1;
                q.push_back(adj);
            }
        }
        steps++;
    }

    Lift jump(0, n, g, minDist);

    while (qs--) {
        int a, b;
        cin >> a >> b;
        a--; b--;
        long long small = jump.mn_on_path(a, b);
        cout << jump.dist(a, b) + 2LL * small << "\n";
    }

    return 0;
}


// jump tables python (TLE)
// class Lift:
//     def __init__(self, root, n, adj, val):
//         self.root = root
//         self.n = n
//         self.adj = adj
//         self.val = val
//         self.LOG = max(1, n.bit_length())
//         self.INF = 10**18

//         self.depth = [0] * n
//         self.up = [[0] * n for _ in range(self.LOG)]
//         self.mn = [[self.INF] * n for _ in range(self.LOG)]

//         parent = [0] * n
//         parent[root] = root

//         st = [root]
//         order = []
//         while st:
//             v = st.pop()
//             order.append(v)
//             for to in adj[v]:
//                 if to == parent[v]:
//                     continue
//                 parent[to] = v
//                 self.depth[to] = self.depth[v] + 1
//                 st.append(to)

//         for v in range(n):
//             p = parent[v]
//             self.up[0][v] = p
//             if v == root:
//                 self.mn[0][v] = val[v]
//             else:
//                 a = val[v]
//                 b = val[p]
//                 self.mn[0][v] = a if a < b else b

//         for k in range(1, self.LOG):
//             upk = self.up[k]
//             upkm1 = self.up[k - 1]
//             mnk = self.mn[k]
//             mnkm1 = self.mn[k - 1]
//             for v in range(n):
//                 mid = upkm1[v]
//                 upk[v] = upkm1[mid]
//                 a = mnkm1[v]
//                 b = mnkm1[mid]
//                 mnk[v] = a if a < b else b

//     def lca(self, a, b):
//         if self.depth[a] < self.depth[b]:
//             a, b = b, a
//         diff = self.depth[a] - self.depth[b]
//         for k in range(self.LOG):
//             if (diff >> k) & 1:
//                 a = self.up[k][a]
//         if a == b:
//             return a
//         for k in range(self.LOG - 1, -1, -1):
//             if self.up[k][a] != self.up[k][b]:
//                 a = self.up[k][a]
//                 b = self.up[k][b]
//         return self.up[0][a]

//     def dist(self, a, b):
//         c = self.lca(a, b)
//         return self.depth[a] + self.depth[b] - 2 * self.depth[c]

//     def mn_on_path(self, a, b):
//         res = self.INF
//         if self.depth[a] < self.depth[b]:
//             a, b = b, a

//         diff = self.depth[a] - self.depth[b]
//         for k in range(self.LOG):
//             if (diff >> k) & 1:
//                 v = self.mn[k][a]
//                 res = v if v < res else res
//                 a = self.up[k][a]

//         if a == b:
//             v = self.val[a]
//             res = v if v < res else res
//             return res

//         for k in range(self.LOG - 1, -1, -1):
//             if self.up[k][a] != self.up[k][b]:
//                 va = self.mn[k][a]
//                 vb = self.mn[k][b]
//                 res = va if va < res else res
//                 res = vb if vb < res else res
//                 a = self.up[k][a]
//                 b = self.up[k][b]

//         va = self.mn[0][a]
//         vb = self.mn[0][b]
//         res = va if va < res else res
//         res = vb if vb < res else res
//         return res

// import collections

// n, qs = map(int, input().split())
// coins = list(map(int, input().split()))
// g = [[] for _ in range(n)]
// for _ in range(n - 1):
//     a, b = map(int, input().split())
//     a -= 1
//     b -= 1
//     g[a].append(b)
//     g[b].append(a)

// q = collections.deque([i for i in range(n) if coins[i]])
// seen = [True if coins[i] else False for i in range(n)]
// minDist = [-1] * n
// steps = 0
// while q:
//     length = len(q)
//     for _ in range(length):
//         node = q.popleft()
//         minDist[node] = steps
//         for adj in g[node]:
//             if seen[adj]:
//                 continue
//             seen[adj] = True
//             q.append(adj)
//     steps += 1

// jump = Lift(0, n, g, minDist)
                
// for _ in range(qs):
//     a, b = map(int, input().split())
//     a -= 1
//     b -= 1
//     small = jump.mn_on_path(a, b)
//     print(jump.dist(a, b) + 2 * small)