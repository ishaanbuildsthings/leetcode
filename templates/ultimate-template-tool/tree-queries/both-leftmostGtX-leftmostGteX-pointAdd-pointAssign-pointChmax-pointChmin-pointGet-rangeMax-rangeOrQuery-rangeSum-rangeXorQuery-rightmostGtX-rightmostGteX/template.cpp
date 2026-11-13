// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/tree-queries/both-leftmostGtX-leftmostGteX-pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeMax-rangeOrQuery-rangeSum-rangeXorQuery-rightmostGtX-rightmostGteX/template.cpp
// The range structure inside is https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/leftmostGtX-leftmostGteX-pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeMax-rangeOrQuery-rangeSum-rangeXorQuery-rightmostGtX-rightmostGteX/fast.cpp
// @operations: countAtDepthInSubtree depth edgeAdd edgeAssign edgeChmax edgeChmin edgeGet edgeNearestAncestorGtX edgeNearestAncestorGteX edgePathFirstGtX edgePathFirstGteX edgePathLastGtX edgePathLastGteX edgePathMax edgePathOR edgePathSum edgePathXOR edgeSubtreeMax edgeSubtreeOR edgeSubtreeSum edgeSubtreeXOR isAncestor isOnPath kthAncestor kthNodeOnPath lca lcaRootedAt median nextNodeOnPath nodeAdd nodeAssign nodeChmax nodeChmin nodeGet nodeNearestAncestorGtX nodeNearestAncestorGteX nodePathFirstGtX nodePathFirstGteX nodePathLastGtX nodePathLastGteX nodePathMax nodePathOR nodePathSum nodePathXOR nodeSubtreeMax nodeSubtreeOR nodeSubtreeSum nodeSubtreeXOR parent parentRootedAt pathIntersection pathNodes subtreeSize subtreeSizeRootedAt unweightedDist unweightedDistBetweenPaths unweightedDistToPath
// @data-structure-type: seg-tree
// @complexities:
//   countAtDepthInSubtree: log(N)
//   depth: 1
//   edgeAdd: log(N)
//   edgeAssign: log(N)
//   edgeChmax: log(N)
//   edgeChmin: log(N)
//   edgeGet: log(N)
//   edgeNearestAncestorGtX: log^2(N)
//   edgeNearestAncestorGteX: log^2(N)
//   edgePathFirstGtX: log^2(N)
//   edgePathFirstGteX: log^2(N)
//   edgePathLastGtX: log^2(N)
//   edgePathLastGteX: log^2(N)
//   edgePathMax: log^2(N)
//   edgePathOR: log^2(N)
//   edgePathSum: log^2(N)
//   edgePathXOR: log^2(N)
//   edgeSubtreeMax: log(N)
//   edgeSubtreeOR: log(N)
//   edgeSubtreeSum: log(N)
//   edgeSubtreeXOR: log(N)
//   isAncestor: 1
//   isOnPath: log(N)
//   kthAncestor: log(N)
//   kthNodeOnPath: log(N)
//   lca: log(N)
//   lcaRootedAt: log(N)
//   median: log(N)
//   nextNodeOnPath: log(N)
//   nodeAdd: log(N)
//   nodeAssign: log(N)
//   nodeChmax: log(N)
//   nodeChmin: log(N)
//   nodeGet: log(N)
//   nodeNearestAncestorGtX: log^2(N)
//   nodeNearestAncestorGteX: log^2(N)
//   nodePathFirstGtX: log^2(N)
//   nodePathFirstGteX: log^2(N)
//   nodePathLastGtX: log^2(N)
//   nodePathLastGteX: log^2(N)
//   nodePathMax: log^2(N)
//   nodePathOR: log^2(N)
//   nodePathSum: log^2(N)
//   nodePathXOR: log^2(N)
//   nodeSubtreeMax: log(N)
//   nodeSubtreeOR: log(N)
//   nodeSubtreeSum: log(N)
//   nodeSubtreeXOR: log(N)
//   parent: 1
//   parentRootedAt: log(N)
//   pathIntersection: log(N)
//   pathNodes: K+log(N)
//   subtreeSize: 1
//   subtreeSizeRootedAt: log(N)
//   unweightedDist: log(N)
//   unweightedDistBetweenPaths: log(N)
//   unweightedDistToPath: log(N)
//   build: N
// @memory:
//   layout: 2n-iterative
//   node: sm[4*N] mx[4*N] xr[4*N] orr[4*N]
//   tags: none
//   other: par[1*N] dep[1*N] sz[1*N] head[1*N] pos[1*N] order[1*N] depthPos[1*N] depthStart[1*N]
//   note: leaves [n, 2n) hold each value's own aggregates
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// FAST MODE (this is the only C++ version): sanitizers are skipped inside this template, so a bad access in it goes
// unreported. To turn that off (say, when debugging with sanitizers), put this line above the template:
//   #define LEETCODE_NO_SANITIZE
// Without sanitizers (Codeforces, a plain -O2 build) it changes nothing. It needs GCC or Clang.

// Segment tree with composable aggregates (2N iterative): point updates and range queries in O(logN); each node keeps
// its sum, its max, its xor, its OR over its range. All indices 0-based, ranges inclusive [l, r]; searches return -1
// when nothing qualifies. Leaves tree[n..2n); a node used by a query or update is a perfect subtree of 2^s leaves (s
// = its level); an update rewrites a leaf, then its ancestors.
// T: int, long long, ...; sums are kept in S (long long for small T).
#ifdef __SSE2__
#include <immintrin.h>
#endif

// LEETCODE_NO_SANITIZE skips sanitizers in a function. It only changes anything where sanitizers run, like LeetCode: on
// Codeforces it compiles and does nothing.
// This template already uses it. To go further, put it on the one function with your hot loop:
//   LEETCODE_NO_SANITIZE long long maxSum(vector<int>& nums, int k) {
// A lambda needs its own: [&](int x) LEETCODE_NO_SANITIZE { ... }. It does not carry into anything that function calls.
// Inside a marked function use raw pointers and plain comparisons, not vector[] and min / max, or it can get slower.
// Bad memory accesses in a marked function go unreported.
#ifndef LEETCODE_NO_SANITIZE
#define LEETCODE_NO_SANITIZE __attribute__((no_sanitize("address"), no_sanitize("undefined")))
#endif
#define LEETCODE_NO_SANITIZE_INLINE LEETCODE_NO_SANITIZE __attribute__((always_inline)) inline

// A vector whose [] and size() always inline, even with sanitizers skipped (libstdc++ only; elsewhere a plain vector)
template <typename U>
struct HotVector : vector<U> {
    using vector<U>::vector;
    HotVector() = default;
    HotVector(const vector<U>& other) : vector<U>(other) {}
    HotVector(vector<U>&& other) : vector<U>(move(other)) {}
#ifdef __GLIBCXX__
    LEETCODE_NO_SANITIZE_INLINE typename vector<U>::reference operator[](size_t i) { return this->_M_impl._M_start[i]; }
    LEETCODE_NO_SANITIZE_INLINE typename vector<U>::const_reference operator[](size_t i) const {
        return this->_M_impl._M_start[i];
    }
    LEETCODE_NO_SANITIZE_INLINE size_t size() const { return size_t(this->_M_impl._M_finish - this->_M_impl._M_start); }
#endif
};

