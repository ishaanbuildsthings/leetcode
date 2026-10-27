// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/sets/fenwick-with-sums-xor-mex/template.cpp
// @operations: add addCount clear count countDistinct countDistinctInValRange countGtX countGteX countInValRange countLtX countLteX firstIndex kth largestLtX largestLteX lastIndex max medianHigh medianLow mex min pop popMax popMin remove removeAll removeCount removeInValRange size smallestGtX smallestGteX sumAbsDiffToMedian sumAbsDiffToX sumAll sumGtX sumGteX sumInValRange sumKthLargestRange sumKthSmallestRange sumLargestK sumLtX sumLteX sumSmallestK xorOfAll xorOfGtX xorOfGteX xorOfInValRange xorOfKthLargestRange xorOfKthSmallestRange xorOfLargestK xorOfLtX xorOfLteX xorOfSmallestK
// @data-structure-type: fenwick
// @values: offline
// @keys: numbers
// @tracks: none
// @complexities:
//   add: log(N)
//   addCount: log(N)
//   clear: N
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
//   medianHigh: log(N)
//   medianLow: log(N)
//   mex: log(N)
//   min: log(N)
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
//   node: cnt[1*N] fc[1*N] fp[1*N] fs[1*N] fx[1*N]
//   tags: none
//   other: vals[1*N]
//   note: N = how many distinct values were given to the constructor; the arrays are allocated once

// Ordered multiset over values known ahead of time (offline): Fenwick trees over the sorted distinct values you pass
// to the constructor, one counting copies, one summing them, one marking which values are present (for mex), one xor-ing the values with an odd count.
// k-th / sum of the k smallest walk down by binary lifting. The constructor only learns which values can appear (it
// compresses them); the multiset starts EMPTY. Every value you add must be one of them; query arguments (x, lo, hi)
// can be anything. T: int, long long, ...; sums in S (long long for small T).
template <typename T>
struct FenwickMultiset {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    vector<T> vals;  // the sorted distinct values
    int m, top, z, run;
    vector<long long> cnt, fc, fp;  // copies per value; Fenwick of copies; Fenwick of present values
    vector<S> fs;  // Fenwick of copies * value
    vector<T> fx;  // Fenwick of xor over the values with an odd count
    long long n = 0, d = 0;
    struct Info { T v; long long before, c; S sb; };  // a value, copies before it, its copies, sum before it
    T xtotal = 0;  // xor of all values (copies count)
    S total = 0;

