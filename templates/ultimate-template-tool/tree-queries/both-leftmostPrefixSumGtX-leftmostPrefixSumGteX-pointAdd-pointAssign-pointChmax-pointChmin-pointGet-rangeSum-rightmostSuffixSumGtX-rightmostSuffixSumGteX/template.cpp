// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/tree-queries/both-leftmostPrefixSumGtX-leftmostPrefixSumGteX-pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeSum-rightmostSuffixSumGtX-rightmostSuffixSumGteX/template.cpp
// The range structure inside is https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/leftmostPrefixSumGtX-leftmostPrefixSumGteX-pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeSum-rightmostSuffixSumGtX-rightmostSuffixSumGteX/fast.cpp
// @operations: countAtDepthInSubtree depth edgeAdd edgeAssign edgeChmax edgeChmin edgeGet edgePathFirstPrefixSumGtX edgePathFirstPrefixSumGteX edgePathLastSuffixSumGtX edgePathLastSuffixSumGteX edgePathSum edgeSubtreeSum isAncestor isOnPath kthAncestor kthNodeOnPath lca lcaRootedAt median nextNodeOnPath nodeAdd nodeAssign nodeChmax nodeChmin nodeGet nodePathFirstPrefixSumGtX nodePathFirstPrefixSumGteX nodePathLastSuffixSumGtX nodePathLastSuffixSumGteX nodePathSum nodeSubtreeSum parent parentRootedAt pathIntersection pathNodes subtreeSize subtreeSizeRootedAt unweightedDist unweightedDistBetweenPaths unweightedDistToPath
// @data-structure-type: BIT
// @complexities:
//   countAtDepthInSubtree: log(N)
//   depth: 1
//   edgeAdd: log(N)
//   edgeAssign: log(N)
//   edgeChmax: log(N)
//   edgeChmin: log(N)
//   edgeGet: log(N)
//   edgePathFirstPrefixSumGtX: log^2(N)
//   edgePathFirstPrefixSumGteX: log^2(N)
//   edgePathLastSuffixSumGtX: log^2(N)
//   edgePathLastSuffixSumGteX: log^2(N)
//   edgePathSum: log^2(N)
//   edgeSubtreeSum: log(N)
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
//   nodePathFirstPrefixSumGtX: log^2(N)
//   nodePathFirstPrefixSumGteX: log^2(N)
//   nodePathLastSuffixSumGtX: log^2(N)
//   nodePathLastSuffixSumGteX: log^2(N)
//   nodePathSum: log^2(N)
//   nodeSubtreeSum: log(N)
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
//   layout: none
//   node: tree[2*N]
//   tags: none
//   other: par[1*N] dep[1*N] sz[1*N] head[1*N] pos[1*N] order[1*N] depthPos[1*N] depthStart[1*N]
//   note: the prefix / suffix-sum searches binary-lift over the tree, so they need every a[i] >= 0
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// FAST MODE (this is the only C++ version): sanitizers are skipped inside this template, so a bad access in it goes
// unreported. To turn that off (say, when debugging with sanitizers), put this line above the template:
//   #define LEETCODE_NO_SANITIZE
// Without sanitizers (Codeforces, a plain -O2 build) it changes nothing. It needs GCC or Clang.

// Point add, range sum (Fenwick tree). All indices 0-based, ranges inclusive [l, r]. T: int, long long, ...
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
struct BIT {
    int n;
    HotVector<T> tree;  // 1-indexed

    // O(N) -- push each node into its parent once
    explicit BIT(const vector<T>& a) : n((int)a.size()), tree(n + 1) {
        for (int i = 1; i <= n; i++) tree[i] = a[i - 1];
        for (int i = 1; i <= n; i++) {
            int j = i + (i & -i);
            if (j <= n) tree[j] += tree[i];
        }
    }

