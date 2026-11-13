// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/tree-queries/both-bit-of-trees-order-stats/template.cpp
// The range structure inside is https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/bit-of-trees-order-stats/fast.cpp
// @operations: countAtDepthInSubtree depth edgeAdd edgeAssign edgeChmax edgeChmin edgeGet edgePathCountGtX edgePathCountGteX edgePathCountInValRange edgePathCountLtX edgePathCountLteX edgePathCountOccurrences edgePathLargestLtX edgePathLargestLteX edgePathMax edgePathMin edgePathSmallestGtX edgePathSmallestGteX edgeSubtreeCountGtX edgeSubtreeCountGteX edgeSubtreeCountInValRange edgeSubtreeCountLtX edgeSubtreeCountLteX edgeSubtreeCountOccurrences edgeSubtreeKthSmallest edgeSubtreeLargestLtX edgeSubtreeLargestLteX edgeSubtreeMax edgeSubtreeMin edgeSubtreeSmallestGtX edgeSubtreeSmallestGteX isAncestor isOnPath kthAncestor kthNodeOnPath lca lcaRootedAt median nextNodeOnPath nodeAdd nodeAssign nodeChmax nodeChmin nodeGet nodePathCountGtX nodePathCountGteX nodePathCountInValRange nodePathCountLtX nodePathCountLteX nodePathCountOccurrences nodePathLargestLtX nodePathLargestLteX nodePathMax nodePathMin nodePathSmallestGtX nodePathSmallestGteX nodeSubtreeCountGtX nodeSubtreeCountGteX nodeSubtreeCountInValRange nodeSubtreeCountLtX nodeSubtreeCountLteX nodeSubtreeCountOccurrences nodeSubtreeKthSmallest nodeSubtreeLargestLtX nodeSubtreeLargestLteX nodeSubtreeMax nodeSubtreeMin nodeSubtreeSmallestGtX nodeSubtreeSmallestGteX parent parentRootedAt pathIntersection pathNodes subtreeSize subtreeSizeRootedAt unweightedDist unweightedDistBetweenPaths unweightedDistToPath
// @data-structure-type: bit-of-trees
// @complexities:
//   countAtDepthInSubtree: log(N)
//   depth: 1
//   edgeAdd: log(N)*log(U)
//   edgeAssign: log(N)*log(U)
//   edgeChmax: log(N)*log(U)
//   edgeChmin: log(N)*log(U)
//   edgeGet: 1
//   edgePathCountGtX: log^2(N)*log(U)
//   edgePathCountGteX: log^2(N)*log(U)
//   edgePathCountInValRange: log^2(N)*log(U)
//   edgePathCountLtX: log^2(N)*log(U)
//   edgePathCountLteX: log^2(N)*log(U)
//   edgePathCountOccurrences: log^2(N)*log(U)
//   edgePathLargestLtX: log^2(N)*log(U)
//   edgePathLargestLteX: log^2(N)*log(U)
//   edgePathMax: log^2(N)*log(U)
//   edgePathMin: log^2(N)*log(U)
//   edgePathSmallestGtX: log^2(N)*log(U)
//   edgePathSmallestGteX: log^2(N)*log(U)
//   edgeSubtreeCountGtX: log(N)*log(U)
//   edgeSubtreeCountGteX: log(N)*log(U)
//   edgeSubtreeCountInValRange: log(N)*log(U)
//   edgeSubtreeCountLtX: log(N)*log(U)
//   edgeSubtreeCountLteX: log(N)*log(U)
//   edgeSubtreeCountOccurrences: log(N)*log(U)
//   edgeSubtreeKthSmallest: log(N)*log(U)
//   edgeSubtreeLargestLtX: log(N)*log(U)
//   edgeSubtreeLargestLteX: log(N)*log(U)
//   edgeSubtreeMax: log(N)*log(U)
//   edgeSubtreeMin: log(N)*log(U)
//   edgeSubtreeSmallestGtX: log(N)*log(U)
//   edgeSubtreeSmallestGteX: log(N)*log(U)
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
//   nodePathCountGtX: log^2(N)*log(U)
//   nodePathCountGteX: log^2(N)*log(U)
//   nodePathCountInValRange: log^2(N)*log(U)
//   nodePathCountLtX: log^2(N)*log(U)
//   nodePathCountLteX: log^2(N)*log(U)
//   nodePathCountOccurrences: log^2(N)*log(U)
//   nodePathLargestLtX: log^2(N)*log(U)
//   nodePathLargestLteX: log^2(N)*log(U)
//   nodePathMax: log^2(N)*log(U)
//   nodePathMin: log^2(N)*log(U)
//   nodePathSmallestGtX: log^2(N)*log(U)
//   nodePathSmallestGteX: log^2(N)*log(U)
//   nodeSubtreeCountGtX: log(N)*log(U)
//   nodeSubtreeCountGteX: log(N)*log(U)
//   nodeSubtreeCountInValRange: log(N)*log(U)
//   nodeSubtreeCountLtX: log(N)*log(U)
//   nodeSubtreeCountLteX: log(N)*log(U)
//   nodeSubtreeCountOccurrences: log(N)*log(U)
//   nodeSubtreeKthSmallest: log(N)*log(U)
//   nodeSubtreeLargestLtX: log(N)*log(U)
//   nodeSubtreeLargestLteX: log(N)*log(U)
//   nodeSubtreeMax: log(N)*log(U)
//   nodeSubtreeMin: log(N)*log(U)
//   nodeSubtreeSmallestGtX: log(N)*log(U)
//   nodeSubtreeSmallestGteX: log(N)*log(U)
//   parent: 1
//   parentRootedAt: log(N)
//   pathIntersection: log(N)
//   pathNodes: K+log(N)
//   subtreeSize: 1
//   subtreeSizeRootedAt: log(N)
//   unweightedDist: log(N)
//   unweightedDistBetweenPaths: log(N)
//   unweightedDistToPath: log(N)
//   build: N*log(N)*log(U)
// @memory:
//   layout: none
//   node: L[2*N*log(N)*log(U)] R[2*N*log(N)*log(U)] C[2*N*log(N)*log(U)]
//   tags: none
//   other: root[2*N] arr[2*N] par[1*N] dep[1*N] sz[1*N] head[1*N] pos[1*N] order[1*N] depthPos[1*N] depthStart[1*N]
//   note: BIT over positions, each BIT node a dynamic value seg tree over [valLo, valHi] (U = its size); nodes are never freed, so each point update adds up to 2 log N log U of them
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// FAST MODE (this is the only C++ version): sanitizers are skipped inside this template, so a bad access in it goes
// unreported. To turn that off (say, when debugging with sanitizers), put this line above the template:
//   #define LEETCODE_NO_SANITIZE
// Without sanitizers (Codeforces, a plain -O2 build) it changes nothing. It needs GCC or Clang.

