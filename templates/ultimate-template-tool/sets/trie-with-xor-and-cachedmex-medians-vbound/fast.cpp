// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/sets/trie-with-xor-and-cachedmex-medians-vbound/fast.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: add addCount andOfAll andOfGtX andOfGteX andOfInValRange andOfKthLargestRange andOfKthSmallestRange andOfLargestK andOfLtX andOfLteX andOfSmallestK clear count countDistinct countDistinctInValRange countGtX countGteX countInValRange countLtX countLteX countXorGtK countXorGteK countXorLtK countXorLteK firstIndex kth kthXor largestLtX largestLteX largestXorLtK largestXorLteK lastIndex max maxXorAgainstX maxXorWithVGtM maxXorWithVGteM maxXorWithVInValRange maxXorWithVLtM maxXorWithVLteM medianHigh medianLow mex mexXor min minXorAgainstX minXorWithVGtM minXorWithVGteM minXorWithVInValRange minXorWithVLtM minXorWithVLteM pop popMax popMin remove removeAll removeCount removeInValRange size smallestGtX smallestGteX smallestXorGtK smallestXorGteK xorOfAll xorOfGtX xorOfGteX xorOfInValRange xorOfKthLargestRange xorOfKthSmallestRange xorOfLargestK xorOfLtX xorOfLteX xorOfSmallestK
// @data-structure-type: trie
// @values: online-bits
// @keys: numbers
// @tracks: vbound medians mex
// @complexities:
//   add: log(U)
//   addCount: log(U)
//   andOfAll: 1
//   andOfGtX: log(U)
//   andOfGteX: log(U)
//   andOfInValRange: log(U)
//   andOfKthLargestRange: log(U)
//   andOfKthSmallestRange: log(U)
//   andOfLargestK: log(U)
//   andOfLtX: log(U)
//   andOfLteX: log(U)
//   andOfSmallestK: log(U)
//   clear: 1 amortized
//   count: log(U)
//   countDistinct: 1
//   countDistinctInValRange: log(U)
//   countGtX: log(U)
//   countGteX: log(U)
//   countInValRange: log(U)
//   countLtX: log(U)
//   countLteX: log(U)
//   countXorGtK: log(U)
//   countXorGteK: log(U)
//   countXorLtK: log(U)
//   countXorLteK: log(U)
//   firstIndex: log(U)
//   kth: log(U)
//   kthXor: log(U)
//   largestLtX: log(U)
//   largestLteX: log(U)
//   largestXorLtK: log(U)
//   largestXorLteK: log(U)
//   lastIndex: log(U)
//   max: 1
//   maxXorAgainstX: log(U)
//   maxXorWithVGtM: log(U)
//   maxXorWithVGteM: log(U)
//   maxXorWithVInValRange: log(U)
//   maxXorWithVLtM: log(U)
//   maxXorWithVLteM: log(U)
//   medianHigh: 1
//   medianLow: 1
//   mex: 1
//   mexXor: log(U)
//   min: 1
//   minXorAgainstX: log(U)
//   minXorWithVGtM: log(U)
//   minXorWithVGteM: log(U)
//   minXorWithVInValRange: log(U)
//   minXorWithVLtM: log(U)
//   minXorWithVLteM: log(U)
//   pop: log(U)
//   popMax: log(U)
//   popMin: log(U)
//   remove: log(U)
//   removeAll: log(U)
//   removeCount: log(U)
//   removeInValRange: log(U) amortized
//   size: 1
//   smallestGtX: log(U)
//   smallestGteX: log(U)
//   smallestXorGtK: log(U)
//   smallestXorGteK: log(U)
//   xorOfAll: 1
//   xorOfGtX: log(U)
//   xorOfGteX: log(U)
//   xorOfInValRange: log(U)
//   xorOfKthLargestRange: log(U)
//   xorOfKthSmallestRange: log(U)
//   xorOfLargestK: log(U)
//   xorOfLtX: log(U)
//   xorOfLteX: log(U)
//   xorOfSmallestK: log(U)
//   build: 1
// @memory:
//   layout: sparse
//   node: c[1*log(U)] p[1*log(U)] mn[1*log(U)] mx[1*log(U)] xor[1*log(U)] and[1*log(U)]
//   tags: none
//   other: children[2*log(U)]
//   note: per add of a new value, one node per bit of its path; U = 2^bits. Each multiset owns its nodes (clear() keeps the arrays' capacity)

// Ordered multiset of integers in [0, 2^bits) as a binary trie: one level per bit, highest bit first; each node keeps
// how many copies, how many distinct values, the smallest and largest value, their xor, their AND are below it. Besides
// the usual ordered queries it answers questions
// about v ^ x over every value v (max / min / k-th / counts / closest to a bound / limits on v, mex) by walking one bit
// per level, so O(bits) each. Each multiset owns its node arrays (node 0 = empty, node 1 = the root); nodes are never
// removed. T: int, long long, ...; sums in S (long long for small T).
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
#ifdef __GLIBCXX__
    LEETCODE_NO_SANITIZE_INLINE typename vector<U>::reference operator[](size_t i) { return this->_M_impl._M_start[i]; }
    LEETCODE_NO_SANITIZE_INLINE typename vector<U>::const_reference operator[](size_t i) const {
        return this->_M_impl._M_start[i];
    }
    LEETCODE_NO_SANITIZE_INLINE size_t size() const { return size_t(this->_M_impl._M_finish - this->_M_impl._M_start); }
