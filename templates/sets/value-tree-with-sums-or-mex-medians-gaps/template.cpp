// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/sets/value-tree-with-sums-or-mex-medians-gaps/template.cpp
// @operations: add addCount clear count countDistinct countDistinctInValRange countGtX countGteX countInValRange countLtX countLteX firstIndex kth largestLtX largestLteX lastIndex max maxGap medianHigh medianLow mex min minAdjacentDiff orOfAll orOfGtX orOfGteX orOfInValRange orOfKthLargestRange orOfKthSmallestRange orOfLargestK orOfLtX orOfLteX orOfSmallestK pop popMax popMin remove removeAll removeCount removeInValRange size smallestGtX smallestGteX sumAbsDiffToMedian sumAbsDiffToX sumAll sumGtX sumGteX sumInValRange sumKthLargestRange sumKthSmallestRange sumLargestK sumLtX sumLteX sumSmallestK
// @data-structure-type: value-tree
// @values: online-range
// @keys: numbers
// @tracks: medians gaps
// @complexities:
//   add: log(U)
//   addCount: log(U)
//   clear: N*log(U)
//   count: log(U)
//   countDistinct: 1
//   countDistinctInValRange: log(U)
//   countGtX: log(U)
//   countGteX: log(U)
//   countInValRange: log(U)
//   countLtX: log(U)
//   countLteX: log(U)
//   firstIndex: log(U)
//   kth: log(U)
//   largestLtX: log(U)
//   largestLteX: log(U)
//   lastIndex: log(U)
//   max: log(U)
//   maxGap: 1 amortized
//   medianHigh: 1
//   medianLow: 1
//   mex: log(U)
//   min: log(U)
//   minAdjacentDiff: 1 amortized
//   orOfAll: 1
//   orOfGtX: log(U)
//   orOfGteX: log(U)
//   orOfInValRange: log(U)
//   orOfKthLargestRange: log(U)
//   orOfKthSmallestRange: log(U)
//   orOfLargestK: log(U)
//   orOfLtX: log(U)
//   orOfLteX: log(U)
//   orOfSmallestK: log(U)
//   pop: log(U)
//   popMax: log(U)
//   popMin: log(U)
//   remove: log(U)
//   removeAll: log(U)
//   removeCount: log(U)
//   removeInValRange: log(U) amortized
//   size: 1
//   smallestGtX: log(U)
//   smallestGteX: log(U)
//   sumAbsDiffToMedian: 1
//   sumAbsDiffToX: log(U)
//   sumAll: 1
//   sumGtX: log(U)
//   sumGteX: log(U)
//   sumInValRange: log(U)
//   sumKthLargestRange: log(U)
//   sumKthSmallestRange: log(U)
//   sumLargestK: log(U)
//   sumLtX: log(U)
//   sumLteX: log(U)
//   sumSmallestK: log(U)
//   build: 1
// @memory:
//   layout: sparse
//   node: c[1*log(U)] p[1*log(U)] s[1*log(U)] o[1*log(U)]
//   tags: none
//   other: children[2*log(U)]
//   note: per add of a new value, one node per level of its root path; U = hi - lo + 1. C++: one shared node pool (node 0 = empty), call resetPool() between test cases; Python: dicts keyed by heap index

// Ordered multiset of integers in a known range [lo, hi] (values not known ahead): a dynamic tree over the value range,
// each node keeping how many copies, their sum,, their OR and how many distinct values (for mex) are below it. Nodes live in one pool
// shared by every ValueTreeMultiset<T> (call resetPool() between test cases); node 0 is the shared empty block.
// k-th / sums of the k smallest descend by counts; mex descends to the first value >= 0 whose block isn't full.
// T: int, long long, ...; sums in S (long long for small T).
template <typename T>
struct ValueTreeMultiset {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    struct Node { long long c; S s; long long p; T orv; int l, r; };  // copies, sum, distinct values, OR below
    static inline vector<Node> pool{Node{}};  // node 0: empty, its children are itself
    long long lo, hi, n = 0, d = 0;
    struct Info { T v; long long before, c; S sb; };  // a value, copies before it, its copies, sum before it
    Info low{}, high{};  // both medians, kept current by addRaw while n > 0
    multiset<long long> gaps;  // differences between neighbouring distinct values
    long long dups = 0;  // values with 2+ copies
    S total = 0;
    int root = 0;

