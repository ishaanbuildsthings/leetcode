// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/tree-queries/node-wavelet-order-stats-mex/template.cpp
// The range structure inside is https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/wavelet-order-stats-mex/fast.cpp
// @operations: countAtDepthInSubtree depth isAncestor isOnPath kthAncestor kthNodeOnPath lca lcaRootedAt median nextNodeOnPath nodeGet nodePathCountGtX nodePathCountGteX nodePathCountInValRange nodePathCountLtX nodePathCountLteX nodePathCountOccurrences nodePathLargestLtX nodePathLargestLteX nodePathMax nodePathMin nodePathSmallestGtX nodePathSmallestGteX nodeSubtreeCountGtX nodeSubtreeCountGteX nodeSubtreeCountInValRange nodeSubtreeCountLtX nodeSubtreeCountLteX nodeSubtreeCountOccurrences nodeSubtreeKthSmallest nodeSubtreeLargestLtX nodeSubtreeLargestLteX nodeSubtreeMax nodeSubtreeMex nodeSubtreeMin nodeSubtreeSmallestGtX nodeSubtreeSmallestGteX parent parentRootedAt pathIntersection pathNodes subtreeSize subtreeSizeRootedAt unweightedDist unweightedDistBetweenPaths unweightedDistToPath
// @data-structure-type: wavelet
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
//   nodeGet: 1
//   nodePathCountGtX: log^2(N)
//   nodePathCountGteX: log^2(N)
//   nodePathCountInValRange: log^2(N)
//   nodePathCountLtX: log^2(N)
//   nodePathCountLteX: log^2(N)
//   nodePathCountOccurrences: log^2(N)
//   nodePathLargestLtX: log^2(N)
//   nodePathLargestLteX: log^2(N)
//   nodePathMax: log^2(N)
//   nodePathMin: log^2(N)
//   nodePathSmallestGtX: log^2(N)
//   nodePathSmallestGteX: log^2(N)
//   nodeSubtreeCountGtX: log(N)
//   nodeSubtreeCountGteX: log(N)
//   nodeSubtreeCountInValRange: log(N)
//   nodeSubtreeCountLtX: log(N)
//   nodeSubtreeCountLteX: log(N)
//   nodeSubtreeCountOccurrences: log(N)
//   nodeSubtreeKthSmallest: log(N)
//   nodeSubtreeLargestLtX: log(N)
//   nodeSubtreeLargestLteX: log(N)
//   nodeSubtreeMax: log(N)
//   nodeSubtreeMex: log(N)
//   nodeSubtreeMin: log(N)
//   nodeSubtreeSmallestGtX: log(N)
//   nodeSubtreeSmallestGteX: log(N)
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
//   node: zeros[1*N*log(N)] arr[1*N] srt[1*N] mexRoot[1*N] ML[1*N*log(N)] MR[1*N*log(N)] MN[1*N*log(N)]
//   tags: none
//   other: par[1*N] dep[1*N] sz[1*N] head[1*N] pos[1*N] order[1*N] depthPos[1*N] depthStart[1*N]
//   note: wavelet matrix: one row of N + 1 prefix counts per bit of the compressed value; rangeMex uses a persistent seg tree over the values 0..N+1 holding each value's last index
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// FAST MODE (this is the only C++ version): sanitizers are skipped inside this template, so a bad access in it goes
// unreported. To turn that off (say, when debugging with sanitizers), put this line above the template:
//   #define LEETCODE_NO_SANITIZE
// Without sanitizers (Codeforces, a plain -O2 build) it changes nothing. It needs GCC or Clang.

// Static array. Each query treats a[l..r] (0-indexed, inclusive) as a sorted multiset. Values are compressed to ranks
// 0..m-1 once, so costs are log of the number of distinct values, never of the value range; query arguments (x,
// lowVal, ...) can be anything. Level d of the wavelet matrix (top bit first) stably splits the current order into the
// ranks with that bit 0, then 1; zeros[d][i] = # of the first i elements of level d's order with the bit 0.
// rangeMex: a persistent seg tree over the values 0..N+1; version p holds, per value, its last index before p (-1 if
// none). The mex of a[l..r] is the first value whose last index in version r + 1 is < l.
// T: int, long long, ....
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
struct WaveletMatrix {
    int n, m, bits;
    HotVector<T> arr, srt;  // srt: sorted distinct values
    HotVector<int> zeros;   // level lv's row is zeros[lv * (n + 1) .. lv * (n + 1) + n]
    HotVector<int> mexRoot, ML, MR, MN;  // the persistent mex tree

