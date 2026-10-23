// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/sets/fenwick-with-sums-mex/template.cpp
// @operations: add addCount count countDistinct countGtX countGteX countInValRange countLtX countLteX kthLargest kthSmallest largestLtX largestLteX max medianHigh medianLow mex min popMax popMin remove removeAll removeCount size smallestGtX smallestGteX sumAbsDiffToMedian sumAbsDiffToX sumAll sumGtX sumGteX sumInValRange sumKthLargestRange sumKthSmallestRange sumLargestK sumLtX sumLteX sumSmallestK
// @data-structure-type: fenwick
// @values: offline
// @complexities:
//   add: log(N)
//   addCount: log(N)
//   count: log(N)
//   countDistinct: 1
//   countGtX: log(N)
//   countGteX: log(N)
//   countInValRange: log(N)
//   countLtX: log(N)
//   countLteX: log(N)
//   kthLargest: log(N)
//   kthSmallest: log(N)
//   largestLtX: log(N)
//   largestLteX: log(N)
//   max: 1
//   medianHigh: 1 amortized
//   medianLow: 1 amortized
//   mex: 1 amortized
//   min: 1
//   popMax: log(N)
//   popMin: log(N)
//   remove: log(N)
//   removeAll: log(N)
//   removeCount: log(N)
//   size: 1
//   smallestGtX: log(N)
//   smallestGteX: log(N)
//   sumAbsDiffToMedian: 1 amortized
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
//   node: cnt[1*N] fc[1*N] fp[1*N] fs[1*N]
//   tags: none
//   other: vals[1*N]
//   note: N = how many distinct values were given to the constructor; the arrays are allocated once