    // O(1) -- an empty multiset for values in [lo, hi] (any long long range, negative is fine)
    ValueTreeMultiset(long long lo, long long hi) : lo(lo), hi(hi) {}

    // O(1) -- forget every node of every ValueTreeMultiset<T>; call between test cases, then build new ones
    static void resetPool() { pool.resize(1); }

    // optional -- reserve room for this many nodes up front
    static void reservePool(size_t nodes) { pool.reserve(nodes); }

    static int make() {
        pool.push_back(Node{});
        return (int)pool.size() - 1;
    }

    long long insert(T x, long long c) {  // returns x's new count
        if (!root) root = make();
        int path[130], dep = 0, y = root;
        long long a = lo, b = hi;
        while (true) {
            path[dep++] = y;
            if (a == b) break;
            long long m = a + (b - a) / 2;
            bool right = x > m;
            int ch = right ? pool[y].r : pool[y].l;
            if (!ch) {
                ch = make();
                (right ? pool[y].r : pool[y].l) = ch;
            }
            y = ch;
            if (right) a = m + 1;
            else b = m;
        }
        long long old = pool[y].c;
        long long pres = (old + c > 0) - (old > 0);
        d += pres;
        for (int k = 0; k < dep; k++) {
            Node& v = pool[path[k]];
            v.c += c;
            v.p += pres;
            v.s += S(c) * x;
        }
        if (pres) {  // x appeared or disappeared: the OR / AND up its path
            pool[y].orv = pres > 0 ? x : T(0);
            for (int k = dep - 2; k >= 0; k--) {
                Node& v = pool[path[k]];
                v.orv = pool[v.l].orv | pool[v.r].orv;
            }
        }
        return old + c;
    }

    // (copies, sum) of the values < x
    pair<long long, S> prefix(T x) const {
        if (x <= lo) return {0, 0};
        if (x > hi) return {pool[root].c, pool[root].s};
        long long cnt = 0;
        S sum = 0;
        int y = root;
        long long a = lo, b = hi;
        while (y && a < b) {
            long long m = a + (b - a) / 2;
            if (x <= m) y = pool[y].l, b = m;
            else {
                const Node& L = pool[pool[y].l];
                cnt += L.c, sum += L.s;
                y = pool[y].r, a = m + 1;
            }
        }
        return {cnt, sum};  // y is now the leaf of x (or empty): values < x only
    }

    long long lt(T x) { return prefix(x).first; }
    long long le(T x) { return prefix(x + 1).first; }

    long long countOf(T x) const {  // walk to the leaf of x
        if (x < lo || x > hi) return 0;
        int y = root;
        long long a = lo, b = hi;
        while (y && a < b) {
            long long m = a + (b - a) / 2;
            if (x <= m) y = pool[y].l, b = m;
            else y = pool[y].r, a = m + 1;
        }
        return pool[y].c;
    }
    S slt(T x) { return prefix(x).second; }
    S sle(T x) { return prefix(x + 1).second; }

    T kthAt(long long k) {
        int y = root;
        long long a = lo, b = hi;
        while (a < b) {
            long long m = a + (b - a) / 2;
            long long cl = pool[pool[y].l].c;
            if (k <= cl) y = pool[y].l, b = m;
            else k -= cl, y = pool[y].r, a = m + 1;
        }
        return T(a);
    }

