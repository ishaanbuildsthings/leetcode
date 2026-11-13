// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/tree-queries/edge-sqrt-tries-xor/template.cpp
// The range structure inside is https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/sqrt-tries-xor/fast.cpp
// @operations: countAtDepthInSubtree depth edgeAssign edgeGet edgePathAssign edgePathCountGtX edgePathCountGteX edgePathCountInValRange edgePathCountLtX edgePathCountLteX edgePathCountOccurrences edgePathLargestLtX edgePathLargestLteX edgePathMax edgePathMaxXorAgainstX edgePathMin edgePathMinXorAgainstX edgePathSmallestGtX edgePathSmallestGteX edgePathXORApply edgeSubtreeAssign edgeSubtreeCountGtX edgeSubtreeCountGteX edgeSubtreeCountInValRange edgeSubtreeCountLtX edgeSubtreeCountLteX edgeSubtreeCountOccurrences edgeSubtreeKthSmallest edgeSubtreeLargestLtX edgeSubtreeLargestLteX edgeSubtreeMax edgeSubtreeMaxXorAgainstX edgeSubtreeMin edgeSubtreeMinXorAgainstX edgeSubtreeSmallestGtX edgeSubtreeSmallestGteX edgeSubtreeXORApply isAncestor isOnPath kthAncestor kthNodeOnPath lca lcaRootedAt median nextNodeOnPath parent parentRootedAt pathIntersection pathNodes subtreeSize subtreeSizeRootedAt unweightedDist unweightedDistBetweenPaths unweightedDistToPath
// @data-structure-type: sqrt-tries
// @complexities:
//   countAtDepthInSubtree: log(N)
//   depth: 1
//   edgeAssign: sqrt(N)*log(U)
//   edgeGet: 1
//   edgePathAssign: sqrt(N)*log(U)*log(N)
//   edgePathCountGtX: sqrt(N)*log(U)*log(N)
//   edgePathCountGteX: sqrt(N)*log(U)*log(N)
//   edgePathCountInValRange: sqrt(N)*log(U)*log(N)
//   edgePathCountLtX: sqrt(N)*log(U)*log(N)
//   edgePathCountLteX: sqrt(N)*log(U)*log(N)
//   edgePathCountOccurrences: sqrt(N)*log(U)*log(N)
//   edgePathLargestLtX: sqrt(N)*log(U)*log(N)
//   edgePathLargestLteX: sqrt(N)*log(U)*log(N)
//   edgePathMax: sqrt(N)*log(U)*log(N)
//   edgePathMaxXorAgainstX: sqrt(N)*log(U)*log(N)
//   edgePathMin: sqrt(N)*log(U)*log(N)
//   edgePathMinXorAgainstX: sqrt(N)*log(U)*log(N)
//   edgePathSmallestGtX: sqrt(N)*log(U)*log(N)
//   edgePathSmallestGteX: sqrt(N)*log(U)*log(N)
//   edgePathXORApply: sqrt(N)*log(U)*log(N)
//   edgeSubtreeAssign: sqrt(N)*log(U)
//   edgeSubtreeCountGtX: sqrt(N)*log(U)
//   edgeSubtreeCountGteX: sqrt(N)*log(U)
//   edgeSubtreeCountInValRange: sqrt(N)*log(U)
//   edgeSubtreeCountLtX: sqrt(N)*log(U)
//   edgeSubtreeCountLteX: sqrt(N)*log(U)
//   edgeSubtreeCountOccurrences: sqrt(N)*log(U)
//   edgeSubtreeKthSmallest: sqrt(N)*log(U)
//   edgeSubtreeLargestLtX: sqrt(N)*log(U)
//   edgeSubtreeLargestLteX: sqrt(N)*log(U)
//   edgeSubtreeMax: sqrt(N)*log(U)
//   edgeSubtreeMaxXorAgainstX: sqrt(N)*log(U)
//   edgeSubtreeMin: sqrt(N)*log(U)
//   edgeSubtreeMinXorAgainstX: sqrt(N)*log(U)
//   edgeSubtreeSmallestGtX: sqrt(N)*log(U)
//   edgeSubtreeSmallestGteX: sqrt(N)*log(U)
//   edgeSubtreeXORApply: sqrt(N)*log(U)
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
//   build: N*log(U)
// @memory:
//   layout: none
//   node: L[1*N*log(U)] R[1*N*log(U)] C[1*N*log(U)]
//   tags: none
//   other: arr[1*N] tag[1*sqrt(N)] uni[1*sqrt(N)] par[1*N] dep[1*N] sz[1*N] head[1*N] pos[1*N] order[1*N] depthPos[1*N] depthStart[1*N]
//   note: blocks of about sqrt N, each a binary trie of its stored values (at most its length times log U nodes, U = 2^bits) with a lazy xor and a lazy assign; a scratch trie of 2 sqrt N log U nodes for the partly covered ends of a query
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// FAST MODE (this is the only C++ version): sanitizers are skipped inside this template, so a bad access in it goes
// unreported. To turn that off (say, when debugging with sanitizers), put this line above the template:
//   #define LEETCODE_NO_SANITIZE
// Without sanitizers (Codeforces, a plain -O2 build) it changes nothing. It needs GCC or Clang.

// a[l..r] as a multiset, asked about v ^ x over its values v, with range xor-apply, range assign and point assign. The
// array is cut into blocks of about sqrt(N); each block keeps a binary trie (one level per bit, highest bit first) of
// its stored values, a lazy xor (its real values are stored ^ tag) and a lazy assign (the trie is one path of copies).
// A whole block updates in O(log U); a partly covered one is rewritten and its trie rebuilt. A query walks the tries of
// the whole blocks inside l..r down together, each through its own lazy xor, plus a scratch trie of the partly covered
// ends. Values and every x must lie in [0, 2^bits); thresholds (k, m, lo, hi) can be any integers. 0-indexed,
// inclusive.
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
struct SqrtXorTries {
    using Src = vector<pair<int, long long>>;  // (trie node, the lazy xor its values go through)
    int B, n, S, nb;
    long long top;
    HotVector<long long> arr;  // the stored values: a[i] = arr[i] ^ tag of its block, unless the block is assigned
    struct Node {  // a node's fields side by side: a walk reads them together
        int L = 0, R = 0, C = 0;
    };
    // node 0 = empty; block b owns the nodes from base[b] (its root) on, at most (its length) * bits + 1 of them; the
    // scratch trie for the partly covered ends of a query comes after them
    mutable HotVector<Node> nd;
    HotVector<int> base;
    int scratch;
    HotVector<long long> tag, uni;  // lazy xor / lazy assign of each block (uni = -1: none)