#endif
};

template <typename T>
struct TrieMultiset {
    // what largestLtX, smallestGtX, ... return when nothing qualifies: compare with ms.NONE (values are never negative)
    static constexpr T NONE = -1;
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    int B;
    long long top;  // the largest value it can hold
    HotVector<array<int, 2>> ch{{0, 0}, {0, 0}};  // child for bit 0 / bit 1; node 0 = empty, node 1 = the root
    HotVector<long long> c{0, 0};  // copies below
    HotVector<long long> p{0, 0};  // distinct values below
    HotVector<long long> mnv{0, 0}, mxv{0, 0};  // smallest / largest value below (meaningful while its count > 0)
    HotVector<T> xr{0, 0};  // xor of the stored values below with an odd count
    HotVector<T> andv{~T(0), ~T(0)};  // AND of the values below (an empty node's: every bit)
    long long n = 0, d = 0;
    struct Info { T v; long long before, c; };  // a value, copies before it, its copies
    Info low{}, high{};  // both medians, kept current by addRaw while n > 0
    long long mexV = 0;  // the mex, kept current (0 for the empty set)
    T xtotal = 0;  // xor of all values (copies count)

    // O(1) -- an empty multiset for integers in [0, 2^bits) (bits = 30 holds values up to 1073741823)
    TrieMultiset(int bits) : B(bits), top((1LL << bits) - 1) {}

    LEETCODE_NO_SANITIZE int newNode() {  // a new empty node
        ch.push_back({0, 0}), c.push_back(0);
        p.push_back(0);
        mnv.push_back(0), mxv.push_back(0);
        xr.push_back(0);
        andv.push_back(~T(0));
        return int(c.size()) - 1;
    }

    LEETCODE_NO_SANITIZE void clearData() {  // back to just the root (the arrays keep their capacity)
        ch.assign(2, array<int, 2>{0, 0}), c.assign(2, 0);
        p.assign(2, 0);
        mnv.assign(2, 0), mxv.assign(2, 0);
        xr.assign(2, 0);
        andv.assign(2, ~T(0));
    }

    LEETCODE_NO_SANITIZE long long insert(T x, long long k) {  // k copies of x; returns x's new count
        long long y = (long long)x;
        int t = 1;
        c[1] += k;
        T xv = k & 1 ? T(y) : T(0);  // (with an odd k the stored value flips in or out of each xor on its path)
        xr[1] ^= xv;
        int path[66], dep = 0;
        path[dep++] = 1;
        for (int h = B - 1; h >= 0; h--) {
            int b = int(y >> h & 1);
            if (!ch[t][b]) {
                int u = newNode();
                ch[t][b] = u;
            }
            t = ch[t][b];
            c[t] += k;
            xr[t] ^= xv;
            path[dep++] = t;
        }
        long long f = c[t];
        if (!f || f == k) {  // x appeared or disappeared
            d += f ? 1 : -1;
            for (int i = 0; i < dep; i++) p[path[i]] += f ? 1 : -1;
            if (f) mnv[t] = mxv[t] = (long long)x;
            andv[t] = f ? x : ~T(0);
            for (int i = dep - 2; i >= 0; i--) {  // from the bottom: what is present below each node changed
                int u = path[i], l = ch[u][0], r = ch[u][1];
                mnv[u] = c[l] ? mnv[l] : mnv[r];
                mxv[u] = c[r] ? mxv[r] : mxv[l];
                andv[u] = andv[l] & andv[r];
            }
        }
        return f;
    }

    LEETCODE_NO_SANITIZE long long cntLt(long long b, long long key) const {  // copies whose stored value ^ key is < b
        if (b <= 0) return 0;
        if (b > top) return n;
        int t = 1;
        long long res = 0;
        for (int h = B - 1; h >= 0 && t; h--) {
            int kb = int(key >> h & 1);
            if (b >> h & 1) res += c[ch[t][kb]], t = ch[t][kb ^ 1];  // everything below the result-bit-0 child is < b
            else t = ch[t][kb];
        }
        return res;
    }

    LEETCODE_NO_SANITIZE long long kthX(long long k, long long key) const {
        // the k-th smallest (1-indexed) stored value ^ key
        int t = 1;
        long long res = 0;
        for (int h = B - 1; h >= 0; h--) {
            int kb = int(key >> h & 1), z = ch[t][kb];
            if (k <= c[z]) t = z;
            else k -= c[z], t = ch[t][kb ^ 1], res |= 1LL << h;
        }
        return res;
    }