// a[l..r] as a sorted multiset, with point updates. A Fenwick tree (BIT) over positions: BIT node j is a dynamic
// value seg tree over [valLo, valHi] holding the values of a[j - lowbit(j) .. j - 1]. The multiset of a[l..r] is the
// BIT prefix of r + 1 minus the prefix of l, so a query walks down those ~2 log N value trees together (pos adds, neg
// subtracts). Values are integers; query arguments (x, lowVal, ...) can be anything.
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
struct DynamicOrderStats {
    int n;
    long long vlo, vhi;
    HotVector<T> arr;
    HotVector<int> root;  // root[j]: BIT node j's value tree; node 0 = the empty tree
    struct Node {  // a node's fields side by side: a walk reads them together (faster than one array per field)
        int L = 0;
        int R = 0;
        int C = 0;
    };
    HotVector<Node> nd;  // node 0 = the empty tree

    // O(N log N log U) -- arr: the initial array, 0-indexed; every value a[i] ever holds must lie in [valLo, valHi]
    // (any integers, negative is fine; U = valHi - valLo + 1)
    DynamicOrderStats(const vector<T>& a, long long valLo, long long valHi)
        : n((int)a.size()), vlo(valLo), vhi(valHi), arr(a), root(n + 1, 0), nd(1) {
        for (int i = 0; i < n; i++) add(i, a[i], 1);
    }

    // O(1) -- a[i]; needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE T pointGet(long long i) const {
        if (i < 0 || i >= n) throw out_of_range("pointGet: needs 0 <= i < n");
        return arr[i];
    }

    // O(N) -- the whole array (a copy)
    LEETCODE_NO_SANITIZE vector<T> getAll() const { return arr; }

    // O(logN logU) -- a[i] = v; needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAssign(long long i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointAssign: needs 0 <= i < n");
        T old = pointGet(i);
        if (v == old) return;
        add(i, old, -1), add(i, v, 1), arr[i] = v;
    }

    // O(logN logU) -- a[i] += v; needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAdd(long long i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointAdd: needs 0 <= i < n");
        pointAssign(i, pointGet(i) + v);
    }

    // O(logN logU) -- a[i] = max(a[i], v); needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointChmax(long long i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointChmax: needs 0 <= i < n");
        pointAssign(i, max(pointGet(i), v));
    }

    // O(logN logU) -- a[i] = min(a[i], v); needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointChmin(long long i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointChmin: needs 0 <= i < n");
        pointAssign(i, min(pointGet(i), v));
    }

    // O(logN * logU) -- # of i in [l, r] with a[i] == x; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE long long countOccurrences(long long l, long long r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("countOccurrences: needs 0 <= l <= r < n");
        return countInValRange(l, r, x, x);
    }

    // O(logN * logU) -- # of i in [l, r] with lowVal <= a[i] <= highVal; needs 0 <= l <= r < n, else throws
    // out_of_range
    LEETCODE_NO_SANITIZE long long countInValRange(long long l, long long r, T lowVal, T highVal) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("countInValRange: needs 0 <= l <= r < n");
        if (highVal < lowVal) return 0;
        return countBelow(l, r, ub(highVal)) - countBelow(l, r, lb(lowVal));
    }

    // O(logN * logU) -- # of values < x in a[l..r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE long long countLtX(long long l, long long r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("countLtX: needs 0 <= l <= r < n");
        return countBelow(l, r, lb(x));
    }

    // O(logN * logU) -- # of values <= x in a[l..r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE long long countLteX(long long l, long long r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("countLteX: needs 0 <= l <= r < n");
        return countBelow(l, r, ub(x));
    }

    // O(logN * logU) -- # of values > x in a[l..r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE long long countGtX(long long l, long long r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("countGtX: needs 0 <= l <= r < n");
        return r - l + 1 - countBelow(l, r, ub(x));
    }

    // O(logN * logU) -- # of values >= x in a[l..r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE long long countGteX(long long l, long long r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("countGteX: needs 0 <= l <= r < n");
        return r - l + 1 - countBelow(l, r, lb(x));
    }

    // O(logN * logU) -- the k-th smallest of a[l..r] (k = 1 is the min); needs 0 <= l <= r < n and 1 <= k <= r - l + 1,
    // else throws out_of_range
    LEETCODE_NO_SANITIZE T kthSmallest(long long l, long long r, long long k) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("kthSmallest: needs 0 <= l <= r < n");
        if (k < 1 || k > r - l + 1) throw out_of_range("kthSmallest: needs 1 <= k <= r - l + 1");
        return kth(l, r, k);
    }

    // O(logN * logU) -- min of a[l..r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE T rangeMin(long long l, long long r) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeMin: needs 0 <= l <= r < n");
        return kth(l, r, 1);
    }

    // O(logN * logU) -- max of a[l..r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE T rangeMax(long long l, long long r) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeMax: needs 0 <= l <= r < n");
        return kth(l, r, r - l + 1);
    }

    // O(logN * logU) -- smallest value >= x in a[l..r], or nullopt; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE optional<T> smallestGteX(long long l, long long r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("smallestGteX: needs 0 <= l <= r < n");
        long long c = countBelow(l, r, lb(x));
        if (c == r - l + 1) return nullopt;
        return kth(l, r, c + 1);
    }

    // O(logN * logU) -- smallest value > x in a[l..r], or nullopt; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE optional<T> smallestGtX(long long l, long long r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("smallestGtX: needs 0 <= l <= r < n");
        long long c = countBelow(l, r, ub(x));
        if (c == r - l + 1) return nullopt;
        return kth(l, r, c + 1);
    }

    // O(logN * logU) -- largest value <= x in a[l..r], or nullopt; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE optional<T> largestLteX(long long l, long long r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("largestLteX: needs 0 <= l <= r < n");
        long long c = countBelow(l, r, ub(x));
        if (c == 0) return nullopt;
        return kth(l, r, c);
    }

    // O(logN * logU) -- largest value < x in a[l..r], or nullopt; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE optional<T> largestLtX(long long l, long long r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("largestLtX: needs 0 <= l <= r < n");
        long long c = countBelow(l, r, lb(x));
        if (c == 0) return nullopt;
        return kth(l, r, c);
    }

    // O(log(N)*log(U)) -- min of the whole array a[0..n-1] (rangeMin(0, n - 1)); needs n >= 1, else throws out_of_range
    LEETCODE_NO_SANITIZE auto minAll() {
        if (n < 1) throw out_of_range("minAll: needs n >= 1");
        return rangeMin(0, n - 1);
    }

    // O(log(N)*log(U)) -- max of the whole array a[0..n-1] (rangeMax(0, n - 1)); needs n >= 1, else throws out_of_range
    LEETCODE_NO_SANITIZE auto maxAll() {
        if (n < 1) throw out_of_range("maxAll: needs n >= 1");
        return rangeMax(0, n - 1);
    }

    // ---- internals ----

    // a[i] = v gains d copies in every BIT node covering i
    LEETCODE_NO_SANITIZE void add(long long i, T v, int d) {
        for (long long j = i + 1; j <= n; j += j & -j) root[j] = ins(root[j], v, d);
    }

    // trees to add / subtract for a[l..r]
    LEETCODE_NO_SANITIZE void sides(long long l, long long r, vector<int>& pos, vector<int>& neg) const {
        for (long long j = r + 1; j; j &= j - 1) pos.push_back(root[j]);
        for (long long j = l; j; j &= j - 1) neg.push_back(root[j]);
    }

    // the k-th smallest of a[l..r], 1 <= k <= r - l + 1
    LEETCODE_NO_SANITIZE T kth(long long l, long long r, long long k) const {
        vector<int> pos, neg;
        sides(l, r, pos, neg);
        return kthIn(pos, neg, k);
    }

    // # of values < x in a[l..r]
    LEETCODE_NO_SANITIZE long long countBelow(long long l, long long r, long long x) const {
        if (x <= vlo) return 0;
        if (x > vhi) return r - l + 1;
        vector<int> pos, neg;
        sides(l, r, pos, neg);
        return belowIn(pos, neg, x);
    }

    // ---- internals: walks over the value trees in pos (added) and neg (subtracted) ----

    // a value threshold as "values < this": lb(x) = x, ub(x) = x + 1 (integers)
    LEETCODE_NO_SANITIZE static long long lb(T x) { return (long long)x; }
    LEETCODE_NO_SANITIZE static long long ub(T x) { return (long long)x + 1; }

    LEETCODE_NO_SANITIZE int newNode() {
        Node n;
        n.L = 0, n.R = 0, n.C = 0;
        nd.push_back(n);
        return (int)nd.size() - 1;
    }

    // tree t (0: a new one) with d more copies of v
    LEETCODE_NO_SANITIZE int ins(int t, T v, int d) {
        if (!t) t = newNode();
        int top = t;
        long long nl = vlo, nh = vhi;
        while (true) {
            nd[t].C += d;
            if (nl == nh) return top;
            long long mid = nl + (nh - nl) / 2;
            if (v <= mid) {
                if (!nd[t].L) { int x = newNode(); nd[t].L = x; }
                t = nd[t].L, nh = mid;
            } else {
                if (!nd[t].R) { int x = newNode(); nd[t].R = x; }
                t = nd[t].R, nl = mid + 1;
            }
        }
    }

    // get(t): node t's field
    template <class F> auto total(const vector<int>& pos, const vector<int>& neg, F get) const {
        decltype(get(0)) s = 0;
        for (int t : pos) s += get(t);
        for (int t : neg) s -= get(t);
        return s;
    }
    LEETCODE_NO_SANITIZE void goLeft(vector<int>& v) const { for (int& t : v) t = nd[t].L; }
    LEETCODE_NO_SANITIZE void goRight(vector<int>& v) const { for (int& t : v) t = nd[t].R; }
    LEETCODE_NO_SANITIZE long long leftCount(const vector<int>& pos, const vector<int>& neg) const {
        long long c = 0;
        for (int t : pos) c += nd[nd[t].L].C;
        for (int t : neg) c -= nd[nd[t].L].C;
        return c;
    }

    // the k-th smallest value, 1 <= k <= the trees' count
    LEETCODE_NO_SANITIZE T kthIn(vector<int> pos, vector<int> neg, long long k) const {
        long long nl = vlo, nh = vhi;
        while (nl != nh) {
            long long mid = nl + (nh - nl) / 2, c = leftCount(pos, neg);
            if (k <= c) goLeft(pos), goLeft(neg), nh = mid;
            else k -= c, goRight(pos), goRight(neg), nl = mid + 1;
        }
        return T(nl);
    }

    // # of values < x, valLo < x <= valHi
    LEETCODE_NO_SANITIZE long long belowIn(vector<int> pos, vector<int> neg, long long x) const {
        long long nl = vlo, nh = vhi, cnt = 0;
        while (nl != nh) {
            long long mid = nl + (nh - nl) / 2;
            if (x <= mid) goLeft(pos), goLeft(neg), nh = mid;
            else {  // the whole left half is below x
                cnt += leftCount(pos, neg);
                goRight(pos), goRight(neg), nl = mid + 1;
            }
        }
        return cnt;
    }
};

