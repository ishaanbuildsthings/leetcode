// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/sets/blocks-with-and-cachedmex-medians-mode/fast.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: add addCount andOfAll andOfGtX andOfGteX andOfInValRange andOfKthLargestRange andOfKthSmallestRange andOfLargestK andOfLtX andOfLteX andOfSmallestK clear count countDistinct countDistinctInValRange countGtX countGteX countInValRange countLtX countLteX firstIndex kth largestLtX largestLteX lastIndex max medianHigh medianLow mex min mode pop popMax popMin remove removeAll removeCount removeInValRange size smallestGtX smallestGteX
// @data-structure-type: blocks
// @values: online
// @keys: numbers
// @tracks: medians mex mode
// @complexities:
//   add: sqrt(N) amortized
//   addCount: sqrt(N) amortized
//   andOfAll: sqrt(N)
//   andOfGtX: sqrt(N)
//   andOfGteX: sqrt(N)
//   andOfInValRange: sqrt(N)
//   andOfKthLargestRange: sqrt(N)
//   andOfKthSmallestRange: sqrt(N)
//   andOfLargestK: sqrt(N)
//   andOfLtX: sqrt(N)
//   andOfLteX: sqrt(N)
//   andOfSmallestK: sqrt(N)
//   clear: 1 amortized
//   count: log(N)
//   countDistinct: 1
//   countDistinctInValRange: sqrt(N)
//   countGtX: sqrt(N)
//   countGteX: sqrt(N)
//   countInValRange: sqrt(N)
//   countLtX: sqrt(N)
//   countLteX: sqrt(N)
//   firstIndex: sqrt(N)
//   kth: sqrt(N)
//   largestLtX: sqrt(N)
//   largestLteX: sqrt(N)
//   lastIndex: sqrt(N)
//   max: sqrt(N)
//   medianHigh: 1
//   medianLow: 1
//   mex: 1
//   min: sqrt(N)
//   mode: 1
//   pop: sqrt(N) amortized
//   popMax: sqrt(N) amortized
//   popMin: sqrt(N) amortized
//   remove: sqrt(N) amortized
//   removeAll: sqrt(N) amortized
//   removeCount: sqrt(N) amortized
//   removeInValRange: sqrt(N) amortized
//   size: 1
//   smallestGtX: sqrt(N)
//   smallestGteX: sqrt(N)
//   build: 1
// @memory:
//   layout: none
//   node: keys[1*N] cnts[1*N]
//   tags: none
//   other: maxes[20*sqrt(N)+2] bc[40*sqrt(N)+5] ba[20*sqrt(N)+2] cnt[1*N]
//   note: N = distinct values present; blocks of max(LOAD, sqrt(N) / 8) values (LOAD: Python 64, C++ 512), all cut again once N / 2 distinct values have come or gone, or once there are more than 2 * N / size + 2 blocks; each operation costs a few binary searches plus one block's worth of C-level list work