    LEETCODE_NO_SANITIZE long long extreme(int t, int h, long long key, bool big) const {
        // bits h..0 of the largest (big) / smallest stored value ^ key below t
        long long res = 0;
        for (; h >= 0; h--) {
            int pb = int(key >> h & 1) ^ int(big);  // the child whose result bit is 1 (big) / 0
            if (c[ch[t][pb]]) {
                t = ch[t][pb];
                if (big) res |= 1LL << h;
            } else {
                t = ch[t][pb ^ 1];
                if (!big) res |= 1LL << h;
            }
        }
        return res;
    }

    LEETCODE_NO_SANITIZE long long lt(T x) const { return cntLt((long long)x, 0); }
    LEETCODE_NO_SANITIZE long long le(T x) const { return cntLt((long long)x + 1, 0); }

    LEETCODE_NO_SANITIZE long long countOf(T x) const {
        if ((long long)x < 0 || (long long)x > top) return 0;
        long long y = (long long)x;
        int t = 1;
        for (int h = B - 1; h >= 0 && t; h--) t = ch[t][y >> h & 1];
        return c[t];
    }

    LEETCODE_NO_SANITIZE T kthAt(long long k) const { return T(kthX(k, 0)); }

    LEETCODE_NO_SANITIZE Info kthInfo(long long k) const {  // the k-th smallest, copies before it, its copies
        int t = 1;
        long long v = 0, before = 0;
        for (int h = B - 1; h >= 0; h--) {
            int l = ch[t][0];
            if (before + c[l] < k) before += c[l], t = ch[t][1], v |= 1LL << h;
            else t = l;
        }
        return {T(v), before, c[t]};
    }

    LEETCODE_NO_SANITIZE long long mexX(long long key) const {  // smallest m >= 0 with no value stored as m ^ key
        if (p[1] > top) return top + 1;  // every value is present
        int t = 1;
        long long res = 0;
        for (int h = B - 1; h >= 0 && t; h--) {
            int kb = int(key >> h & 1), z = ch[t][kb];
            if (p[z] == 1LL << h) res |= 1LL << h, t = ch[t][kb ^ 1];  // that half is full: the answer has bit h set
            else t = z;
        }
        return res;
    }

    LEETCODE_NO_SANITIZE long long findMex() const { return mexX(0); }

    LEETCODE_NO_SANITIZE long long distinctLt(T x) const {  // distinct values < x
        long long b = (long long)x, key = 0;
        if (b <= 0) return 0;
        if (b > top) return d;
        int t = 1;
        long long res = 0;
        for (int h = B - 1; h >= 0 && t; h--) {
            int kb = int(key >> h & 1);
            if (b >> h & 1) res += p[ch[t][kb]], t = ch[t][kb ^ 1];
            else t = ch[t][kb];
        }
        return res;
    }

    LEETCODE_NO_SANITIZE optional<T> bestIn(long long x, long long lo, long long hi, bool big) const {
        // the largest (big) / smallest v ^ x over the values v in [lo, hi]
        lo = std::max(lo, 0LL), hi = std::min(hi, top);
        if (lo > hi) return nullopt;
        int t = 1, h = B - 1;
        // the bits lo and hi share: one path
        for (; h >= 0 && (lo >> h & 1) == (hi >> h & 1); h--) t = ch[t][lo >> h & 1];
        if (!c[t]) return nullopt;
        if (h < 0) return T(lo ^ x);  // lo == hi, present
        // where they split, the left child only needs v >= lo and the right child only v <= hi
        optional<T> a = bestSide(ch[t][0], h - 1, x, lo, true, big), b = bestSide(ch[t][1], h - 1, x, hi, false, big);
        if (!a || !b) return a ? a : b;
        return big ? std::max(*a, *b) : std::min(*a, *b);
    }

    LEETCODE_NO_SANITIZE optional<T> bestSide(int t, int h, long long x, long long bound, bool ge, bool big) const {
        // best v ^ x below t with v >= bound (ge) / v <= bound
        auto ok = [&](int u) { return c[u] && (ge ? mxv[u] >= bound : mnv[u] <= bound); };
        if (!ok(t)) return nullopt;
        for (; h >= 0; h--) {
            int pb = int(x >> h & 1) ^ int(big);  // the child whose bit of v ^ x is 1 (big) / 0
            t = ok(ch[t][pb]) ? ch[t][pb] : ch[t][pb ^ 1];
        }
        return T(mnv[t] ^ x);
    }