// Tree tree(edges, root, vals, valLo, valHi);
//
// edges: the tree's n - 1 edges with their weights, vector<vector<int>> (vector<vector<long long>> works too). Whether
//        nodes are 0..n-1 or 1..n is detected automatically from the edge list (smallest label is 0 -> 0..n-1,
//        otherwise 1..n; with no edges, from root)
//   {{a, b, w}, ...}     e.g. {{0, 1, 5}, {1, 2, 7}}
// root: the root node (required), e.g. 0 or 1.
// vals: the node values, vector<T> (T = long long, or int; the weights are kept as T too), vals[node] is node's value
//   nodes 0..n-1: size n        e.g. n = 3: {10, 20, 30}         node 0 -> 10
//   nodes 1..n:   size n + 1    e.g. n = 3: {0, 10, 20, 30}      vals[0] is ignored, node 1 -> 10
// valLo: every value ever held is >= valLo (any integer, negative is fine).
// valHi: every value ever held is <= valHi.
//
//   Tree<long long> tree({{0, 1, 5}, {1, 2, 7}}, 0, {10, 20, 30}, valLo, valHi);       // nodes 0..2, rooted at 0
//   Tree<long long> tree({{1, 2, 5}, {2, 3, 7}}, 1, {0, 10, 20, 30}, valLo, valHi);    // nodes 1..3, rooted at 1
//
// The node... ops act on the node values and the edge... ops on the edge weights: the two never affect each other. For
// nodes, a path a..b includes both a and b. For edges, a path a..b covers the edges between a and b and a subtree the
// edges below node; an edge is named by its two ends in either order, a search that finds an edge returns its lower end
// (the end farther from the root), and a query with no edges to look at (a path a..a, a leaf's subtree) says what it
// returns. Nodes go in and come out with your labels, -1 means "none", and a label that is not in the tree throws
// out_of_range. Nothing recurses, so a 10^6-node chain is fine.
//
// How it works: one heavy-light pass gives every node a position, so that each heavy chain and each subtree is one
// stretch of positions (pos[node] .. pos[node] + sz[node] - 1). Two copies of the range structure above
// (DynamicOrderStats) sit over those positions: nodeSeg holds each node's value at its position, edgeSeg each edge's
// weight at its lower end's position (the root's holds no edge). A subtree is one range, and a path a..b is O(log n)
// ranges, one per chain it crosses.
template <typename T>
struct Tree {
    int n, lo, hi, root;  // nodes are lo..hi
    // by node label: parent (-1 for the root), depth, subtree size, top of its chain, position
    HotVector<int> par, dep, sz, head, pos;
    HotVector<int> order;  // order[pos[v]] = v
    // depthPos[depthStart[d] .. depthStart[d + 1]) = the positions of the nodes at depth d, increasing
    HotVector<int> depthStart, depthPos;
    DynamicOrderStats<T> nodeSeg;  // the node values, in position order
    DynamicOrderStats<T> edgeSeg;  // each edge's weight, at its lower end's position

    // O(n * log n * log U) -- builds the layout and the two range structures; throws invalid_argument when the edges
    // are not one tree on nodes 0..n-1 or 1..n, an edge has no weight, or vals has the wrong size
    template <typename E = int> Tree(const vector<vector<E>>& edges, int root, const vector<T>& vals,
                                    long long valLo, long long valHi)
        : nodeSeg(layout(edges, root, vals), valLo, valHi), edgeSeg(weights(edges), valLo, valHi) {}

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

    // O(1) -- val(node)
    LEETCODE_NO_SANITIZE auto nodeGet(int node) {
        if (node < lo || node > hi) bad("nodeGet");
        return nodeSeg.pointGet(pos[node]);
    }

