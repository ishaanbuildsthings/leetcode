// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/sets/blocks-with-sums-minmax/template.cpp
// @operations: add addCount clear count countDistinct countDistinctInValRange countGtX countGteX countInValRange countLtX countLteX firstIndex kth largestLtX largestLteX lastIndex max medianHigh medianLow mex min pop popMax popMin remove removeAll removeCount removeInValRange size smallestGtX smallestGteX sumAbsDiffToMedian sumAbsDiffToX sumAll sumGtX sumGteX sumInValRange sumKthLargestRange sumKthSmallestRange sumLargestK sumLtX sumLteX sumSmallestK
// @data-structure-type: blocks
// @values: online
// @keys: numbers
// @tracks: minmax
// @complexities:
//   add: sqrt(N)
//   addCount: sqrt(N)
//   clear: N
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
//   max: 1
//   medianHigh: sqrt(N)
//   medianLow: sqrt(N)
//   mex: sqrt(N)
//   min: 1
//   pop: sqrt(N)
//   popMax: sqrt(N)
//   popMin: sqrt(N)
//   remove: sqrt(N)
//   removeAll: sqrt(N)
//   removeCount: sqrt(N)
//   removeInValRange: sqrt(N) amortized
//   size: 1
//   smallestGtX: sqrt(N)
//   smallestGteX: sqrt(N)
//   sumAbsDiffToMedian: sqrt(N)
//   sumAbsDiffToX: sqrt(N)
//   sumAll: 1
//   sumGtX: sqrt(N)
//   sumGteX: sqrt(N)
//   sumInValRange: sqrt(N)
//   sumKthLargestRange: sqrt(N)
//   sumKthSmallestRange: sqrt(N)
//   sumLargestK: sqrt(N)
//   sumLtX: sqrt(N)
//   sumLteX: sqrt(N)
//   sumSmallestK: sqrt(N)
//   build: 1
// @memory:
//   layout: none
//   node: keys[1*N] cnts[1*N] sums[1*N]
//   tags: none
//   other: maxes[1*sqrt(N)] bc[2*sqrt(N)] bs[2*sqrt(N)] cnt[1*N]
//   note: N = distinct values present; blocks of LOAD..2*LOAD values (Python LOAD = 64, C++ 512); each operation costs a few binary searches plus one block's worth of C-level list work

// Ordered multiset (online: any values, nothing known ahead), sqrt-style: the distinct values in sorted blocks of
// LOAD..2*LOAD, each block keeping its values' copies and copies * value plus block totals, and a Fenwick tree over the
// block totals (rebuilt only after a block splits or empties). A query finds its block by binary search (or by
// lifting over the block Fenwick for k-th) and then works inside one block. T: an integer type; sums in S.
template <typename T>
struct BlockMultiset {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    static constexpr int LOAD = 512;
    vector<vector<T>> keys;  // blocks of sorted distinct values
    vector<vector<long long>> cnts;  // per block: copies of each value
    vector<vector<S>> sums;  // per block: copies * value
    vector<T> maxes;  // last value of each block
    vector<long long> bc, fc;  // per block total copies; Fenwick over it
    vector<S> bs, fs;  // per block total sum; Fenwick over it
    bool stale = true;  // the Fenwicks need a rebuild
    long long n = 0, d = 0;
    struct Info { T v; long long before, c; S sb; };  // a value, copies before it, its copies, sum before it
    T mn{}, mx{};  // kept current by addRaw while n > 0
    S total = 0;

    // O(1) -- an empty multiset
    BlockMultiset() {}

    template <class V>
    static void build(vector<V>& f, const vector<V>& a) {
        f.assign(a.size() + 1, 0);
        for (size_t i = 1; i < f.size(); i++) {
            f[i] += a[i - 1];
            size_t j = i + (i & -i);
            if (j < f.size()) f[j] += f[i];
        }
    }

    void fresh() {
        if (!stale) return;
        build(fc, bc);
        build(fs, bs);
        stale = false;
    }