    LEETCODE_NO_SANITIZE void addRaw(T x, long long c) {
        // c copies of x (c < 0 removes); keeps both medians, the mex current
        n += c;
        if (c & 1) xtotal ^= x;  // an odd number of copies flips x in or out of the xor of everything
        long long f = insert(x, c);  // x's new count
        if (c > 0) {
            if constexpr (is_integral_v<T>) if (x == T(mexV)) mexV = findMex();  // x filled the mex
            if (n == c) {  // the set was empty
                low = high = Info{x, 0, c};
                return;
            }
        } else {
            // the last copy of a value below the mex
            if constexpr (is_integral_v<T>) if (x >= 0 && x < T(mexV) && !f) mexV = x;
            if (!n) return;
        }
        // each median is a tracked rank: shift its (value, copies before, copies), and search again only
        // when the rank leaves the tracked value
        if (x < low.v) low.before += c;
        else if (x == low.v) low.c += c;
        long long r = (n + 1) / 2;
        if (r <= low.before || r > low.before + low.c) low = kthInfo(r);
        if (x < high.v) high.before += c;
        else if (x == high.v) high.c += c;
        r = n / 2 + 1;
        if (r <= high.before || r > high.before + high.c) high = kthInfo(r);
    }

    LEETCODE_NO_SANITIZE void resetCached() {  // nothing counted: as newly built
        mexV = 0;
        n = d = 0;
        xtotal = 0;
    }

    LEETCODE_NO_SANITIZE T xlt(T x) const {  // xor of the values < x (copies count)
        long long b = (long long)x;
        if (b <= 0) return 0;
        if (b > top) return xtotal;
        int t = 1;
        T res = 0;
        for (int h = B - 1; h >= 0 && t; h--) {
            if (b >> h & 1) res ^= xr[ch[t][0]], t = ch[t][1];
            else t = ch[t][0];
        }
        return res;
    }

    LEETCODE_NO_SANITIZE T xle(T x) const { return xlt(T((long long)x + 1)); }

    LEETCODE_NO_SANITIZE T xorFirst(long long k) const {  // xor of the k smallest values (copies count)
        if (k <= 0) return 0;
        int t = 1;
        long long y = 0;  // the stored value of the leaf reached
        T res = 0;
        for (int h = B - 1; h >= 0; h--) {
            int l = ch[t][0];
            if (k <= c[l]) t = l;
            else k -= c[l], res ^= xr[l], t = ch[t][1], y |= 1LL << h;
        }
        if (k & 1) res ^= T(y);  // k copies of the leaf's value left
        return res;
    }

    LEETCODE_NO_SANITIZE T andIn(T ql, T qr) const {  // AND of the values in [ql, qr]
        long long lo = std::max<long long>(ql, 0), hi = std::min<long long>(qr, top);
        if (lo > hi) return ~T(0);
        int t = 1, h = B - 1;
        // the bits lo and hi share: one path
        for (; h >= 0 && (lo >> h & 1) == (hi >> h & 1); h--) t = ch[t][lo >> h & 1];
        if (h < 0 || !t) return andv[t];
        T res = ~T(0);
        int u = ch[t][0];  // where they split, the left child only needs v >= lo
        for (int g = h - 1; g >= 0 && u; g--) {
            if (lo >> g & 1) u = ch[u][1];
            else res &= andv[ch[u][1]], u = ch[u][0];
        }
        res &= andv[u];
        u = ch[t][1];  // and the right child only v <= hi
        for (int g = h - 1; g >= 0 && u; g--) {
            if (hi >> g & 1) res &= andv[ch[u][0]], u = ch[u][1];
            else u = ch[u][0];
        }
        return res & andv[u];
    }

    LEETCODE_NO_SANITIZE T andLe(T x) const { return andIn(T(0), x); }  // AND of the values <= x
    LEETCODE_NO_SANITIZE T andGe(T x) const { return andIn(x, T(top)); }  // AND of the values >= x

    // O(logU) -- add one copy of x
    LEETCODE_NO_SANITIZE void add(T x) {
        addRaw(x, 1);
    }

    // O(logU) -- add cnt copies of val (nothing if cnt <= 0)
    LEETCODE_NO_SANITIZE void addCount(T val, long long cnt) {
        if (cnt > 0) addRaw(val, cnt);
    }

    // O(1) -- bitwise AND of all values; -1 (every bit set) if empty
    LEETCODE_NO_SANITIZE T andOfAll() {
        return andv[1];
    }

    // O(logU) -- bitwise AND of the values > x; -1 (every bit set) if there are none
    LEETCODE_NO_SANITIZE T andOfGtX(T x) {
        if (x == numeric_limits<T>::max()) return ~T(0);
        return andGe(x + 1);
    }

    // O(logU) -- bitwise AND of the values >= x; -1 (every bit set) if there are none
    LEETCODE_NO_SANITIZE T andOfGteX(T x) {
        return andGe(x);
    }

    // O(logU) -- bitwise AND of the values v with lo <= v <= hi; -1 (every bit set) if there are none
    LEETCODE_NO_SANITIZE T andOfInValRange(T lo, T hi) {
        return lo <= hi ? andIn(lo, hi) : ~T(0);
    }