    // O(log n * log U) -- val(node) = x
    LEETCODE_NO_SANITIZE void nodeAssign(int node, T x) {
        if (node < lo || node > hi) bad("nodeAssign");
        nodeSeg.pointAssign(pos[node], x);
    }

    // O(log n * log U) -- val(node) += x
    LEETCODE_NO_SANITIZE void nodeAdd(int node, T x) {
        if (node < lo || node > hi) bad("nodeAdd");
        nodeSeg.pointAdd(pos[node], x);
    }

    // O(log n * log U) -- val(node) = max(val, x)
    LEETCODE_NO_SANITIZE void nodeChmax(int node, T x) {
        if (node < lo || node > hi) bad("nodeChmax");
        nodeSeg.pointChmax(pos[node], x);
    }

    // O(log n * log U) -- val(node) = min(val, x)
    LEETCODE_NO_SANITIZE void nodeChmin(int node, T x) {
        if (node < lo || node > hi) bad("nodeChmin");
        nodeSeg.pointChmin(pos[node], x);
    }

    // O(log^2 n * log U) -- min node value on the path a..b
    LEETCODE_NO_SANITIZE auto nodePathMin(int a, int b) {
        if (a < lo || a > hi || b < lo || b > hi) bad("nodePathMin");
        using R = decltype(nodeSeg.rangeMin(0, 0));
        R res = numeric_limits<R>::max();
        while (head[a] != head[b]) {
            if (dep[head[a]] < dep[head[b]]) {
                int t = a;
                a = b, b = t;
            }
            R v = nodeSeg.rangeMin(pos[head[a]], pos[a]);
            if (v < res) res = v;
            a = par[head[a]];
        }
        int l = pos[a], r = pos[b];
        if (l > r) {
            int t = l;
            l = r, r = t;
        }
        R v = nodeSeg.rangeMin(l, r);
        if (v < res) res = v;
        return res;
    }

    // O(log^2 n * log U) -- max node value on the path a..b
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

    // O(log^2 n * log U) -- how many node values on the path a..b are < x
    LEETCODE_NO_SANITIZE auto nodePathCountLtX(int a, int b, T x) {
        if (a < lo || a > hi || b < lo || b > hi) bad("nodePathCountLtX");
        using R = decltype(nodeSeg.countLtX(0, 0, x));
        R res = 0;
        while (head[a] != head[b]) {
            if (dep[head[a]] < dep[head[b]]) {
                int t = a;
                a = b, b = t;
            }
            R v = nodeSeg.countLtX(pos[head[a]], pos[a], x);
            res += v;
            a = par[head[a]];
        }
        int l = pos[a], r = pos[b];
        if (l > r) {
            int t = l;
            l = r, r = t;
        }
        R v = nodeSeg.countLtX(l, r, x);
        res += v;
        return res;
    }

    // O(log^2 n * log U) -- how many node values on the path a..b are <= x
    LEETCODE_NO_SANITIZE auto nodePathCountLteX(int a, int b, T x) {
        if (a < lo || a > hi || b < lo || b > hi) bad("nodePathCountLteX");
        using R = decltype(nodeSeg.countLteX(0, 0, x));
        R res = 0;
        while (head[a] != head[b]) {
            if (dep[head[a]] < dep[head[b]]) {
                int t = a;
                a = b, b = t;
            }
            R v = nodeSeg.countLteX(pos[head[a]], pos[a], x);
            res += v;
            a = par[head[a]];
        }
        int l = pos[a], r = pos[b];
        if (l > r) {
            int t = l;
            l = r, r = t;
        }
        R v = nodeSeg.countLteX(l, r, x);
        res += v;
        return res;
    }

    // O(log^2 n * log U) -- how many node values on the path a..b are > x
    LEETCODE_NO_SANITIZE auto nodePathCountGtX(int a, int b, T x) {
        if (a < lo || a > hi || b < lo || b > hi) bad("nodePathCountGtX");
        using R = decltype(nodeSeg.countGtX(0, 0, x));
        R res = 0;
        while (head[a] != head[b]) {
            if (dep[head[a]] < dep[head[b]]) {
                int t = a;
                a = b, b = t;
            }
            R v = nodeSeg.countGtX(pos[head[a]], pos[a], x);
            res += v;
            a = par[head[a]];
        }
        int l = pos[a], r = pos[b];
        if (l > r) {
            int t = l;
            l = r, r = t;
        }
        R v = nodeSeg.countGtX(l, r, x);
        res += v;
        return res;
    }

    // O(log^2 n * log U) -- how many node values on the path a..b are >= x
    LEETCODE_NO_SANITIZE auto nodePathCountGteX(int a, int b, T x) {
        if (a < lo || a > hi || b < lo || b > hi) bad("nodePathCountGteX");
        using R = decltype(nodeSeg.countGteX(0, 0, x));
        R res = 0;
        while (head[a] != head[b]) {
            if (dep[head[a]] < dep[head[b]]) {
                int t = a;
                a = b, b = t;
            }
            R v = nodeSeg.countGteX(pos[head[a]], pos[a], x);
            res += v;
            a = par[head[a]];
        }
        int l = pos[a], r = pos[b];
        if (l > r) {
            int t = l;
            l = r, r = t;
        }
        R v = nodeSeg.countGteX(l, r, x);
        res += v;
        return res;
    }

    // O(log^2 n * log U) -- how many node values on the path a..b are in [low, high]
    LEETCODE_NO_SANITIZE auto nodePathCountInValRange(int a, int b, T low, T high) {
        if (a < lo || a > hi || b < lo || b > hi) bad("nodePathCountInValRange");
        using R = decltype(nodeSeg.countInValRange(0, 0, low, high));
        R res = 0;
        while (head[a] != head[b]) {
            if (dep[head[a]] < dep[head[b]]) {
                int t = a;
                a = b, b = t;
            }
            R v = nodeSeg.countInValRange(pos[head[a]], pos[a], low, high);
            res += v;
            a = par[head[a]];
        }
        int l = pos[a], r = pos[b];
        if (l > r) {
            int t = l;
            l = r, r = t;
        }
        R v = nodeSeg.countInValRange(l, r, low, high);
        res += v;
        return res;
    }

    // O(log^2 n * log U) -- smallest of the node values on the path a..b that is >= x (nullopt if none)
    LEETCODE_NO_SANITIZE auto nodePathSmallestGteX(int a, int b, T x) {
        if (a < lo || a > hi || b < lo || b > hi) bad("nodePathSmallestGteX");
        using R = decltype(nodeSeg.smallestGteX(0, 0, x));
        R res = R();
        while (head[a] != head[b]) {
            if (dep[head[a]] < dep[head[b]]) {
                int t = a;
                a = b, b = t;
            }
            R v = nodeSeg.smallestGteX(pos[head[a]], pos[a], x);
            if (v && (!res || *v < *res)) res = v;
            a = par[head[a]];
        }
        int l = pos[a], r = pos[b];
        if (l > r) {
            int t = l;
            l = r, r = t;
        }
        R v = nodeSeg.smallestGteX(l, r, x);
        if (v && (!res || *v < *res)) res = v;
        return res;
    }

