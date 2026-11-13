// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/tree-queries/path-rank-updates-node/template.cpp
// @operations: countAtDepthInSubtree depth isAncestor isOnPath kthAncestor kthNodeOnPath lca lcaRootedAt median nextNodeOnPath nodeAdd nodeAssign nodeChmax nodeChmin nodeGet nodePathCountGtX nodePathCountGteX nodePathCountInValRange nodePathCountLtX nodePathCountLteX nodePathCountOccurrences nodePathKthLargest nodePathKthSmallest nodePathLargestLtX nodePathLargestLteX nodePathMax nodePathMin nodePathSmallestGtX nodePathSmallestGteX nodePathSum nodePathSumAbsDiffToMedian nodePathSumAbsDiffToX nodePathSumGtX nodePathSumGteX nodePathSumInValRange nodePathSumKthLargestRange nodePathSumKthSmallestRange nodePathSumLargestK nodePathSumLtX nodePathSumLteX nodePathSumSmallestK parent parentRootedAt pathIntersection pathNodes subtreeSize subtreeSizeRootedAt unweightedDist unweightedDistBetweenPaths unweightedDistToPath
// @data-structure-type: persistent-paths
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
//   nodeGet: 1
//   nodePathCountGtX: log(N)*log(U)
//   nodePathCountGteX: log(N)*log(U)
//   nodePathCountInValRange: log(N)*log(U)
//   nodePathCountLtX: log(N)*log(U)
//   nodePathCountLteX: log(N)*log(U)
//   nodePathCountOccurrences: log(N)*log(U)
//   nodePathKthLargest: log(N)*log(U)
//   nodePathKthSmallest: log(N)*log(U)
//   nodePathLargestLtX: log(N)*log(U)
//   nodePathLargestLteX: log(N)*log(U)
//   nodePathMax: log(N)*log(U)
//   nodePathMin: log(N)*log(U)
//   nodePathSmallestGtX: log(N)*log(U)
//   nodePathSmallestGteX: log(N)*log(U)
//   nodePathSum: log(N)*log(U)
//   nodePathSumAbsDiffToMedian: log(N)*log(U)
//   nodePathSumAbsDiffToX: log(N)*log(U)
//   nodePathSumGtX: log(N)*log(U)
//   nodePathSumGteX: log(N)*log(U)
//   nodePathSumInValRange: log(N)*log(U)
//   nodePathSumKthLargestRange: log(N)*log(U)
//   nodePathSumKthSmallestRange: log(N)*log(U)
//   nodePathSumLargestK: log(N)*log(U)
//   nodePathSumLtX: log(N)*log(U)
//   nodePathSumLteX: log(N)*log(U)
//   nodePathSumSmallestK: log(N)*log(U)
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
//   layout: none
//   node: lc[1*N*log(U)] rc[1*N*log(U)] cnt[1*N*log(U)] tot[1*N*log(U)]
//   tags: none
//   other: top[1*N] ver[1*N] val[1*N] par[1*N] dep[1*N] sz[1*N] head[1*N] pos[1*N] order[1*N] depthPos[1*N] depthStart[1*N]
//   note: U = valHi - valLo + 1. On top of the sizes above, every update adds up to 4*log(N)*log(U) nodes to lc / rc / cnt / tot, and none is ever freed. Measured in C++ at N = 2*10^5, U = 10^9: 124 MB to start, then about 500 nodes (10 KB) an update, so 10^4 updates add 100 MB
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// FAST MODE (this is the only C++ version): sanitizers are skipped inside this template, so a bad access in it goes
// unreported. To turn that off (say, when debugging with sanitizers), put this line above the template:
//   #define LEETCODE_NO_SANITIZE
// Without sanitizers (Codeforces, a plain -O2 build) it changes nothing. It needs GCC or Clang.
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
#ifdef __GLIBCXX__
    LEETCODE_NO_SANITIZE_INLINE typename vector<U>::reference operator[](size_t i) { return this->_M_impl._M_start[i]; }
    LEETCODE_NO_SANITIZE_INLINE typename vector<U>::const_reference operator[](size_t i) const {
        return this->_M_impl._M_start[i];
    }
    LEETCODE_NO_SANITIZE_INLINE size_t size() const { return size_t(this->_M_impl._M_finish - this->_M_impl._M_start); }
