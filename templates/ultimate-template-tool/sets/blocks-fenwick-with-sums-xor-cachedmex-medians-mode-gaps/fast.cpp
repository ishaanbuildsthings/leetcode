// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/sets/blocks-fenwick-with-sums-xor-cachedmex-medians-mode-gaps/fast.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: add addCount clear count countDistinct countDistinctInValRange countGtX countGteX countInValRange countLtX countLteX firstIndex kth largestLtX largestLteX lastIndex max maxGap medianHigh medianLow mex min minAdjacentDiff mode pop popMax popMin remove removeAll removeCount removeInValRange size smallestGtX smallestGteX sumAbsDiffToMedian sumAbsDiffToX sumAll sumGtX sumGteX sumInValRange sumKthLargestRange sumKthSmallestRange sumLargestK sumLtX sumLteX sumSmallestK xorOfAll xorOfGtX xorOfGteX xorOfInValRange xorOfKthLargestRange xorOfKthSmallestRange xorOfLargestK xorOfLtX xorOfLteX xorOfSmallestK
// @data-structure-type: blocks-fenwick
// @values: online
// @keys: numbers
// @tracks: medians mex mode gaps
// @complexities:
//   add: sqrt(N) amortized
//   addCount: sqrt(N) amortized
//   clear: 1 amortized
//   count: log(N)
//   countDistinct: 1
//   countDistinctInValRange: sqrt(N)
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
//   medianHigh: 1
//   medianLow: 1
//   mex: 1
//   min: log(N)
//   minAdjacentDiff: 1 amortized
//   mode: 1
//   pop: sqrt(N) amortized
//   popMax: sqrt(N) amortized
//   popMin: sqrt(N) amortized
//   remove: sqrt(N) amortized
//   removeAll: sqrt(N) amortized
//   removeCount: sqrt(N) amortized
//   removeInValRange: sqrt(N) amortized
//   size: 1
//   smallestGtX: log(N)
//   smallestGteX: log(N)
//   sumAbsDiffToMedian: 1
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
//   build: 1
// @memory:
//   layout: none
//   node: keys[1*N] cnts[1*N] fcs[1*N] sums[1*N] fss[1*N] xvs[1*N] fxs[1*N]
//   tags: none
//   other: maxes[20*sqrt(N)+2] bc[40*sqrt(N)+5] bs[40*sqrt(N)+5] bx[40*sqrt(N)+5] cnt[1*N]
//   note: N = distinct values present; blocks of max(LOAD, sqrt(N) / 8) values (LOAD: Python 64, C++ 512), all cut again once N / 2 distinct values have come or gone, or once there are more than 2 * N / size + 2 blocks; queries are O(log N), and only updates that add or drop a distinct value pay O(sqrt N) (one block rebuilt; amortized: a cut now and then)

// Ordered multiset (online: any values, nothing known ahead), sqrt-style with a Fenwick tree inside every block: the
// distinct values in sorted blocks of max(LOAD, sqrt(N) / 8), each block keeping its values' copies and copies * value
// and xor plus a Fenwick tree over them, and a Fenwick tree over the block totals. Every query is two Fenwick walks
// (over blocks, then inside one), so O(log N); an update that adds or drops a distinct value rebuilds its block's
// Fenwick (O(sqrt N)).
// A block splits in half past twice the block size, and once N / 2 distinct values have come or gone since the last
// cut, every block is cut again at that size, and also as soon as there are more than 2 * N / size + 2 blocks
// (never more than 20 sqrt(N) + 2): a cut is O(N), paid for by the N / 4 or more updates since the last one.
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
struct BlockFenwickMultiset {
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
    HotVector<HotVector<long long>> cnts, fcs;  // per block: copies of each value; Fenwick over them
    HotVector<HotVector<S>> sums, fss;  // per block: copies * value; Fenwick over them
    HotVector<T> maxes;  // last value of each block
    HotVector<long long> bc, fc{0};  // per block total copies; Fenwick over them
    HotVector<S> bs, fs{0};  // per block total sum; Fenwick over them
    HotVector<HotVector<T>> xvs, fxs;  // per block: each value where its count is odd (else 0); xor Fenwick over them
    HotVector<T> bx, fx{0};  // per block xor of those; xor Fenwick over them
    long long n = 0, d = 0;
    struct Info { T v; long long before, c; S sb; };  // a value, copies before it, its copies, sum before it
    Info low{}, high{};  // both medians, kept current by addRaw while n > 0
    long long mexV = 0;  // the mex, kept current (0 for the empty set)
    map<long long, set<T>> bk;  // mode: count -> the values with that many copies
    multiset<long long> gaps;  // differences between neighbouring distinct values
    long long dups = 0;  // values with 2+ copies
    T xtotal = 0;  // xor of all values (copies count)
    S total = 0;