template <typename T>
struct SegTree {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    int n, h;
    HotVector<S> sm;
    HotVector<T> mx;
    HotVector<T> xr;
    HotVector<T> orr;

    // O(N) -- arr: the initial array (non-empty)
    explicit SegTree(const vector<T>& arr) : n((int)arr.size()), h(n ? 32 - __builtin_clz(n) : 0) {
        sm.assign(2 * n, 0);
        mx.assign(2 * n, T(0));
        xr.assign(2 * n, T(0));
        orr.assign(2 * n, T(0));
        for (int i = 0; i < n; i++) setLeaf(n + i, arr[i]);
        for (int x = n - 1; x > 0; x--) pull(x);
    }

    // O(N) -- the whole array
    LEETCODE_NO_SANITIZE vector<T> getAll() const {
        vector<T> out(n);
        for (int i = 0; i < n; i++) out[i] = leaf(n + i);
        return out;
    }

    // O(logN) -- the first i in [l, r] with a[i] > x, or -1 (a walk pruned by the node max); needs 0 <= l <= r < n,
    // else throws out_of_range
    LEETCODE_NO_SANITIZE int leftmostGtX(int l, int r, T x) {
        if (l < 0 || l > r || r >= n) throw out_of_range("leftmostGtX: needs 0 <= l <= r < n");
        int ns[64]{}, ls[64]{}, c = cover(l, r, ns, ls);  // (zeroed: l <= r gives at least one node)
        for (int i = 0; i < c; i++) {
            int t = ns[i];
            if (!(mx[t] > x)) continue;
            while (t < n) t = mx[2 * t] > x ? 2 * t : 2 * t + 1;  // walk down the passing node
            return t - n;
        }
        return -1;
    }

    // O(logN) -- the first i in [l, r] with a[i] >= x, or -1 (a walk pruned by the node max); needs 0 <= l <= r < n,
    // else throws out_of_range
    LEETCODE_NO_SANITIZE int leftmostGteX(int l, int r, T x) {
        if (l < 0 || l > r || r >= n) throw out_of_range("leftmostGteX: needs 0 <= l <= r < n");
        int ns[64]{}, ls[64]{}, c = cover(l, r, ns, ls);  // (zeroed: l <= r gives at least one node)
        for (int i = 0; i < c; i++) {
            int t = ns[i];
            if (!(mx[t] >= x)) continue;
            while (t < n) t = mx[2 * t] >= x ? 2 * t : 2 * t + 1;  // walk down the passing node
            return t - n;
        }
        return -1;
    }

    // O(logN) -- a[i] += v; needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAdd(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointAdd: needs 0 <= i < n");
        int p = i + n;
        setLeaf(p, T(leaf(p) + v)), rebuild(p);
    }

    // O(logN) -- a[i] = v; needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAssign(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointAssign: needs 0 <= i < n");
        int p = i + n;
        setLeaf(p, v), rebuild(p);
    }

    // O(logN) -- a[i] = max(a[i], v); needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointChmax(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointChmax: needs 0 <= i < n");
        int p = i + n;
        setLeaf(p, max(leaf(p), v)), rebuild(p);
    }

    // O(logN) -- a[i] = min(a[i], v); needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointChmin(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointChmin: needs 0 <= i < n");
        int p = i + n;
        setLeaf(p, min(leaf(p), v)), rebuild(p);
    }

    // O(logN) -- a[i]; needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE T pointGet(int i) {
        if (i < 0 || i >= n) throw out_of_range("pointGet: needs 0 <= i < n");
        int p = i + n;
        return leaf(p);
    }

    // O(logN) -- max of a[l..r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE T rangeMax(int l, int r) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeMax: needs 0 <= l <= r < n");
        T res = numeric_limits<T>::lowest();
        for (int lo = l + n, hi = r + n + 1; lo < hi; lo >>= 1, hi >>= 1) {
            if (lo & 1) res = max(res, mx[lo++]);
            if (hi & 1) res = max(res, mx[--hi]);
        }
        return res;
    }

    // O(logN) -- a[l] | ... | a[r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE T rangeOrQuery(int l, int r) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeOrQuery: needs 0 <= l <= r < n");
        T res = T(0);
        for (int lo = l + n, hi = r + n + 1; lo < hi; lo >>= 1, hi >>= 1) {
            if (lo & 1) res |= orr[lo++];
            if (hi & 1) res |= orr[--hi];
        }
        return res;
    }

    // O(logN) -- a[l] + ... + a[r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE S rangeSum(int l, int r) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeSum: needs 0 <= l <= r < n");
        S res = S(0);
        for (int lo = l + n, hi = r + n + 1; lo < hi; lo >>= 1, hi >>= 1) {
            if (lo & 1) res += sm[lo++];
            if (hi & 1) res += sm[--hi];
        }
        return res;
    }

    // O(logN) -- a[l] ^ ... ^ a[r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE T rangeXorQuery(int l, int r) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeXorQuery: needs 0 <= l <= r < n");
        T res = T(0);
        for (int lo = l + n, hi = r + n + 1; lo < hi; lo >>= 1, hi >>= 1) {
            if (lo & 1) res ^= xr[lo++];
            if (hi & 1) res ^= xr[--hi];
        }
        return res;
    }

    // O(logN) -- the last i in [l, r] with a[i] > x, or -1 (a walk pruned by the node max); needs 0 <= l <= r < n,
    // else throws out_of_range
    LEETCODE_NO_SANITIZE int rightmostGtX(int l, int r, T x) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rightmostGtX: needs 0 <= l <= r < n");
        int ns[64]{}, ls[64]{}, c = cover(l, r, ns, ls);  // (zeroed: l <= r gives at least one node)
        for (int i = c - 1; i >= 0; i--) {
            int t = ns[i];
            if (!(mx[t] > x)) continue;
            while (t < n) t = mx[2 * t + 1] > x ? 2 * t + 1 : 2 * t;  // walk down the passing node
            return t - n;
        }
        return -1;
    }

    // O(logN) -- the last i in [l, r] with a[i] >= x, or -1 (a walk pruned by the node max); needs 0 <= l <= r < n,
    // else throws out_of_range
    LEETCODE_NO_SANITIZE int rightmostGteX(int l, int r, T x) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rightmostGteX: needs 0 <= l <= r < n");
        int ns[64]{}, ls[64]{}, c = cover(l, r, ns, ls);  // (zeroed: l <= r gives at least one node)
        for (int i = c - 1; i >= 0; i--) {
            int t = ns[i];
            if (!(mx[t] >= x)) continue;
            while (t < n) t = mx[2 * t + 1] >= x ? 2 * t + 1 : 2 * t;  // walk down the passing node
            return t - n;
        }
        return -1;
    }

    // O(log(N)) -- sum of the whole array a[0..n-1] (rangeSum(0, n - 1)); needs n >= 1, else throws out_of_range
    LEETCODE_NO_SANITIZE auto sumAll() {
        if (n < 1) throw out_of_range("sumAll: needs n >= 1");
        return rangeSum(0, n - 1);
    }

    // O(log(N)) -- max of the whole array a[0..n-1] (rangeMax(0, n - 1)); needs n >= 1, else throws out_of_range
    LEETCODE_NO_SANITIZE auto maxAll() {
        if (n < 1) throw out_of_range("maxAll: needs n >= 1");
        return rangeMax(0, n - 1);
    }

    // O(log(N)) -- xor of the whole array a[0..n-1] (rangeXorQuery(0, n - 1)); needs n >= 1, else throws out_of_range
    LEETCODE_NO_SANITIZE auto xorAll() {
        if (n < 1) throw out_of_range("xorAll: needs n >= 1");
        return rangeXorQuery(0, n - 1);
    }

    // O(log(N)) -- OR of the whole array a[0..n-1] (rangeOrQuery(0, n - 1)); needs n >= 1, else throws out_of_range
    LEETCODE_NO_SANITIZE auto orAll() {
        if (n < 1) throw out_of_range("orAll: needs n >= 1");
        return rangeOrQuery(0, n - 1);
    }

    // ---- internals ----

    LEETCODE_NO_SANITIZE void setLeaf(int p, T v) {  // leaf p holds v alone
        sm[p] = S(v), mx[p] = v, xr[p] = v, orr[p] = v;
    }

    LEETCODE_NO_SANITIZE T leaf(int p) const { return T(sm[p]); }  // the value at leaf p

    LEETCODE_NO_SANITIZE void pull(int x) {  // recompute node x from its children
        int a = 2 * x, b = 2 * x + 1;
        sm[x] = sm[a] + sm[b];
        mx[x] = max(mx[a], mx[b]);
        xr[x] = xr[a] ^ xr[b];
        orr[x] = orr[a] | orr[b];
    }

    LEETCODE_NO_SANITIZE void rebuild(int p) {  // recompute every ancestor of leaf p
        while (p > 1) p >>= 1, pull(p);
    }

    LEETCODE_NO_SANITIZE int cover(int l, int r, int* ns, int* ls) {
        // the nodes covering a[l..r] left to right (ns) and their levels (ls)
        int c = 0, rc = 0, rn[32], rl[32];
        for (int lo = l + n, hi = r + n + 1, s = 0; lo < hi; lo >>= 1, hi >>= 1, s++) {
            if (lo & 1) ns[c] = lo++, ls[c++] = s;
            if (hi & 1) rn[rc] = --hi, rl[rc++] = s;
        }
        while (rc) rc--, ns[c] = rn[rc], ls[c++] = rl[rc];
        return c;
    }
};

