# EXAMPLE
#
# TYPES:
# NodeData (usually a tuple or normal number)
#
# here NodeData is a tuple (total, pref, suf, best, length) for max subsegment sum

# def base(rawVal) -> NodeData:
#     return (rawVal, rawVal, rawVal, rawVal, 1)

# how to aggregate two NodeData nodes, order matters
# def mergeFn(A, B) -> NodeData:
#     at, ap, asf, ab, al = A
#     bt, bp, bsf, bb, bl = B
#     return (at + bt, max(ap, at + bp), max(bsf, bt + asf), max(ab, bb, asf + bp), al + bl)

# how to reverse a NodeData
# def reverseFn(nodeData) -> NodeData:
#     total, pref, suf, best, length = nodeData
#     return (total, suf, pref, best, length)


# TO CREATE THE HLD (O(n) build time)
# edges should be [(a, b), (c, d), ...]
# vals[node] is the value AT that node, if the nodes are 1..n then vals[0] can be whatever dummy value
# root can be any node in the tree, separate from if the nodes are 0..n-1 or 1..n
# last param is `zeroIndexed`, so False means the nodes are 1..n
# hld = HldSegTreeReverse(edges, vals, base, mergeFn, reverseFn, 1, False)


# METHODS

# O(logN)
# pointSet(nodeLabel, RawVal), overwrites the value at `nodeLabel` with this new raw value

# O(logN)
# pointApply(nodeLabel, RawVal), combines this raw value into `nodeLabel`

# O(log^2 N)
# pathQuery(a, b) -> NodeData, gives us the aggregated data on the path a->b, includes both endpoints

# O(log N)
# subtreeQuery(nodeLabel) -> NodeData, aggregated data of all nodes in the subtree (orientation is unspecified / not ordered), includes nodeLabel itself


