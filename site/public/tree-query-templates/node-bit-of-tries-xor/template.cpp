// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/tree-queries/node-bit-of-tries-xor/template.cpp
// The range structure inside is https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/bit-of-tries-xor/fast.cpp
// @operations: countAtDepthInSubtree depth isAncestor isOnPath kthAncestor kthNodeOnPath lca lcaRootedAt median nextNodeOnPath nodeAssign nodeGet nodePathCountGtX nodePathCountGteX nodePathCountInValRange nodePathCountLtX nodePathCountLteX nodePathCountOccurrences nodePathLargestLtX nodePathLargestLteX nodePathMax nodePathMaxXorAgainstX nodePathMin nodePathMinXorAgainstX nodePathSmallestGtX nodePathSmallestGteX nodeSubtreeCountGtX nodeSubtreeCountGteX nodeSubtreeCountInValRange nodeSubtreeCountLtX nodeSubtreeCountLteX nodeSubtreeCountOccurrences nodeSubtreeKthSmallest nodeSubtreeLargestLtX nodeSubtreeLargestLteX nodeSubtreeMax nodeSubtreeMaxXorAgainstX nodeSubtreeMin nodeSubtreeMinXorAgainstX nodeSubtreeSmallestGtX nodeSubtreeSmallestGteX parent parentRootedAt pathIntersection pathNodes subtreeSize subtreeSizeRootedAt unweightedDist unweightedDistBetweenPaths unweightedDistToPath
// @data-structure-type: bit-of-tries
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
//   nodeAssign: log(N)*log(U)
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
//   nodePathMaxXorAgainstX: log^2(N)*log(U)
//   nodePathMin: log^2(N)*log(U)
//   nodePathMinXorAgainstX: log^2(N)*log(U)
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
//   nodeSubtreeMaxXorAgainstX: log(N)*log(U)
//   nodeSubtreeMin: log(N)*log(U)
//   nodeSubtreeMinXorAgainstX: log(N)*log(U)
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
//   node: L[1*N*log(N)*log(U)] R[1*N*log(N)*log(U)] C[1*N*log(N)*log(U)]
//   tags: none
//   other: root[1*N] arr[1*N] par[1*N] dep[1*N] sz[1*N] head[1*N] pos[1*N] order[1*N] depthPos[1*N] depthStart[1*N]
//   note: BIT over positions, each BIT node a binary trie of its block's values (U = 2^bits); nodes are never freed, so each point assign adds up to 2 log N log U of them
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// FAST MODE (this is the only C++ version): sanitizers are skipped inside this template, so a bad access in it goes
// unreported. To turn that off (say, when debugging with sanitizers), put this line above the template:
//   #define LEETCODE_NO_SANITIZE
// Without sanitizers (Codeforces, a plain -O2 build) it changes nothing. It needs GCC or Clang.

// a[l..r] as a multiset, asked about v ^ x over its values v, with point assigns. A Fenwick tree (BIT) over positions:
// BIT node j is a binary trie (one level per bit, highest bit first) of the values a[j - lowbit(j) .. j - 1]. The
// values of a[l..r] are the BIT prefix of r + 1 minus the prefix of l, so a query walks those ~2 log N tries down
// together
// (adding the first prefix's counts, subtracting the second's). Values and every x must lie in [0, 2^bits); thresholds
// (k, m, lo, hi) can be any integers. 0-indexed, inclusive.
// The plain order statistics (counts, k-th, min / max, predecessor / successor) are the same walks with x = 0.
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
struct BitXorTries {
    int B, n;
    long long top;
    HotVector<T> arr;
    HotVector<int> root;  // root[j] = BIT node j's trie (1-indexed)
    struct Node {  // a node's fields side by side: a walk reads them together
        int L = 0, R = 0, C = 0;
    };
    HotVector<Node> nd;  // node 0 = empty
    struct Span {  // the tries whose counts add up to a[l..r]'s values: P minus N
        vector<int> P, N;
    };

    // O(N logN logU) -- arr: the initial values, each in [0, 2^bits) (bits = 30 holds values up to 1073741823);
    // U = 2^bits
    BitXorTries(const vector<T>& a, int bits)
        : B(bits), n((int)a.size()), top((1LL << bits) - 1), arr(a), root(n + 1), nd(1) {
        for (int j = 1; j <= n; j++) root[j] = newNode();
        for (int i = 0; i < n; i++) {
            if (a[i] < 0 || (long long)a[i] > top) throw invalid_argument("BitXorTries: needs 0 <= v < 2^bits");
            add(i, a[i], 1);
        }
    }