    // O(logN) -- a[i] += delta; needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAdd(int i, T delta) {
        if (i < 0 || i >= n) throw out_of_range("pointAdd: needs 0 <= i < n");
        for (i++; i <= n; i += i & -i) tree[i] += delta;
    }

    // O(logN) -- a[0] + ... + a[i]
    LEETCODE_NO_SANITIZE T prefixSum(int i) const {
        T s = 0;
        for (i++; i > 0; i &= i - 1) s += tree[i];
        return s;
    }

    // O(logN) -- a[l] + ... + a[r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE T rangeSum(int l, int r) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeSum: needs 0 <= l <= r < n");
        return l > r ? T(0) : prefixSum(r) - (l ? prefixSum(l - 1) : T(0));
    }

    // O(logN) -- a[i] in one walk instead of two prefix sums; needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE T pointGet(int i) const {
        if (i < 0 || i >= n) throw out_of_range("pointGet: needs 0 <= i < n");
        i++;
        T v = tree[i];
        int stop = i - (i & -i);
        for (i--; i > stop; i &= i - 1) v -= tree[i];
        return v;
    }

    // O(N) -- the whole array: undo the Fenwick sums on a copy (last index first: entry i was added into
    // i + lowbit(i) once complete)
    LEETCODE_NO_SANITIZE vector<T> getAll() const {
        vector<T> t(tree);
        for (int i = n; i > 0; i--) {
            int j = i + (i & -i);
            if (j <= n) t[j] -= t[i];
        }
        return vector<T>(t.begin() + 1, t.end());
    }

    // O(logN) -- a[i] = v; needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAssign(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointAssign: needs 0 <= i < n");
        pointAdd(i, v - pointGet(i));
    }

    // O(logN) -- a[i] = max(a[i], v); needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointChmax(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointChmax: needs 0 <= i < n");
        T cur = pointGet(i);
        if (v > cur) pointAdd(i, v - cur);
    }

    // O(logN) -- a[i] = min(a[i], v); needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointChmin(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointChmin: needs 0 <= i < n");
        T cur = pointGet(i);
        if (v < cur) pointAdd(i, v - cur);
    }

    // O(logN) -- smallest i with a[0] + ... + a[i] >= target (> target if strict), or n if none.
    // Binary lifting: grow pos by powers of two while the prefix stays below target. Needs every a[i] >= 0.
    LEETCODE_NO_SANITIZE int prefixLowerBound(T target, bool strict) const {
        int pos = 0;
        T acc = 0;
        for (int step = n ? 1 << (31 - __builtin_clz(n)) : 0; step; step >>= 1) {
            int nxt = pos + step;
            if (nxt <= n) {
                T v = acc + tree[nxt];
                if (v < target || (strict && v == target)) pos = nxt, acc = v;
            }
        }
        return pos;
    }

    // O(logN) -- first i in [l, r] with a[l] + ... + a[i] >= x, or -1. Needs every a[i] >= 0. e.g. on a 0/1 array,
    // leftmostPrefixSumGteX(0, n - 1, k) is the index of the k-th one.; needs 0 <= l <= r < n, else throws
    // out_of_range
    LEETCODE_NO_SANITIZE int leftmostPrefixSumGteX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("leftmostPrefixSumGteX: needs 0 <= l <= r < n");
        int i = max(l, prefixLowerBound((l ? prefixSum(l - 1) : T(0)) + x, false));
        return i <= r ? i : -1;
    }

    // O(logN) -- first i in [l, r] with a[l] + ... + a[i] > x, or -1. Needs every a[i] >= 0.; needs 0 <= l <= r < n,
    // else throws out_of_range
    LEETCODE_NO_SANITIZE int leftmostPrefixSumGtX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("leftmostPrefixSumGtX: needs 0 <= l <= r < n");
        int i = max(l, prefixLowerBound((l ? prefixSum(l - 1) : T(0)) + x, true));
        return i <= r ? i : -1;
    }

    // O(logN) -- last i in [l, r] with a[i] + ... + a[r] >= x, or -1. Needs every a[i] >= 0. That is the last i with
    // a[0] + ... + a[i - 1] <= prefixSum(r) - x: one binary lift.; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE int rightmostSuffixSumGteX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("rightmostSuffixSumGteX: needs 0 <= l <= r < n");
        T t = prefixSum(r) - x;
        if (t < 0) return -1;
        int i = min(r, prefixLowerBound(t, true));
        return i >= l ? i : -1;
    }

    // O(logN) -- last i in [l, r] with a[i] + ... + a[r] > x, or -1. Needs every a[i] >= 0.; needs 0 <= l <= r < n,
    // else throws out_of_range
    LEETCODE_NO_SANITIZE int rightmostSuffixSumGtX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("rightmostSuffixSumGtX: needs 0 <= l <= r < n");
        T t = prefixSum(r) - x;
        if (t <= 0) return -1;
        int i = min(r, prefixLowerBound(t, false));
        return i >= l ? i : -1;
    }

    // O(log(N)) -- sum of the whole array a[0..n-1] (rangeSum(0, n - 1)); needs n >= 1, else throws out_of_range
    LEETCODE_NO_SANITIZE auto sumAll() {
        if (n < 1) throw out_of_range("sumAll: needs n >= 1");
        return rangeSum(0, n - 1);
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
// stretch of positions (pos[node] .. pos[node] + sz[node] - 1). Two copies of the range structure above (BIT) sit over
// those positions: nodeSeg holds each node's value at its position, edgeSeg each edge's weight at its lower end's
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
    BIT<T> nodeSeg;  // the node values, in position order
    BIT<T> edgeSeg;  // each edge's weight, at its lower end's position

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

    LEETCODE_NO_SANITIZE int nodeFirstPrefixSumGteX(int a, int b, T x) {
        decltype(nodeSeg.rangeSum(0, 0)) run = 0;  // the sum of the pieces already walked
        int downs[64], m = 0;  // the chain pieces on b's side, bottom first (walked last, top first)
        while (head[a] != head[b]) {
            if (dep[head[a]] >= dep[head[b]]) {
                int l = pos[head[a]], r = pos[a];
                int i = nodeSeg.rightmostSuffixSumGteX(l, r, x - run);
                if (i != -1) return order[i];
                run += nodeSeg.rangeSum(l, r);
                a = par[head[a]];
            } else {
                downs[m++] = b;
                b = par[head[b]];
            }
        }
        if (pos[a] >= pos[b]) {  // the piece holding the lca: b is the top
            int l = pos[b], r = pos[a];
            int i = nodeSeg.rightmostSuffixSumGteX(l, r, x - run);
            if (i != -1) return order[i];
            run += nodeSeg.rangeSum(l, r);
        } else {
            int l = pos[a], r = pos[b];
            int i = nodeSeg.leftmostPrefixSumGteX(l, r, x - run);
            if (i != -1) return order[i];
            run += nodeSeg.rangeSum(l, r);
        }
        while (m > 0) {
            int d = downs[--m], l = pos[head[d]], r = pos[d];
            int i = nodeSeg.leftmostPrefixSumGteX(l, r, x - run);
            if (i != -1) return order[i];
            run += nodeSeg.rangeSum(l, r);
        }
        return -1;
    }

    // O(log^2 n) -- first node walking a -> b where the sum from a to it is >= x (-1 if none) (needs every val >= 0)
    LEETCODE_NO_SANITIZE int nodePathFirstPrefixSumGteX(int a, int b, T x) {
        if (a < lo || a > hi || b < lo || b > hi) bad("nodePathFirstPrefixSumGteX");
        return nodeFirstPrefixSumGteX(a, b, x);
    }

    // O(log^2 n) -- last node walking a -> b where the sum from it to b is >= x (-1 if none) (needs every val >= 0)
    LEETCODE_NO_SANITIZE int nodePathLastSuffixSumGteX(int a, int b, T x) {
        if (a < lo || a > hi || b < lo || b > hi) bad("nodePathLastSuffixSumGteX");
        return nodeFirstPrefixSumGteX(b, a, x);
    }

    LEETCODE_NO_SANITIZE int nodeFirstPrefixSumGtX(int a, int b, T x) {
        decltype(nodeSeg.rangeSum(0, 0)) run = 0;  // the sum of the pieces already walked
        int downs[64], m = 0;  // the chain pieces on b's side, bottom first (walked last, top first)
        while (head[a] != head[b]) {
            if (dep[head[a]] >= dep[head[b]]) {
                int l = pos[head[a]], r = pos[a];
                int i = nodeSeg.rightmostSuffixSumGtX(l, r, x - run);
                if (i != -1) return order[i];
                run += nodeSeg.rangeSum(l, r);
                a = par[head[a]];
            } else {
                downs[m++] = b;
                b = par[head[b]];
            }
        }
        if (pos[a] >= pos[b]) {  // the piece holding the lca: b is the top
            int l = pos[b], r = pos[a];
            int i = nodeSeg.rightmostSuffixSumGtX(l, r, x - run);
            if (i != -1) return order[i];
            run += nodeSeg.rangeSum(l, r);
        } else {
            int l = pos[a], r = pos[b];
            int i = nodeSeg.leftmostPrefixSumGtX(l, r, x - run);
            if (i != -1) return order[i];
            run += nodeSeg.rangeSum(l, r);
        }
        while (m > 0) {
            int d = downs[--m], l = pos[head[d]], r = pos[d];
            int i = nodeSeg.leftmostPrefixSumGtX(l, r, x - run);
            if (i != -1) return order[i];
            run += nodeSeg.rangeSum(l, r);
        }
        return -1;
    }

    // O(log^2 n) -- first node walking a -> b where the sum from a to it is > x (-1 if none) (needs every val >= 0)
    LEETCODE_NO_SANITIZE int nodePathFirstPrefixSumGtX(int a, int b, T x) {
        if (a < lo || a > hi || b < lo || b > hi) bad("nodePathFirstPrefixSumGtX");
        return nodeFirstPrefixSumGtX(a, b, x);
    }

    // O(log^2 n) -- last node walking a -> b where the sum from it to b is > x (-1 if none) (needs every val >= 0)
    LEETCODE_NO_SANITIZE int nodePathLastSuffixSumGtX(int a, int b, T x) {
        if (a < lo || a > hi || b < lo || b > hi) bad("nodePathLastSuffixSumGtX");
        return nodeFirstPrefixSumGtX(b, a, x);
    }

    // O(log n) -- sum of the node values in node's subtree
    LEETCODE_NO_SANITIZE auto nodeSubtreeSum(int node) {
        if (node < lo || node > hi) bad("nodeSubtreeSum");
        int l = pos[node];
        return nodeSeg.rangeSum(l, l + sz[node] - 1);
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

    LEETCODE_NO_SANITIZE int edgeFirstPrefixSumGteX(int a, int b, T x) {
        decltype(edgeSeg.rangeSum(0, 0)) run = 0;  // the sum of the pieces already walked
        int downs[64], m = 0;  // the chain pieces on b's side, bottom first (walked last, top first)
        while (head[a] != head[b]) {
            if (dep[head[a]] >= dep[head[b]]) {
                int l = pos[head[a]], r = pos[a];
                int i = edgeSeg.rightmostSuffixSumGteX(l, r, x - run);
                if (i != -1) return order[i];
                run += edgeSeg.rangeSum(l, r);
                a = par[head[a]];
            } else {
                downs[m++] = b;
                b = par[head[b]];
            }
        }
        if (pos[a] > pos[b]) {  // the piece holding the lca (b): its edges sit after the lca's position
            int l = pos[b] + 1, r = pos[a];
            int i = edgeSeg.rightmostSuffixSumGteX(l, r, x - run);
            if (i != -1) return order[i];
            run += edgeSeg.rangeSum(l, r);
        } else if (pos[a] < pos[b]) {
            int l = pos[a] + 1, r = pos[b];
            int i = edgeSeg.leftmostPrefixSumGteX(l, r, x - run);
            if (i != -1) return order[i];
            run += edgeSeg.rangeSum(l, r);
        }
        while (m > 0) {
            int d = downs[--m], l = pos[head[d]], r = pos[d];
            int i = edgeSeg.leftmostPrefixSumGteX(l, r, x - run);
            if (i != -1) return order[i];
            run += edgeSeg.rangeSum(l, r);
        }
        return -1;
    }

    // O(log^2 n) -- first edge walking a -> b where the sum from a to it is >= x, as its lower end (-1 if none) (needs
    // every weight >= 0)
    LEETCODE_NO_SANITIZE int edgePathFirstPrefixSumGteX(int a, int b, T x) {
        if (a < lo || a > hi || b < lo || b > hi) bad("edgePathFirstPrefixSumGteX");
        return edgeFirstPrefixSumGteX(a, b, x);
    }

    // O(log^2 n) -- last edge walking a -> b where the sum from it to b is >= x, as its lower end (-1 if none) (needs
    // every weight >= 0)
    LEETCODE_NO_SANITIZE int edgePathLastSuffixSumGteX(int a, int b, T x) {
        if (a < lo || a > hi || b < lo || b > hi) bad("edgePathLastSuffixSumGteX");
        return edgeFirstPrefixSumGteX(b, a, x);
    }

    LEETCODE_NO_SANITIZE int edgeFirstPrefixSumGtX(int a, int b, T x) {
        decltype(edgeSeg.rangeSum(0, 0)) run = 0;  // the sum of the pieces already walked
        int downs[64], m = 0;  // the chain pieces on b's side, bottom first (walked last, top first)
        while (head[a] != head[b]) {
            if (dep[head[a]] >= dep[head[b]]) {
                int l = pos[head[a]], r = pos[a];
                int i = edgeSeg.rightmostSuffixSumGtX(l, r, x - run);
                if (i != -1) return order[i];
                run += edgeSeg.rangeSum(l, r);
                a = par[head[a]];
            } else {
                downs[m++] = b;
                b = par[head[b]];
            }
        }
        if (pos[a] > pos[b]) {  // the piece holding the lca (b): its edges sit after the lca's position
            int l = pos[b] + 1, r = pos[a];
            int i = edgeSeg.rightmostSuffixSumGtX(l, r, x - run);
            if (i != -1) return order[i];
            run += edgeSeg.rangeSum(l, r);
        } else if (pos[a] < pos[b]) {
            int l = pos[a] + 1, r = pos[b];
            int i = edgeSeg.leftmostPrefixSumGtX(l, r, x - run);
            if (i != -1) return order[i];
            run += edgeSeg.rangeSum(l, r);
        }
        while (m > 0) {
            int d = downs[--m], l = pos[head[d]], r = pos[d];
            int i = edgeSeg.leftmostPrefixSumGtX(l, r, x - run);
            if (i != -1) return order[i];
            run += edgeSeg.rangeSum(l, r);
        }
        return -1;
    }

    // O(log^2 n) -- first edge walking a -> b where the sum from a to it is > x, as its lower end (-1 if none) (needs
    // every weight >= 0)
    LEETCODE_NO_SANITIZE int edgePathFirstPrefixSumGtX(int a, int b, T x) {
        if (a < lo || a > hi || b < lo || b > hi) bad("edgePathFirstPrefixSumGtX");
        return edgeFirstPrefixSumGtX(a, b, x);
    }

    // O(log^2 n) -- last edge walking a -> b where the sum from it to b is > x, as its lower end (-1 if none) (needs
    // every weight >= 0)
    LEETCODE_NO_SANITIZE int edgePathLastSuffixSumGtX(int a, int b, T x) {
        if (a < lo || a > hi || b < lo || b > hi) bad("edgePathLastSuffixSumGtX");
        return edgeFirstPrefixSumGtX(b, a, x);
    }

    // O(log n) -- sum of the edge weights in node's subtree; 0 when node is a leaf (no edges)
    LEETCODE_NO_SANITIZE auto edgeSubtreeSum(int node) {
        if (node < lo || node > hi) bad("edgeSubtreeSum");
        int l = pos[node] + 1, r = pos[node] + sz[node] - 1;  // (l > r for a leaf: no edges below it)
        using R = decltype(edgeSeg.rangeSum(0, 0));
        if (l > r) return R(0);
        return edgeSeg.rangeSum(l, r);
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
