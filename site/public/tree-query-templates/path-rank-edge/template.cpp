// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/tree-queries/path-rank-edge/template.cpp
// @operations: countAtDepthInSubtree depth edgeGet edgePathCountGtX edgePathCountGteX edgePathCountInValRange edgePathCountLtX edgePathCountLteX edgePathCountOccurrences edgePathKthLargest edgePathKthSmallest edgePathLargestLtX edgePathLargestLteX edgePathMax edgePathMin edgePathSmallestGtX edgePathSmallestGteX edgePathSum edgePathSumAbsDiffToMedian edgePathSumAbsDiffToX edgePathSumGtX edgePathSumGteX edgePathSumInValRange edgePathSumKthLargestRange edgePathSumKthSmallestRange edgePathSumLargestK edgePathSumLtX edgePathSumLteX edgePathSumSmallestK isAncestor isOnPath kthAncestor kthNodeOnPath lca lcaRootedAt median nextNodeOnPath parent parentRootedAt pathIntersection pathNodes subtreeSize subtreeSizeRootedAt unweightedDist unweightedDistBetweenPaths unweightedDistToPath
// @data-structure-type: persistent-paths
// @complexities:
//   countAtDepthInSubtree: log(N)
//   depth: 1
//   edgeGet: 1
//   edgePathCountGtX: log(N)
//   edgePathCountGteX: log(N)
//   edgePathCountInValRange: log(N)
//   edgePathCountLtX: log(N)
//   edgePathCountLteX: log(N)
//   edgePathCountOccurrences: log(N)
//   edgePathKthLargest: log(N)
//   edgePathKthSmallest: log(N)
//   edgePathLargestLtX: log(N)
//   edgePathLargestLteX: log(N)
//   edgePathMax: log(N)
//   edgePathMin: log(N)
//   edgePathSmallestGtX: log(N)
//   edgePathSmallestGteX: log(N)
//   edgePathSum: log(N)
//   edgePathSumAbsDiffToMedian: log(N)
//   edgePathSumAbsDiffToX: log(N)
//   edgePathSumGtX: log(N)
//   edgePathSumGteX: log(N)
//   edgePathSumInValRange: log(N)
//   edgePathSumKthLargestRange: log(N)
//   edgePathSumKthSmallestRange: log(N)
//   edgePathSumLargestK: log(N)
//   edgePathSumLtX: log(N)
//   edgePathSumLteX: log(N)
//   edgePathSumSmallestK: log(N)
//   isAncestor: 1
//   isOnPath: log(N)
//   kthAncestor: log(N)
//   kthNodeOnPath: log(N)
//   lca: log(N)
//   lcaRootedAt: log(N)
//   median: log(N)
//   nextNodeOnPath: log(N)
//   parent: 1
//   parentRootedAt: log(N)
//   pathIntersection: log(N)
//   pathNodes: K+log(N)
//   subtreeSize: 1
//   subtreeSizeRootedAt: log(N)
//   unweightedDist: log(N)
//   unweightedDistBetweenPaths: log(N)
//   unweightedDistToPath: log(N)
//   build: N*log(N)
// @memory:
//   layout: none
//   node: lc[1*N*log(N)] rc[1*N*log(N)] cnt[1*N*log(N)] tot[1*N*log(N)]
//   tags: none
//   other: ver[1*N] srt[1*N] val[1*N] par[1*N] dep[1*N] sz[1*N] head[1*N] pos[1*N] order[1*N] depthPos[1*N] depthStart[1*N]
//   note: a version is a root in lc / rc / cnt / tot; each adds log(N) nodes to its parent's
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