    // O(log^2 n * log U) -- smallest of the node values on the path a..b that is > x (nullopt if none)
    LEETCODE_NO_SANITIZE auto nodePathSmallestGtX(int a, int b, T x) {
        if (a < lo || a > hi || b < lo || b > hi) bad("nodePathSmallestGtX");
        using R = decltype(nodeSeg.smallestGtX(0, 0, x));
        R res = R();
        while (head[a] != head[b]) {
            if (dep[head[a]] < dep[head[b]]) {
                int t = a;
                a = b, b = t;
            }
            R v = nodeSeg.smallestGtX(pos[head[a]], pos[a], x);
            if (v && (!res || *v < *res)) res = v;
            a = par[head[a]];
        }
        int l = pos[a], r = pos[b];
        if (l > r) {
            int t = l;
            l = r, r = t;
        }
        R v = nodeSeg.smallestGtX(l, r, x);
        if (v && (!res || *v < *res)) res = v;
        return res;
    }

    // O(log^2 n * log U) -- largest of the node values on the path a..b that is <= x (nullopt if none)
    LEETCODE_NO_SANITIZE auto nodePathLargestLteX(int a, int b, T x) {
        if (a < lo || a > hi || b < lo || b > hi) bad("nodePathLargestLteX");
        using R = decltype(nodeSeg.largestLteX(0, 0, x));
        R res = R();
        while (head[a] != head[b]) {
            if (dep[head[a]] < dep[head[b]]) {
                int t = a;
                a = b, b = t;
            }
            R v = nodeSeg.largestLteX(pos[head[a]], pos[a], x);
            if (v && (!res || *v > *res)) res = v;
            a = par[head[a]];
        }
        int l = pos[a], r = pos[b];
        if (l > r) {
            int t = l;
            l = r, r = t;
        }
        R v = nodeSeg.largestLteX(l, r, x);
        if (v && (!res || *v > *res)) res = v;
        return res;
    }

    // O(log^2 n * log U) -- largest of the node values on the path a..b that is < x (nullopt if none)
    LEETCODE_NO_SANITIZE auto nodePathLargestLtX(int a, int b, T x) {
        if (a < lo || a > hi || b < lo || b > hi) bad("nodePathLargestLtX");
        using R = decltype(nodeSeg.largestLtX(0, 0, x));
        R res = R();
        while (head[a] != head[b]) {
            if (dep[head[a]] < dep[head[b]]) {
                int t = a;
                a = b, b = t;
            }
            R v = nodeSeg.largestLtX(pos[head[a]], pos[a], x);
            if (v && (!res || *v > *res)) res = v;
            a = par[head[a]];
        }
        int l = pos[a], r = pos[b];
        if (l > r) {
            int t = l;
            l = r, r = t;
        }
        R v = nodeSeg.largestLtX(l, r, x);
        if (v && (!res || *v > *res)) res = v;
        return res;
    }

    // O(log^2 n * log U) -- how many node values on the path a..b equal x
    LEETCODE_NO_SANITIZE auto nodePathCountOccurrences(int a, int b, T x) {
        if (a < lo || a > hi || b < lo || b > hi) bad("nodePathCountOccurrences");
        using R = decltype(nodeSeg.countOccurrences(0, 0, x));
        R res = 0;
        while (head[a] != head[b]) {
            if (dep[head[a]] < dep[head[b]]) {
                int t = a;
                a = b, b = t;
            }
            R v = nodeSeg.countOccurrences(pos[head[a]], pos[a], x);
            res += v;
            a = par[head[a]];
        }
        int l = pos[a], r = pos[b];
        if (l > r) {
            int t = l;
            l = r, r = t;
        }
        R v = nodeSeg.countOccurrences(l, r, x);
        res += v;
        return res;
    }

    // O(log n * log U) -- min node value in node's subtree
    LEETCODE_NO_SANITIZE auto nodeSubtreeMin(int node) {
        if (node < lo || node > hi) bad("nodeSubtreeMin");
        int l = pos[node];
        return nodeSeg.rangeMin(l, l + sz[node] - 1);
    }

    // O(log n * log U) -- max node value in node's subtree
    LEETCODE_NO_SANITIZE auto nodeSubtreeMax(int node) {
        if (node < lo || node > hi) bad("nodeSubtreeMax");
        int l = pos[node];
        return nodeSeg.rangeMax(l, l + sz[node] - 1);
    }

    // O(log n * log U) -- kth smallest of the node values in node's subtree (1-indexed: k = 1 is the min)
    LEETCODE_NO_SANITIZE auto nodeSubtreeKthSmallest(int node, long long k) {
        if (node < lo || node > hi) bad("nodeSubtreeKthSmallest");
        int l = pos[node];
        return nodeSeg.kthSmallest(l, l + sz[node] - 1, k);
    }

    // O(log n * log U) -- how many node values in node's subtree are < x
    LEETCODE_NO_SANITIZE auto nodeSubtreeCountLtX(int node, T x) {
        if (node < lo || node > hi) bad("nodeSubtreeCountLtX");
        int l = pos[node];
        return nodeSeg.countLtX(l, l + sz[node] - 1, x);
    }

    // O(log n * log U) -- how many node values in node's subtree are <= x
    LEETCODE_NO_SANITIZE auto nodeSubtreeCountLteX(int node, T x) {
        if (node < lo || node > hi) bad("nodeSubtreeCountLteX");
        int l = pos[node];
        return nodeSeg.countLteX(l, l + sz[node] - 1, x);
    }

    // O(log n * log U) -- how many node values in node's subtree are > x
    LEETCODE_NO_SANITIZE auto nodeSubtreeCountGtX(int node, T x) {
        if (node < lo || node > hi) bad("nodeSubtreeCountGtX");
        int l = pos[node];
        return nodeSeg.countGtX(l, l + sz[node] - 1, x);
    }

    // O(log n * log U) -- how many node values in node's subtree are >= x
    LEETCODE_NO_SANITIZE auto nodeSubtreeCountGteX(int node, T x) {
        if (node < lo || node > hi) bad("nodeSubtreeCountGteX");
        int l = pos[node];
        return nodeSeg.countGteX(l, l + sz[node] - 1, x);
    }

    // O(log n * log U) -- how many node values in node's subtree are in [low, high]
    LEETCODE_NO_SANITIZE auto nodeSubtreeCountInValRange(int node, T low, T high) {
        if (node < lo || node > hi) bad("nodeSubtreeCountInValRange");
        int l = pos[node];
        return nodeSeg.countInValRange(l, l + sz[node] - 1, low, high);
    }

    // O(log n * log U) -- smallest of the node values in node's subtree that is >= x (nullopt if none)
    LEETCODE_NO_SANITIZE auto nodeSubtreeSmallestGteX(int node, T x) {
        if (node < lo || node > hi) bad("nodeSubtreeSmallestGteX");
        int l = pos[node];
        return nodeSeg.smallestGteX(l, l + sz[node] - 1, x);
    }

    // O(log n * log U) -- smallest of the node values in node's subtree that is > x (nullopt if none)
    LEETCODE_NO_SANITIZE auto nodeSubtreeSmallestGtX(int node, T x) {
        if (node < lo || node > hi) bad("nodeSubtreeSmallestGtX");
        int l = pos[node];
        return nodeSeg.smallestGtX(l, l + sz[node] - 1, x);
    }

