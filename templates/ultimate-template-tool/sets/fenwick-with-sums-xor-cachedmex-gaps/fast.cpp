// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/sets/fenwick-with-sums-xor-cachedmex-gaps/fast.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: add addCount clear count countDistinct countDistinctInValRange countGtX countGteX countInValRange countLtX countLteX firstIndex kth largestLtX largestLteX lastIndex max maxGap medianHigh medianLow mex min minAdjacentDiff pop popMax popMin remove removeAll removeCount removeInValRange size smallestGtX smallestGteX sumAbsDiffToMedian sumAbsDiffToX sumAll sumGtX sumGteX sumInValRange sumKthLargestRange sumKthSmallestRange sumLargestK sumLtX sumLteX sumSmallestK xorOfAll xorOfGtX xorOfGteX xorOfInValRange xorOfKthLargestRange xorOfKthSmallestRange xorOfLargestK xorOfLtX xorOfLteX xorOfSmallestK
// @data-structure-type: fenwick
// @values: offline
// @keys: numbers
// @tracks: mex gaps
// @complexities:
//   add: log(N)
//   addCount: log(N)
//   clear: 1 amortized
//   count: log(N)
//   countDistinct: 1
//   countDistinctInValRange: log(N)
//   countGtX: log(N)
//   countGteX: log(N)
//   countInValRange: log(N)
//   countLtX: log(N)
//   countLteX: log(N)
//   firstIndex: log(N)
//   kth: log(N)
//   largestLtX: log(N)
//   largestLteX: log(N)
//   lastIndex: log(N)
//   max: log(N)
//   maxGap: 1 amortized
//   medianHigh: log(N)
//   medianLow: log(N)
//   mex: 1
//   min: log(N)
//   minAdjacentDiff: 1 amortized
//   pop: log(N)
//   popMax: log(N)
//   popMin: log(N)
//   remove: log(N)
//   removeAll: log(N)
//   removeCount: log(N)
//   removeInValRange: log(N) amortized
//   size: 1
//   smallestGtX: log(N)
//   smallestGteX: log(N)
//   sumAbsDiffToMedian: log(N)
//   sumAbsDiffToX: log(N)
//   sumAll: 1
//   sumGtX: log(N)
//   sumGteX: log(N)
//   sumInValRange: log(N)
//   sumKthLargestRange: log(N)
//   sumKthSmallestRange: log(N)
//   sumLargestK: log(N)
//   sumLtX: log(N)
//   sumLteX: log(N)
//   sumSmallestK: log(N)
//   xorOfAll: 1
//   xorOfGtX: log(N)
//   xorOfGteX: log(N)
//   xorOfInValRange: log(N)
//   xorOfKthLargestRange: log(N)
//   xorOfKthSmallestRange: log(N)
//   xorOfLargestK: log(N)
//   xorOfLtX: log(N)
//   xorOfLteX: log(N)
//   xorOfSmallestK: log(N)
//   build: N*log(N)
// @memory:
//   layout: none
//   node: cnt[1*N] tree[1*N] fp[1*N] fs[1*N] fx[1*N]
//   tags: none
//   other: vals[1*N]
//   note: N = how many distinct values were given to the constructor; the arrays are allocated once. C++ integers also keep a hash table of at most 4*N ints from value to position; gaps keeps one of 8*N

// Ordered multiset over values known ahead of time (offline): Fenwick trees over the sorted distinct values you pass
// to the constructor, one counting copies, one summing them, one marking which values are present (for mex), one xor-ing the values with an odd count.
// k-th / sum of the k smallest walk down by binary lifting. The constructor only learns which values can appear (it
// compresses them); the multiset starts EMPTY. Every value you add must be one of them; query arguments (x, lo, hi)
// can be anything. T: int, long long, ...; sums in S (long long for small T).
// FAST MODE drawbacks compared with template.cpp:
//   - at most 2147483647 copies in total: going past that throws length_error
//   - sanitizers are skipped inside this template, so a bad access in it goes unreported
//   - adding a value not given to the constructor can corrupt memory unreported
// Same public operations and answers; it needs GCC or Clang and C++17, and uses SSE2 where the CPU has it.
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