class HldSegTreeReverse:
    def __init__(self, edges, vals, base, combine, reverse, root, zeroIndexed):
        n = len(edges) + 1
        self.n = n
        self.root = root
        self.zeroIndexed = zeroIndexed
        self.base = base
        self.combine = combine
        self.reverse = reverse
        arrSize = n if zeroIndexed else n + 1
        self.adj = [[] for _ in range(arrSize)]
        for u, v in edges:
            self.adj[u].append(v)
            self.adj[v].append(u)
        self.par = [-1] * arrSize
        self.depth = [0] * arrSize
        self.sz = [1] * arrSize
        self.heavy = [-1] * arrSize
        self.head = [0] * arrSize
        self.pos = [0] * arrSize
        self._dfsInit()
        self._dfsDecompose()
        segN = 1
        while segN < max(n, 1):
            segN <<= 1
        self.segN = segN
        self.tree = [None] * (2 * segN)
        lo = 0 if zeroIndexed else 1
        hi = n if zeroIndexed else n + 1
        for i in range(lo, hi):
            self.tree[segN + self.pos[i]] = base(vals[i])
        for i in range(segN - 1, 0, -1):
            self.tree[i] = self._combineOpt(self.tree[2*i], self.tree[2*i+1])

    def _combineOpt(self, a, b):
        if a is None: return b
        if b is None: return a
        return self.combine(a, b)

    def _reverseOpt(self, a):
        if a is None: return a
        return self.reverse(a)

    def _dfsInit(self):
        adj, par, depth, sz, heavy = self.adj, self.par, self.depth, self.sz, self.heavy
        order = []
        stack = [(self.root, -1, 0)]
        while stack:
            node, parent, d = stack.pop()
            par[node] = parent
            depth[node] = d
            order.append(node)
            for nxt in adj[node]:
                if nxt != parent:
                    stack.append((nxt, node, d + 1))
        for node in reversed(order):
            best = 0
            for nxt in adj[node]:
                if nxt == par[node]:
                    continue
                sz[node] += sz[nxt]
                if sz[nxt] > best:
                    best = sz[nxt]
                    heavy[node] = nxt

    def _dfsDecompose(self):
        adj, par, heavy, head, pos = self.adj, self.par, self.heavy, self.head, self.pos
        timer = 0
        stack = [(self.root, self.root)]
        while stack:
            node, h = stack.pop()
            head[node] = h
            pos[node] = timer
            timer += 1
            for nxt in adj[node]:
                if nxt == par[node] or nxt == heavy[node]:
                    continue
                stack.append((nxt, nxt))
            if heavy[node] != -1:
                stack.append((heavy[node], h))

    def _segQuery(self, l, r):
        if l > r:
            return None
        segN = self.segN
        tree = self.tree
        combine = self.combine
        l += segN
        r += segN + 1
        resL = None
        resR = None
        while l < r:
            if l & 1:
                t = tree[l]
                if t is not None:
                    resL = t if resL is None else combine(resL, t)
                l += 1
            if r & 1:
                r -= 1
                t = tree[r]
                if t is not None:
                    resR = t if resR is None else combine(t, resR)
            l >>= 1; r >>= 1
        if resL is None: return resR
        if resR is None: return resL
        return combine(resL, resR)

    def _segPointSet(self, idx, newData):
        tree = self.tree
        combine = self.combine
        p = idx + self.segN
        tree[p] = newData
        p >>= 1
        while p:
            a = tree[2*p]; b = tree[2*p+1]
            if a is None:
                tree[p] = b
            elif b is None:
                tree[p] = a
            else:
                tree[p] = combine(a, b)
            p >>= 1

    def pointSet(self, node, rawVal):
        self._segPointSet(self.pos[node], self.base(rawVal))

    def pointApply(self, node, rawVal):
        p = self.pos[node] + self.segN
        self._segPointSet(self.pos[node], self._combineOpt(self.tree[p], self.base(rawVal)))

    # ORDERED path query a -> b, includes both endpoints.
    # Each _segQuery chunk is stored ancestor->descendant (pos-increasing). We split the
    # path at the LCA, giving the LCA node to the b-side. As we climb, each newly fetched
    # chunk is higher up, so we PREPEND it to keep each side ordered top->bottom
    # (ancestor->descendant). The b-side in that orientation is already the correct forward
    # order (lca->b). The a-side's real traversal is a->lca (exclusive of lca), i.e.
    # bottom->top, the reverse of how it's stored, so we reverse it before joining.
    def pathQuery(self, a, b):
        head, depth, par, pos = self.head, self.depth, self.par, self.pos
        accA = None  # a-side nodes below the LCA, stored ancestor->descendant
        accB = None  # b-side nodes plus the LCA, stored ancestor->descendant
        ca, cb = a, b
        while head[ca] != head[cb]:
            if depth[head[ca]] > depth[head[cb]]:
                accA = self._combineOpt(self._segQuery(pos[head[ca]], pos[ca]), accA)
                ca = par[head[ca]]
            else:
                accB = self._combineOpt(self._segQuery(pos[head[cb]], pos[cb]), accB)
                cb = par[head[cb]]
        # same chain now; shallower endpoint is the LCA. The LCA node goes to the b-side.
        if depth[ca] > depth[cb]:
            accA = self._combineOpt(self._segQuery(pos[cb] + 1, pos[ca]), accA)
            accB = self._combineOpt(self._segQuery(pos[cb], pos[cb]), accB)
        else:
            accB = self._combineOpt(self._segQuery(pos[ca], pos[cb]), accB)
        return self._combineOpt(self._reverseOpt(accA), accB)

    def subtreeQuery(self, node):
        return self._segQuery(self.pos[node], self.pos[node] + self.sz[node] - 1)#include <bits/stdc++.h>
using namespace std;
using ll = long long;


// EXAMPLE
// using RawVal = ll; // the raw node value input, could also be a struct

// // Accumulated node data
// struct NodeData {
//     ll total, pref, suf, best;
//     int len;
// };

// // Maps the raw node value to our NodeData
// auto base = [](RawVal v) -> NodeData {
//     return NodeData{v, v, v, v, 1};
// };

// // How to aggregate two NodeData nodes, order matters
// auto mergeFn = [](NodeData A, NodeData B) -> NodeData {
//     return NodeData{
//         A.total + B.total,
//         max(A.pref, A.total + B.pref),
//         max(B.suf,  B.total + A.suf),
//         max({A.best, B.best, A.suf + B.pref}),
//         A.len + B.len
//     };
// };