    // O(logU) -- bitwise AND of the kFrom-th through kTo-th largest values; RANKS, 1-indexed and inclusive: (1, 1) is
    // just the largest, (5, 8) the 5th, 6th, 7th and 8th largest, (1, size) every value (copies count); throws
    // out_of_range unless 1 <= kFrom <= kTo <= size
    LEETCODE_NO_SANITIZE T andOfKthLargestRange(long long kFrom, long long kTo) {
        if (kFrom < 1 || kFrom > kTo
            || kTo > n) throw out_of_range("andOfKthLargestRange: needs 1 <= kFrom <= kTo <= size");
        T a = kthAt(n - kTo + 1);
        return andIn(a, kthAt(n - kFrom + 1));
    }

    // O(logU) -- bitwise AND of the kFrom-th through kTo-th smallest values; RANKS, 1-indexed and inclusive: (1, 1) is
    // just the smallest, (2, 4) the 2nd, 3rd and 4th smallest, (1, size) every value (copies count); throws
    // out_of_range unless 1 <= kFrom <= kTo <= size
    LEETCODE_NO_SANITIZE T andOfKthSmallestRange(long long kFrom, long long kTo) {
        if (kFrom < 1 || kFrom > kTo
            || kTo > n) throw out_of_range("andOfKthSmallestRange: needs 1 <= kFrom <= kTo <= size");
        T a = kthAt(kFrom);
        return andIn(a, kthAt(kTo));
    }

    // O(logU) -- bitwise AND of the k largest values; k is a COUNT, not an index: k = 0 takes no values (returns -1,
    // every bit set), k = 1 just the largest, k = size every value (copies count: in {2, 5, 5}, k = 2 takes 5 and 5);
    // throws out_of_range unless 0 <= k <= size
    LEETCODE_NO_SANITIZE T andOfLargestK(long long k) {
        if (k < 0 || k > n) throw out_of_range("andOfLargestK: needs 0 <= k <= size");
        return k ? andGe(kthAt(n - k + 1)) : ~T(0);
    }

    // O(logU) -- bitwise AND of the values < x; -1 (every bit set) if there are none
    LEETCODE_NO_SANITIZE T andOfLtX(T x) {
        if (x == numeric_limits<T>::min()) return ~T(0);
        return andLe(x - 1);
    }

    // O(logU) -- bitwise AND of the values <= x; -1 (every bit set) if there are none
    LEETCODE_NO_SANITIZE T andOfLteX(T x) {
        return andLe(x);
    }

    // O(logU) -- bitwise AND of the k smallest values; k is a COUNT, not an index: k = 0 takes no values (returns -1,
    // every bit set), k = 1 just the smallest, k = size every value (copies count: in {2, 2, 5}, k = 2 takes 2 and 2);
    // throws out_of_range unless 0 <= k <= size
    LEETCODE_NO_SANITIZE T andOfSmallestK(long long k) {
        if (k < 0 || k > n) throw out_of_range("andOfSmallestK: needs 0 <= k <= size");
        return k ? andLe(kthAt(k)) : ~T(0);
    }

    // O(1 amortized) -- remove everything: afterwards it is as if newly built (same constructor arguments), so reuse it
    // instead of building a new one
    LEETCODE_NO_SANITIZE void clear() {
        clearData();
        resetCached();
    }

    // O(logU) -- how many copies of x
    LEETCODE_NO_SANITIZE long long count(T x) {
        return countOf(x);
    }

    // O(1) -- how many distinct values
    LEETCODE_NO_SANITIZE long long countDistinct() {
        return d;
    }

    // O(logU) -- how many distinct values v with lo <= v <= hi (0 if lo > hi)
    LEETCODE_NO_SANITIZE long long countDistinctInValRange(T lo, T hi) {
        if (hi < lo) return 0;
        return distinctLt(hi) - distinctLt(lo) + (countOf(hi) ? 1 : 0);
    }

    // O(logU) -- how many values > x
    LEETCODE_NO_SANITIZE long long countGtX(T x) {
        return n - le(x);
    }

    // O(logU) -- how many values >= x
    LEETCODE_NO_SANITIZE long long countGteX(T x) {
        return n - lt(x);
    }

    // O(logU) -- how many values v with lo <= v <= hi (0 if lo > hi)
    LEETCODE_NO_SANITIZE long long countInValRange(T lo, T hi) {
        return lo <= hi ? le(hi) - lt(lo) : 0;
    }

    // O(logU) -- how many values < x
    LEETCODE_NO_SANITIZE long long countLtX(T x) {
        return lt(x);
    }

    // O(logU) -- how many values <= x
    LEETCODE_NO_SANITIZE long long countLteX(T x) {
        return le(x);
    }

    // O(logU) -- how many values v have v ^ x > k (k is a VALUE to compare against, not a rank or count; copies count)
    LEETCODE_NO_SANITIZE long long countXorGtK(T x, long long k) {
        return n - cntLt(k + 1, (long long)x);
    }

    // O(logU) -- how many values v have v ^ x >= k (k is a VALUE to compare against, not a rank or count; copies count)
    LEETCODE_NO_SANITIZE long long countXorGteK(T x, long long k) {
        return n - cntLt(k, (long long)x);
    }