    // O(N log N) -- arr: the initial array, 0-indexed
    explicit WaveletMatrix(const vector<T>& a) : n((int)a.size()), arr(a), srt(a) {
        sort(srt.begin(), srt.end());
        srt.erase(unique(srt.begin(), srt.end()), srt.end());
        m = (int)srt.size();
        bits = 1;
        while ((1 << bits) < m) bits++;
        zeros.assign((size_t)bits * (n + 1), 0);
        vector<int> cur(n), nxt(n);
        for (int i = 0; i < n; i++) cur[i] = lb(a[i]);
        for (int lv = 0; lv < bits; lv++) {
            int d = bits - 1 - lv, k = 0, *z = &zeros[(size_t)lv * (n + 1)];
            for (int i = 0; i < n; i++) {
                bool one = (cur[i] >> d) & 1;
                z[i + 1] = z[i] + !one;
            }
            for (int v : cur) if (!((v >> d) & 1)) nxt[k++] = v;
            for (int v : cur) if ((v >> d) & 1) nxt[k++] = v;
            swap(cur, nxt);
        }
        buildMex();
    }

    // O(1) -- a[i]; needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE T pointGet(int i) const {
        if (i < 0 || i >= n) throw out_of_range("pointGet: needs 0 <= i < n");
        return arr[i];
    }

    // O(logN) -- # of i in [l, r] with a[i] == x; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE int countOccurrences(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("countOccurrences: needs 0 <= l <= r < n");
        return countInValRange(l, r, x, x);
    }

    // O(logN) -- # of i in [l, r] with lowVal <= a[i] <= highVal; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE int countInValRange(int l, int r, T lowVal, T highVal) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("countInValRange: needs 0 <= l <= r < n");
        if (highVal < lowVal) return 0;
        return countBelow(l, r, ub(highVal)) - countBelow(l, r, lb(lowVal));
    }

    // O(logN) -- # of values < x in a[l..r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE int countLtX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("countLtX: needs 0 <= l <= r < n");
        return countBelow(l, r, lb(x));
    }

    // O(logN) -- # of values <= x in a[l..r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE int countLteX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("countLteX: needs 0 <= l <= r < n");
        return countBelow(l, r, ub(x));
    }

    // O(logN) -- # of values > x in a[l..r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE int countGtX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("countGtX: needs 0 <= l <= r < n");
        return r - l + 1 - countBelow(l, r, ub(x));
    }

    // O(logN) -- # of values >= x in a[l..r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE int countGteX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("countGteX: needs 0 <= l <= r < n");
        return r - l + 1 - countBelow(l, r, lb(x));
    }

    // O(logN) -- the k-th smallest of a[l..r] (k = 1 is the min); needs 0 <= l <= r < n and 1 <= k <= r - l + 1, else
    // throws out_of_range
    LEETCODE_NO_SANITIZE T kthSmallest(int l, int r, int k) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("kthSmallest: needs 0 <= l <= r < n");
        if (k < 1 || k > r - l + 1) throw out_of_range("kthSmallest: needs 1 <= k <= r - l + 1");
        return kth(l, r, k);
    }

    // O(logN) -- min of a[l..r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE T rangeMin(int l, int r) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeMin: needs 0 <= l <= r < n");
        return kth(l, r, 1);
    }

    // O(logN) -- max of a[l..r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE T rangeMax(int l, int r) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeMax: needs 0 <= l <= r < n");
        return kth(l, r, r - l + 1);
    }

    // O(logN) -- smallest value >= x in a[l..r], or nullopt; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE optional<T> smallestGteX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("smallestGteX: needs 0 <= l <= r < n");
        int c = countBelow(l, r, lb(x));
        if (c == r - l + 1) return nullopt;
        return kth(l, r, c + 1);
    }

    // O(logN) -- smallest value > x in a[l..r], or nullopt; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE optional<T> smallestGtX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("smallestGtX: needs 0 <= l <= r < n");
        int c = countBelow(l, r, ub(x));
        if (c == r - l + 1) return nullopt;
        return kth(l, r, c + 1);
    }

    // O(logN) -- largest value <= x in a[l..r], or nullopt; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE optional<T> largestLteX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("largestLteX: needs 0 <= l <= r < n");
        int c = countBelow(l, r, ub(x));
        if (c == 0) return nullopt;
        return kth(l, r, c);
    }

    // O(logN) -- largest value < x in a[l..r], or nullopt; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE optional<T> largestLtX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("largestLtX: needs 0 <= l <= r < n");
        int c = countBelow(l, r, lb(x));
        if (c == 0) return nullopt;
        return kth(l, r, c);
    }

    // O(logN) -- smallest integer >= 0 that is not in a[l..r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE int rangeMex(int l, int r) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeMex: needs 0 <= l <= r < n");
        return mexFrom(l, r, 0);
    }

    // O(log(N)) -- min of the whole array a[0..n-1] (rangeMin(0, n - 1)); needs n >= 1, else throws out_of_range
    LEETCODE_NO_SANITIZE auto minAll() {
        if (n < 1) throw out_of_range("minAll: needs n >= 1");
        return rangeMin(0, n - 1);
    }

    // O(log(N)) -- max of the whole array a[0..n-1] (rangeMax(0, n - 1)); needs n >= 1, else throws out_of_range
    LEETCODE_NO_SANITIZE auto maxAll() {
        if (n < 1) throw out_of_range("maxAll: needs n >= 1");
        return rangeMax(0, n - 1);
    }

    // ---- internals ----

    LEETCODE_NO_SANITIZE int lb(const T& v) const { return int(lower_bound(srt.begin(), srt.end(), v) - srt.begin()); }
    LEETCODE_NO_SANITIZE int ub(const T& v) const { return int(upper_bound(srt.begin(), srt.end(), v) - srt.begin()); }
    LEETCODE_NO_SANITIZE const int* row(int lv) const { return &zeros[(size_t)lv * (n + 1)]; }

    // the k-th smallest of a[l..r], 1 <= k <= r - l + 1
    LEETCODE_NO_SANITIZE T kth(int l, int r, int k) const {
        int lo = l, hi = r + 1, rank = 0;
        for (int lv = 0; lv < bits; lv++) {
            const int* z = row(lv);
            int zl = z[lo], zh = z[hi];
            if (k <= zh - zl) lo = zl, hi = zh;  // enough 0s at this bit: the answer has it 0
            else k -= zh - zl, rank |= 1 << (bits - 1 - lv), lo = z[n] + lo - zl, hi = z[n] + hi - zh;
        }
        return srt[rank];
    }

    // # of i in [l, r] whose rank is < x
    LEETCODE_NO_SANITIZE int countBelow(int l, int r, int x) const {
        if (x <= 0) return 0;
        if (x >= m) return r - l + 1;
        int lo = l, hi = r + 1, res = 0;
        for (int lv = 0; lv < bits; lv++) {
            const int* z = row(lv);
            int zl = z[lo], zh = z[hi];
            // all 0s are below x
            if ((x >> (bits - 1 - lv)) & 1) res += zh - zl, lo = z[n] + lo - zl, hi = z[n] + hi - zh;
            else lo = zl, hi = zh;
        }
        return res;
    }

    // persistent seg tree over the values 0..n+1: version p holds, per value, its last index before p (-1: none)
    LEETCODE_NO_SANITIZE void buildMex() {
        ML.assign(1, 0), MR.assign(1, 0), MN.assign(1, -1);  // node 0 = the empty tree (every last index -1)
        mexRoot.assign(n + 1, 0);
        for (int i = 0; i < n; i++)
            mexRoot[i + 1] = T(0) <= arr[i] && arr[i] <= T(n + 1) ? mexSet(mexRoot[i], 0, n + 1, int(arr[i]),
                i) : mexRoot[i];
    }

    // copy of node with value v's last index set to i
    LEETCODE_NO_SANITIZE int mexSet(int node, int nl, int nh, int v, int i) {
        int l = ML[node], r = MR[node], x;
        if (nl == nh) x = i;
        else {
            int mid = (nl + nh) >> 1;
            if (v <= mid) l = mexSet(l, nl, mid, v, i);
            else r = mexSet(r, mid + 1, nh, v, i);
            x = min(MN[l], MN[r]);
        }
        ML.push_back(nl == nh ? 0 : l), MR.push_back(nl == nh ? 0 : r), MN.push_back(x);
        return (int)MN.size() - 1;
    }

    // smallest value >= s that is not in a[l..r]: the leftmost value >= s whose last index (as of r) is < l
    LEETCODE_NO_SANITIZE int mexFrom(int l, int r, int s) const {
        auto go = [&](auto&& self, int t, int nl, int nh) -> int {
            if (nh < s || MN[t] >= l) return -1;  // nothing allowed here, or every value here is in a[l..r]
            if (!t) return max(nl, s);            // no value here was ever seen
            if (nl == nh) return nl;
            int mid = (nl + nh) >> 1, res = self(self, ML[t], nl, mid);
            return res >= 0 ? res : self(self, MR[t], mid + 1, nh);
        };
        return go(go, mexRoot[r + 1], 0, n + 1);
    }
};

