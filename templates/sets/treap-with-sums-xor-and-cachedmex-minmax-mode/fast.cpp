// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/sets/treap-with-sums-xor-and-cachedmex-minmax-mode/fast.cpp
// @operations: add addCount andOfAll andOfGtX andOfGteX andOfInValRange andOfKthLargestRange andOfKthSmallestRange andOfLargestK andOfLtX andOfLteX andOfSmallestK clear count countDistinct countDistinctInValRange countGtX countGteX countInValRange countLtX countLteX firstIndex kth largestLtX largestLteX lastIndex max medianHigh medianLow mex min mode pop popMax popMin remove removeAll removeCount removeInValRange size smallestGtX smallestGteX sumAbsDiffToMedian sumAbsDiffToX sumAll sumGtX sumGteX sumInValRange sumKthLargestRange sumKthSmallestRange sumLargestK sumLtX sumLteX sumSmallestK xorOfAll xorOfGtX xorOfGteX xorOfInValRange xorOfKthLargestRange xorOfKthSmallestRange xorOfLargestK xorOfLtX xorOfLteX xorOfSmallestK
// @data-structure-type: treap
// @values: online
// @keys: numbers
// @tracks: minmax mex mode
// @complexities:
//   add: log(N) expected
//   addCount: log(N) expected
//   andOfAll: 1
//   andOfGtX: log(N) expected
//   andOfGteX: log(N) expected
//   andOfInValRange: log(N) expected
//   andOfKthLargestRange: log(N) expected
//   andOfKthSmallestRange: log(N) expected
//   andOfLargestK: log(N) expected
//   andOfLtX: log(N) expected
//   andOfLteX: log(N) expected
//   andOfSmallestK: log(N) expected
//   clear: 1 amortized
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
//   mex: 1
//   min: 1
//   mode: 1
//   pop: log(N) expected
//   popMax: log(N) expected
//   popMin: log(N) expected
//   remove: log(N) expected
//   removeAll: log(N) expected
//   removeCount: log(N) expected
//   removeInValRange: log(N) expected
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
//   xorOfAll: 1
//   xorOfGtX: log(N) expected
//   xorOfGteX: log(N) expected
//   xorOfInValRange: log(N) expected
//   xorOfKthLargestRange: log(N) expected
//   xorOfKthSmallestRange: log(N) expected
//   xorOfLargestK: log(N) expected
//   xorOfLtX: log(N) expected
//   xorOfLteX: log(N) expected
//   xorOfSmallestK: log(N) expected
//   build: 1
// @memory:
//   layout: none
//   node: key[1*N] cnt[1*N] size[1*N] dn[1*N] sum[1*N] xor[1*N] and[1*N]
//   tags: none
//   other: children[2*N] prio[1*N]
//   note: N = most distinct values present at once (removed nodes are reused). C++: each multiset owns its node pool; Python: parallel lists per tree

// Ordered multiset (online: any values, nothing known ahead): a treap with one node per distinct value. Each node keeps
// its value, its copies, and the copies, sum, xor, AND and distinct values in its subtree. Each multiset owns its node pool
// (freed when it goes out of scope; clear() keeps it for reuse); node 0 is the empty tree and removed nodes are reused.
// Updates split around x and merge back. T: an integer type; sums in S (long long for small T).
// FAST MODE drawbacks compared with template.cpp:
//   - sanitizers are skipped inside this template, so a bad access in it goes unreported
// Same public operations and answers, same limits; it needs GCC or Clang and C++17.
#ifdef __SSE2__
#include <immintrin.h>
#endif

// LEETCODE_NO_SANITIZE skips sanitizers in a function. It only changes anything where sanitizers run, like LeetCode: on
// Codeforces it compiles and does nothing.
// This template already uses it. To go further, put it on the one function with your hot loop:
//   LEETCODE_NO_SANITIZE long long maxSum(vector<int>& nums, int k) {
// A lambda needs its own: [&](int x) LEETCODE_NO_SANITIZE { ... }. It does not carry into anything that function calls.
// Inside a marked function use raw pointers and plain comparisons, not vector[] and min / max, or it can get slower.
// Bad memory accesses in a marked function go unreported.
#ifndef LEETCODE_NO_SANITIZE
#define LEETCODE_NO_SANITIZE __attribute__((no_sanitize("address"), no_sanitize("undefined")))
#endif
#define LEETCODE_NO_SANITIZE_INLINE LEETCODE_NO_SANITIZE __attribute__((always_inline)) inline