// Tree tree(edges, root, vals);
//
// edges: the tree's n - 1 edges with their weights, vector<vector<int>> (vector<vector<long long>> works too). Whether
//        nodes are 0..n-1 or 1..n is detected automatically from the edge list (smallest label is 0 -> 0..n-1,
//        otherwise 1..n; with no edges, from root)
//   {{a, b, w}, ...}     e.g. {{0, 1, 5}, {1, 2, 7}}
// root: the root node (required), e.g. 0 or 1.
// vals: the node values, vector<T> (T = long long, or int; the weights are kept as T too), vals[node] is node's value
//   nodes 0..n-1: size n        e.g. n = 3: {10, 20, 30}         node 0 -> 10
//   nodes 1..n:   size n + 1    e.g. n = 3: {0, 10, 20, 30}      vals[0] is ignored, node 1 -> 10
//
//   Tree<long long> tree({{0, 1, 5}, {1, 2, 7}}, 0, {10, 20, 30});       // nodes 0..2, rooted at 0
//   Tree<long long> tree({{1, 2, 5}, {2, 3, 7}}, 1, {0, 10, 20, 30});    // nodes 1..3, rooted at 1
//
// The node... ops act on the node values and the edge... ops on the edge weights: the two never affect each other. For
// nodes, a path a..b includes both a and b. For edges, a path a..b covers the edges between a and b and a subtree the
// edges below node; an edge is named by its two ends in either order, a search that finds an edge returns its lower end
// (the end farther from the root), and a query with no edges to look at (a path a..a, a leaf's subtree) says what it
// returns. Nodes go in and come out with your labels, -1 means "none", and a label that is not in the tree throws
// out_of_range. Nothing recurses, so a 10^6-node chain is fine.
//
// How it works: one heavy-light pass gives every node a position, so that each heavy chain and each subtree is one
// stretch of positions (pos[node] .. pos[node] + sz[node] - 1). Two copies of the range structure above (SegTree) sit
// over those positions: nodeSeg holds each node's value at its position, edgeSeg each edge's weight at its lower end's
// position (the root's holds no edge). A subtree is one range, and a path a..b is O(log n) ranges, one per chain it
// crosses.
template <typename T>
struct Tree {
    int n, lo, hi, root;  // nodes are lo..hi
    // by node label: parent (-1 for the root), depth, subtree size, top of its chain, position
    HotVector<int> par, dep, sz, head, pos;
    HotVector<int> order;  // order[pos[v]] = v
    // depthPos[depthStart[d] .. depthStart[d + 1]) = the positions of the nodes at depth d, increasing
    HotVector<int> depthStart, depthPos;
    SegTree<T> nodeSeg;  // the node values, in position order
    SegTree<T> edgeSeg;  // each edge's weight, at its lower end's position

    // O(n) -- builds the layout and the two range structures; throws invalid_argument when the edges are not one tree
    // on nodes 0..n-1 or 1..n, an edge has no weight, or vals has the wrong size
    template <typename E = int> Tree(const vector<vector<E>>& edges, int root, const vector<T>& vals)
        : nodeSeg(layout(edges, root, vals)), edgeSeg(weights(edges)) {}