    // O(N logU) -- arr: the initial values, each in [0, 2^bits) (bits = 30 holds values up to 1073741823); U = 2^bits
    SqrtXorTries(const vector<T>& a, int bits) : B(bits), n((int)a.size()), top((1LL << bits) - 1) {
        S = max(1, (int)sqrtl((long double)n));
        while ((long long)(S + 1) * (S + 1) <= n) S++;
        while ((long long)S * S > n && S > 1) S--;
        nb = (n + S - 1) / S;
        for (const T& v : a) {
            if (v < 0 || (long long)v > top) throw invalid_argument("SqrtXorTries: needs 0 <= v < 2^bits");
            arr.push_back((long long)v);
        }
        long long total = 1;
        for (int b = 0; b < nb; b++) {
            base.push_back((int)total);
            total += (long long)(blockEnd(b) - b * S + 1) * B + 1;
        }
        scratch = (int)total;
        total += 2LL * S * B + 1;
        nd.assign(total, Node());
        tag.assign(nb, 0), uni.assign(nb, -1);
        for (int b = 0; b < nb; b++) rebuild(b);
    }

    // O(sqrt(N) logU) -- a[i] = v (0 <= v < 2^bits); needs 0 <= i < size(), else throws out_of_range (invalid_argument
    // for v)
    LEETCODE_NO_SANITIZE void pointAssign(long long i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointAssign: needs 0 <= i < size()");
        checkVal("pointAssign", v);
        int b = (int)(i / S);
        push(b);
        arr[i] = (long long)v;
        rebuild(b);
    }

    // O(sqrt(N) logU) -- a[i] ^= x for every i in [l, r] (0 <= x < 2^bits); needs 0 <= l <= r < size(), else throws
    // out_of_range
    LEETCODE_NO_SANITIZE void rangeXorApply(long long l, long long r, T x) {
        checkRange("rangeXorApply", l, r);
        checkVal("rangeXorApply", x);
        for (int b = (int)(l / S); b <= r / S; b++) {
            long long s = (long long)b * S, e = blockEnd(b);
            if (l <= s && e <= r) {
                tag[b] ^= (long long)x;
            } else {
                push(b);
                for (long long i = max(l, s); i <= min(r, e); i++) arr[i] ^= (long long)x;
                rebuild(b);
            }
        }
    }

    // O(sqrt(N) logU) -- a[i] = v for every i in [l, r] (0 <= v < 2^bits); needs 0 <= l <= r < size(), else throws
    // out_of_range
    LEETCODE_NO_SANITIZE void rangeAssign(long long l, long long r, T v) {
        checkRange("rangeAssign", l, r);
        checkVal("rangeAssign", v);
        for (int b = (int)(l / S); b <= r / S; b++) {
            long long s = (long long)b * S, e = blockEnd(b);
            if (l <= s && e <= r) {
                assignBlock(b, (long long)v);
            } else {
                push(b);
                for (long long i = max(l, s); i <= min(r, e); i++) arr[i] = (long long)v;
                rebuild(b);
            }
        }
    }