// Ordered multiset (online: any values, nothing known ahead), sqrt-style: the distinct values in sorted blocks of
// max(LOAD, sqrt(N) / 8), each block keeping its values' copies plus block totals and each block's AND, and a Fenwick
// tree over the
// block totals (rebuilt only after a block splits or empties). A block splits in half past twice the block size, and
// once N / 2 distinct values have come or gone since the last cut, every block is cut again at that size: blocks
// follow sqrt(N) as N grows or shrinks (small blocks are faster in practice; any constant times sqrt(N) keeps the
// bounds). The blocks are also cut again as soon as there are more than 2 * N / size + 2 of them (removals can leave
// many small blocks), so there are never more than 20 sqrt(N) + 2. A cut is O(N), paid for by the N / 4 or more
// updates since the last one. A query
// finds its block by binary search (or by lifting over the block Fenwick for k-th) and then works inside one block.
// T: an integer type; sums in S.
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
struct BlockMultiset {
    template <class K>
    LEETCODE_NO_SANITIZE static K noneOf() {  // the lowest value of K, part by part for pairs and tuples
        if constexpr (is_arithmetic_v<K>) return numeric_limits<K>::lowest();
        else return apply([](auto... parts) { return K{noneOf<decltype(parts)>()...}; }, K{});
    }
    // what largestLtX, smallestGtX, ... return when nothing qualifies: compare with ms.NONE. It is the lowest T, so a
    // real value equal to it reads as "nothing"
    static inline const T NONE = noneOf<T>();

    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    static constexpr int LOAD = 512;  // the smallest block size (sqrt(N) / 8 once N passes (8 * LOAD)^2)
    int load = LOAD;  // the block size now
    long long due = (long long)LOAD * LOAD / 2;  // distinct values to add or drop before the next cut
    HotVector<HotVector<T>> keys;  // blocks of sorted distinct values
    HotVector<HotVector<long long>> cnts;  // per block: copies of each value
    HotVector<T> maxes;  // last value of each block
    HotVector<long long> bc, fc;  // per block total copies; Fenwick over it
    HotVector<T> ba;  // per block AND of its values
    bool stale = true;  // the Fenwicks need a rebuild
    long long n = 0, d = 0;
    struct Info { T v; long long before, c; };  // a value, copies before it, its copies
    Info low{}, high{};  // both medians, kept current by addRaw while n > 0
    long long mexV = 0;  // the mex, kept current (0 for the empty set)
    map<long long, set<T>> bk;  // mode: count -> the values with that many copies

    // O(1) -- an empty multiset
    BlockMultiset() {}

    template <class V>
    LEETCODE_NO_SANITIZE static void build(HotVector<V>& f, const HotVector<V>& a) {
        f.assign(a.size() + 1, 0);
        for (size_t i = 1; i < f.size(); i++) {
            f[i] += a[i - 1];
            size_t j = i + (i & -i);
            if (j < f.size()) f[j] += f[i];
        }
    }

    LEETCODE_NO_SANITIZE void fresh() {
        if (!stale) return;
        build(fc, bc);
        stale = false;
    }

    template <class V>
    LEETCODE_NO_SANITIZE void fen(HotVector<V>& f, int i, V v) {
        if (stale) return;
        for (i++; i < (int)f.size(); i += i & -i) f[i] += v;
    }

    template <class V>
    LEETCODE_NO_SANITIZE V pre(const HotVector<V>& f, int k) {  // total of blocks 0..k-1
        fresh();
        V res = 0;
        for (; k > 0; k &= k - 1) res += f[k];
        return res;
    }

    LEETCODE_NO_SANITIZE int blockOf(T x) const {
        return int(lower_bound(maxes.begin(), maxes.end(), x) - maxes.begin());
    }