// Tree tree(edges, root, vals);
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
//
//   Tree<long long> tree({{0, 1}, {1, 2}}, 0, {10, 20, 30});       // nodes 0..2, rooted at 0
//   Tree<long long> tree({{1, 2}, {2, 3}}, 1, {0, 10, 20, 30});    // nodes 1..3, rooted at 1
//
// Nodes go in and come out with your labels, and -1 means "no such node". A label that is not in the tree throws
// out_of_range. A path a..b includes both a and b. Nothing recurses, so a 10^6-node chain is fine.
//
// How it works: one heavy-light pass gives every node a position, so that each heavy chain and each subtree is one
// stretch of positions (pos[node] .. pos[node] + sz[node] - 1). The values sit in the range structure above
// (WaveletMatrix) in position order: a subtree is one range of it, and a path a..b is O(log n) ranges, one per chain it
// crosses.
template <typename T>
struct Tree {
    int n, lo, hi, root;  // nodes are lo..hi
    // by node label: parent (-1 for the root), depth, subtree size, top of its chain, position
    HotVector<int> par, dep, sz, head, pos;
    HotVector<int> order;  // order[pos[v]] = v
    // depthPos[depthStart[d] .. depthStart[d + 1]) = the positions of the nodes at depth d, increasing
    HotVector<int> depthStart, depthPos;
    WaveletMatrix<T> seg;  // the values, in position order