    // O(logU) -- how many values v have v ^ x < k (k is a VALUE to compare against, not a rank or count; copies count)
    LEETCODE_NO_SANITIZE long long countXorLtK(T x, long long k) {
        return cntLt(k, (long long)x);
    }

    // O(logU) -- how many values v have v ^ x <= k (k is a VALUE to compare against, not a rank or count; copies count)
    LEETCODE_NO_SANITIZE long long countXorLteK(T x, long long k) {
        return cntLt(k + 1, (long long)x);
    }

    // O(logU) -- 0-indexed position of the first copy of x in sorted order (= how many values < x); -1 if x is not in
    // the set
    LEETCODE_NO_SANITIZE long long firstIndex(T x) {
        return countOf(x) ? lt(x) : -1;
    }

    // O(logU) -- the value at sorted position i, 0-indexed: kth(0) is the smallest, kth(1) the 2nd smallest,
    // kth(size - 1) the largest (copies count: in {2, 2, 5}, kth(1) is 2); throws out_of_range unless 0 <= i < size
    LEETCODE_NO_SANITIZE T kth(long long i) {
        if (i < 0 || i >= n) throw out_of_range("kth: needs 0 <= i < size");
        return kthAt(i + 1);
    }

    // O(logU) -- the i-th smallest of v ^ x over the values v, 0-indexed: kthXor(x, 0) is the smallest v ^ x,
    // kthXor(x, 1) the 2nd smallest (copies count); throws out_of_range unless 0 <= i < size
    LEETCODE_NO_SANITIZE T kthXor(T x, long long i) {
        if (i < 0 || i >= n) throw out_of_range("kthXor: needs 0 <= i < size");
        return T(kthX(i + 1, (long long)x));
    }

    // O(logU) -- largest value < x; ms.NONE if there is none
    LEETCODE_NO_SANITIZE T largestLtX(T x) {
        long long c = lt(x);
        if (!c) return NONE;
        return kthAt(c);
    }

    // O(logU) -- largest value <= x; ms.NONE if there is none
    LEETCODE_NO_SANITIZE T largestLteX(T x) {
        long long c = le(x);
        if (!c) return NONE;
        return kthAt(c);
    }

    // O(logU) -- largest v ^ x that is < k (k is a VALUE to compare against, not a rank); -1 if there is none
    LEETCODE_NO_SANITIZE T largestXorLtK(T x, long long k) {
        long long key = (long long)x, c0 = cntLt(k, key);
        if (!c0) return -1;
        return T(kthX(c0, key));
    }

    // O(logU) -- largest v ^ x that is <= k (k is a VALUE to compare against, not a rank); -1 if there is none
    LEETCODE_NO_SANITIZE T largestXorLteK(T x, long long k) {
        long long key = (long long)x, c0 = cntLt(k + 1, key);
        if (!c0) return -1;
        return T(kthX(c0, key));
    }

    // O(logU) -- 0-indexed position of the last copy of x in sorted order (= how many values <= x, minus 1); -1 if x is
    // not in the set
    LEETCODE_NO_SANITIZE long long lastIndex(T x) {
        return countOf(x) ? le(x) - 1 : -1;
    }

    // O(1) -- largest value; throws out_of_range if empty
    LEETCODE_NO_SANITIZE T max() {
        if (!n) throw out_of_range("max: the set is empty");
        return T(mxv[1]);
    }

    // O(logU) -- largest v ^ x over the values v in the set; throws out_of_range if the set is empty
    // (needs 0 <= x < 2^bits)
    LEETCODE_NO_SANITIZE T maxXorAgainstX(T x) {
        if (!n) throw out_of_range("maxXorAgainstX: the set is empty");
        return T(extreme(1, B - 1, (long long)x, true));
    }

    // O(logU) -- largest v ^ x over the values v > m; -1 if there is none
    LEETCODE_NO_SANITIZE T maxXorWithVGtM(T x, long long m) {
        return bestIn(x, m + 1, top, true).value_or(T(-1));
    }

    // O(logU) -- largest v ^ x over the values v >= m; -1 if there is none
    LEETCODE_NO_SANITIZE T maxXorWithVGteM(T x, long long m) {
        return bestIn(x, m, top, true).value_or(T(-1));
    }

    // O(logU) -- largest v ^ x over the values v with lo <= v <= hi; -1 if there is none
    LEETCODE_NO_SANITIZE T maxXorWithVInValRange(T x, long long lo, long long hi) {
        return bestIn(x, lo, hi, true).value_or(T(-1));
    }

    // O(logU) -- largest v ^ x over the values v < m; -1 if there is none
    LEETCODE_NO_SANITIZE T maxXorWithVLtM(T x, long long m) {
        return bestIn(x, 0, m - 1, true).value_or(T(-1));
    }

    // O(logU) -- largest v ^ x over the values v <= m; -1 if there is none
    LEETCODE_NO_SANITIZE T maxXorWithVLteM(T x, long long m) {
        return bestIn(x, 0, m, true).value_or(T(-1));
    }