    LEETCODE_NO_SANITIZE long long insert(T x, long long c) {  // returns x's new count
        if (due <= 0) recut();  // enough distinct values came or went: cut the blocks again
        int k = blockOf(x);
        if (k < (int)keys.size()) {
            int j = int(lower_bound(keys[k].begin(), keys[k].end(), x) - keys[k].begin());
            if (j < (int)keys[k].size() && keys[k][j] == x) {  // x is already here
                if (cnts[k][j] + c) {
                    cnts[k][j] += c, bc[k] += c, fen(fc, k, c);
                    return cnts[k][j];
                }
                d--, due--;
                keys[k].erase(keys[k].begin() + j), cnts[k].erase(cnts[k].begin() + j);
                if (keys[k].empty()) {  // the block is empty: drop it
                    keys.erase(keys.begin() + k), cnts.erase(cnts.begin() + k), maxes.erase(maxes.begin() + k),
                        bc.erase(bc.begin() + k);
                    ba.erase(ba.begin() + k);
                    stale = true;
                    return 0;
                }
                ba[k] = accumulate(keys[k].begin(), keys[k].end(), ~T(0), bit_and<T>());
                maxes[k] = keys[k].back(), bc[k] += c, fen(fc, k, c);
                if ((long long)keys.size() > 2 * d / load + 2) recut();  // too many blocks for the values: cut again
                return 0;
            }
        }
        d++, due--;
        if (keys.empty()) {
            keys.push_back({x}), cnts.push_back({c}), maxes.push_back(x), bc.push_back(c);
            ba.push_back(x);
            stale = true;
            return c;
        }
        if (k == (int)keys.size()) k--;
        int j = int(lower_bound(keys[k].begin(), keys[k].end(), x) - keys[k].begin());
        keys[k].insert(keys[k].begin() + j, x), cnts[k].insert(cnts[k].begin() + j, c);
        maxes[k] = keys[k].back(), bc[k] += c, fen(fc, k, c);
        ba[k] &= x;
        if ((int)keys[k].size() > 2 * load) {  // split the block in half
            auto half = [&](auto& arr) {
                arr.insert(arr.begin() + k + 1, decay_t<decltype(arr[k])>(arr[k].begin() + load, arr[k].end()));
                arr[k].resize(load);
            };
            half(keys), half(cnts);
            maxes[k] = keys[k].back(), maxes.insert(maxes.begin() + k + 1, keys[k + 1].back());
            bc[k] = accumulate(cnts[k].begin(), cnts[k].end(), 0LL);
            bc.insert(bc.begin() + k + 1, accumulate(cnts[k + 1].begin(), cnts[k + 1].end(), 0LL));
            ba[k] = accumulate(keys[k].begin(), keys[k].end(), ~T(0), bit_and<T>());
            ba.insert(ba.begin() + k + 1, accumulate(keys[k + 1].begin(), keys[k + 1].end(), ~T(0), bit_and<T>()));
            stale = true;
            if ((long long)keys.size() > 2 * d / load + 2) recut();  // too many blocks for the values: cut again
        }
        return c;
    }

    LEETCODE_NO_SANITIZE void recut() {
        // every block cut again at sqrt(N) / 8: O(N), at most once per N / 4 value adds / drops
        int size = std::max(LOAD, (int)sqrt((double)d) / 8);  // (std::: the class has its own min / max)
        due = std::max(d, (long long)LOAD * LOAD) / 2;
        if (size == load && (long long)keys.size() <= d / size + 1) return;  // same size, blocks still full on average
        load = size;
        auto regroup = [&](auto& arr) {  // the blocks' entries end to end, cut into blocks of load
            decay_t<decltype(arr[0])> all;
            for (auto& b : arr) all.insert(all.end(), b.begin(), b.end());
            arr.clear();
            for (size_t i = 0; i < all.size(); i += load)
                arr.emplace_back(all.begin() + i, all.begin() + std::min(all.size(), i + load));
        };
        regroup(keys), regroup(cnts);
        int m = (int)keys.size();
        maxes.resize(m), bc.resize(m);
        ba.resize(m);
        for (int k = 0; k < m; k++) {
            maxes[k] = keys[k].back(), bc[k] = accumulate(cnts[k].begin(), cnts[k].end(), 0LL);
            ba[k] = accumulate(keys[k].begin(), keys[k].end(), ~T(0), bit_and<T>());
        }
        stale = true;
    }

    LEETCODE_NO_SANITIZE long long countBelow(T x, bool strict) {  // copies of the values < x (strict) or <= x
        int k = blockOf(x);
        if (k == (int)keys.size()) return n;
        const HotVector<T>& b = keys[k];
        int j = int((strict ? lower_bound(b.begin(), b.end(), x) : upper_bound(b.begin(), b.end(), x)) - b.begin());
        return pre(fc, k) + accumulate(cnts[k].begin(), cnts[k].begin() + j, 0LL);
    }

    LEETCODE_NO_SANITIZE long long lt(T x) { return countBelow(x, true); }
    LEETCODE_NO_SANITIZE long long le(T x) { return countBelow(x, false); }

    LEETCODE_NO_SANITIZE long long countOf(T x) const {
        int k = blockOf(x);
        if (k == (int)keys.size()) return 0;
        int j = int(lower_bound(keys[k].begin(), keys[k].end(), x) - keys[k].begin());
        return j < (int)keys[k].size() && keys[k][j] == x ? cnts[k][j] : 0;
    }