#endif
};

// Tree tree(edges, root, vals, valLo, valHi);
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
// valLo: every value ever held is >= valLo (any integer, negative is fine).
// valHi: every value ever held is <= valHi.
//
//   Tree<long long> tree({{0, 1}, {1, 2}}, 0, {10, 20, 30}, valLo, valHi);       // nodes 0..2, rooted at 0
//   Tree<long long> tree({{1, 2}, {2, 3}}, 1, {0, 10, 20, 30}, valLo, valHi);    // nodes 1..3, rooted at 1
//
// Nodes go in and come out with your labels, and -1 means "no such node". A label that is not in the tree throws
// out_of_range. A path a..b includes both a and b. Nothing recurses, so a 10^6-node chain is fine.
//
// How it works: every node keeps a version of a persistent segment tree over the value range [valLo, valHi], holding
// the starting values on its path from the root. A version copies its parent's and adds one value. Changes go into a
// Fenwick tree over the heavy-light positions, each of its nodes a tree over the value range too: changing the value at
// v from old to new counts old one time less and new one time more from pos[v] on, and the opposite from just past v's
// subtree on. So the path root..u is u's version plus the O(log n) Fenwick trees through pos[u], a path a..b is root..a
// + root..b - root..lca - root..parent(lca), and all those trees walk down the value range together: O(log n * log U) a
// query, with U = valHi - valLo + 1.
//
// Memory is the price. The versions take about n * log U tree nodes, and every update adds up to 4 * log n * log U
// more, none of them ever freed. Measured in C++ with n = 2 * 10^5 and U = 10^9: 124 MB to start, then about 500 nodes
// (10 KB) an update, so 10^4 updates add 100 MB and 10^5 would add a gigabyte. A tighter [valLo, valHi] makes both
// smaller. With no updates at all, the path-rank templates (fixed values) are lighter and a log faster.
template <typename T>
struct Tree {
    int n, lo, hi, root;  // nodes are lo..hi
    // by node label: parent (-1 for the root), depth, subtree size, top of its chain, position
    HotVector<int> par, dep, sz, head, pos;
    HotVector<int> order;  // order[pos[v]] = v
    // depthPos[depthStart[d] .. depthStart[d + 1]) = the positions of the nodes at depth d, increasing
    HotVector<int> depthStart, depthPos;
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;  // what sums are kept in
    long long valLo, valHi, span;  // every value lies in [valLo, valHi]; span: how many values that is
    // lc, rc, cnt, tot: one pool of tree nodes over the value range (a value's place in it is value - valLo): a node's
    // two children, how many values it holds and their sum; node 0 is the empty tree. ver[v] is the root of v's
    // version: its parent's, plus its own value (the versions share everything else).
    HotVector<int> lc, rc, cnt;
    HotVector<S> tot;
    HotVector<int> ver;  // ver[v]: the root of v's version
    HotVector<int> top;  // the Fenwick tree over the positions: top[i] is its i-th tree of changes (0: empty)
    HotVector<T> val;  // the node values
    // the trees whose counts add up to a path: r[0 .. plus) count for it, r[plus .. total) count against it
    struct Roots {
        int r[136];
        int plus, total;
    };

    // O(n log U) -- builds the layout and a version per node; throws invalid_argument when the edges are not one tree
    // on nodes 0..n-1 or 1..n, vals has the wrong length, or a value is outside [valLo, valHi]
    template <typename E = int> Tree(const vector<vector<E>>& edges, int root, const vector<T>& vals,
                                    long long valLo, long long valHi)
        : root(root), valLo(valLo), valHi(valHi), span(valHi - valLo + 1) {
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
        val.assign(vals.begin(), vals.end());
        int depth = 1;
        while ((1LL << depth) < span) depth++;
        size_t room = (size_t)n * (depth + 1) + 1;
        lc.assign(room, 0), rc.assign(room, 0), cnt.assign(room, 0), tot.assign(room, 0);
        ver.assign(hi + 1, 0);
        int used = 1;
        for (int k = 0; k < n; k++) {
            int v = bfs[k], prev = v == root ? 0 : ver[par[v]];
            T x = val[v];
            if (x < valLo || x > valHi) throw invalid_argument("Tree: every value must lie in [valLo, valHi]");
            long long i = (long long)x - valLo, a = 0, b = span - 1;
            int cur = ver[v] = used;
            while (true) {
                cnt[cur] = cnt[prev] + 1, tot[cur] = tot[prev] + x;
                used++;
                if (a == b) break;
                long long mid = (a + b) >> 1;
                if (i <= mid) rc[cur] = rc[prev], lc[cur] = used, prev = lc[prev], b = mid;
                else lc[cur] = lc[prev], rc[cur] = used, prev = rc[prev], a = mid + 1;
                cur = used;
            }
        }
        lc.resize(used), rc.resize(used), cnt.resize(used), tot.resize(used);  // (an update appends the nodes it needs)
        top.assign(n + 1, 0);
    }