    // O(log n * log U) -- largest of the node values in node's subtree that is <= x (nullopt if none)
    LEETCODE_NO_SANITIZE auto nodeSubtreeLargestLteX(int node, T x) {
        if (node < lo || node > hi) bad("nodeSubtreeLargestLteX");
        int l = pos[node];
        return nodeSeg.largestLteX(l, l + sz[node] - 1, x);
    }

    // O(log n * log U) -- largest of the node values in node's subtree that is < x (nullopt if none)
    LEETCODE_NO_SANITIZE auto nodeSubtreeLargestLtX(int node, T x) {
        if (node < lo || node > hi) bad("nodeSubtreeLargestLtX");
        int l = pos[node];
        return nodeSeg.largestLtX(l, l + sz[node] - 1, x);
    }

    // O(log n * log U) -- how many node values in node's subtree equal x
    LEETCODE_NO_SANITIZE auto nodeSubtreeCountOccurrences(int node, T x) {
        if (node < lo || node > hi) bad("nodeSubtreeCountOccurrences");
        int l = pos[node];
        return nodeSeg.countOccurrences(l, l + sz[node] - 1, x);
    }

    // the position that holds the edge a - b: its lower end's (a and b in either order)
    LEETCODE_NO_SANITIZE int edgeAt(const char* name, int a, int b) const {
        if (a < lo || a > hi || b < lo || b > hi) bad(name);
        if (par[a] == b) return pos[a];
        if (par[b] == a) return pos[b];
        throw out_of_range(string(name) + ": needs an edge between a and b");
    }

    // O(1) -- weight(a - b); a and b are the edge's two ends, in either order
    LEETCODE_NO_SANITIZE auto edgeGet(int a, int b) {
        return edgeSeg.pointGet(edgeAt("edgeGet", a, b));
    }

    // O(log n * log U) -- weight(a - b) = w; a and b are the edge's two ends, in either order
    LEETCODE_NO_SANITIZE void edgeAssign(int a, int b, T w) {
        edgeSeg.pointAssign(edgeAt("edgeAssign", a, b), w);
    }

    // O(log n * log U) -- weight(a - b) += w; a and b are the edge's two ends, in either order
    LEETCODE_NO_SANITIZE void edgeAdd(int a, int b, T w) {
        edgeSeg.pointAdd(edgeAt("edgeAdd", a, b), w);
    }

    // O(log n * log U) -- weight(a - b) = max(weight, w); a and b are the edge's two ends, in either order
    LEETCODE_NO_SANITIZE void edgeChmax(int a, int b, T w) {
        edgeSeg.pointChmax(edgeAt("edgeChmax", a, b), w);
    }

    // O(log n * log U) -- weight(a - b) = min(weight, w); a and b are the edge's two ends, in either order
    LEETCODE_NO_SANITIZE void edgeChmin(int a, int b, T w) {
        edgeSeg.pointChmin(edgeAt("edgeChmin", a, b), w);
    }

    // O(log^2 n * log U) -- min edge weight on the path a..b; the largest value of its type when a == b (no edges)
    LEETCODE_NO_SANITIZE auto edgePathMin(int a, int b) {
        if (a < lo || a > hi || b < lo || b > hi) bad("edgePathMin");
        using R = decltype(edgeSeg.rangeMin(0, 0));
        R res = numeric_limits<R>::max();
        while (head[a] != head[b]) {
            if (dep[head[a]] < dep[head[b]]) {
                int t = a;
                a = b, b = t;
            }
            R v = edgeSeg.rangeMin(pos[head[a]], pos[a]);
            if (v < res) res = v;
            a = par[head[a]];
        }
        int l = pos[a], r = pos[b];
        if (l > r) {
            int t = l;
            l = r, r = t;
        }
        if (l < r) {  // (the lca's own position is the edge above it)
            R v = edgeSeg.rangeMin(l + 1, r);
            if (v < res) res = v;
        }
        return res;
    }

    // O(log^2 n * log U) -- max edge weight on the path a..b; the smallest value of its type when a == b (no edges)
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

    // O(log^2 n * log U) -- how many edge weights on the path a..b are < x; 0 when a == b (no edges)
    LEETCODE_NO_SANITIZE auto edgePathCountLtX(int a, int b, T x) {
        if (a < lo || a > hi || b < lo || b > hi) bad("edgePathCountLtX");
        using R = decltype(edgeSeg.countLtX(0, 0, x));
        R res = 0;
        while (head[a] != head[b]) {
            if (dep[head[a]] < dep[head[b]]) {
                int t = a;
                a = b, b = t;
            }
            R v = edgeSeg.countLtX(pos[head[a]], pos[a], x);
            res += v;
            a = par[head[a]];
        }
        int l = pos[a], r = pos[b];
        if (l > r) {
            int t = l;
            l = r, r = t;
        }
        if (l < r) {  // (the lca's own position is the edge above it)
            R v = edgeSeg.countLtX(l + 1, r, x);
            res += v;
        }
        return res;
    }

    // O(log^2 n * log U) -- how many edge weights on the path a..b are <= x; 0 when a == b (no edges)
    LEETCODE_NO_SANITIZE auto edgePathCountLteX(int a, int b, T x) {
        if (a < lo || a > hi || b < lo || b > hi) bad("edgePathCountLteX");
        using R = decltype(edgeSeg.countLteX(0, 0, x));
        R res = 0;
        while (head[a] != head[b]) {
            if (dep[head[a]] < dep[head[b]]) {
                int t = a;
                a = b, b = t;
            }
            R v = edgeSeg.countLteX(pos[head[a]], pos[a], x);
            res += v;
            a = par[head[a]];
        }
        int l = pos[a], r = pos[b];
        if (l > r) {
            int t = l;
            l = r, r = t;
        }
        if (l < r) {  // (the lca's own position is the edge above it)
            R v = edgeSeg.countLteX(l + 1, r, x);
            res += v;
        }
        return res;
    }

    // O(log^2 n * log U) -- how many edge weights on the path a..b are > x; 0 when a == b (no edges)
    LEETCODE_NO_SANITIZE auto edgePathCountGtX(int a, int b, T x) {
        if (a < lo || a > hi || b < lo || b > hi) bad("edgePathCountGtX");
        using R = decltype(edgeSeg.countGtX(0, 0, x));
        R res = 0;
        while (head[a] != head[b]) {
            if (dep[head[a]] < dep[head[b]]) {
                int t = a;
                a = b, b = t;
            }
            R v = edgeSeg.countGtX(pos[head[a]], pos[a], x);
            res += v;
            a = par[head[a]];
        }
        int l = pos[a], r = pos[b];
        if (l > r) {
            int t = l;
            l = r, r = t;
        }
        if (l < r) {  // (the lca's own position is the edge above it)
            R v = edgeSeg.countGtX(l + 1, r, x);
            res += v;
        }
        return res;
    }

    // O(log^2 n * log U) -- how many edge weights on the path a..b are >= x; 0 when a == b (no edges)
    LEETCODE_NO_SANITIZE auto edgePathCountGteX(int a, int b, T x) {
        if (a < lo || a > hi || b < lo || b > hi) bad("edgePathCountGteX");
        using R = decltype(edgeSeg.countGteX(0, 0, x));
        R res = 0;
        while (head[a] != head[b]) {
            if (dep[head[a]] < dep[head[b]]) {
                int t = a;
                a = b, b = t;
            }
            R v = edgeSeg.countGteX(pos[head[a]], pos[a], x);
            res += v;
            a = par[head[a]];
        }
        int l = pos[a], r = pos[b];
        if (l > r) {
            int t = l;
            l = r, r = t;
        }
        if (l < r) {  // (the lca's own position is the edge above it)
            R v = edgeSeg.countGteX(l + 1, r, x);
            res += v;
        }
        return res;
    }

