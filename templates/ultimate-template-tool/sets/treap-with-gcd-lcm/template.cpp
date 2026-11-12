// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/sets/treap-with-gcd-lcm/template.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: add addCount clear count countDistinct countGtX countGteX countInValRange countLtX countLteX firstIndex gcdOfAll gcdOfGtX gcdOfGteX gcdOfInValRange gcdOfKthLargestRange gcdOfKthSmallestRange gcdOfLargestK gcdOfLtX gcdOfLteX gcdOfSmallestK kth largestLtX largestLteX lastIndex lcmOfAll lcmOfGtX lcmOfGteX lcmOfInValRange lcmOfKthLargestRange lcmOfKthSmallestRange lcmOfLargestK lcmOfLtX lcmOfLteX lcmOfSmallestK max medianHigh medianLow min pop popMax popMin remove removeAll removeCount removeInValRange size smallestGtX smallestGteX
// @data-structure-type: treap
// @values: online
// @keys: numbers
// @tracks: none
// @complexities:
//   add: log(N)*log(U) expected
//   addCount: log(N)*log(U) expected
//   clear: 1 amortized
//   count: log(N) expected
//   countDistinct: 1
//   countGtX: log(N) expected
//   countGteX: log(N) expected
//   countInValRange: log(N) expected
//   countLtX: log(N) expected
//   countLteX: log(N) expected
//   firstIndex: log(N) expected
//   gcdOfAll: 1
//   gcdOfGtX: log(N)*log(U) expected
//   gcdOfGteX: log(N)*log(U) expected
//   gcdOfInValRange: log(N)*log(U) expected
//   gcdOfKthLargestRange: log(N)*log(U) expected
//   gcdOfKthSmallestRange: log(N)*log(U) expected
//   gcdOfLargestK: log(N)*log(U) expected
//   gcdOfLtX: log(N)*log(U) expected
//   gcdOfLteX: log(N)*log(U) expected
//   gcdOfSmallestK: log(N)*log(U) expected
//   kth: log(N) expected
//   largestLtX: log(N) expected
//   largestLteX: log(N) expected
//   lastIndex: log(N) expected
//   lcmOfAll: 1
//   lcmOfGtX: log(N)*log(U) expected
//   lcmOfGteX: log(N)*log(U) expected
//   lcmOfInValRange: log(N)*log(U) expected
//   lcmOfKthLargestRange: log(N)*log(U) expected
//   lcmOfKthSmallestRange: log(N)*log(U) expected
//   lcmOfLargestK: log(N)*log(U) expected
//   lcmOfLtX: log(N)*log(U) expected
//   lcmOfLteX: log(N)*log(U) expected
//   lcmOfSmallestK: log(N)*log(U) expected
//   max: log(N) expected
//   medianHigh: log(N) expected
//   medianLow: log(N) expected
//   min: log(N) expected
//   pop: log(N)*log(U) expected
//   popMax: log(N)*log(U) expected
//   popMin: log(N)*log(U) expected
//   remove: log(N)*log(U) expected
//   removeAll: log(N)*log(U) expected
//   removeCount: log(N)*log(U) expected
//   removeInValRange: log(N)*log(U) expected
//   size: 1
//   smallestGtX: log(N) expected
//   smallestGteX: log(N) expected
//   build: 1
// @memory:
//   layout: none
//   node: key[1*N] cnt[1*N] size[1*N] gcd[1*N] lcm[1*N]
//   tags: none
//   other: children[2*N] prio[1*N]
//   note: N = most distinct values present at once (removed nodes are reused). C++: each multiset owns its node pool; Python: parallel lists per tree
// lcmOf... answers -1 once the LCM passes cap, so it never overflows: cap is a constructor argument, the largest T
// (2^63 - 1 for long long) by default; pass your own, e.g. TreapMultiset<long long> s(1000000000LL). Removing values is
// safe: every node keeps the capped LCM of just its own values, so once the values that pushed it past cap are gone,
// lcmOf... is exact again. Values must be >= 0 (add / addCount of a negative one is an error). An empty selection gives
// the identity: gcd 0, LCM 1.