    // a new, empty tree node at the end of the pool
    int newNode() {
        lc.push_back(0), rc.push_back(0), cnt.push_back(0), tot.push_back(0);
        return (int)cnt.size() - 1;
    }

    // from position p on, the Fenwick trees count x d more times (d is 1 or -1); nothing when p is past the last
    // position
    void change(int p, T x, int d) {
        long long place = (long long)x - valLo;
        for (int i = p + 1; i <= n; i += i & -i) {
            if (!top[i]) top[i] = newNode();
            int cur = top[i];
            long long a = 0, b = span - 1;
            while (true) {
                cnt[cur] += d, tot[cur] += (S)d * x;
                if (a == b) break;
                long long mid = (a + b) >> 1;
                int next = place <= mid ? lc[cur] : rc[cur];
                if (!next) {
                    next = newNode();  // (the pool may have moved: lc / rc are read again below)
                    (place <= mid ? lc[cur] : rc[cur]) = next;
                }
                cur = next;
                if (place <= mid) b = mid;
                else a = mid + 1;
            }
        }
    }

    // the value kept at node v becomes x: every path root..u with u in v's subtree loses the old value and gains x
    void setValue(int v, T x) {
        T old = val[v];
        if (x == old) return;
        if (x < valLo || x > valHi) throw invalid_argument("Tree: every value must lie in [valLo, valHi]");
        int p = pos[v], q = p + sz[v];
        change(p, old, -1), change(p, x, 1);
        change(q, old, 1), change(q, x, -1);
        val[v] = x;
    }

    // how many values of the range [valLo, valHi] are < x (after: <= x): the rank x would take
    LEETCODE_NO_SANITIZE long long rankOf(T x, bool after) const {
        if (x < valLo) return 0;
        if (x > valHi) return span;
        return (long long)x - valLo + (after ? 1 : 0);
    }

    // adds to rs the trees that together hold the path root..v: v's version and the Fenwick trees through pos[v]
    LEETCODE_NO_SANITIZE void gather(int v, Roots& rs) const {
        rs.r[rs.total++] = ver[v];
        for (int i = pos[v] + 1; i > 0; i -= i & -i)
            if (top[i]) rs.r[rs.total++] = top[i];
    }

    // the trees whose counts add up to the path a..b
    LEETCODE_NO_SANITIZE Roots roots(int a, int b) const {
        Roots rs;
        rs.total = 0;
        int c = lcaOf(a, b);
        gather(a, rs), gather(b, rs);
        rs.plus = rs.total;
        gather(c, rs);
        if (c != root) gather(par[c], rs);
        return rs;
    }

    // how many values a path has, and their sum
    LEETCODE_NO_SANITIZE int countOf(const Roots& rs) const {
        int res = 0;
        for (int i = 0; i < rs.plus; i++) res += cnt[rs.r[i]];
        for (int i = rs.plus; i < rs.total; i++) res -= cnt[rs.r[i]];
        return res;
    }
    LEETCODE_NO_SANITIZE S sumOf(const Roots& rs) const {
        S res = 0;
        for (int i = 0; i < rs.plus; i++) res += tot[rs.r[i]];
        for (int i = rs.plus; i < rs.total; i++) res -= tot[rs.r[i]];
        return res;
    }