    Info kthInfo(long long k) {  // the k-th smallest, copies before it, its copies, sum before it
        int y = root;
        long long a = lo, b = hi, before = 0;
        S acc = 0;
        while (a < b) {
            long long m = a + (b - a) / 2;
            const Node& L = pool[pool[y].l];
            if (k <= before + L.c) y = pool[y].l, b = m;
            else before += L.c, acc += L.s, y = pool[y].r, a = m + 1;
        }
        return {T(a), before, pool[y].c, acc};
    }
    // the first value >= from in [a, b] (node y) that is not present, or LLONG_MAX
    long long firstMissing(int y, long long a, long long b, long long from) const {
        if (b < from) return LLONG_MAX;
        if (!y) return std::max(a, from);
        if (pool[y].p == b - a + 1) return LLONG_MAX;
        if (a == b) return a;
        long long m = a + (b - a) / 2;
        long long res = firstMissing(pool[y].l, a, m, from);
        return res != LLONG_MAX ? res : firstMissing(pool[y].r, m + 1, b, from);
    }

    // smallest non-negative integer not in the set (hi + 1 if all of [0, hi] are present)
    long long findMex() {
        if (lo > 0) return 0;
        long long res = firstMissing(root, lo, hi, 0);
        return res == LLONG_MAX ? hi + 1 : res;
    }

