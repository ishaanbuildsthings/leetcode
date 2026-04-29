#include <bits/stdc++.h>
using namespace std;

struct HLD {
    int n; // number of nodes
    vector<vector<int>> adj; // adj[node] -> list of adjacent nodes
    vector<int> par; // par[node] -> parent, or an invalid value if root
    vector<int> depth; // depth[node] is depth, depth of root is 0
    vector<int> sz; // sz[node] is # of nodes in that subtree
    vector<int> heavy; // heavy[node] is the heavy child, or unset if a leaf
    vector<int> head; // head[node] is the topmost node in the chain for that node
    vector<int> pos; // index of node in the array
    int timer = 0;
    int segN; // power of 2 >= n, leaves live at [segN, 2*segN)
    vector<int> seg; // iterative seg tree, size 2 * segN, leaf i = seg[segN + i]

    int lg;
    vector<vector<int>> lift; // lift[node][power] is the 2^power ancestor, I use this for path queries to find the LCA, but we could avoid with some dual-walking technique that felt inintuitive

    static int roundUpPow2(int x) {
        int p = 1;
        while (p < x) p <<= 1;
        return p;
    }

    // first at compile time the compiler figures out how much space is needed for each of the above variables
    // nothing actually exists at compile time, the compiler just knows how much space the struct is going to take
    // but at runtime say during HLD hld(5):
    // -stack space gets reserved based on the variables in the struct
    // -constructor gets called, initializer list runs, all of the space for the above gets allocated and set up
    HLD(int n) :
        n(n),
        adj(n),
        par(n, -1), // we are going to stay 0-indexed internally for everything, so if we add edges we should add (a-1, b-1) if we need to convert
        depth(n, 0),
        sz(n, 1),
        heavy(n, -1),
        head(n),
        pos(n),
        segN(roundUpPow2(max(n, 1))),
        seg(2 * roundUpPow2(max(n, 1)), 0),
        lg(max(1, int(ceil(log2(n))))),
        lift(n, vector<int>(lg, -1))
    {}

    void addEdge(int a, int b) {
        adj[a].push_back(b);
        adj[b].push_back(a);
    }

    // initialize sizes, parents, etc
    void _dfsInit(int node, int parent, int currDepth) {
        par[node] = parent;
        depth[node] = currDepth;
        int maxChildSize = 0;
        int currSize = 1;
        for (auto adjN : adj[node]) {
            if (adjN == parent) continue;
            _dfsInit(adjN, node, currDepth + 1);
            if (sz[adjN] > maxChildSize) {
                maxChildSize = sz[adjN];
                heavy[node] = adjN;
            }
            currSize += sz[adjN];
        }
        sz[node] = currSize;
    }

    void _dfsDecompose(int node, int chainHead) {
        head[node] = chainHead;
        pos[node] = timer++;
        // always visit heavy first, keeps chains contiguous in our seg tree
        if (heavy[node] != -1) {
            _dfsDecompose(heavy[node], chainHead);
        }
        for (auto adjN : adj[node]) {
            if (adjN == par[node]) continue;
            if (adjN == heavy[node]) continue;
            _dfsDecompose(adjN, adjN);
        }
    }

    void _liftBuild() {
        for (int node = 0; node < n; node++) {
            lift[node][0] = par[node];
        }
        for (int power = 1; power < lg; power++) {
            for (int node = 0; node < n; node++) {
                int half = lift[node][power - 1];
                if (half == -1) {
                    lift[node][power] = -1;
                } else {
                    lift[node][power] = lift[half][power - 1];
                }
            }
        }
    }

    // given a list of values for each node, build things
    void build(const vector<int>& vals) {
        _dfsInit(0, -1, 0); // use 0-indexing internally, run this which sets up our basic arrays like par[node] sz[node] etc
        _dfsDecompose(0, 0); // generate the head[node] and also get the dfs ordering
        // the dfs ordering (we always visit heavy first) makes it so in our array representing the tree values, each heavy chain is some contiguous region of that array
        // so when we use it in the seg tree, we can do a subarray query

        // populate seg tree leaves directly at their linearized positions, then build internal nodes bottom-up
        for (int node = 0; node < n; node++) {
            seg[segN + pos[node]] = vals[node];
        }
        for (int i = segN - 1; i >= 1; i--) {
            seg[i] = max(seg[2 * i], seg[2 * i + 1]);
        }

        _liftBuild();
    }