    template <class V>
    void fen(vector<V>& f, int i, V v) {
        if (stale) return;
        for (i++; i < (int)f.size(); i += i & -i) f[i] += v;
    }

    template <class V>
    V pre(const vector<V>& f, int k) {  // total of blocks 0..k-1
        fresh();
        V res = 0;
        for (; k > 0; k &= k - 1) res += f[k];
        return res;
    }

    int blockOf(T x) const { return int(lower_bound(maxes.begin(), maxes.end(), x) - maxes.begin()); }

    long long insert(T x, long long c) {  // returns x's new count
        int k = blockOf(x);
        if (k < (int)keys.size()) {
            int j = int(lower_bound(keys[k].begin(), keys[k].end(), x) - keys[k].begin());
            if (j < (int)keys[k].size() && keys[k][j] == x) {  // x is already here
                if (cnts[k][j] + c) {
                    cnts[k][j] += c, bc[k] += c, fen(fc, k, c);
                    sums[k][j] += S(c) * x, bs[k] += S(c) * x, fen(fs, k, S(c) * x);
                    return cnts[k][j];
                }
                d--;
                keys[k].erase(keys[k].begin() + j), cnts[k].erase(cnts[k].begin() + j);
                sums[k].erase(sums[k].begin() + j);
                if (keys[k].empty()) {  // the block is empty: drop it
                    keys.erase(keys.begin() + k), cnts.erase(cnts.begin() + k), maxes.erase(maxes.begin() + k), bc.erase(bc.begin() + k);
                    sums.erase(sums.begin() + k), bs.erase(bs.begin() + k);
                    stale = true;
                    return 0;
                }
                maxes[k] = keys[k].back(), bc[k] += c, fen(fc, k, c);
                bs[k] += S(c) * x, fen(fs, k, S(c) * x);
                return 0;
            }
        }
        d++;
        if (keys.empty()) {
            keys.push_back({x}), cnts.push_back({c}), maxes.push_back(x), bc.push_back(c);
            sums.push_back({S(c) * x}), bs.push_back(S(c) * x);
            stale = true;
            return c;
        }
        if (k == (int)keys.size()) k--;
        int j = int(lower_bound(keys[k].begin(), keys[k].end(), x) - keys[k].begin());
        keys[k].insert(keys[k].begin() + j, x), cnts[k].insert(cnts[k].begin() + j, c);
        sums[k].insert(sums[k].begin() + j, S(c) * x), bs[k] += S(c) * x, fen(fs, k, S(c) * x);
        maxes[k] = keys[k].back(), bc[k] += c, fen(fc, k, c);
        if ((int)keys[k].size() > 2 * LOAD) {  // split the block in half
            auto half = [&](auto& arr) {
                arr.insert(arr.begin() + k + 1, decay_t<decltype(arr[k])>(arr[k].begin() + LOAD, arr[k].end()));
                arr[k].resize(LOAD);
            };
            half(keys), half(cnts);
            half(sums);
            maxes[k] = keys[k].back(), maxes.insert(maxes.begin() + k + 1, keys[k + 1].back());
            bc[k] = accumulate(cnts[k].begin(), cnts[k].end(), 0LL);
            bc.insert(bc.begin() + k + 1, accumulate(cnts[k + 1].begin(), cnts[k + 1].end(), 0LL));
            bs[k] = accumulate(sums[k].begin(), sums[k].end(), S(0));
            bs.insert(bs.begin() + k + 1, accumulate(sums[k + 1].begin(), sums[k + 1].end(), S(0)));
            stale = true;
        }
        return c;
    }

    long long countBelow(T x, bool strict) {  // copies of the values < x (strict) or <= x
        int k = blockOf(x);
        if (k == (int)keys.size()) return n;
        const vector<T>& b = keys[k];
        int j = int((strict ? lower_bound(b.begin(), b.end(), x) : upper_bound(b.begin(), b.end(), x)) - b.begin());
        return pre(fc, k) + accumulate(cnts[k].begin(), cnts[k].begin() + j, 0LL);
    }