    // the same two for the lower half of the value range the trees are at
    LEETCODE_NO_SANITIZE int leftCount(const Roots& rs) const {
        int res = 0;
        for (int i = 0; i < rs.plus; i++) res += cnt[lc[rs.r[i]]];
        for (int i = rs.plus; i < rs.total; i++) res -= cnt[lc[rs.r[i]]];
        return res;
    }
    LEETCODE_NO_SANITIZE S leftSum(const Roots& rs) const {
        S res = 0;
        for (int i = 0; i < rs.plus; i++) res += tot[lc[rs.r[i]]];
        for (int i = rs.plus; i < rs.total; i++) res -= tot[lc[rs.r[i]]];
        return res;
    }

    // every tree steps into the lower (the upper) half of its value range
    LEETCODE_NO_SANITIZE void goLeft(Roots& rs) const {
        for (int i = 0; i < rs.total; i++) rs.r[i] = lc[rs.r[i]];
    }
    LEETCODE_NO_SANITIZE void goRight(Roots& rs) const {
        for (int i = 0; i < rs.total; i++) rs.r[i] = rc[rs.r[i]];
    }

    // the kth smallest value of a path (1 <= k <= its size): its trees walk down the value range together
    LEETCODE_NO_SANITIZE T kthValue(Roots rs, int k) const {
        long long lo = 0, hi = span - 1;
        while (lo < hi) {
            long long mid = (lo + hi) >> 1;
            int left = leftCount(rs);
            if (k <= left) {
                goLeft(rs);
                hi = mid;
            } else {
                k -= left;
                goRight(rs);
                lo = mid + 1;
            }
        }
        return (T)(valLo + lo);
    }

    // how many of a path's values are among the r smallest values of the range [valLo, valHi]; total: their sum
    LEETCODE_NO_SANITIZE int valuesBelow(Roots rs, long long r, S& total) const {
        long long lo = 0, hi = span - 1;
        int many = 0;
        total = 0;
        if (r <= 0) return 0;
        if (r > hi) {
            total = sumOf(rs);
            return countOf(rs);
        }
        while (lo < hi) {
            long long mid = (lo + hi) >> 1;
            if (r > mid) {  // the whole lower half is wanted
                many += leftCount(rs);
                total += leftSum(rs);
                goRight(rs);
                lo = mid + 1;
            } else {
                goLeft(rs);
                hi = mid;
            }
        }
        return many;
    }

    // the sum of a path's k smallest values (0 <= k <= its size)
    LEETCODE_NO_SANITIZE S smallestSum(Roots rs, int k) const {
        if (k <= 0) return 0;
        S total = 0;
        long long lo = 0, hi = span - 1;
        while (lo < hi) {
            long long mid = (lo + hi) >> 1;
            int left = leftCount(rs);
            if (k <= left) {
                goLeft(rs);
                hi = mid;
            } else {
                k -= left;
                total += leftSum(rs);
                goRight(rs);
                lo = mid + 1;
            }
        }
        return total + (S)k * (S)(valLo + lo);
    }

    // O(1) -- val(node)
    LEETCODE_NO_SANITIZE T nodeGet(int node) const {
        if (node < lo || node > hi) bad("nodeGet");
        return val[node];
    }

    // O(log n * log U) -- val(node) = x; the new value must lie in [valLo, valHi]
    void nodeAssign(int node, T x) {
        if (node < lo || node > hi) bad("nodeAssign");
        setValue(node, x);
    }

    // O(log n * log U) -- val(node) += x; the new value must lie in [valLo, valHi]
    void nodeAdd(int node, T x) {
        if (node < lo || node > hi) bad("nodeAdd");
        setValue(node, val[node] + x);
    }

    // O(log n * log U) -- val(node) = max(val, x); the new value must lie in [valLo, valHi]
    void nodeChmax(int node, T x) {
        if (node < lo || node > hi) bad("nodeChmax");
        if (x > val[node]) setValue(node, x);
    }

    // O(log n * log U) -- val(node) = min(val, x); the new value must lie in [valLo, valHi]
    void nodeChmin(int node, T x) {
        if (node < lo || node > hi) bad("nodeChmin");
        if (x < val[node]) setValue(node, x);
    }

