// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/tree-queries/node-pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAndQuery-rangeOrQuery-rangeSum-rangeXorApply/template.cpp
// The range structure inside is https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAndQuery-rangeOrQuery-rangeSum-rangeXorApply/fast.cpp
// @operations: countAtDepthInSubtree depth isAncestor isOnPath kthAncestor kthNodeOnPath lca lcaRootedAt median nextNodeOnPath nodeAdd nodeAssign nodeChmax nodeChmin nodeGet nodePathAND nodePathOR nodePathSum nodePathXORApply nodeSubtreeAND nodeSubtreeOR nodeSubtreeSum nodeSubtreeXORApply parent parentRootedAt pathIntersection pathNodes subtreeSize subtreeSizeRootedAt unweightedDist unweightedDistBetweenPaths unweightedDistToPath
// @data-structure-type: lazy-seg-tree
// @complexities:
//   countAtDepthInSubtree: log(N)
//   depth: 1
//   isAncestor: 1
//   isOnPath: log(N)
//   kthAncestor: log(N)
//   kthNodeOnPath: log(N)
//   lca: log(N)
//   lcaRootedAt: log(N)
//   median: log(N)
//   nextNodeOnPath: log(N)
//   nodeAdd: log(N)*log(U)
//   nodeAssign: log(N)*log(U)
//   nodeChmax: log(N)*log(U)
//   nodeChmin: log(N)*log(U)
//   nodeGet: log(N)*log(U)
//   nodePathAND: log^2(N)*log(U)
//   nodePathOR: log^2(N)*log(U)
//   nodePathSum: log^2(N)*log(U)
//   nodePathXORApply: log^2(N)*log(U)
//   nodeSubtreeAND: log(N)*log(U)
//   nodeSubtreeOR: log(N)*log(U)
//   nodeSubtreeSum: log(N)*log(U)
//   nodeSubtreeXORApply: log(N)*log(U)
//   parent: 1
//   parentRootedAt: log(N)
//   pathIntersection: log(N)
//   pathNodes: K+log(N)
//   subtreeSize: 1
//   subtreeSizeRootedAt: log(N)
//   unweightedDist: log(N)
//   unweightedDistBetweenPaths: log(N)
//   unweightedDistToPath: log(N)
//   build: N*log(U)
// @memory:
//   layout: 2n-iterative
//   node: cnt[2*N*log(U)]
//   tags: xorTag[1*N]
//   other: par[1*N] dep[1*N] sz[1*N] head[1*N] pos[1*N] order[1*N] depthPos[1*N] depthStart[1*N]
//   note: cnt keeps, per node and per bit, how many values below have that bit set (bits = log U, 20 by default); tags live on internal nodes only
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// FAST MODE (this is the only C++ version): sanitizers are skipped inside this template, so a bad access in it goes
// unreported. To turn that off (say, when debugging with sanitizers), put this line above the template:
//   #define LEETCODE_NO_SANITIZE
// Without sanitizers (Codeforces, a plain -O2 build) it changes nothing. It needs GCC or Clang.

// Range xor= with range sum / and / or queries, plus point ops. All indices 0-based, ranges inclusive.
// Values live in [0, 2^bits). Each node counts, for every bit, how many of its values have that bit set. A xor X
// flips the bits set in X: per bit, a flip turns the count c into length - c, so the tag is just the mask to
// flip (this is BitCountTree without the AND tag that only and= / or= need).
// So every update is an ordinary lazy tag, a true O(log N * bits) with no amortization (unlike bitwise beats, which
// cannot apply xor to a node whose values disagree on a bit). Sum = sum over bits of count * 2^bit.
// Iterative 2N lazy tree; a covering node at level s is a perfect subtree of 2^s leaves.
// T: int, long long, ...; sums accumulate in S (long long for small T).
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
struct BitCountTree {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    int n, h, bits;
    T full;
    HotVector<int> cnt;          // cnt[x * bits + b] = # of values under node x with bit b set (2N nodes)
    HotVector<T> xorTag;  // N: tags on internal nodes

