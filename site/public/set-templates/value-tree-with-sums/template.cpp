// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/sets/value-tree-with-sums/template.cpp
// @operations: add addCount count countDistinct countGtX countGteX countInValRange countLtX countLteX kthLargest kthSmallest largestLtX largestLteX max medianHigh medianLow min popMax popMin remove removeAll removeCount size smallestGtX smallestGteX sumAbsDiffToMedian sumAbsDiffToX sumAll sumGtX sumGteX sumInValRange sumKthLargestRange sumKthSmallestRange sumLargestK sumLtX sumLteX sumSmallestK
// @data-structure-type: value-tree
// @values: online-range
// @complexities:
//   add: log(U)
//   addCount: log(U)
//   count: log(U)
//   countDistinct: 1
//   countGtX: log(U)
//   countGteX: log(U)
//   countInValRange: log(U)
//   countLtX: log(U)
//   countLteX: log(U)
//   kthLargest: log(U)
//   kthSmallest: log(U)
//   largestLtX: log(U)
//   largestLteX: log(U)
//   max: 1
//   medianHigh: 1 amortized
//   medianLow: 1 amortized
//   min: 1
//   popMax: log(U)
//   popMin: log(U)
//   remove: log(U)
//   removeAll: log(U)
//   removeCount: log(U)
//   size: 1
//   smallestGtX: log(U)
//   smallestGteX: log(U)
//   sumAbsDiffToMedian: 1 amortized
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
//   node: c[1*log(U)] s[1*log(U)]
//   tags: none
//   other: children[2*log(U)]
//   note: per add of a new value, one node per level of its root path; U = hi - lo + 1. C++: one shared node pool (node 0 = empty), call resetPool() between test cases; Python: dicts keyed by heap index

// Ordered multiset of integers in a known range [lo, hi] (values not known ahead): a dynamic tree over the value range,
// each node keeping how many copies, their sum, are below it. Nodes live in one pool
// shared by every ValueTreeMultiset<T> (call resetPool() between test cases); node 0 is the shared empty block.
// k-th / sums of the k smallest descend by counts.
// T: int, long long, ...; sums in S (long long for small T).
template <typename T>
struct ValueTreeMultiset {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    struct Node { long long c; S s; int l, r; };  // copies, sum below
    static inline vector<Node> pool{Node{}};  // node 0: empty, its children are itself
    long long lo, hi, n = 0, d = 0;
    struct Info { T v; long long before, c; S sb; };  // a value, copies before it, its copies, sum before it
    T mn{}, mx{};  // kept current by addRaw while n > 0
    bool med = false;  // medians (low, high) are tracked from the first median query on
    Info low{}, high{};
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

    void insert(T x, long long c) {
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
            v.s += S(c) * x;
        }
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

    T kth(long long k) {
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

    void addRaw(T x, long long c) {  // c copies of x (c < 0 removes); keeps min / max (and medians / mex once asked for) current
        n += c;
        total += S(c) * x;
        insert(x, c);
        if (c > 0) {
            if (n == c) {  // the set was empty
                mn = mx = x;
                if (med) low = high = Info{x, 0, c, 0};
                return;
            }
            if (x < mn) mn = x;
            if (x > mx) mx = x;
        } else {
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

    // O(logU) -- add one copy of x
    void add(T x) {
        addRaw(x, 1);
    }

    // O(logU) -- add c copies of x (nothing if c <= 0)
    void addCount(T x, long long c) {
        if (c > 0) addRaw(x, c);
    }

    // O(logU) -- how many copies of x
    long long count(T x) {
        return countOf(x);
    }

    // O(1) -- how many distinct values
    long long countDistinct() {
        return d;
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

    // O(logU) -- k-th largest value (1-indexed); throws out_of_range unless 1 <= k <= size
    T kthLargest(long long k) {
        if (k < 1 || k > n) throw out_of_range("kthLargest: needs 1 <= k <= size");
        return kth(n - k + 1);
    }

    // O(logU) -- k-th smallest value (1-indexed); throws out_of_range unless 1 <= k <= size
    T kthSmallest(long long k) {
        if (k < 1 || k > n) throw out_of_range("kthSmallest: needs 1 <= k <= size");
        return kth(k);
    }

    // O(logU) -- largest value < x; nullopt if there is none
    optional<T> largestLtX(T x) {
        long long c = lt(x);
        if (!c) return nullopt;
        return kth(c);
    }

    // O(logU) -- largest value <= x; nullopt if there is none
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

    // O(1) -- smallest value; nullopt if empty
    optional<T> min() {
        if (!n) return nullopt;
        return mn;
    }

    // O(logU) -- remove and return the largest value; nullopt if empty
    optional<T> popMax() {
        if (!n) return nullopt;
        T v = mx;
        addRaw(v, -1);
        return v;
    }

    // O(logU) -- remove and return the smallest value; nullopt if empty
    optional<T> popMin() {
        if (!n) return nullopt;
        T v = mn;
        addRaw(v, -1);
        return v;
    }

    // O(logU) -- remove one copy of x if present; returns how many were removed (0 or 1)
    long long remove(T x) {
        if (!count(x)) return 0;
        addRaw(x, -1);
        return 1;
    }

    // O(logU) -- remove every copy of x; returns how many were removed
    long long removeAll(T x) {
        long long k = count(x);
        if (k) addRaw(x, -k);
        return k;
    }

    // O(logU) -- remove min(c, count(x)) copies of x; returns how many were removed
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

    // O(logU) -- smallest value > x; nullopt if there is none
    optional<T> smallestGtX(T x) {
        long long c = le(x);
        if (c == n) return nullopt;
        return kth(c + 1);
    }

    // O(logU) -- smallest value >= x; nullopt if there is none
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

    // O(logU) -- sum of the i-th..j-th largest values (1-indexed, inclusive; (5, 8) = 5th..8th biggest); throws out_of_range unless 1 <= i <= j <= size
    S sumKthLargestRange(long long i, long long j) {
        if (i < 1 || i > j || j > n) throw out_of_range("sumKthLargestRange: needs 1 <= i <= j <= size");
        return sumFirst(n - i + 1) - sumFirst(n - j);
    }

    // O(logU) -- sum of the i-th..j-th smallest values (1-indexed, inclusive); throws out_of_range unless 1 <= i <= j <= size
    S sumKthSmallestRange(long long i, long long j) {
        if (i < 1 || i > j || j > n) throw out_of_range("sumKthSmallestRange: needs 1 <= i <= j <= size");
        return sumFirst(j) - sumFirst(i - 1);
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