// A minimal array: unlike vector, its accessors always inline, even with sanitizers skipped
template <typename U>
struct FlatArray {
    U* items = nullptr;
    int count = 0;
    FlatArray() = default;
    FlatArray(const FlatArray& other) { *this = other; }
    FlatArray& operator=(const FlatArray& other) {
        if (this == &other) return *this;
        delete[] items;
        count = other.count;
        items = count ? new U[count] : nullptr;
        std::copy(other.items, other.items + count, items);
        return *this;
    }
    ~FlatArray() { delete[] items; }
    void assign(int size, U value) {
        delete[] items;
        count = size;
        items = size ? new U[size] : nullptr;
        std::fill(items, items + size, value);
    }
    LEETCODE_NO_SANITIZE_INLINE U& operator[](int i) { return items[i]; }
    LEETCODE_NO_SANITIZE_INLINE const U& operator[](int i) const { return items[i]; }
    LEETCODE_NO_SANITIZE_INLINE U* data() { return items; }
    LEETCODE_NO_SANITIZE_INLINE const U* data() const { return items; }
    U* begin() { return items; }
    U* end() { return items + count; }
    const U* begin() const { return items; }
    const U* end() const { return items + count; }
};

template <typename T>
struct FenwickMultiset {
    template <class K>
    static K noneOf() {  // the lowest value of K, part by part for pairs and tuples
        if constexpr (is_arithmetic_v<K>) return numeric_limits<K>::lowest();
        else return apply([](auto... parts) { return K{noneOf<decltype(parts)>()...}; }, K{});
    }
    static inline const T NONE = noneOf<T>();  // what largestLtX, smallestGtX, ... return when nothing qualifies: compare with ms.NONE

    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    FlatArray<T> vals;  // the sorted distinct values
    int m, top, z, run;
    FlatArray<int> cnt;  // copies per value (fits: total copies are capped)
    FlatArray<long long> fp;  // Fenwick of present values
    FlatArray<int> tree;  // the 16-way count tree: 16 running totals per node, leaf level first
    int levels = 0, levelStart[8] = {};  // how many levels; where each level begins in tree
    FlatArray<S> fs;  // Fenwick of copies * value
    FlatArray<T> fx;  // Fenwick of xor over the values with an odd count
    FlatArray<int> slotOf;  // integer values only: hash table from a value to its position in vals, -1 for an empty slot
    unsigned long long hashMultiplier = 1;  // random per instance, so no fixed input can force collisions
    int hashShift = 0;
    unsigned hashMask = 0;
    int segSize = 1;  // positions in the segment trees below (a power of two >= m)
    long long n = 0, d = 0;
    struct Info { T v; long long before, c; S sb; };  // a value, copies before it, its copies, sum before it
    long long mexV = 0;  // the mex, kept current (0 for the empty set)
    FlatArray<int> gapFirst, gapLast;  // segment tree over positions: the first and last present value in each range, -1 if none
    FlatArray<long long> gapMin, gapMax;  // ... and the smallest and largest gap between neighbours inside it
    long long dups = 0;  // values with 2+ copies
    T xtotal = 0;  // xor of all values (copies count)
    S total = 0;

    // O(N log N) -- allValuesThatWillEverBeInsertedForOfflineCompression: every value you will EVER add (any order, duplicates fine), only to compress values; this does NOT add them, the multiset starts empty; N = distinct values
    explicit FenwickMultiset(vector<T> allValuesThatWillEverBeInsertedForOfflineCompression) {
        vector<T>& sortedValues = allValuesThatWillEverBeInsertedForOfflineCompression;
        sort(sortedValues.begin(), sortedValues.end());
        sortedValues.erase(unique(sortedValues.begin(), sortedValues.end()), sortedValues.end());
        m = (int)sortedValues.size();
        vals.assign(m, T());
        std::copy(sortedValues.begin(), sortedValues.end(), vals.begin());
        top = m ? 1 << (31 - __builtin_clz(m)) : 0;  // highest power of two <= m, for binary lifting
        cnt.assign(m, 0);
        int nodes = m, slots = 0;
        do {
            nodes = (nodes + 15) / 16;
            levelStart[levels++] = slots;
            slots += nodes * 16;
        } while (nodes > 1);
        tree.assign(slots, 0);
        while (segSize < m) segSize <<= 1;
        gapFirst.assign(2 * segSize, -1), gapLast.assign(2 * segSize, -1);
        gapMin.assign(2 * segSize, LLONG_MAX), gapMax.assign(2 * segSize, -1);
        fp.assign(m + 1, 0);
        fs.assign(m + 1, 0);
        fx.assign(m + 1, 0);
        z = int(lower_bound(vals.begin(), vals.end(), T(0)) - vals.begin());
        run = 0;
        while (z + run < m && vals[z + run] == T(run)) run++;  // vals[z .. z + run - 1] = 0, 1, ..., run - 1
        if constexpr (is_integral_v<T>) {
            unsigned long long seed = chrono::steady_clock::now().time_since_epoch().count() ^ (unsigned long long)(uintptr_t)this;
            seed = (seed ^ (seed >> 30)) * 0xBF58476D1CE4E5B9ULL;
            seed = (seed ^ (seed >> 27)) * 0x94D049BB133111EBULL;
            hashMultiplier = (seed ^ (seed >> 31)) | 1;
            int bits = 3;
            while ((1LL << bits) < 2LL * m) bits++;
            hashShift = 64 - bits, hashMask = (1u << bits) - 1;
            slotOf.assign(1u << bits, -1);
            for (int i = 0; i < m; i++) {
                unsigned h = hashOf(vals[i]);
                while (slotOf[h] >= 0) h = (h + 1) & hashMask;
                slotOf[h] = i;
            }
        }
    }