    // O(n * log n) -- builds the layout and the range structure; throws invalid_argument when the edges are not one
    // tree on nodes 0..n-1 or 1..n, or vals has the wrong size
    template <typename E = int> Tree(const vector<vector<E>>& edges, int root, const vector<T>& vals)
        : seg(layout(edges, root, vals)) {}

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

    // O(1) -- val(node)
    LEETCODE_NO_SANITIZE auto nodeGet(int node) {
        if (node < lo || node > hi) bad("nodeGet");
        return seg.pointGet(pos[node]);
    }

    // O(log^2 n) -- min node value on the path a..b
    LEETCODE_NO_SANITIZE auto nodePathMin(int a, int b) {
        if (a < lo || a > hi || b < lo || b > hi) bad("nodePathMin");
        using R = decltype(seg.rangeMin(0, 0));
        R res = numeric_limits<R>::max();
        while (head[a] != head[b]) {
            if (dep[head[a]] < dep[head[b]]) {
                int t = a;
                a = b, b = t;
            }
            R v = seg.rangeMin(pos[head[a]], pos[a]);
            if (v < res) res = v;
            a = par[head[a]];
        }
        int l = pos[a], r = pos[b];
        if (l > r) {
            int t = l;
            l = r, r = t;
        }
        R v = seg.rangeMin(l, r);
        if (v < res) res = v;
        return res;
    }

    // O(log^2 n) -- max node value on the path a..b
    LEETCODE_NO_SANITIZE auto nodePathMax(int a, int b) {
        if (a < lo || a > hi || b < lo || b > hi) bad("nodePathMax");
        using R = decltype(seg.rangeMax(0, 0));
        R res = numeric_limits<R>::lowest();
        while (head[a] != head[b]) {
            if (dep[head[a]] < dep[head[b]]) {
                int t = a;
                a = b, b = t;
            }
            R v = seg.rangeMax(pos[head[a]], pos[a]);
            if (v > res) res = v;
            a = par[head[a]];
        }
        int l = pos[a], r = pos[b];
        if (l > r) {
            int t = l;
            l = r, r = t;
        }
        R v = seg.rangeMax(l, r);
        if (v > res) res = v;
        return res;
    }