// Ordered multiset over values known ahead of time (offline): Fenwick trees over the sorted distinct values you pass
// to the constructor, one counting copies, one summing them, one marking which values are present (for mex).
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
    long long n = 0, d = 0;
    struct Info { T v; long long before, c; S sb; };  // a value, copies before it, its copies, sum before it
    T mn{}, mx{};  // kept current by addRaw while n > 0
    bool med = false;  // medians (low, high) are tracked from the first median query on
    Info low{}, high{};
    long long mexV = -1;  // -1 until mex() is first called, then kept current
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

    void insert(T x, long long c) {
        int i = lowerIdx(x);  // x must be one of the given values
        long long old = cnt[i];
        cnt[i] += c;
        fen(fc, i, c);
        fen(fs, i, S(c) * x);
        if (!old) fen(fp, i, 1LL), d++;
        else if (!cnt[i]) fen(fp, i, -1LL), d--;
    }

    long long lt(T x) { return pre(fc, lowerIdx(x)); }
    long long le(T x) { return pre(fc, upperIdx(x)); }

    long long countOf(T x) const {
        int i = lowerIdx(x);
        return i < m && vals[i] == x ? cnt[i] : 0;
    }
    S slt(T x) { return pre(fs, lowerIdx(x)); }
    S sle(T x) { return pre(fs, upperIdx(x)); }

    T kth(long long k) {  // binary lifting: the largest prefix with fewer than k copies ends right before the answer
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

    void addRaw(T x, long long c) {  // c copies of x (c < 0 removes); keeps min / max (and medians / mex once asked for) current
        n += c;
        total += S(c) * x;
        insert(x, c);
        if (c > 0) {
            if (x == T(mexV) && mexV >= 0) mexV = findMex();  // x filled the mex (mexV is -1 until mex() is first called)
            if (n == c) {  // the set was empty
                mn = mx = x;
                if (med) low = high = Info{x, 0, c, 0};
                return;
            }
            if (x < mn) mn = x;
            if (x > mx) mx = x;
        } else {
            if (x >= 0 && x < T(mexV) && !countOf(x)) mexV = x;  // the last copy of a value below the mex
            if (!n) return;
            if (x == mn) mn = kth(1);
            if (x == mx) mx = kth(n);
        }
        if (!med) return;
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

    void startMedians() {  // the first median query (n > 0): from now on addRaw keeps both medians current
        med = true;
        low = kthInfo((n + 1) / 2), high = kthInfo(n / 2 + 1);
    }

    S sumFirst(long long k) {  // sum of the k smallest values
        if (k <= 0) return 0;
        Info f = kthInfo(k);
        return f.sb + S(k - f.before) * f.v;
    }

    // O(logN) -- add one copy of x
    void add(T x) {
        addRaw(x, 1);
    }

    // O(logN) -- add cnt copies of val (nothing if cnt <= 0)
    void addCount(T val, long long cnt) {
        if (cnt > 0) addRaw(val, cnt);
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

    // O(logN) -- k-th largest value (1-indexed); throws out_of_range unless 1 <= k <= size
    T kthLargest(long long k) {
        if (k < 1 || k > n) throw out_of_range("kthLargest: needs 1 <= k <= size");
        return kth(n - k + 1);
    }

    // O(logN) -- k-th smallest value (1-indexed); throws out_of_range unless 1 <= k <= size
    T kthSmallest(long long k) {
        if (k < 1 || k > n) throw out_of_range("kthSmallest: needs 1 <= k <= size");
        return kth(k);
    }

    // O(logN) -- largest value < x; nullopt if there is none
    optional<T> largestLtX(T x) {
        long long c = lt(x);
        if (!c) return nullopt;
        return kth(c);
    }

    // O(logN) -- largest value <= x; nullopt if there is none
    optional<T> largestLteX(T x) {
        long long c = le(x);
        if (!c) return nullopt;
        return kth(c);
    }

    // O(1) -- largest value; nullopt if empty
    optional<T> max() {
        if (!n) return nullopt;
        return mx;
    }

    // O(1 amortized) -- upper median: the (floor(size/2) + 1)-th smallest value; nullopt if empty
    optional<T> medianHigh() {
        if (!n) return nullopt;
        if (!med) startMedians();
        return high.v;
    }

    // O(1 amortized) -- lower median: the ceil(size/2)-th smallest value; nullopt if empty
    optional<T> medianLow() {
        if (!n) return nullopt;
        if (!med) startMedians();
        return low.v;
    }

    // O(1 amortized) -- smallest non-negative integer not in the set
    long long mex() {
        if (mexV < 0) mexV = findMex();  // the first call: from now on addRaw keeps it current
        return mexV;
    }

    // O(1) -- smallest value; nullopt if empty
    optional<T> min() {
        if (!n) return nullopt;
        return mn;
    }

    // O(logN) -- remove and return the largest value; nullopt if empty
    optional<T> popMax() {
        if (!n) return nullopt;
        T v = mx;
        addRaw(v, -1);
        return v;
    }

    // O(logN) -- remove and return the smallest value; nullopt if empty
    optional<T> popMin() {
        if (!n) return nullopt;
        T v = mn;
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

    // O(1) -- how many values (copies count)
    long long size() {
        return n;
    }

    // O(logN) -- smallest value > x; nullopt if there is none
    optional<T> smallestGtX(T x) {
        long long c = le(x);
        if (c == n) return nullopt;
        return kth(c + 1);
    }

    // O(logN) -- smallest value >= x; nullopt if there is none
    optional<T> smallestGteX(T x) {
        long long c = lt(x);
        if (c == n) return nullopt;
        return kth(c + 1);
    }

    // O(1 amortized) -- sum of |v - medianLow()| over all values (min total moves to make all equal); 0 if empty
    S sumAbsDiffToMedian() {
        if (!n) return 0;
        if (!med) startMedians();
        const Info& m = low;
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

    // O(logN) -- sum of the i-th..j-th largest values (1-indexed, inclusive; (5, 8) = 5th..8th biggest); throws out_of_range unless 1 <= i <= j <= size
    S sumKthLargestRange(long long i, long long j) {
        if (i < 1 || i > j || j > n) throw out_of_range("sumKthLargestRange: needs 1 <= i <= j <= size");
        return sumFirst(n - i + 1) - sumFirst(n - j);
    }

    // O(logN) -- sum of the i-th..j-th smallest values (1-indexed, inclusive); throws out_of_range unless 1 <= i <= j <= size
    S sumKthSmallestRange(long long i, long long j) {
        if (i < 1 || i > j || j > n) throw out_of_range("sumKthSmallestRange: needs 1 <= i <= j <= size");
        return sumFirst(j) - sumFirst(i - 1);
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
};