    template <class V>
    LEETCODE_NO_SANITIZE void fen(FlatArray<V>& f, int i, V v) {
        for (i++; i <= m; i += i & -i) f[i] += v;
    }

    template <class V>
    LEETCODE_NO_SANITIZE V pre(const FlatArray<V>& f, int i) const {  // f's total over positions 0..i-1
        V s = 0;
        for (; i > 0; i &= i - 1) s += f[i];
        return s;
    }

    LEETCODE_NO_SANITIZE_INLINE static int countBelow(const int* node, int k) {  // how many of the node's 16 running totals are < k
#ifdef __SSE2__
        __m128i key = _mm_set1_epi32(k);
        __m128i part0 = _mm_cmplt_epi32(_mm_loadu_si128((const __m128i*)node), key);
        __m128i part1 = _mm_cmplt_epi32(_mm_loadu_si128((const __m128i*)(node + 4)), key);
        __m128i part2 = _mm_cmplt_epi32(_mm_loadu_si128((const __m128i*)(node + 8)), key);
        __m128i part3 = _mm_cmplt_epi32(_mm_loadu_si128((const __m128i*)(node + 12)), key);
        int below = _mm_movemask_epi8(_mm_packs_epi16(_mm_packs_epi32(part0, part1), _mm_packs_epi32(part2, part3)));
        return __builtin_ctz(~below);  // the totals never decrease, so the bits are one solid run from the bottom
#else
        int c = 0;
        for (int j = 0; j < 16; j++) c += node[j] < k;
        return c;
#endif
    }