// Tree<long long> tree(edges, root);
//
// edges: the tree's n - 1 edges with their weights, vector<vector<int>> (vector<vector<long long>> works too). Whether
//        nodes are 0..n-1 or 1..n is detected automatically from the edge list (smallest label is 0 -> 0..n-1,
//        otherwise 1..n; with no edges, from root)
//   {{a, b, w}, ...}     e.g. {{0, 1, 5}, {1, 2, 7}}
// root: the root node (required), e.g. 0 or 1.
//
//   Tree<long long> tree({{0, 1, 5}, {1, 2, 7}}, 0);    // nodes 0..2, rooted at 0
//   Tree<long long> tree({{1, 2, 5}, {2, 3, 7}}, 1);    // nodes 1..3, rooted at 1
//
// T is the type the weights are kept in (long long, or int).
// An edge is named by its two ends in either order: (a, b) and (b, a) are the same edge. A path a..b covers the edges
// between a and b, and a subtree covers the edges below node. A search that finds an edge returns its lower end (the
// end farther from the root). A query with no edges to look at (a path a..a, a leaf's subtree) says what it returns.
// Nodes go in and come out with your labels, -1 means "none", and a label that is not in the tree throws out_of_range.
// Nothing recurses, so a 10^6-node chain is fine.
//
// How it works: every node keeps a version of a persistent segment tree over the values (by rank), holding the edges on
// its path from the root, each as its weight. A version copies its parent's and adds one value, so all of them take O(n
// log n) nodes. A path a..b is then ver[a] + ver[b] - 2 * ver[lca], and the versions walk down together: O(log n) a
// query. The values are fixed: there are no updates.
template <typename T>
struct Tree {
    int n, lo, hi, root;  // nodes are lo..hi
    // by node label: parent (-1 for the root), depth, subtree size, top of its chain, position
    HotVector<int> par, dep, sz, head, pos;
    HotVector<int> order;  // order[pos[v]] = v
    // depthPos[depthStart[d] .. depthStart[d + 1]) = the positions of the nodes at depth d, increasing
    HotVector<int> depthStart, depthPos;
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;  // what sums are kept in
    HotVector<int> lc, rc, cnt;  // the versions' nodes: children and how many values (node 0 is the empty version)
    HotVector<S> tot;  // ... and their sum
    HotVector<int> ver;  // ver[v]: the root of v's version
    HotVector<T> srt;  // the distinct values, sorted: a version is a tree over their ranks
    HotVector<T> val;  // val[v]: the weight of the edge above v (the root has none)

    // O(n * log n) -- builds the layout and a version per node; throws invalid_argument when the edges are not one tree
    // on nodes 0..n-1 or 1..n, or an edge has no weight
    template <typename E = int> Tree(const vector<vector<E>>& edges, int root) : root(root) {
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
        for (const auto& e : edges)
            if (e.size() != 3) throw invalid_argument("Tree: every edge needs its weight here, {a, b, w}");
        val.assign(hi + 1, T(0));
        for (const auto& e : edges) {
            int a = (int)e[0], b = (int)e[1];
            val[par[a] == b ? a : b] = (T)e[2];
        }
        // one version per node: its parent's, plus the weight of the edge above it (the versions share everything else)
        vector<T> sorted;  // the distinct values: a version is a tree over their ranks
        for (int i = 1; i < n; i++) sorted.push_back(val[bfs[i]]);
        sort(sorted.begin(), sorted.end());
        sorted.erase(unique(sorted.begin(), sorted.end()), sorted.end());
        srt.assign(sorted.begin(), sorted.end());
        int depth = 1;
        while ((1 << depth) < (int)srt.size()) depth++;
        size_t cap = (size_t)n * (depth + 1) + 1;  // node 0 is the empty version
        lc.assign(cap, 0), rc.assign(cap, 0), cnt.assign(cap, 0), tot.assign(cap, 0);
        ver.assign(hi + 1, 0);
        int used = 1;
        for (int k = 1; k < n; k++) {
            int v = bfs[k], prev = ver[par[v]];
            T x = val[v];
            int i = (int)(lower_bound(sorted.begin(), sorted.end(), x) - sorted.begin());
            int cur = ver[v] = used, a = 0, b = (int)srt.size() - 1;
            while (true) {
                cnt[cur] = cnt[prev] + 1, tot[cur] = tot[prev] + x;
                used++;
                if (a == b) break;
                int mid = (a + b) >> 1;
                if (i <= mid) rc[cur] = rc[prev], lc[cur] = used, prev = lc[prev], b = mid;
                else lc[cur] = lc[prev], rc[cur] = used, prev = rc[prev], a = mid + 1;
                cur = used;
            }
        }
    }