    // lays the tree out (fills the arrays above) and returns the values in position order
    template <typename E> vector<T> layout(const vector<vector<E>>& edges, int root, const vector<T>& vals) {
        this->root = root;
        n = (int)edges.size() + 1;
        long long least = root;
        if (!edges.empty()) {
            least = LLONG_MAX;
            for (const auto& e : edges) {
                if (e.size() != 2 && e.size() != 3)
                    throw invalid_argument("Tree: every edge needs 2 or 3 numbers, {a, b} or {a, b, w}");
                least = min({least, (long long)e[0], (long long)e[1]});
            }
        }
        if (least != 0 && least != 1)
            throw invalid_argument("Tree: nodes must be labeled 0..n-1 or 1..n, but the smallest label is " +
                                   to_string(least));
        lo = (int)least, hi = lo + n - 1;
        string nodes = to_string(lo) + ".." + to_string(hi);
        if (root < lo || root > hi)
            throw invalid_argument("Tree: root must be one of the nodes " + nodes + ", got " + to_string(root));
        int size = hi + 1;

        // the neighbors of v are adj[start[v] .. start[v + 1])
        vector<int> start(size + 1, 0), adj(2 * (n - 1));
        for (const auto& e : edges) {
            if ((long long)e[0] > hi || (long long)e[1] > hi)
                throw invalid_argument("Tree: " + to_string(n - 1) + " edges means the nodes are " + nodes +
                                       ", got the edge (" + to_string(e[0]) + ", " + to_string(e[1]) + ")");
            start[e[0] + 1]++, start[e[1] + 1]++;
        }
        for (int v = 0; v < size; v++) start[v + 1] += start[v];
        vector<int> at(start.begin(), start.end() - 1);
        for (const auto& e : edges) {
            int a = (int)e[0], b = (int)e[1];
            adj[at[a]++] = b, adj[at[b]++] = a;
        }

        // parents and depths, top down (par is -2 until a node is reached)
        par.assign(size, -2), dep.assign(size, 0);
        vector<int> bfs(n);
        int reached = 0;
        par[root] = -1, bfs[reached++] = root;
        for (int i = 0; i < reached; i++) {
            int v = bfs[i];
            for (int k = start[v]; k < start[v + 1]; k++) {
                int u = adj[k];
                if (par[u] == -2) par[u] = v, dep[u] = dep[v] + 1, bfs[reached++] = u;
            }
        }
        if (reached != n)
            throw invalid_argument("Tree: the edges do not form one tree (some node cannot be reached from root)");

        // subtree sizes bottom up, then each node's heavy child (the one with the biggest subtree)
        sz.assign(size, 1);
        for (int i = n - 1; i > 0; i--) sz[par[bfs[i]]] += sz[bfs[i]];
        vector<int> heavy(size, -1);
        for (int i = 1; i < n; i++) {
            int v = bfs[i], p = par[v];
            if (heavy[p] == -1 || sz[v] > sz[heavy[p]]) heavy[p] = v;
        }

        // positions: a preorder that always steps into the heavy child first, so a heavy chain is one stretch
        head.assign(size, 0), pos.assign(size, 0), order.assign(n, 0);
        vector<int> todo = {root};
        todo.reserve(n);
        head[root] = root;
        int t = 0;
        while (!todo.empty()) {
            int v = todo.back();
            todo.pop_back();
            pos[v] = t, order[t++] = v;
            int h = heavy[v], p = par[v];
            for (int k = start[v]; k < start[v + 1]; k++) {
                int u = adj[k];
                if (u != p && u != h) head[u] = u, todo.push_back(u);
            }
            if (h != -1) head[h] = head[v], todo.push_back(h);  // pushed last, so it is popped next
        }

        int maxDep = dep[bfs[n - 1]];
        depthStart.assign(maxDep + 2, 0), depthPos.assign(n, 0);
        for (int i = 0; i < n; i++) depthStart[dep[bfs[i]] + 1]++;
        for (int d = 0; d <= maxDep; d++) depthStart[d + 1] += depthStart[d];
        vector<int> slot(depthStart.begin(), depthStart.end() - 1);
        for (int i = 0; i < n; i++) depthPos[slot[dep[order[i]]]++] = i;
        if ((int)vals.size() != hi + 1)
            throw invalid_argument("Tree: vals[node] is node's value, so nodes " + nodes + " need vals.size() = " +
                                   to_string(hi + 1) + ", got " + to_string(vals.size()));
        vector<T> inOrder(n);
        for (int i = 0; i < n; i++) inOrder[i] = vals[order[i]];
        return inOrder;
    }

    // each edge's weight, at its lower end's position (the layout is built by the time this runs)
    template <typename E> vector<T> weights(const vector<vector<E>>& edges) {
        for (const auto& e : edges)
            if (e.size() != 3) throw invalid_argument("Tree: every edge needs its weight here, {a, b, w}");
        // (position 0 is the root's: it holds no edge and is never read)
        vector<T> inOrder(n, edges.empty() ? T(0) : (T)edges[0][2]);
        for (const auto& e : edges) {
            int a = (int)e[0], b = (int)e[1];
            inOrder[par[a] == b ? pos[a] : pos[b]] = (T)e[2];
        }
        return inOrder;
    }

    // O(log n) -- val(node)
    LEETCODE_NO_SANITIZE auto nodeGet(int node) {
        if (node < lo || node > hi) bad("nodeGet");
        return nodeSeg.pointGet(pos[node]);
    }

    // O(log n) -- val(node) = x
    LEETCODE_NO_SANITIZE void nodeAssign(int node, T x) {
        if (node < lo || node > hi) bad("nodeAssign");
        nodeSeg.pointAssign(pos[node], x);
    }

    // O(log n) -- val(node) += x
    LEETCODE_NO_SANITIZE void nodeAdd(int node, T x) {
        if (node < lo || node > hi) bad("nodeAdd");
        nodeSeg.pointAdd(pos[node], x);
    }

    // O(log n) -- val(node) = max(val, x)
    LEETCODE_NO_SANITIZE void nodeChmax(int node, T x) {
        if (node < lo || node > hi) bad("nodeChmax");
        nodeSeg.pointChmax(pos[node], x);
    }

    // O(log n) -- val(node) = min(val, x)
    LEETCODE_NO_SANITIZE void nodeChmin(int node, T x) {
        if (node < lo || node > hi) bad("nodeChmin");
        nodeSeg.pointChmin(pos[node], x);
    }

    // O(log^2 n) -- sum of the node values on the path a..b
    LEETCODE_NO_SANITIZE auto nodePathSum(int a, int b) {
        if (a < lo || a > hi || b < lo || b > hi) bad("nodePathSum");
        using R = decltype(nodeSeg.rangeSum(0, 0));
        R res = 0;
        while (head[a] != head[b]) {
            if (dep[head[a]] < dep[head[b]]) {
                int t = a;
                a = b, b = t;
            }
            R v = nodeSeg.rangeSum(pos[head[a]], pos[a]);
            res += v;
            a = par[head[a]];
        }
        int l = pos[a], r = pos[b];
        if (l > r) {
            int t = l;
            l = r, r = t;
        }
        R v = nodeSeg.rangeSum(l, r);
        res += v;
        return res;
    }

    // O(log^2 n) -- max node value on the path a..b
    LEETCODE_NO_SANITIZE auto nodePathMax(int a, int b) {
        if (a < lo || a > hi || b < lo || b > hi) bad("nodePathMax");
        using R = decltype(nodeSeg.rangeMax(0, 0));
        R res = numeric_limits<R>::lowest();
        while (head[a] != head[b]) {
            if (dep[head[a]] < dep[head[b]]) {
                int t = a;
                a = b, b = t;
            }
            R v = nodeSeg.rangeMax(pos[head[a]], pos[a]);
            if (v > res) res = v;
            a = par[head[a]];
        }
        int l = pos[a], r = pos[b];
        if (l > r) {
            int t = l;
            l = r, r = t;
        }
        R v = nodeSeg.rangeMax(l, r);
        if (v > res) res = v;
        return res;
    }

    // O(log^2 n) -- xor of the node values on the path a..b
    LEETCODE_NO_SANITIZE auto nodePathXOR(int a, int b) {
        if (a < lo || a > hi || b < lo || b > hi) bad("nodePathXOR");
        using R = decltype(nodeSeg.rangeXorQuery(0, 0));
        R res = 0;
        while (head[a] != head[b]) {
            if (dep[head[a]] < dep[head[b]]) {
                int t = a;
                a = b, b = t;
            }
            R v = nodeSeg.rangeXorQuery(pos[head[a]], pos[a]);
            res ^= v;
            a = par[head[a]];
        }
        int l = pos[a], r = pos[b];
        if (l > r) {
            int t = l;
            l = r, r = t;
        }
        R v = nodeSeg.rangeXorQuery(l, r);
        res ^= v;
        return res;
    }

