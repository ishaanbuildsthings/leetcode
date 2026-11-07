// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/sets/fenwick-with-mex-minmax-medians/template.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: add addCount clear count countDistinct countDistinctInValRange countGtX countGteX countInValRange countLtX countLteX firstIndex kth largestLtX largestLteX lastIndex max medianHigh medianLow mex min pop popMax popMin remove removeAll removeCount removeInValRange size smallestGtX smallestGteX
// @data-structure-type: fenwick
// @values: offline
// @keys: numbers
// @tracks: minmax medians
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
//   max: 1
//   medianHigh: 1
//   medianLow: 1
//   mex: log(N)
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
//   build: N*log(N)
// @memory:
//   layout: none
//   node: cnt[1*N] fc[1*N] fp[1*N]
//   tags: none
//   other: vals[1*N]
//   note: N = how many distinct values were given to the constructor; the arrays are allocated once. C++ integers also keep a hash table of at most 8*N ints from value to position

// Ordered multiset over values known ahead of time (offline): Fenwick trees over the sorted distinct values you pass
// to the constructor, one counting copies, one marking which values are present (for mex).
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
    int m, top, z, run;
    vector<long long> cnt, fc, fp;  // copies per value; Fenwick of copies; Fenwick of present values
    vector<int> slotOf;  // integer values only: hash table from a value to its position in vals, -1 for an empty slot
    unsigned long long hashMultiplier = 1;  // random per instance, so no fixed input can force collisions
    int hashShift = 0;
    unsigned hashMask = 0;
    long long n = 0, d = 0;
    struct Info { T v; long long before, c; };  // a value, copies before it, its copies
    T mn{}, mx{};  // kept current by addRaw while n > 0
    Info low{}, high{};  // both medians, kept current by addRaw while n > 0

    // O(N log N) -- allValuesThatWillEverBeInsertedForOfflineCompression: every value you will EVER add (any order, duplicates fine), only to compress values; this does NOT add them, the multiset starts empty; N = distinct values
    explicit FenwickMultiset(vector<T> allValuesThatWillEverBeInsertedForOfflineCompression) : vals(move(allValuesThatWillEverBeInsertedForOfflineCompression)) {
        sort(vals.begin(), vals.end());
        vals.erase(unique(vals.begin(), vals.end()), vals.end());
        m = (int)vals.size();
        top = m ? 1 << (31 - __builtin_clz(m)) : 0;  // highest power of two <= m, for binary lifting
        cnt.assign(m, 0), fc.assign(m + 1, 0);
        fp.assign(m + 1, 0);
        z = int(lower_bound(vals.begin(), vals.end(), T(0)) - vals.begin());
        run = 0;
        while (z + run < m && vals[z + run] == T(run)) run++;  // vals[z .. z + run - 1] = 0, 1, ..., run - 1
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
        if (!old) fen(fp, i, 1LL), d++;
        else if (!cnt[i]) fen(fp, i, -1LL), d--;
        return cnt[i];
    }

    long long lt(T x) { return pre(fc, lowerIdx(x)); }
    long long le(T x) { return pre(fc, upperIdx(x)); }

    long long countOf(T x) const {
        int i = rankOf(x);
        return i < m ? cnt[i] : 0;
    }

    T kthAt(long long k) {  // binary lifting: the largest prefix with fewer than k copies ends right before the answer
        int pos = 0;
        for (int step = top; step; step >>= 1)
            if (pos + step <= m && fc[pos + step] < k) pos += step, k -= fc[pos];
        return vals[pos];
    }
    Info kthInfo(long long k) {  // the k-th smallest, copies before it, its copies
        int pos = 0;
        long long before = 0;
        for (int step = top; step; step >>= 1)
            if (pos + step <= m && before + fc[pos + step] < k) pos += step, before += fc[pos];
        return {vals[pos], before, cnt[pos]};
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

    void addRaw(T x, long long c) {  // c copies of x (c < 0 removes); keeps min / max, both medians current
        int i = rankOf(x);
        addAt(i == m ? lowerIdx(x) : i, x, c);
    }

    void addAt(int i, T x, long long c) {  // addRaw, with x's position known
        n += c;
        long long f = insertAt(i, x, c);  // x's new count
        if (c > 0) {
            if (n == c) {  // the set was empty
                mn = mx = x;
                low = high = Info{x, 0, c};
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

    void resetCached() {  // nothing counted: as newly built
        n = d = 0;
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
                for (int j = i + 1; j <= m; j += j & -j) fc[j] = 0, fp[j] = 0;
            }
        } else {
            fill(cnt.begin(), cnt.end(), 0), fill(fc.begin(), fc.end(), 0), fill(fp.begin(), fp.end(), 0);
        }
    }

    long long distinctLt(T x) { return pre(fp, lowerIdx(x)); }  // distinct values < x: the Fenwick of present values

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

    // O(1) -- upper median: the (floor(size/2) + 1)-th smallest value; throws out_of_range if empty
    T medianHigh() {
        if (!n) throw out_of_range("medianHigh: the set is empty");
        return high.v;
    }

    // O(1) -- lower median: the ceil(size/2)-th smallest value; throws out_of_range if empty
    T medianLow() {
        if (!n) throw out_of_range("medianLow: the set is empty");
        return low.v;
    }

    // O(logN) -- smallest non-negative integer not in the set
    long long mex() {
        return findMex();
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
};