    // O(1) -- weight(a - b); a and b are the edge's two ends, in either order
    LEETCODE_NO_SANITIZE T edgeGet(int a, int b) const {
        if (a < lo || a > hi || b < lo || b > hi) bad("edgeGet");
        if (par[a] == b) return val[a];
        if (par[b] == a) return val[b];
        throw out_of_range("edgeGet: needs an edge between a and b");
    }

    // the versions whose counts add up to the edges of the path a..b: ver[a] + ver[b] - 2 * ver[lca]
    LEETCODE_NO_SANITIZE void roots(int a, int b, int& A, int& B, int& X) const {
        A = ver[a], B = ver[b], X = ver[lcaOf(a, b)];
    }

    // how many of the tree's distinct values are < x (after: <= x): the rank x would take
    LEETCODE_NO_SANITIZE int rankOf(T x, bool after) const {
        int lo = 0, hi = (int)srt.size();
        while (lo < hi) {
            int mid = (lo + hi) >> 1;
            if (srt[mid] < x || (after && !(x < srt[mid]))) lo = mid + 1;
            else hi = mid;
        }
        return lo;
    }

    // the kth smallest value of a path (1 <= k <= its size): its versions walk down together
    LEETCODE_NO_SANITIZE T kthValue(int A, int B, int X, int k) const {
        int lo = 0, hi = (int)srt.size() - 1;
        while (lo < hi) {
            int mid = (lo + hi) >> 1, left = cnt[lc[A]] + cnt[lc[B]] - 2 * cnt[lc[X]];
            if (k <= left) {
                A = lc[A], B = lc[B], X = lc[X];
                hi = mid;
            } else {
                k -= left;
                A = rc[A], B = rc[B], X = rc[X];
                lo = mid + 1;
            }
        }
        return srt[lo];
    }

    // how many of a path's values are among the r smallest distinct values of the tree; total: their sum
    LEETCODE_NO_SANITIZE int valuesBelow(int A, int B, int X, int r, S& total) const {
        int lo = 0, hi = (int)srt.size() - 1, many = 0;
        total = 0;
        if (r <= 0) return 0;
        if (r > hi) {
            total = tot[A] + tot[B] - 2 * tot[X];
            return cnt[A] + cnt[B] - 2 * cnt[X];
        }
        while (lo < hi) {
            int mid = (lo + hi) >> 1;
            if (r > mid) {  // the whole left half is wanted
                many += cnt[lc[A]] + cnt[lc[B]] - 2 * cnt[lc[X]];
                total += tot[lc[A]] + tot[lc[B]] - 2 * tot[lc[X]];
                A = rc[A], B = rc[B], X = rc[X];
                lo = mid + 1;
            } else {
                A = lc[A], B = lc[B], X = lc[X];
                hi = mid;
            }
        }
        return many;
    }

    // the sum of a path's k smallest values (0 <= k <= its size)
    LEETCODE_NO_SANITIZE S smallestSum(int A, int B, int X, int k) const {
        if (k <= 0) return 0;
        S total = 0;
        int lo = 0, hi = (int)srt.size() - 1;
        while (lo < hi) {
            int mid = (lo + hi) >> 1, left = cnt[lc[A]] + cnt[lc[B]] - 2 * cnt[lc[X]];
            if (k <= left) {
                A = lc[A], B = lc[B], X = lc[X];
                hi = mid;
            } else {
                k -= left;
                total += tot[lc[A]] + tot[lc[B]] - 2 * tot[lc[X]];
                A = rc[A], B = rc[B], X = rc[X];
                lo = mid + 1;
            }
        }
        return total + (S)k * srt[lo];
    }