    // O(N * bits)
    explicit BitCountTree(const vector<T>& a, int bits = 20)
        : n((int)a.size()), h(a.empty() ? 0 : 32 - __builtin_clz((unsigned)a.size())), bits(bits),
            full(T((T(1) << bits) - 1)),
          cnt(2 * a.size() * bits), xorTag(a.size(), 0) {
        for (int i = 0; i < n; i++)
            for (int b = 0; b < bits; b++) cnt[(n + i) * bits + b] = a[i] >> b & 1;
        for (int x = n - 1; x > 0; x--)
            for (int b = 0; b < bits; b++) cnt[x * bits + b] = cnt[2 * x * bits + b] + cnt[(2 * x + 1) * bits + b];
    }

    // v -> v ^ xr on node x, which covers k slots
    LEETCODE_NO_SANITIZE void apply(int x, int k, T xr) {
        int* c = &cnt[x * bits];
        for (int b = 0; b < bits; b++) {
            if (xr >> b & 1) c[b] = k - c[b];
        }
        if (x < n) xorTag[x] ^= xr;
    }

    LEETCODE_NO_SANITIZE void push(int p) {
        for (int s = h; s > 0; s--) {
            int x = p >> s;
            if (xorTag[x]) {
                int k = 1 << (s - 1);
                apply(2 * x, k, xorTag[x]), apply(2 * x + 1, k, xorTag[x]);
                xorTag[x] = 0;
            }
        }
    }

    LEETCODE_NO_SANITIZE void rebuild(int p) {
        for (int k = 2; p > 1; k <<= 1) {
            p >>= 1;
            for (int b = 0; b < bits; b++) {
                int v = cnt[2 * p * bits + b] + cnt[(2 * p + 1) * bits + b];
                if (xorTag[p] >> b & 1) v = k - v;
                cnt[p * bits + b] = v;
            }
        }
    }

    LEETCODE_NO_SANITIZE void update(int l, int r, T xr) {
        if (l > r) return;
        int l0 = l + n, r0 = r + n;
        push(l0), push(r0);
        for (int i = l0, j = r0 + 1, k = 1; i < j; i >>= 1, j >>= 1, k <<= 1) {
            if (i & 1) apply(i++, k, xr);
            if (j & 1) apply(--j, k, xr);
        }
        rebuild(l0), rebuild(r0);
    }

    // the canonical nodes of [l, r] with their lengths, after pushing the two boundary paths
    LEETCODE_NO_SANITIZE vector<pair<int, int>> nodes(int l, int r) {
        vector<pair<int, int>> out;
        l += n, r += n;
        push(l), push(r);
        for (int k = 1, rr = r + 1; l < rr; l >>= 1, rr >>= 1, k <<= 1) {
            if (l & 1) out.push_back({l++, k});
            if (rr & 1) out.push_back({--rr, k});
        }
        return out;
    }

