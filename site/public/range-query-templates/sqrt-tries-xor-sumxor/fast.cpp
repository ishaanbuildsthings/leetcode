// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/sqrt-tries-xor-sumxor/fast.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: countGtX countGteX countInValRange countLtX countLteX countOccurrences countXorGtK countXorGteK countXorLtK countXorLteK getAll kthSmallest kthXor largestLtX largestLteX largestXorLtK largestXorLteK maxAll maxXorAgainstX maxXorWithVGtM maxXorWithVGteM maxXorWithVInValRange maxXorWithVLtM maxXorWithVLteM minAll minXorAgainstX minXorWithVGtM minXorWithVGteM minXorWithVInValRange minXorWithVLtM minXorWithVLteM pointAssign pointGet rangeAssign rangeMax rangeMin rangeSum rangeXorApply rangeXorQuery size smallestGtX smallestGteX smallestXorGtK smallestXorGteK sumXor
// @data-structure-type: sqrt-tries
// @complexities:
//   countGtX: sqrt(N)*log(U)
//   countGteX: sqrt(N)*log(U)
//   countInValRange: sqrt(N)*log(U)
//   countLtX: sqrt(N)*log(U)
//   countLteX: sqrt(N)*log(U)
//   countOccurrences: sqrt(N)*log(U)
//   countXorGtK: sqrt(N)*log(U)
//   countXorGteK: sqrt(N)*log(U)
//   countXorLtK: sqrt(N)*log(U)
//   countXorLteK: sqrt(N)*log(U)
//   getAll: N
//   kthSmallest: sqrt(N)*log(U)
//   kthXor: sqrt(N)*log(U)
//   largestLtX: sqrt(N)*log(U)
//   largestLteX: sqrt(N)*log(U)
//   largestXorLtK: sqrt(N)*log(U)
//   largestXorLteK: sqrt(N)*log(U)
//   maxAll: sqrt(N)*log(U)
//   maxXorAgainstX: sqrt(N)*log(U)
//   maxXorWithVGtM: sqrt(N)*log(U)
//   maxXorWithVGteM: sqrt(N)*log(U)
//   maxXorWithVInValRange: sqrt(N)*log(U)
//   maxXorWithVLtM: sqrt(N)*log(U)
//   maxXorWithVLteM: sqrt(N)*log(U)
//   minAll: sqrt(N)*log(U)
//   minXorAgainstX: sqrt(N)*log(U)
//   minXorWithVGtM: sqrt(N)*log(U)
//   minXorWithVGteM: sqrt(N)*log(U)
//   minXorWithVInValRange: sqrt(N)*log(U)
//   minXorWithVLtM: sqrt(N)*log(U)
//   minXorWithVLteM: sqrt(N)*log(U)
//   pointAssign: sqrt(N)*log(U)
//   pointGet: 1
//   rangeAssign: sqrt(N)*log(U)
//   rangeMax: sqrt(N)*log(U)
//   rangeMin: sqrt(N)*log(U)
//   rangeSum: sqrt(N)*log(U)
//   rangeXorApply: sqrt(N)*log(U)
//   rangeXorQuery: sqrt(N)*log(U)
//   size: 1
//   smallestGtX: sqrt(N)*log(U)
//   smallestGteX: sqrt(N)*log(U)
//   smallestXorGtK: sqrt(N)*log(U)
//   smallestXorGteK: sqrt(N)*log(U)
//   sumXor: sqrt(N)*log(U)
//   build: N*log(U)
// @memory:
//   layout: none
//   node: L[1*N*log(U)] R[1*N*log(U)] C[1*N*log(U)]
//   tags: none
//   other: arr[1*N] tag[1*sqrt(N)] uni[1*sqrt(N)] ones[1*sqrt(N)*log(U)]
//   note: blocks of about sqrt N, each a binary trie of its stored values (at most its length times log U nodes, U = 2^bits) with a lazy xor and a lazy assign; a scratch trie of 2 sqrt N log U nodes for the partly covered ends of a query