    // the block holding the k-th smallest value: (block, copies before it, sum before it)
    LEETCODE_NO_SANITIZE tuple<int, long long, S> locate(long long k) {
        fresh();
        int pos = 0, m = (int)bc.size();
        long long before = 0;
        S acc{};
        for (int step = m ? 1 << (31 - __builtin_clz(m)) : 0; step; step >>= 1)
            if (pos + step <= m && before + fc[pos + step] < k) {
                pos += step, before += fc[pos];
            }
        return {pos, before, acc};
    }

    LEETCODE_NO_SANITIZE T kthAt(long long k) {
        auto [b, before, acc] = locate(k);
        (void)acc;
        k -= before;
        for (size_t j = 0;; j++) {
            if (k <= cnts[b][j]) return keys[b][j];
            k -= cnts[b][j];
        }
    }
    LEETCODE_NO_SANITIZE Info kthInfo(long long k) {  // the k-th smallest, copies before it, its copies
        auto [b, before, acc] = locate(k);
        (void)acc;
        for (size_t j = 0;; j++) {
            if (k <= before + cnts[b][j]) return {keys[b][j], before, cnts[b][j]};
            before += cnts[b][j];
        }
    }
    // smallest non-negative integer not in the set: walk the blocks from 0 while the values run 0, 1, 2, ...
    LEETCODE_NO_SANITIZE long long findMex() {
        int k = blockOf(T(0));
        if (k == (int)keys.size()) return 0;
        int j = int(lower_bound(keys[k].begin(), keys[k].end(), T(0)) - keys[k].begin());
        long long want = 0;
        for (; k < (int)keys.size(); k++, j = 0) {
            const HotVector<T>& b = keys[k];
            if (b[j] != T(want)) return want;
            long long len = (long long)b.size();
            if ((long long)b.back() - b[j] == len - 1 - j) {  // this block continues the run to its end
                want = (long long)b.back() + 1;
                continue;
            }
            int lo = j, hi = (int)len - 1;  // the run breaks inside: first p with b[p] - p > b[j] - j
            while (lo < hi) {
                int mid = (lo + hi) / 2;
                if ((long long)b[mid] - mid > (long long)b[j] - j) hi = mid;
                else lo = mid + 1;
            }
            return (long long)b[lo - 1] + 1;
        }
        return want;
    }

    LEETCODE_NO_SANITIZE void addRaw(T x, long long c) {
        // c copies of x (c < 0 removes); keeps both medians, the mex current
        n += c;
        long long f = insert(x, c);  // x's new count
        long long g = f - c;  // x's old count
        {  // mode: x moves from the bucket of its old count to its new one
            if (g) {
                auto it = bk.find(g);
                it->second.erase(x);
                if (it->second.empty()) bk.erase(it);
            }
            if (f) bk[f].insert(x);
        }
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
        bk.clear();
        n = d = 0;
    }

    LEETCODE_NO_SANITIZE void clearData() {
        keys.clear(), cnts.clear(), maxes.clear(), bc.clear(), fc.clear();
        load = LOAD, due = (long long)LOAD * LOAD / 2;
        ba.clear();
        stale = true;
    }

    LEETCODE_NO_SANITIZE long long distinctLt(T x) const {
        // distinct values < x: every block before x's, then a binary search in x's block
        int b = int(lower_bound(maxes.begin(), maxes.end(), x) - maxes.begin());
        long long res = 0;
        for (int k = 0; k < b; k++) res += (long long)keys[k].size();
        if (b < (int)keys.size()) res += lower_bound(keys[b].begin(), keys[b].end(), x) - keys[b].begin();
        return res;
    }