    // O(logN * bits) -- a[i] ^= X for i in [l, r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void rangeXorApply(int l, int r, T X) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeXorApply: needs 0 <= l <= r < n");
        update(l, r, X & full);
    }

    // O(logN * bits) -- a[l] + ... + a[r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE S rangeSum(int l, int r) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeSum: needs 0 <= l <= r < n");
        if (l > r) return 0;
        S res = 0;
        for (auto [x, k] : nodes(l, r))
            for (int b = 0; b < bits; b++) res += S(cnt[x * bits + b]) << b;
        return res;
    }

    // O(logN * bits) -- a[l] & ... & a[r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE T rangeAndQuery(int l, int r) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeAndQuery: needs 0 <= l <= r < n");
        T res = full;
        for (auto [x, k] : nodes(l, r))
            for (int b = 0; b < bits; b++)
                if (cnt[x * bits + b] != k) res &= ~(T(1) << b);
        return res;
    }

    // O(logN * bits) -- a[l] | ... | a[r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE T rangeOrQuery(int l, int r) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeOrQuery: needs 0 <= l <= r < n");
        T res = 0;
        for (auto [x, k] : nodes(l, r))
            for (int b = 0; b < bits; b++)
                if (cnt[x * bits + b]) res |= T(1) << b;
        return res;
    }

    // O(logN * bits) -- a[i]; needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE T pointGet(int i) {
        if (i < 0 || i >= n) throw out_of_range("pointGet: needs 0 <= i < n");
        int p = i + n;
        push(p);
        T v = 0;
        for (int b = 0; b < bits; b++) v |= T(cnt[p * bits + b]) << b;
        return v;
    }

    // O(N * logU) -- the whole array: push every tag down one level at a time from the root (the nodes s levels above
    // the leaves are (n >> s) .. ((2n - 1) >> s); their children cover k = 1 << (s - 1) leaves), then read the leaves
    LEETCODE_NO_SANITIZE vector<T> getAll() {
        for (int s = h; s > 0; s--) {
            int k = 1 << (s - 1);
            for (int x = max(1, n >> s); x <= (2 * n - 1) >> s; x++)
                if (xorTag[x]) {
                    apply(2 * x, k, xorTag[x]), apply(2 * x + 1, k, xorTag[x]);
                    xorTag[x] = 0;
                }
        }
        vector<T> out(n, 0);
        for (int i = 0; i < n; i++)
            for (int b = 0; b < bits; b++) out[i] |= T(cnt[(n + i) * bits + b]) << b;
        return out;
    }

    // O(logN * bits) -- a[i] = v & FULL; needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAssign(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointAssign: needs 0 <= i < n");
        int p = i + n;
        push(p);
        v &= full;
        for (int b = 0; b < bits; b++) cnt[p * bits + b] = v >> b & 1;
        rebuild(p);
    }

    // O(logN * bits) -- a[i] = (a[i] + delta) & FULL; needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAdd(int i, T delta) {
        if (i < 0 || i >= n) throw out_of_range("pointAdd: needs 0 <= i < n");
        pointAssign(i, pointGet(i) + delta);
    }

    // O(logN * bits) -- a[i] = max(a[i], v); needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointChmax(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointChmax: needs 0 <= i < n");
        if (v > pointGet(i)) pointAssign(i, v);
    }

    // O(logN * bits) -- a[i] = min(a[i], v); needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointChmin(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointChmin: needs 0 <= i < n");
        if (v < pointGet(i)) pointAssign(i, v);
    }

    // O(log(N)*log(U)) -- sum of the whole array a[0..n-1] (rangeSum(0, n - 1)); needs n >= 1, else throws out_of_range
    LEETCODE_NO_SANITIZE auto sumAll() {
        if (n < 1) throw out_of_range("sumAll: needs n >= 1");
        return rangeSum(0, n - 1);
    }

    // O(log(N)*log(U)) -- AND of the whole array a[0..n-1] (rangeAndQuery(0, n - 1)); needs n >= 1, else throws
    // out_of_range
    LEETCODE_NO_SANITIZE auto andAll() {
        if (n < 1) throw out_of_range("andAll: needs n >= 1");
        return rangeAndQuery(0, n - 1);
    }

    // O(log(N)*log(U)) -- OR of the whole array a[0..n-1] (rangeOrQuery(0, n - 1)); needs n >= 1, else throws
    // out_of_range
    LEETCODE_NO_SANITIZE auto orAll() {
        if (n < 1) throw out_of_range("orAll: needs n >= 1");
        return rangeOrQuery(0, n - 1);
    }

};