    // O(logN logU) -- a[i] = v (0 <= v < 2^bits); needs 0 <= i < size(), else throws out_of_range (invalid_argument
    // for v)
    LEETCODE_NO_SANITIZE void pointAssign(long long i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointAssign: needs 0 <= i < size()");
        if (v < 0 || (long long)v > top) throw invalid_argument("pointAssign: needs 0 <= v < 2^bits");
        if (arr[i] == v) return;
        add(i, arr[i], -1);
        add(i, v, 1);
        arr[i] = v;
    }

    // O(1) -- a[i]; needs 0 <= i < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE T pointGet(long long i) const {
        if (i < 0 || i >= n) throw out_of_range("pointGet: needs 0 <= i < size()");
        return arr[i];
    }

    // O(N) -- the whole array (a copy)
    LEETCODE_NO_SANITIZE vector<T> getAll() const { return arr; }

    // O(1) -- the length of the array
    LEETCODE_NO_SANITIZE long long size() const { return n; }

    // O(logN logU) -- largest v ^ x over the values v in a[l..r]; needs 0 <= l <= r < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE long long maxXorAgainstX(long long l, long long r, long long x) const {
        Span s = span("maxXorAgainstX", l, r);
        return extreme(s, B - 1, x, 1);
    }

    // O(logN logU) -- smallest v ^ x over the values v in a[l..r]; needs 0 <= l <= r < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE long long minXorAgainstX(long long l, long long r, long long x) const {
        Span s = span("minXorAgainstX", l, r);
        return extreme(s, B - 1, x, 0);
    }

    // O(logN logU) -- the i-th smallest of v ^ x over the values v in a[l..r], 0-indexed: kthXor(l, r, x, 0) is the
    // smallest (copies count); needs 0 <= l <= r < size() and 0 <= i <= r - l, else throws out_of_range
    LEETCODE_NO_SANITIZE long long kthXor(long long l, long long r, long long x, long long i) const {
        Span s = span("kthXor", l, r);
        if (i < 0 || i > r - l) throw out_of_range("kthXor: needs 0 <= i <= r - l");
        return kthX(s, i + 1, x);
    }

    // O(logN logU) -- how many values v in a[l..r] have v ^ x < k (k is a VALUE, not a rank); needs 0 <= l <= r <
    // size()
    LEETCODE_NO_SANITIZE long long countXorLtK(long long l, long long r, long long x, long long k) const {
        Span s = span("countXorLtK", l, r);
        return cntLt(s, r - l + 1, k, x);
    }

    // O(logN logU) -- how many values v in a[l..r] have v ^ x <= k (k is a VALUE, not a rank); needs
    // 0 <= l <= r < size()
    LEETCODE_NO_SANITIZE long long countXorLteK(long long l, long long r, long long x, long long k) const {
        Span s = span("countXorLteK", l, r);
        return cntLt(s, r - l + 1, k + 1, x);
    }

    // O(logN logU) -- how many values v in a[l..r] have v ^ x > k (k is a VALUE, not a rank); needs 0 <= l <= r <
    // size()
    LEETCODE_NO_SANITIZE long long countXorGtK(long long l, long long r, long long x, long long k) const {
        Span s = span("countXorGtK", l, r);
        return r - l + 1 - cntLt(s, r - l + 1, k + 1, x);
    }

    // O(logN logU) -- how many values v in a[l..r] have v ^ x >= k (k is a VALUE, not a rank); needs
    // 0 <= l <= r < size()
    LEETCODE_NO_SANITIZE long long countXorGteK(long long l, long long r, long long x, long long k) const {
        Span s = span("countXorGteK", l, r);
        return r - l + 1 - cntLt(s, r - l + 1, k, x);
    }

    // O(logN logU) -- largest v ^ x < k over the values v in a[l..r] (k is a VALUE, not a rank), or nullopt; needs
    // 0 <= l <= r < size()
    LEETCODE_NO_SANITIZE optional<long long> largestXorLtK(long long l, long long r, long long x, long long k) const {
        Span s = span("largestXorLtK", l, r);
        long long c = cntLt(s, r - l + 1, k, x);
        if (!c) return nullopt;
        return kthX(s, c, x);
    }

    // O(logN logU) -- largest v ^ x <= k over the values v in a[l..r] (k is a VALUE, not a rank), or nullopt; needs
    // 0 <= l <= r < size()
    LEETCODE_NO_SANITIZE optional<long long> largestXorLteK(long long l, long long r, long long x, long long k) const {
        Span s = span("largestXorLteK", l, r);
        long long c = cntLt(s, r - l + 1, k + 1, x);
        if (!c) return nullopt;
        return kthX(s, c, x);
    }

    // O(logN logU) -- smallest v ^ x > k over the values v in a[l..r] (k is a VALUE, not a rank), or nullopt; needs
    // 0 <= l <= r < size()
    LEETCODE_NO_SANITIZE optional<long long> smallestXorGtK(long long l, long long r, long long x, long long k) const {
        Span s = span("smallestXorGtK", l, r);
        long long c = cntLt(s, r - l + 1, k + 1, x);
        if (c > r - l) return nullopt;
        return kthX(s, c + 1, x);
    }

    // O(logN logU) -- smallest v ^ x >= k over the values v in a[l..r] (k is a VALUE, not a rank), or nullopt; needs
    // 0 <= l <= r < size()
    LEETCODE_NO_SANITIZE optional<long long> smallestXorGteK(long long l, long long r, long long x, long long k) const {
        Span s = span("smallestXorGteK", l, r);
        long long c = cntLt(s, r - l + 1, k, x);
        if (c > r - l) return nullopt;
        return kthX(s, c + 1, x);
    }


    // O(logN logU) -- largest v ^ x over the values v < m in a[l..r], or nullopt; needs 0 <= l <= r < size()
    LEETCODE_NO_SANITIZE optional<long long> maxXorWithVLtM(long long l, long long r, long long x, long long m) const {
        return bestIn(span("maxXorWithVLtM", l, r), x, 0, m - 1, 1);
    }

    // O(logN logU) -- largest v ^ x over the values v <= m in a[l..r], or nullopt; needs 0 <= l <= r < size()
    LEETCODE_NO_SANITIZE optional<long long> maxXorWithVLteM(long long l, long long r, long long x, long long m) const {
        return bestIn(span("maxXorWithVLteM", l, r), x, 0, m, 1);
    }

    // O(logN logU) -- largest v ^ x over the values v > m in a[l..r], or nullopt; needs 0 <= l <= r < size()
    LEETCODE_NO_SANITIZE optional<long long> maxXorWithVGtM(long long l, long long r, long long x, long long m) const {
        return bestIn(span("maxXorWithVGtM", l, r), x, m + 1, top, 1);
    }

    // O(logN logU) -- largest v ^ x over the values v >= m in a[l..r], or nullopt; needs 0 <= l <= r < size()
    LEETCODE_NO_SANITIZE optional<long long> maxXorWithVGteM(long long l, long long r, long long x, long long m) const {
        return bestIn(span("maxXorWithVGteM", l, r), x, m, top, 1);
    }

    // O(logN logU) -- smallest v ^ x over the values v < m in a[l..r], or nullopt; needs 0 <= l <= r < size()
    LEETCODE_NO_SANITIZE optional<long long> minXorWithVLtM(long long l, long long r, long long x, long long m) const {
        return bestIn(span("minXorWithVLtM", l, r), x, 0, m - 1, 0);
    }

    // O(logN logU) -- smallest v ^ x over the values v <= m in a[l..r], or nullopt; needs 0 <= l <= r < size()
    LEETCODE_NO_SANITIZE optional<long long> minXorWithVLteM(long long l, long long r, long long x, long long m) const {
        return bestIn(span("minXorWithVLteM", l, r), x, 0, m, 0);
    }

    // O(logN logU) -- smallest v ^ x over the values v > m in a[l..r], or nullopt; needs 0 <= l <= r < size()
    LEETCODE_NO_SANITIZE optional<long long> minXorWithVGtM(long long l, long long r, long long x, long long m) const {
        return bestIn(span("minXorWithVGtM", l, r), x, m + 1, top, 0);
    }

    // O(logN logU) -- smallest v ^ x over the values v >= m in a[l..r], or nullopt; needs 0 <= l <= r < size()
    LEETCODE_NO_SANITIZE optional<long long> minXorWithVGteM(long long l, long long r, long long x, long long m) const {
        return bestIn(span("minXorWithVGteM", l, r), x, m, top, 0);
    }

    // O(logN logU) -- largest v ^ x over the values v in a[l..r] with lo <= v <= hi, or nullopt; needs
    // 0 <= l <= r < size()
    LEETCODE_NO_SANITIZE optional<long long> maxXorWithVInValRange(long long l, long long r, long long x,
        long long lo, long long hi) const {
        return bestIn(span("maxXorWithVInValRange", l, r), x, lo, hi, 1);
    }

    // O(logN logU) -- smallest v ^ x over the values v in a[l..r] with lo <= v <= hi, or nullopt; needs
    // 0 <= l <= r < size()
    LEETCODE_NO_SANITIZE optional<long long> minXorWithVInValRange(long long l, long long r, long long x,
        long long lo, long long hi) const {
        return bestIn(span("minXorWithVInValRange", l, r), x, lo, hi, 0);
    }

    // ---- plain order statistics over a[l..r] (the same walks with x = 0) ----

    // O(logN logU) -- # of values < x in a[l..r]; needs 0 <= l <= r < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE long long countLtX(long long l, long long r, long long x) const {
        rangeCheck("countLtX", l, r);
        return lt(l, r, x);
    }

    // O(logN logU) -- # of values <= x in a[l..r]; needs 0 <= l <= r < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE long long countLteX(long long l, long long r, long long x) const {
        rangeCheck("countLteX", l, r);
        return lt(l, r, x + 1);
    }

    // O(logN logU) -- # of values > x in a[l..r]; needs 0 <= l <= r < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE long long countGtX(long long l, long long r, long long x) const {
        rangeCheck("countGtX", l, r);
        return r - l + 1 - lt(l, r, x + 1);
    }

    // O(logN logU) -- # of values >= x in a[l..r]; needs 0 <= l <= r < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE long long countGteX(long long l, long long r, long long x) const {
        rangeCheck("countGteX", l, r);
        return r - l + 1 - lt(l, r, x);
    }

    // O(logN logU) -- # of values v in a[l..r] with lowVal <= v <= highVal (0 if lowVal > highVal); needs 0 <= l <= r <
    // size()
    LEETCODE_NO_SANITIZE long long countInValRange(long long l, long long r, long long lowVal,
        long long highVal) const {
        rangeCheck("countInValRange", l, r);
        return lowVal <= highVal ? lt(l, r, highVal + 1) - lt(l, r, lowVal) : 0;
    }

    // O(logN logU) -- # of i in [l, r] with a[i] == x; needs 0 <= l <= r < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE long long countOccurrences(long long l, long long r, long long x) const {
        rangeCheck("countOccurrences", l, r);
        return lt(l, r, x + 1) - lt(l, r, x);
    }

    // O(logN logU) -- the k-th smallest of a[l..r] (k = 1 is the min); needs 0 <= l <= r < size() and 1 <= k <= r - l +
    // 1, else throws out_of_range
    LEETCODE_NO_SANITIZE T kthSmallest(long long l, long long r, long long k) const {
        rangeCheck("kthSmallest", l, r);
        if (k < 1 || k > r - l + 1) throw out_of_range("kthSmallest: needs 1 <= k <= r - l + 1");
        return (T)kth(l, r, k);
    }

    // O(logN logU) -- min of a[l..r]; needs 0 <= l <= r < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE T rangeMin(long long l, long long r) const {
        rangeCheck("rangeMin", l, r);
        return (T)kth(l, r, 1);
    }

    // O(logN logU) -- max of a[l..r]; needs 0 <= l <= r < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE T rangeMax(long long l, long long r) const {
        rangeCheck("rangeMax", l, r);
        return (T)kth(l, r, r - l + 1);
    }

    // O(logN logU) -- smallest value >= x in a[l..r], or nullopt; needs 0 <= l <= r < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE optional<T> smallestGteX(long long l, long long r, long long x) const {
        rangeCheck("smallestGteX", l, r);
        long long c = lt(l, r, x);
        if (c == r - l + 1) return nullopt;
        return (T)kth(l, r, c + 1);
    }

    // O(logN logU) -- smallest value > x in a[l..r], or nullopt; needs 0 <= l <= r < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE optional<T> smallestGtX(long long l, long long r, long long x) const {
        rangeCheck("smallestGtX", l, r);
        long long c = lt(l, r, x + 1);
        if (c == r - l + 1) return nullopt;
        return (T)kth(l, r, c + 1);
    }

    // O(logN logU) -- largest value <= x in a[l..r], or nullopt; needs 0 <= l <= r < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE optional<T> largestLteX(long long l, long long r, long long x) const {
        rangeCheck("largestLteX", l, r);
        long long c = lt(l, r, x + 1);
        if (!c) return nullopt;
        return (T)kth(l, r, c);
    }

    // O(logN logU) -- largest value < x in a[l..r], or nullopt; needs 0 <= l <= r < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE optional<T> largestLtX(long long l, long long r, long long x) const {
        rangeCheck("largestLtX", l, r);
        long long c = lt(l, r, x);
        if (!c) return nullopt;
        return (T)kth(l, r, c);
    }

    // O(logN logU) -- min of the whole array; throws out_of_range if it is empty
    LEETCODE_NO_SANITIZE T minAll() const {
        if (!size()) throw out_of_range("minAll: the array is empty");
        return (T)kth(0, size() - 1, 1);
    }

    // O(logN logU) -- max of the whole array; throws out_of_range if it is empty
    LEETCODE_NO_SANITIZE T maxAll() const {
        if (!size()) throw out_of_range("maxAll: the array is empty");
        return (T)kth(0, size() - 1, size());
    }

  private:
    LEETCODE_NO_SANITIZE int newNode() {
        nd.emplace_back();
        return (int)nd.size() - 1;
    }

    // d copies of v at index i (d = -1 removes one): every BIT node covering i, and the per-bit counts
    LEETCODE_NO_SANITIZE void add(long long i, long long v, int d) {
        for (long long j = i + 1; j <= n; j += j & -j) {
            int t = root[j];
            nd[t].C += d;
            for (int h = B - 1; h >= 0; h--) {
                int bit = v >> h & 1;
                int c = bit ? nd[t].R : nd[t].L;
                if (!c) {
                    c = newNode();
                    (bit ? nd[t].R : nd[t].L) = c;
                }
                t = c;
                nd[t].C += d;
            }
        }
    }

    LEETCODE_NO_SANITIZE void rangeCheck(const char* name, long long l, long long r) const {
        if (l < 0 || l > r || r >= n) throw out_of_range(string(name) + ": needs 0 <= l <= r < size()");
    }

    // checks 0 <= l <= r < size(); the tries of prefix r + 1 (P) and prefix l (N)
    LEETCODE_NO_SANITIZE Span span(const char* name, long long l, long long r) const {
        rangeCheck(name, l, r);
        return tries(l, r);
    }

    LEETCODE_NO_SANITIZE Span tries(long long l, long long r) const {  // the tries of prefix r + 1 (P) and prefix l (N)
        Span s;
        for (long long j = r + 1; j; j &= j - 1) s.P.push_back(root[j]);
        for (long long j = l; j; j &= j - 1) s.N.push_back(root[j]);
        return s;
    }

    // # < k
    LEETCODE_NO_SANITIZE long long lt(long long l, long long r, long long k) const {
        return cntLt(tries(l, r), r - l + 1, k, 0);
    }

    // k-th smallest
    LEETCODE_NO_SANITIZE long long kth(long long l, long long r, long long k) const { return kthX(tries(l, r), k, 0); }

    LEETCODE_NO_SANITIZE long long cnt(const Span& s) const {
        long long c = 0;
        for (int t : s.P) c += nd[t].C;
        for (int t : s.N) c -= nd[t].C;
        return c;
    }

    // the count of the children for v's bit = bit, without building them
    LEETCODE_NO_SANITIZE long long childCount(const Span& s, int bit) const {
        long long c = 0;
        for (int t : s.P) c += nd[bit ? nd[t].R : nd[t].L].C;
        for (int t : s.N) c -= nd[bit ? nd[t].R : nd[t].L].C;
        return c;
    }

    LEETCODE_NO_SANITIZE void descend(Span& s, int bit) const {
        // s becomes its children for v's bit = bit (empty ones dropped), in place
        for (auto* side : {&s.P, &s.N}) {
            size_t k = 0;
            for (int t : *side)
                if (int c = bit ? nd[t].R : nd[t].L) (*side)[k++] = c;
            side->resize(k);
        }
    }

    LEETCODE_NO_SANITIZE Span down(const Span& s, int bit) const {
        // the children for v's bit = bit (empty ones dropped)
        Span o;
        for (int t : s.P) if (int c = bit ? nd[t].R : nd[t].L) o.P.push_back(c);
        for (int t : s.N) if (int c = bit ? nd[t].R : nd[t].L) o.N.push_back(c);
        return o;
    }

    // how many values v below s (all of them: total) have v ^ x < k
    LEETCODE_NO_SANITIZE long long cntLt(Span s, long long total, long long k, long long x) const {
        if (k <= 0) return 0;
        if (k > top) return total;
        long long res = 0;
        for (int h = B - 1; h >= 0 && !s.P.empty(); h--) {
            int xb = x >> h & 1;
            if (k >> h & 1) {  // every result with bit h = 0 is < k
                res += childCount(s, xb);
                descend(s, xb ^ 1);
            } else {
                descend(s, xb);
            }
        }
        return res;
    }

    // the k-th smallest (1-indexed) v ^ x over the values below s
    LEETCODE_NO_SANITIZE long long kthX(Span s, long long k, long long x) const {
        long long res = 0;
        for (int h = B - 1; h >= 0; h--) {
            int xb = x >> h & 1;
            long long c = childCount(s, xb);
            if (k <= c) {
                descend(s, xb);
            } else {
                k -= c;
                descend(s, xb ^ 1);
                res |= 1LL << h;
            }
        }
        return res;
    }

    // bits h..0 of the largest (big = 1) / smallest v ^ x below s, which holds some value
    LEETCODE_NO_SANITIZE long long extreme(Span s, int h, long long x, int big) const {
        long long res = 0;
        for (; h >= 0; h--) {
            int p = (int)(x >> h & 1) ^ big;  // the child whose result bit is big
            if (childCount(s, p)) {
                descend(s, p);
                res |= (long long)big << h;
            } else {
                descend(s, p ^ 1);
                res |= (long long)(big ^ 1) << h;
            }
        }
        return res;
    }

    // the largest (big = 1) / smallest v ^ x over the values v below s with lo <= v <= hi, or nullopt. Walks down the
    // bits lo and hi share, then splits: below lo's side only the lower bound matters, below hi's only the upper one
    LEETCODE_NO_SANITIZE optional<long long> bestIn(Span s, long long x, long long lo, long long hi, int big) const {
        lo = max(lo, 0LL), hi = min(hi, top);
        if (lo > hi) return nullopt;
        int h = B - 1;
        long long res = 0;
        for (; h >= 0 && (lo >> h & 1) == (hi >> h & 1); h--) {
            int bit = lo >> h & 1;
            descend(s, bit);
            if (!cnt(s)) return nullopt;
            res |= (long long)(bit ^ (x >> h & 1)) << h;
        }
        if (h < 0) return res;
        long long xb = x >> h & 1;
        auto c0 = oneSide(down(s, 0), h - 1, lo, x, big, 1, res | xb << h);
        auto c1 = oneSide(down(s, 1), h - 1, hi, x, big, 0, res | (xb ^ 1) << h);
        if (!c0 || !c1) return c0 ? c0 : c1;
        return big ? max(*c0, *c1) : min(*c0, *c1);
    }

    // below s: the best v ^ x whose bits h..0 are >= (lower = 1) / <= bound's bits h..0, or nullopt; res holds the
    // result's bits above h. Along the path that matches bound, each step off it (to the side the bound allows) is a
    // free subtree: take it at once if its result bit beats the path's, else remember the deepest one
    LEETCODE_NO_SANITIZE optional<long long> oneSide(Span s, int h, long long bound, long long x, int big, int lower,
        long long res) const {
        if (!cnt(s)) return nullopt;
        Span f;
        int fh = -2;
        long long fres = 0;
        for (; h >= 0; h--) {
            int xb = x >> h & 1, bb = bound >> h & 1;
            if (bb != lower) {  // a free side exists: v bit = lower
                Span c = down(s, lower);
                if (cnt(c)) {
                    long long cres = res | (long long)(lower ^ xb) << h;
                    if ((lower ^ xb) == big) return cres | extreme(std::move(c), h - 1, x, big);
                    f = std::move(c), fh = h, fres = cres;
                }
            }
            descend(s, bb);
            if (!cnt(s)) break;
            res |= (long long)(bb ^ xb) << h;
        }
        if (h < 0) return res;  // v equal to bound below here: allowed (inclusive)
        if (fh == -2) return nullopt;
        return fres | extreme(std::move(f), fh - 1, x, big);
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
// (BitXorTries) in position order: a subtree is one range of it, and a path a..b is O(log n) ranges, one per chain it
// crosses.
template <typename T>
struct Tree {
    int n, lo, hi, root;  // nodes are lo..hi
    // by node label: parent (-1 for the root), depth, subtree size, top of its chain, position
    HotVector<int> par, dep, sz, head, pos;
    HotVector<int> order;  // order[pos[v]] = v
    // depthPos[depthStart[d] .. depthStart[d + 1]) = the positions of the nodes at depth d, increasing
    HotVector<int> depthStart, depthPos;
    BitXorTries<T> seg;  // the values, in position order

    // O(n * log n * log U) -- builds the layout and the range structure; throws invalid_argument when the edges are not
    // one tree on nodes 0..n-1 or 1..n, or vals has the wrong size
    template <typename E = int> Tree(const vector<vector<E>>& edges, int root, const vector<T>& vals, int bits)
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

    // O(1) -- val(node)
    LEETCODE_NO_SANITIZE auto nodeGet(int node) {
        if (node < lo || node > hi) bad("nodeGet");
        return seg.pointGet(pos[node]);
    }

    // O(log n * log U) -- val(node) = x
    LEETCODE_NO_SANITIZE void nodeAssign(int node, T x) {
        if (node < lo || node > hi) bad("nodeAssign");
        seg.pointAssign(pos[node], x);
    }

    // O(log^2 n * log U) -- min node value on the path a..b
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

    // O(log^2 n * log U) -- max node value on the path a..b
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

    // O(log^2 n * log U) -- how many node values on the path a..b are < x
    LEETCODE_NO_SANITIZE auto nodePathCountLtX(int a, int b, long long x) {
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

    // O(log^2 n * log U) -- how many node values on the path a..b are <= x
    LEETCODE_NO_SANITIZE auto nodePathCountLteX(int a, int b, long long x) {
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

    // O(log^2 n * log U) -- how many node values on the path a..b are > x
    LEETCODE_NO_SANITIZE auto nodePathCountGtX(int a, int b, long long x) {
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

    // O(log^2 n * log U) -- how many node values on the path a..b are >= x
    LEETCODE_NO_SANITIZE auto nodePathCountGteX(int a, int b, long long x) {
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

    // O(log^2 n * log U) -- how many node values on the path a..b are in [low, high]
    LEETCODE_NO_SANITIZE auto nodePathCountInValRange(int a, int b, long long low, long long high) {
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

    // O(log^2 n * log U) -- smallest of the node values on the path a..b that is >= x (nullopt if none)
    LEETCODE_NO_SANITIZE auto nodePathSmallestGteX(int a, int b, long long x) {
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

    // O(log^2 n * log U) -- smallest of the node values on the path a..b that is > x (nullopt if none)
    LEETCODE_NO_SANITIZE auto nodePathSmallestGtX(int a, int b, long long x) {
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

    // O(log^2 n * log U) -- largest of the node values on the path a..b that is <= x (nullopt if none)
    LEETCODE_NO_SANITIZE auto nodePathLargestLteX(int a, int b, long long x) {
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

    // O(log^2 n * log U) -- largest of the node values on the path a..b that is < x (nullopt if none)
    LEETCODE_NO_SANITIZE auto nodePathLargestLtX(int a, int b, long long x) {
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

    // O(log^2 n * log U) -- how many node values on the path a..b equal x
    LEETCODE_NO_SANITIZE auto nodePathCountOccurrences(int a, int b, long long x) {
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

    // O(log^2 n * log U) -- largest val ^ x over the node values on the path a..b
    LEETCODE_NO_SANITIZE auto nodePathMaxXorAgainstX(int a, int b, long long x) {
        if (a < lo || a > hi || b < lo || b > hi) bad("nodePathMaxXorAgainstX");
        using R = decltype(seg.maxXorAgainstX(0, 0, x));
        R res = numeric_limits<R>::lowest();
        while (head[a] != head[b]) {
            if (dep[head[a]] < dep[head[b]]) {
                int t = a;
                a = b, b = t;
            }
            R v = seg.maxXorAgainstX(pos[head[a]], pos[a], x);
            if (v > res) res = v;
            a = par[head[a]];
        }
        int l = pos[a], r = pos[b];
        if (l > r) {
            int t = l;
            l = r, r = t;
        }
        R v = seg.maxXorAgainstX(l, r, x);
        if (v > res) res = v;
        return res;
    }

    // O(log^2 n * log U) -- smallest val ^ x over the node values on the path a..b
    LEETCODE_NO_SANITIZE auto nodePathMinXorAgainstX(int a, int b, long long x) {
        if (a < lo || a > hi || b < lo || b > hi) bad("nodePathMinXorAgainstX");
        using R = decltype(seg.minXorAgainstX(0, 0, x));
        R res = numeric_limits<R>::max();
        while (head[a] != head[b]) {
            if (dep[head[a]] < dep[head[b]]) {
                int t = a;
                a = b, b = t;
            }
            R v = seg.minXorAgainstX(pos[head[a]], pos[a], x);
            if (v < res) res = v;
            a = par[head[a]];
        }
        int l = pos[a], r = pos[b];
        if (l > r) {
            int t = l;
            l = r, r = t;
        }
        R v = seg.minXorAgainstX(l, r, x);
        if (v < res) res = v;
        return res;
    }

    // O(log n * log U) -- min node value in node's subtree
    LEETCODE_NO_SANITIZE auto nodeSubtreeMin(int node) {
        if (node < lo || node > hi) bad("nodeSubtreeMin");
        int l = pos[node];
        return seg.rangeMin(l, l + sz[node] - 1);
    }

    // O(log n * log U) -- max node value in node's subtree
    LEETCODE_NO_SANITIZE auto nodeSubtreeMax(int node) {
        if (node < lo || node > hi) bad("nodeSubtreeMax");
        int l = pos[node];
        return seg.rangeMax(l, l + sz[node] - 1);
    }

    // O(log n * log U) -- kth smallest of the node values in node's subtree (1-indexed: k = 1 is the min)
    LEETCODE_NO_SANITIZE auto nodeSubtreeKthSmallest(int node, long long k) {
        if (node < lo || node > hi) bad("nodeSubtreeKthSmallest");
        int l = pos[node];
        return seg.kthSmallest(l, l + sz[node] - 1, k);
    }

    // O(log n * log U) -- how many node values in node's subtree are < x
    LEETCODE_NO_SANITIZE auto nodeSubtreeCountLtX(int node, long long x) {
        if (node < lo || node > hi) bad("nodeSubtreeCountLtX");
        int l = pos[node];
        return seg.countLtX(l, l + sz[node] - 1, x);
    }

    // O(log n * log U) -- how many node values in node's subtree are <= x
    LEETCODE_NO_SANITIZE auto nodeSubtreeCountLteX(int node, long long x) {
        if (node < lo || node > hi) bad("nodeSubtreeCountLteX");
        int l = pos[node];
        return seg.countLteX(l, l + sz[node] - 1, x);
    }

    // O(log n * log U) -- how many node values in node's subtree are > x
    LEETCODE_NO_SANITIZE auto nodeSubtreeCountGtX(int node, long long x) {
        if (node < lo || node > hi) bad("nodeSubtreeCountGtX");
        int l = pos[node];
        return seg.countGtX(l, l + sz[node] - 1, x);
    }

    // O(log n * log U) -- how many node values in node's subtree are >= x
    LEETCODE_NO_SANITIZE auto nodeSubtreeCountGteX(int node, long long x) {
        if (node < lo || node > hi) bad("nodeSubtreeCountGteX");
        int l = pos[node];
        return seg.countGteX(l, l + sz[node] - 1, x);
    }

    // O(log n * log U) -- how many node values in node's subtree are in [low, high]
    LEETCODE_NO_SANITIZE auto nodeSubtreeCountInValRange(int node, long long low, long long high) {
        if (node < lo || node > hi) bad("nodeSubtreeCountInValRange");
        int l = pos[node];
        return seg.countInValRange(l, l + sz[node] - 1, low, high);
    }

    // O(log n * log U) -- smallest of the node values in node's subtree that is >= x (nullopt if none)
    LEETCODE_NO_SANITIZE auto nodeSubtreeSmallestGteX(int node, long long x) {
        if (node < lo || node > hi) bad("nodeSubtreeSmallestGteX");
        int l = pos[node];
        return seg.smallestGteX(l, l + sz[node] - 1, x);
    }

    // O(log n * log U) -- smallest of the node values in node's subtree that is > x (nullopt if none)
    LEETCODE_NO_SANITIZE auto nodeSubtreeSmallestGtX(int node, long long x) {
        if (node < lo || node > hi) bad("nodeSubtreeSmallestGtX");
        int l = pos[node];
        return seg.smallestGtX(l, l + sz[node] - 1, x);
    }

    // O(log n * log U) -- largest of the node values in node's subtree that is <= x (nullopt if none)
    LEETCODE_NO_SANITIZE auto nodeSubtreeLargestLteX(int node, long long x) {
        if (node < lo || node > hi) bad("nodeSubtreeLargestLteX");
        int l = pos[node];
        return seg.largestLteX(l, l + sz[node] - 1, x);
    }

    // O(log n * log U) -- largest of the node values in node's subtree that is < x (nullopt if none)
    LEETCODE_NO_SANITIZE auto nodeSubtreeLargestLtX(int node, long long x) {
        if (node < lo || node > hi) bad("nodeSubtreeLargestLtX");
        int l = pos[node];
        return seg.largestLtX(l, l + sz[node] - 1, x);
    }

    // O(log n * log U) -- how many node values in node's subtree equal x
    LEETCODE_NO_SANITIZE auto nodeSubtreeCountOccurrences(int node, long long x) {
        if (node < lo || node > hi) bad("nodeSubtreeCountOccurrences");
        int l = pos[node];
        return seg.countOccurrences(l, l + sz[node] - 1, x);
    }

    // O(log n * log U) -- largest val ^ x over the node values in node's subtree
    LEETCODE_NO_SANITIZE auto nodeSubtreeMaxXorAgainstX(int node, long long x) {
        if (node < lo || node > hi) bad("nodeSubtreeMaxXorAgainstX");
        int l = pos[node];
        return seg.maxXorAgainstX(l, l + sz[node] - 1, x);
    }

    // O(log n * log U) -- smallest val ^ x over the node values in node's subtree
    LEETCODE_NO_SANITIZE auto nodeSubtreeMinXorAgainstX(int node, long long x) {
        if (node < lo || node > hi) bad("nodeSubtreeMinXorAgainstX");
        int l = pos[node];
        return seg.minXorAgainstX(l, l + sz[node] - 1, x);
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