    LEETCODE_NO_SANITIZE T andLe(T x) const {  // AND of the values <= x
        // blocks before b hold only values <= x
        int b = int(upper_bound(maxes.begin(), maxes.end(), x) - maxes.begin());
        T res = ~T(0);
        for (int k = 0; k < b; k++) res &= ba[k];
        if (b < (int)keys.size())
            for (T v : keys[b]) {
                if (x < v) break;
                res &= v;
            }
        return res;
    }

    LEETCODE_NO_SANITIZE T andGe(T x) const {  // AND of the values >= x
        int a = blockOf(x);  // blocks after a hold only values >= x
        T res = ~T(0);
        if (a == (int)keys.size()) return res;
        for (int k = a + 1; k < (int)keys.size(); k++) res &= ba[k];
        for (auto it = lower_bound(keys[a].begin(), keys[a].end(), x); it != keys[a].end(); ++it) res &= *it;
        return res;
    }

    LEETCODE_NO_SANITIZE T andIn(T lo, T hi) const {  // AND of the values in [lo, hi] (lo <= hi)
        int a = blockOf(lo), b = int(upper_bound(maxes.begin(), maxes.end(), hi) - maxes.begin());
        T res = ~T(0);
        if (a == (int)keys.size()) return res;
        auto it = lower_bound(keys[a].begin(), keys[a].end(), lo);
        if (a == b) {  // one block holds them all
            for (; it != keys[a].end() && !(hi < *it); ++it) res &= *it;
            return res;
        }
        for (; it != keys[a].end(); ++it) res &= *it;
        for (int k = a + 1; k < b; k++) res &= ba[k];  // blocks a + 1 .. b - 1 lie wholly inside
        if (b < (int)keys.size())
            for (T v : keys[b]) {
                if (hi < v) break;
                res &= v;
            }
        return res;
    }

    // O(sqrtN amortized) -- add one copy of x
    LEETCODE_NO_SANITIZE void add(T x) {
        addRaw(x, 1);
    }

    // O(sqrtN amortized) -- add cnt copies of val (nothing if cnt <= 0)
    LEETCODE_NO_SANITIZE void addCount(T val, long long cnt) {
        if (cnt > 0) addRaw(val, cnt);
    }

    // O(sqrtN) -- bitwise AND of all values; -1 (every bit set) if empty
    LEETCODE_NO_SANITIZE T andOfAll() {
        T res = ~T(0);
        for (T v : ba) res &= v;
        return res;
    }

    // O(sqrtN) -- bitwise AND of the values > x; -1 (every bit set) if there are none
    LEETCODE_NO_SANITIZE T andOfGtX(T x) {
        if (x == numeric_limits<T>::max()) return ~T(0);
        return andGe(x + 1);
    }

    // O(sqrtN) -- bitwise AND of the values >= x; -1 (every bit set) if there are none
    LEETCODE_NO_SANITIZE T andOfGteX(T x) {
        return andGe(x);
    }

    // O(sqrtN) -- bitwise AND of the values v with lo <= v <= hi; -1 (every bit set) if there are none
    LEETCODE_NO_SANITIZE T andOfInValRange(T lo, T hi) {
        return lo <= hi ? andIn(lo, hi) : ~T(0);
    }

    // O(sqrtN) -- bitwise AND of the kFrom-th through kTo-th largest values; RANKS, 1-indexed and inclusive: (1, 1) is
    // just the largest, (5, 8) the 5th, 6th, 7th and 8th largest, (1, size) every value (copies count); throws
    // out_of_range unless 1 <= kFrom <= kTo <= size
    LEETCODE_NO_SANITIZE T andOfKthLargestRange(long long kFrom, long long kTo) {
        if (kFrom < 1 || kFrom > kTo
            || kTo > n) throw out_of_range("andOfKthLargestRange: needs 1 <= kFrom <= kTo <= size");
        T a = kthAt(n - kTo + 1);
        return andIn(a, kthAt(n - kFrom + 1));
    }