    // O(1) -- an empty multiset
    BlockFenwickMultiset() {}

    template <class V>
    LEETCODE_NO_SANITIZE static HotVector<V> build(const HotVector<V>& a) {
        HotVector<V> f(a.size() + 1, 0);
        for (size_t i = 1; i < f.size(); i++) {
            f[i] += a[i - 1];
            size_t j = i + (i & -i);
            if (j < f.size()) f[j] += f[i];
        }
        return f;
    }

    template <class V>
    LEETCODE_NO_SANITIZE static void fen(HotVector<V>& f, int i, V v) {
        for (i++; i < (int)f.size(); i += i & -i) f[i] += v;
    }

    template <class V>
    LEETCODE_NO_SANITIZE static V pre(const HotVector<V>& f, int i) {  // f's total over positions 0..i-1
        V res = 0;
        for (; i > 0; i &= i - 1) res += f[i];
        return res;
    }

    LEETCODE_NO_SANITIZE void reblock() {
        fc = build(bc);
        fs = build(bs);
        fx = buildx(bx);
    }

    template <class V>
    LEETCODE_NO_SANITIZE static void rebuildFrom(HotVector<V>& f, const HotVector<V>& a, int from) {
        // only positions >= from changed
        int size = a.size();
        f.resize(size + 1);
        for (int i = from + 1; i <= size; i++) f[i] = 0;
        for (int i = from; i > 0; i &= i - 1)  // finished entries that feed the rebuilt part
            if (int up = i + (i & -i); up <= size) f[up] += f[i];
        for (int i = from + 1; i <= size; i++) {
            f[i] += a[i - 1];
            if (int up = i + (i & -i); up <= size) f[up] += f[i];
        }
    }

