// SOLUTION 1 WITH BINARY LIFTING, O(n^2 * logn * n/W)
template<typename T, typename V, typename BaseFn, typename MergeFn>
struct Lift {
    int n, LOG;
    vector<int> dep;
    vector<vector<int>> up;
    vector<vector<optional<T>>> upData;
    BaseFn baseFn;
    MergeFn mergeFn;
    vector<V> vals;

    optional<T> mergeOpt(optional<T> a, optional<T> b) {
        if (!a) return b;
        if (!b) return a;
        return mergeFn(*a, *b);
    }

    Lift(int root, vector<pair<int,int>>& edges, vector<V>& vals,
         BaseFn baseFn, MergeFn mergeFn)
        : vals(vals), baseFn(baseFn), mergeFn(mergeFn) {

        n = edges.size() + 1;
        LOG = max(1, __lg(n) + 1);
        dep.assign(n, 0);
        up.assign(LOG, vector<int>(n));
        upData.assign(LOG, vector<optional<T>>(n, nullopt));

        vector<vector<int>> g(n);
        for (auto [u, v] : edges) {
            g[u].push_back(v);
            g[v].push_back(u);
        }

        vector<bool> vis(n, false);
        queue<int> q;
        q.push(root);
        vis[root] = true;
        up[0][root] = root;

        while (!q.empty()) {
            int v = q.front(); q.pop();
            for (int u : g[v]) {
                if (vis[u]) continue;
                vis[u] = true;
                dep[u] = dep[v] + 1;
                up[0][u] = v;
                upData[0][u] = baseFn(vals[v]);
                q.push(u);
            }
        }

        for (int k = 1; k < LOG; k++)
            for (int v = 0; v < n; v++) {
                up[k][v] = up[k-1][up[k-1][v]];
                upData[k][v] = mergeOpt(upData[k-1][v], upData[k-1][up[k-1][v]]);
            }
    }

    T applyBase(int v) { return baseFn(vals[v]); }

    int kthAncestor(int v, int k) {
        for (int i = LOG - 1; i >= 0; i--)
            if (k >= (1 << i)) { v = up[i][v]; k -= (1 << i); }
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

    int geodesic(int a, int b, int c) {
        return lca(a, b) ^ lca(a, c) ^ lca(b, c);
    }

    int kthOnPath(int a, int b, int k) {
        int l = lca(a, b);
        int da = dep[a] - dep[l], db = dep[b] - dep[l];
        if (k < 1 || k > da + db + 1) return -1;
        if (k <= da + 1) return kthAncestor(a, k - 1);
        return kthAncestor(b, db - (k - da - 1));
    }

    bool inPath(int a, int b, int x) { return geodesic(a, b, x) == x; }

    int distToPath(int a, int b, int x) {
        return dep[x] - dep[geodesic(a, b, x)];
    }

    T liftQuery(int v, int cnt) {
        T acc = applyBase(v);
        int rem = cnt - 1;
        for (int k = LOG - 1; k >= 0; k--)
            if (rem >= (1 << k)) {
                if (upData[k][v]) acc = mergeFn(acc, *upData[k][v]);
                v = up[k][v];
                rem -= (1 << k);
            }
        return acc;
    }

    T pathQuery(int a, int b) {
        int l = lca(a, b);
        int da = dep[a] - dep[l], db = dep[b] - dep[l];
        T res = applyBase(l);
        if (da > 0) res = mergeFn(liftQuery(a, da), res);
        if (db > 0) res = mergeFn(res, liftQuery(b, db));
        return res;
    }
};

template<typename V, typename BaseFn, typename MergeFn>
auto makeLift(int root, vector<pair<int,int>>& edges, vector<V>& vals,
              BaseFn base, MergeFn merge) {
    using T = invoke_result_t<BaseFn, V>;
    return Lift<T, V, BaseFn, MergeFn>(root, edges, vals, base, merge);
}

/**
 * Definition for a binary tree node.
 * struct TreeNode {
 *     int val;
 *     TreeNode *left;
 *     TreeNode *right;
 *     TreeNode() : val(0), left(nullptr), right(nullptr) {}
 *     TreeNode(int x) : val(x), left(nullptr), right(nullptr) {}
 *     TreeNode(int x, TreeNode *left, TreeNode *right) : val(x), left(left), right(right) {}
 * };
 */