    // O(log n) -- kth smallest of the edge weights on the path a..b (1-indexed: k = 1 is the min); needs 1 <= k <= the
    // path's size, else throws out_of_range
    LEETCODE_NO_SANITIZE T edgePathKthSmallest(int a, int b, int k) const {
        if (a < lo || a > hi || b < lo || b > hi) bad("edgePathKthSmallest");
        int A, B, X;
        roots(a, b, A, B, X);
        int size = cnt[A] + cnt[B] - 2 * cnt[X];
        if (k < 1 || k > size)
            throw out_of_range("edgePathKthSmallest: needs 1 <= k <= the path's size");
        return kthValue(A, B, X, k);
    }

    // O(log n) -- kth largest of the edge weights on the path a..b (1-indexed: k = 1 is the max); needs 1 <= k <= the
    // path's size, else throws out_of_range
    LEETCODE_NO_SANITIZE T edgePathKthLargest(int a, int b, int k) const {
        if (a < lo || a > hi || b < lo || b > hi) bad("edgePathKthLargest");
        int A, B, X;
        roots(a, b, A, B, X);
        int size = cnt[A] + cnt[B] - 2 * cnt[X];
        if (k < 1 || k > size)
            throw out_of_range("edgePathKthLargest: needs 1 <= k <= the path's size");
        return kthValue(A, B, X, size + 1 - k);
    }

    // O(log n) -- sum of the k smallest edge weights on the path a..b; needs 0 <= k <= the path's size, else throws
    // out_of_range
    LEETCODE_NO_SANITIZE S edgePathSumSmallestK(int a, int b, int k) const {
        if (a < lo || a > hi || b < lo || b > hi) bad("edgePathSumSmallestK");
        int A, B, X;
        roots(a, b, A, B, X);
        int size = cnt[A] + cnt[B] - 2 * cnt[X];
        if (k < 0 || k > size)
            throw out_of_range("edgePathSumSmallestK: needs 0 <= k <= the path's size");
        return smallestSum(A, B, X, k);
    }

    // O(log n) -- sum of the k largest edge weights on the path a..b; needs 0 <= k <= the path's size, else throws
    // out_of_range
    LEETCODE_NO_SANITIZE S edgePathSumLargestK(int a, int b, int k) const {
        if (a < lo || a > hi || b < lo || b > hi) bad("edgePathSumLargestK");
        int A, B, X;
        roots(a, b, A, B, X);
        int size = cnt[A] + cnt[B] - 2 * cnt[X];
        if (k < 0 || k > size)
            throw out_of_range("edgePathSumLargestK: needs 0 <= k <= the path's size");
        return tot[A] + tot[B] - 2 * tot[X] - smallestSum(A, B, X, size - k);
    }

    // O(log n) -- sum of the kFrom-th ... kTo-th smallest edge weights on the path a..b (1-indexed); needs 1 <= kFrom
    // <= kTo <= the path's size, else throws out_of_range
    LEETCODE_NO_SANITIZE S edgePathSumKthSmallestRange(int a, int b, int kFrom, int kTo) const {
        if (a < lo || a > hi || b < lo || b > hi) bad("edgePathSumKthSmallestRange");
        int A, B, X;
        roots(a, b, A, B, X);
        int size = cnt[A] + cnt[B] - 2 * cnt[X];
        if (kFrom < 1 || kFrom > kTo || kTo > size)
            throw out_of_range("edgePathSumKthSmallestRange: needs 1 <= kFrom <= kTo <= the path's size");
        return smallestSum(A, B, X, kTo) - smallestSum(A, B, X, kFrom - 1);
    }