    // O(sqrtN) -- bitwise AND of the kFrom-th through kTo-th smallest values; RANKS, 1-indexed and inclusive: (1, 1) is
    // just the smallest, (2, 4) the 2nd, 3rd and 4th smallest, (1, size) every value (copies count); throws
    // out_of_range unless 1 <= kFrom <= kTo <= size
    LEETCODE_NO_SANITIZE T andOfKthSmallestRange(long long kFrom, long long kTo) {
        if (kFrom < 1 || kFrom > kTo
            || kTo > n) throw out_of_range("andOfKthSmallestRange: needs 1 <= kFrom <= kTo <= size");
        T a = kthAt(kFrom);
        return andIn(a, kthAt(kTo));
    }

    // O(sqrtN) -- bitwise AND of the k largest values; k is a COUNT, not an index: k = 0 takes no values (returns -1,
    // every bit set), k = 1 just the largest, k = size every value (copies count: in {2, 5, 5}, k = 2 takes 5 and 5);
    // throws out_of_range unless 0 <= k <= size
    LEETCODE_NO_SANITIZE T andOfLargestK(long long k) {
        if (k < 0 || k > n) throw out_of_range("andOfLargestK: needs 0 <= k <= size");
        return k ? andGe(kthAt(n - k + 1)) : ~T(0);
    }

    // O(sqrtN) -- bitwise AND of the values < x; -1 (every bit set) if there are none
    LEETCODE_NO_SANITIZE T andOfLtX(T x) {
        if (x == numeric_limits<T>::min()) return ~T(0);
        return andLe(x - 1);
    }

    // O(sqrtN) -- bitwise AND of the values <= x; -1 (every bit set) if there are none
    LEETCODE_NO_SANITIZE T andOfLteX(T x) {
        return andLe(x);
    }

    // O(sqrtN) -- bitwise AND of the k smallest values; k is a COUNT, not an index: k = 0 takes no values (returns -1,
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

    // O(logN) -- how many copies of x
    LEETCODE_NO_SANITIZE long long count(T x) {
        return countOf(x);
    }

    // O(1) -- how many distinct values
    LEETCODE_NO_SANITIZE long long countDistinct() {
        return d;
    }

    // O(sqrtN) -- how many distinct values v with lo <= v <= hi (0 if lo > hi)
    LEETCODE_NO_SANITIZE long long countDistinctInValRange(T lo, T hi) {
        if (hi < lo) return 0;
        return distinctLt(hi) - distinctLt(lo) + (countOf(hi) ? 1 : 0);
    }

    // O(sqrtN) -- how many values > x
    LEETCODE_NO_SANITIZE long long countGtX(T x) {
        return n - le(x);
    }

    // O(sqrtN) -- how many values >= x
    LEETCODE_NO_SANITIZE long long countGteX(T x) {
        return n - lt(x);
    }

    // O(sqrtN) -- how many values v with lo <= v <= hi (0 if lo > hi)
    LEETCODE_NO_SANITIZE long long countInValRange(T lo, T hi) {
        return lo <= hi ? le(hi) - lt(lo) : 0;
    }

    // O(sqrtN) -- how many values < x
    LEETCODE_NO_SANITIZE long long countLtX(T x) {
        return lt(x);
    }

    // O(sqrtN) -- how many values <= x
    LEETCODE_NO_SANITIZE long long countLteX(T x) {
        return le(x);
    }

    // O(sqrtN) -- 0-indexed position of the first copy of x in sorted order (= how many values < x); -1 if x is not in
    // the set
    LEETCODE_NO_SANITIZE long long firstIndex(T x) {
        return countOf(x) ? lt(x) : -1;
    }

    // O(sqrtN) -- the value at sorted position i, 0-indexed: kth(0) is the smallest, kth(1) the 2nd smallest,
    // kth(size - 1) the largest (copies count: in {2, 2, 5}, kth(1) is 2); throws out_of_range unless 0 <= i < size
    LEETCODE_NO_SANITIZE T kth(long long i) {
        if (i < 0 || i >= n) throw out_of_range("kth: needs 0 <= i < size");
        return kthAt(i + 1);
    }

