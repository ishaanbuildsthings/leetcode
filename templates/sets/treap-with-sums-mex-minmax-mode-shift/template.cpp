// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/sets/treap-with-sums-mex-minmax-mode-shift/template.cpp
// @operations: add addCount clear count countDistinct countDistinctInValRange countGtX countGteX countInValRange countLtX countLteX firstIndex kth largestLtX largestLteX lastIndex max medianHigh medianLow mex min mode pop popMax popMin remove removeAll removeCount removeInValRange shiftAll size smallestGtX smallestGteX sumAbsDiffToMedian sumAbsDiffToX sumAll sumGtX sumGteX sumInValRange sumKthLargestRange sumKthSmallestRange sumLargestK sumLtX sumLteX sumSmallestK
// @data-structure-type: treap
// @values: online
// @keys: numbers
// @tracks: minmax mode shift
// @complexities:
//   add: log(N) expected
//   addCount: log(N) expected
//   clear: N
//   count: log(N) expected
//   countDistinct: 1
//   countDistinctInValRange: log(N) expected
//   countGtX: log(N) expected
//   countGteX: log(N) expected
//   countInValRange: log(N) expected
//   countLtX: log(N) expected
//   countLteX: log(N) expected
//   firstIndex: log(N) expected
//   kth: log(N) expected
//   largestLtX: log(N) expected
//   largestLteX: log(N) expected
//   lastIndex: log(N) expected
//   max: 1
//   medianHigh: log(N) expected
//   medianLow: log(N) expected
//   mex: log(N) expected
//   min: 1
//   mode: 1
//   pop: log(N) expected
//   popMax: log(N) expected
//   popMin: log(N) expected
//   remove: log(N) expected
//   removeAll: log(N) expected
//   removeCount: log(N) expected
//   removeInValRange: log(N) expected
//   shiftAll: 1
//   size: 1
//   smallestGtX: log(N) expected
//   smallestGteX: log(N) expected
//   sumAbsDiffToMedian: log(N) expected
//   sumAbsDiffToX: log(N) expected
//   sumAll: 1
//   sumGtX: log(N) expected
//   sumGteX: log(N) expected
//   sumInValRange: log(N) expected
//   sumKthLargestRange: log(N) expected
//   sumKthSmallestRange: log(N) expected
//   sumLargestK: log(N) expected
//   sumLtX: log(N) expected
//   sumLteX: log(N) expected
//   sumSmallestK: log(N) expected
//   build: 1
// @memory:
//   layout: none
//   node: key[1*N] cnt[1*N] size[1*N] dn[1*N] sum[1*N]
//   tags: none
//   other: children[2*N] prio[1*N]
//   note: N = most distinct values present at once (removed nodes are reused). C++: each multiset owns its node pool; Python: parallel lists per tree

// Ordered multiset (online: any values, nothing known ahead): a treap with one node per distinct value. Each node keeps
// its value, its copies, and the copies, sum and distinct values in its subtree. Each multiset owns its node pool
// (freed when it goes out of scope; clear() keeps it for reuse); node 0 is the empty tree and removed nodes are reused.
// Updates split around x and merge back. T: an integer type; sums in S (long long for small T).
template <typename T>
struct TreapMultiset {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    struct Node { T key; long long c, z; S s; long long dn; unsigned prio; int l, r; };  // copies; copies, sum, distinct below
    vector<Node> pool{Node{}};
    vector<int> freeList;
    static inline mt19937 rng{(unsigned)chrono::steady_clock::now().time_since_epoch().count()};
    int root = 0;
    long long n = 0, d = 0;
    struct Info { T v; long long before, c; S sb; };  // a value, copies before it, its copies, sum before it
    T mn{}, mx{};  // kept current by addRaw while n > 0
    map<long long, set<T>> bk;  // mode: count -> the values with that many copies
    T off = 0;  // every value v is stored as v - off: shiftAll only moves off
    S total = 0;

    // O(1) -- an empty multiset
    TreapMultiset() {}