    // O(log n) -- sum of the kFrom-th ... kTo-th largest edge weights on the path a..b (1-indexed); needs 1 <= kFrom <=
    // kTo <= the path's size, else throws out_of_range
    LEETCODE_NO_SANITIZE S edgePathSumKthLargestRange(int a, int b, int kFrom, int kTo) const {
        if (a < lo || a > hi || b < lo || b > hi) bad("edgePathSumKthLargestRange");
        int A, B, X;
        roots(a, b, A, B, X);
        int size = cnt[A] + cnt[B] - 2 * cnt[X];
        if (kFrom < 1 || kFrom > kTo || kTo > size)
            throw out_of_range("edgePathSumKthLargestRange: needs 1 <= kFrom <= kTo <= the path's size");
        return smallestSum(A, B, X, size - kFrom + 1) - smallestSum(A, B, X, size - kTo);
    }

    // O(log n) -- sum of the edge weights on the path a..b; 0 when a == b (no edges)
    LEETCODE_NO_SANITIZE S edgePathSum(int a, int b) const {
        if (a < lo || a > hi || b < lo || b > hi) bad("edgePathSum");
        int A, B, X;
        roots(a, b, A, B, X);
        return tot[A] + tot[B] - 2 * tot[X];
    }

    // O(log n) -- min edge weight on the path a..b; the largest value of its type when a == b (no edges)
    LEETCODE_NO_SANITIZE T edgePathMin(int a, int b) const {
        if (a < lo || a > hi || b < lo || b > hi) bad("edgePathMin");
        int A, B, X;
        roots(a, b, A, B, X);
        int size = cnt[A] + cnt[B] - 2 * cnt[X];
        if (size == 0) return numeric_limits<T>::max();
        return kthValue(A, B, X, 1);
    }

    // O(log n) -- max edge weight on the path a..b; the smallest value of its type when a == b (no edges)
    LEETCODE_NO_SANITIZE T edgePathMax(int a, int b) const {
        if (a < lo || a > hi || b < lo || b > hi) bad("edgePathMax");
        int A, B, X;
        roots(a, b, A, B, X);
        int size = cnt[A] + cnt[B] - 2 * cnt[X];
        if (size == 0) return numeric_limits<T>::lowest();
        return kthValue(A, B, X, size);
    }

    // O(log n) -- how many edge weights on the path a..b are < x; 0 when a == b (no edges)
    LEETCODE_NO_SANITIZE int edgePathCountLtX(int a, int b, T x) const {
        if (a < lo || a > hi || b < lo || b > hi) bad("edgePathCountLtX");
        int A, B, X;
        roots(a, b, A, B, X);
        S unused;
        return valuesBelow(A, B, X, rankOf(x, false), unused);
    }

    // O(log n) -- sum of the edge weights on the path a..b that are < x; 0 when a == b (no edges)
    LEETCODE_NO_SANITIZE S edgePathSumLtX(int a, int b, T x) const {
        if (a < lo || a > hi || b < lo || b > hi) bad("edgePathSumLtX");
        int A, B, X;
        roots(a, b, A, B, X);
        S low;
        valuesBelow(A, B, X, rankOf(x, false), low);
        return low;
    }

    // O(log n) -- how many edge weights on the path a..b are <= x; 0 when a == b (no edges)
    LEETCODE_NO_SANITIZE int edgePathCountLteX(int a, int b, T x) const {
        if (a < lo || a > hi || b < lo || b > hi) bad("edgePathCountLteX");
        int A, B, X;
        roots(a, b, A, B, X);
        S unused;
        return valuesBelow(A, B, X, rankOf(x, true), unused);
    }

    // O(log n) -- sum of the edge weights on the path a..b that are <= x; 0 when a == b (no edges)
    LEETCODE_NO_SANITIZE S edgePathSumLteX(int a, int b, T x) const {
        if (a < lo || a > hi || b < lo || b > hi) bad("edgePathSumLteX");
        int A, B, X;
        roots(a, b, A, B, X);
        S low;
        valuesBelow(A, B, X, rankOf(x, true), low);
        return low;
    }