    long long lt(T x) { return countBelow(x, true); }
    long long le(T x) { return countBelow(x, false); }

    long long countOf(T x) const {
        int k = blockOf(x);
        if (k == (int)keys.size()) return 0;
        int j = int(lower_bound(keys[k].begin(), keys[k].end(), x) - keys[k].begin());
        return j < (int)keys[k].size() && keys[k][j] == x ? cnts[k][j] : 0;
    }

    S sumBelow(T x, bool strict) {  // sum of the values < x (strict) or <= x
        int k = blockOf(x);
        if (k == (int)keys.size()) return total;
        const vector<T>& b = keys[k];
        int j = int((strict ? lower_bound(b.begin(), b.end(), x) : upper_bound(b.begin(), b.end(), x)) - b.begin());
        return pre(fs, k) + accumulate(sums[k].begin(), sums[k].begin() + j, S(0));
    }

    S slt(T x) { return sumBelow(x, true); }
    S sle(T x) { return sumBelow(x, false); }

    // the block holding the k-th smallest value: (block, copies before it, sum before it)
    tuple<int, long long, S> locate(long long k) {
        fresh();
        int pos = 0, m = (int)bc.size();
        long long before = 0;
        S acc{};
        for (int step = m ? 1 << (31 - __builtin_clz(m)) : 0; step; step >>= 1)
            if (pos + step <= m && before + fc[pos + step] < k) {
                pos += step, before += fc[pos];
                acc += fs[pos];
            }
        return {pos, before, acc};
    }