    // O(log n * log U) -- kth smallest of the node values on the path a..b (1-indexed: k = 1 is the min); needs 1 <= k
    // <= the path's size, else throws out_of_range
    LEETCODE_NO_SANITIZE T nodePathKthSmallest(int a, int b, int k) const {
        if (a < lo || a > hi || b < lo || b > hi) bad("nodePathKthSmallest");
        Roots rs = roots(a, b);
        int size = countOf(rs);
        if (k < 1 || k > size)
            throw out_of_range("nodePathKthSmallest: needs 1 <= k <= the path's size");
        return kthValue(rs, k);
    }

    // O(log n * log U) -- kth largest of the node values on the path a..b (1-indexed: k = 1 is the max); needs 1 <= k
    // <= the path's size, else throws out_of_range
    LEETCODE_NO_SANITIZE T nodePathKthLargest(int a, int b, int k) const {
        if (a < lo || a > hi || b < lo || b > hi) bad("nodePathKthLargest");
        Roots rs = roots(a, b);
        int size = countOf(rs);
        if (k < 1 || k > size)
            throw out_of_range("nodePathKthLargest: needs 1 <= k <= the path's size");
        return kthValue(rs, size + 1 - k);
    }

    // O(log n * log U) -- sum of the k smallest node values on the path a..b; needs 0 <= k <= the path's size, else
    // throws out_of_range
    LEETCODE_NO_SANITIZE S nodePathSumSmallestK(int a, int b, int k) const {
        if (a < lo || a > hi || b < lo || b > hi) bad("nodePathSumSmallestK");
        Roots rs = roots(a, b);
        int size = countOf(rs);
        if (k < 0 || k > size)
            throw out_of_range("nodePathSumSmallestK: needs 0 <= k <= the path's size");
        return smallestSum(rs, k);
    }

    // O(log n * log U) -- sum of the k largest node values on the path a..b; needs 0 <= k <= the path's size, else
    // throws out_of_range
    LEETCODE_NO_SANITIZE S nodePathSumLargestK(int a, int b, int k) const {
        if (a < lo || a > hi || b < lo || b > hi) bad("nodePathSumLargestK");
        Roots rs = roots(a, b);
        int size = countOf(rs);
        if (k < 0 || k > size)
            throw out_of_range("nodePathSumLargestK: needs 0 <= k <= the path's size");
        return sumOf(rs) - smallestSum(rs, size - k);
    }

    // O(log n * log U) -- sum of the kFrom-th ... kTo-th smallest node values on the path a..b (1-indexed); needs 1 <=
    // kFrom <= kTo <= the path's size, else throws out_of_range
    LEETCODE_NO_SANITIZE S nodePathSumKthSmallestRange(int a, int b, int kFrom, int kTo) const {
        if (a < lo || a > hi || b < lo || b > hi) bad("nodePathSumKthSmallestRange");
        Roots rs = roots(a, b);
        int size = countOf(rs);
        if (kFrom < 1 || kFrom > kTo || kTo > size)
            throw out_of_range("nodePathSumKthSmallestRange: needs 1 <= kFrom <= kTo <= the path's size");
        return smallestSum(rs, kTo) - smallestSum(rs, kFrom - 1);
    }

    // O(log n * log U) -- sum of the kFrom-th ... kTo-th largest node values on the path a..b (1-indexed); needs 1 <=
    // kFrom <= kTo <= the path's size, else throws out_of_range
    LEETCODE_NO_SANITIZE S nodePathSumKthLargestRange(int a, int b, int kFrom, int kTo) const {
        if (a < lo || a > hi || b < lo || b > hi) bad("nodePathSumKthLargestRange");
        Roots rs = roots(a, b);
        int size = countOf(rs);
        if (kFrom < 1 || kFrom > kTo || kTo > size)
            throw out_of_range("nodePathSumKthLargestRange: needs 1 <= kFrom <= kTo <= the path's size");
        return smallestSum(rs, size - kFrom + 1) - smallestSum(rs, size - kTo);
    }

    // O(log n * log U) -- sum of the node values on the path a..b
    LEETCODE_NO_SANITIZE S nodePathSum(int a, int b) const {
        if (a < lo || a > hi || b < lo || b > hi) bad("nodePathSum");
        Roots rs = roots(a, b);
        return sumOf(rs);
    }