    // O(log^2 n) -- how many node values on the path a..b are < x
    LEETCODE_NO_SANITIZE auto nodePathCountLtX(int a, int b, T x) {
        if (a < lo || a > hi || b < lo || b > hi) bad("nodePathCountLtX");
        using R = decltype(seg.countLtX(0, 0, x));
        R res = 0;
        while (head[a] != head[b]) {
            if (dep[head[a]] < dep[head[b]]) {
                int t = a;
                a = b, b = t;
            }
            R v = seg.countLtX(pos[head[a]], pos[a], x);
            res += v;
            a = par[head[a]];
        }
        int l = pos[a], r = pos[b];
        if (l > r) {
            int t = l;
            l = r, r = t;
        }
        R v = seg.countLtX(l, r, x);
        res += v;
        return res;
    }

    // O(log^2 n) -- how many node values on the path a..b are <= x
    LEETCODE_NO_SANITIZE auto nodePathCountLteX(int a, int b, T x) {
        if (a < lo || a > hi || b < lo || b > hi) bad("nodePathCountLteX");
        using R = decltype(seg.countLteX(0, 0, x));
        R res = 0;
        while (head[a] != head[b]) {
            if (dep[head[a]] < dep[head[b]]) {
                int t = a;
                a = b, b = t;
            }
            R v = seg.countLteX(pos[head[a]], pos[a], x);
            res += v;
            a = par[head[a]];
        }
        int l = pos[a], r = pos[b];
        if (l > r) {
            int t = l;
            l = r, r = t;
        }
        R v = seg.countLteX(l, r, x);
        res += v;
        return res;
    }

    // O(log^2 n) -- how many node values on the path a..b are > x
    LEETCODE_NO_SANITIZE auto nodePathCountGtX(int a, int b, T x) {
        if (a < lo || a > hi || b < lo || b > hi) bad("nodePathCountGtX");
        using R = decltype(seg.countGtX(0, 0, x));
        R res = 0;
        while (head[a] != head[b]) {
            if (dep[head[a]] < dep[head[b]]) {
                int t = a;
                a = b, b = t;
            }
            R v = seg.countGtX(pos[head[a]], pos[a], x);
            res += v;
            a = par[head[a]];
        }
        int l = pos[a], r = pos[b];
        if (l > r) {
            int t = l;
            l = r, r = t;
        }
        R v = seg.countGtX(l, r, x);
        res += v;
        return res;
    }

    // O(log^2 n) -- how many node values on the path a..b are >= x
    LEETCODE_NO_SANITIZE auto nodePathCountGteX(int a, int b, T x) {
        if (a < lo || a > hi || b < lo || b > hi) bad("nodePathCountGteX");
        using R = decltype(seg.countGteX(0, 0, x));
        R res = 0;
        while (head[a] != head[b]) {
            if (dep[head[a]] < dep[head[b]]) {
                int t = a;
                a = b, b = t;
            }
            R v = seg.countGteX(pos[head[a]], pos[a], x);
            res += v;
            a = par[head[a]];
        }
        int l = pos[a], r = pos[b];
        if (l > r) {
            int t = l;
            l = r, r = t;
        }
        R v = seg.countGteX(l, r, x);
        res += v;
        return res;
    }

    // O(log^2 n) -- how many node values on the path a..b are in [low, high]
    LEETCODE_NO_SANITIZE auto nodePathCountInValRange(int a, int b, T low, T high) {
        if (a < lo || a > hi || b < lo || b > hi) bad("nodePathCountInValRange");
        using R = decltype(seg.countInValRange(0, 0, low, high));
        R res = 0;
        while (head[a] != head[b]) {
            if (dep[head[a]] < dep[head[b]]) {
                int t = a;
                a = b, b = t;
            }
            R v = seg.countInValRange(pos[head[a]], pos[a], low, high);
            res += v;
            a = par[head[a]];
        }
        int l = pos[a], r = pos[b];
        if (l > r) {
            int t = l;
            l = r, r = t;
        }
        R v = seg.countInValRange(l, r, low, high);
        res += v;
        return res;
    }

    // O(log^2 n) -- smallest of the node values on the path a..b that is >= x (nullopt if none)
    LEETCODE_NO_SANITIZE auto nodePathSmallestGteX(int a, int b, T x) {
        if (a < lo || a > hi || b < lo || b > hi) bad("nodePathSmallestGteX");
        using R = decltype(seg.smallestGteX(0, 0, x));
        R res = R();
        while (head[a] != head[b]) {
            if (dep[head[a]] < dep[head[b]]) {
                int t = a;
                a = b, b = t;
            }
            R v = seg.smallestGteX(pos[head[a]], pos[a], x);
            if (v && (!res || *v < *res)) res = v;
            a = par[head[a]];
        }
        int l = pos[a], r = pos[b];
        if (l > r) {
            int t = l;
            l = r, r = t;
        }
        R v = seg.smallestGteX(l, r, x);
        if (v && (!res || *v < *res)) res = v;
        return res;
    }