    T kthAt(long long k) {
        auto [b, before, acc] = locate(k);
        (void)acc;
        k -= before;
        for (size_t j = 0;; j++) {
            if (k <= cnts[b][j]) return keys[b][j];
            k -= cnts[b][j];
        }
    }
    Info kthInfo(long long k) {  // the k-th smallest, copies before it, its copies, sum before it
        auto [b, before, acc] = locate(k);
        for (size_t j = 0;; j++) {
            if (k <= before + cnts[b][j]) return {keys[b][j], before, cnts[b][j], acc};
            before += cnts[b][j], acc += sums[b][j];
        }
    }
    // smallest non-negative integer not in the set: walk the blocks from 0 while the values run 0, 1, 2, ...
    long long findMex() {
        int k = blockOf(T(0));
        if (k == (int)keys.size()) return 0;
        int j = int(lower_bound(keys[k].begin(), keys[k].end(), T(0)) - keys[k].begin());
        long long want = 0;
        for (; k < (int)keys.size(); k++, j = 0) {
            const vector<T>& b = keys[k];
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

    void addRaw(T x, long long c) {  // c copies of x (c < 0 removes); keeps min / max current
        n += c;
        total += S(c) * x;
        long long f = insert(x, c);  // x's new count
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

    void clearData() {
        keys.clear(), cnts.clear(), maxes.clear(), bc.clear(), fc.clear();
        sums.clear(), bs.clear(), fs.clear();
        stale = true;
    }

    long long distinctLt(T x) const {  // distinct values < x: every block before x's, then a binary search in x's block
        int b = int(lower_bound(maxes.begin(), maxes.end(), x) - maxes.begin());
        long long res = 0;
        for (int k = 0; k < b; k++) res += (long long)keys[k].size();
        if (b < (int)keys.size()) res += lower_bound(keys[b].begin(), keys[b].end(), x) - keys[b].begin();
        return res;
    }

    // O(sqrtN) -- add one copy of x
    void add(T x) {
        addRaw(x, 1);
    }

    // O(sqrtN) -- add cnt copies of val (nothing if cnt <= 0)
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

    // O(sqrtN) -- how many distinct values v with lo <= v <= hi (0 if lo > hi)
    long long countDistinctInValRange(T lo, T hi) {
        if (hi < lo) return 0;
        return distinctLt(hi) - distinctLt(lo) + (countOf(hi) ? 1 : 0);
    }

    // O(sqrtN) -- how many values > x
    long long countGtX(T x) {
        return n - le(x);
    }

    // O(sqrtN) -- how many values >= x
    long long countGteX(T x) {
        return n - lt(x);
    }

    // O(sqrtN) -- how many values v with lo <= v <= hi (0 if lo > hi)
    long long countInValRange(T lo, T hi) {
        return lo <= hi ? le(hi) - lt(lo) : 0;
    }

    // O(sqrtN) -- how many values < x
    long long countLtX(T x) {
        return lt(x);
    }

    // O(sqrtN) -- how many values <= x
    long long countLteX(T x) {
        return le(x);
    }

    // O(sqrtN) -- 0-indexed position of the first copy of x in sorted order (= how many values < x); -1 if x is not in the set
    long long firstIndex(T x) {
        return countOf(x) ? lt(x) : -1;
    }

    // O(sqrtN) -- the value at sorted position i (0-indexed: kth(0) is the min); throws out_of_range unless 0 <= i < size
    T kth(long long i) {
        if (i < 0 || i >= n) throw out_of_range("kth: needs 0 <= i < size");
        return kthAt(i + 1);
    }

    // O(sqrtN) -- largest value < x; nullopt if there is none
    optional<T> largestLtX(T x) {
        long long c = lt(x);
        if (!c) return nullopt;
        return kthAt(c);
    }

    // O(sqrtN) -- largest value <= x; nullopt if there is none
    optional<T> largestLteX(T x) {
        long long c = le(x);
        if (!c) return nullopt;
        return kthAt(c);
    }

    // O(sqrtN) -- 0-indexed position of the last copy of x in sorted order (= how many values <= x, minus 1); -1 if x is not in the set
    long long lastIndex(T x) {
        return countOf(x) ? le(x) - 1 : -1;
    }

    // O(1) -- largest value; nullopt if empty
    optional<T> max() {
        if (!n) return nullopt;
        return mx;
    }

    // O(sqrtN) -- upper median: the (floor(size/2) + 1)-th smallest value; nullopt if empty
    optional<T> medianHigh() {
        if (!n) return nullopt;
        return kthAt(n / 2 + 1);
    }

    // O(sqrtN) -- lower median: the ceil(size/2)-th smallest value; nullopt if empty
    optional<T> medianLow() {
        if (!n) return nullopt;
        return kthAt((n + 1) / 2);
    }

    // O(sqrtN) -- smallest non-negative integer not in the set
    long long mex() {
        return findMex();
    }

    // O(1) -- smallest value; nullopt if empty
    optional<T> min() {
        if (!n) return nullopt;
        return mn;
    }

    // O(sqrtN) -- remove and return the value at sorted position i (0-indexed: pop(0) is popMin()); throws out_of_range unless 0 <= i < size
    T pop(long long i) {
        if (i < 0 || i >= n) throw out_of_range("pop: needs 0 <= i < size");
        T v = kthAt(i + 1);
        addRaw(v, -1);
        return v;
    }

    // O(sqrtN) -- remove and return the largest value; nullopt if empty
    optional<T> popMax() {
        if (!n) return nullopt;
        T v = mx;
        addRaw(v, -1);
        return v;
    }

    // O(sqrtN) -- remove and return the smallest value; nullopt if empty
    optional<T> popMin() {
        if (!n) return nullopt;
        T v = mn;
        addRaw(v, -1);
        return v;
    }

    // O(sqrtN) -- remove one copy of x if present; returns how many were removed (0 or 1)
    long long remove(T x) {
        if (!count(x)) return 0;
        addRaw(x, -1);
        return 1;
    }

    // O(sqrtN) -- remove every copy of val; returns how many were removed
    long long removeAll(T val) {
        long long k = count(val);
        if (k) addRaw(val, -k);
        return k;
    }

    // O(sqrtN) -- remove min(cnt, count(val)) copies of val; returns how many were removed
    long long removeCount(T val, long long cnt) {
        long long k = std::min(cnt, count(val));
        if (k <= 0) return 0;
        addRaw(val, -k);
        return k;
    }

    // O(sqrtN amortized) -- remove every value v with lo <= v <= hi; returns how many copies were removed (0 if lo > hi)
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

    // O(sqrtN) -- smallest value > x; nullopt if there is none
    optional<T> smallestGtX(T x) {
        long long c = le(x);
        if (c == n) return nullopt;
        return kthAt(c + 1);
    }

    // O(sqrtN) -- smallest value >= x; nullopt if there is none
    optional<T> smallestGteX(T x) {
        long long c = lt(x);
        if (c == n) return nullopt;
        return kthAt(c + 1);
    }

    // O(sqrtN) -- sum of |v - medianLow()| over all values (min total moves to make all equal); 0 if empty
    S sumAbsDiffToMedian() {
        if (!n) return 0;
        Info m = kthInfo((n + 1) / 2);
        return S(m.v) * m.before - m.sb + (total - m.sb - S(m.v) * m.c) - S(m.v) * (n - m.before - m.c);
    }

    // O(sqrtN) -- sum of |v - x| over all values
    S sumAbsDiffToX(T x) {
        long long c = lt(x);
        S s = slt(x);
        return S(x) * c - s + (total - s) - S(x) * (n - c);
    }

    // O(1) -- sum of all values
    S sumAll() {
        return total;
    }

    // O(sqrtN) -- sum of the values > x
    S sumGtX(T x) {
        return total - sle(x);
    }

    // O(sqrtN) -- sum of the values >= x
    S sumGteX(T x) {
        return total - slt(x);
    }

    // O(sqrtN) -- sum of the values v with lo <= v <= hi (0 if lo > hi)
    S sumInValRange(T lo, T hi) {
        return lo <= hi ? sle(hi) - slt(lo) : S(0);
    }

    // O(sqrtN) -- sum of the kFrom-th..kTo-th largest values (1-indexed, inclusive; (5, 8) = 5th..8th biggest); throws out_of_range unless 1 <= kFrom <= kTo <= size
    S sumKthLargestRange(long long kFrom, long long kTo) {
        if (kFrom < 1 || kFrom > kTo || kTo > n) throw out_of_range("sumKthLargestRange: needs 1 <= kFrom <= kTo <= size");
        return sumFirst(n - kFrom + 1) - sumFirst(n - kTo);
    }

    // O(sqrtN) -- sum of the kFrom-th..kTo-th smallest values (1-indexed, inclusive); throws out_of_range unless 1 <= kFrom <= kTo <= size
    S sumKthSmallestRange(long long kFrom, long long kTo) {
        if (kFrom < 1 || kFrom > kTo || kTo > n) throw out_of_range("sumKthSmallestRange: needs 1 <= kFrom <= kTo <= size");
        return sumFirst(kTo) - sumFirst(kFrom - 1);
    }

    // O(sqrtN) -- sum of the k largest values; throws out_of_range unless 0 <= k <= size
    S sumLargestK(long long k) {
        if (k < 0 || k > n) throw out_of_range("sumLargestK: needs 0 <= k <= size");
        return total - sumFirst(n - k);
    }

    // O(sqrtN) -- sum of the values < x
    S sumLtX(T x) {
        return slt(x);
    }

    // O(sqrtN) -- sum of the values <= x
    S sumLteX(T x) {
        return sle(x);
    }

    // O(sqrtN) -- sum of the k smallest values; throws out_of_range unless 0 <= k <= size
    S sumSmallestK(long long k) {
        if (k < 0 || k > n) throw out_of_range("sumSmallestK: needs 0 <= k <= size");
        return sumFirst(k);
    }
};