    // O(log^2 n) -- OR of the node values on the path a..b
    LEETCODE_NO_SANITIZE auto nodePathOR(int a, int b) {
        if (a < lo || a > hi || b < lo || b > hi) bad("nodePathOR");
        using R = decltype(nodeSeg.rangeOrQuery(0, 0));
        R res = 0;
        while (head[a] != head[b]) {
            if (dep[head[a]] < dep[head[b]]) {
                int t = a;
                a = b, b = t;
            }
            R v = nodeSeg.rangeOrQuery(pos[head[a]], pos[a]);
            res |= v;
            a = par[head[a]];
        }
        int l = pos[a], r = pos[b];
        if (l > r) {
            int t = l;
            l = r, r = t;
        }
        R v = nodeSeg.rangeOrQuery(l, r);
        res |= v;
        return res;
    }

    // O(log^2 n) -- nearest ancestor of node (node included) with val >= x (-1 if none)
    LEETCODE_NO_SANITIZE int nodeNearestAncestorGteX(int node, T x) {
        if (node < lo || node > hi) bad("nodeNearestAncestorGteX");
        while (node != -1) {
            int i = nodeSeg.rightmostGteX(pos[head[node]], pos[node], x);
            if (i != -1) return order[i];
            node = par[head[node]];
        }
        return -1;
    }

    LEETCODE_NO_SANITIZE int nodeFirstGteX(int a, int b, T x) {
        int downs[64], m = 0;  // the chain pieces on b's side, bottom first (walked last, top first)
        while (head[a] != head[b]) {
            if (dep[head[a]] >= dep[head[b]]) {
                int l = pos[head[a]], r = pos[a];
                int i = nodeSeg.rightmostGteX(l, r, x);
                if (i != -1) return order[i];
                a = par[head[a]];
            } else {
                downs[m++] = b;
                b = par[head[b]];
            }
        }
        if (pos[a] >= pos[b]) {  // the piece holding the lca: b is the top
            int l = pos[b], r = pos[a];
            int i = nodeSeg.rightmostGteX(l, r, x);
            if (i != -1) return order[i];
        } else {
            int l = pos[a], r = pos[b];
            int i = nodeSeg.leftmostGteX(l, r, x);
            if (i != -1) return order[i];
        }
        while (m > 0) {
            int d = downs[--m], l = pos[head[d]], r = pos[d];
            int i = nodeSeg.leftmostGteX(l, r, x);
            if (i != -1) return order[i];
        }
        return -1;
    }

    // O(log^2 n) -- first node walking a -> b with val >= x (-1 if none)
    LEETCODE_NO_SANITIZE int nodePathFirstGteX(int a, int b, T x) {
        if (a < lo || a > hi || b < lo || b > hi) bad("nodePathFirstGteX");
        return nodeFirstGteX(a, b, x);
    }

    // O(log^2 n) -- last node walking a -> b with val >= x (-1 if none)
    LEETCODE_NO_SANITIZE int nodePathLastGteX(int a, int b, T x) {
        if (a < lo || a > hi || b < lo || b > hi) bad("nodePathLastGteX");
        return nodeFirstGteX(b, a, x);
    }

    // O(log^2 n) -- nearest ancestor of node (node included) with val > x (-1 if none)
    LEETCODE_NO_SANITIZE int nodeNearestAncestorGtX(int node, T x) {
        if (node < lo || node > hi) bad("nodeNearestAncestorGtX");
        while (node != -1) {
            int i = nodeSeg.rightmostGtX(pos[head[node]], pos[node], x);
            if (i != -1) return order[i];
            node = par[head[node]];
        }
        return -1;
    }

    LEETCODE_NO_SANITIZE int nodeFirstGtX(int a, int b, T x) {
        int downs[64], m = 0;  // the chain pieces on b's side, bottom first (walked last, top first)
        while (head[a] != head[b]) {
            if (dep[head[a]] >= dep[head[b]]) {
                int l = pos[head[a]], r = pos[a];
                int i = nodeSeg.rightmostGtX(l, r, x);
                if (i != -1) return order[i];
                a = par[head[a]];
            } else {
                downs[m++] = b;
                b = par[head[b]];
            }
        }
        if (pos[a] >= pos[b]) {  // the piece holding the lca: b is the top
            int l = pos[b], r = pos[a];
            int i = nodeSeg.rightmostGtX(l, r, x);
            if (i != -1) return order[i];
        } else {
            int l = pos[a], r = pos[b];
            int i = nodeSeg.leftmostGtX(l, r, x);
            if (i != -1) return order[i];
        }
        while (m > 0) {
            int d = downs[--m], l = pos[head[d]], r = pos[d];
            int i = nodeSeg.leftmostGtX(l, r, x);
            if (i != -1) return order[i];
        }
        return -1;
    }

    // O(log^2 n) -- first node walking a -> b with val > x (-1 if none)
    LEETCODE_NO_SANITIZE int nodePathFirstGtX(int a, int b, T x) {
        if (a < lo || a > hi || b < lo || b > hi) bad("nodePathFirstGtX");
        return nodeFirstGtX(a, b, x);
    }

    // O(log^2 n) -- last node walking a -> b with val > x (-1 if none)
    LEETCODE_NO_SANITIZE int nodePathLastGtX(int a, int b, T x) {
        if (a < lo || a > hi || b < lo || b > hi) bad("nodePathLastGtX");
        return nodeFirstGtX(b, a, x);
    }

    // O(log n) -- sum of the node values in node's subtree
    LEETCODE_NO_SANITIZE auto nodeSubtreeSum(int node) {
        if (node < lo || node > hi) bad("nodeSubtreeSum");
        int l = pos[node];
        return nodeSeg.rangeSum(l, l + sz[node] - 1);
    }

    // O(log n) -- max node value in node's subtree
    LEETCODE_NO_SANITIZE auto nodeSubtreeMax(int node) {
        if (node < lo || node > hi) bad("nodeSubtreeMax");
        int l = pos[node];
        return nodeSeg.rangeMax(l, l + sz[node] - 1);
    }

    // O(log n) -- xor of the node values in node's subtree
    LEETCODE_NO_SANITIZE auto nodeSubtreeXOR(int node) {
        if (node < lo || node > hi) bad("nodeSubtreeXOR");
        int l = pos[node];
        return nodeSeg.rangeXorQuery(l, l + sz[node] - 1);
    }

    // O(log n) -- OR of the node values in node's subtree
    LEETCODE_NO_SANITIZE auto nodeSubtreeOR(int node) {
        if (node < lo || node > hi) bad("nodeSubtreeOR");
        int l = pos[node];
        return nodeSeg.rangeOrQuery(l, l + sz[node] - 1);
    }

    // the position that holds the edge a - b: its lower end's (a and b in either order)
    LEETCODE_NO_SANITIZE int edgeAt(const char* name, int a, int b) const {
        if (a < lo || a > hi || b < lo || b > hi) bad(name);
        if (par[a] == b) return pos[a];
        if (par[b] == a) return pos[b];
        throw out_of_range(string(name) + ": needs an edge between a and b");
    }

    // O(log n) -- weight(a - b); a and b are the edge's two ends, in either order
    LEETCODE_NO_SANITIZE auto edgeGet(int a, int b) {
        return edgeSeg.pointGet(edgeAt("edgeGet", a, b));
    }