    // O(sqrtN) -- largest value < x; ms.NONE if there is none
    LEETCODE_NO_SANITIZE T largestLtX(T x) {
        long long c = lt(x);
        if (!c) return NONE;
        return kthAt(c);
    }

    // O(sqrtN) -- largest value <= x; ms.NONE if there is none
    LEETCODE_NO_SANITIZE T largestLteX(T x) {
        long long c = le(x);
        if (!c) return NONE;
        return kthAt(c);
    }

    // O(sqrtN) -- 0-indexed position of the last copy of x in sorted order (= how many values <= x, minus 1); -1 if x
    // is not in the set
    LEETCODE_NO_SANITIZE long long lastIndex(T x) {
        return countOf(x) ? le(x) - 1 : -1;
    }

    // O(sqrtN) -- largest value; throws out_of_range if empty
    LEETCODE_NO_SANITIZE T max() {
        if (!n) throw out_of_range("max: the set is empty");
        return kthAt(n);
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

    // O(sqrtN) -- smallest value; throws out_of_range if empty
    LEETCODE_NO_SANITIZE T min() {
        if (!n) throw out_of_range("min: the set is empty");
        return kthAt(1);
    }

    // O(1) -- (a most frequent value, its count); throws out_of_range if empty. C++ returns the smallest of the most
    // frequent values
    LEETCODE_NO_SANITIZE pair<T, long long> mode() {
        if (!n) throw out_of_range("mode: the set is empty");
        auto& [f, vs] = *bk.rbegin();
        return pair<T, long long>{*vs.begin(), f};
    }

    // O(sqrtN amortized) -- remove and return the value at sorted position i, 0-indexed: pop(0) removes the smallest (=
    // popMin()), pop(size - 1) the largest (copies count); throws out_of_range unless 0 <= i < size
    LEETCODE_NO_SANITIZE T pop(long long i) {
        if (i < 0 || i >= n) throw out_of_range("pop: needs 0 <= i < size");
        T v = kthAt(i + 1);
        addRaw(v, -1);
        return v;
    }

    // O(sqrtN amortized) -- remove and return the largest value; throws out_of_range if empty
    LEETCODE_NO_SANITIZE T popMax() {
        if (!n) throw out_of_range("popMax: the set is empty");
        T v = kthAt(n);
        addRaw(v, -1);
        return v;
    }

    // O(sqrtN amortized) -- remove and return the smallest value; throws out_of_range if empty
    LEETCODE_NO_SANITIZE T popMin() {
        if (!n) throw out_of_range("popMin: the set is empty");
        T v = kthAt(1);
        addRaw(v, -1);
        return v;
    }

    // O(sqrtN amortized) -- remove one copy of x if present; returns how many were removed (0 or 1)
    LEETCODE_NO_SANITIZE long long remove(T x) {
        if (!count(x)) return 0;
        addRaw(x, -1);
        return 1;
    }

    // O(sqrtN amortized) -- remove every copy of val; returns how many were removed
    LEETCODE_NO_SANITIZE long long removeAll(T val) {
        long long k = count(val);
        if (k) addRaw(val, -k);
        return k;
    }

    // O(sqrtN amortized) -- remove min(cnt, count(val)) copies of val; returns how many were removed
    LEETCODE_NO_SANITIZE long long removeCount(T val, long long cnt) {
        long long k = std::min(cnt, count(val));
        if (k <= 0) return 0;
        addRaw(val, -k);
        return k;
    }

    // O(sqrtN amortized) -- remove every value v with lo <= v <= hi; returns how many copies were removed
    // (0 if lo > hi)
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

    // O(sqrtN) -- smallest value > x; ms.NONE if there is none
    LEETCODE_NO_SANITIZE T smallestGtX(T x) {
        long long c = le(x);
        if (c == n) return NONE;
        return kthAt(c + 1);
    }

    // O(sqrtN) -- smallest value >= x; ms.NONE if there is none
    LEETCODE_NO_SANITIZE T smallestGteX(T x) {
        long long c = lt(x);
        if (c == n) return NONE;
        return kthAt(c + 1);
    }
};