    // optional -- reserve room for this many nodes up front
    void reservePool(size_t nodes) { pool.reserve(nodes); }

    int make(T x) {
        int t;
        if (!freeList.empty()) t = freeList.back(), freeList.pop_back();
        else pool.push_back(Node{}), t = (int)pool.size() - 1;
        pool[t] = Node{};
        pool[t].key = x, pool[t].prio = rng();
        return t;
    }

    void pull(int t) {
        Node& v = pool[t];
        const Node &a = pool[v.l], &b = pool[v.r];
        v.z = a.z + b.z + v.c;
        v.dn = a.dn + b.dn + 1;
        v.s = a.s + b.s + S(v.c) * v.key;
    }

    void split(int t, T x, int& a, int& b) {  // (keys < x, keys >= x)
        if (!t) {
            a = b = 0;
            return;
        }
        if (pool[t].key < x) {
            int ra, rb;
            split(pool[t].r, x, ra, rb);
            pool[t].r = ra, pull(t), a = t, b = rb;
        } else {
            int la, lb;
            split(pool[t].l, x, la, lb);
            pool[t].l = lb, pull(t), a = la, b = t;
        }
    }

    void splitLe(int t, const T& x, int& a, int& b) {  // a: keys <= x, b: keys > x
        if (!t) {
            a = b = 0;
            return;
        }
        if (x < pool[t].key) {
            int la, lb;
            splitLe(pool[t].l, x, la, lb);
            pool[t].l = lb, pull(t), a = la, b = t;
        } else {
            int ra, rb;
            splitLe(pool[t].r, x, ra, rb);
            pool[t].r = ra, pull(t), a = t, b = rb;
        }
    }

    int merge(int a, int b) {  // every key in a < every key in b
        if (!a || !b) return a ? a : b;
        if (pool[a].prio > pool[b].prio) {
            int r = merge(pool[a].r, b);
            pool[a].r = r, pull(a);
            return a;
        }
        int l = merge(a, pool[b].l);
        pool[b].l = l, pull(b);
        return b;
    }

    long long insert(T x, long long c) {  // returns x's new count
        int a, b, m;
        split(root, x, a, b);
        splitLe(b, x, m, b);  // m: the node of x, or 0
        if (!m) m = make(x), d++;
        long long f = pool[m].c += c;
        if (f) pull(m);
        else freeList.push_back(m), m = 0, d--;
        root = merge(merge(a, m), b);
        return f;
    }

    long long lt(T x) {  // copies of values < x
        int t = root;
        long long res = 0;
        while (t) {
            if (pool[t].key < x) res += pool[pool[t].l].z + pool[t].c, t = pool[t].r;
            else t = pool[t].l;
        }
        return res;
    }

    long long le(T x) {  // copies of values <= x
        int t = root;
        long long res = 0;
        while (t) {
            if (x < pool[t].key) t = pool[t].l;
            else res += pool[pool[t].l].z + pool[t].c, t = pool[t].r;
        }
        return res;
    }

    long long countOf(T x) {
        int t = root;
        while (t && pool[t].key != x) t = x < pool[t].key ? pool[t].l : pool[t].r;
        return pool[t].c;
    }

    S slt(T x) {  // sum of the values < x
        int t = root;
        S res = 0;
        while (t) {
            if (pool[t].key < x) res += pool[pool[t].l].s + S(pool[t].c) * pool[t].key, t = pool[t].r;
            else t = pool[t].l;
        }
        return res;
    }

    S sle(T x) {  // sum of the values <= x
        int t = root;
        S res = 0;
        while (t) {
            if (x < pool[t].key) t = pool[t].l;
            else res += pool[pool[t].l].s + S(pool[t].c) * pool[t].key, t = pool[t].r;
        }
        return res;
    }

    T kthAt(long long k) {
        int t = root;
        while (true) {
            long long zl = pool[pool[t].l].z;
            if (k <= zl) t = pool[t].l;
            else if (k <= zl + pool[t].c) return pool[t].key;
            else k -= zl + pool[t].c, t = pool[t].r;
        }
    }