    // O(1) -- a[i]; needs 0 <= i < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE T pointGet(long long i) const {
        if (i < 0 || i >= n) throw out_of_range("pointGet: needs 0 <= i < size()");
        return (T)get(i);
    }

    // O(N) -- the whole array
    LEETCODE_NO_SANITIZE vector<T> getAll() const {
        vector<T> out(n);
        for (int i = 0; i < n; i++) out[i] = (T)get(i);
        return out;
    }

    // O(1) -- the length of the array
    LEETCODE_NO_SANITIZE long long size() const { return n; }

    // O(sqrt(N) logU) -- largest v ^ x over the values v in a[l..r]; needs 0 <= l <= r < size(), else throws
    // out_of_range
    LEETCODE_NO_SANITIZE long long maxXorAgainstX(long long l, long long r, long long x) const {
        return extreme(span("maxXorAgainstX", l, r), B - 1, x, 1);
    }

    // O(sqrt(N) logU) -- smallest v ^ x over the values v in a[l..r]; needs 0 <= l <= r < size(), else throws
    // out_of_range
    LEETCODE_NO_SANITIZE long long minXorAgainstX(long long l, long long r, long long x) const {
        return extreme(span("minXorAgainstX", l, r), B - 1, x, 0);
    }

    // O(sqrt(N) logU) -- the i-th smallest of v ^ x over the values v in a[l..r], 0-indexed: kthXor(l, r, x, 0) is the
    // smallest (copies count); needs 0 <= l <= r < size() and 0 <= i <= r - l, else throws out_of_range
    LEETCODE_NO_SANITIZE long long kthXor(long long l, long long r, long long x, long long i) const {
        Src src = span("kthXor", l, r);
        if (i < 0 || i > r - l) throw out_of_range("kthXor: needs 0 <= i <= r - l");
        return kthX(src, i + 1, x);
    }

    // O(sqrt(N) logU) -- how many values v in a[l..r] have v ^ x < k (k is a VALUE, not a rank); needs
    // 0 <= l <= r < size()
    LEETCODE_NO_SANITIZE long long countXorLtK(long long l, long long r, long long x, long long k) const {
        return cntLt(span("countXorLtK", l, r), r - l + 1, k, x);
    }

    // O(sqrt(N) logU) -- how many values v in a[l..r] have v ^ x <= k (k is a VALUE, not a rank); needs
    // 0 <= l <= r < size()
    LEETCODE_NO_SANITIZE long long countXorLteK(long long l, long long r, long long x, long long k) const {
        return cntLt(span("countXorLteK", l, r), r - l + 1, k + 1, x);
    }

    // O(sqrt(N) logU) -- how many values v in a[l..r] have v ^ x > k (k is a VALUE, not a rank); needs
    // 0 <= l <= r < size()
    LEETCODE_NO_SANITIZE long long countXorGtK(long long l, long long r, long long x, long long k) const {
        return r - l + 1 - cntLt(span("countXorGtK", l, r), r - l + 1, k + 1, x);
    }

    // O(sqrt(N) logU) -- how many values v in a[l..r] have v ^ x >= k (k is a VALUE, not a rank); needs
    // 0 <= l <= r < size()
    LEETCODE_NO_SANITIZE long long countXorGteK(long long l, long long r, long long x, long long k) const {
        return r - l + 1 - cntLt(span("countXorGteK", l, r), r - l + 1, k, x);
    }

    // O(sqrt(N) logU) -- largest v ^ x < k over the values v in a[l..r] (k is a VALUE, not a rank), or nullopt; needs
    // 0 <= l <= r < size()
    LEETCODE_NO_SANITIZE optional<long long> largestXorLtK(long long l, long long r, long long x, long long k) const {
        Src src = span("largestXorLtK", l, r);
        long long c = cntLt(src, r - l + 1, k, x);
        if (!c) return nullopt;
        return kthX(src, c, x);
    }

    // O(sqrt(N) logU) -- largest v ^ x <= k over the values v in a[l..r] (k is a VALUE, not a rank), or nullopt; needs
    // 0 <= l <= r < size()
    LEETCODE_NO_SANITIZE optional<long long> largestXorLteK(long long l, long long r, long long x, long long k) const {
        Src src = span("largestXorLteK", l, r);
        long long c = cntLt(src, r - l + 1, k + 1, x);
        if (!c) return nullopt;
        return kthX(src, c, x);
    }

    // O(sqrt(N) logU) -- smallest v ^ x > k over the values v in a[l..r] (k is a VALUE, not a rank), or nullopt; needs
    // 0 <= l <= r < size()
    LEETCODE_NO_SANITIZE optional<long long> smallestXorGtK(long long l, long long r, long long x, long long k) const {
        Src src = span("smallestXorGtK", l, r);
        long long c = cntLt(src, r - l + 1, k + 1, x);
        if (c > r - l) return nullopt;
        return kthX(src, c + 1, x);
    }

    // O(sqrt(N) logU) -- smallest v ^ x >= k over the values v in a[l..r] (k is a VALUE, not a rank), or nullopt;
    // needs 0 <= l <= r < size()
    LEETCODE_NO_SANITIZE optional<long long> smallestXorGteK(long long l, long long r, long long x, long long k) const {
        Src src = span("smallestXorGteK", l, r);
        long long c = cntLt(src, r - l + 1, k, x);
        if (c > r - l) return nullopt;
        return kthX(src, c + 1, x);
    }


    // O(sqrt(N) logU) -- largest v ^ x over the values v < m in a[l..r], or nullopt; needs 0 <= l <= r < size()
    LEETCODE_NO_SANITIZE optional<long long> maxXorWithVLtM(long long l, long long r, long long x, long long m) const {
        return bestIn(span("maxXorWithVLtM", l, r), x, 0, m - 1, 1);
    }

    // O(sqrt(N) logU) -- largest v ^ x over the values v <= m in a[l..r], or nullopt; needs 0 <= l <= r < size()
    LEETCODE_NO_SANITIZE optional<long long> maxXorWithVLteM(long long l, long long r, long long x, long long m) const {
        return bestIn(span("maxXorWithVLteM", l, r), x, 0, m, 1);
    }

    // O(sqrt(N) logU) -- largest v ^ x over the values v > m in a[l..r], or nullopt; needs 0 <= l <= r < size()
    LEETCODE_NO_SANITIZE optional<long long> maxXorWithVGtM(long long l, long long r, long long x, long long m) const {
        return bestIn(span("maxXorWithVGtM", l, r), x, m + 1, top, 1);
    }

    // O(sqrt(N) logU) -- largest v ^ x over the values v >= m in a[l..r], or nullopt; needs 0 <= l <= r < size()
    LEETCODE_NO_SANITIZE optional<long long> maxXorWithVGteM(long long l, long long r, long long x, long long m) const {
        return bestIn(span("maxXorWithVGteM", l, r), x, m, top, 1);
    }

    // O(sqrt(N) logU) -- smallest v ^ x over the values v < m in a[l..r], or nullopt; needs 0 <= l <= r < size()
    LEETCODE_NO_SANITIZE optional<long long> minXorWithVLtM(long long l, long long r, long long x, long long m) const {
        return bestIn(span("minXorWithVLtM", l, r), x, 0, m - 1, 0);
    }

    // O(sqrt(N) logU) -- smallest v ^ x over the values v <= m in a[l..r], or nullopt; needs 0 <= l <= r < size()
    LEETCODE_NO_SANITIZE optional<long long> minXorWithVLteM(long long l, long long r, long long x, long long m) const {
        return bestIn(span("minXorWithVLteM", l, r), x, 0, m, 0);
    }

    // O(sqrt(N) logU) -- smallest v ^ x over the values v > m in a[l..r], or nullopt; needs 0 <= l <= r < size()
    LEETCODE_NO_SANITIZE optional<long long> minXorWithVGtM(long long l, long long r, long long x, long long m) const {
        return bestIn(span("minXorWithVGtM", l, r), x, m + 1, top, 0);
    }

    // O(sqrt(N) logU) -- smallest v ^ x over the values v >= m in a[l..r], or nullopt; needs 0 <= l <= r < size()
    LEETCODE_NO_SANITIZE optional<long long> minXorWithVGteM(long long l, long long r, long long x, long long m) const {
        return bestIn(span("minXorWithVGteM", l, r), x, m, top, 0);
    }

    // O(sqrt(N) logU) -- largest v ^ x over the values v in a[l..r] with lo <= v <= hi, or nullopt; needs
    // 0 <= l <= r < size()
    LEETCODE_NO_SANITIZE optional<long long> maxXorWithVInValRange(long long l, long long r, long long x,
        long long lo, long long hi) const {
        return bestIn(span("maxXorWithVInValRange", l, r), x, lo, hi, 1);
    }

    // O(sqrt(N) logU) -- smallest v ^ x over the values v in a[l..r] with lo <= v <= hi, or nullopt; needs
    // 0 <= l <= r < size()
    LEETCODE_NO_SANITIZE optional<long long> minXorWithVInValRange(long long l, long long r, long long x,
        long long lo, long long hi) const {
        return bestIn(span("minXorWithVInValRange", l, r), x, lo, hi, 0);
    }

    // ---- plain order statistics over a[l..r] (the same walks with x = 0) ----

    // O(sqrt(N) logU) -- # of values < x in a[l..r]; needs 0 <= l <= r < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE long long countLtX(long long l, long long r, long long x) const {
        rangeCheck("countLtX", l, r);
        return lt(l, r, x);
    }

    // O(sqrt(N) logU) -- # of values <= x in a[l..r]; needs 0 <= l <= r < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE long long countLteX(long long l, long long r, long long x) const {
        rangeCheck("countLteX", l, r);
        return lt(l, r, x + 1);
    }

    // O(sqrt(N) logU) -- # of values > x in a[l..r]; needs 0 <= l <= r < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE long long countGtX(long long l, long long r, long long x) const {
        rangeCheck("countGtX", l, r);
        return r - l + 1 - lt(l, r, x + 1);
    }

    // O(sqrt(N) logU) -- # of values >= x in a[l..r]; needs 0 <= l <= r < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE long long countGteX(long long l, long long r, long long x) const {
        rangeCheck("countGteX", l, r);
        return r - l + 1 - lt(l, r, x);
    }

    // O(sqrt(N) logU) -- # of values v in a[l..r] with lowVal <= v <= highVal (0 if lowVal > highVal); needs 0 <= l <=
    // r < size()
    LEETCODE_NO_SANITIZE long long countInValRange(long long l, long long r, long long lowVal,
        long long highVal) const {
        rangeCheck("countInValRange", l, r);
        return lowVal <= highVal ? lt(l, r, highVal + 1) - lt(l, r, lowVal) : 0;
    }

    // O(sqrt(N) logU) -- # of i in [l, r] with a[i] == x; needs 0 <= l <= r < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE long long countOccurrences(long long l, long long r, long long x) const {
        rangeCheck("countOccurrences", l, r);
        return lt(l, r, x + 1) - lt(l, r, x);
    }

    // O(sqrt(N) logU) -- the k-th smallest of a[l..r] (k = 1 is the min); needs 0 <= l <= r < size() and 1 <= k <= r -
    // l + 1, else throws out_of_range
    LEETCODE_NO_SANITIZE T kthSmallest(long long l, long long r, long long k) const {
        rangeCheck("kthSmallest", l, r);
        if (k < 1 || k > r - l + 1) throw out_of_range("kthSmallest: needs 1 <= k <= r - l + 1");
        return (T)kth(l, r, k);
    }

    // O(sqrt(N) logU) -- min of a[l..r]; needs 0 <= l <= r < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE T rangeMin(long long l, long long r) const {
        rangeCheck("rangeMin", l, r);
        return (T)kth(l, r, 1);
    }

    // O(sqrt(N) logU) -- max of a[l..r]; needs 0 <= l <= r < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE T rangeMax(long long l, long long r) const {
        rangeCheck("rangeMax", l, r);
        return (T)kth(l, r, r - l + 1);
    }

    // O(sqrt(N) logU) -- smallest value >= x in a[l..r], or nullopt; needs 0 <= l <= r < size(), else throws
    // out_of_range
    LEETCODE_NO_SANITIZE optional<T> smallestGteX(long long l, long long r, long long x) const {
        rangeCheck("smallestGteX", l, r);
        long long c = lt(l, r, x);
        if (c == r - l + 1) return nullopt;
        return (T)kth(l, r, c + 1);
    }

    // O(sqrt(N) logU) -- smallest value > x in a[l..r], or nullopt; needs 0 <= l <= r < size(), else throws
    // out_of_range
    LEETCODE_NO_SANITIZE optional<T> smallestGtX(long long l, long long r, long long x) const {
        rangeCheck("smallestGtX", l, r);
        long long c = lt(l, r, x + 1);
        if (c == r - l + 1) return nullopt;
        return (T)kth(l, r, c + 1);
    }

    // O(sqrt(N) logU) -- largest value <= x in a[l..r], or nullopt; needs 0 <= l <= r < size(), else throws
    // out_of_range
    LEETCODE_NO_SANITIZE optional<T> largestLteX(long long l, long long r, long long x) const {
        rangeCheck("largestLteX", l, r);
        long long c = lt(l, r, x + 1);
        if (!c) return nullopt;
        return (T)kth(l, r, c);
    }

    // O(sqrt(N) logU) -- largest value < x in a[l..r], or nullopt; needs 0 <= l <= r < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE optional<T> largestLtX(long long l, long long r, long long x) const {
        rangeCheck("largestLtX", l, r);
        long long c = lt(l, r, x);
        if (!c) return nullopt;
        return (T)kth(l, r, c);
    }

    // O(sqrt(N) logU) -- min of the whole array; throws out_of_range if it is empty
    LEETCODE_NO_SANITIZE T minAll() const {
        if (!size()) throw out_of_range("minAll: the array is empty");
        return (T)kth(0, size() - 1, 1);
    }

    // O(sqrt(N) logU) -- max of the whole array; throws out_of_range if it is empty
    LEETCODE_NO_SANITIZE T maxAll() const {
        if (!size()) throw out_of_range("maxAll: the array is empty");
        return (T)kth(0, size() - 1, size());
    }

  private:
    LEETCODE_NO_SANITIZE long long blockEnd(int b) const { return min((long long)n, (long long)b * S + S) - 1; }

    LEETCODE_NO_SANITIZE void checkRange(const char* name, long long l, long long r) const {
        if (l < 0 || l > r || r >= n) throw out_of_range(string(name) + ": needs 0 <= l <= r < size()");
    }

    LEETCODE_NO_SANITIZE void checkVal(const char* name, T v) const {
        if (v < 0 || (long long)v > top) throw invalid_argument(string(name) + ": needs 0 <= value < 2^bits");
    }

    LEETCODE_NO_SANITIZE long long get(long long i) const {
        int b = (int)(i / S);
        return (uni[b] < 0 ? arr[i] : uni[b]) ^ tag[b];
    }

    // c copies of v into the trie at root, new nodes taken from free on; returns the next free node
    LEETCODE_NO_SANITIZE int insert(int root, long long v, int c, int free) const {
        int t = root;
        nd[t].C += c;
        for (int h = B - 1; h >= 0; h--) {
            int& k = v >> h & 1 ? nd[t].R : nd[t].L;
            if (!k) {
                nd[free] = Node();
                k = free++;
            }
            t = k;
            nd[t].C += c;
        }
        return free;
    }

    // block b's trie (and bit counts) from its stored values; its lazy tags must be clear
    LEETCODE_NO_SANITIZE void rebuild(int b) {
        int root = base[b], free = root + 1;
        nd[root] = Node();
        for (long long i = (long long)b * S; i <= blockEnd(b); i++) {
            free = insert(root, arr[i], 1, free);
        }
    }

    // every value of block b becomes v: its trie is one path of copies
    LEETCODE_NO_SANITIZE void assignBlock(int b, long long v) {
        int root = base[b], size = (int)(blockEnd(b) - (long long)b * S + 1);
        nd[root] = Node();
        insert(root, v, size, root + 1);
        tag[b] = 0, uni[b] = v;
    }

    // write block b's lazy tags into its stored values (its trie must be rebuilt after)
    LEETCODE_NO_SANITIZE void push(int b) {
        long long s = (long long)b * S, e = blockEnd(b);
        if (uni[b] >= 0) {
            for (long long i = s; i <= e; i++) arr[i] = uni[b] ^ tag[b];
        } else if (tag[b]) {
            for (long long i = s; i <= e; i++) arr[i] ^= tag[b];
        }
        tag[b] = 0, uni[b] = -1;
    }

    LEETCODE_NO_SANITIZE void rangeCheck(const char* name, long long l, long long r) const { checkRange(name, l, r); }

    // # < k
    LEETCODE_NO_SANITIZE long long lt(long long l, long long r, long long k) const {
        return cntLt(sources(l, r), r - l + 1, k, 0);
    }

    // k-th smallest
    LEETCODE_NO_SANITIZE long long kth(long long l, long long r, long long k) const {
        return kthX(sources(l, r), k, 0);
    }

    // checks 0 <= l <= r < size(); the tries whose values make up a[l..r]
    LEETCODE_NO_SANITIZE Src span(const char* name, long long l, long long r) const {
        checkRange(name, l, r);
        return sources(l, r);
    }

    // the tries whose values make up a[l..r]: the whole blocks, plus the scratch trie holding the partly covered ends
    LEETCODE_NO_SANITIZE Src sources(long long l, long long r) const {
        Src src;
        bool ends = false;
        int free = scratch + 1;
        nd[scratch] = Node();
        for (int b = (int)(l / S); b <= r / S; b++) {
            long long s = (long long)b * S, e = blockEnd(b);
            if (l <= s && e <= r) {
                src.push_back({base[b], tag[b]});
            } else {
                for (long long i = max(l, s); i <= min(r, e); i++) free = insert(scratch, get(i), 1, free);
                ends = true;
            }
        }
        if (ends) src.push_back({scratch, 0});
        return src;
    }

    LEETCODE_NO_SANITIZE long long cnt(const Src& src) const {
        long long c = 0;
        for (auto& [t, g] : src) c += nd[t].C;
        return c;
    }

    // the count of the children for real bit h = bit, without building them
    LEETCODE_NO_SANITIZE long long childCount(const Src& src, int bit, int h) const {
        long long c = 0;
        for (auto& [t, g] : src) c += nd[(bit ^ (int)(g >> h & 1)) ? nd[t].R : nd[t].L].C;
        return c;
    }

    LEETCODE_NO_SANITIZE void descend(Src& src, int bit, int h) const {
        // src becomes its children for real bit h = bit, in place
        size_t k = 0;
        for (auto& [t, g] : src)
            if (int c = (bit ^ (int)(g >> h & 1)) ? nd[t].R : nd[t].L) src[k++] = {c, g};
        src.resize(k);
    }

    LEETCODE_NO_SANITIZE Src down(const Src& src, int bit, int h) const {
        // the children for real bit h = bit (each through its lazy xor)
        Src out;
        out.reserve(src.size());
        for (auto& [t, g] : src)
            if (int u = (bit ^ (int)(g >> h & 1)) ? nd[t].R : nd[t].L) out.push_back({u, g});
        return out;
    }

    // how many values v below src (all of them: total) have v ^ x < k
    LEETCODE_NO_SANITIZE long long cntLt(Src src, long long total, long long k, long long x) const {
        if (k <= 0) return 0;
        if (k > top) return total;
        long long res = 0;
        for (int h = B - 1; h >= 0 && !src.empty(); h--) {
            int xb = x >> h & 1;
            if (k >> h & 1) {  // every result with bit h = 0 is < k
                res += childCount(src, xb, h);
                descend(src, xb ^ 1, h);
            } else {
                descend(src, xb, h);
            }
        }
        return res;
    }

    // the k-th smallest (1-indexed) v ^ x over the values below src
    LEETCODE_NO_SANITIZE long long kthX(Src src, long long k, long long x) const {
        long long res = 0;
        for (int h = B - 1; h >= 0; h--) {
            int xb = x >> h & 1;
            long long c = childCount(src, xb, h);
            if (k <= c) {
                descend(src, xb, h);
            } else {
                k -= c;
                descend(src, xb ^ 1, h);
                res |= 1LL << h;
            }
        }
        return res;
    }

    // bits h..0 of the largest (big = 1) / smallest v ^ x below src, which holds some value
    LEETCODE_NO_SANITIZE long long extreme(Src src, int h, long long x, int big) const {
        long long res = 0;
        for (; h >= 0; h--) {
            int p = (int)(x >> h & 1) ^ big;  // the child whose result bit is big
            if (childCount(src, p, h)) {
                descend(src, p, h);
                res |= (long long)big << h;
            } else {
                descend(src, p ^ 1, h);
                res |= (long long)(big ^ 1) << h;
            }
        }
        return res;
    }

    // the largest (big = 1) / smallest v ^ x over the values v below src with lo <= v <= hi, or nullopt. Walks down the
    // bits lo and hi share, then splits: below lo's side only the lower bound matters, below hi's only the upper one
    LEETCODE_NO_SANITIZE optional<long long> bestIn(Src src, long long x, long long lo, long long hi, int big) const {
        lo = max(lo, 0LL), hi = min(hi, top);
        if (lo > hi) return nullopt;
        int h = B - 1;
        long long res = 0;
        for (; h >= 0 && (lo >> h & 1) == (hi >> h & 1); h--) {
            int bit = lo >> h & 1;
            descend(src, bit, h);
            if (!cnt(src)) return nullopt;
            res |= (long long)(bit ^ (x >> h & 1)) << h;
        }
        if (h < 0) return res;
        long long xb = x >> h & 1;
        auto c0 = oneSide(down(src, 0, h), h - 1, lo, x, big, 1, res | xb << h);
        auto c1 = oneSide(down(src, 1, h), h - 1, hi, x, big, 0, res | (xb ^ 1) << h);
        if (!c0 || !c1) return c0 ? c0 : c1;
        return big ? max(*c0, *c1) : min(*c0, *c1);
    }

    // below src: the best v ^ x whose bits h..0 are >= (lower = 1) / <= bound's bits h..0, or nullopt; res holds the
    // result's bits above h. Along the path that matches bound, each step off it (to the side the bound allows) is a
    // free subtree: take it at once if its result bit beats the path's, else remember the deepest one
    LEETCODE_NO_SANITIZE optional<long long> oneSide(Src src, int h, long long bound, long long x, int big, int lower,
        long long res) const {
        if (!cnt(src)) return nullopt;
        Src f;
        int fh = -2;
        long long fres = 0;
        for (; h >= 0; h--) {
            int xb = x >> h & 1, bb = bound >> h & 1;
            if (bb != lower) {  // a free side exists: v bit = lower
                Src c = down(src, lower, h);
                if (cnt(c)) {
                    long long cres = res | (long long)(lower ^ xb) << h;
                    if ((lower ^ xb) == big) return cres | extreme(std::move(c), h - 1, x, big);
                    f = std::move(c), fh = h, fres = cres;
                }
            }
            descend(src, bb, h);
            if (!cnt(src)) break;
            res |= (long long)(bb ^ xb) << h;
        }
        if (h < 0) return res;  // v equal to bound below here: allowed (inclusive)
        if (fh == -2) return nullopt;
        return fres | extreme(std::move(f), fh - 1, x, big);
    }
};