    // O(log^2 n * log U) -- how many edge weights on the path a..b are in [low, high]; 0 when a == b (no edges)
    LEETCODE_NO_SANITIZE auto edgePathCountInValRange(int a, int b, T low, T high) {
        if (a < lo || a > hi || b < lo || b > hi) bad("edgePathCountInValRange");
        using R = decltype(edgeSeg.countInValRange(0, 0, low, high));
        R res = 0;
        while (head[a] != head[b]) {
            if (dep[head[a]] < dep[head[b]]) {
                int t = a;
                a = b, b = t;
            }
            R v = edgeSeg.countInValRange(pos[head[a]], pos[a], low, high);
            res += v;
            a = par[head[a]];
        }
        int l = pos[a], r = pos[b];
        if (l > r) {
            int t = l;
            l = r, r = t;
        }
        if (l < r) {  // (the lca's own position is the edge above it)
            R v = edgeSeg.countInValRange(l + 1, r, low, high);
            res += v;
        }
        return res;
    }

    // O(log^2 n * log U) -- smallest of the edge weights on the path a..b that is >= x (nullopt if none); nullopt when
    // a == b (no edges)
    LEETCODE_NO_SANITIZE auto edgePathSmallestGteX(int a, int b, T x) {
        if (a < lo || a > hi || b < lo || b > hi) bad("edgePathSmallestGteX");
        using R = decltype(edgeSeg.smallestGteX(0, 0, x));
        R res = R();
        while (head[a] != head[b]) {
            if (dep[head[a]] < dep[head[b]]) {
                int t = a;
                a = b, b = t;
            }
            R v = edgeSeg.smallestGteX(pos[head[a]], pos[a], x);
            if (v && (!res || *v < *res)) res = v;
            a = par[head[a]];
        }
        int l = pos[a], r = pos[b];
        if (l > r) {
            int t = l;
            l = r, r = t;
        }
        if (l < r) {  // (the lca's own position is the edge above it)
            R v = edgeSeg.smallestGteX(l + 1, r, x);
            if (v && (!res || *v < *res)) res = v;
        }
        return res;
    }

    // O(log^2 n * log U) -- smallest of the edge weights on the path a..b that is > x (nullopt if none); nullopt when a
    // == b (no edges)
    LEETCODE_NO_SANITIZE auto edgePathSmallestGtX(int a, int b, T x) {
        if (a < lo || a > hi || b < lo || b > hi) bad("edgePathSmallestGtX");
        using R = decltype(edgeSeg.smallestGtX(0, 0, x));
        R res = R();
        while (head[a] != head[b]) {
            if (dep[head[a]] < dep[head[b]]) {
                int t = a;
                a = b, b = t;
            }
            R v = edgeSeg.smallestGtX(pos[head[a]], pos[a], x);
            if (v && (!res || *v < *res)) res = v;
            a = par[head[a]];
        }
        int l = pos[a], r = pos[b];
        if (l > r) {
            int t = l;
            l = r, r = t;
        }
        if (l < r) {  // (the lca's own position is the edge above it)
            R v = edgeSeg.smallestGtX(l + 1, r, x);
            if (v && (!res || *v < *res)) res = v;
        }
        return res;
    }

    // O(log^2 n * log U) -- largest of the edge weights on the path a..b that is <= x (nullopt if none); nullopt when a
    // == b (no edges)
    LEETCODE_NO_SANITIZE auto edgePathLargestLteX(int a, int b, T x) {
        if (a < lo || a > hi || b < lo || b > hi) bad("edgePathLargestLteX");
        using R = decltype(edgeSeg.largestLteX(0, 0, x));
        R res = R();
        while (head[a] != head[b]) {
            if (dep[head[a]] < dep[head[b]]) {
                int t = a;
                a = b, b = t;
            }
            R v = edgeSeg.largestLteX(pos[head[a]], pos[a], x);
            if (v && (!res || *v > *res)) res = v;
            a = par[head[a]];
        }
        int l = pos[a], r = pos[b];
        if (l > r) {
            int t = l;
            l = r, r = t;
        }
        if (l < r) {  // (the lca's own position is the edge above it)
            R v = edgeSeg.largestLteX(l + 1, r, x);
            if (v && (!res || *v > *res)) res = v;
        }
        return res;
    }

    // O(log^2 n * log U) -- largest of the edge weights on the path a..b that is < x (nullopt if none); nullopt when a
    // == b (no edges)
    LEETCODE_NO_SANITIZE auto edgePathLargestLtX(int a, int b, T x) {
        if (a < lo || a > hi || b < lo || b > hi) bad("edgePathLargestLtX");
        using R = decltype(edgeSeg.largestLtX(0, 0, x));
        R res = R();
        while (head[a] != head[b]) {
            if (dep[head[a]] < dep[head[b]]) {
                int t = a;
                a = b, b = t;
            }
            R v = edgeSeg.largestLtX(pos[head[a]], pos[a], x);
            if (v && (!res || *v > *res)) res = v;
            a = par[head[a]];
        }
        int l = pos[a], r = pos[b];
        if (l > r) {
            int t = l;
            l = r, r = t;
        }
        if (l < r) {  // (the lca's own position is the edge above it)
            R v = edgeSeg.largestLtX(l + 1, r, x);
            if (v && (!res || *v > *res)) res = v;
        }
        return res;
    }

    // O(log^2 n * log U) -- how many edge weights on the path a..b equal x; 0 when a == b (no edges)
    LEETCODE_NO_SANITIZE auto edgePathCountOccurrences(int a, int b, T x) {
        if (a < lo || a > hi || b < lo || b > hi) bad("edgePathCountOccurrences");
        using R = decltype(edgeSeg.countOccurrences(0, 0, x));
        R res = 0;
        while (head[a] != head[b]) {
            if (dep[head[a]] < dep[head[b]]) {
                int t = a;
                a = b, b = t;
            }
            R v = edgeSeg.countOccurrences(pos[head[a]], pos[a], x);
            res += v;
            a = par[head[a]];
        }
        int l = pos[a], r = pos[b];
        if (l > r) {
            int t = l;
            l = r, r = t;
        }
        if (l < r) {  // (the lca's own position is the edge above it)
            R v = edgeSeg.countOccurrences(l + 1, r, x);
            res += v;
        }
        return res;
    }

    // O(log n * log U) -- min edge weight in node's subtree; the largest value of its type when node is a leaf (no
    // edges)
    LEETCODE_NO_SANITIZE auto edgeSubtreeMin(int node) {
        if (node < lo || node > hi) bad("edgeSubtreeMin");
        int l = pos[node] + 1, r = pos[node] + sz[node] - 1;  // (l > r for a leaf: no edges below it)
        using R = decltype(edgeSeg.rangeMin(0, 0));
        if (l > r) return numeric_limits<R>::max();
        return edgeSeg.rangeMin(l, r);
    }