    // O(log n) -- how many edge weights on the path a..b are > x; 0 when a == b (no edges)
    LEETCODE_NO_SANITIZE int edgePathCountGtX(int a, int b, T x) const {
        if (a < lo || a > hi || b < lo || b > hi) bad("edgePathCountGtX");
        int A, B, X;
        roots(a, b, A, B, X);
        int size = cnt[A] + cnt[B] - 2 * cnt[X];
        S unused;
        return size - valuesBelow(A, B, X, rankOf(x, true), unused);
    }

    // O(log n) -- sum of the edge weights on the path a..b that are > x; 0 when a == b (no edges)
    LEETCODE_NO_SANITIZE S edgePathSumGtX(int a, int b, T x) const {
        if (a < lo || a > hi || b < lo || b > hi) bad("edgePathSumGtX");
        int A, B, X;
        roots(a, b, A, B, X);
        S low;
        valuesBelow(A, B, X, rankOf(x, true), low);
        return tot[A] + tot[B] - 2 * tot[X] - low;
    }

    // O(log n) -- how many edge weights on the path a..b are >= x; 0 when a == b (no edges)
    LEETCODE_NO_SANITIZE int edgePathCountGteX(int a, int b, T x) const {
        if (a < lo || a > hi || b < lo || b > hi) bad("edgePathCountGteX");
        int A, B, X;
        roots(a, b, A, B, X);
        int size = cnt[A] + cnt[B] - 2 * cnt[X];
        S unused;
        return size - valuesBelow(A, B, X, rankOf(x, false), unused);
    }

    // O(log n) -- sum of the edge weights on the path a..b that are >= x; 0 when a == b (no edges)
    LEETCODE_NO_SANITIZE S edgePathSumGteX(int a, int b, T x) const {
        if (a < lo || a > hi || b < lo || b > hi) bad("edgePathSumGteX");
        int A, B, X;
        roots(a, b, A, B, X);
        S low;
        valuesBelow(A, B, X, rankOf(x, false), low);
        return tot[A] + tot[B] - 2 * tot[X] - low;
    }

    // O(log n) -- how many edge weights on the path a..b are in [low, high]; 0 when a == b (no edges)
    LEETCODE_NO_SANITIZE int edgePathCountInValRange(int a, int b, T low, T high) const {
        if (a < lo || a > hi || b < lo || b > hi) bad("edgePathCountInValRange");
        int A, B, X;
        roots(a, b, A, B, X);
        if (high < low) return 0;
        S unused;
        int upTo = valuesBelow(A, B, X, rankOf(high, true), unused);
        return upTo - valuesBelow(A, B, X, rankOf(low, false), unused);
    }

    // O(log n) -- sum of the edge weights on the path a..b in [low, high]; 0 when a == b (no edges)
    LEETCODE_NO_SANITIZE S edgePathSumInValRange(int a, int b, T low, T high) const {
        if (a < lo || a > hi || b < lo || b > hi) bad("edgePathSumInValRange");
        int A, B, X;
        roots(a, b, A, B, X);
        if (high < low) return 0;
        S upTo, under;
        valuesBelow(A, B, X, rankOf(high, true), upTo), valuesBelow(A, B, X, rankOf(low, false), under);
        return upTo - under;
    }

    // O(log n) -- how many edge weights on the path a..b equal x; 0 when a == b (no edges)
    LEETCODE_NO_SANITIZE int edgePathCountOccurrences(int a, int b, T x) const {
        if (a < lo || a > hi || b < lo || b > hi) bad("edgePathCountOccurrences");
        int A, B, X;
        roots(a, b, A, B, X);
        S unused;
        return valuesBelow(A, B, X, rankOf(x, true), unused) - valuesBelow(A, B, X, rankOf(x, false), unused);
    }