    // O(N log N) -- allValuesThatWillEverBeInsertedForOfflineCompression: every value you will EVER add (any order, duplicates fine), only to compress values; this does NOT add them, the multiset starts empty; N = distinct values
    explicit FenwickMultiset(vector<T> allValuesThatWillEverBeInsertedForOfflineCompression) : vals(move(allValuesThatWillEverBeInsertedForOfflineCompression)) {
        sort(vals.begin(), vals.end());
        vals.erase(unique(vals.begin(), vals.end()), vals.end());
        m = (int)vals.size();
        top = m ? 1 << (31 - __builtin_clz(m)) : 0;  // highest power of two <= m, for binary lifting
        cnt.assign(m, 0), fc.assign(m + 1, 0);
        fp.assign(m + 1, 0);
        fs.assign(m + 1, 0);
        fx.assign(m + 1, 0);
        z = int(lower_bound(vals.begin(), vals.end(), T(0)) - vals.begin());
        run = 0;
        while (z + run < m && vals[z + run] == T(run)) run++;  // vals[z .. z + run - 1] = 0, 1, ..., run - 1
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

    long long insert(T x, long long c) {  // returns x's new count
        int i = lowerIdx(x);  // x must be one of the given values
        long long old = cnt[i];
        cnt[i] += c;
        fen(fc, i, c);
        fen(fs, i, S(c) * x);
        if (c & 1)
            for (int j = i + 1; j <= m; j += j & -j) fx[j] ^= x;  // x's parity flips
        if (!old) fen(fp, i, 1LL), d++;
        else if (!cnt[i]) fen(fp, i, -1LL), d--;
        return cnt[i];
    }

    long long lt(T x) { return pre(fc, lowerIdx(x)); }
    long long le(T x) { return pre(fc, upperIdx(x)); }

    long long countOf(T x) const {
        int i = lowerIdx(x);
        return i < m && vals[i] == x ? cnt[i] : 0;
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
    long long findMex() {  // smallest non-negative integer not in the set
        if (!run) return 0;  // 0 is not even a possible value
        // first absent position p >= z: lift while the number of absent positions so far stays at the count before z
        long long a0 = z - pre(fp, z), acc = 0;
        int pos = 0;
        for (int step = top; step; step >>= 1)
            if (pos + step <= m && (pos + step) - (acc + fp[pos + step]) <= a0) pos += step, acc += fp[pos];
        return std::min<long long>(pos - z, run);
    }

    void addRaw(T x, long long c) {  // c copies of x (c < 0 removes)
        n += c;
        total += S(c) * x;
        if (c & 1) xtotal ^= x;  // an odd number of copies flips x in or out of the xor of everything
        insert(x, c);
    }

    S sumFirst(long long k) {  // sum of the k smallest values
        if (k <= 0) return 0;
        Info f = kthInfo(k);
        return f.sb + S(k - f.before) * f.v;
    }

    void resetCached() {  // nothing counted: as newly built
        n = d = 0;
        total = 0;
        xtotal = 0;
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
                for (int j = i + 1; j <= m; j += j & -j) fc[j] = 0, fs[j] = 0, fp[j] = 0, fx[j] = 0;
            }
        } else {
            fill(cnt.begin(), cnt.end(), 0), fill(fc.begin(), fc.end(), 0), fill(fs.begin(), fs.end(), 0), fill(fp.begin(), fp.end(), 0), fill(fx.begin(), fx.end(), 0);
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
        int pos = 0;
        long long before = 0;
        T res = 0;
        for (int step = top; step; step >>= 1)
            if (pos + step <= m && before + fc[pos + step] < k) pos += step, before += fc[pos], res ^= fx[pos];
        return (k - before) & 1 ? T(res ^ vals[pos]) : res;  // k - before copies of the answer's value
    }

    // O(logN) -- add one copy of x
    void add(T x) {
        addRaw(x, 1);
    }

    // O(logN) -- add cnt copies of val (nothing if cnt <= 0)
    void addCount(T val, long long cnt) {
        if (cnt > 0) addRaw(val, cnt);
    }

    // O(N) -- remove everything: afterwards it is as if newly built (same constructor arguments), so reuse it instead of building a new one
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

    // O(logN) -- 0-indexed position of the first copy of x in sorted order (= how many values < x); -1 if x is not in the set
    long long firstIndex(T x) {
        return countOf(x) ? lt(x) : -1;
    }

    // O(logN) -- the value at sorted position i (0-indexed: kth(0) is the min); throws out_of_range unless 0 <= i < size
    T kth(long long i) {
        if (i < 0 || i >= n) throw out_of_range("kth: needs 0 <= i < size");
        return kthAt(i + 1);
    }

    // O(logN) -- largest value < x; nullopt if there is none
    optional<T> largestLtX(T x) {
        long long c = lt(x);
        if (!c) return nullopt;
        return kthAt(c);
    }

    // O(logN) -- largest value <= x; nullopt if there is none
    optional<T> largestLteX(T x) {
        long long c = le(x);
        if (!c) return nullopt;
        return kthAt(c);
    }

    // O(logN) -- 0-indexed position of the last copy of x in sorted order (= how many values <= x, minus 1); -1 if x is not in the set
    long long lastIndex(T x) {
        return countOf(x) ? le(x) - 1 : -1;
    }

    // O(logN) -- largest value; nullopt if empty
    optional<T> max() {
        if (!n) return nullopt;
        return kthAt(n);
    }

    // O(logN) -- upper median: the (floor(size/2) + 1)-th smallest value; nullopt if empty
    optional<T> medianHigh() {
        if (!n) return nullopt;
        return kthAt(n / 2 + 1);
    }

    // O(logN) -- lower median: the ceil(size/2)-th smallest value; nullopt if empty
    optional<T> medianLow() {
        if (!n) return nullopt;
        return kthAt((n + 1) / 2);
    }

    // O(logN) -- smallest non-negative integer not in the set
    long long mex() {
        return findMex();
    }

    // O(logN) -- smallest value; nullopt if empty
    optional<T> min() {
        if (!n) return nullopt;
        return kthAt(1);
    }

    // O(logN) -- remove and return the value at sorted position i (0-indexed: pop(0) is popMin()); throws out_of_range unless 0 <= i < size
    T pop(long long i) {
        if (i < 0 || i >= n) throw out_of_range("pop: needs 0 <= i < size");
        T v = kthAt(i + 1);
        addRaw(v, -1);
        return v;
    }

    // O(logN) -- remove and return the largest value; nullopt if empty
    optional<T> popMax() {
        if (!n) return nullopt;
        T v = kthAt(n);
        addRaw(v, -1);
        return v;
    }

    // O(logN) -- remove and return the smallest value; nullopt if empty
    optional<T> popMin() {
        if (!n) return nullopt;
        T v = kthAt(1);
        addRaw(v, -1);
        return v;
    }

    // O(logN) -- remove one copy of x if present; returns how many were removed (0 or 1)
    long long remove(T x) {
        if (!count(x)) return 0;
        addRaw(x, -1);
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

    // O(logN) -- smallest value > x; nullopt if there is none
    optional<T> smallestGtX(T x) {
        long long c = le(x);
        if (c == n) return nullopt;
        return kthAt(c + 1);
    }

    // O(logN) -- smallest value >= x; nullopt if there is none
    optional<T> smallestGteX(T x) {
        long long c = lt(x);
        if (c == n) return nullopt;
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

    // O(logN) -- sum of the kFrom-th..kTo-th largest values (1-indexed, inclusive; (5, 8) = 5th..8th biggest); throws out_of_range unless 1 <= kFrom <= kTo <= size
    S sumKthLargestRange(long long kFrom, long long kTo) {
        if (kFrom < 1 || kFrom > kTo || kTo > n) throw out_of_range("sumKthLargestRange: needs 1 <= kFrom <= kTo <= size");
        return sumFirst(n - kFrom + 1) - sumFirst(n - kTo);
    }

    // O(logN) -- sum of the kFrom-th..kTo-th smallest values (1-indexed, inclusive); throws out_of_range unless 1 <= kFrom <= kTo <= size
    S sumKthSmallestRange(long long kFrom, long long kTo) {
        if (kFrom < 1 || kFrom > kTo || kTo > n) throw out_of_range("sumKthSmallestRange: needs 1 <= kFrom <= kTo <= size");
        return sumFirst(kTo) - sumFirst(kFrom - 1);
    }

    // O(logN) -- sum of the k largest values; throws out_of_range unless 0 <= k <= size
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

    // O(logN) -- sum of the k smallest values; throws out_of_range unless 0 <= k <= size
    S sumSmallestK(long long k) {
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

    // O(logN) -- xor of the kFrom-th..kTo-th largest values (1-indexed, inclusive); throws out_of_range unless 1 <= kFrom <= kTo <= size
    T xorOfKthLargestRange(long long kFrom, long long kTo) {
        if (kFrom < 1 || kFrom > kTo || kTo > n) throw out_of_range("xorOfKthLargestRange: needs 1 <= kFrom <= kTo <= size");
        return xorFirst(n - kFrom + 1) ^ xorFirst(n - kTo);
    }

    // O(logN) -- xor of the kFrom-th..kTo-th smallest values (1-indexed, inclusive); throws out_of_range unless 1 <= kFrom <= kTo <= size
    T xorOfKthSmallestRange(long long kFrom, long long kTo) {
        if (kFrom < 1 || kFrom > kTo || kTo > n) throw out_of_range("xorOfKthSmallestRange: needs 1 <= kFrom <= kTo <= size");
        return xorFirst(kTo) ^ xorFirst(kFrom - 1);
    }

    // O(logN) -- xor of the k largest values (copies count); throws out_of_range unless 0 <= k <= size
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

    // O(logN) -- xor of the k smallest values (copies count); throws out_of_range unless 0 <= k <= size
    T xorOfSmallestK(long long k) {
        if (k < 0 || k > n) throw out_of_range("xorOfSmallestK: needs 0 <= k <= size");
        return xorFirst(k);
    }
};