 struct NodeData {
    int sum;
    bitset<2001> mask;
 };

class Solution {
public:
    int maxSum(TreeNode* root) {
        auto base = [&](int v) -> NodeData {
            NodeData nd;
            nd.sum = v;
            nd.mask.set(v + 1000);
            return nd;
        };
        auto merge = [&](NodeData n1, NodeData n2) -> NodeData {
            NodeData agg;
            agg.sum = n1.sum + n2.sum;
            agg.mask = n1.mask | n2.mask;
            return agg;
        };
        
        unordered_map<TreeNode*,int> nodeToId;
        int id = 0;
        auto dfs = [&](auto&&self, TreeNode* node) -> void {
            nodeToId[node] = id++;
            if (node->left) {
                self(self, node->left);
            }
            if (node->right) {
                self(self, node->right);
            }
        };
        dfs(dfs, root);

        int n = nodeToId.size();
        vector<int> vals(n);
        vector<pair<int,int>> edges;
        auto dfs2 = [&](auto&& self, TreeNode* node) -> void {
            vals[nodeToId[node]] = node->val;
            if (node->left) {
                self(self, node->left);
                edges.push_back({nodeToId[node], nodeToId[node->left]});
                
            }
            if (node->right) {
                self(self, node->right);
                edges.push_back({nodeToId[node], nodeToId[node->right]});
            }
        };
        dfs2(dfs2, root);

        auto lifter = makeLift(0, edges, vals, base, merge);
        int res = -10000000;
        for (int node1 = 0; node1 < n; node1++) {
            res = max(res, vals[node1]); // single node paths
            for (int node2 = node1 + 1; node2 < n; node2++) {
                auto nodeData = lifter.pathQuery(node1, node2);
                auto pathDist = lifter.pathDist(node1, node2);
                int reqNodes = 1 + pathDist;
                if (nodeData.mask.count() == reqNodes) {
                    res = max(res, nodeData.sum);
                }
            }
        }
        return res;
    }
};




// SOLUTION 2 WITH BASIC DFS, O(n^2)
// # Definition for a binary tree node.
// # class TreeNode:
// #     def __init__(self, val=0, left=None, right=None):
// #         self.val = val
// #         self.left = left
// #         self.right = right
// class Solution:
//     def maxSum(self, root: Optional[TreeNode]) -> int:
//         # dfs from every node, visiting all other nodes

//         g = defaultdict(list) # node -> list of adj nodes

//         def makeG(node):
//             for ch in [node.left, node.right]:
//                 if ch:
//                     g[node].append(ch)
//                     g[ch].append(node)
//                     makeG(ch)
//         makeG(root)

//         used = set() # used values
//         seen = set() # basically our path
//         res = -inf
//         def dfs(node, currSum):
//             nonlocal res
//             used.add(node.val)
//             seen.add(node)
//             res = max(res, currSum)
//             for adj in g[node]:
//                 if adj not in seen and adj.val not in used:
//                     dfs(adj, currSum + adj.val)
//             used.remove(node.val)
//             seen.remove(node)
        
//         def getScores(node):
//             dfs(node, node.val)
//             for ch in [node.left, node.right]:
//                 if ch:
//                     getScores(ch)
//         getScores(root)

//         return res

            

// Solution 3 WITH TREE CONVOLUTION DFS O(n^2 * n/W)
# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def maxSum(self, root: Optional[TreeNode]) -> int:

        res = -inf
        
        # returns all possible (pathSum, bitset) up
        def dfs(node):
            nonlocal res
            res = max(res, node.val) # single node paths
            bs = 1 << (node.val + 1000)
            # if we are a leaf just send that up
            if not node.left and not node.right:
                return [(node.val, bs)]
            # chains up to root
            chains = [(node.val, bs)]
            for child in [node.left, node.right]:
                nchains = []
                if not child: continue
                allData = dfs(child)
                for pathSum, pathBs in allData:
                    # generate new chains
                    if (not bs & pathBs):
                        nchains.append((node.val + pathSum, bs | pathBs))
                    else:
                        continue
                    for beforePathSum, beforeBs in chains:
                        if not (beforeBs & pathBs):
                            nsum = beforePathSum + pathSum
                            res = max(res, nsum)

                chains += nchains
            
            return chains
        
        dfs(root)

        return res