    // O(log^2 n) -- smallest of the node values on the path a..b that is > x (nullopt if none)
    LEETCODE_NO_SANITIZE auto nodePathSmallestGtX(int a, int b, T x) {
        if (a < lo || a > hi || b < lo || b > hi) bad("nodePathSmallestGtX");
        using R = decltype(seg.smallestGtX(0, 0, x));
        R res = R();
        while (head[a] != head[b]) {
            if (dep[head[a]] < dep[head[b]]) {
                int t = a;
                a = b, b = t;
            }
            R v = seg.smallestGtX(pos[head[a]], pos[a], x);
            if (v && (!res || *v < *res)) res = v;
            a = par[head[a]];
        }
        int l = pos[a], r = pos[b];
        if (l > r) {
            int t = l;
            l = r, r = t;
        }
        R v = seg.smallestGtX(l, r, x);
        if (v && (!res || *v < *res)) res = v;
        return res;
    }

    // O(log^2 n) -- largest of the node values on the path a..b that is <= x (nullopt if none)
    LEETCODE_NO_SANITIZE auto nodePathLargestLteX(int a, int b, T x) {
        if (a < lo || a > hi || b < lo || b > hi) bad("nodePathLargestLteX");
        using R = decltype(seg.largestLteX(0, 0, x));
        R res = R();
        while (head[a] != head[b]) {
            if (dep[head[a]] < dep[head[b]]) {
                int t = a;
                a = b, b = t;
            }
            R v = seg.largestLteX(pos[head[a]], pos[a], x);
            if (v && (!res || *v > *res)) res = v;
            a = par[head[a]];
        }
        int l = pos[a], r = pos[b];
        if (l > r) {
            int t = l;
            l = r, r = t;
        }
        R v = seg.largestLteX(l, r, x);
        if (v && (!res || *v > *res)) res = v;
        return res;
    }

    // O(log^2 n) -- largest of the node values on the path a..b that is < x (nullopt if none)
    LEETCODE_NO_SANITIZE auto nodePathLargestLtX(int a, int b, T x) {
        if (a < lo || a > hi || b < lo || b > hi) bad("nodePathLargestLtX");
        using R = decltype(seg.largestLtX(0, 0, x));
        R res = R();
        while (head[a] != head[b]) {
            if (dep[head[a]] < dep[head[b]]) {
                int t = a;
                a = b, b = t;
            }
            R v = seg.largestLtX(pos[head[a]], pos[a], x);
            if (v && (!res || *v > *res)) res = v;
            a = par[head[a]];
        }
        int l = pos[a], r = pos[b];
        if (l > r) {
            int t = l;
            l = r, r = t;
        }
        R v = seg.largestLtX(l, r, x);
        if (v && (!res || *v > *res)) res = v;
        return res;
    }

    // O(log^2 n) -- how many node values on the path a..b equal x
    LEETCODE_NO_SANITIZE auto nodePathCountOccurrences(int a, int b, T x) {
        if (a < lo || a > hi || b < lo || b > hi) bad("nodePathCountOccurrences");
        using R = decltype(seg.countOccurrences(0, 0, x));
        R res = 0;
        while (head[a] != head[b]) {
            if (dep[head[a]] < dep[head[b]]) {
                int t = a;
                a = b, b = t;
            }
            R v = seg.countOccurrences(pos[head[a]], pos[a], x);
            res += v;
            a = par[head[a]];
        }
        int l = pos[a], r = pos[b];
        if (l > r) {
            int t = l;
            l = r, r = t;
        }
        R v = seg.countOccurrences(l, r, x);
        res += v;
        return res;
    }

    // O(log n) -- min node value in node's subtree
    LEETCODE_NO_SANITIZE auto nodeSubtreeMin(int node) {
        if (node < lo || node > hi) bad("nodeSubtreeMin");
        int l = pos[node];
        return seg.rangeMin(l, l + sz[node] - 1);
    }

    // O(log n) -- max node value in node's subtree
    LEETCODE_NO_SANITIZE auto nodeSubtreeMax(int node) {
        if (node < lo || node > hi) bad("nodeSubtreeMax");
        int l = pos[node];
        return seg.rangeMax(l, l + sz[node] - 1);
    }