// How to reverse a NodeData
// auto reverseFn = [](NodeData nodeData) -> NodeData {
//     return NodeData{nodeData.total, nodeData.suf, nodeData.pref, nodeData.best, nodeData.len};
// };


// TO CREATE THE HLD (O(n) build time)
// RawVal, NodeData are the types
// edges should be vector<pair<int,int>> with node labels (either 0...n-1, or 1...n)
// vals[node] is the value AT that node, if the nodes are 1...n then vals[0] can be whatever dummy value
// 1 at the end is the root, it can be any value in the tree, separate from if the nodes are 0...n-1 or 1...n
// last param is `zeroIndexed`, so false means the nodes are 1...n
// HldSegTreeReverse<RawVal, NodeData> hld(edges, vals, base, mergeFn, reverseFn, 1, false);


// METHODS

// O(logN)
// pointSet(nodeLabel, RawVal), overwrites the value at `nodeLabel` with this new raw value

// O(logN)
// pointApply(nodeLabel, RawVal), combines this raw value into `nodeLabel`

// O(log^2 N)
// pathQuery(a, b) -> NodeData, gives us the aggregated data on the path a->b, includes both endpoints

// O(log N)
// subtreeQuery(nodeLabel) -> NodeData, aggregated data of all nodes in the subtree (orientation is unspecified / not ordered), includes nodeLabel itself


template <typename RawT, typename StoredT>
struct HldSegTreeReverse {
    int n, root, arrSize;
    bool zeroIndexed;
    function<StoredT(RawT)> base;
    function<StoredT(StoredT, StoredT)> combine;
    function<StoredT(StoredT)> reverse_;
    vector<vector<int>> adj;
    vector<int> par, depth, sz, heavy, head, pos;
    int segN, LOG;
    vector<optional<StoredT>> tree;

    HldSegTreeReverse(
        const vector<pair<int,int>>& edges,
        const vector<RawT>& vals,
        function<StoredT(RawT)> base,
        function<StoredT(StoredT, StoredT)> combine,
        function<StoredT(StoredT)> reverse_,
        int root,
        bool zeroIndexed)
        : n((int)edges.size() + 1), root(root),
          arrSize(zeroIndexed ? (int)edges.size() + 1 : (int)edges.size() + 2), zeroIndexed(zeroIndexed),
          base(base), combine(combine), reverse_(reverse_),
          adj(arrSize), par(arrSize, -1), depth(arrSize, 0), sz(arrSize, 1),
          heavy(arrSize, -1), head(arrSize, 0), pos(arrSize, 0)
    {
        assert(zeroIndexed ? (root >= 0 && root < n) : (root >= 1 && root <= n));
        for (auto& [u, v] : edges) {
            adj[u].push_back(v);
            adj[v].push_back(u);
        }
        _dfsInit();
        _dfsDecompose();
        segN = 1;
        while (segN < max(n, 1)) segN <<= 1;
        LOG = max(1, __lg(segN));
        tree.assign(2 * segN, nullopt);
        int lo = zeroIndexed ? 0 : 1;
        int hi = zeroIndexed ? n : n + 1;
        for (int i = lo; i < hi; i++) {
            tree[segN + pos[i]] = base(vals[i]);
        }
        for (int i = segN - 1; i >= 1; i--) {
            tree[i] = _combineOpt(tree[2*i], tree[2*i+1]);
        }
    }

    optional<StoredT> _combineOpt(const optional<StoredT>& a, const optional<StoredT>& b) {
        if (!a.has_value()) return b;
        if (!b.has_value()) return a;
        return combine(*a, *b);
    }

    optional<StoredT> _reverseOpt(const optional<StoredT>& a) {
        if (!a.has_value()) return a;
        return reverse_(*a);
    }