    // O(log n) -- sum of |weight - x| over the edge weights on the path a..b; 0 when a == b (no edges)
    LEETCODE_NO_SANITIZE S edgePathSumAbsDiffToX(int a, int b, T x) const {
        if (a < lo || a > hi || b < lo || b > hi) bad("edgePathSumAbsDiffToX");
        int A, B, X;
        roots(a, b, A, B, X);
        int size = cnt[A] + cnt[B] - 2 * cnt[X];
        S low;
        int many = valuesBelow(A, B, X, rankOf(x, false), low);
        return (S)x * many - low + (tot[A] + tot[B] - 2 * tot[X] - low) - (S)x * (size - many);
    }

    // O(log n) -- sum of |weight - median| over the edge weights on the path a..b (the lower median); needs at least
    // one edge (a != b), else throws out_of_range
    LEETCODE_NO_SANITIZE S edgePathSumAbsDiffToMedian(int a, int b) const {
        if (a < lo || a > hi || b < lo || b > hi) bad("edgePathSumAbsDiffToMedian");
        int A, B, X;
        roots(a, b, A, B, X);
        int size = cnt[A] + cnt[B] - 2 * cnt[X];
        if (size == 0) throw out_of_range("edgePathSumAbsDiffToMedian: needs at least one edge (a != b)");
        T x = kthValue(A, B, X, (size + 1) / 2);
        S low;
        int many = valuesBelow(A, B, X, rankOf(x, false), low);
        return (S)x * many - low + (tot[A] + tot[B] - 2 * tot[X] - low) - (S)x * (size - many);
    }

    // O(log n) -- smallest of the edge weights on the path a..b that is >= x (nullopt if none)
    LEETCODE_NO_SANITIZE optional<T> edgePathSmallestGteX(int a, int b, T x) const {
        if (a < lo || a > hi || b < lo || b > hi) bad("edgePathSmallestGteX");
        int A, B, X;
        roots(a, b, A, B, X);
        int size = cnt[A] + cnt[B] - 2 * cnt[X];
        S unused;
        int k = valuesBelow(A, B, X, rankOf(x, false), unused);
        if (k == size) return nullopt;
        return kthValue(A, B, X, k + 1);
    }

    // O(log n) -- smallest of the edge weights on the path a..b that is > x (nullopt if none)
    LEETCODE_NO_SANITIZE optional<T> edgePathSmallestGtX(int a, int b, T x) const {
        if (a < lo || a > hi || b < lo || b > hi) bad("edgePathSmallestGtX");
        int A, B, X;
        roots(a, b, A, B, X);
        int size = cnt[A] + cnt[B] - 2 * cnt[X];
        S unused;
        int k = valuesBelow(A, B, X, rankOf(x, true), unused);
        if (k == size) return nullopt;
        return kthValue(A, B, X, k + 1);
    }

    // O(log n) -- largest of the edge weights on the path a..b that is <= x (nullopt if none)
    LEETCODE_NO_SANITIZE optional<T> edgePathLargestLteX(int a, int b, T x) const {
        if (a < lo || a > hi || b < lo || b > hi) bad("edgePathLargestLteX");
        int A, B, X;
        roots(a, b, A, B, X);
        S unused;
        int k = valuesBelow(A, B, X, rankOf(x, true), unused);
        if (k == 0) return nullopt;
        return kthValue(A, B, X, k);
    }

    // O(log n) -- largest of the edge weights on the path a..b that is < x (nullopt if none)
    LEETCODE_NO_SANITIZE optional<T> edgePathLargestLtX(int a, int b, T x) const {
        if (a < lo || a > hi || b < lo || b > hi) bad("edgePathLargestLtX");
        int A, B, X;
        roots(a, b, A, B, X);
        S unused;
        int k = valuesBelow(A, B, X, rankOf(x, false), unused);
        if (k == 0) return nullopt;
        return kthValue(A, B, X, k);
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