// Tree tree(edges, root, vals, bits);
//
// edges: the tree's n - 1 edges, vector<vector<int>> (vector<vector<long long>> works too). Whether nodes are 0..n-1
//        or 1..n is detected automatically from the edge list (smallest label is 0 -> 0..n-1, otherwise 1..n; with
//        no edges, from root)
//   {{a, b}, ...}        e.g. {{0, 1}, {1, 2}}
//   {{a, b, w}, ...}     also accepted: the weights are ignored here
// root: the root node (required), e.g. 0 or 1.
// vals: the node values, vector<T> (T = long long, or int), vals[node] is node's value
//   nodes 0..n-1: size n        e.g. n = 3: {10, 20, 30}         node 0 -> 10
//   nodes 1..n:   size n + 1    e.g. n = 3: {0, 10, 20, 30}      vals[0] is ignored, node 1 -> 10
// bits: values live in [0, 2^bits).
//
//   Tree<long long> tree({{0, 1}, {1, 2}}, 0, {10, 20, 30}, bits);       // nodes 0..2, rooted at 0
//   Tree<long long> tree({{1, 2}, {2, 3}}, 1, {0, 10, 20, 30}, bits);    // nodes 1..3, rooted at 1
//
// Nodes go in and come out with your labels, and -1 means "no such node". A label that is not in the tree throws
// out_of_range. A path a..b includes both a and b. Nothing recurses, so a 10^6-node chain is fine.
//
// How it works: one heavy-light pass gives every node a position, so that each heavy chain and each subtree is one
// stretch of positions (pos[node] .. pos[node] + sz[node] - 1). The values sit in the range structure above
// (BitCountTree) in position order: a subtree is one range of it, and a path a..b is O(log n) ranges, one per chain it
// crosses.
template <typename T>
struct Tree {
    int n, lo, hi, root;  // nodes are lo..hi
    // by node label: parent (-1 for the root), depth, subtree size, top of its chain, position
    HotVector<int> par, dep, sz, head, pos;
    HotVector<int> order;  // order[pos[v]] = v
    // depthPos[depthStart[d] .. depthStart[d + 1]) = the positions of the nodes at depth d, increasing
    HotVector<int> depthStart, depthPos;
    BitCountTree<T> seg;  // the values, in position order

    // O(n * log U) -- builds the layout and the range structure; throws invalid_argument when the edges are not one
    // tree on nodes 0..n-1 or 1..n, or vals has the wrong size
    template <typename E = int> Tree(const vector<vector<E>>& edges, int root, const vector<T>& vals, int bits = 20)
        : seg(layout(edges, root, vals), bits) {}

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

    // O(log n * log U) -- val(node)
    LEETCODE_NO_SANITIZE auto nodeGet(int node) {
        if (node < lo || node > hi) bad("nodeGet");
        return seg.pointGet(pos[node]);
    }

    // O(log n * log U) -- val(node) = x
    LEETCODE_NO_SANITIZE void nodeAssign(int node, T x) {
        if (node < lo || node > hi) bad("nodeAssign");
        seg.pointAssign(pos[node], x);
    }

    // O(log n * log U) -- val(node) += x
    LEETCODE_NO_SANITIZE void nodeAdd(int node, T x) {
        if (node < lo || node > hi) bad("nodeAdd");
        seg.pointAdd(pos[node], x);
    }

    // O(log n * log U) -- val(node) = max(val, x)
    LEETCODE_NO_SANITIZE void nodeChmax(int node, T x) {
        if (node < lo || node > hi) bad("nodeChmax");
        seg.pointChmax(pos[node], x);
    }

    // O(log n * log U) -- val(node) = min(val, x)
    LEETCODE_NO_SANITIZE void nodeChmin(int node, T x) {
        if (node < lo || node > hi) bad("nodeChmin");
        seg.pointChmin(pos[node], x);
    }

    // O(log^2 n * log U) -- val ^= x for every node on the path a..b
    LEETCODE_NO_SANITIZE void nodePathXORApply(int a, int b, T x) {
        if (a < lo || a > hi || b < lo || b > hi) bad("nodePathXORApply");
        while (head[a] != head[b]) {
            if (dep[head[a]] < dep[head[b]]) {
                int t = a;
                a = b, b = t;
            }
            seg.rangeXorApply(pos[head[a]], pos[a], x);
            a = par[head[a]];
        }
        int l = pos[a], r = pos[b];
        if (l <= r) seg.rangeXorApply(l, r, x);
        else seg.rangeXorApply(r, l, x);
    }