    LEETCODE_NO_SANITIZE void reinner(int k, int from = 0) {
        rebuildFrom(fcs[k], cnts[k], from);
        rebuildFrom(fss[k], sums[k], from);
        fxs[k] = buildx(xvs[k]);
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
                bc[k] += c, fen(fc, k, c);
                bs[k] += S(c) * x, fen(fs, k, S(c) * x);
                if (c & 1) bx[k] ^= x, fenx(fx, k, x);  // x's parity flips
                if (cnts[k][j] + c) {  // x stays: point updates only
                    cnts[k][j] += c, fen(fcs[k], j, c);
                    sums[k][j] += S(c) * x, fen(fss[k], j, S(c) * x);
                    if (c & 1) xvs[k][j] ^= x, fenx(fxs[k], j, x);
                    return cnts[k][j];
                }
                d--, due--;
                keys[k].erase(keys[k].begin() + j), cnts[k].erase(cnts[k].begin() + j);
                sums[k].erase(sums[k].begin() + j);
                xvs[k].erase(xvs[k].begin() + j);
                if (keys[k].empty()) {  // the block is empty: drop it
                    keys.erase(keys.begin() + k), cnts.erase(cnts.begin() + k), fcs.erase(fcs.begin() + k);
                    maxes.erase(maxes.begin() + k), bc.erase(bc.begin() + k);
                    sums.erase(sums.begin() + k), fss.erase(fss.begin() + k), bs.erase(bs.begin() + k);
                    xvs.erase(xvs.begin() + k), fxs.erase(fxs.begin() + k), bx.erase(bx.begin() + k);
                    reblock();
                    return 0;
                }
                maxes[k] = keys[k].back();
                reinner(k, j);
                if ((long long)keys.size() > 2 * d / load + 2) recut();  // too many blocks for the values: cut again
                return 0;
            }
        }
        d++, due--;
        if (keys.empty()) {
            keys.push_back({x}), cnts.push_back({c}), fcs.emplace_back(), maxes.push_back(x), bc.push_back(c);
            sums.push_back({S(c) * x}), fss.emplace_back(), bs.push_back(S(c) * x);
            xvs.push_back({c & 1 ? x : T(0)}), fxs.emplace_back(), bx.push_back(c & 1 ? x : T(0));
            reinner(0), reblock();
            return c;
        }
        if (k == (int)keys.size()) k--;
        int j = int(lower_bound(keys[k].begin(), keys[k].end(), x) - keys[k].begin());
        keys[k].insert(keys[k].begin() + j, x), cnts[k].insert(cnts[k].begin() + j, c);
        sums[k].insert(sums[k].begin() + j, S(c) * x), bs[k] += S(c) * x, fen(fs, k, S(c) * x);
        xvs[k].insert(xvs[k].begin() + j, c & 1 ? x : T(0));
        if (c & 1) bx[k] ^= x, fenx(fx, k, x);
        maxes[k] = keys[k].back(), bc[k] += c, fen(fc, k, c);
        if ((int)keys[k].size() > 2 * load) {  // split the block in half
            auto half = [&](auto& arr) {
                arr.insert(arr.begin() + k + 1, decay_t<decltype(arr[k])>(arr[k].begin() + load, arr[k].end()));
                arr[k].resize(load);
            };
            half(keys), half(cnts);
            fcs.emplace(fcs.begin() + k + 1);
            half(sums), fss.emplace(fss.begin() + k + 1);
            half(xvs), fxs.emplace(fxs.begin() + k + 1);
            reinner(k), reinner(k + 1);
            maxes[k] = keys[k].back(), maxes.insert(maxes.begin() + k + 1, keys[k + 1].back());
            bc[k] = accumulate(cnts[k].begin(), cnts[k].end(), 0LL);
            bc.insert(bc.begin() + k + 1, accumulate(cnts[k + 1].begin(), cnts[k + 1].end(), 0LL));
            bs[k] = accumulate(sums[k].begin(), sums[k].end(), S(0));
            bs.insert(bs.begin() + k + 1, accumulate(sums[k + 1].begin(), sums[k + 1].end(), S(0)));
            bx[k] = accumulate(xvs[k].begin(), xvs[k].end(), T(0), bit_xor<T>());
            bx.insert(bx.begin() + k + 1, accumulate(xvs[k + 1].begin(), xvs[k + 1].end(), T(0), bit_xor<T>()));
            reblock();
            if ((long long)keys.size() > 2 * d / load + 2) recut();  // too many blocks for the values: cut again
        } else reinner(k, j);
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
        regroup(sums);
        regroup(xvs);
        int m = (int)keys.size();
        fcs.clear(), fcs.resize(m), maxes.resize(m), bc.resize(m);
        fss.clear(), fss.resize(m), bs.resize(m);
        fxs.clear(), fxs.resize(m), bx.resize(m);
        for (int k = 0; k < m; k++) {
            reinner(k);
            maxes[k] = keys[k].back(), bc[k] = accumulate(cnts[k].begin(), cnts[k].end(), 0LL);
            bs[k] = accumulate(sums[k].begin(), sums[k].end(), S(0));
            bx[k] = accumulate(xvs[k].begin(), xvs[k].end(), T(0), bit_xor<T>());
        }
        reblock();
    }

    template <class V>
    LEETCODE_NO_SANITIZE V below(T x, bool strict, const HotVector<V>& outer, const HotVector<HotVector<V>>& inner,
        V all) const {
        // over values < x / <= x
        int k = int((strict ? lower_bound(maxes.begin(), maxes.end(), x) : upper_bound(maxes.begin(), maxes.end(),
            x)) - maxes.begin());
        if (k == (int)keys.size()) return all;
        const HotVector<T>& b = keys[k];
        int j = int((strict ? lower_bound(b.begin(), b.end(), x) : upper_bound(b.begin(), b.end(), x)) - b.begin());
        return pre(outer, k) + pre(inner[k], j);
    }

    LEETCODE_NO_SANITIZE long long lt(T x) { return below(x, true, fc, fcs, n); }
    LEETCODE_NO_SANITIZE long long le(T x) { return below(x, false, fc, fcs, n); }
    LEETCODE_NO_SANITIZE S slt(T x) { return below(x, true, fs, fss, total); }
    LEETCODE_NO_SANITIZE S sle(T x) { return below(x, false, fs, fss, total); }

    LEETCODE_NO_SANITIZE long long countOf(T x) const {
        int k = blockOf(x);
        if (k == (int)keys.size()) return 0;
        int j = int(lower_bound(keys[k].begin(), keys[k].end(), x) - keys[k].begin());
        return j < (int)keys[k].size() && keys[k][j] == x ? cnts[k][j] : 0;
    }

    LEETCODE_NO_SANITIZE Info kthInfo(long long k) {
        // the k-th smallest, copies before it, its copies, sum before it: lift over blocks, then inside one
        int m = (int)bc.size(), b = 0, j = 0;
        long long before = 0;
        S acc = 0;
        for (int step = 1 << (31 - __builtin_clz(m)); step; step >>= 1)
            if (b + step <= m && before + fc[b + step] < k) b += step, before += fc[b], acc += fs[b];
        const HotVector<long long>& f = fcs[b];
        m = (int)keys[b].size();
        for (int step = 1 << (31 - __builtin_clz(m)); step; step >>= 1)
            if (j + step <= m && before + f[j + step] < k) j += step, before += f[j], acc += fss[b][j];
        return {keys[b][j], before, cnts[b][j], acc};
    }

    LEETCODE_NO_SANITIZE T kthAt(long long k) { return kthInfo(k).v; }

    LEETCODE_NO_SANITIZE long long findMex() {
        // smallest non-negative integer not in the set: walk the blocks from 0 while the values run 0, 1, ...
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
        total += S(c) * x;
        if (c & 1) xtotal ^= x;  // an odd number of copies flips x in or out of the xor of everything
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
        {  // gaps
            // values with 2+ copies (then the smallest difference is 0)
            if ((g >= 2) != (f >= 2)) dups += f >= 2 ? 1 : -1;
            if (!g || !f) {  // x appeared or disappeared: the gap between its neighbours splits or comes back
                long long cl = lt(x), ce = cl + f;  // (ranks, not the public ops: a real value may equal NONE)
                optional<T> p, q;
                if (cl) p = kthAt(cl);
                if (ce < n) q = kthAt(ce + 1);
                auto drop = [&](long long v) { gaps.erase(gaps.find(v)); };
                if (f) {
                    if (p && q) drop((long long)*q - (long long)*p);
                    if (p) gaps.insert((long long)x - (long long)*p);
                    if (q) gaps.insert((long long)*q - (long long)x);
                } else {
                    if (p) drop((long long)x - (long long)*p);
                    if (q) drop((long long)*q - (long long)x);
                    if (p && q) gaps.insert((long long)*q - (long long)*p);
                }
            }
        }
        if (c > 0) {
            if constexpr (is_integral_v<T>) if (x == T(mexV)) mexV = findMex();  // x filled the mex
            if (n == c) {  // the set was empty
                low = high = Info{x, 0, c, 0};
                return;
            }
        } else {
            // the last copy of a value below the mex
            if constexpr (is_integral_v<T>) if (x >= 0 && x < T(mexV) && !f) mexV = x;
            if (!n) return;
        }
        // each median is a tracked rank: shift its (value, copies before, copies, sum before), and search again only
        // when the rank leaves the tracked value
        if (x < low.v) low.before += c, low.sb += S(c) * x;
        else if (x == low.v) low.c += c;
        long long r = (n + 1) / 2;
        if (r <= low.before || r > low.before + low.c) low = kthInfo(r);
        if (x < high.v) high.before += c, high.sb += S(c) * x;
        else if (x == high.v) high.c += c;
        r = n / 2 + 1;
        if (r <= high.before || r > high.before + high.c) high = kthInfo(r);
    }

    LEETCODE_NO_SANITIZE S sumFirst(long long k) {  // sum of the k smallest values
        if (k <= 0) return 0;
        Info f = kthInfo(k);
        return f.sb + S(k - f.before) * f.v;
    }

    LEETCODE_NO_SANITIZE void resetCached() {  // nothing counted: as newly built
        mexV = 0;
        bk.clear();
        gaps.clear(), dups = 0;
        n = d = 0;
        total = 0;
        xtotal = 0;
    }

    LEETCODE_NO_SANITIZE void clearData() {
        keys.clear(), cnts.clear(), fcs.clear(), maxes.clear(), bc.clear();
        fc.assign(1, 0);
        load = LOAD, due = (long long)LOAD * LOAD / 2;
        sums.clear(), fss.clear(), bs.clear();
        fs.assign(1, S(0));
        xvs.clear(), fxs.clear(), bx.clear();
        fx.assign(1, T(0));
    }

    LEETCODE_NO_SANITIZE long long distinctLt(T x) const {
        // distinct values < x: every block before x's, then a binary search in x's block
        int b = int(lower_bound(maxes.begin(), maxes.end(), x) - maxes.begin());
        long long res = 0;
        for (int k = 0; k < b; k++) res += (long long)keys[k].size();
        if (b < (int)keys.size()) res += lower_bound(keys[b].begin(), keys[b].end(), x) - keys[b].begin();
        return res;
    }

    LEETCODE_NO_SANITIZE static HotVector<T> buildx(const HotVector<T>& a) {  // xor Fenwick over a
        HotVector<T> f(a.size() + 1, 0);
        for (size_t i = 1; i < f.size(); i++) {
            f[i] ^= a[i - 1];
            size_t j = i + (i & -i);
            if (j < f.size()) f[j] ^= f[i];
        }
        return f;
    }

    LEETCODE_NO_SANITIZE static void fenx(HotVector<T>& f, int i, T v) {
        for (i++; i < (int)f.size(); i += i & -i) f[i] ^= v;
    }

    LEETCODE_NO_SANITIZE static T xpre(const HotVector<T>& f, int i) {  // xor over positions 0..i-1
        T res = 0;
        for (; i > 0; i &= i - 1) res ^= f[i];
        return res;
    }

    LEETCODE_NO_SANITIZE T xbelow(T x, bool strict) const {  // xor of the values < x (strict) or <= x (copies count)
        int k = int((strict ? lower_bound(maxes.begin(), maxes.end(), x) : upper_bound(maxes.begin(), maxes.end(),
            x)) - maxes.begin());
        if (k == (int)keys.size()) return xtotal;
        const HotVector<T>& b = keys[k];
        int j = int((strict ? lower_bound(b.begin(), b.end(), x) : upper_bound(b.begin(), b.end(), x)) - b.begin());
        return xpre(fx, k) ^ xpre(fxs[k], j);
    }

    LEETCODE_NO_SANITIZE T xlt(T x) const { return xbelow(x, true); }
    LEETCODE_NO_SANITIZE T xle(T x) const { return xbelow(x, false); }

    LEETCODE_NO_SANITIZE T xorFirst(long long k) const {
        // xor of the k smallest values (copies count): lift over blocks, then inside one
        if (k <= 0) return 0;
        int m = (int)bc.size(), b = 0, j = 0;
        long long before = 0;
        T res = 0;
        for (int step = 1 << (31 - __builtin_clz(m)); step; step >>= 1)
            if (b + step <= m && before + fc[b + step] < k) b += step, before += fc[b], res ^= fx[b];
        const HotVector<long long>& f = fcs[b];
        m = (int)keys[b].size();
        for (int step = 1 << (31 - __builtin_clz(m)); step; step >>= 1)
            if (j + step <= m && before + f[j + step] < k) j += step, before += f[j], res ^= fxs[b][j];
        return (k - before) & 1 ? T(res ^ keys[b][j]) : res;  // k - before copies of the answer's value
    }

    // O(sqrtN amortized) -- add one copy of x
    LEETCODE_NO_SANITIZE void add(T x) {
        addRaw(x, 1);
    }

    // O(sqrtN amortized) -- add cnt copies of val (nothing if cnt <= 0)
    LEETCODE_NO_SANITIZE void addCount(T val, long long cnt) {
        if (cnt > 0) addRaw(val, cnt);
    }

    // O(1 amortized) -- remove everything (fine on an empty set): afterwards it is as if newly built (same constructor
    // arguments), so reuse it instead of building a new one
    LEETCODE_NO_SANITIZE void clear() {
        clearData();
        resetCached();
    }

    // O(logN) -- how many copies of x (0 if x isn't there, e.g. on an empty set)
    LEETCODE_NO_SANITIZE long long count(T x) {
        return countOf(x);
    }

    // O(1) -- how many distinct values (0 if empty)
    LEETCODE_NO_SANITIZE long long countDistinct() {
        return d;
    }

    // O(sqrtN) -- how many distinct values v with lo <= v <= hi (0 if lo > hi)
    LEETCODE_NO_SANITIZE long long countDistinctInValRange(T lo, T hi) {
        if (hi < lo) return 0;
        return distinctLt(hi) - distinctLt(lo) + (countOf(hi) ? 1 : 0);
    }

    // O(logN) -- how many values > x (0 if there are none, e.g. on an empty set)
    LEETCODE_NO_SANITIZE long long countGtX(T x) {
        return n - le(x);
    }

    // O(logN) -- how many values >= x (0 if there are none, e.g. on an empty set)
    LEETCODE_NO_SANITIZE long long countGteX(T x) {
        return n - lt(x);
    }

    // O(logN) -- how many values v with lo <= v <= hi (0 if lo > hi)
    LEETCODE_NO_SANITIZE long long countInValRange(T lo, T hi) {
        return lo <= hi ? le(hi) - lt(lo) : 0;
    }

    // O(logN) -- how many values < x (0 if there are none, e.g. on an empty set)
    LEETCODE_NO_SANITIZE long long countLtX(T x) {
        return lt(x);
    }

    // O(logN) -- how many values <= x (0 if there are none, e.g. on an empty set)
    LEETCODE_NO_SANITIZE long long countLteX(T x) {
        return le(x);
    }

    // O(logN) -- 0-indexed position of the first copy of x in sorted order (= how many values < x); -1 if x is not in
    // the set
    LEETCODE_NO_SANITIZE long long firstIndex(T x) {
        return countOf(x) ? lt(x) : -1;
    }

    // O(logN) -- the value at sorted position i, 0-indexed: kth(0) is the smallest, kth(1) the 2nd smallest,
    // kth(size - 1) the largest (copies count: in {2, 2, 5}, kth(1) is 2); throws out_of_range unless 0 <= i < size
    LEETCODE_NO_SANITIZE T kth(long long i) {
        if (i < 0 || i >= n) throw out_of_range("kth: needs 0 <= i < size");
        return kthAt(i + 1);
    }

    // O(logN) -- largest value < x; ms.NONE if there is none
    LEETCODE_NO_SANITIZE T largestLtX(T x) {
        long long c = lt(x);
        if (!c) return NONE;
        return kthAt(c);
    }

    // O(logN) -- largest value <= x; ms.NONE if there is none
    LEETCODE_NO_SANITIZE T largestLteX(T x) {
        long long c = le(x);
        if (!c) return NONE;
        return kthAt(c);
    }

    // O(logN) -- 0-indexed position of the last copy of x in sorted order (= how many values <= x, minus 1); -1 if x is
    // not in the set
    LEETCODE_NO_SANITIZE long long lastIndex(T x) {
        return countOf(x) ? le(x) - 1 : -1;
    }

    // O(logN) -- largest value; throws out_of_range if empty
    LEETCODE_NO_SANITIZE T max() {
        if (!n) throw out_of_range("max: the set is empty");
        return kthAt(n);
    }

    // O(1 amortized) -- largest difference between two neighbouring distinct values; -1 if fewer than 2 distinct values
    LEETCODE_NO_SANITIZE long long maxGap() {
        if (d < 2) return -1;
        return *gaps.rbegin();
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

    // O(1) -- smallest non-negative integer not in the set (0 if empty)
    LEETCODE_NO_SANITIZE long long mex() {
        return mexV;
    }

    // O(logN) -- smallest value; throws out_of_range if empty
    LEETCODE_NO_SANITIZE T min() {
        if (!n) throw out_of_range("min: the set is empty");
        return kthAt(1);
    }

    // O(1 amortized) -- smallest difference between two values in the set (0 if some value has 2+ copies); -1 if fewer
    // than 2 values
    LEETCODE_NO_SANITIZE long long minAdjacentDiff() {
        if (n < 2) return -1;
        if (dups) return 0LL;
        return *gaps.begin();
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

    // O(sqrtN amortized) -- remove one copy of x if present; returns how many were removed (0 or 1: 0 if x isn't there,
    // e.g. on an empty set)
    LEETCODE_NO_SANITIZE long long remove(T x) {
        if (!count(x)) return 0;
        addRaw(x, -1);
        return 1;
    }

    // O(sqrtN amortized) -- remove every copy of val; returns how many were removed (0 if val isn't there, e.g. on an
    // empty set)
    LEETCODE_NO_SANITIZE long long removeAll(T val) {
        long long k = count(val);
        if (k) addRaw(val, -k);
        return k;
    }

    // O(sqrtN amortized) -- remove min(cnt, count(val)) copies of val; returns how many were removed (0 if val isn't
    // there, e.g. on an empty set)
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

    // O(1) -- how many values (copies count; 0 if empty)
    LEETCODE_NO_SANITIZE long long size() {
        return n;
    }

    // O(logN) -- smallest value > x; ms.NONE if there is none
    LEETCODE_NO_SANITIZE T smallestGtX(T x) {
        long long c = le(x);
        if (c == n) return NONE;
        return kthAt(c + 1);
    }

    // O(logN) -- smallest value >= x; ms.NONE if there is none
    LEETCODE_NO_SANITIZE T smallestGteX(T x) {
        long long c = lt(x);
        if (c == n) return NONE;
        return kthAt(c + 1);
    }

    // O(1) -- sum of |v - medianLow()| over all values (min total moves to make all equal); 0 if empty
    LEETCODE_NO_SANITIZE S sumAbsDiffToMedian() {
        if (!n) return 0;
        const Info& m = low;
        return S(m.v) * m.before - m.sb + (total - m.sb - S(m.v) * m.c) - S(m.v) * (n - m.before - m.c);
    }

    // O(logN) -- sum of |v - x| over all values (0 if empty)
    LEETCODE_NO_SANITIZE S sumAbsDiffToX(T x) {
        long long c = lt(x);
        S s = slt(x);
        return S(x) * c - s + (total - s) - S(x) * (n - c);
    }

    // O(1) -- sum of all values (0 if empty)
    LEETCODE_NO_SANITIZE S sumAll() {
        return total;
    }

    // O(logN) -- sum of the values > x (0 if there are none, e.g. on an empty set)
    LEETCODE_NO_SANITIZE S sumGtX(T x) {
        return total - sle(x);
    }

    // O(logN) -- sum of the values >= x (0 if there are none, e.g. on an empty set)
    LEETCODE_NO_SANITIZE S sumGteX(T x) {
        return total - slt(x);
    }

    // O(logN) -- sum of the values v with lo <= v <= hi (0 if lo > hi)
    LEETCODE_NO_SANITIZE S sumInValRange(T lo, T hi) {
        return lo <= hi ? sle(hi) - slt(lo) : S(0);
    }

    // O(logN) -- sum of the kFrom-th through kTo-th largest values; RANKS, 1-indexed and inclusive: (1, 1) is just the
    // largest, (5, 8) the 5th, 6th, 7th and 8th largest, (1, size) every value (copies count); throws out_of_range
    // unless 1 <= kFrom <= kTo <= size
    LEETCODE_NO_SANITIZE S sumKthLargestRange(long long kFrom, long long kTo) {
        if (kFrom < 1 || kFrom > kTo
            || kTo > n) throw out_of_range("sumKthLargestRange: needs 1 <= kFrom <= kTo <= size");
        return sumFirst(n - kFrom + 1) - sumFirst(n - kTo);
    }

    // O(logN) -- sum of the kFrom-th through kTo-th smallest values; RANKS, 1-indexed and inclusive: (1, 1) is just the
    // smallest, (2, 4) the 2nd, 3rd and 4th smallest, (1, size) every value (copies count); throws out_of_range unless
    // 1 <= kFrom <= kTo <= size
    LEETCODE_NO_SANITIZE S sumKthSmallestRange(long long kFrom, long long kTo) {
        if (kFrom < 1 || kFrom > kTo
            || kTo > n) throw out_of_range("sumKthSmallestRange: needs 1 <= kFrom <= kTo <= size");
        return sumFirst(kTo) - sumFirst(kFrom - 1);
    }

    // O(logN) -- sum of the k largest values; k is a COUNT, not an index: k = 0 takes no values (returns 0), k = 1 just
    // the largest, k = size every value (copies count: in {2, 5, 5}, k = 2 takes 5 and 5); throws out_of_range unless 0
    // <= k <= size
    LEETCODE_NO_SANITIZE S sumLargestK(long long k) {
        if (k < 0 || k > n) throw out_of_range("sumLargestK: needs 0 <= k <= size");
        return total - sumFirst(n - k);
    }

    // O(logN) -- sum of the values < x (0 if there are none, e.g. on an empty set)
    LEETCODE_NO_SANITIZE S sumLtX(T x) {
        return slt(x);
    }

    // O(logN) -- sum of the values <= x (0 if there are none, e.g. on an empty set)
    LEETCODE_NO_SANITIZE S sumLteX(T x) {
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
    LEETCODE_NO_SANITIZE T xorOfAll() {
        return xtotal;
    }

    // O(logN) -- xor of the values > x (copies count; 0 if there are none)
    LEETCODE_NO_SANITIZE T xorOfGtX(T x) {
        return xtotal ^ xle(x);
    }

    // O(logN) -- xor of the values >= x (copies count; 0 if there are none)
    LEETCODE_NO_SANITIZE T xorOfGteX(T x) {
        return xtotal ^ xlt(x);
    }

    // O(logN) -- xor of the values v with lo <= v <= hi (copies count; 0 if lo > hi)
    LEETCODE_NO_SANITIZE T xorOfInValRange(T lo, T hi) {
        return lo <= hi ? T(xle(hi) ^ xlt(lo)) : T(0);
    }

    // O(logN) -- xor of the kFrom-th through kTo-th largest values; RANKS, 1-indexed and inclusive: (1, 1) is just the
    // largest, (5, 8) the 5th, 6th, 7th and 8th largest, (1, size) every value (copies count); throws out_of_range
    // unless 1 <= kFrom <= kTo <= size
    LEETCODE_NO_SANITIZE T xorOfKthLargestRange(long long kFrom, long long kTo) {
        if (kFrom < 1 || kFrom > kTo
            || kTo > n) throw out_of_range("xorOfKthLargestRange: needs 1 <= kFrom <= kTo <= size");
        return xorFirst(n - kFrom + 1) ^ xorFirst(n - kTo);
    }

    // O(logN) -- xor of the kFrom-th through kTo-th smallest values; RANKS, 1-indexed and inclusive: (1, 1) is just the
    // smallest, (2, 4) the 2nd, 3rd and 4th smallest, (1, size) every value (copies count); throws out_of_range unless
    // 1 <= kFrom <= kTo <= size
    LEETCODE_NO_SANITIZE T xorOfKthSmallestRange(long long kFrom, long long kTo) {
        if (kFrom < 1 || kFrom > kTo
            || kTo > n) throw out_of_range("xorOfKthSmallestRange: needs 1 <= kFrom <= kTo <= size");
        return xorFirst(kTo) ^ xorFirst(kFrom - 1);
    }

    // O(logN) -- xor of the k largest values; k is a COUNT, not an index: k = 0 takes no values (returns 0), k = 1 just
    // the largest, k = size every value (copies count: in {2, 5, 5}, k = 2 takes 5 and 5); throws out_of_range unless 0
    // <= k <= size
    LEETCODE_NO_SANITIZE T xorOfLargestK(long long k) {
        if (k < 0 || k > n) throw out_of_range("xorOfLargestK: needs 0 <= k <= size");
        return xtotal ^ xorFirst(n - k);
    }

    // O(logN) -- xor of the values < x (copies count; 0 if there are none)
    LEETCODE_NO_SANITIZE T xorOfLtX(T x) {
        return xlt(x);
    }

    // O(logN) -- xor of the values <= x (copies count; 0 if there are none)
    LEETCODE_NO_SANITIZE T xorOfLteX(T x) {
        return xle(x);
    }

    // O(logN) -- xor of the k smallest values; k is a COUNT, not an index: k = 0 takes no values (returns 0), k = 1
    // just the smallest, k = size every value (copies count: in {2, 2, 5}, k = 2 takes 2 and 2); throws out_of_range
    // unless 0 <= k <= size
    LEETCODE_NO_SANITIZE T xorOfSmallestK(long long k) {
        if (k < 0 || k > n) throw out_of_range("xorOfSmallestK: needs 0 <= k <= size");
        return xorFirst(k);
    }
};