    // O(1) -- upper median: the (floor(size/2) + 1)-th smallest value; throws out_of_range if empty
    LEETCODE_NO_SANITIZE T medianHigh() {
        if (!n) throw out_of_range("medianHigh: the set is empty");
        return high.v;
    }

    // O(1) -- lower median: the ceil(size/2)-th smallest value; throws out_of_range if empty
    LEETCODE_NO_SANITIZE T medianLow() {
        if (!n) throw out_of_range("medianLow: the set is empty");
        return low.v;
    }

    // O(1) -- smallest non-negative integer not in the set
    LEETCODE_NO_SANITIZE long long mex() {
        return mexV;
    }

    // O(logU) -- smallest non-negative integer that is not v ^ x for any value v
    LEETCODE_NO_SANITIZE long long mexXor(T x) {
        return mexX((long long)x);
    }

    // O(1) -- smallest value; throws out_of_range if empty
    LEETCODE_NO_SANITIZE T min() {
        if (!n) throw out_of_range("min: the set is empty");
        return T(mnv[1]);
    }

    // O(logU) -- smallest v ^ x over the values v in the set; throws out_of_range if the set is empty
    // (needs 0 <= x < 2^bits)
    LEETCODE_NO_SANITIZE T minXorAgainstX(T x) {
        if (!n) throw out_of_range("minXorAgainstX: the set is empty");
        return T(extreme(1, B - 1, (long long)x, false));
    }

    // O(logU) -- smallest v ^ x over the values v > m; -1 if there is none
    LEETCODE_NO_SANITIZE T minXorWithVGtM(T x, long long m) {
        return bestIn(x, m + 1, top, false).value_or(T(-1));
    }

    // O(logU) -- smallest v ^ x over the values v >= m; -1 if there is none
    LEETCODE_NO_SANITIZE T minXorWithVGteM(T x, long long m) {
        return bestIn(x, m, top, false).value_or(T(-1));
    }

    // O(logU) -- smallest v ^ x over the values v with lo <= v <= hi; -1 if there is none
    LEETCODE_NO_SANITIZE T minXorWithVInValRange(T x, long long lo, long long hi) {
        return bestIn(x, lo, hi, false).value_or(T(-1));
    }

    // O(logU) -- smallest v ^ x over the values v < m; -1 if there is none
    LEETCODE_NO_SANITIZE T minXorWithVLtM(T x, long long m) {
        return bestIn(x, 0, m - 1, false).value_or(T(-1));
    }

    // O(logU) -- smallest v ^ x over the values v <= m; -1 if there is none
    LEETCODE_NO_SANITIZE T minXorWithVLteM(T x, long long m) {
        return bestIn(x, 0, m, false).value_or(T(-1));
    }

    // O(logU) -- remove and return the value at sorted position i, 0-indexed: pop(0) removes the smallest (= popMin()),
    // pop(size - 1) the largest (copies count); throws out_of_range unless 0 <= i < size
    LEETCODE_NO_SANITIZE T pop(long long i) {
        if (i < 0 || i >= n) throw out_of_range("pop: needs 0 <= i < size");
        T v = kthAt(i + 1);
        addRaw(v, -1);
        return v;
    }

    // O(logU) -- remove and return the largest value; throws out_of_range if empty
    LEETCODE_NO_SANITIZE T popMax() {
        if (!n) throw out_of_range("popMax: the set is empty");
        T v = T(mxv[1]);
        addRaw(v, -1);
        return v;
    }

    // O(logU) -- remove and return the smallest value; throws out_of_range if empty
    LEETCODE_NO_SANITIZE T popMin() {
        if (!n) throw out_of_range("popMin: the set is empty");
        T v = T(mnv[1]);
        addRaw(v, -1);
        return v;
    }

    // O(logU) -- remove one copy of x if present; returns how many were removed (0 or 1)
    LEETCODE_NO_SANITIZE long long remove(T x) {
        if (!count(x)) return 0;
        addRaw(x, -1);
        return 1;
    }

    // O(logU) -- remove every copy of val; returns how many were removed
    LEETCODE_NO_SANITIZE long long removeAll(T val) {
        long long k = count(val);
        if (k) addRaw(val, -k);
        return k;
    }

    // O(logU) -- remove min(cnt, count(val)) copies of val; returns how many were removed
    LEETCODE_NO_SANITIZE long long removeCount(T val, long long cnt) {
        long long k = std::min(cnt, count(val));
        if (k <= 0) return 0;
        addRaw(val, -k);
        return k;
    }

    // O(logU amortized) -- remove every value v with lo <= v <= hi; returns how many copies were removed (0 if lo > hi)
    LEETCODE_NO_SANITIZE long long removeInValRange(T lo, T hi) {
        if (hi < lo) return 0;
        long long removed = 0;
        while (n) {  // the smallest value >= lo, while it is <= hi: drop all its copies
            long long c = lt(lo);
            if (c == n) break;
            T v = kthAt(c + 1);
            if (hi < v) break;
            long long k = countOf(v);
            addRaw(v, -k), removed += k;
        }
        return removed;
    }