    // O(log n * log U) -- min node value on the path a..b
    LEETCODE_NO_SANITIZE T nodePathMin(int a, int b) const {
        if (a < lo || a > hi || b < lo || b > hi) bad("nodePathMin");
        Roots rs = roots(a, b);
        return kthValue(rs, 1);
    }

    // O(log n * log U) -- max node value on the path a..b
    LEETCODE_NO_SANITIZE T nodePathMax(int a, int b) const {
        if (a < lo || a > hi || b < lo || b > hi) bad("nodePathMax");
        Roots rs = roots(a, b);
        int size = countOf(rs);
        return kthValue(rs, size);
    }

    // O(log n * log U) -- how many node values on the path a..b are < x
    LEETCODE_NO_SANITIZE int nodePathCountLtX(int a, int b, T x) const {
        if (a < lo || a > hi || b < lo || b > hi) bad("nodePathCountLtX");
        Roots rs = roots(a, b);
        S unused;
        return valuesBelow(rs, rankOf(x, false), unused);
    }

    // O(log n * log U) -- sum of the node values on the path a..b that are < x
    LEETCODE_NO_SANITIZE S nodePathSumLtX(int a, int b, T x) const {
        if (a < lo || a > hi || b < lo || b > hi) bad("nodePathSumLtX");
        Roots rs = roots(a, b);
        S low;
        valuesBelow(rs, rankOf(x, false), low);
        return low;
    }

    // O(log n * log U) -- how many node values on the path a..b are <= x
    LEETCODE_NO_SANITIZE int nodePathCountLteX(int a, int b, T x) const {
        if (a < lo || a > hi || b < lo || b > hi) bad("nodePathCountLteX");
        Roots rs = roots(a, b);
        S unused;
        return valuesBelow(rs, rankOf(x, true), unused);
    }

    // O(log n * log U) -- sum of the node values on the path a..b that are <= x
    LEETCODE_NO_SANITIZE S nodePathSumLteX(int a, int b, T x) const {
        if (a < lo || a > hi || b < lo || b > hi) bad("nodePathSumLteX");
        Roots rs = roots(a, b);
        S low;
        valuesBelow(rs, rankOf(x, true), low);
        return low;
    }

    // O(log n * log U) -- how many node values on the path a..b are > x
    LEETCODE_NO_SANITIZE int nodePathCountGtX(int a, int b, T x) const {
        if (a < lo || a > hi || b < lo || b > hi) bad("nodePathCountGtX");
        Roots rs = roots(a, b);
        int size = countOf(rs);
        S unused;
        return size - valuesBelow(rs, rankOf(x, true), unused);
    }

    // O(log n * log U) -- sum of the node values on the path a..b that are > x
    LEETCODE_NO_SANITIZE S nodePathSumGtX(int a, int b, T x) const {
        if (a < lo || a > hi || b < lo || b > hi) bad("nodePathSumGtX");
        Roots rs = roots(a, b);
        S low;
        valuesBelow(rs, rankOf(x, true), low);
        return sumOf(rs) - low;
    }

    // O(log n * log U) -- how many node values on the path a..b are >= x
    LEETCODE_NO_SANITIZE int nodePathCountGteX(int a, int b, T x) const {
        if (a < lo || a > hi || b < lo || b > hi) bad("nodePathCountGteX");
        Roots rs = roots(a, b);
        int size = countOf(rs);
        S unused;
        return size - valuesBelow(rs, rankOf(x, false), unused);
    }

    // O(log n * log U) -- sum of the node values on the path a..b that are >= x
    LEETCODE_NO_SANITIZE S nodePathSumGteX(int a, int b, T x) const {
        if (a < lo || a > hi || b < lo || b > hi) bad("nodePathSumGteX");
        Roots rs = roots(a, b);
        S low;
        valuesBelow(rs, rankOf(x, false), low);
        return sumOf(rs) - low;
    }

    // O(log n * log U) -- how many node values on the path a..b are in [low, high]
    LEETCODE_NO_SANITIZE int nodePathCountInValRange(int a, int b, T low, T high) const {
        if (a < lo || a > hi || b < lo || b > hi) bad("nodePathCountInValRange");
        Roots rs = roots(a, b);
        if (high < low) return 0;
        S unused;
        int upTo = valuesBelow(rs, rankOf(high, true), unused);
        return upTo - valuesBelow(rs, rankOf(low, false), unused);
    }