    Info kthInfo(long long k) {  // the k-th smallest, copies before it, its copies, sum before it
        int t = root;
        long long before = 0;
        S acc = 0;
        while (true) {
            const Node& v = pool[t];
            long long zl = before + pool[v.l].z;
            if (k <= zl) t = v.l;
            else if (k <= zl + v.c) return {v.key, zl, v.c, acc + pool[v.l].s};
            else before = zl + v.c, acc += pool[v.l].s + S(v.c) * v.key, t = v.r;
        }
    }

    long long distinctLt(T x) {  // distinct values < x
        int t = root;
        long long res = 0;
        while (t) {
            if (pool[t].key < x) res += pool[pool[t].l].dn + 1, t = pool[t].r;
            else t = pool[t].l;
        }
        return res;
    }

    // smallest non-negative integer not in the set. With c0 distinct negatives, the distinct values >= 0
    // in order v_0 < v_1 < ... satisfy v_j >= j, and v_j == j means 0..v_j are all present; the answer is the first j
    // with v_j > j (or how many there are). One walk down: at a node of distinct rank c0 + j, go right if v_j == j.
    long long findMex() {
        T base = -off;  // (stored as v - off: the real values >= 0 are the stored ones >= -off)
        long long c0 = distinctLt(base), before = -c0, res = d - c0;  // before: distinct values >= 0 left of t's subtree
        int t = root;
        while (t) {
            long long j = before + pool[pool[t].l].dn;
            if (pool[t].key < base || pool[t].key == T(base + j)) before = j + 1, t = pool[t].r;
            else res = j, t = pool[t].l;
        }
        return base + res;  // (a stored value)
    }

    void addRaw(T x, long long c) {  // c copies of x (c < 0 removes); keeps min / max current
        n += c;
        total += S(c) * x;
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
        bk.clear();
        n = d = 0;
        total = 0;
        off = 0;
    }

    void clearData() {  // drop every node but keep the pool's memory for the next adds
        pool.resize(1), freeList.clear(), root = 0;
    }

    // O(logN expected) -- add one copy of x
    void add(T x) {
        x -= off;
        addRaw(x, 1);
    }

    // O(logN expected) -- add cnt copies of val (nothing if cnt <= 0)
    void addCount(T val, long long cnt) {
        val -= off;
        if (cnt > 0) addRaw(val, cnt);
    }

    // O(N) -- remove everything: afterwards it is as if newly built (same constructor arguments), so reuse it instead of building a new one
    void clear() {
        clearData();
        resetCached();
    }

    // O(logN expected) -- how many copies of x
    long long count(T x) {
        x -= off;
        return countOf(x);
    }

    // O(1) -- how many distinct values
    long long countDistinct() {
        return d;
    }

    // O(logN expected) -- how many distinct values v with lo <= v <= hi (0 if lo > hi)
    long long countDistinctInValRange(T lo, T hi) {
        lo -= off, hi -= off;
        if (hi < lo) return 0;
        return distinctLt(hi) - distinctLt(lo) + (countOf(hi) ? 1 : 0);
    }

    // O(logN expected) -- how many values > x
    long long countGtX(T x) {
        x -= off;
        return n - le(x);
    }

    // O(logN expected) -- how many values >= x
    long long countGteX(T x) {
        x -= off;
        return n - lt(x);
    }

    // O(logN expected) -- how many values v with lo <= v <= hi (0 if lo > hi)
    long long countInValRange(T lo, T hi) {
        lo -= off, hi -= off;
        return lo <= hi ? le(hi) - lt(lo) : 0;
    }

    // O(logN expected) -- how many values < x
    long long countLtX(T x) {
        x -= off;
        return lt(x);
    }

    // O(logN expected) -- how many values <= x
    long long countLteX(T x) {
        x -= off;
        return le(x);
    }

    // O(logN expected) -- 0-indexed position of the first copy of x in sorted order (= how many values < x); -1 if x is not in the set
    long long firstIndex(T x) {
        x -= off;
        return countOf(x) ? lt(x) : -1;
    }