    // O(log^2 n * log U) -- sum of the node values on the path a..b
    LEETCODE_NO_SANITIZE auto nodePathSum(int a, int b) {
        if (a < lo || a > hi || b < lo || b > hi) bad("nodePathSum");
        using R = decltype(seg.rangeSum(0, 0));
        R res = 0;
        while (head[a] != head[b]) {
            if (dep[head[a]] < dep[head[b]]) {
                int t = a;
                a = b, b = t;
            }
            R v = seg.rangeSum(pos[head[a]], pos[a]);
            res += v;
            a = par[head[a]];
        }
        int l = pos[a], r = pos[b];
        if (l > r) {
            int t = l;
            l = r, r = t;
        }
        R v = seg.rangeSum(l, r);
        res += v;
        return res;
    }

    // O(log^2 n * log U) -- AND of the node values on the path a..b
    LEETCODE_NO_SANITIZE auto nodePathAND(int a, int b) {
        if (a < lo || a > hi || b < lo || b > hi) bad("nodePathAND");
        using R = decltype(seg.rangeAndQuery(0, 0));
        R res = ~R(0);
        while (head[a] != head[b]) {
            if (dep[head[a]] < dep[head[b]]) {
                int t = a;
                a = b, b = t;
            }
            R v = seg.rangeAndQuery(pos[head[a]], pos[a]);
            res &= v;
            a = par[head[a]];
        }
        int l = pos[a], r = pos[b];
        if (l > r) {
            int t = l;
            l = r, r = t;
        }
        R v = seg.rangeAndQuery(l, r);
        res &= v;
        return res;
    }

    // O(log^2 n * log U) -- OR of the node values on the path a..b
    LEETCODE_NO_SANITIZE auto nodePathOR(int a, int b) {
        if (a < lo || a > hi || b < lo || b > hi) bad("nodePathOR");
        using R = decltype(seg.rangeOrQuery(0, 0));
        R res = 0;
        while (head[a] != head[b]) {
            if (dep[head[a]] < dep[head[b]]) {
                int t = a;
                a = b, b = t;
            }
            R v = seg.rangeOrQuery(pos[head[a]], pos[a]);
            res |= v;
            a = par[head[a]];
        }
        int l = pos[a], r = pos[b];
        if (l > r) {
            int t = l;
            l = r, r = t;
        }
        R v = seg.rangeOrQuery(l, r);
        res |= v;
        return res;
    }

    // O(log n * log U) -- val ^= x for every node in node's subtree
    LEETCODE_NO_SANITIZE void nodeSubtreeXORApply(int node, T x) {
        if (node < lo || node > hi) bad("nodeSubtreeXORApply");
        int l = pos[node];
        seg.rangeXorApply(l, l + sz[node] - 1, x);
    }

    // O(log n * log U) -- sum of the node values in node's subtree
    LEETCODE_NO_SANITIZE auto nodeSubtreeSum(int node) {
        if (node < lo || node > hi) bad("nodeSubtreeSum");
        int l = pos[node];
        return seg.rangeSum(l, l + sz[node] - 1);
    }

    // O(log n * log U) -- AND of the node values in node's subtree
    LEETCODE_NO_SANITIZE auto nodeSubtreeAND(int node) {
        if (node < lo || node > hi) bad("nodeSubtreeAND");
        int l = pos[node];
        return seg.rangeAndQuery(l, l + sz[node] - 1);
    }

    // O(log n * log U) -- OR of the node values in node's subtree
    LEETCODE_NO_SANITIZE auto nodeSubtreeOR(int node) {
        if (node < lo || node > hi) bad("nodeSubtreeOR");
        int l = pos[node];
        return seg.rangeOrQuery(l, l + sz[node] - 1);
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