// A minimal growable array: unlike vector, its accessors always inline, even with sanitizers skipped
template <typename U>
struct FlatPool {
    U* items = nullptr;
    int count = 0, room = 0;
    explicit FlatPool(int size = 0) { resize(size); }
    FlatPool(const FlatPool& other) { *this = other; }
    FlatPool& operator=(const FlatPool& other) {
        if (this == &other) return *this;
        delete[] items;
        count = room = other.count;
        items = count ? new U[count] : nullptr;
        std::copy(other.items, other.items + count, items);
        return *this;
    }
    ~FlatPool() { delete[] items; }
    void reserve(size_t want) {
        if ((long long)want <= room) return;
        U* grown = new U[want];
        std::copy(items, items + count, grown);
        delete[] items;
        items = grown, room = (int)want;
    }
    void resize(int size) {
        reserve(size);
        for (int i = count; i < size; i++) items[i] = U{};
        count = size;
    }
    LEETCODE_NO_SANITIZE_INLINE void push_back(const U& value) {
        if (count == room) reserve(room ? 2LL * room : 16);
        items[count++] = value;
    }
    LEETCODE_NO_SANITIZE_INLINE void pop_back() { count--; }
    LEETCODE_NO_SANITIZE_INLINE U& back() { return items[count - 1]; }
    LEETCODE_NO_SANITIZE_INLINE bool empty() const { return !count; }
    LEETCODE_NO_SANITIZE_INLINE size_t size() const { return count; }
    void clear() { count = 0; }
    LEETCODE_NO_SANITIZE_INLINE U& operator[](int i) { return items[i]; }
    LEETCODE_NO_SANITIZE_INLINE const U& operator[](int i) const { return items[i]; }
};

template <typename T>
struct TreapMultiset {
    template <class K>
    LEETCODE_NO_SANITIZE static K noneOf() {  // the lowest value of K, part by part for pairs and tuples
        if constexpr (is_arithmetic_v<K>) return numeric_limits<K>::lowest();
        else return apply([](auto... parts) { return K{noneOf<decltype(parts)>()...}; }, K{});
    }
    static inline const T NONE = noneOf<T>();  // largestLtX and friends when nothing qualifies: compare with it

    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    struct Node { T key; long long c, z; S s; long long dn; T xr; T andv = ~T(0); unsigned prio; int l, r; };  // copies; copies, sum, distinct below
    FlatPool<Node> pool{1};
    FlatPool<int> freeList;
    static inline mt19937 rng{(unsigned)chrono::steady_clock::now().time_since_epoch().count()};
    int root = 0;
    long long n = 0, d = 0;
    struct Info { T v; long long before, c; S sb; };  // a value, copies before it, its copies, sum before it
    T mn{}, mx{};  // kept current by addRaw while n > 0
    long long mexV = 0;  // the mex, kept current (0 for the empty set)
    map<long long, set<T>> bk;  // mode: count -> the values with that many copies
    T xtotal = 0;  // xor of all values (copies count)
    S total = 0;

    // O(1) -- an empty multiset
    TreapMultiset() {}


    // optional -- reserve room for this many nodes up front
    LEETCODE_NO_SANITIZE void reservePool(size_t nodes) { pool.reserve(nodes); }

    LEETCODE_NO_SANITIZE int make(T x) {
        int t;
        if (!freeList.empty()) t = freeList.back(), freeList.pop_back();
        else pool.push_back(Node{}), t = (int)pool.size() - 1;
        pool[t] = Node{};
        pool[t].key = x, pool[t].prio = rng();
        return t;
    }

    LEETCODE_NO_SANITIZE void pull(int t) {
        Node& v = pool[t];
        const Node &a = pool[v.l], &b = pool[v.r];
        v.z = a.z + b.z + v.c;
        v.dn = a.dn + b.dn + 1;
        v.xr = a.xr ^ b.xr ^ (v.c & 1 ? v.key : T(0));
        v.andv = a.andv & b.andv & v.key;
        v.s = a.s + b.s + S(v.c) * v.key;
    }