    // O(1) -- how many values (copies count)
    LEETCODE_NO_SANITIZE long long size() {
        return n;
    }

    // O(logU) -- smallest value > x; ms.NONE if there is none
    LEETCODE_NO_SANITIZE T smallestGtX(T x) {
        long long c = le(x);
        if (c == n) return NONE;
        return kthAt(c + 1);
    }

    // O(logU) -- smallest value >= x; ms.NONE if there is none
    LEETCODE_NO_SANITIZE T smallestGteX(T x) {
        long long c = lt(x);
        if (c == n) return NONE;
        return kthAt(c + 1);
    }

    // O(logU) -- smallest v ^ x that is > k (k is a VALUE to compare against, not a rank); -1 if there is none
    LEETCODE_NO_SANITIZE T smallestXorGtK(T x, long long k) {
        long long key = (long long)x, c0 = cntLt(k + 1, key);
        if (c0 == n) return -1;
        return T(kthX(c0 + 1, key));
    }

    // O(logU) -- smallest v ^ x that is >= k (k is a VALUE to compare against, not a rank); -1 if there is none
    LEETCODE_NO_SANITIZE T smallestXorGteK(T x, long long k) {
        long long key = (long long)x, c0 = cntLt(k, key);
        if (c0 == n) return -1;
        return T(kthX(c0 + 1, key));
    }

    // O(1) -- xor of all values (copies count: a value with an even count cancels out); 0 if empty
    LEETCODE_NO_SANITIZE T xorOfAll() {
        return xtotal;
    }

    // O(logU) -- xor of the values > x (copies count)
    LEETCODE_NO_SANITIZE T xorOfGtX(T x) {
        return xtotal ^ xle(x);
    }

    // O(logU) -- xor of the values >= x (copies count)
    LEETCODE_NO_SANITIZE T xorOfGteX(T x) {
        return xtotal ^ xlt(x);
    }

    // O(logU) -- xor of the values v with lo <= v <= hi (copies count; 0 if lo > hi)
    LEETCODE_NO_SANITIZE T xorOfInValRange(T lo, T hi) {
        return lo <= hi ? T(xle(hi) ^ xlt(lo)) : T(0);
    }

    // O(logU) -- xor of the kFrom-th through kTo-th largest values; RANKS, 1-indexed and inclusive: (1, 1) is just the
    // largest, (5, 8) the 5th, 6th, 7th and 8th largest, (1, size) every value (copies count); throws out_of_range
    // unless 1 <= kFrom <= kTo <= size
    LEETCODE_NO_SANITIZE T xorOfKthLargestRange(long long kFrom, long long kTo) {
        if (kFrom < 1 || kFrom > kTo
            || kTo > n) throw out_of_range("xorOfKthLargestRange: needs 1 <= kFrom <= kTo <= size");
        return xorFirst(n - kFrom + 1) ^ xorFirst(n - kTo);
    }

    // O(logU) -- xor of the kFrom-th through kTo-th smallest values; RANKS, 1-indexed and inclusive: (1, 1) is just the
    // smallest, (2, 4) the 2nd, 3rd and 4th smallest, (1, size) every value (copies count); throws out_of_range unless
    // 1 <= kFrom <= kTo <= size
    LEETCODE_NO_SANITIZE T xorOfKthSmallestRange(long long kFrom, long long kTo) {
        if (kFrom < 1 || kFrom > kTo
            || kTo > n) throw out_of_range("xorOfKthSmallestRange: needs 1 <= kFrom <= kTo <= size");
        return xorFirst(kTo) ^ xorFirst(kFrom - 1);
    }

    // O(logU) -- xor of the k largest values; k is a COUNT, not an index: k = 0 takes no values (returns 0), k = 1 just
    // the largest, k = size every value (copies count: in {2, 5, 5}, k = 2 takes 5 and 5); throws out_of_range unless 0
    // <= k <= size
    LEETCODE_NO_SANITIZE T xorOfLargestK(long long k) {
        if (k < 0 || k > n) throw out_of_range("xorOfLargestK: needs 0 <= k <= size");
        return xtotal ^ xorFirst(n - k);
    }

    // O(logU) -- xor of the values < x (copies count)
    LEETCODE_NO_SANITIZE T xorOfLtX(T x) {
        return xlt(x);
    }

    // O(logU) -- xor of the values <= x (copies count)
    LEETCODE_NO_SANITIZE T xorOfLteX(T x) {
        return xle(x);
    }

    // O(logU) -- xor of the k smallest values; k is a COUNT, not an index: k = 0 takes no values (returns 0), k = 1
    // just the smallest, k = size every value (copies count: in {2, 2, 5}, k = 2 takes 2 and 2); throws out_of_range
    // unless 0 <= k <= size
    LEETCODE_NO_SANITIZE T xorOfSmallestK(long long k) {
        if (k < 0 || k > n) throw out_of_range("xorOfSmallestK: needs 0 <= k <= size");
        return xorFirst(k);
    }
};