    void addRaw(T x, long long c) {  // c copies of x (c < 0 removes); keeps both medians current
        n += c;
        total += S(c) * x;
        long long f = insert(x, c);  // x's new count
        long long g = f - c;  // x's old count
        {  // gaps
            if ((g >= 2) != (f >= 2)) dups += f >= 2 ? 1 : -1;  // values with 2+ copies (then the smallest difference is 0)
            if (!g || !f) {  // x appeared or disappeared: the gap between its neighbours splits or comes back
                optional<T> p = largestLtX(x), q = smallestGtX(x);
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
            if (n == c) {  // the set was empty
                low = high = Info{x, 0, c, 0};
                return;
            }
        } else {
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

    S sumFirst(long long k) {  // sum of the k smallest values
        if (k <= 0) return 0;
        Info f = kthInfo(k);
        return f.sb + S(k - f.before) * f.v;
    }

    void resetCached() {  // nothing counted: as newly built
        gaps.clear(), dups = 0;
        n = d = 0;
        total = 0;
    }

    void clearData() {  // zero this tree's nonzero nodes in place: the next adds reuse them, so nothing leaks
        vector<int> st;
        if (root && pool[root].c) st.push_back(root);
        while (!st.empty()) {
            Node& v = pool[st.back()];
            st.pop_back();
            v.c = 0, v.s = 0, v.p = 0, v.orv = 0;
            if (v.l && pool[v.l].c) st.push_back(v.l);
            if (v.r && pool[v.r].c) st.push_back(v.r);
        }
    }

    long long distinctLt(T x) const {  // distinct values < x
        if (x <= lo) return 0;
        if (x > hi) return pool[root].p;
        long long res = 0, a = lo, b = hi;
        int y = root;
        while (y && a < b) {
            long long m = a + (b - a) / 2;
            if (x <= m) y = pool[y].l, b = m;
            else res += pool[pool[y].l].p, y = pool[y].r, a = m + 1;
        }
        return res;
    }

    T orWalk(int y, long long a, long long b, long long ql, long long qr) const {  // OR of node y's values in [ql, qr]
        if (!y || qr < a || b < ql) return T(0);
        if (ql <= a && b <= qr) return pool[y].orv;
        long long m = a + (b - a) / 2;
        return orWalk(pool[y].l, a, m, ql, qr) | orWalk(pool[y].r, m + 1, b, ql, qr);
    }

    T orIn(T ql, T qr) const { return orWalk(root, lo, hi, ql, qr); }  // OR of the values in [ql, qr]
    T orLe(T x) const { return orWalk(root, lo, hi, lo, x); }  // OR of the values <= x
    T orGe(T x) const { return orWalk(root, lo, hi, x, hi); }  // OR of the values >= x

    // O(logU) -- add one copy of x
    void add(T x) {
        addRaw(x, 1);
    }

    // O(logU) -- add cnt copies of val (nothing if cnt <= 0)
    void addCount(T val, long long cnt) {
        if (cnt > 0) addRaw(val, cnt);
    }

    // O(N logU) -- remove everything: afterwards it is as if newly built (same constructor arguments), so reuse it instead of building a new one
    void clear() {
        clearData();
        resetCached();
    }

    // O(logU) -- how many copies of x
    long long count(T x) {
        return countOf(x);
    }

    // O(1) -- how many distinct values
    long long countDistinct() {
        return d;
    }

    // O(logU) -- how many distinct values v with lo <= v <= hi (0 if lo > hi)
    long long countDistinctInValRange(T lo, T hi) {
        if (hi < lo) return 0;
        return distinctLt(hi) - distinctLt(lo) + (countOf(hi) ? 1 : 0);
    }

    // O(logU) -- how many values > x
    long long countGtX(T x) {
        return n - le(x);
    }

    // O(logU) -- how many values >= x
    long long countGteX(T x) {
        return n - lt(x);
    }

    // O(logU) -- how many values v with lo <= v <= hi (0 if lo > hi)
    long long countInValRange(T lo, T hi) {
        return lo <= hi ? le(hi) - lt(lo) : 0;
    }

    // O(logU) -- how many values < x
    long long countLtX(T x) {
        return lt(x);
    }

    // O(logU) -- how many values <= x
    long long countLteX(T x) {
        return le(x);
    }

    // O(logU) -- 0-indexed position of the first copy of x in sorted order (= how many values < x); -1 if x is not in the set
    long long firstIndex(T x) {
        return countOf(x) ? lt(x) : -1;
    }

    // O(logU) -- the value at sorted position i (0-indexed: kth(0) is the min); throws out_of_range unless 0 <= i < size
    T kth(long long i) {
        if (i < 0 || i >= n) throw out_of_range("kth: needs 0 <= i < size");
        return kthAt(i + 1);
    }

    // O(logU) -- largest value < x; nullopt if there is none
    optional<T> largestLtX(T x) {
        long long c = lt(x);
        if (!c) return nullopt;
        return kthAt(c);
    }

    // O(logU) -- largest value <= x; nullopt if there is none
    optional<T> largestLteX(T x) {
        long long c = le(x);
        if (!c) return nullopt;
        return kthAt(c);
    }

    // O(logU) -- 0-indexed position of the last copy of x in sorted order (= how many values <= x, minus 1); -1 if x is not in the set
    long long lastIndex(T x) {
        return countOf(x) ? le(x) - 1 : -1;
    }

    // O(logU) -- largest value; nullopt if empty
    optional<T> max() {
        if (!n) return nullopt;
        return kthAt(n);
    }

    // O(1 amortized) -- largest difference between two neighbouring distinct values; nullopt if fewer than 2 distinct values
    optional<long long> maxGap() {
        if (d < 2) return nullopt;
        return *gaps.rbegin();
    }

    // O(1) -- upper median: the (floor(size/2) + 1)-th smallest value; nullopt if empty
    optional<T> medianHigh() {
        if (!n) return nullopt;
        return high.v;
    }

    // O(1) -- lower median: the ceil(size/2)-th smallest value; nullopt if empty
    optional<T> medianLow() {
        if (!n) return nullopt;
        return low.v;
    }

    // O(logU) -- smallest non-negative integer not in the set
    long long mex() {
        return findMex();
    }

    // O(logU) -- smallest value; nullopt if empty
    optional<T> min() {
        if (!n) return nullopt;
        return kthAt(1);
    }

    // O(1 amortized) -- smallest difference between two values in the set (0 if some value has 2+ copies); nullopt if fewer than 2 values
    optional<long long> minAdjacentDiff() {
        if (n < 2) return nullopt;
        if (dups) return 0LL;
        return *gaps.begin();
    }

    // O(1) -- bitwise OR of all values; 0 if empty
    T orOfAll() {
        return pool[root].orv;
    }

    // O(logU) -- bitwise OR of the values > x; 0 if there are none
    T orOfGtX(T x) {
        if (x == numeric_limits<T>::max()) return T(0);
        return orGe(x + 1);
    }

    // O(logU) -- bitwise OR of the values >= x; 0 if there are none
    T orOfGteX(T x) {
        return orGe(x);
    }

    // O(logU) -- bitwise OR of the values v with lo <= v <= hi; 0 if there are none
    T orOfInValRange(T lo, T hi) {
        return lo <= hi ? orIn(lo, hi) : T(0);
    }

    // O(logU) -- bitwise OR of the kFrom-th..kTo-th largest values (1-indexed, inclusive); throws out_of_range unless 1 <= kFrom <= kTo <= size
    T orOfKthLargestRange(long long kFrom, long long kTo) {
        if (kFrom < 1 || kFrom > kTo || kTo > n) throw out_of_range("orOfKthLargestRange: needs 1 <= kFrom <= kTo <= size");
        T a = kthAt(n - kTo + 1);
        return orIn(a, kthAt(n - kFrom + 1));
    }

    // O(logU) -- bitwise OR of the kFrom-th..kTo-th smallest values (1-indexed, inclusive); throws out_of_range unless 1 <= kFrom <= kTo <= size
    T orOfKthSmallestRange(long long kFrom, long long kTo) {
        if (kFrom < 1 || kFrom > kTo || kTo > n) throw out_of_range("orOfKthSmallestRange: needs 1 <= kFrom <= kTo <= size");
        T a = kthAt(kFrom);
        return orIn(a, kthAt(kTo));
    }

    // O(logU) -- bitwise OR of the k largest values (0 for k = 0); throws out_of_range unless 0 <= k <= size
    T orOfLargestK(long long k) {
        if (k < 0 || k > n) throw out_of_range("orOfLargestK: needs 0 <= k <= size");
        return k ? orGe(kthAt(n - k + 1)) : T(0);
    }

    // O(logU) -- bitwise OR of the values < x; 0 if there are none
    T orOfLtX(T x) {
        if (x == numeric_limits<T>::min()) return T(0);
        return orLe(x - 1);
    }

    // O(logU) -- bitwise OR of the values <= x; 0 if there are none
    T orOfLteX(T x) {
        return orLe(x);
    }

    // O(logU) -- bitwise OR of the k smallest values (0 for k = 0); throws out_of_range unless 0 <= k <= size
    T orOfSmallestK(long long k) {
        if (k < 0 || k > n) throw out_of_range("orOfSmallestK: needs 0 <= k <= size");
        return k ? orLe(kthAt(k)) : T(0);
    }

    // O(logU) -- remove and return the value at sorted position i (0-indexed: pop(0) is popMin()); throws out_of_range unless 0 <= i < size
    T pop(long long i) {
        if (i < 0 || i >= n) throw out_of_range("pop: needs 0 <= i < size");
        T v = kthAt(i + 1);
        addRaw(v, -1);
        return v;
    }

    // O(logU) -- remove and return the largest value; nullopt if empty
    optional<T> popMax() {
        if (!n) return nullopt;
        T v = kthAt(n);
        addRaw(v, -1);
        return v;
    }

    // O(logU) -- remove and return the smallest value; nullopt if empty
    optional<T> popMin() {
        if (!n) return nullopt;
        T v = kthAt(1);
        addRaw(v, -1);
        return v;
    }

    // O(logU) -- remove one copy of x if present; returns how many were removed (0 or 1)
    long long remove(T x) {
        if (!count(x)) return 0;
        addRaw(x, -1);
        return 1;
    }

    // O(logU) -- remove every copy of val; returns how many were removed
    long long removeAll(T val) {
        long long k = count(val);
        if (k) addRaw(val, -k);
        return k;
    }

    // O(logU) -- remove min(cnt, count(val)) copies of val; returns how many were removed
    long long removeCount(T val, long long cnt) {
        long long k = std::min(cnt, count(val));
        if (k <= 0) return 0;
        addRaw(val, -k);
        return k;
    }

    // O(logU amortized) -- remove every value v with lo <= v <= hi; returns how many copies were removed (0 if lo > hi)
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

    // O(logU) -- smallest value > x; nullopt if there is none
    optional<T> smallestGtX(T x) {
        long long c = le(x);
        if (c == n) return nullopt;
        return kthAt(c + 1);
    }

    // O(logU) -- smallest value >= x; nullopt if there is none
    optional<T> smallestGteX(T x) {
        long long c = lt(x);
        if (c == n) return nullopt;
        return kthAt(c + 1);
    }

    // O(1) -- sum of |v - medianLow()| over all values (min total moves to make all equal); 0 if empty
    S sumAbsDiffToMedian() {
        if (!n) return 0;
        const Info& m = low;
        return S(m.v) * m.before - m.sb + (total - m.sb - S(m.v) * m.c) - S(m.v) * (n - m.before - m.c);
    }

    // O(logU) -- sum of |v - x| over all values
    S sumAbsDiffToX(T x) {
        long long c = lt(x);
        S s = slt(x);
        return S(x) * c - s + (total - s) - S(x) * (n - c);
    }

    // O(1) -- sum of all values
    S sumAll() {
        return total;
    }

    // O(logU) -- sum of the values > x
    S sumGtX(T x) {
        return total - sle(x);
    }

    // O(logU) -- sum of the values >= x
    S sumGteX(T x) {
        return total - slt(x);
    }

    // O(logU) -- sum of the values v with lo <= v <= hi (0 if lo > hi)
    S sumInValRange(T lo, T hi) {
        return lo <= hi ? sle(hi) - slt(lo) : S(0);
    }

    // O(logU) -- sum of the kFrom-th..kTo-th largest values (1-indexed, inclusive; (5, 8) = 5th..8th biggest); throws out_of_range unless 1 <= kFrom <= kTo <= size
    S sumKthLargestRange(long long kFrom, long long kTo) {
        if (kFrom < 1 || kFrom > kTo || kTo > n) throw out_of_range("sumKthLargestRange: needs 1 <= kFrom <= kTo <= size");
        return sumFirst(n - kFrom + 1) - sumFirst(n - kTo);
    }

    // O(logU) -- sum of the kFrom-th..kTo-th smallest values (1-indexed, inclusive); throws out_of_range unless 1 <= kFrom <= kTo <= size
    S sumKthSmallestRange(long long kFrom, long long kTo) {
        if (kFrom < 1 || kFrom > kTo || kTo > n) throw out_of_range("sumKthSmallestRange: needs 1 <= kFrom <= kTo <= size");
        return sumFirst(kTo) - sumFirst(kFrom - 1);
    }

    // O(logU) -- sum of the k largest values; throws out_of_range unless 0 <= k <= size
    S sumLargestK(long long k) {
        if (k < 0 || k > n) throw out_of_range("sumLargestK: needs 0 <= k <= size");
        return total - sumFirst(n - k);
    }

    // O(logU) -- sum of the values < x
    S sumLtX(T x) {
        return slt(x);
    }

    // O(logU) -- sum of the values <= x
    S sumLteX(T x) {
        return sle(x);
    }

    // O(logU) -- sum of the k smallest values; throws out_of_range unless 0 <= k <= size
    S sumSmallestK(long long k) {
        if (k < 0 || k > n) throw out_of_range("sumSmallestK: needs 0 <= k <= size");
        return sumFirst(k);
    }
};