    // O(log n * log U) -- sum of the node values on the path a..b in [low, high]
    LEETCODE_NO_SANITIZE S nodePathSumInValRange(int a, int b, T low, T high) const {
        if (a < lo || a > hi || b < lo || b > hi) bad("nodePathSumInValRange");
        Roots rs = roots(a, b);
        if (high < low) return 0;
        S upTo, under;
        valuesBelow(rs, rankOf(high, true), upTo), valuesBelow(rs, rankOf(low, false), under);
        return upTo - under;
    }

    // O(log n * log U) -- how many node values on the path a..b equal x
    LEETCODE_NO_SANITIZE int nodePathCountOccurrences(int a, int b, T x) const {
        if (a < lo || a > hi || b < lo || b > hi) bad("nodePathCountOccurrences");
        Roots rs = roots(a, b);
        S unused;
        return valuesBelow(rs, rankOf(x, true), unused) - valuesBelow(rs, rankOf(x, false), unused);
    }

    // O(log n * log U) -- sum of |val - x| over the node values on the path a..b
    LEETCODE_NO_SANITIZE S nodePathSumAbsDiffToX(int a, int b, T x) const {
        if (a < lo || a > hi || b < lo || b > hi) bad("nodePathSumAbsDiffToX");
        Roots rs = roots(a, b);
        int size = countOf(rs);
        S low;
        int many = valuesBelow(rs, rankOf(x, false), low);
        return (S)x * many - low + (sumOf(rs) - low) - (S)x * (size - many);
    }

    // O(log n * log U) -- sum of |val - median| over the node values on the path a..b (the lower median)
    LEETCODE_NO_SANITIZE S nodePathSumAbsDiffToMedian(int a, int b) const {
        if (a < lo || a > hi || b < lo || b > hi) bad("nodePathSumAbsDiffToMedian");
        Roots rs = roots(a, b);
        int size = countOf(rs);
        T x = kthValue(rs, (size + 1) / 2);
        S low;
        int many = valuesBelow(rs, rankOf(x, false), low);
        return (S)x * many - low + (sumOf(rs) - low) - (S)x * (size - many);
    }

    // O(log n * log U) -- smallest of the node values on the path a..b that is >= x (nullopt if none)
    LEETCODE_NO_SANITIZE optional<T> nodePathSmallestGteX(int a, int b, T x) const {
        if (a < lo || a > hi || b < lo || b > hi) bad("nodePathSmallestGteX");
        Roots rs = roots(a, b);
        int size = countOf(rs);
        S unused;
        int k = valuesBelow(rs, rankOf(x, false), unused);
        if (k == size) return nullopt;
        return kthValue(rs, k + 1);
    }

    // O(log n * log U) -- smallest of the node values on the path a..b that is > x (nullopt if none)
    LEETCODE_NO_SANITIZE optional<T> nodePathSmallestGtX(int a, int b, T x) const {
        if (a < lo || a > hi || b < lo || b > hi) bad("nodePathSmallestGtX");
        Roots rs = roots(a, b);
        int size = countOf(rs);
        S unused;
        int k = valuesBelow(rs, rankOf(x, true), unused);
        if (k == size) return nullopt;
        return kthValue(rs, k + 1);
    }

    // O(log n * log U) -- largest of the node values on the path a..b that is <= x (nullopt if none)
    LEETCODE_NO_SANITIZE optional<T> nodePathLargestLteX(int a, int b, T x) const {
        if (a < lo || a > hi || b < lo || b > hi) bad("nodePathLargestLteX");
        Roots rs = roots(a, b);
        S unused;
        int k = valuesBelow(rs, rankOf(x, true), unused);
        if (k == 0) return nullopt;
        return kthValue(rs, k);
    }

    // O(log n * log U) -- largest of the node values on the path a..b that is < x (nullopt if none)
    LEETCODE_NO_SANITIZE optional<T> nodePathLargestLtX(int a, int b, T x) const {
        if (a < lo || a > hi || b < lo || b > hi) bad("nodePathLargestLtX");
        Roots rs = roots(a, b);
        S unused;
        int k = valuesBelow(rs, rankOf(x, false), unused);
        if (k == 0) return nullopt;
        return kthValue(rs, k);
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
