// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/sets/fenwick-with-sums-minmax/template.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: add addCount clear count countDistinct countGtX countGteX countInValRange countLtX countLteX firstIndex kth largestLtX largestLteX lastIndex max medianHigh medianLow min pop popMax popMin remove removeAll removeCount removeInValRange size smallestGtX smallestGteX sumAbsDiffToMedian sumAbsDiffToX sumAll sumGtX sumGteX sumInValRange sumKthLargestRange sumKthSmallestRange sumLargestK sumLtX sumLteX sumSmallestK
// @data-structure-type: fenwick
// @values: offline
// @keys: numbers
// @tracks: minmax
// @complexities:
//   add: log(N)
//   addCount: log(N)
//   clear: 1 amortized
//   count: log(N)
//   countDistinct: 1
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
//   max: 1
//   medianHigh: log(N)
//   medianLow: log(N)
//   min: 1
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
//   build: N*log(N)
// @memory:
//   layout: none
//   node: cnt[1*N] fc[1*N] fs[1*N]
//   tags: none
//   other: vals[1*N]
//   note: N = how many distinct values were given to the constructor; the arrays are allocated once. C++ integers also keep a hash table of at most 8*N ints from value to position

// Ordered multiset over values known ahead of time (offline): Fenwick trees over the sorted distinct values you pass
// to the constructor, one counting copies, one summing them.
// k-th / sum of the k smallest walk down by binary lifting. The constructor only learns which values can appear (it
// compresses them); the multiset starts EMPTY. Every value you add must be one of them; query arguments (x, lo, hi)
// can be anything. T: int, long long, ...; sums in S (long long for small T).
template <typename T>
struct FenwickMultiset {
    template <class K>
    static K noneOf() {  // the lowest value of K, part by part for pairs and tuples
        if constexpr (is_arithmetic_v<K>) return numeric_limits<K>::lowest();
        else return apply([](auto... parts) { return K{noneOf<decltype(parts)>()...}; }, K{});
    }
    static inline const T NONE = noneOf<T>();  // what largestLtX, smallestGtX, ... return when nothing qualifies: compare with ms.NONE

    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    vector<T> vals;  // the sorted distinct values
    int m, top;
    vector<long long> cnt, fc;  // copies per value; Fenwick of copies
    vector<S> fs;  // Fenwick of copies * value
    vector<int> slotOf;  // integer values only: hash table from a value to its position in vals, -1 for an empty slot
    unsigned long long hashMultiplier = 1;  // random per instance, so no fixed input can force collisions
    int hashShift = 0;
    unsigned hashMask = 0;
    long long n = 0, d = 0;
    struct Info { T v; long long before, c; S sb; };  // a value, copies before it, its copies, sum before it
    T mn{}, mx{};  // kept current by addRaw while n > 0
    S total = 0;