// Tree<long long> tree(edges, root, bits);
//
// edges: the tree's n - 1 edges with their weights, vector<vector<int>> (vector<vector<long long>> works too). Whether
//        nodes are 0..n-1 or 1..n is detected automatically from the edge list (smallest label is 0 -> 0..n-1,
//        otherwise 1..n; with no edges, from root)
//   {{a, b, w}, ...}     e.g. {{0, 1, 5}, {1, 2, 7}}
// root: the root node (required), e.g. 0 or 1.
// bits: values live in [0, 2^bits).
//
//   Tree<long long> tree({{0, 1, 5}, {1, 2, 7}}, 0, bits);    // nodes 0..2, rooted at 0
//   Tree<long long> tree({{1, 2, 5}, {2, 3, 7}}, 1, bits);    // nodes 1..3, rooted at 1
//
// T is the type the weights are kept in (long long, or int).
// An edge is named by its two ends in either order: (a, b) and (b, a) are the same edge. A path a..b covers the edges
// between a and b, and a subtree covers the edges below node. A search that finds an edge returns its lower end (the
// end farther from the root). A query with no edges to look at (a path a..a, a leaf's subtree) says what it returns.
// Nodes go in and come out with your labels, -1 means "none", and a label that is not in the tree throws out_of_range.
// Nothing recurses, so a 10^6-node chain is fine.
//
// How it works: one heavy-light pass gives every node a position, so that each heavy chain and each subtree is one
// stretch of positions (pos[node] .. pos[node] + sz[node] - 1). Each edge's weight sits at its lower end's position in
// the range structure above (SqrtXorTries); the root's position holds no edge. The edges below node are one range of
// it, and the edges of a path a..b are O(log n) ranges, one per chain it crosses.
template <typename T>
struct Tree {
    int n, lo, hi, root;  // nodes are lo..hi
    // by node label: parent (-1 for the root), depth, subtree size, top of its chain, position
    HotVector<int> par, dep, sz, head, pos;
    HotVector<int> order;  // order[pos[v]] = v
    // depthPos[depthStart[d] .. depthStart[d + 1]) = the positions of the nodes at depth d, increasing
    HotVector<int> depthStart, depthPos;
    SqrtXorTries<T> seg;  // each edge's weight, at its lower end's position