// a[l..r] as a multiset, asked about v ^ x over its values v, with range xor-apply, range assign and point assign. The
// array is cut into blocks of about sqrt(N); each block keeps a binary trie (one level per bit, highest bit first) of
// its
// stored values, a lazy xor (its real values are stored ^ tag) and a lazy assign (the trie is one path of copies). A
// whole block updates in O(log U); a partly covered one is rewritten and its trie rebuilt. A query walks the tries of
// the whole blocks inside l..r down together, each through its own lazy xor, plus a scratch trie of the partly covered
// ends. Values and every x must lie in [0, 2^bits); thresholds (k, m, lo, hi) can be any integers. 0-indexed,
// inclusive.
// sumXor: per block, how many stored values have each bit set.
// The plain order statistics (counts, k-th, min / max, predecessor / successor) are the same walks with x = 0.
// T: int, long long, ....
// FAST MODE drawbacks compared with template.cpp:
//   - sanitizers are skipped inside this template, so a bad access in it goes unreported
// Same public operations and answers, same limits; it needs GCC or Clang and C++17.
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
    HotVector<int> ones;  // ones[b * B + h] = how many stored values of block b have bit h set

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
        ones.assign((size_t)nb * B, 0);
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

    // O(sqrt(N) logU) -- sum of v ^ x over the values v in a[l..r]; needs 0 <= l <= r < size()
    LEETCODE_NO_SANITIZE long long sumXor(long long l, long long r, long long x) const {
        checkRange("sumXor", l, r);
        vector<long long> cntOnes(B, 0);
        long long res = 0, cnt = 0;  // cnt: how many values the whole blocks hold
        for (int b = (int)(l / S); b <= r / S; b++) {
            long long s = (long long)b * S, e = blockEnd(b);
            if (l <= s && e <= r) {
                long long size = e - s + 1;
                cnt += size;
                for (int h = 0; h < B;
                    h++) cntOnes[h] += tag[b] >> h & 1 ? size - ones[(size_t)b * B + h] : ones[(size_t)b * B + h];
            } else {
                for (long long i = max(l, s); i <= min(r, e); i++) res += get(i) ^ x;
            }
        }
        for (int h = 0; h < B; h++) res += (x >> h & 1 ? cnt - cntOnes[h] : cntOnes[h]) << h;
        return res;
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
    // l + 1,
    // else throws out_of_range
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

    // O(sqrt(N) logU) -- a[l] + ... + a[r]; needs 0 <= l <= r < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE long long rangeSum(long long l, long long r) const {
        rangeCheck("rangeSum", l, r);
        return sumAll(l, r);
    }

    // O(sqrt(N) logU) -- a[l] ^ ... ^ a[r]; needs 0 <= l <= r < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE long long rangeXorQuery(long long l, long long r) const {
        rangeCheck("rangeXorQuery", l, r);
        return xorAll(l, r);
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
        fill(ones.begin() + (size_t)b * B, ones.begin() + (size_t)(b + 1) * B, 0);
        for (long long i = (long long)b * S; i <= blockEnd(b); i++) {
            free = insert(root, arr[i], 1, free);
            for (int h = 0; h < B; h++) ones[(size_t)b * B + h] += arr[i] >> h & 1;
        }
    }

    // every value of block b becomes v: its trie is one path of copies
    LEETCODE_NO_SANITIZE void assignBlock(int b, long long v) {
        int root = base[b], size = (int)(blockEnd(b) - (long long)b * S + 1);
        nd[root] = Node();
        insert(root, v, size, root + 1);
        tag[b] = 0, uni[b] = v;
        for (int h = 0; h < B; h++) ones[(size_t)b * B + h] = v >> h & 1 ? size : 0;
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

    LEETCODE_NO_SANITIZE long long sumAll(long long l, long long r) const { return sumXor(l, r, 0); }

    LEETCODE_NO_SANITIZE long long xorAll(long long l, long long r) const {
        // each bit is set in an odd number of values
        long long res = 0;
        for (int b = (int)(l / S); b <= r / S; b++) {
            long long s = (long long)b * S, e = blockEnd(b);
            if (l <= s && e <= r) {
                long long size = e - s + 1;
                for (int h = 0; h < B; h++) {
                    long long c = tag[b] >> h & 1 ? size - ones[(size_t)b * B + h] : ones[(size_t)b * B + h];
                    res ^= (c & 1) << h;
                }
            } else {
                for (long long i = max(l, s); i <= min(r, e); i++) res ^= get(i);
            }
        }
        return res;
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