    // O(logN expected) -- the value at sorted position i (0-indexed: kth(0) is the min); throws out_of_range unless 0 <= i < size
    T kth(long long i) {
        if (i < 0 || i >= n) throw out_of_range("kth: needs 0 <= i < size");
        return T(kthAt(i + 1) + off);
    }

    // O(logN expected) -- largest value < x; nullopt if there is none
    optional<T> largestLtX(T x) {
        x -= off;
        long long c = lt(x);
        if (!c) return nullopt;
        return T(kthAt(c) + off);
    }

    // O(logN expected) -- largest value <= x; nullopt if there is none
    optional<T> largestLteX(T x) {
        x -= off;
        long long c = le(x);
        if (!c) return nullopt;
        return T(kthAt(c) + off);
    }

    // O(logN expected) -- 0-indexed position of the last copy of x in sorted order (= how many values <= x, minus 1); -1 if x is not in the set
    long long lastIndex(T x) {
        x -= off;
        return countOf(x) ? le(x) - 1 : -1;
    }

    // O(1) -- largest value; nullopt if empty
    optional<T> max() {
        if (!n) return nullopt;
        return T(mx + off);
    }

    // O(logN expected) -- upper median: the (floor(size/2) + 1)-th smallest value; nullopt if empty
    optional<T> medianHigh() {
        if (!n) return nullopt;
        return T(kthAt(n / 2 + 1) + off);
    }

    // O(logN expected) -- lower median: the ceil(size/2)-th smallest value; nullopt if empty
    optional<T> medianLow() {
        if (!n) return nullopt;
        return T(kthAt((n + 1) / 2) + off);
    }

    // O(logN expected) -- smallest non-negative integer not in the set
    long long mex() {
        return findMex() + off;
    }

    // O(1) -- smallest value; nullopt if empty
    optional<T> min() {
        if (!n) return nullopt;
        return T(mn + off);
    }

    // O(1) -- (a most frequent value, its count); nullopt if empty. C++ returns the smallest of the most frequent values
    optional<pair<T, long long>> mode() {
        if (!n) return nullopt;
        auto& [f, vs] = *bk.rbegin();
        return pair<T, long long>{T(*vs.begin() + off), f};
    }

    // O(logN expected) -- remove and return the value at sorted position i (0-indexed: pop(0) is popMin()); throws out_of_range unless 0 <= i < size
    T pop(long long i) {
        if (i < 0 || i >= n) throw out_of_range("pop: needs 0 <= i < size");
        T v = kthAt(i + 1);
        addRaw(v, -1);
        return T(v + off);
    }

    // O(logN expected) -- remove and return the largest value; nullopt if empty
    optional<T> popMax() {
        if (!n) return nullopt;
        T v = mx;
        addRaw(v, -1);
        return T(v + off);
    }

    // O(logN expected) -- remove and return the smallest value; nullopt if empty
    optional<T> popMin() {
        if (!n) return nullopt;
        T v = mn;
        addRaw(v, -1);
        return T(v + off);
    }

    // O(logN expected) -- remove one copy of x if present; returns how many were removed (0 or 1)
    long long remove(T x) {
        x -= off;
        if (!countOf(x)) return 0;
        addRaw(x, -1);
        return 1;
    }

    // O(logN expected) -- remove every copy of val; returns how many were removed
    long long removeAll(T val) {
        val -= off;
        long long k = countOf(val);
        if (k) addRaw(val, -k);
        return k;
    }

    // O(logN expected) -- remove min(cnt, count(val)) copies of val; returns how many were removed
    long long removeCount(T val, long long cnt) {
        val -= off;
        long long k = std::min(cnt, countOf(val));
        if (k <= 0) return 0;
        addRaw(val, -k);
        return k;
    }

