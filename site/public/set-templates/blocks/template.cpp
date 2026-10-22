// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/sets/blocks/template.cpp
// @operations: add addCount count countDistinct countGtX countGteX countInValRange countLtX countLteX kthLargest kthSmallest largestLtX largestLteX max medianHigh medianLow mex min popMax popMin remove removeAll removeCount size smallestGtX smallestGteX
// @data-structure-type: blocks
// @values: online
// @complexities:
//   add: sqrt(N)
//   addCount: sqrt(N)
//   count: log(N)
//   countDistinct: 1
//   countGtX: sqrt(N)
//   countGteX: sqrt(N)
//   countInValRange: sqrt(N)
//   countLtX: sqrt(N)
//   countLteX: sqrt(N)
//   kthLargest: sqrt(N)
//   kthSmallest: sqrt(N)
//   largestLtX: sqrt(N)
//   largestLteX: sqrt(N)
//   max: 1
//   medianHigh: 1 amortized
//   medianLow: 1 amortized
//   mex: 1 amortized
//   min: 1
//   popMax: sqrt(N)
//   popMin: sqrt(N)
//   remove: sqrt(N)
//   removeAll: sqrt(N)
//   removeCount: sqrt(N)
//   size: 1
//   smallestGtX: sqrt(N)
//   smallestGteX: sqrt(N)
//   build: 1
// @memory:
//   layout: none
//   node: keys[1*N] cnts[1*N]
//   tags: none
//   other: maxes[1*sqrt(N)] bc[2*sqrt(N)] cnt[1*N]
//   note: N = distinct values present; blocks of LOAD..2*LOAD values (Python LOAD = 64, C++ 512); each operation costs a few binary searches plus one block's worth of C-level list work

// Ordered multiset (online: any values, nothing known ahead), sqrt-style: the distinct values in sorted blocks of
// LOAD..2*LOAD, each block keeping its values' copies plus block totals, and a Fenwick tree over the
// block totals (rebuilt only after a block splits or empties). A query finds its block by binary search (or by
// lifting over the block Fenwick for k-th) and then works inside one block. T: an integer type; sums in S.
template <typename T>
struct BlockMultiset {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    static constexpr int LOAD = 512;
    vector<vector<T>> keys;  // blocks of sorted distinct values
    vector<vector<long long>> cnts;  // per block: copies of each value
    vector<T> maxes;  // last value of each block
    vector<long long> bc, fc;  // per block total copies; Fenwick over it
    bool stale = true;  // the Fenwicks need a rebuild
    long long n = 0, d = 0;
    struct Info { T v; long long before, c; };  // a value, copies before it, its copies
    T mn{}, mx{};  // kept current by addRaw while n > 0
    bool med = false;  // medians (low, high) are tracked from the first median query on
    Info low{}, high{};
    long long mexV = -1;  // -1 until mex() is first called, then kept current

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