    // O(log n) -- weight(a - b) = w; a and b are the edge's two ends, in either order
    LEETCODE_NO_SANITIZE void edgeAssign(int a, int b, T w) {
        edgeSeg.pointAssign(edgeAt("edgeAssign", a, b), w);
    }

    // O(log n) -- weight(a - b) += w; a and b are the edge's two ends, in either order
    LEETCODE_NO_SANITIZE void edgeAdd(int a, int b, T w) {
        edgeSeg.pointAdd(edgeAt("edgeAdd", a, b), w);
    }

    // O(log n) -- weight(a - b) = max(weight, w); a and b are the edge's two ends, in either order
    LEETCODE_NO_SANITIZE void edgeChmax(int a, int b, T w) {
        edgeSeg.pointChmax(edgeAt("edgeChmax", a, b), w);
    }

    // O(log n) -- weight(a - b) = min(weight, w); a and b are the edge's two ends, in either order
    LEETCODE_NO_SANITIZE void edgeChmin(int a, int b, T w) {
        edgeSeg.pointChmin(edgeAt("edgeChmin", a, b), w);
    }

    // O(log^2 n) -- sum of the edge weights on the path a..b; 0 when a == b (no edges)
    LEETCODE_NO_SANITIZE auto edgePathSum(int a, int b) {
        if (a < lo || a > hi || b < lo || b > hi) bad("edgePathSum");
        using R = decltype(edgeSeg.rangeSum(0, 0));
        R res = 0;
        while (head[a] != head[b]) {
            if (dep[head[a]] < dep[head[b]]) {
                int t = a;
                a = b, b = t;
            }
            R v = edgeSeg.rangeSum(pos[head[a]], pos[a]);
            res += v;
            a = par[head[a]];
        }
        int l = pos[a], r = pos[b];
        if (l > r) {
            int t = l;
            l = r, r = t;
        }
        if (l < r) {  // (the lca's own position is the edge above it)
            R v = edgeSeg.rangeSum(l + 1, r);
            res += v;
        }
        return res;
    }

    // O(log^2 n) -- max edge weight on the path a..b; the smallest value of its type when a == b (no edges)
    LEETCODE_NO_SANITIZE auto edgePathMax(int a, int b) {
        if (a < lo || a > hi || b < lo || b > hi) bad("edgePathMax");
        using R = decltype(edgeSeg.rangeMax(0, 0));
        R res = numeric_limits<R>::lowest();
        while (head[a] != head[b]) {
            if (dep[head[a]] < dep[head[b]]) {
                int t = a;
                a = b, b = t;
            }
            R v = edgeSeg.rangeMax(pos[head[a]], pos[a]);
            if (v > res) res = v;
            a = par[head[a]];
        }
        int l = pos[a], r = pos[b];
        if (l > r) {
            int t = l;
            l = r, r = t;
        }
        if (l < r) {  // (the lca's own position is the edge above it)
            R v = edgeSeg.rangeMax(l + 1, r);
            if (v > res) res = v;
        }
        return res;
    }

    // O(log^2 n) -- xor of the edge weights on the path a..b; 0 when a == b (no edges)
    LEETCODE_NO_SANITIZE auto edgePathXOR(int a, int b) {
        if (a < lo || a > hi || b < lo || b > hi) bad("edgePathXOR");
        using R = decltype(edgeSeg.rangeXorQuery(0, 0));
        R res = 0;
        while (head[a] != head[b]) {
            if (dep[head[a]] < dep[head[b]]) {
                int t = a;
                a = b, b = t;
            }
            R v = edgeSeg.rangeXorQuery(pos[head[a]], pos[a]);
            res ^= v;
            a = par[head[a]];
        }
        int l = pos[a], r = pos[b];
        if (l > r) {
            int t = l;
            l = r, r = t;
        }
        if (l < r) {  // (the lca's own position is the edge above it)
            R v = edgeSeg.rangeXorQuery(l + 1, r);
            res ^= v;
        }
        return res;
    }

    // O(log^2 n) -- OR of the edge weights on the path a..b; 0 when a == b (no edges)
    LEETCODE_NO_SANITIZE auto edgePathOR(int a, int b) {
        if (a < lo || a > hi || b < lo || b > hi) bad("edgePathOR");
        using R = decltype(edgeSeg.rangeOrQuery(0, 0));
        R res = 0;
        while (head[a] != head[b]) {
            if (dep[head[a]] < dep[head[b]]) {
                int t = a;
                a = b, b = t;
            }
            R v = edgeSeg.rangeOrQuery(pos[head[a]], pos[a]);
            res |= v;
            a = par[head[a]];
        }
        int l = pos[a], r = pos[b];
        if (l > r) {
            int t = l;
            l = r, r = t;
        }
        if (l < r) {  // (the lca's own position is the edge above it)
            R v = edgeSeg.rangeOrQuery(l + 1, r);
            res |= v;
        }
        return res;
    }

    // O(log^2 n) -- nearest edge above node (toward the root) with weight >= x, as its lower end (-1 if none)
    LEETCODE_NO_SANITIZE int edgeNearestAncestorGteX(int node, T x) {
        if (node < lo || node > hi) bad("edgeNearestAncestorGteX");
        while (node != -1) {
            int l = pos[head[node]] ? pos[head[node]] : 1;  // (position 0 is the root's: it holds no edge)
            if (l <= pos[node]) {
                int i = edgeSeg.rightmostGteX(l, pos[node], x);
                if (i != -1) return order[i];
            }
            node = par[head[node]];
        }
        return -1;
    }

    LEETCODE_NO_SANITIZE int edgeFirstGteX(int a, int b, T x) {
        int downs[64], m = 0;  // the chain pieces on b's side, bottom first (walked last, top first)
        while (head[a] != head[b]) {
            if (dep[head[a]] >= dep[head[b]]) {
                int l = pos[head[a]], r = pos[a];
                int i = edgeSeg.rightmostGteX(l, r, x);
                if (i != -1) return order[i];
                a = par[head[a]];
            } else {
                downs[m++] = b;
                b = par[head[b]];
            }
        }
        if (pos[a] > pos[b]) {  // the piece holding the lca (b): its edges sit after the lca's position
            int l = pos[b] + 1, r = pos[a];
            int i = edgeSeg.rightmostGteX(l, r, x);
            if (i != -1) return order[i];
        } else if (pos[a] < pos[b]) {
            int l = pos[a] + 1, r = pos[b];
            int i = edgeSeg.leftmostGteX(l, r, x);
            if (i != -1) return order[i];
        }
        while (m > 0) {
            int d = downs[--m], l = pos[head[d]], r = pos[d];
            int i = edgeSeg.leftmostGteX(l, r, x);
            if (i != -1) return order[i];
        }
        return -1;
    }

    // O(log^2 n) -- first edge walking a -> b with weight >= x, as its lower end (-1 if none)
    LEETCODE_NO_SANITIZE int edgePathFirstGteX(int a, int b, T x) {
        if (a < lo || a > hi || b < lo || b > hi) bad("edgePathFirstGteX");
        return edgeFirstGteX(a, b, x);
    }

    // O(log^2 n) -- last edge walking a -> b with weight >= x, as its lower end (-1 if none)
    LEETCODE_NO_SANITIZE int edgePathLastGteX(int a, int b, T x) {
        if (a < lo || a > hi || b < lo || b > hi) bad("edgePathLastGteX");
        return edgeFirstGteX(b, a, x);
    }