    // O(n * log U) -- builds the layout and the range structure; throws invalid_argument when the edges are not one
    // tree on nodes 0..n-1 or 1..n, or an edge has no weight
    template <typename E = int> Tree(const vector<vector<E>>& edges, int root, int bits)
        : seg(layout(edges, root), bits) {}

    // lays the tree out (fills the arrays above) and returns each edge's weight at its lower end's position
    template <typename E> vector<T> layout(const vector<vector<E>>& edges, int root) {
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

    // the position that holds the edge a - b: its lower end's (a and b in either order)
    LEETCODE_NO_SANITIZE int edgeAt(const char* name, int a, int b) const {
        if (a < lo || a > hi || b < lo || b > hi) bad(name);
        if (par[a] == b) return pos[a];
        if (par[b] == a) return pos[b];
        throw out_of_range(string(name) + ": needs an edge between a and b");
    }

    // O(1) -- weight(a - b); a and b are the edge's two ends, in either order
    LEETCODE_NO_SANITIZE auto edgeGet(int a, int b) {
        return seg.pointGet(edgeAt("edgeGet", a, b));
    }

    // O(sqrt(n) * log U) -- weight(a - b) = w; a and b are the edge's two ends, in either order
    LEETCODE_NO_SANITIZE void edgeAssign(int a, int b, T w) {
        seg.pointAssign(edgeAt("edgeAssign", a, b), w);
    }

    // O(sqrt(n) * log U * log n) -- weight = w for every edge on the path a..b
    LEETCODE_NO_SANITIZE void edgePathAssign(int a, int b, T w) {
        if (a < lo || a > hi || b < lo || b > hi) bad("edgePathAssign");
        while (head[a] != head[b]) {
            if (dep[head[a]] < dep[head[b]]) {
                int t = a;
                a = b, b = t;
            }
            seg.rangeAssign(pos[head[a]], pos[a], w);
            a = par[head[a]];
        }
        int l = pos[a], r = pos[b];
        if (l < r) seg.rangeAssign(l + 1, r, w);  // (the lca's own position is the edge above it)
        else if (l > r) seg.rangeAssign(r + 1, l, w);
    }

    // O(sqrt(n) * log U * log n) -- weight ^= w for every edge on the path a..b
    LEETCODE_NO_SANITIZE void edgePathXORApply(int a, int b, T w) {
        if (a < lo || a > hi || b < lo || b > hi) bad("edgePathXORApply");
        while (head[a] != head[b]) {
            if (dep[head[a]] < dep[head[b]]) {
                int t = a;
                a = b, b = t;
            }
            seg.rangeXorApply(pos[head[a]], pos[a], w);
            a = par[head[a]];
        }
        int l = pos[a], r = pos[b];
        if (l < r) seg.rangeXorApply(l + 1, r, w);  // (the lca's own position is the edge above it)
        else if (l > r) seg.rangeXorApply(r + 1, l, w);
    }

    // O(sqrt(n) * log U * log n) -- min edge weight on the path a..b; the largest value of its type when a == b (no
    // edges)
    LEETCODE_NO_SANITIZE auto edgePathMin(int a, int b) {
        if (a < lo || a > hi || b < lo || b > hi) bad("edgePathMin");
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
        if (l < r) {  // (the lca's own position is the edge above it)
            R v = seg.rangeMin(l + 1, r);
            if (v < res) res = v;
        }
        return res;
    }

    // O(sqrt(n) * log U * log n) -- max edge weight on the path a..b; the smallest value of its type when a == b (no
    // edges)
    LEETCODE_NO_SANITIZE auto edgePathMax(int a, int b) {
        if (a < lo || a > hi || b < lo || b > hi) bad("edgePathMax");
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
        if (l < r) {  // (the lca's own position is the edge above it)
            R v = seg.rangeMax(l + 1, r);
            if (v > res) res = v;
        }
        return res;
    }

    // O(sqrt(n) * log U * log n) -- how many edge weights on the path a..b are < x; 0 when a == b (no edges)
    LEETCODE_NO_SANITIZE auto edgePathCountLtX(int a, int b, long long x) {
        if (a < lo || a > hi || b < lo || b > hi) bad("edgePathCountLtX");
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
        if (l < r) {  // (the lca's own position is the edge above it)
            R v = seg.countLtX(l + 1, r, x);
            res += v;
        }
        return res;
    }

    // O(sqrt(n) * log U * log n) -- how many edge weights on the path a..b are <= x; 0 when a == b (no edges)
    LEETCODE_NO_SANITIZE auto edgePathCountLteX(int a, int b, long long x) {
        if (a < lo || a > hi || b < lo || b > hi) bad("edgePathCountLteX");
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
        if (l < r) {  // (the lca's own position is the edge above it)
            R v = seg.countLteX(l + 1, r, x);
            res += v;
        }
        return res;
    }

    // O(sqrt(n) * log U * log n) -- how many edge weights on the path a..b are > x; 0 when a == b (no edges)
    LEETCODE_NO_SANITIZE auto edgePathCountGtX(int a, int b, long long x) {
        if (a < lo || a > hi || b < lo || b > hi) bad("edgePathCountGtX");
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
        if (l < r) {  // (the lca's own position is the edge above it)
            R v = seg.countGtX(l + 1, r, x);
            res += v;
        }
        return res;
    }

    // O(sqrt(n) * log U * log n) -- how many edge weights on the path a..b are >= x; 0 when a == b (no edges)
    LEETCODE_NO_SANITIZE auto edgePathCountGteX(int a, int b, long long x) {
        if (a < lo || a > hi || b < lo || b > hi) bad("edgePathCountGteX");
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
        if (l < r) {  // (the lca's own position is the edge above it)
            R v = seg.countGteX(l + 1, r, x);
            res += v;
        }
        return res;
    }

    // O(sqrt(n) * log U * log n) -- how many edge weights on the path a..b are in [low, high]; 0 when a == b (no edges)
    LEETCODE_NO_SANITIZE auto edgePathCountInValRange(int a, int b, long long low, long long high) {
        if (a < lo || a > hi || b < lo || b > hi) bad("edgePathCountInValRange");
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
        if (l < r) {  // (the lca's own position is the edge above it)
            R v = seg.countInValRange(l + 1, r, low, high);
            res += v;
        }
        return res;
    }

    // O(sqrt(n) * log U * log n) -- smallest of the edge weights on the path a..b that is >= x (nullopt if none);
    // nullopt when a == b (no edges)
    LEETCODE_NO_SANITIZE auto edgePathSmallestGteX(int a, int b, long long x) {
        if (a < lo || a > hi || b < lo || b > hi) bad("edgePathSmallestGteX");
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
        if (l < r) {  // (the lca's own position is the edge above it)
            R v = seg.smallestGteX(l + 1, r, x);
            if (v && (!res || *v < *res)) res = v;
        }
        return res;
    }

    // O(sqrt(n) * log U * log n) -- smallest of the edge weights on the path a..b that is > x (nullopt if none);
    // nullopt when a == b (no edges)
    LEETCODE_NO_SANITIZE auto edgePathSmallestGtX(int a, int b, long long x) {
        if (a < lo || a > hi || b < lo || b > hi) bad("edgePathSmallestGtX");
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
        if (l < r) {  // (the lca's own position is the edge above it)
            R v = seg.smallestGtX(l + 1, r, x);
            if (v && (!res || *v < *res)) res = v;
        }
        return res;
    }

    // O(sqrt(n) * log U * log n) -- largest of the edge weights on the path a..b that is <= x (nullopt if none);
    // nullopt when a == b (no edges)
    LEETCODE_NO_SANITIZE auto edgePathLargestLteX(int a, int b, long long x) {
        if (a < lo || a > hi || b < lo || b > hi) bad("edgePathLargestLteX");
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
        if (l < r) {  // (the lca's own position is the edge above it)
            R v = seg.largestLteX(l + 1, r, x);
            if (v && (!res || *v > *res)) res = v;
        }
        return res;
    }

    // O(sqrt(n) * log U * log n) -- largest of the edge weights on the path a..b that is < x (nullopt if none); nullopt
    // when a == b (no edges)
    LEETCODE_NO_SANITIZE auto edgePathLargestLtX(int a, int b, long long x) {
        if (a < lo || a > hi || b < lo || b > hi) bad("edgePathLargestLtX");
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
        if (l < r) {  // (the lca's own position is the edge above it)
            R v = seg.largestLtX(l + 1, r, x);
            if (v && (!res || *v > *res)) res = v;
        }
        return res;
    }

    // O(sqrt(n) * log U * log n) -- how many edge weights on the path a..b equal x; 0 when a == b (no edges)
    LEETCODE_NO_SANITIZE auto edgePathCountOccurrences(int a, int b, long long x) {
        if (a < lo || a > hi || b < lo || b > hi) bad("edgePathCountOccurrences");
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
        if (l < r) {  // (the lca's own position is the edge above it)
            R v = seg.countOccurrences(l + 1, r, x);
            res += v;
        }
        return res;
    }

    // O(sqrt(n) * log U * log n) -- largest weight ^ x over the edge weights on the path a..b; the smallest value of
    // its type when a == b (no edges)
    LEETCODE_NO_SANITIZE auto edgePathMaxXorAgainstX(int a, int b, long long x) {
        if (a < lo || a > hi || b < lo || b > hi) bad("edgePathMaxXorAgainstX");
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
        if (l < r) {  // (the lca's own position is the edge above it)
            R v = seg.maxXorAgainstX(l + 1, r, x);
            if (v > res) res = v;
        }
        return res;
    }

    // O(sqrt(n) * log U * log n) -- smallest weight ^ x over the edge weights on the path a..b; the largest value of
    // its type when a == b (no edges)
    LEETCODE_NO_SANITIZE auto edgePathMinXorAgainstX(int a, int b, long long x) {
        if (a < lo || a > hi || b < lo || b > hi) bad("edgePathMinXorAgainstX");
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
        if (l < r) {  // (the lca's own position is the edge above it)
            R v = seg.minXorAgainstX(l + 1, r, x);
            if (v < res) res = v;
        }
        return res;
    }

    // O(sqrt(n) * log U) -- weight = w for every edge in node's subtree
    LEETCODE_NO_SANITIZE void edgeSubtreeAssign(int node, T w) {
        if (node < lo || node > hi) bad("edgeSubtreeAssign");
        int l = pos[node] + 1, r = pos[node] + sz[node] - 1;  // (l > r for a leaf: no edges below it)
        if (l > r) return;
        seg.rangeAssign(l, r, w);
    }

    // O(sqrt(n) * log U) -- weight ^= w for every edge in node's subtree
    LEETCODE_NO_SANITIZE void edgeSubtreeXORApply(int node, T w) {
        if (node < lo || node > hi) bad("edgeSubtreeXORApply");
        int l = pos[node] + 1, r = pos[node] + sz[node] - 1;  // (l > r for a leaf: no edges below it)
        if (l > r) return;
        seg.rangeXorApply(l, r, w);
    }

    // O(sqrt(n) * log U) -- min edge weight in node's subtree; the largest value of its type when node is a leaf (no
    // edges)
    LEETCODE_NO_SANITIZE auto edgeSubtreeMin(int node) {
        if (node < lo || node > hi) bad("edgeSubtreeMin");
        int l = pos[node] + 1, r = pos[node] + sz[node] - 1;  // (l > r for a leaf: no edges below it)
        using R = decltype(seg.rangeMin(0, 0));
        if (l > r) return numeric_limits<R>::max();
        return seg.rangeMin(l, r);
    }

    // O(sqrt(n) * log U) -- max edge weight in node's subtree; the smallest value of its type when node is a leaf (no
    // edges)
    LEETCODE_NO_SANITIZE auto edgeSubtreeMax(int node) {
        if (node < lo || node > hi) bad("edgeSubtreeMax");
        int l = pos[node] + 1, r = pos[node] + sz[node] - 1;  // (l > r for a leaf: no edges below it)
        using R = decltype(seg.rangeMax(0, 0));
        if (l > r) return numeric_limits<R>::lowest();
        return seg.rangeMax(l, r);
    }

    // O(sqrt(n) * log U) -- kth smallest of the edge weights in node's subtree (1-indexed: k = 1 is the min); needs at
    // least one edge (not node is a leaf), else throws out_of_range
    LEETCODE_NO_SANITIZE auto edgeSubtreeKthSmallest(int node, long long k) {
        if (node < lo || node > hi) bad("edgeSubtreeKthSmallest");
        int l = pos[node] + 1, r = pos[node] + sz[node] - 1;  // (l > r for a leaf: no edges below it)
        if (l > r) throw out_of_range("edgeSubtreeKthSmallest: needs at least one edge in node's subtree");
        return seg.kthSmallest(l, r, k);
    }

    // O(sqrt(n) * log U) -- how many edge weights in node's subtree are < x; 0 when node is a leaf (no edges)
    LEETCODE_NO_SANITIZE auto edgeSubtreeCountLtX(int node, long long x) {
        if (node < lo || node > hi) bad("edgeSubtreeCountLtX");
        int l = pos[node] + 1, r = pos[node] + sz[node] - 1;  // (l > r for a leaf: no edges below it)
        using R = decltype(seg.countLtX(0, 0, x));
        if (l > r) return R(0);
        return seg.countLtX(l, r, x);
    }

    // O(sqrt(n) * log U) -- how many edge weights in node's subtree are <= x; 0 when node is a leaf (no edges)
    LEETCODE_NO_SANITIZE auto edgeSubtreeCountLteX(int node, long long x) {
        if (node < lo || node > hi) bad("edgeSubtreeCountLteX");
        int l = pos[node] + 1, r = pos[node] + sz[node] - 1;  // (l > r for a leaf: no edges below it)
        using R = decltype(seg.countLteX(0, 0, x));
        if (l > r) return R(0);
        return seg.countLteX(l, r, x);
    }

    // O(sqrt(n) * log U) -- how many edge weights in node's subtree are > x; 0 when node is a leaf (no edges)
    LEETCODE_NO_SANITIZE auto edgeSubtreeCountGtX(int node, long long x) {
        if (node < lo || node > hi) bad("edgeSubtreeCountGtX");
        int l = pos[node] + 1, r = pos[node] + sz[node] - 1;  // (l > r for a leaf: no edges below it)
        using R = decltype(seg.countGtX(0, 0, x));
        if (l > r) return R(0);
        return seg.countGtX(l, r, x);
    }

    // O(sqrt(n) * log U) -- how many edge weights in node's subtree are >= x; 0 when node is a leaf (no edges)
    LEETCODE_NO_SANITIZE auto edgeSubtreeCountGteX(int node, long long x) {
        if (node < lo || node > hi) bad("edgeSubtreeCountGteX");
        int l = pos[node] + 1, r = pos[node] + sz[node] - 1;  // (l > r for a leaf: no edges below it)
        using R = decltype(seg.countGteX(0, 0, x));
        if (l > r) return R(0);
        return seg.countGteX(l, r, x);
    }

    // O(sqrt(n) * log U) -- how many edge weights in node's subtree are in [low, high]; 0 when node is a leaf (no
    // edges)
    LEETCODE_NO_SANITIZE auto edgeSubtreeCountInValRange(int node, long long low, long long high) {
        if (node < lo || node > hi) bad("edgeSubtreeCountInValRange");
        int l = pos[node] + 1, r = pos[node] + sz[node] - 1;  // (l > r for a leaf: no edges below it)
        using R = decltype(seg.countInValRange(0, 0, low, high));
        if (l > r) return R(0);
        return seg.countInValRange(l, r, low, high);
    }

    // O(sqrt(n) * log U) -- smallest of the edge weights in node's subtree that is >= x (nullopt if none); nullopt when
    // node is a leaf (no edges)
    LEETCODE_NO_SANITIZE auto edgeSubtreeSmallestGteX(int node, long long x) {
        if (node < lo || node > hi) bad("edgeSubtreeSmallestGteX");
        int l = pos[node] + 1, r = pos[node] + sz[node] - 1;  // (l > r for a leaf: no edges below it)
        using R = decltype(seg.smallestGteX(0, 0, x));
        if (l > r) return R();
        return seg.smallestGteX(l, r, x);
    }

    // O(sqrt(n) * log U) -- smallest of the edge weights in node's subtree that is > x (nullopt if none); nullopt when
    // node is a leaf (no edges)
    LEETCODE_NO_SANITIZE auto edgeSubtreeSmallestGtX(int node, long long x) {
        if (node < lo || node > hi) bad("edgeSubtreeSmallestGtX");
        int l = pos[node] + 1, r = pos[node] + sz[node] - 1;  // (l > r for a leaf: no edges below it)
        using R = decltype(seg.smallestGtX(0, 0, x));
        if (l > r) return R();
        return seg.smallestGtX(l, r, x);
    }

    // O(sqrt(n) * log U) -- largest of the edge weights in node's subtree that is <= x (nullopt if none); nullopt when
    // node is a leaf (no edges)
    LEETCODE_NO_SANITIZE auto edgeSubtreeLargestLteX(int node, long long x) {
        if (node < lo || node > hi) bad("edgeSubtreeLargestLteX");
        int l = pos[node] + 1, r = pos[node] + sz[node] - 1;  // (l > r for a leaf: no edges below it)
        using R = decltype(seg.largestLteX(0, 0, x));
        if (l > r) return R();
        return seg.largestLteX(l, r, x);
    }

    // O(sqrt(n) * log U) -- largest of the edge weights in node's subtree that is < x (nullopt if none); nullopt when
    // node is a leaf (no edges)
    LEETCODE_NO_SANITIZE auto edgeSubtreeLargestLtX(int node, long long x) {
        if (node < lo || node > hi) bad("edgeSubtreeLargestLtX");
        int l = pos[node] + 1, r = pos[node] + sz[node] - 1;  // (l > r for a leaf: no edges below it)
        using R = decltype(seg.largestLtX(0, 0, x));
        if (l > r) return R();
        return seg.largestLtX(l, r, x);
    }

    // O(sqrt(n) * log U) -- how many edge weights in node's subtree equal x; 0 when node is a leaf (no edges)
    LEETCODE_NO_SANITIZE auto edgeSubtreeCountOccurrences(int node, long long x) {
        if (node < lo || node > hi) bad("edgeSubtreeCountOccurrences");
        int l = pos[node] + 1, r = pos[node] + sz[node] - 1;  // (l > r for a leaf: no edges below it)
        using R = decltype(seg.countOccurrences(0, 0, x));
        if (l > r) return R(0);
        return seg.countOccurrences(l, r, x);
    }

    // O(sqrt(n) * log U) -- largest weight ^ x over the edge weights in node's subtree; the smallest value of its type
    // when node is a leaf (no edges)
    LEETCODE_NO_SANITIZE auto edgeSubtreeMaxXorAgainstX(int node, long long x) {
        if (node < lo || node > hi) bad("edgeSubtreeMaxXorAgainstX");
        int l = pos[node] + 1, r = pos[node] + sz[node] - 1;  // (l > r for a leaf: no edges below it)
        using R = decltype(seg.maxXorAgainstX(0, 0, x));
        if (l > r) return numeric_limits<R>::lowest();
        return seg.maxXorAgainstX(l, r, x);
    }

    // O(sqrt(n) * log U) -- smallest weight ^ x over the edge weights in node's subtree; the largest value of its type
    // when node is a leaf (no edges)
    LEETCODE_NO_SANITIZE auto edgeSubtreeMinXorAgainstX(int node, long long x) {
        if (node < lo || node > hi) bad("edgeSubtreeMinXorAgainstX");
        int l = pos[node] + 1, r = pos[node] + sz[node] - 1;  // (l > r for a leaf: no edges below it)
        using R = decltype(seg.minXorAgainstX(0, 0, x));
        if (l > r) return numeric_limits<R>::max();
        return seg.minXorAgainstX(l, r, x);
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