    // O(log n * log U) -- max edge weight in node's subtree; the smallest value of its type when node is a leaf (no
    // edges)
    LEETCODE_NO_SANITIZE auto edgeSubtreeMax(int node) {
        if (node < lo || node > hi) bad("edgeSubtreeMax");
        int l = pos[node] + 1, r = pos[node] + sz[node] - 1;  // (l > r for a leaf: no edges below it)
        using R = decltype(edgeSeg.rangeMax(0, 0));
        if (l > r) return numeric_limits<R>::lowest();
        return edgeSeg.rangeMax(l, r);
    }

    // O(log n * log U) -- kth smallest of the edge weights in node's subtree (1-indexed: k = 1 is the min); needs at
    // least one edge (not node is a leaf), else throws out_of_range
    LEETCODE_NO_SANITIZE auto edgeSubtreeKthSmallest(int node, long long k) {
        if (node < lo || node > hi) bad("edgeSubtreeKthSmallest");
        int l = pos[node] + 1, r = pos[node] + sz[node] - 1;  // (l > r for a leaf: no edges below it)
        if (l > r) throw out_of_range("edgeSubtreeKthSmallest: needs at least one edge in node's subtree");
        return edgeSeg.kthSmallest(l, r, k);
    }

    // O(log n * log U) -- how many edge weights in node's subtree are < x; 0 when node is a leaf (no edges)
    LEETCODE_NO_SANITIZE auto edgeSubtreeCountLtX(int node, T x) {
        if (node < lo || node > hi) bad("edgeSubtreeCountLtX");
        int l = pos[node] + 1, r = pos[node] + sz[node] - 1;  // (l > r for a leaf: no edges below it)
        using R = decltype(edgeSeg.countLtX(0, 0, x));
        if (l > r) return R(0);
        return edgeSeg.countLtX(l, r, x);
    }

    // O(log n * log U) -- how many edge weights in node's subtree are <= x; 0 when node is a leaf (no edges)
    LEETCODE_NO_SANITIZE auto edgeSubtreeCountLteX(int node, T x) {
        if (node < lo || node > hi) bad("edgeSubtreeCountLteX");
        int l = pos[node] + 1, r = pos[node] + sz[node] - 1;  // (l > r for a leaf: no edges below it)
        using R = decltype(edgeSeg.countLteX(0, 0, x));
        if (l > r) return R(0);
        return edgeSeg.countLteX(l, r, x);
    }

    // O(log n * log U) -- how many edge weights in node's subtree are > x; 0 when node is a leaf (no edges)
    LEETCODE_NO_SANITIZE auto edgeSubtreeCountGtX(int node, T x) {
        if (node < lo || node > hi) bad("edgeSubtreeCountGtX");
        int l = pos[node] + 1, r = pos[node] + sz[node] - 1;  // (l > r for a leaf: no edges below it)
        using R = decltype(edgeSeg.countGtX(0, 0, x));
        if (l > r) return R(0);
        return edgeSeg.countGtX(l, r, x);
    }

    // O(log n * log U) -- how many edge weights in node's subtree are >= x; 0 when node is a leaf (no edges)
    LEETCODE_NO_SANITIZE auto edgeSubtreeCountGteX(int node, T x) {
        if (node < lo || node > hi) bad("edgeSubtreeCountGteX");
        int l = pos[node] + 1, r = pos[node] + sz[node] - 1;  // (l > r for a leaf: no edges below it)
        using R = decltype(edgeSeg.countGteX(0, 0, x));
        if (l > r) return R(0);
        return edgeSeg.countGteX(l, r, x);
    }

    // O(log n * log U) -- how many edge weights in node's subtree are in [low, high]; 0 when node is a leaf (no edges)
    LEETCODE_NO_SANITIZE auto edgeSubtreeCountInValRange(int node, T low, T high) {
        if (node < lo || node > hi) bad("edgeSubtreeCountInValRange");
        int l = pos[node] + 1, r = pos[node] + sz[node] - 1;  // (l > r for a leaf: no edges below it)
        using R = decltype(edgeSeg.countInValRange(0, 0, low, high));
        if (l > r) return R(0);
        return edgeSeg.countInValRange(l, r, low, high);
    }

    // O(log n * log U) -- smallest of the edge weights in node's subtree that is >= x (nullopt if none); nullopt when
    // node is a leaf (no edges)
    LEETCODE_NO_SANITIZE auto edgeSubtreeSmallestGteX(int node, T x) {
        if (node < lo || node > hi) bad("edgeSubtreeSmallestGteX");
        int l = pos[node] + 1, r = pos[node] + sz[node] - 1;  // (l > r for a leaf: no edges below it)
        using R = decltype(edgeSeg.smallestGteX(0, 0, x));
        if (l > r) return R();
        return edgeSeg.smallestGteX(l, r, x);
    }

    // O(log n * log U) -- smallest of the edge weights in node's subtree that is > x (nullopt if none); nullopt when
    // node is a leaf (no edges)
    LEETCODE_NO_SANITIZE auto edgeSubtreeSmallestGtX(int node, T x) {
        if (node < lo || node > hi) bad("edgeSubtreeSmallestGtX");
        int l = pos[node] + 1, r = pos[node] + sz[node] - 1;  // (l > r for a leaf: no edges below it)
        using R = decltype(edgeSeg.smallestGtX(0, 0, x));
        if (l > r) return R();
        return edgeSeg.smallestGtX(l, r, x);
    }

    // O(log n * log U) -- largest of the edge weights in node's subtree that is <= x (nullopt if none); nullopt when
    // node is a leaf (no edges)
    LEETCODE_NO_SANITIZE auto edgeSubtreeLargestLteX(int node, T x) {
        if (node < lo || node > hi) bad("edgeSubtreeLargestLteX");
        int l = pos[node] + 1, r = pos[node] + sz[node] - 1;  // (l > r for a leaf: no edges below it)
        using R = decltype(edgeSeg.largestLteX(0, 0, x));
        if (l > r) return R();
        return edgeSeg.largestLteX(l, r, x);
    }

    // O(log n * log U) -- largest of the edge weights in node's subtree that is < x (nullopt if none); nullopt when
    // node is a leaf (no edges)
    LEETCODE_NO_SANITIZE auto edgeSubtreeLargestLtX(int node, T x) {
        if (node < lo || node > hi) bad("edgeSubtreeLargestLtX");
        int l = pos[node] + 1, r = pos[node] + sz[node] - 1;  // (l > r for a leaf: no edges below it)
        using R = decltype(edgeSeg.largestLtX(0, 0, x));
        if (l > r) return R();
        return edgeSeg.largestLtX(l, r, x);
    }

    // O(log n * log U) -- how many edge weights in node's subtree equal x; 0 when node is a leaf (no edges)
    LEETCODE_NO_SANITIZE auto edgeSubtreeCountOccurrences(int node, T x) {
        if (node < lo || node > hi) bad("edgeSubtreeCountOccurrences");
        int l = pos[node] + 1, r = pos[node] + sz[node] - 1;  // (l > r for a leaf: no edges below it)
        using R = decltype(edgeSeg.countOccurrences(0, 0, x));
        if (l > r) return R(0);
        return edgeSeg.countOccurrences(l, r, x);
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