// Ordered multiset (online: any values, nothing known ahead): a treap with one node per distinct value. Each node keeps
// its value, its copies, and totals over its subtree: copies, gcd, LCM. Each multiset owns its node pool
// (freed when it goes out of scope; clear() keeps it for reuse); node 0 is the empty tree and removed nodes are reused.
// Updates split around x and merge back. T: an integer type; sums in S (long long for small T).
template <typename T>
struct TreapMultiset {
    T cap;  // lcmOf... is -1 past it
    T lc(T a, T b) const {
        // capped LCM: 0 if either is 0, else -1 if either is -1 (too big), else the LCM or -1 past cap
        if (a == 0 || b == 0) return 0;
        if (a < 0 || b < 0) return -1;
        T r;
        if (__builtin_mul_overflow(a / gcd(a, b), b, &r) || r > cap) return -1;
        return r;
    }
    template <class K>
    static K noneOf() {  // the lowest value of K, part by part for pairs and tuples
        if constexpr (is_arithmetic_v<K>) return numeric_limits<K>::lowest();
        else return apply([](auto... parts) { return K{noneOf<decltype(parts)>()...}; }, K{});
    }
    // what largestLtX, smallestGtX, ... return when nothing qualifies: compare with ms.NONE. It is the lowest T, so a
    // real value equal to it reads as "nothing"
    static inline const T NONE = noneOf<T>();

    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    struct Node { T key; long long c, z; T gcdv; T lcmv = 1; unsigned prio; int l, r; };  // copies; copies below
    vector<Node> pool{Node{}};
    vector<int> freeList;
    static inline mt19937 rng{(unsigned)chrono::steady_clock::now().time_since_epoch().count()};
    int root = 0;
    long long n = 0, d = 0;
    struct Info { T v; long long before, c; };  // a value, copies before it, its copies

    // O(1) -- an empty multiset
    explicit TreapMultiset(T cap = numeric_limits<T>::max()) : cap(cap) {}


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
        v.gcdv = gcd(gcd(a.gcdv, b.gcdv), v.key);
        v.lcmv = lc(lc(a.lcmv, b.lcmv), v.key);
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

