// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/sets/blocks-fenwick/template.cpp
// @operations: add addCount count countDistinct countGtX countGteX countInValRange countLtX countLteX kthLargest kthSmallest largestLtX largestLteX max medianHigh medianLow mex min popMax popMin remove removeAll removeCount size smallestGtX smallestGteX
// @data-structure-type: blocks-fenwick
// @values: online
// @complexities:
//   add: sqrt(N)
//   addCount: sqrt(N)
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
//   popMax: sqrt(N)
//   popMin: sqrt(N)
//   remove: sqrt(N)
//   removeAll: sqrt(N)
//   removeCount: sqrt(N)
//   size: 1
//   smallestGtX: log(N)
//   smallestGteX: log(N)
//   build: 1
// @memory:
//   layout: none
//   node: keys[1*N] cnts[1*N] fcs[1*N]
//   tags: none
//   other: maxes[1*sqrt(N)] bc[2*sqrt(N)] cnt[1*N]
//   note: N = distinct values present; blocks of LOAD..2*LOAD values (Python LOAD = 64, C++ 512); queries are O(log N), and only updates that add or drop a distinct value pay O(sqrt N) (one block rebuilt)

// Ordered multiset (online: any values, nothing known ahead), sqrt-style with a Fenwick tree inside every block: the
// distinct values in sorted blocks of LOAD..2*LOAD, each block keeping its values' copies plus a Fenwick
// tree over them, and a Fenwick tree over the block totals. Every query is two Fenwick walks (over blocks, then inside
// one), so O(log N); an update that adds or drops a distinct value rebuilds its block's Fenwick (O(sqrt N)).
// T: an integer type; sums in S.
template <typename T>
struct BlockFenwickMultiset {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    static constexpr int LOAD = 512;
    vector<vector<T>> keys;  // blocks of sorted distinct values
    vector<vector<long long>> cnts, fcs;  // per block: copies of each value; Fenwick over them
    vector<T> maxes;  // last value of each block
    vector<long long> bc, fc{0};  // per block total copies; Fenwick over them
    long long n = 0, d = 0;
    struct Info { T v; long long before, c; };  // a value, copies before it, its copies
    T mn{}, mx{};  // kept current by addRaw while n > 0
    bool med = false;  // medians (low, high) are tracked from the first median query on
    Info low{}, high{};
    long long mexV = -1;  // -1 until mex() is first called, then kept current

    // O(1) -- an empty multiset
    BlockFenwickMultiset() {}

    template <class V>
    static vector<V> build(const vector<V>& a) {
        vector<V> f(a.size() + 1, 0);
        for (size_t i = 1; i < f.size(); i++) {
            f[i] += a[i - 1];
            size_t j = i + (i & -i);
            if (j < f.size()) f[j] += f[i];
        }
        return f;
    }

    template <class V>
    static void fen(vector<V>& f, int i, V v) {
        for (i++; i < (int)f.size(); i += i & -i) f[i] += v;
    }

    template <class V>
    static V pre(const vector<V>& f, int i) {  // f's total over positions 0..i-1
        V res = 0;
        for (; i > 0; i &= i - 1) res += f[i];
        return res;
    }

    void reblock() {
        fc = build(bc);
    }

    void reinner(int k) {
        fcs[k] = build(cnts[k]);
    }

    int blockOf(T x) const { return int(lower_bound(maxes.begin(), maxes.end(), x) - maxes.begin()); }

    void insert(T x, long long c) {
        int k = blockOf(x);
        if (k < (int)keys.size()) {
            int j = int(lower_bound(keys[k].begin(), keys[k].end(), x) - keys[k].begin());
            if (j < (int)keys[k].size() && keys[k][j] == x) {  // x is already here
                bc[k] += c, fen(fc, k, c);
                if (cnts[k][j] + c) {  // x stays: point updates only
                    cnts[k][j] += c, fen(fcs[k], j, c);
                    return;
                }
                d--;
                keys[k].erase(keys[k].begin() + j), cnts[k].erase(cnts[k].begin() + j);
                if (keys[k].empty()) {  // the block is empty: drop it
                    keys.erase(keys.begin() + k), cnts.erase(cnts.begin() + k), fcs.erase(fcs.begin() + k);
                    maxes.erase(maxes.begin() + k), bc.erase(bc.begin() + k);
                    reblock();
                    return;
                }
                maxes[k] = keys[k].back();
                reinner(k);
                return;
            }
        }
        d++;
        if (keys.empty()) {
            keys.push_back({x}), cnts.push_back({c}), fcs.emplace_back(), maxes.push_back(x), bc.push_back(c);
            reinner(0), reblock();
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
            fcs.emplace(fcs.begin() + k + 1);
            reinner(k), reinner(k + 1);
            maxes[k] = keys[k].back(), maxes.insert(maxes.begin() + k + 1, keys[k + 1].back());
            bc[k] = accumulate(cnts[k].begin(), cnts[k].end(), 0LL);
            bc.insert(bc.begin() + k + 1, accumulate(cnts[k + 1].begin(), cnts[k + 1].end(), 0LL));
            reblock();
        } else reinner(k);
    }

    template <class V>
    V below(T x, bool strict, const vector<V>& outer, const vector<vector<V>>& inner, V all) const {  // over values < x / <= x
        int k = int((strict ? lower_bound(maxes.begin(), maxes.end(), x) : upper_bound(maxes.begin(), maxes.end(), x)) - maxes.begin());
        if (k == (int)keys.size()) return all;
        const vector<T>& b = keys[k];
        int j = int((strict ? lower_bound(b.begin(), b.end(), x) : upper_bound(b.begin(), b.end(), x)) - b.begin());
        return pre(outer, k) + pre(inner[k], j);
    }

    long long lt(T x) { return below(x, true, fc, fcs, n); }
    long long le(T x) { return below(x, false, fc, fcs, n); }

    long long countOf(T x) const {
        int k = blockOf(x);
        if (k == (int)keys.size()) return 0;
        int j = int(lower_bound(keys[k].begin(), keys[k].end(), x) - keys[k].begin());
        return j < (int)keys[k].size() && keys[k][j] == x ? cnts[k][j] : 0;
    }

    Info kthInfo(long long k) {  // the k-th smallest, copies before it, its copies: lift over blocks, then inside one
        int m = (int)bc.size(), b = 0, j = 0;
        long long before = 0;
        for (int step = 1 << (31 - __builtin_clz(m)); step; step >>= 1)
            if (b + step <= m && before + fc[b + step] < k) b += step, before += fc[b];
        const vector<long long>& f = fcs[b];
        m = (int)keys[b].size();
        for (int step = 1 << (31 - __builtin_clz(m)); step; step >>= 1)
            if (j + step <= m && before + f[j + step] < k) j += step, before += f[j];
        return {keys[b][j], before, cnts[b][j]};
    }

    T kth(long long k) { return kthInfo(k).v; }

    long long findMex() {  // smallest non-negative integer not in the set: walk the blocks from 0 while the values run 0, 1, ...
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

    // O(sqrtN) -- add cnt copies of val (nothing if cnt <= 0)
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
};