    // O(log n) -- kth smallest of the node values in node's subtree (1-indexed: k = 1 is the min)
    LEETCODE_NO_SANITIZE auto nodeSubtreeKthSmallest(int node, int k) {
        if (node < lo || node > hi) bad("nodeSubtreeKthSmallest");
        int l = pos[node];
        return seg.kthSmallest(l, l + sz[node] - 1, k);
    }

    // O(log n) -- how many node values in node's subtree are < x
    LEETCODE_NO_SANITIZE auto nodeSubtreeCountLtX(int node, T x) {
        if (node < lo || node > hi) bad("nodeSubtreeCountLtX");
        int l = pos[node];
        return seg.countLtX(l, l + sz[node] - 1, x);
    }

    // O(log n) -- how many node values in node's subtree are <= x
    LEETCODE_NO_SANITIZE auto nodeSubtreeCountLteX(int node, T x) {
        if (node < lo || node > hi) bad("nodeSubtreeCountLteX");
        int l = pos[node];
        return seg.countLteX(l, l + sz[node] - 1, x);
    }

    // O(log n) -- how many node values in node's subtree are > x
    LEETCODE_NO_SANITIZE auto nodeSubtreeCountGtX(int node, T x) {
        if (node < lo || node > hi) bad("nodeSubtreeCountGtX");
        int l = pos[node];
        return seg.countGtX(l, l + sz[node] - 1, x);
    }

    // O(log n) -- how many node values in node's subtree are >= x
    LEETCODE_NO_SANITIZE auto nodeSubtreeCountGteX(int node, T x) {
        if (node < lo || node > hi) bad("nodeSubtreeCountGteX");
        int l = pos[node];
        return seg.countGteX(l, l + sz[node] - 1, x);
    }

    // O(log n) -- how many node values in node's subtree are in [low, high]
    LEETCODE_NO_SANITIZE auto nodeSubtreeCountInValRange(int node, T low, T high) {
        if (node < lo || node > hi) bad("nodeSubtreeCountInValRange");
        int l = pos[node];
        return seg.countInValRange(l, l + sz[node] - 1, low, high);
    }

    // O(log n) -- smallest of the node values in node's subtree that is >= x (nullopt if none)
    LEETCODE_NO_SANITIZE auto nodeSubtreeSmallestGteX(int node, T x) {
        if (node < lo || node > hi) bad("nodeSubtreeSmallestGteX");
        int l = pos[node];
        return seg.smallestGteX(l, l + sz[node] - 1, x);
    }

    // O(log n) -- smallest of the node values in node's subtree that is > x (nullopt if none)
    LEETCODE_NO_SANITIZE auto nodeSubtreeSmallestGtX(int node, T x) {
        if (node < lo || node > hi) bad("nodeSubtreeSmallestGtX");
        int l = pos[node];
        return seg.smallestGtX(l, l + sz[node] - 1, x);
    }

    // O(log n) -- largest of the node values in node's subtree that is <= x (nullopt if none)
    LEETCODE_NO_SANITIZE auto nodeSubtreeLargestLteX(int node, T x) {
        if (node < lo || node > hi) bad("nodeSubtreeLargestLteX");
        int l = pos[node];
        return seg.largestLteX(l, l + sz[node] - 1, x);
    }

    // O(log n) -- largest of the node values in node's subtree that is < x (nullopt if none)
    LEETCODE_NO_SANITIZE auto nodeSubtreeLargestLtX(int node, T x) {
        if (node < lo || node > hi) bad("nodeSubtreeLargestLtX");
        int l = pos[node];
        return seg.largestLtX(l, l + sz[node] - 1, x);
    }

    // O(log n) -- how many node values in node's subtree equal x
    LEETCODE_NO_SANITIZE auto nodeSubtreeCountOccurrences(int node, T x) {
        if (node < lo || node > hi) bad("nodeSubtreeCountOccurrences");
        int l = pos[node];
        return seg.countOccurrences(l, l + sz[node] - 1, x);
    }

    // O(log n) -- smallest integer >= 0 missing from the node values in node's subtree
    LEETCODE_NO_SANITIZE auto nodeSubtreeMex(int node) {
        if (node < lo || node > hi) bad("nodeSubtreeMex");
        int l = pos[node];
        return seg.rangeMex(l, l + sz[node] - 1);
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