    // O(logN expected) -- remove every value v with lo <= v <= hi; returns how many copies were removed (0 if lo > hi)
    long long removeInValRange(T lo, T hi) {
        lo -= off, hi -= off;
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

    // O(1) -- add d to every value (d may be negative)
    void shiftAll(T d) {
        off += d;
    }

    // O(1) -- how many values (copies count)
    long long size() {
        return n;
    }

    // O(logN expected) -- smallest value > x; nullopt if there is none
    optional<T> smallestGtX(T x) {
        x -= off;
        long long c = le(x);
        if (c == n) return nullopt;
        return T(kthAt(c + 1) + off);
    }

    // O(logN expected) -- smallest value >= x; nullopt if there is none
    optional<T> smallestGteX(T x) {
        x -= off;
        long long c = lt(x);
        if (c == n) return nullopt;
        return T(kthAt(c + 1) + off);
    }

    // O(logN expected) -- sum of |v - medianLow()| over all values (min total moves to make all equal); 0 if empty
    S sumAbsDiffToMedian() {
        if (!n) return 0;
        Info m = kthInfo((n + 1) / 2);
        return S(m.v) * m.before - m.sb + (total - m.sb - S(m.v) * m.c) - S(m.v) * (n - m.before - m.c);
    }

    // O(logN expected) -- sum of |v - x| over all values
    S sumAbsDiffToX(T x) {
        x -= off;
        long long c = lt(x);
        S s = slt(x);
        return S(x) * c - s + (total - s) - S(x) * (n - c);
    }

    // O(1) -- sum of all values
    S sumAll() {
        return total + S(off) * n;
    }

    // O(logN expected) -- sum of the values > x
    S sumGtX(T x) {
        x -= off;
        return total - sle(x) + S(off) * (n - le(x));
    }

    // O(logN expected) -- sum of the values >= x
    S sumGteX(T x) {
        x -= off;
        return total - slt(x) + S(off) * (n - lt(x));
    }

    // O(logN expected) -- sum of the values v with lo <= v <= hi (0 if lo > hi)
    S sumInValRange(T lo, T hi) {
        if (hi < lo) return 0;
        lo -= off, hi -= off;
        return sle(hi) - slt(lo) + S(off) * (le(hi) - lt(lo));
    }

    // O(logN expected) -- sum of the kFrom-th..kTo-th largest values (1-indexed, inclusive; (5, 8) = 5th..8th biggest); throws out_of_range unless 1 <= kFrom <= kTo <= size
    S sumKthLargestRange(long long kFrom, long long kTo) {
        if (kFrom < 1 || kFrom > kTo || kTo > n) throw out_of_range("sumKthLargestRange: needs 1 <= kFrom <= kTo <= size");
        return sumFirst(n - kFrom + 1) - sumFirst(n - kTo) + S(off) * (kTo - kFrom + 1);
    }

    // O(logN expected) -- sum of the kFrom-th..kTo-th smallest values (1-indexed, inclusive); throws out_of_range unless 1 <= kFrom <= kTo <= size
    S sumKthSmallestRange(long long kFrom, long long kTo) {
        if (kFrom < 1 || kFrom > kTo || kTo > n) throw out_of_range("sumKthSmallestRange: needs 1 <= kFrom <= kTo <= size");
        return sumFirst(kTo) - sumFirst(kFrom - 1) + S(off) * (kTo - kFrom + 1);
    }

    // O(logN expected) -- sum of the k largest values; throws out_of_range unless 0 <= k <= size
    S sumLargestK(long long k) {
        if (k < 0 || k > n) throw out_of_range("sumLargestK: needs 0 <= k <= size");
        return total - sumFirst(n - k) + S(off) * k;
    }

    // O(logN expected) -- sum of the values < x
    S sumLtX(T x) {
        x -= off;
        return slt(x) + S(off) * lt(x);
    }

    // O(logN expected) -- sum of the values <= x
    S sumLteX(T x) {
        x -= off;
        return sle(x) + S(off) * le(x);
    }

    // O(logN expected) -- sum of the k smallest values; throws out_of_range unless 0 <= k <= size
    S sumSmallestK(long long k) {
        if (k < 0 || k > n) throw out_of_range("sumSmallestK: needs 0 <= k <= size");
        return sumFirst(k) + S(off) * k;
    }
};