    // O(log^2 n) -- nearest edge above node (toward the root) with weight > x, as its lower end (-1 if none)
    LEETCODE_NO_SANITIZE int edgeNearestAncestorGtX(int node, T x) {
        if (node < lo || node > hi) bad("edgeNearestAncestorGtX");
        while (node != -1) {
            int l = pos[head[node]] ? pos[head[node]] : 1;  // (position 0 is the root's: it holds no edge)
            if (l <= pos[node]) {
                int i = edgeSeg.rightmostGtX(l, pos[node], x);
                if (i != -1) return order[i];
            }
            node = par[head[node]];
        }
        return -1;
    }

    LEETCODE_NO_SANITIZE int edgeFirstGtX(int a, int b, T x) {
        int downs[64], m = 0;  // the chain pieces on b's side, bottom first (walked last, top first)
        while (head[a] != head[b]) {
            if (dep[head[a]] >= dep[head[b]]) {
                int l = pos[head[a]], r = pos[a];
                int i = edgeSeg.rightmostGtX(l, r, x);
                if (i != -1) return order[i];
                a = par[head[a]];
            } else {
                downs[m++] = b;
                b = par[head[b]];
            }
        }
        if (pos[a] > pos[b]) {  // the piece holding the lca (b): its edges sit after the lca's position
            int l = pos[b] + 1, r = pos[a];
            int i = edgeSeg.rightmostGtX(l, r, x);
            if (i != -1) return order[i];
        } else if (pos[a] < pos[b]) {
            int l = pos[a] + 1, r = pos[b];
            int i = edgeSeg.leftmostGtX(l, r, x);
            if (i != -1) return order[i];
        }
        while (m > 0) {
            int d = downs[--m], l = pos[head[d]], r = pos[d];
            int i = edgeSeg.leftmostGtX(l, r, x);
            if (i != -1) return order[i];
        }
        return -1;
    }

    // O(log^2 n) -- first edge walking a -> b with weight > x, as its lower end (-1 if none)
    LEETCODE_NO_SANITIZE int edgePathFirstGtX(int a, int b, T x) {
        if (a < lo || a > hi || b < lo || b > hi) bad("edgePathFirstGtX");
        return edgeFirstGtX(a, b, x);
    }

    // O(log^2 n) -- last edge walking a -> b with weight > x, as its lower end (-1 if none)
    LEETCODE_NO_SANITIZE int edgePathLastGtX(int a, int b, T x) {
        if (a < lo || a > hi || b < lo || b > hi) bad("edgePathLastGtX");
        return edgeFirstGtX(b, a, x);
    }

    // O(log n) -- sum of the edge weights in node's subtree; 0 when node is a leaf (no edges)
    LEETCODE_NO_SANITIZE auto edgeSubtreeSum(int node) {
        if (node < lo || node > hi) bad("edgeSubtreeSum");
        int l = pos[node] + 1, r = pos[node] + sz[node] - 1;  // (l > r for a leaf: no edges below it)
        using R = decltype(edgeSeg.rangeSum(0, 0));
        if (l > r) return R(0);
        return edgeSeg.rangeSum(l, r);
    }

    // O(log n) -- max edge weight in node's subtree; the smallest value of its type when node is a leaf (no edges)
    LEETCODE_NO_SANITIZE auto edgeSubtreeMax(int node) {
        if (node < lo || node > hi) bad("edgeSubtreeMax");
        int l = pos[node] + 1, r = pos[node] + sz[node] - 1;  // (l > r for a leaf: no edges below it)
        using R = decltype(edgeSeg.rangeMax(0, 0));
        if (l > r) return numeric_limits<R>::lowest();
        return edgeSeg.rangeMax(l, r);
    }

    // O(log n) -- xor of the edge weights in node's subtree; 0 when node is a leaf (no edges)
    LEETCODE_NO_SANITIZE auto edgeSubtreeXOR(int node) {
        if (node < lo || node > hi) bad("edgeSubtreeXOR");
        int l = pos[node] + 1, r = pos[node] + sz[node] - 1;  // (l > r for a leaf: no edges below it)
        using R = decltype(edgeSeg.rangeXorQuery(0, 0));
        if (l > r) return R(0);
        return edgeSeg.rangeXorQuery(l, r);
    }

    // O(log n) -- OR of the edge weights in node's subtree; 0 when node is a leaf (no edges)
    LEETCODE_NO_SANITIZE auto edgeSubtreeOR(int node) {
        if (node < lo || node > hi) bad("edgeSubtreeOR");
        int l = pos[node] + 1, r = pos[node] + sz[node] - 1;  // (l > r for a leaf: no edges below it)
        using R = decltype(edgeSeg.rangeOrQuery(0, 0));
        if (l > r) return R(0);
        return edgeSeg.rangeOrQuery(l, r);
    }

    [[noreturn]] void bad(const char* name) const {
        throw out_of_range(string(name) + ": needs " + to_string(lo) + " <= node <= " + to_string(hi));
    }

    LEETCODE_NO_SANITIZE int lcaOf(int a, int b) const {
        while (head[a] != head[b]) {
            if (dep[head[a]] > dep[head[b]]) a = par[head[a]];
            else b = par[head[b]];
        }
        return dep[a] < dep[b] ? a : b;
    }

    // the node k steps above node (k <= its depth): a whole chain at a time
    LEETCODE_NO_SANITIZE int kthOf(int node, int k) const {
        while (true) {
            int h = head[node], d = pos[node] - pos[h];
            if (k <= d) return order[pos[node] - k];
            k -= d + 1;
            node = par[h];
        }
    }

    LEETCODE_NO_SANITIZE int distOf(int a, int b) const { return dep[a] + dep[b] - 2 * dep[lcaOf(a, b)]; }

    // of the three pairwise lcas two are equal and the third, the deeper one, is the median
    LEETCODE_NO_SANITIZE int medianOf(int a, int b, int c) const {
        int x = lcaOf(a, b), y = lcaOf(a, c), z = lcaOf(b, c);
        if (dep[y] > dep[x]) x = y;
        return dep[z] > dep[x] ? z : x;
    }

    LEETCODE_NO_SANITIZE bool above(int a, int b) const { return pos[a] <= pos[b] && pos[b] < pos[a] + sz[a]; }

    LEETCODE_NO_SANITIZE bool onPath(int a, int b, int node) const {
        return above(lcaOf(a, b), node) && (above(node, a) || above(node, b));
    }

    // the neighbor of a on the way to b (a != b): the child holding b when b is below a, else a's parent
    LEETCODE_NO_SANITIZE int nextOf(int a, int b) const {
        return above(a, b) ? kthOf(b, dep[b] - dep[a] - 1) : par[a];
    }

    LEETCODE_NO_SANITIZE int lowerPos(int s, int e, int x) const {  // first index in [s, e) with depthPos >= x
        while (s < e) {
            int m = (s + e) >> 1;
            if (depthPos[m] < x) s = m + 1;
            else e = m;
        }
        return s;
    }