    void insert(T x, long long c) {
        int k = blockOf(x);
        if (k < (int)keys.size()) {
            int j = int(lower_bound(keys[k].begin(), keys[k].end(), x) - keys[k].begin());
            if (j < (int)keys[k].size() && keys[k][j] == x) {  // x is already here
                if (cnts[k][j] + c) {
                    cnts[k][j] += c, bc[k] += c, fen(fc, k, c);
                    return;
                }
                d--;
                keys[k].erase(keys[k].begin() + j), cnts[k].erase(cnts[k].begin() + j);
                if (keys[k].empty()) {  // the block is empty: drop it
                    keys.erase(keys.begin() + k), cnts.erase(cnts.begin() + k), maxes.erase(maxes.begin() + k), bc.erase(bc.begin() + k);
                    stale = true;
                    return;
                }
                maxes[k] = keys[k].back(), bc[k] += c, fen(fc, k, c);
                return;
            }
        }
        d++;
        if (keys.empty()) {
            keys.push_back({x}), cnts.push_back({c}), maxes.push_back(x), bc.push_back(c);
            stale = true;
            return;
        }
        if (k == (int)keys.size()) k--;
        int j = int(lower_bound(keys[k].begin(), keys[k].end(), x) - keys[k].begin());
        keys[k].insert(keys[k].begin() + j, x), cnts[k].insert(cnts[k].begin() + j, c);
        maxes[k] = keys[k].back(), bc[k] += c, fen(fc, k, c);
        if ((int)keys[k].size() > 2 * LOAD) {  // split the block in half
            auto half = [&](auto& arr) {
                arr.insert(arr.begin() + k + 1, decay_t<decltype(arr[k])>(arr[k].begin() + LOAD, arr[k].end()));
                arr[k].resize(LOAD);
            };
            half(keys), half(cnts);
            maxes[k] = keys[k].back(), maxes.insert(maxes.begin() + k + 1, keys[k + 1].back());
            bc[k] = accumulate(cnts[k].begin(), cnts[k].end(), 0LL);
            bc.insert(bc.begin() + k + 1, accumulate(cnts[k + 1].begin(), cnts[k + 1].end(), 0LL));
            stale = true;
        }
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

    // the block holding the k-th smallest value: (block, copies before it, sum before it)
    tuple<int, long long, S> locate(long long k) {
        fresh();
        int pos = 0, m = (int)bc.size();
        long long before = 0;
        S acc = 0;
        for (int step = m ? 1 << (31 - __builtin_clz(m)) : 0; step; step >>= 1)
            if (pos + step <= m && before + fc[pos + step] < k) {
                pos += step, before += fc[pos];
            }
        return {pos, before, acc};
    }

    T kth(long long k) {
        auto [b, before, acc] = locate(k);
        (void)acc;
        k -= before;
        for (size_t j = 0;; j++) {
            if (k <= cnts[b][j]) return keys[b][j];
            k -= cnts[b][j];
        }
    }
    Info kthInfo(long long k) {  // the k-th smallest, copies before it, its copies
        auto [b, before, acc] = locate(k);
        (void)acc;
        for (size_t j = 0;; j++) {
            if (k <= before + cnts[b][j]) return {keys[b][j], before, cnts[b][j]};
            before += cnts[b][j];
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

    void addRaw(T x, long long c) {  // c copies of x (c < 0 removes); keeps min / max (and medians / mex once asked for) current
        n += c;
        insert(x, c);
        if (c > 0) {
            if (x == T(mexV) && mexV >= 0) mexV = findMex();  // x filled the mex (mexV is -1 until mex() is first called)
            if (n == c) {  // the set was empty
                mn = mx = x;
                if (med) low = high = Info{x, 0, c};
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

    void startMedians() {  // the first median query (n > 0): from now on addRaw keeps both medians current
        med = true;
        low = kthInfo((n + 1) / 2), high = kthInfo(n / 2 + 1);
    }

    // O(sqrtN) -- add one copy of x
    void add(T x) {
        addRaw(x, 1);
    }

    // O(sqrtN) -- add c copies of x (nothing if c <= 0)
    void addCount(T x, long long c) {
        if (c > 0) addRaw(x, c);
    }

    // O(logN) -- how many copies of x
    long long count(T x) {
        return countOf(x);
    }

    // O(1) -- how many distinct values
    long long countDistinct() {
        return d;
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

    // O(sqrtN) -- k-th largest value (1-indexed); throws out_of_range unless 1 <= k <= size
    T kthLargest(long long k) {
        if (k < 1 || k > n) throw out_of_range("kthLargest: needs 1 <= k <= size");
        return kth(n - k + 1);
    }

    // O(sqrtN) -- k-th smallest value (1-indexed); throws out_of_range unless 1 <= k <= size
    T kthSmallest(long long k) {
        if (k < 1 || k > n) throw out_of_range("kthSmallest: needs 1 <= k <= size");
        return kth(k);
    }

    // O(sqrtN) -- largest value < x; nullopt if there is none
    optional<T> largestLtX(T x) {
        long long c = lt(x);
        if (!c) return nullopt;
        return kth(c);
    }

    // O(sqrtN) -- largest value <= x; nullopt if there is none
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

    // O(sqrtN) -- remove every copy of x; returns how many were removed
    long long removeAll(T x) {
        long long k = count(x);
        if (k) addRaw(x, -k);
        return k;
    }

    // O(sqrtN) -- remove min(c, count(x)) copies of x; returns how many were removed
    long long removeCount(T x, long long c) {
        long long k = std::min(c, count(x));
        if (k <= 0) return 0;
        addRaw(x, -k);
        return k;
    }

    // O(1) -- how many values (copies count)
    long long size() {
        return n;
    }

    // O(sqrtN) -- smallest value > x; nullopt if there is none
    optional<T> smallestGtX(T x) {
        long long c = le(x);
        if (c == n) return nullopt;
        return kth(c + 1);
    }

    // O(sqrtN) -- smallest value >= x; nullopt if there is none
    optional<T> smallestGteX(T x) {
        long long c = lt(x);
        if (c == n) return nullopt;
        return kth(c + 1);
    }
};