    // iterative point update: write the leaf, walk up recomputing parents
    void pointUpdate(int idx, int newVal) {
        // basically what is happening here is we want to update some node in a tree
        // we had taken that tree, produces an array `linear` so every heavy chain is a contiguous region of that array (allowing all heavy chain queries)
        // and we remembered each nodes position in that array, even though linear went away after we built the seg tree
        // this feels confusing but actually makes sense, we know how to locate any position in that linear array, inside our seg tree, because of the 2*i and 2*i + 1 rule
        // so we take our node, get its position in the original array, and pass that to point update, it can relocate that index in the seg tree and handle things
        int p = pos[idx] + segN;
        seg[p] = newVal;
        for (p >>= 1; p > 0; p >>= 1) {
            seg[p] = max(seg[2 * p], seg[2 * p + 1]);
        }
    }

    // iterative range max over inclusive [ql, qr]
    // returns 0 for empty/no-overlap (safe since all values >= 1 in this problem)
    int _rangeMax(int ql, int qr) {
        int res = 0;
        for (ql += segN, qr += segN + 1; ql < qr; ql >>= 1, qr >>= 1) {
            if (ql & 1) res = max(res, seg[ql++]);
            if (qr & 1) res = max(res, seg[--qr]);
        }
        return res;
    }


    int kthAncestor(int node, int k) {
        int curr = node;
        for (int b = 0; b < lg; b++) {
            if (k & (1 << b)) {
                curr = lift[curr][b];
                if (curr == -1) return -1;
            }
            
        }
        return curr;
    }

    int lca(int a, int b) {
        if (depth[a] < depth[b]) swap(a, b);
        int diff = depth[a] - depth[b];
        a = kthAncestor(a, diff);
        if (a == b) return a;
        for (int power = lg - 1; power >= 0; power--) {
            int upA = lift[a][power];
            int upB = lift[b][power];
            if (upA == upB) continue;
            a = upA;
            b = upB;
        }
        return lift[a][0];
    }

    // gets the path query from node up to the excluded ancestor, not including it
    int upChainExclusive(int node, int excludedAncestor) {
        int res = INT_MIN;
        while (head[node] != head[excludedAncestor]) {
            int chainVal = _rangeMax(pos[head[node]], pos[node]);
            res = max(res, chainVal);
            node = par[head[node]];
        }
        if (node != excludedAncestor) {
            // now we are on the same chain as our ancestor
            // we could use a clever trick that pos[excludedAncestor]+1 is the node right below it
            // or we could find the depth of the excluded ancestor, add 1 to it to get the depth of the node below it, use kth ancestor to find that node, then _rangeMax on the poses of our node to that node we found
            int lastVal = _rangeMax(pos[excludedAncestor] + 1, pos[node]);
            res = max(res, lastVal);
        }
        return res;
    }
    // int pathQuery(int a, int b) {
    //     int res = INT_MIN;
    //     while (head[a] != head[b]) {
    //         if (depth[head[a]] < depth[head[b]]) swap(a, b);
    //         res = max(res, _rangeMax(pos[head[a]], pos[a]));
    //         a = par[head[a]];
    //     }
    //     if (depth[a] > depth[b]) swap(a, b);
    //     res = max(res, _rangeMax(pos[a], pos[b]));
    //     return res;
    // }
    int pathQuery(int a, int b) {
        int lcaNode = lca(a, b);
        int lcaVal = _rangeMax(pos[lcaNode], pos[lcaNode]);
        int path1 = upChainExclusive(a, lcaNode);
        int path2 = upChainExclusive(b, lcaNode);
        return max({path1, path2, lcaVal});
    }
};

int main() {
    int n, q;
    scanf("%d %d", &n, &q);
    
    vector<int> A(n);
    for (int i = 0; i < n; i++) scanf("%d", &A[i]);
    
    HLD hld(n);
    for (int i = 0; i < n - 1; i++) {
        int a, b;
        scanf("%d %d", &a, &b);
        hld.addEdge(a - 1, b - 1);
    }
    hld.build(A);
    for (int i = 0; i < q; i++) {
        int qtype;
        scanf("%d", &qtype);
        if (qtype == 1) {
            int s; int x;
            scanf("%d %d", &s, &x);
            hld.pointUpdate(s - 1, x);
        } else {
            int a, b;
            scanf("%d %d", &a, &b);
            printf("%d ", hld.pathQuery(a - 1, b - 1));
        }
    }
}