    // O(log n) -- lowest common ancestor of a and b
    LEETCODE_NO_SANITIZE int lca(int a, int b) const {
        if (a < lo || a > hi || b < lo || b > hi) bad("lca");
        return lcaOf(a, b);
    }

    // O(log n) -- number of edges on the path a..b
    LEETCODE_NO_SANITIZE int unweightedDist(int a, int b) const {
        if (a < lo || a > hi || b < lo || b > hi) bad("unweightedDist");
        return distOf(a, b);
    }

    // O(1) -- edges from the root to node (the root is depth 0)
    LEETCODE_NO_SANITIZE int depth(int node) const {
        if (node < lo || node > hi) bad("depth");
        return dep[node];
    }

    // O(1) -- node's parent (-1 for the root)
    LEETCODE_NO_SANITIZE int parent(int node) const {
        if (node < lo || node > hi) bad("parent");
        return par[node];
    }

    // O(log n) -- the node k steps above node (k = 0 is node itself; -1 if that is past the root); needs k >= 0
    LEETCODE_NO_SANITIZE int kthAncestor(int node, int k) const {
        if (node < lo || node > hi) bad("kthAncestor");
        if (k < 0) throw out_of_range("kthAncestor: needs k >= 0");
        return k <= dep[node] ? kthOf(node, k) : -1;
    }

    // O(1) -- is a an ancestor of b? (true when a == b)
    LEETCODE_NO_SANITIZE bool isAncestor(int a, int b) const {
        if (a < lo || a > hi || b < lo || b > hi) bad("isAncestor");
        return above(a, b);
    }

    // O(1) -- number of nodes in node's subtree (node included)
    LEETCODE_NO_SANITIZE int subtreeSize(int node) const {
        if (node < lo || node > hi) bad("subtreeSize");
        return sz[node];
    }

    // O(log n) -- number of nodes in node's subtree at depth d (the root is depth 0); 0 when there are none
    LEETCODE_NO_SANITIZE int countAtDepthInSubtree(int node, int d) const {
        if (node < lo || node > hi) bad("countAtDepthInSubtree");
        if (d < 0 || d + 1 >= (int)depthStart.size()) return 0;
        int s = depthStart[d], e = depthStart[d + 1], l = pos[node];
        return lowerPos(s, e, l + sz[node]) - lowerPos(s, e, l);
    }

    // O(log n) -- lca of a and b if the tree were rooted at r instead
    LEETCODE_NO_SANITIZE int lcaRootedAt(int r, int a, int b) const {
        if (r < lo || r > hi || a < lo || a > hi || b < lo || b > hi) bad("lcaRootedAt");
        return medianOf(a, b, r);
    }

    // O(log n) -- node's parent if the tree were rooted at r (-1 when node == r)
    LEETCODE_NO_SANITIZE int parentRootedAt(int r, int node) const {
        if (r < lo || r > hi || node < lo || node > hi) bad("parentRootedAt");
        return node == r ? -1 : nextOf(node, r);
    }

    // O(log n) -- size of node's subtree if the tree were rooted at r
    LEETCODE_NO_SANITIZE int subtreeSizeRootedAt(int r, int node) const {
        if (r < lo || r > hi || node < lo || node > hi) bad("subtreeSizeRootedAt");
        if (node == r) return n;
        // r hangs below node: everything but the child holding r
        if (above(node, r)) return n - sz[kthOf(r, dep[r] - dep[node] - 1)];
        return sz[node];
    }

    // O(log n) -- the kth node walking a -> b (k = 0 is a, k = unweightedDist(a, b) is b; -1 if k is past b); needs
    // k >= 0
    LEETCODE_NO_SANITIZE int kthNodeOnPath(int a, int b, int k) const {
        if (a < lo || a > hi || b < lo || b > hi) bad("kthNodeOnPath");
        if (k < 0) throw out_of_range("kthNodeOnPath: needs k >= 0");
        int c = lcaOf(a, b), up = dep[a] - dep[c], total = up + dep[b] - dep[c];
        if (k > total) return -1;
        return k <= up ? kthOf(a, k) : kthOf(b, total - k);
    }

    // O(log n) -- the neighbor of a one step toward b (-1 if a == b)
    LEETCODE_NO_SANITIZE int nextNodeOnPath(int a, int b) const {
        if (a < lo || a > hi || b < lo || b > hi) bad("nextNodeOnPath");
        return a == b ? -1 : nextOf(a, b);
    }

    // O(log n) -- does the path a..b pass through node? (a and b count)
    LEETCODE_NO_SANITIZE bool isOnPath(int a, int b, int node) const {
        if (a < lo || a > hi || b < lo || b > hi || node < lo || node > hi) bad("isOnPath");
        return onPath(a, b, node);
    }

    // O(log n) -- fewest edges from node to any node on the path a..b (0 if node is on it)
    LEETCODE_NO_SANITIZE int unweightedDistToPath(int a, int b, int node) const {
        if (a < lo || a > hi || b < lo || b > hi || node < lo || node > hi) bad("unweightedDistToPath");
        return distOf(node, medianOf(a, b, node));
    }

    // O(log n) -- fewest edges between any node on path a..b and any node on path c..d (0 if they share a node)
    LEETCODE_NO_SANITIZE int unweightedDistBetweenPaths(int a, int b, int c, int d) const {
        if (a < lo || a > hi || b < lo || b > hi || c < lo || c > hi || d < lo || d > hi)
            bad("unweightedDistBetweenPaths");
        int p = medianOf(a, b, c);  // where c's side meets the path a..b
        if (p != medianOf(a, b, d)) return 0;  // c and d meet it at different nodes, so c..d runs along it
        return distOf(p, medianOf(c, d, p));
    }

    // O(log n) -- the one node that lies on all three paths between a, b and c
    LEETCODE_NO_SANITIZE int median(int a, int b, int c) const {
        if (a < lo || a > hi || b < lo || b > hi || c < lo || c > hi) bad("median");
        return medianOf(a, b, c);
    }

    // O(log n) -- the shared part of paths a..b and c..d as its two end nodes {p, q}, p first walking a -> b; p == q
    // if they share one node; {-1, -1} if they share none
    LEETCODE_NO_SANITIZE pair<int, int> pathIntersection(int a, int b, int c, int d) const {
        if (a < lo || a > hi || b < lo || b > hi || c < lo || c > hi || d < lo || d > hi) bad("pathIntersection");
        int p = medianOf(a, b, c), q = medianOf(a, b, d);  // where c's side and d's side meet the path a..b
        if (p == q) return onPath(c, d, p) ? pair<int, int>{p, p} : pair<int, int>{-1, -1};
        return distOf(a, p) < distOf(a, q) ? pair<int, int>{p, q} : pair<int, int>{q, p};
    }

    // O(K + log n) -- every node on the path a..b, in order from a (K = how many)
    LEETCODE_NO_SANITIZE vector<int> pathNodes(int a, int b) const {
        if (a < lo || a > hi || b < lo || b > hi) bad("pathNodes");
        int c = lcaOf(a, b), up = dep[a] - dep[c], len = up + dep[b] - dep[c] + 1;
        vector<int> out(len);
        int* p = out.data();
        for (int i = 0; a != c; a = par[a]) p[i++] = a;
        p[up] = c;
        for (int i = len - 1; b != c; b = par[b]) p[i--] = b;
        return out;
    }
};