    LEETCODE_NO_SANITIZE void split(int t, T x, int& a, int& b) {  // (keys < x, keys >= x)
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

    LEETCODE_NO_SANITIZE void splitLe(int t, const T& x, int& a, int& b) {  // a: keys <= x, b: keys > x
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

    LEETCODE_NO_SANITIZE int merge(int a, int b) {  // every key in a < every key in b
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

    FlatPool<int> path;  // scratch for insert: the nodes it walked through
    LEETCODE_NO_SANITIZE long long insert(T x, long long c) {  // returns x's new count; a value already present never needs a split or merge
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
            while (i < walked && pool[path[i]].prio >= pool[m].prio) i++;  // the new node goes where its priority belongs
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

    LEETCODE_NO_SANITIZE long long lt(T x) {  // copies of values < x
        int t = root;
        long long res = 0;
        while (t) {
            if (pool[t].key < x) res += pool[pool[t].l].z + pool[t].c, t = pool[t].r;
            else t = pool[t].l;
        }
        return res;
    }

    LEETCODE_NO_SANITIZE long long le(T x) {  // copies of values <= x
        int t = root;
        long long res = 0;
        while (t) {
            if (x < pool[t].key) t = pool[t].l;
            else res += pool[pool[t].l].z + pool[t].c, t = pool[t].r;
        }
        return res;
    }

    LEETCODE_NO_SANITIZE long long countOf(T x) {
        int t = root;
        while (t && pool[t].key != x) t = x < pool[t].key ? pool[t].l : pool[t].r;
        return pool[t].c;
    }

    LEETCODE_NO_SANITIZE S slt(T x) {  // sum of the values < x
        int t = root;
        S res = 0;
        while (t) {
            if (pool[t].key < x) res += pool[pool[t].l].s + S(pool[t].c) * pool[t].key, t = pool[t].r;
            else t = pool[t].l;
        }
        return res;
    }

    LEETCODE_NO_SANITIZE S sle(T x) {  // sum of the values <= x
        int t = root;
        S res = 0;
        while (t) {
            if (x < pool[t].key) t = pool[t].l;
            else res += pool[pool[t].l].s + S(pool[t].c) * pool[t].key, t = pool[t].r;
        }
        return res;
    }

    LEETCODE_NO_SANITIZE T kthAt(long long k) {
        int t = root;
        while (true) {
            long long zl = pool[pool[t].l].z;
            if (k <= zl) t = pool[t].l;
            else if (k <= zl + pool[t].c) return pool[t].key;
            else k -= zl + pool[t].c, t = pool[t].r;
        }
    }

    LEETCODE_NO_SANITIZE Info kthInfo(long long k) {  // the k-th smallest, copies before it, its copies, sum before it
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

    LEETCODE_NO_SANITIZE long long distinctLt(T x) {  // distinct values < x
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
    LEETCODE_NO_SANITIZE long long findMex() {
        long long c0 = distinctLt(0), before = -c0, res = d - c0;  // before: distinct values >= 0 left of t's subtree
        int t = root;
        while (t) {
            long long j = before + pool[pool[t].l].dn;
            if (pool[t].key < 0 || pool[t].key == T(j)) before = j + 1, t = pool[t].r;
            else res = j, t = pool[t].l;
        }
        return res;
    }

    LEETCODE_NO_SANITIZE void addRaw(T x, long long c) {  // c copies of x (c < 0 removes); keeps min / max, the mex current
        n += c;
        total += S(c) * x;
        if (c & 1) xtotal ^= x;  // an odd number of copies flips x in or out of the xor of everything
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
            if constexpr (is_integral_v<T>) if (x == T(mexV)) mexV = findMex();  // x filled the mex
            if (n == c) {  // the set was empty
                mn = mx = x;
                return;
            }
            if (x < mn) mn = x;
            if (x > mx) mx = x;
        } else {
            if constexpr (is_integral_v<T>) if (x >= 0 && x < T(mexV) && !f) mexV = x;  // the last copy of a value below the mex
            if (!n) return;
            if (!f) {  // x is gone: it may have been the min / max
                if (x == mn) mn = kthAt(1);
                if (x == mx) mx = kthAt(n);
            }
        }
    }

    LEETCODE_NO_SANITIZE S sumFirst(long long k) {  // sum of the k smallest values
        if (k <= 0) return 0;
        Info f = kthInfo(k);
        return f.sb + S(k - f.before) * f.v;
    }

    LEETCODE_NO_SANITIZE void resetCached() {  // nothing counted: as newly built
        mexV = 0;
        bk.clear();
        n = d = 0;
        total = 0;
        xtotal = 0;
    }

    LEETCODE_NO_SANITIZE void clearData() {  // drop every node but keep the pool's memory for the next adds
        pool.resize(1), freeList.clear(), root = 0;
    }

    LEETCODE_NO_SANITIZE T xlt(T x) {  // xor of the values < x (copies count)
        int t = root;
        T res = 0;
        while (t) {
            const Node& v = pool[t];
            if (v.key < x) res ^= pool[v.l].xr ^ (v.c & 1 ? v.key : T(0)), t = v.r;
            else t = v.l;
        }
        return res;
    }

    LEETCODE_NO_SANITIZE T xle(T x) {  // xor of the values <= x (copies count)
        int t = root;
        T res = 0;
        while (t) {
            const Node& v = pool[t];
            if (x < v.key) t = v.l;
            else res ^= pool[v.l].xr ^ (v.c & 1 ? v.key : T(0)), t = v.r;
        }
        return res;
    }

    LEETCODE_NO_SANITIZE T xorFirst(long long k) {  // xor of the k smallest values (copies count)
        if (k <= 0) return 0;
        int t = root;
        T res = 0;
        while (true) {
            const Node& v = pool[t];
            long long zl = pool[v.l].z;
            if (k <= zl) t = v.l;
            else if (k <= zl + v.c) {
                res ^= pool[v.l].xr ^ ((k - zl) & 1 ? v.key : T(0));
                return res;
            } else k -= zl + v.c, res ^= pool[v.l].xr ^ (v.c & 1 ? v.key : T(0)), t = v.r;
        }
    }

    LEETCODE_NO_SANITIZE T andLe(T x) {  // AND of the values <= x
        int t = root;
        T res = ~T(0);
        while (t) {
            if (x < pool[t].key) t = pool[t].l;
            else res &= pool[pool[t].l].andv & pool[t].key, t = pool[t].r;
        }
        return res;
    }

    LEETCODE_NO_SANITIZE T andGe(T x) {  // AND of the values >= x
        int t = root;
        T res = ~T(0);
        while (t) {
            if (pool[t].key < x) t = pool[t].r;
            else res &= pool[pool[t].r].andv & pool[t].key, t = pool[t].l;
        }
        return res;
    }

    LEETCODE_NO_SANITIZE T andIn(T lo, T hi) {  // AND of the values in [lo, hi] (lo <= hi)
        int t = root;
        while (t && (pool[t].key < lo || hi < pool[t].key)) {  // down to the highest node inside [lo, hi]
            t = hi < pool[t].key ? pool[t].l : pool[t].r;
        }
        if (!t) {
            return ~T(0);
        }
        T res = pool[t].key;
        for (int u = pool[t].l; u;) {  // its left side is <= hi: keep what is >= lo
            if (lo <= pool[u].key) res &= pool[u].key & pool[pool[u].r].andv, u = pool[u].l;
            else u = pool[u].r;
        }
        for (int u = pool[t].r; u;) {  // its right side is >= lo: keep what is <= hi
            if (pool[u].key <= hi) res &= pool[u].key & pool[pool[u].l].andv, u = pool[u].r;
            else u = pool[u].l;
        }
        return res;
    }

    // O(logN expected) -- add one copy of x
    LEETCODE_NO_SANITIZE void add(T x) {
        addRaw(x, 1);
    }

    // O(logN expected) -- add cnt copies of val (nothing if cnt <= 0)
    LEETCODE_NO_SANITIZE void addCount(T val, long long cnt) {
        if (cnt > 0) addRaw(val, cnt);
    }

    // O(1) -- bitwise AND of all values; -1 (every bit set) if empty
    LEETCODE_NO_SANITIZE T andOfAll() {
        return pool[root].andv;
    }

    // O(logN expected) -- bitwise AND of the values > x; -1 (every bit set) if there are none
    LEETCODE_NO_SANITIZE T andOfGtX(T x) {
        if (x == numeric_limits<T>::max()) return ~T(0);
        return andGe(x + 1);
    }

    // O(logN expected) -- bitwise AND of the values >= x; -1 (every bit set) if there are none
    LEETCODE_NO_SANITIZE T andOfGteX(T x) {
        return andGe(x);
    }

    // O(logN expected) -- bitwise AND of the values v with lo <= v <= hi; -1 (every bit set) if there are none
    LEETCODE_NO_SANITIZE T andOfInValRange(T lo, T hi) {
        return lo <= hi ? andIn(lo, hi) : ~T(0);
    }

    // O(logN expected) -- bitwise AND of the kFrom-th through kTo-th largest values; RANKS, 1-indexed and inclusive:
    // (1, 1) is just the largest, (5, 8) the 5th, 6th, 7th and 8th largest, (1, size) every value (copies count);
    // throws out_of_range unless 1 <= kFrom <= kTo <= size
    LEETCODE_NO_SANITIZE T andOfKthLargestRange(long long kFrom, long long kTo) {
        if (kFrom < 1 || kFrom > kTo || kTo > n) throw out_of_range("andOfKthLargestRange: needs 1 <= kFrom <= kTo <= size");
        T a = kthAt(n - kTo + 1);
        return andIn(a, kthAt(n - kFrom + 1));
    }

    // O(logN expected) -- bitwise AND of the kFrom-th through kTo-th smallest values; RANKS, 1-indexed and inclusive:
    // (1, 1) is just the smallest, (2, 4) the 2nd, 3rd and 4th smallest, (1, size) every value (copies count); throws
    // out_of_range unless 1 <= kFrom <= kTo <= size
    LEETCODE_NO_SANITIZE T andOfKthSmallestRange(long long kFrom, long long kTo) {
        if (kFrom < 1 || kFrom > kTo || kTo > n) throw out_of_range("andOfKthSmallestRange: needs 1 <= kFrom <= kTo <= size");
        T a = kthAt(kFrom);
        return andIn(a, kthAt(kTo));
    }

    // O(logN expected) -- bitwise AND of the k largest values; k is a COUNT, not an index: k = 0 takes no values
    // (returns -1, every bit set), k = 1 just the largest, k = size every value (copies count: in {2, 5, 5}, k = 2
    // takes 5 and 5); throws out_of_range unless 0 <= k <= size
    LEETCODE_NO_SANITIZE T andOfLargestK(long long k) {
        if (k < 0 || k > n) throw out_of_range("andOfLargestK: needs 0 <= k <= size");
        return k ? andGe(kthAt(n - k + 1)) : ~T(0);
    }

    // O(logN expected) -- bitwise AND of the values < x; -1 (every bit set) if there are none
    LEETCODE_NO_SANITIZE T andOfLtX(T x) {
        if (x == numeric_limits<T>::min()) return ~T(0);
        return andLe(x - 1);
    }

    // O(logN expected) -- bitwise AND of the values <= x; -1 (every bit set) if there are none
    LEETCODE_NO_SANITIZE T andOfLteX(T x) {
        return andLe(x);
    }

    // O(logN expected) -- bitwise AND of the k smallest values; k is a COUNT, not an index: k = 0 takes no values
    // (returns -1, every bit set), k = 1 just the smallest, k = size every value (copies count: in {2, 2, 5}, k = 2
    // takes 2 and 2); throws out_of_range unless 0 <= k <= size
    LEETCODE_NO_SANITIZE T andOfSmallestK(long long k) {
        if (k < 0 || k > n) throw out_of_range("andOfSmallestK: needs 0 <= k <= size");
        return k ? andLe(kthAt(k)) : ~T(0);
    }

    // O(1 amortized) -- remove everything: afterwards it is as if newly built (same constructor arguments), so reuse it
    // instead of building a new one
    LEETCODE_NO_SANITIZE void clear() {
        clearData();
        resetCached();
    }

    // O(logN expected) -- how many copies of x
    LEETCODE_NO_SANITIZE long long count(T x) {
        return countOf(x);
    }

    // O(1) -- how many distinct values
    LEETCODE_NO_SANITIZE long long countDistinct() {
        return d;
    }

    // O(logN expected) -- how many distinct values v with lo <= v <= hi (0 if lo > hi)
    LEETCODE_NO_SANITIZE long long countDistinctInValRange(T lo, T hi) {
        if (hi < lo) return 0;
        return distinctLt(hi) - distinctLt(lo) + (countOf(hi) ? 1 : 0);
    }

    // O(logN expected) -- how many values > x
    LEETCODE_NO_SANITIZE long long countGtX(T x) {
        return n - le(x);
    }

    // O(logN expected) -- how many values >= x
    LEETCODE_NO_SANITIZE long long countGteX(T x) {
        return n - lt(x);
    }

    // O(logN expected) -- how many values v with lo <= v <= hi (0 if lo > hi)
    LEETCODE_NO_SANITIZE long long countInValRange(T lo, T hi) {
        return lo <= hi ? le(hi) - lt(lo) : 0;
    }

    // O(logN expected) -- how many values < x
    LEETCODE_NO_SANITIZE long long countLtX(T x) {
        return lt(x);
    }

    // O(logN expected) -- how many values <= x
    LEETCODE_NO_SANITIZE long long countLteX(T x) {
        return le(x);
    }

    // O(logN expected) -- 0-indexed position of the first copy of x in sorted order (= how many values < x); -1 if x is
    // not in the set
    LEETCODE_NO_SANITIZE long long firstIndex(T x) {
        return countOf(x) ? lt(x) : -1;
    }

    // O(logN expected) -- the value at sorted position i, 0-indexed: kth(0) is the smallest, kth(1) the 2nd smallest,
    // kth(size - 1) the largest (copies count: in {2, 2, 5}, kth(1) is 2); throws out_of_range unless 0 <= i < size
    LEETCODE_NO_SANITIZE T kth(long long i) {
        if (i < 0 || i >= n) throw out_of_range("kth: needs 0 <= i < size");
        return kthAt(i + 1);
    }

    // O(logN expected) -- largest value < x; NONE if there is none
    LEETCODE_NO_SANITIZE T largestLtX(T x) {
        long long c = lt(x);
        if (!c) return NONE;
        return kthAt(c);
    }

    // O(logN expected) -- largest value <= x; NONE if there is none
    LEETCODE_NO_SANITIZE T largestLteX(T x) {
        long long c = le(x);
        if (!c) return NONE;
        return kthAt(c);
    }

    // O(logN expected) -- 0-indexed position of the last copy of x in sorted order (= how many values <= x, minus 1);
    // -1 if x is not in the set
    LEETCODE_NO_SANITIZE long long lastIndex(T x) {
        return countOf(x) ? le(x) - 1 : -1;
    }

    // O(1) -- largest value; throws out_of_range if empty
    LEETCODE_NO_SANITIZE T max() {
        if (!n) throw out_of_range("max: the set is empty");
        return mx;
    }

    // O(logN expected) -- upper median: the (floor(size/2) + 1)-th smallest value; throws out_of_range if empty
    LEETCODE_NO_SANITIZE T medianHigh() {
        if (!n) throw out_of_range("medianHigh: the set is empty");
        return kthAt(n / 2 + 1);
    }

    // O(logN expected) -- lower median: the ceil(size/2)-th smallest value; throws out_of_range if empty
    LEETCODE_NO_SANITIZE T medianLow() {
        if (!n) throw out_of_range("medianLow: the set is empty");
        return kthAt((n + 1) / 2);
    }

    // O(1) -- smallest non-negative integer not in the set
    LEETCODE_NO_SANITIZE long long mex() {
        return mexV;
    }

    // O(1) -- smallest value; throws out_of_range if empty
    LEETCODE_NO_SANITIZE T min() {
        if (!n) throw out_of_range("min: the set is empty");
        return mn;
    }

    // O(1) -- (a most frequent value, its count); throws out_of_range if empty. C++ returns the smallest of the most
    // frequent values
    LEETCODE_NO_SANITIZE pair<T, long long> mode() {
        if (!n) throw out_of_range("mode: the set is empty");
        auto& [f, vs] = *bk.rbegin();
        return pair<T, long long>{*vs.begin(), f};
    }

    // O(logN expected) -- remove and return the value at sorted position i, 0-indexed: pop(0) removes the smallest (=
    // popMin()), pop(size - 1) the largest (copies count); throws out_of_range unless 0 <= i < size
    LEETCODE_NO_SANITIZE T pop(long long i) {
        if (i < 0 || i >= n) throw out_of_range("pop: needs 0 <= i < size");
        T v = kthAt(i + 1);
        addRaw(v, -1);
        return v;
    }

    // O(logN expected) -- remove and return the largest value; throws out_of_range if empty
    LEETCODE_NO_SANITIZE T popMax() {
        if (!n) throw out_of_range("popMax: the set is empty");
        T v = mx;
        addRaw(v, -1);
        return v;
    }

    // O(logN expected) -- remove and return the smallest value; throws out_of_range if empty
    LEETCODE_NO_SANITIZE T popMin() {
        if (!n) throw out_of_range("popMin: the set is empty");
        T v = mn;
        addRaw(v, -1);
        return v;
    }

    // O(logN expected) -- remove one copy of x if present; returns how many were removed (0 or 1)
    LEETCODE_NO_SANITIZE long long remove(T x) {
        if (!count(x)) return 0;
        addRaw(x, -1);
        return 1;
    }

    // O(logN expected) -- remove every copy of val; returns how many were removed
    LEETCODE_NO_SANITIZE long long removeAll(T val) {
        long long k = count(val);
        if (k) addRaw(val, -k);
        return k;
    }

    // O(logN expected) -- remove min(cnt, count(val)) copies of val; returns how many were removed
    LEETCODE_NO_SANITIZE long long removeCount(T val, long long cnt) {
        long long k = std::min(cnt, count(val));
        if (k <= 0) return 0;
        addRaw(val, -k);
        return k;
    }

    // O(logN expected) -- remove every value v with lo <= v <= hi; returns how many copies were removed (0 if lo > hi)
    LEETCODE_NO_SANITIZE long long removeInValRange(T lo, T hi) {
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
    LEETCODE_NO_SANITIZE long long size() {
        return n;
    }

    // O(logN expected) -- smallest value > x; NONE if there is none
    LEETCODE_NO_SANITIZE T smallestGtX(T x) {
        long long c = le(x);
        if (c == n) return NONE;
        return kthAt(c + 1);
    }

    // O(logN expected) -- smallest value >= x; NONE if there is none
    LEETCODE_NO_SANITIZE T smallestGteX(T x) {
        long long c = lt(x);
        if (c == n) return NONE;
        return kthAt(c + 1);
    }

    // O(logN expected) -- sum of |v - medianLow()| over all values (min total moves to make all equal); 0 if empty
    LEETCODE_NO_SANITIZE S sumAbsDiffToMedian() {
        if (!n) return 0;
        Info m = kthInfo((n + 1) / 2);
        return S(m.v) * m.before - m.sb + (total - m.sb - S(m.v) * m.c) - S(m.v) * (n - m.before - m.c);
    }

    // O(logN expected) -- sum of |v - x| over all values
    LEETCODE_NO_SANITIZE S sumAbsDiffToX(T x) {
        long long c = lt(x);
        S s = slt(x);
        return S(x) * c - s + (total - s) - S(x) * (n - c);
    }

    // O(1) -- sum of all values
    LEETCODE_NO_SANITIZE S sumAll() {
        return total;
    }

    // O(logN expected) -- sum of the values > x
    LEETCODE_NO_SANITIZE S sumGtX(T x) {
        return total - sle(x);
    }

    // O(logN expected) -- sum of the values >= x
    LEETCODE_NO_SANITIZE S sumGteX(T x) {
        return total - slt(x);
    }

    // O(logN expected) -- sum of the values v with lo <= v <= hi (0 if lo > hi)
    LEETCODE_NO_SANITIZE S sumInValRange(T lo, T hi) {
        return lo <= hi ? sle(hi) - slt(lo) : S(0);
    }

    // O(logN expected) -- sum of the kFrom-th through kTo-th largest values; RANKS, 1-indexed and inclusive: (1, 1) is
    // just the largest, (5, 8) the 5th, 6th, 7th and 8th largest, (1, size) every value (copies count); throws
    // out_of_range unless 1 <= kFrom <= kTo <= size
    LEETCODE_NO_SANITIZE S sumKthLargestRange(long long kFrom, long long kTo) {
        if (kFrom < 1 || kFrom > kTo || kTo > n) throw out_of_range("sumKthLargestRange: needs 1 <= kFrom <= kTo <= size");
        return sumFirst(n - kFrom + 1) - sumFirst(n - kTo);
    }

    // O(logN expected) -- sum of the kFrom-th through kTo-th smallest values; RANKS, 1-indexed and inclusive: (1, 1) is
    // just the smallest, (2, 4) the 2nd, 3rd and 4th smallest, (1, size) every value (copies count); throws
    // out_of_range unless 1 <= kFrom <= kTo <= size
    LEETCODE_NO_SANITIZE S sumKthSmallestRange(long long kFrom, long long kTo) {
        if (kFrom < 1 || kFrom > kTo || kTo > n) throw out_of_range("sumKthSmallestRange: needs 1 <= kFrom <= kTo <= size");
        return sumFirst(kTo) - sumFirst(kFrom - 1);
    }

    // O(logN expected) -- sum of the k largest values; k is a COUNT, not an index: k = 0 takes no values (returns 0), k
    // = 1 just the largest, k = size every value (copies count: in {2, 5, 5}, k = 2 takes 5 and 5); throws out_of_range
    // unless 0 <= k <= size
    LEETCODE_NO_SANITIZE S sumLargestK(long long k) {
        if (k < 0 || k > n) throw out_of_range("sumLargestK: needs 0 <= k <= size");
        return total - sumFirst(n - k);
    }

    // O(logN expected) -- sum of the values < x
    LEETCODE_NO_SANITIZE S sumLtX(T x) {
        return slt(x);
    }

    // O(logN expected) -- sum of the values <= x
    LEETCODE_NO_SANITIZE S sumLteX(T x) {
        return sle(x);
    }

    // O(logN expected) -- sum of the k smallest values; k is a COUNT, not an index: k = 0 takes no values (returns 0),
    // k = 1 just the smallest, k = size every value (copies count: in {2, 2, 5}, k = 2 takes 2 and 2); throws
    // out_of_range unless 0 <= k <= size
    LEETCODE_NO_SANITIZE S sumSmallestK(long long k) {
        if (k < 0 || k > n) throw out_of_range("sumSmallestK: needs 0 <= k <= size");
        return sumFirst(k);
    }

    // O(1) -- xor of all values (copies count: a value with an even count cancels out); 0 if empty
    LEETCODE_NO_SANITIZE T xorOfAll() {
        return xtotal;
    }

    // O(logN expected) -- xor of the values > x (copies count)
    LEETCODE_NO_SANITIZE T xorOfGtX(T x) {
        return xtotal ^ xle(x);
    }

    // O(logN expected) -- xor of the values >= x (copies count)
    LEETCODE_NO_SANITIZE T xorOfGteX(T x) {
        return xtotal ^ xlt(x);
    }

    // O(logN expected) -- xor of the values v with lo <= v <= hi (copies count; 0 if lo > hi)
    LEETCODE_NO_SANITIZE T xorOfInValRange(T lo, T hi) {
        return lo <= hi ? T(xle(hi) ^ xlt(lo)) : T(0);
    }

    // O(logN expected) -- xor of the kFrom-th through kTo-th largest values; RANKS, 1-indexed and inclusive: (1, 1) is
    // just the largest, (5, 8) the 5th, 6th, 7th and 8th largest, (1, size) every value (copies count); throws
    // out_of_range unless 1 <= kFrom <= kTo <= size
    LEETCODE_NO_SANITIZE T xorOfKthLargestRange(long long kFrom, long long kTo) {
        if (kFrom < 1 || kFrom > kTo || kTo > n) throw out_of_range("xorOfKthLargestRange: needs 1 <= kFrom <= kTo <= size");
        return xorFirst(n - kFrom + 1) ^ xorFirst(n - kTo);
    }

    // O(logN expected) -- xor of the kFrom-th through kTo-th smallest values; RANKS, 1-indexed and inclusive: (1, 1) is
    // just the smallest, (2, 4) the 2nd, 3rd and 4th smallest, (1, size) every value (copies count); throws
    // out_of_range unless 1 <= kFrom <= kTo <= size
    LEETCODE_NO_SANITIZE T xorOfKthSmallestRange(long long kFrom, long long kTo) {
        if (kFrom < 1 || kFrom > kTo || kTo > n) throw out_of_range("xorOfKthSmallestRange: needs 1 <= kFrom <= kTo <= size");
        return xorFirst(kTo) ^ xorFirst(kFrom - 1);
    }

    // O(logN expected) -- xor of the k largest values; k is a COUNT, not an index: k = 0 takes no values (returns 0), k
    // = 1 just the largest, k = size every value (copies count: in {2, 5, 5}, k = 2 takes 5 and 5); throws out_of_range
    // unless 0 <= k <= size
    LEETCODE_NO_SANITIZE T xorOfLargestK(long long k) {
        if (k < 0 || k > n) throw out_of_range("xorOfLargestK: needs 0 <= k <= size");
        return xtotal ^ xorFirst(n - k);
    }

    // O(logN expected) -- xor of the values < x (copies count)
    LEETCODE_NO_SANITIZE T xorOfLtX(T x) {
        return xlt(x);
    }

    // O(logN expected) -- xor of the values <= x (copies count)
    LEETCODE_NO_SANITIZE T xorOfLteX(T x) {
        return xle(x);
    }

    // O(logN expected) -- xor of the k smallest values; k is a COUNT, not an index: k = 0 takes no values (returns 0),
    // k = 1 just the smallest, k = size every value (copies count: in {2, 2, 5}, k = 2 takes 2 and 2); throws
    // out_of_range unless 0 <= k <= size
    LEETCODE_NO_SANITIZE T xorOfSmallestK(long long k) {
        if (k < 0 || k > n) throw out_of_range("xorOfSmallestK: needs 0 <= k <= size");
        return xorFirst(k);
    }
};