    LEETCODE_NO_SANITIZE_INLINE static void addFrom(int* node, int child, int delta) {  // add delta to running totals child..15
#ifdef __SSE2__
        alignas(16) static const int mask[31] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1};
        const int* childMask = mask + 15 - child;
        __m128i value = _mm_set1_epi32(delta);
        for (int j = 0; j < 16; j += 4) {
            __m128i* at = (__m128i*)(node + j);
            __m128i masked = _mm_and_si128(value, _mm_loadu_si128((const __m128i*)(childMask + j)));
            _mm_storeu_si128(at, _mm_add_epi32(_mm_loadu_si128(at), masked));
        }
#else
        for (int j = 0; j < 16; j++) node[j] += delta & -(j >= child);
#endif
    }

    LEETCODE_NO_SANITIZE long long countBefore(int i) const {  // copies over positions 0..i-1
        if (i >= m) return n;
        const int* t = tree.data();
        long long s = 0;
        for (int level = 0; level < levels; level++) {
            int c = i & 15;
            i >>= 4;
            if (c) s += t[levelStart[level] + i * 16 + c - 1];
        }
        return s;
    }

    LEETCODE_NO_SANITIZE int findSlot(long long k, long long& before) const {  // position of the k-th smallest; copies before it
        const int* t = tree.data();
        int pos = 0, want = int(k);
        for (int level = levels - 1; level >= 0; level--) {
            const int* node = t + levelStart[level] + pos * 16;
            int c = countBelow(node, want);
            int skipped = c ? node[c - 1] : 0;
            want -= skipped;
            pos = pos * 16 + c;
        }
        before = k - want;
        return pos;
    }

    [[noreturn]] __attribute__((noinline, cold)) static void tooManyCopies() {
        throw length_error("fast FenwickMultiset: at most 2147483647 copies");
    }

    int lowerIdx(T x) const { return int(lower_bound(vals.begin(), vals.end(), x) - vals.begin()); }
    int upperIdx(T x) const { return int(upper_bound(vals.begin(), vals.end(), x) - vals.begin()); }

    LEETCODE_NO_SANITIZE_INLINE unsigned hashOf(T x) const {
        return unsigned((unsigned long long)(long long)x * hashMultiplier >> hashShift);
    }
    LEETCODE_NO_SANITIZE int rankOf(T x) const {  // x's position in vals, or m if it is not a given value; expected O(1) for integers
        if constexpr (is_integral_v<T>) {
            const int* table = slotOf.data();
            const T* sorted = vals.data();
            for (unsigned h = hashOf(x);; h = (h + 1) & hashMask) {
                int i = table[h];
                if (i < 0) return m;
                if (sorted[i] == x) return i;
            }
        } else {
            int i = lowerIdx(x);
            return i < m && vals[i] == x ? i : m;
        }
    }

    LEETCODE_NO_SANITIZE void gapSet(int i, bool present) {  // position i's value appeared or disappeared
        int j = i + segSize;
        gapFirst[j] = gapLast[j] = present ? i : -1;
        for (j >>= 1; j; j >>= 1) {
            int a = 2 * j, b = a + 1;
            if (gapLast[a] < 0 || gapFirst[b] < 0) {
                int side = gapLast[a] < 0 ? b : a;
                gapFirst[j] = gapFirst[side], gapLast[j] = gapLast[side], gapMin[j] = gapMin[side], gapMax[j] = gapMax[side];
            } else {
                long long middle = (long long)vals[gapFirst[b]] - (long long)vals[gapLast[a]];
                gapFirst[j] = gapFirst[a], gapLast[j] = gapLast[b];
                gapMin[j] = gapMin[a] < gapMin[b] ? gapMin[a] : gapMin[b];
                if (middle < gapMin[j]) gapMin[j] = middle;
                gapMax[j] = gapMax[a] > gapMax[b] ? gapMax[a] : gapMax[b];
                if (middle > gapMax[j]) gapMax[j] = middle;
            }
        }
    }

    LEETCODE_NO_SANITIZE long long insert(T x, long long c) {  // returns x's new count
        int i = rankOf(x);
        if (i == m) i = lowerIdx(x);  // x must be one of the given values
        return insertAt(i, x, c);
    }

    LEETCODE_NO_SANITIZE long long insertAt(int i, T x, long long c) {  // i is x's position in vals; returns x's new count
        int* counts = cnt.data();
        long long old = counts[i];
        long long now = counts[i] += int(c);
        int* t = tree.data();
        for (int level = 0, idx = i; level < levels; level++) {
            int child = idx & 15;
            idx >>= 4;
            addFrom(t + levelStart[level] + idx * 16, child, int(c));
        }
        S* f = fs.data();
        S sumDelta = S(c) * x;
        for (int j = i + 1; j <= m; j += j & -j) f[j] += sumDelta;
        if (c & 1)
            for (int j = i + 1; j <= m; j += j & -j) fx[j] ^= x;  // x's parity flips
        if (!old) fen(fp, i, 1LL), d++;
        else if (!now) fen(fp, i, -1LL), d--;
        if (!old || !now) gapSet(i, now > 0);
        return now;
    }

    long long lt(T x) { return countBefore(lowerIdx(x)); }
    long long le(T x) { return countBefore(upperIdx(x)); }

    LEETCODE_NO_SANITIZE long long countOf(T x) const {
        int i = rankOf(x);
        const int* counts = cnt.data();
        return i < m ? counts[i] : 0;
    }
    S slt(T x) { return pre(fs, lowerIdx(x)); }
    S sle(T x) { return pre(fs, upperIdx(x)); }

    LEETCODE_NO_SANITIZE T kthAt(long long k) {  // the k-th smallest
        long long before;
        const T* sorted = vals.data();
        return sorted[findSlot(k, before)];
    }
    LEETCODE_NO_SANITIZE Info kthInfo(long long k) {  // the k-th smallest, copies before it, its copies, sum before it
        long long before;
        int pos = findSlot(k, before);
        const T* sorted = vals.data();
        const int* counts = cnt.data();
        return {sorted[pos], before, counts[pos], pre(fs, pos)};
    }
    long long findMex() {  // smallest non-negative integer not in the set
        if (!run) return 0;  // 0 is not even a possible value
        // first absent position p >= z: lift while the number of absent positions so far stays at the count before z
        long long a0 = z - pre(fp, z), acc = 0;
        int pos = 0;
        for (int step = top; step; step >>= 1)
            if (pos + step <= m && (pos + step) - (acc + fp[pos + step]) <= a0) pos += step, acc += fp[pos];
        return std::min<long long>(pos - z, run);
    }

    LEETCODE_NO_SANITIZE void addRaw(T x, long long c) {  // c copies of x (c < 0 removes); keeps the mex current
        int i = rankOf(x);
        addAt(i == m ? lowerIdx(x) : i, x, c);
    }

    LEETCODE_NO_SANITIZE void addAt(int i, T x, long long c) {  // addRaw, with x's position known
        if (__builtin_expect(n + c > 2147483647LL, 0)) tooManyCopies();
        n += c;
        total += S(c) * x;
        if (c & 1) xtotal ^= x;  // an odd number of copies flips x in or out of the xor of everything
        long long f = insertAt(i, x, c);  // x's new count
        long long g = f - c;  // x's old count
        {  // gaps
            if ((g >= 2) != (f >= 2)) dups += f >= 2 ? 1 : -1;  // values with 2+ copies (then the smallest difference is 0)
        }
        if (c > 0) {
            if constexpr (is_integral_v<T>) if (x == T(mexV)) mexV = findMex();  // x filled the mex
        } else {
            if constexpr (is_integral_v<T>) if (x >= 0 && x < T(mexV) && !f) mexV = x;  // the last copy of a value below the mex
        }
    }

    LEETCODE_NO_SANITIZE S sumFirst(long long k) {  // sum of the k smallest values
        if (k <= 0) return 0;
        Info f = kthInfo(k);
        return f.sb + S(k - f.before) * f.v;
    }

    void resetCached() {  // nothing counted: as newly built
        mexV = 0;
        dups = 0;
        n = d = 0;
        total = 0;
        xtotal = 0;
    }

    void clearData() {  // few distinct values present: zero only their slots and Fenwick paths, else wipe in bulk
        if (d * (65 - __builtin_clzll((unsigned long long)top | 1)) * 8 < m) {
            vector<int> slots;
            for (long long k = 1; k <= n;) {  // the slot of the k-th smallest, by binary lifting; then skip its copies
                long long before;
                int pos = findSlot(k, before);
                slots.push_back(pos);
                k = before + cnt[pos] + 1;
            }
            for (int i : slots) {
                cnt[i] = 0;
                gapSet(i, false);
                for (int j = i + 1; j <= m; j += j & -j) fs[j] = 0, fp[j] = 0, fx[j] = 0;
                for (int level = 0, idx = i; level < levels; level++) {
                    idx >>= 4;
                    fill_n(tree.begin() + levelStart[level] + idx * 16, 16, 0);
                }
            }
        } else {
            fill(cnt.begin(), cnt.end(), 0), fill(tree.begin(), tree.end(), 0), fill(fs.begin(), fs.end(), 0), fill(fp.begin(), fp.end(), 0), fill(fx.begin(), fx.end(), 0), fill(gapFirst.begin(), gapFirst.end(), -1), fill(gapLast.begin(), gapLast.end(), -1), fill(gapMin.begin(), gapMin.end(), LLONG_MAX), fill(gapMax.begin(), gapMax.end(), -1);
        }
    }

    long long distinctLt(T x) { return pre(fp, lowerIdx(x)); }  // distinct values < x: the Fenwick of present values

    T xpre(int i) const {  // xor over positions 0..i-1
        T res = 0;
        for (; i > 0; i &= i - 1) res ^= fx[i];
        return res;
    }

    T xlt(T x) const { return xpre(lowerIdx(x)); }
    T xle(T x) const { return xpre(upperIdx(x)); }

    T xorFirst(long long k) const {  // xor of the k smallest values (copies count): binary lifting, as for the k-th
        if (k <= 0) return 0;
        long long before;
        int pos = findSlot(k, before);
        T res = xpre(pos);
        return (k - before) & 1 ? T(res ^ vals[pos]) : res;  // k - before copies of the answer's value
    }

    // O(logN) -- add one copy of x
    LEETCODE_NO_SANITIZE void add(T x) {
        addRaw(x, 1);
    }

    // O(logN) -- add cnt copies of val (nothing if cnt <= 0)
    void addCount(T val, long long cnt) {
        if (cnt > 0) addRaw(val, cnt);
    }

    // O(1 amortized) -- remove everything: afterwards it is as if newly built (same constructor arguments), so reuse it
    // instead of building a new one
    void clear() {
        clearData();
        resetCached();
    }

    // O(logN) -- how many copies of x
    LEETCODE_NO_SANITIZE long long count(T x) {
        return countOf(x);
    }

    // O(1) -- how many distinct values
    long long countDistinct() {
        return d;
    }

    // O(logN) -- how many distinct values v with lo <= v <= hi (0 if lo > hi)
    long long countDistinctInValRange(T lo, T hi) {
        if (hi < lo) return 0;
        return distinctLt(hi) - distinctLt(lo) + (countOf(hi) ? 1 : 0);
    }

    // O(logN) -- how many values > x
    long long countGtX(T x) {
        return n - le(x);
    }

    // O(logN) -- how many values >= x
    long long countGteX(T x) {
        return n - lt(x);
    }

    // O(logN) -- how many values v with lo <= v <= hi (0 if lo > hi)
    long long countInValRange(T lo, T hi) {
        return lo <= hi ? le(hi) - lt(lo) : 0;
    }

    // O(logN) -- how many values < x
    long long countLtX(T x) {
        return lt(x);
    }

    // O(logN) -- how many values <= x
    long long countLteX(T x) {
        return le(x);
    }

    // O(logN) -- 0-indexed position of the first copy of x in sorted order (= how many values < x); -1 if x is not in
    // the set
    long long firstIndex(T x) {
        return countOf(x) ? lt(x) : -1;
    }

    // O(logN) -- the value at sorted position i, 0-indexed: kth(0) is the smallest, kth(1) the 2nd smallest,
    // kth(size - 1) the largest (copies count: in {2, 2, 5}, kth(1) is 2); throws out_of_range unless 0 <= i < size
    LEETCODE_NO_SANITIZE T kth(long long i) {
        if (i < 0 || i >= n) throw out_of_range("kth: needs 0 <= i < size");
        return kthAt(i + 1);
    }

    // O(logN) -- largest value < x; ms.NONE if there is none
    T largestLtX(T x) {
        long long c = lt(x);
        if (!c) return NONE;
        return kthAt(c);
    }

    // O(logN) -- largest value <= x; ms.NONE if there is none
    T largestLteX(T x) {
        long long c = le(x);
        if (!c) return NONE;
        return kthAt(c);
    }

    // O(logN) -- 0-indexed position of the last copy of x in sorted order (= how many values <= x, minus 1); -1 if x is
    // not in the set
    long long lastIndex(T x) {
        return countOf(x) ? le(x) - 1 : -1;
    }

    // O(logN) -- largest value; throws out_of_range if empty
    T max() {
        if (!n) throw out_of_range("max: the set is empty");
        return kthAt(n);
    }

    // O(1 amortized) -- largest difference between two neighbouring distinct values; -1 if fewer than 2 distinct values
    long long maxGap() {
        if (d < 2) return -1;
        return gapMax[1];
    }

    // O(logN) -- upper median: the (floor(size/2) + 1)-th smallest value; throws out_of_range if empty
    T medianHigh() {
        if (!n) throw out_of_range("medianHigh: the set is empty");
        return kthAt(n / 2 + 1);
    }

    // O(logN) -- lower median: the ceil(size/2)-th smallest value; throws out_of_range if empty
    T medianLow() {
        if (!n) throw out_of_range("medianLow: the set is empty");
        return kthAt((n + 1) / 2);
    }

    // O(1) -- smallest non-negative integer not in the set
    long long mex() {
        return mexV;
    }

    // O(logN) -- smallest value; throws out_of_range if empty
    T min() {
        if (!n) throw out_of_range("min: the set is empty");
        return kthAt(1);
    }

    // O(1 amortized) -- smallest difference between two values in the set (0 if some value has 2+ copies); -1 if fewer
    // than 2 values
    long long minAdjacentDiff() {
        if (n < 2) return -1;
        if (dups) return 0LL;
        return gapMin[1];
    }

    // O(logN) -- remove and return the value at sorted position i, 0-indexed: pop(0) removes the smallest (= popMin()),
    // pop(size - 1) the largest (copies count); throws out_of_range unless 0 <= i < size
    T pop(long long i) {
        if (i < 0 || i >= n) throw out_of_range("pop: needs 0 <= i < size");
        T v = kthAt(i + 1);
        addRaw(v, -1);
        return v;
    }

    // O(logN) -- remove and return the largest value; throws out_of_range if empty
    T popMax() {
        if (!n) throw out_of_range("popMax: the set is empty");
        T v = kthAt(n);
        addRaw(v, -1);
        return v;
    }

    // O(logN) -- remove and return the smallest value; throws out_of_range if empty
    T popMin() {
        if (!n) throw out_of_range("popMin: the set is empty");
        T v = kthAt(1);
        addRaw(v, -1);
        return v;
    }

    // O(logN) -- remove one copy of x if present; returns how many were removed (0 or 1)
    LEETCODE_NO_SANITIZE long long remove(T x) {
        int i = rankOf(x);  // one lookup for both the check and the removal
        const int* counts = cnt.data();
        if (i == m || !counts[i]) return 0;
        addAt(i, x, -1);
        return 1;
    }

    // O(logN) -- remove every copy of val; returns how many were removed
    long long removeAll(T val) {
        long long k = count(val);
        if (k) addRaw(val, -k);
        return k;
    }

    // O(logN) -- remove min(cnt, count(val)) copies of val; returns how many were removed
    long long removeCount(T val, long long cnt) {
        long long k = std::min(cnt, count(val));
        if (k <= 0) return 0;
        addRaw(val, -k);
        return k;
    }

    // O(logN amortized) -- remove every value v with lo <= v <= hi; returns how many copies were removed (0 if lo > hi)
    long long removeInValRange(T lo, T hi) {
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

    // O(logN) -- smallest value > x; ms.NONE if there is none
    T smallestGtX(T x) {
        long long c = le(x);
        if (c == n) return NONE;
        return kthAt(c + 1);
    }

    // O(logN) -- smallest value >= x; ms.NONE if there is none
    T smallestGteX(T x) {
        long long c = lt(x);
        if (c == n) return NONE;
        return kthAt(c + 1);
    }

    // O(logN) -- sum of |v - medianLow()| over all values (min total moves to make all equal); 0 if empty
    S sumAbsDiffToMedian() {
        if (!n) return 0;
        Info m = kthInfo((n + 1) / 2);
        return S(m.v) * m.before - m.sb + (total - m.sb - S(m.v) * m.c) - S(m.v) * (n - m.before - m.c);
    }

    // O(logN) -- sum of |v - x| over all values
    S sumAbsDiffToX(T x) {
        long long c = lt(x);
        S s = slt(x);
        return S(x) * c - s + (total - s) - S(x) * (n - c);
    }

    // O(1) -- sum of all values
    S sumAll() {
        return total;
    }

    // O(logN) -- sum of the values > x
    S sumGtX(T x) {
        return total - sle(x);
    }

    // O(logN) -- sum of the values >= x
    S sumGteX(T x) {
        return total - slt(x);
    }

    // O(logN) -- sum of the values v with lo <= v <= hi (0 if lo > hi)
    S sumInValRange(T lo, T hi) {
        return lo <= hi ? sle(hi) - slt(lo) : S(0);
    }

    // O(logN) -- sum of the kFrom-th through kTo-th largest values; RANKS, 1-indexed and inclusive: (1, 1) is just the
    // largest, (5, 8) the 5th, 6th, 7th and 8th largest, (1, size) every value (copies count); throws out_of_range
    // unless 1 <= kFrom <= kTo <= size
    S sumKthLargestRange(long long kFrom, long long kTo) {
        if (kFrom < 1 || kFrom > kTo || kTo > n) throw out_of_range("sumKthLargestRange: needs 1 <= kFrom <= kTo <= size");
        return sumFirst(n - kFrom + 1) - sumFirst(n - kTo);
    }

    // O(logN) -- sum of the kFrom-th through kTo-th smallest values; RANKS, 1-indexed and inclusive: (1, 1) is just the
    // smallest, (2, 4) the 2nd, 3rd and 4th smallest, (1, size) every value (copies count); throws out_of_range unless
    // 1 <= kFrom <= kTo <= size
    S sumKthSmallestRange(long long kFrom, long long kTo) {
        if (kFrom < 1 || kFrom > kTo || kTo > n) throw out_of_range("sumKthSmallestRange: needs 1 <= kFrom <= kTo <= size");
        return sumFirst(kTo) - sumFirst(kFrom - 1);
    }

    // O(logN) -- sum of the k largest values; k is a COUNT, not an index: k = 0 takes no values (returns 0), k = 1 just
    // the largest, k = size every value (copies count: in {2, 5, 5}, k = 2 takes 5 and 5); throws out_of_range unless 0
    // <= k <= size
    LEETCODE_NO_SANITIZE S sumLargestK(long long k) {
        if (k < 0 || k > n) throw out_of_range("sumLargestK: needs 0 <= k <= size");
        return total - sumFirst(n - k);
    }

    // O(logN) -- sum of the values < x
    S sumLtX(T x) {
        return slt(x);
    }

    // O(logN) -- sum of the values <= x
    S sumLteX(T x) {
        return sle(x);
    }

    // O(logN) -- sum of the k smallest values; k is a COUNT, not an index: k = 0 takes no values (returns 0), k = 1
    // just the smallest, k = size every value (copies count: in {2, 2, 5}, k = 2 takes 2 and 2); throws out_of_range
    // unless 0 <= k <= size
    LEETCODE_NO_SANITIZE S sumSmallestK(long long k) {
        if (k < 0 || k > n) throw out_of_range("sumSmallestK: needs 0 <= k <= size");
        return sumFirst(k);
    }

    // O(1) -- xor of all values (copies count: a value with an even count cancels out); 0 if empty
    T xorOfAll() {
        return xtotal;
    }

    // O(logN) -- xor of the values > x (copies count)
    T xorOfGtX(T x) {
        return xtotal ^ xle(x);
    }

    // O(logN) -- xor of the values >= x (copies count)
    T xorOfGteX(T x) {
        return xtotal ^ xlt(x);
    }

    // O(logN) -- xor of the values v with lo <= v <= hi (copies count; 0 if lo > hi)
    T xorOfInValRange(T lo, T hi) {
        return lo <= hi ? T(xle(hi) ^ xlt(lo)) : T(0);
    }

    // O(logN) -- xor of the kFrom-th through kTo-th largest values; RANKS, 1-indexed and inclusive: (1, 1) is just the
    // largest, (5, 8) the 5th, 6th, 7th and 8th largest, (1, size) every value (copies count); throws out_of_range
    // unless 1 <= kFrom <= kTo <= size
    T xorOfKthLargestRange(long long kFrom, long long kTo) {
        if (kFrom < 1 || kFrom > kTo || kTo > n) throw out_of_range("xorOfKthLargestRange: needs 1 <= kFrom <= kTo <= size");
        return xorFirst(n - kFrom + 1) ^ xorFirst(n - kTo);
    }

    // O(logN) -- xor of the kFrom-th through kTo-th smallest values; RANKS, 1-indexed and inclusive: (1, 1) is just the
    // smallest, (2, 4) the 2nd, 3rd and 4th smallest, (1, size) every value (copies count); throws out_of_range unless
    // 1 <= kFrom <= kTo <= size
    T xorOfKthSmallestRange(long long kFrom, long long kTo) {
        if (kFrom < 1 || kFrom > kTo || kTo > n) throw out_of_range("xorOfKthSmallestRange: needs 1 <= kFrom <= kTo <= size");
        return xorFirst(kTo) ^ xorFirst(kFrom - 1);
    }

    // O(logN) -- xor of the k largest values; k is a COUNT, not an index: k = 0 takes no values (returns 0), k = 1 just
    // the largest, k = size every value (copies count: in {2, 5, 5}, k = 2 takes 5 and 5); throws out_of_range unless 0
    // <= k <= size
    T xorOfLargestK(long long k) {
        if (k < 0 || k > n) throw out_of_range("xorOfLargestK: needs 0 <= k <= size");
        return xtotal ^ xorFirst(n - k);
    }

    // O(logN) -- xor of the values < x (copies count)
    T xorOfLtX(T x) {
        return xlt(x);
    }

    // O(logN) -- xor of the values <= x (copies count)
    T xorOfLteX(T x) {
        return xle(x);
    }

    // O(logN) -- xor of the k smallest values; k is a COUNT, not an index: k = 0 takes no values (returns 0), k = 1
    // just the smallest, k = size every value (copies count: in {2, 2, 5}, k = 2 takes 2 and 2); throws out_of_range
    // unless 0 <= k <= size
    T xorOfSmallestK(long long k) {
        if (k < 0 || k > n) throw out_of_range("xorOfSmallestK: needs 0 <= k <= size");
        return xorFirst(k);
    }
};