    // O(N log N) -- allValuesThatWillEverBeInsertedForOfflineCompression: every value you will EVER add (any order, duplicates fine), only to compress values; this does NOT add them, the multiset starts empty; N = distinct values
    explicit FenwickMultiset(vector<T> allValuesThatWillEverBeInsertedForOfflineCompression) : vals(move(allValuesThatWillEverBeInsertedForOfflineCompression)) {
        sort(vals.begin(), vals.end());
        vals.erase(unique(vals.begin(), vals.end()), vals.end());
        m = (int)vals.size();
        top = m ? 1 << (31 - __builtin_clz(m)) : 0;  // highest power of two <= m, for binary lifting
        cnt.assign(m, 0), fc.assign(m + 1, 0);
        fs.assign(m + 1, 0);
        if constexpr (is_integral_v<T>) {
            unsigned long long seed = chrono::steady_clock::now().time_since_epoch().count() ^ (unsigned long long)(uintptr_t)this;
            seed = (seed ^ (seed >> 30)) * 0xBF58476D1CE4E5B9ULL;
            seed = (seed ^ (seed >> 27)) * 0x94D049BB133111EBULL;
            hashMultiplier = (seed ^ (seed >> 31)) | 1;
            int bits = 3;
            while ((1LL << bits) < 4LL * m) bits++;
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
    void fen(vector<V>& f, int i, V v) {
        for (i++; i <= m; i += i & -i) f[i] += v;
    }

    template <class V>
    V pre(const vector<V>& f, int i) const {  // f's total over positions 0..i-1
        V s = 0;
        for (; i > 0; i &= i - 1) s += f[i];
        return s;
    }

    int lowerIdx(T x) const { return int(lower_bound(vals.begin(), vals.end(), x) - vals.begin()); }
    int upperIdx(T x) const { return int(upper_bound(vals.begin(), vals.end(), x) - vals.begin()); }

    unsigned hashOf(T x) const {
        return unsigned((unsigned long long)(long long)x * hashMultiplier >> hashShift);
    }
    int rankOf(T x) const {  // x's position in vals, or m if it is not a given value; expected O(1) for integers
        if constexpr (is_integral_v<T>) {
            for (unsigned h = hashOf(x);; h = (h + 1) & hashMask) {
                int i = slotOf[h];
                if (i < 0) return m;
                if (vals[i] == x) return i;
            }
        } else {
            int i = lowerIdx(x);
            return i < m && vals[i] == x ? i : m;
        }
    }

    long long insert(T x, long long c) {  // returns x's new count
        int i = rankOf(x);
        if (i == m) i = lowerIdx(x);  // x must be one of the given values
        return insertAt(i, x, c);
    }

    long long insertAt(int i, T x, long long c) {  // i is x's position in vals; returns x's new count
        long long old = cnt[i];
        cnt[i] += c;
        fen(fc, i, c);
        fen(fs, i, S(c) * x);
        if (!old) d++;
        else if (!cnt[i]) d--;
        return cnt[i];
    }

    long long lt(T x) { return pre(fc, lowerIdx(x)); }
    long long le(T x) { return pre(fc, upperIdx(x)); }

    long long countOf(T x) const {
        int i = rankOf(x);
        return i < m ? cnt[i] : 0;
    }
    S slt(T x) { return pre(fs, lowerIdx(x)); }
    S sle(T x) { return pre(fs, upperIdx(x)); }

    T kthAt(long long k) {  // binary lifting: the largest prefix with fewer than k copies ends right before the answer
        int pos = 0;
        for (int step = top; step; step >>= 1)
            if (pos + step <= m && fc[pos + step] < k) pos += step, k -= fc[pos];
        return vals[pos];
    }
    Info kthInfo(long long k) {  // the k-th smallest, copies before it, its copies, sum before it
        int pos = 0;
        long long before = 0;
        S acc = 0;
        for (int step = top; step; step >>= 1)
            if (pos + step <= m && before + fc[pos + step] < k) pos += step, before += fc[pos], acc += fs[pos];
        return {vals[pos], before, cnt[pos], acc};
    }

    void addRaw(T x, long long c) {  // c copies of x (c < 0 removes); keeps min / max current
        int i = rankOf(x);
        addAt(i == m ? lowerIdx(x) : i, x, c);
    }

    void addAt(int i, T x, long long c) {  // addRaw, with x's position known
        n += c;
        total += S(c) * x;
        long long f = insertAt(i, x, c);  // x's new count
        if (c > 0) {
            if (n == c) {  // the set was empty
                mn = mx = x;
                return;
            }
            if (x < mn) mn = x;
            if (x > mx) mx = x;
        } else {
            if (!n) return;
            if (!f) {  // x is gone: it may have been the min / max
                if (x == mn) mn = kthAt(1);
                if (x == mx) mx = kthAt(n);
            }
        }
    }

    S sumFirst(long long k) {  // sum of the k smallest values
        if (k <= 0) return 0;
        Info f = kthInfo(k);
        return f.sb + S(k - f.before) * f.v;
    }

    void resetCached() {  // nothing counted: as newly built
        n = d = 0;
        total = 0;
    }

    void clearData() {  // few distinct values present: zero only their slots and Fenwick paths, else wipe in bulk
        if (d * (65 - __builtin_clzll((unsigned long long)top | 1)) * 8 < m) {
            vector<int> slots;
            for (long long k = 1; k <= n;) {  // the slot of the k-th smallest, by binary lifting; then skip its copies
                int pos = 0;
                long long before = 0;
                for (int step = top; step; step >>= 1)
                    if (pos + step <= m && before + fc[pos + step] < k) pos += step, before += fc[pos];
                slots.push_back(pos);
                k = before + cnt[pos] + 1;
            }
            for (int i : slots) {
                cnt[i] = 0;
                for (int j = i + 1; j <= m; j += j & -j) fc[j] = 0, fs[j] = 0;
            }
        } else {
            fill(cnt.begin(), cnt.end(), 0), fill(fc.begin(), fc.end(), 0), fill(fs.begin(), fs.end(), 0);
        }
    }

    // O(logN) -- add one copy of x
    void add(T x) {
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
    long long count(T x) {
        return countOf(x);
    }

    // O(1) -- how many distinct values
    long long countDistinct() {
        return d;
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
    T kth(long long i) {
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

    // O(1) -- largest value; throws out_of_range if empty
    T max() {
        if (!n) throw out_of_range("max: the set is empty");
        return mx;
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

    // O(1) -- smallest value; throws out_of_range if empty
    T min() {
        if (!n) throw out_of_range("min: the set is empty");
        return mn;
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
        T v = mx;
        addRaw(v, -1);
        return v;
    }

    // O(logN) -- remove and return the smallest value; throws out_of_range if empty
    T popMin() {
        if (!n) throw out_of_range("popMin: the set is empty");
        T v = mn;
        addRaw(v, -1);
        return v;
    }

    // O(logN) -- remove one copy of x if present; returns how many were removed (0 or 1)
    long long remove(T x) {
        int i = rankOf(x);  // one lookup for both the check and the removal
        if (i == m || !cnt[i]) return 0;
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
    long long size() {
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
    S sumLargestK(long long k) {
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
    S sumSmallestK(long long k) {
        if (k < 0 || k > n) throw out_of_range("sumSmallestK: needs 0 <= k <= size");
        return sumFirst(k);
    }
};