    void _dfsInit() {
        vector<int> order;
        order.reserve(n);
        vector<tuple<int,int,int>> stack;
        stack.push_back({root, -1, 0});
        while (!stack.empty()) {
            auto [node, parent, d] = stack.back();
            stack.pop_back();
            par[node] = parent;
            depth[node] = d;
            order.push_back(node);
            for (int nxt : adj[node]) {
                if (nxt != parent) stack.push_back({nxt, node, d + 1});
            }
        }
        for (int i = (int)order.size() - 1; i >= 0; i--) {
            int node = order[i];
            int best = 0;
            for (int nxt : adj[node]) {
                if (nxt == par[node]) continue;
                sz[node] += sz[nxt];
                if (sz[nxt] > best) {
                    best = sz[nxt];
                    heavy[node] = nxt;
                }
            }
        }
    }

    void _dfsDecompose() {
        int timer = 0;
        vector<pair<int,int>> stack;
        stack.push_back({root, root});
        while (!stack.empty()) {
            auto [node, h] = stack.back();
            stack.pop_back();
            head[node] = h;
            pos[node] = timer++;
            for (int nxt : adj[node]) {
                if (nxt == par[node] || nxt == heavy[node]) continue;
                stack.push_back({nxt, nxt});
            }
            if (heavy[node] != -1) {
                stack.push_back({heavy[node], h});
            }
        }
    }

    optional<StoredT> _segQuery(int l, int r) {
        if (l > r) return nullopt;
        l += segN;
        r += segN + 1;
        optional<StoredT> resL = nullopt, resR = nullopt;
        while (l < r) {
            if (l & 1) { resL = _combineOpt(resL, tree[l]); l++; }
            if (r & 1) { r--; resR = _combineOpt(tree[r], resR); }
            l >>= 1; r >>= 1;
        }
        return _combineOpt(resL, resR);
    }

    void _segPointSet(int idx, const optional<StoredT>& newData) {
        int p = idx + segN;
        tree[p] = newData;
        for (p >>= 1; p > 0; p >>= 1) {
            tree[p] = _combineOpt(tree[2*p], tree[2*p+1]);
        }
    }

    void pointSet(int node, RawT rawVal) {
        _segPointSet(pos[node], base(rawVal));
    }

    void pointApply(int node, RawT rawVal) {
        _segPointSet(pos[node], _combineOpt(tree[pos[node] + segN], optional<StoredT>(base(rawVal))));
    }

    // ORDERED path query a -> b, includes both endpoints.
    // Each _segQuery chunk is stored ancestor->descendant (pos-increasing). We split the
    // path at the LCA, giving the LCA node to the b-side. As we climb, each newly fetched
    // chunk is higher up, so we PREPEND it (_combineOpt(chunk, acc)) to keep each side
    // ordered top->bottom (ancestor->descendant). The b-side in that orientation is already
    // the correct forward order (lca->b). The a-side's real traversal is a->lca (exclusive
    // of lca), i.e. bottom->top, the reverse of how it's stored, so we reverse it first.
    StoredT pathQuery(int a, int b) {
        optional<StoredT> accA = nullopt;   // a-side nodes below the LCA, ancestor->descendant
        optional<StoredT> accB = nullopt;   // b-side nodes plus the LCA, ancestor->descendant
        int ca = a, cb = b;
        while (head[ca] != head[cb]) {
            if (depth[head[ca]] > depth[head[cb]]) {
                accA = _combineOpt(_segQuery(pos[head[ca]], pos[ca]), accA);
                ca = par[head[ca]];
            } else {
                accB = _combineOpt(_segQuery(pos[head[cb]], pos[cb]), accB);
                cb = par[head[cb]];
            }
        }
        // same chain: shallower endpoint is the LCA; the LCA node goes to the b-side
        if (depth[ca] > depth[cb]) {
            accA = _combineOpt(_segQuery(pos[cb] + 1, pos[ca]), accA);
            accB = _combineOpt(_segQuery(pos[cb], pos[cb]), accB);
        } else {
            accB = _combineOpt(_segQuery(pos[ca], pos[cb]), accB);
        }
        return *_combineOpt(_reverseOpt(accA), accB);
    }

    StoredT subtreeQuery(int node) {
        return *_segQuery(pos[node], pos[node] + sz[node] - 1);
    }
};