    vector<int> path;  // scratch for insert: the nodes it walked through
    long long insert(T x, long long c) {  // returns x's new count; a value already present never needs a split or merge
        path.clear();
        int t = root, cur;
        while (t) {
            path.push_back(t);
            if (x < pool[t].key) t = pool[t].l;
            else if (pool[t].key < x) t = pool[t].r;
            else break;
        }
        long long f;
        if (t) {
            f = pool[t].c += c;
            path.pop_back();
            if (f) {
                pull(t);
                cur = t;
            } else {
                freeList.push_back(t), d--;
                cur = merge(pool[t].l, pool[t].r);
            }
        } else {
            int m = make(x);
            d++;
            f = pool[m].c = c;
            int i = 0, walked = int(path.size());
            // the new node goes where its priority belongs
            while (i < walked && pool[path[i]].prio >= pool[m].prio) i++;
            if (i < walked) {
                int a, b;
                split(path[i], x, a, b);
                pool[m].l = a, pool[m].r = b;
                path.resize(i);
            }
            pull(m);
            cur = m;
        }
        while (!path.empty()) {
            int q = path.back();
            path.pop_back();
            if (x < pool[q].key) pool[q].l = cur;
            else pool[q].r = cur;
            pull(q);
            cur = q;
        }
        root = cur;
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

    T kthAt(long long k) {
        int t = root;
        while (true) {
            long long zl = pool[pool[t].l].z;
            if (k <= zl) t = pool[t].l;
            else if (k <= zl + pool[t].c) return pool[t].key;
            else k -= zl + pool[t].c, t = pool[t].r;
        }
    }

    Info kthInfo(long long k) {  // the k-th smallest, copies before it, its copies
        int t = root;
        long long before = 0;
        while (true) {
            const Node& v = pool[t];
            long long zl = before + pool[v.l].z;
            if (k <= zl) t = v.l;
            else if (k <= zl + v.c) return {v.key, zl, v.c};
            else before = zl + v.c, t = v.r;
        }
    }


    void addRaw(T x, long long c) {  // c copies of x (c < 0 removes)
        n += c;
        insert(x, c);
    }

    void resetCached() {  // nothing counted: as newly built
        n = d = 0;
    }

    void clearData() {  // drop every node but keep the pool's memory for the next adds
        pool.resize(1), freeList.clear(), root = 0;
    }

    T gcdLe(T x) {  // gcd of the values <= x
        int t = root;
        T res = T(0);
        while (t) {
            if (x < pool[t].key) t = pool[t].l;
            else res = gcd(res, gcd(pool[pool[t].l].gcdv, pool[t].key)), t = pool[t].r;
        }
        return res;
    }

    T gcdGe(T x) {  // gcd of the values >= x
        int t = root;
        T res = T(0);
        while (t) {
            if (pool[t].key < x) t = pool[t].r;
            else res = gcd(res, gcd(pool[pool[t].r].gcdv, pool[t].key)), t = pool[t].l;
        }
        return res;
    }

    T gcdIn(T lo, T hi) {  // gcd of the values in [lo, hi] (lo <= hi)
        int t = root;
        while (t && (pool[t].key < lo || hi < pool[t].key)) {  // down to the highest node inside [lo, hi]
            t = hi < pool[t].key ? pool[t].l : pool[t].r;
        }
        if (!t) {
            return T(0);
        }
        T res = gcd(T(0), pool[t].key);
        for (int u = pool[t].l; u;) {  // its left side is <= hi: keep what is >= lo
            if (lo <= pool[u].key) res = gcd(res, gcd(pool[u].key, pool[pool[u].r].gcdv)), u = pool[u].l;
            else u = pool[u].r;
        }
        for (int u = pool[t].r; u;) {  // its right side is >= lo: keep what is <= hi
            if (pool[u].key <= hi) res = gcd(res, gcd(pool[u].key, pool[pool[u].l].gcdv)), u = pool[u].r;
            else u = pool[u].l;
        }
        return res;
    }

    T lcmLe(T x) {  // capped LCM of the values <= x
        int t = root;
        T res = T(1);
        while (t) {
            if (x < pool[t].key) t = pool[t].l;
            else res = lc(res, lc(pool[pool[t].l].lcmv, pool[t].key)), t = pool[t].r;
        }
        return res;
    }

    T lcmGe(T x) {  // capped LCM of the values >= x
        int t = root;
        T res = T(1);
        while (t) {
            if (pool[t].key < x) t = pool[t].r;
            else res = lc(res, lc(pool[pool[t].r].lcmv, pool[t].key)), t = pool[t].l;
        }
        return res;
    }

    T lcmIn(T lo, T hi) {  // capped LCM of the values in [lo, hi] (lo <= hi)
        int t = root;
        while (t && (pool[t].key < lo || hi < pool[t].key)) {  // down to the highest node inside [lo, hi]
            t = hi < pool[t].key ? pool[t].l : pool[t].r;
        }
        if (!t) {
            return T(1);
        }
        T res = lc(T(1), pool[t].key);
        for (int u = pool[t].l; u;) {  // its left side is <= hi: keep what is >= lo
            if (lo <= pool[u].key) res = lc(res, lc(pool[u].key, pool[pool[u].r].lcmv)), u = pool[u].l;
            else u = pool[u].r;
        }
        for (int u = pool[t].r; u;) {  // its right side is >= lo: keep what is <= hi
            if (pool[u].key <= hi) res = lc(res, lc(pool[u].key, pool[pool[u].l].lcmv)), u = pool[u].r;
            else u = pool[u].l;
        }
        return res;
    }

    // O(logN * logU expected) -- add one copy of x; throws invalid_argument if x < 0
    void add(T x) {
        if (x < 0) throw invalid_argument("TreapMultiset::add: negative value (the LCM needs values >= 0)");
        addRaw(x, 1);
    }

    // O(logN * logU expected) -- add cnt copies of val (nothing if cnt <= 0); throws invalid_argument if val < 0
    void addCount(T val, long long cnt) {
        if (val < 0) throw invalid_argument("TreapMultiset::addCount: negative value (the LCM needs values >= 0)");
        if (cnt > 0) addRaw(val, cnt);
    }

    // O(1) -- LCM (-1 once it passes cap) of all values; 1 if empty
    T lcmOfAll() {
        return pool[root].lcmv;
    }

    // O(logN * logU expected) -- LCM (-1 once it passes cap) of the values > x; 1 if there are none
    T lcmOfGtX(T x) {
        if (x == numeric_limits<T>::max()) return T(1);
        return lcmGe(x + 1);
    }

    // O(logN * logU expected) -- LCM (-1 once it passes cap) of the values >= x; 1 if there are none
    T lcmOfGteX(T x) {
        return lcmGe(x);
    }

    // O(logN * logU expected) -- LCM (-1 once it passes cap) of the values v with lo <= v <= hi; 1 if there are none
    T lcmOfInValRange(T lo, T hi) {
        return lo <= hi ? lcmIn(lo, hi) : T(1);
    }

    // O(logN * logU expected) -- LCM (-1 once it passes cap) of the kFrom-th through kTo-th largest values; RANKS,
    // 1-indexed and inclusive:
    // (1, 1) is just the largest, (5, 8) the 5th, 6th, 7th and 8th largest, (1, size) every value (copies count);
    // throws out_of_range unless 1 <= kFrom <= kTo <= size
    T lcmOfKthLargestRange(long long kFrom, long long kTo) {
        if (kFrom < 1 || kFrom > kTo
            || kTo > n) throw out_of_range("lcmOfKthLargestRange: needs 1 <= kFrom <= kTo <= size");
        T a = kthAt(n - kTo + 1);
        return lcmIn(a, kthAt(n - kFrom + 1));
    }

    // O(logN * logU expected) -- LCM (-1 once it passes cap) of the kFrom-th through kTo-th smallest values; RANKS,
    // 1-indexed and inclusive:
    // (1, 1) is just the smallest, (2, 4) the 2nd, 3rd and 4th smallest, (1, size) every value (copies count); throws
    // out_of_range unless 1 <= kFrom <= kTo <= size
    T lcmOfKthSmallestRange(long long kFrom, long long kTo) {
        if (kFrom < 1 || kFrom > kTo
            || kTo > n) throw out_of_range("lcmOfKthSmallestRange: needs 1 <= kFrom <= kTo <= size");
        T a = kthAt(kFrom);
        return lcmIn(a, kthAt(kTo));
    }

    // O(logN * logU expected) -- LCM (-1 once it passes cap) of the k largest values; k is a COUNT, not an index: k = 0
    // takes no values
    // (returns 1), k = 1 just the largest, k = size every value (copies count: in {2, 5, 5}, k = 2 takes 5 and 5);
    // throws out_of_range unless 0 <= k <= size
    T lcmOfLargestK(long long k) {
        if (k < 0 || k > n) throw out_of_range("lcmOfLargestK: needs 0 <= k <= size");
        return k ? lcmGe(kthAt(n - k + 1)) : T(1);
    }

    // O(logN * logU expected) -- LCM (-1 once it passes cap) of the values < x; 1 if there are none
    T lcmOfLtX(T x) {
        if (x == numeric_limits<T>::min()) return T(1);
        return lcmLe(x - 1);
    }

    // O(logN * logU expected) -- LCM (-1 once it passes cap) of the values <= x; 1 if there are none
    T lcmOfLteX(T x) {
        return lcmLe(x);
    }

    // O(logN * logU expected) -- LCM (-1 once it passes cap) of the k smallest values; k is a COUNT, not an index: k =
    // 0 takes no values
    // (returns 1), k = 1 just the smallest, k = size every value (copies count: in {2, 2, 5}, k = 2 takes 2 and 2);
    // throws out_of_range unless 0 <= k <= size
    T lcmOfSmallestK(long long k) {
        if (k < 0 || k > n) throw out_of_range("lcmOfSmallestK: needs 0 <= k <= size");
        return k ? lcmLe(kthAt(k)) : T(1);
    }

    // O(1 amortized) -- remove everything (fine on an empty set): afterwards it is as if newly built (same constructor
    // arguments), so reuse it instead of building a new one
    void clear() {
        clearData();
        resetCached();
    }

    // O(logN expected) -- how many copies of x (0 if x isn't there, e.g. on an empty set)
    long long count(T x) {
        return countOf(x);
    }

    // O(1) -- how many distinct values (0 if empty)
    long long countDistinct() {
        return d;
    }

    // O(logN expected) -- how many values > x (0 if there are none, e.g. on an empty set)
    long long countGtX(T x) {
        return n - le(x);
    }

    // O(logN expected) -- how many values >= x (0 if there are none, e.g. on an empty set)
    long long countGteX(T x) {
        return n - lt(x);
    }

    // O(logN expected) -- how many values v with lo <= v <= hi (0 if lo > hi)
    long long countInValRange(T lo, T hi) {
        return lo <= hi ? le(hi) - lt(lo) : 0;
    }

    // O(logN expected) -- how many values < x (0 if there are none, e.g. on an empty set)
    long long countLtX(T x) {
        return lt(x);
    }

    // O(logN expected) -- how many values <= x (0 if there are none, e.g. on an empty set)
    long long countLteX(T x) {
        return le(x);
    }

    // O(logN expected) -- 0-indexed position of the first copy of x in sorted order (= how many values < x); -1 if x is
    // not in the set
    long long firstIndex(T x) {
        return countOf(x) ? lt(x) : -1;
    }

    // O(logN expected) -- the value at sorted position i, 0-indexed: kth(0) is the smallest, kth(1) the 2nd smallest,
    // kth(size - 1) the largest (copies count: in {2, 2, 5}, kth(1) is 2); throws out_of_range unless 0 <= i < size
    T kth(long long i) {
        if (i < 0 || i >= n) throw out_of_range("kth: needs 0 <= i < size");
        return kthAt(i + 1);
    }

    // O(logN expected) -- largest value < x; ms.NONE if there is none
    T largestLtX(T x) {
        long long c = lt(x);
        if (!c) return NONE;
        return kthAt(c);
    }

    // O(logN expected) -- largest value <= x; ms.NONE if there is none
    T largestLteX(T x) {
        long long c = le(x);
        if (!c) return NONE;
        return kthAt(c);
    }

    // O(logN expected) -- 0-indexed position of the last copy of x in sorted order (= how many values <= x, minus 1);
    // -1 if x is not in the set
    long long lastIndex(T x) {
        return countOf(x) ? le(x) - 1 : -1;
    }

    // O(logN expected) -- largest value; throws out_of_range if empty
    T max() {
        if (!n) throw out_of_range("max: the set is empty");
        return kthAt(n);
    }

    // O(logN expected) -- upper median: the (floor(size/2) + 1)-th smallest value; throws out_of_range if empty
    T medianHigh() {
        if (!n) throw out_of_range("medianHigh: the set is empty");
        return kthAt(n / 2 + 1);
    }

    // O(logN expected) -- lower median: the ceil(size/2)-th smallest value; throws out_of_range if empty
    T medianLow() {
        if (!n) throw out_of_range("medianLow: the set is empty");
        return kthAt((n + 1) / 2);
    }

    // O(logN expected) -- smallest value; throws out_of_range if empty
    T min() {
        if (!n) throw out_of_range("min: the set is empty");
        return kthAt(1);
    }

    // O(1) -- gcd of all values; 0 if empty
    T gcdOfAll() {
        return pool[root].gcdv;
    }

    // O(logN * logU expected) -- gcd of the values > x; 0 if there are none
    T gcdOfGtX(T x) {
        if (x == numeric_limits<T>::max()) return T(0);
        return gcdGe(x + 1);
    }

    // O(logN * logU expected) -- gcd of the values >= x; 0 if there are none
    T gcdOfGteX(T x) {
        return gcdGe(x);
    }

    // O(logN * logU expected) -- gcd of the values v with lo <= v <= hi; 0 if there are none
    T gcdOfInValRange(T lo, T hi) {
        return lo <= hi ? gcdIn(lo, hi) : T(0);
    }

    // O(logN * logU expected) -- gcd of the kFrom-th through kTo-th largest values; RANKS, 1-indexed and inclusive:
    // (1, 1) is just the largest, (5, 8) the 5th, 6th, 7th and 8th largest, (1, size) every value (copies count);
    // throws out_of_range unless 1 <= kFrom <= kTo <= size
    T gcdOfKthLargestRange(long long kFrom, long long kTo) {
        if (kFrom < 1 || kFrom > kTo
            || kTo > n) throw out_of_range("gcdOfKthLargestRange: needs 1 <= kFrom <= kTo <= size");
        T a = kthAt(n - kTo + 1);
        return gcdIn(a, kthAt(n - kFrom + 1));
    }

    // O(logN * logU expected) -- gcd of the kFrom-th through kTo-th smallest values; RANKS, 1-indexed and inclusive:
    // (1, 1) is just the smallest, (2, 4) the 2nd, 3rd and 4th smallest, (1, size) every value (copies count); throws
    // out_of_range unless 1 <= kFrom <= kTo <= size
    T gcdOfKthSmallestRange(long long kFrom, long long kTo) {
        if (kFrom < 1 || kFrom > kTo
            || kTo > n) throw out_of_range("gcdOfKthSmallestRange: needs 1 <= kFrom <= kTo <= size");
        T a = kthAt(kFrom);
        return gcdIn(a, kthAt(kTo));
    }

    // O(logN * logU expected) -- gcd of the k largest values; k is a COUNT, not an index: k = 0 takes no values
    // (returns 0), k = 1 just the largest, k = size every value (copies count: in {2, 5, 5}, k = 2 takes 5 and 5);
    // throws out_of_range unless 0 <= k <= size
    T gcdOfLargestK(long long k) {
        if (k < 0 || k > n) throw out_of_range("gcdOfLargestK: needs 0 <= k <= size");
        return k ? gcdGe(kthAt(n - k + 1)) : T(0);
    }

    // O(logN * logU expected) -- gcd of the values < x; 0 if there are none
    T gcdOfLtX(T x) {
        if (x == numeric_limits<T>::min()) return T(0);
        return gcdLe(x - 1);
    }

    // O(logN * logU expected) -- gcd of the values <= x; 0 if there are none
    T gcdOfLteX(T x) {
        return gcdLe(x);
    }

    // O(logN * logU expected) -- gcd of the k smallest values; k is a COUNT, not an index: k = 0 takes no values
    // (returns 0), k = 1 just the smallest, k = size every value (copies count: in {2, 2, 5}, k = 2 takes 2 and 2);
    // throws out_of_range unless 0 <= k <= size
    T gcdOfSmallestK(long long k) {
        if (k < 0 || k > n) throw out_of_range("gcdOfSmallestK: needs 0 <= k <= size");
        return k ? gcdLe(kthAt(k)) : T(0);
    }

    // O(logN * logU expected) -- remove and return the value at sorted position i, 0-indexed: pop(0) removes the
    // smallest (=
    // popMin()), pop(size - 1) the largest (copies count); throws out_of_range unless 0 <= i < size
    T pop(long long i) {
        if (i < 0 || i >= n) throw out_of_range("pop: needs 0 <= i < size");
        T v = kthAt(i + 1);
        addRaw(v, -1);
        return v;
    }

    // O(logN * logU expected) -- remove and return the largest value; throws out_of_range if empty
    T popMax() {
        if (!n) throw out_of_range("popMax: the set is empty");
        T v = kthAt(n);
        addRaw(v, -1);
        return v;
    }

    // O(logN * logU expected) -- remove and return the smallest value; throws out_of_range if empty
    T popMin() {
        if (!n) throw out_of_range("popMin: the set is empty");
        T v = kthAt(1);
        addRaw(v, -1);
        return v;
    }

    // O(logN * logU expected) -- remove one copy of x if present; returns how many were removed (0 or 1: 0 if x isn't
    // there, e.g. on an empty set)
    long long remove(T x) {
        if (!count(x)) return 0;
        addRaw(x, -1);
        return 1;
    }

    // O(logN * logU expected) -- remove every copy of val; returns how many were removed (0 if val isn't there, e.g. on
    // an empty set)
    long long removeAll(T val) {
        long long k = count(val);
        if (k) addRaw(val, -k);
        return k;
    }

    // O(logN * logU expected) -- remove min(cnt, count(val)) copies of val; returns how many were removed (0 if val
    // isn't there, e.g. on an empty set)
    long long removeCount(T val, long long cnt) {
        long long k = std::min(cnt, count(val));
        if (k <= 0) return 0;
        addRaw(val, -k);
        return k;
    }

    // O(logN * logU expected) -- remove every value v with lo <= v <= hi; returns how many copies were removed (0 if lo
    // > hi)
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

    // O(1) -- how many values (copies count; 0 if empty)
    long long size() {
        return n;
    }

    // O(logN expected) -- smallest value > x; ms.NONE if there is none
    T smallestGtX(T x) {
        long long c = le(x);
        if (c == n) return NONE;
        return kthAt(c + 1);
    }

    // O(logN expected) -- smallest value >= x; ms.NONE if there is none
    T smallestGteX(T x) {
        long long c = lt(x);
        if (c == n) return NONE;
        return kthAt(c + 1);
    }
};
