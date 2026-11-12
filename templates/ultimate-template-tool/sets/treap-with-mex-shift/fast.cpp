// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/sets/treap-with-mex-shift/fast.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: add addCount clear count countDistinct countDistinctInValRange countGtX countGteX countInValRange countLtX countLteX firstIndex kth largestLtX largestLteX lastIndex max medianHigh medianLow mex min pop popMax popMin remove removeAll removeCount removeInValRange shiftAll size smallestGtX smallestGteX
// @data-structure-type: treap
// @values: online
// @keys: numbers
// @tracks: shift
// @complexities:
//   add: log(N) expected
//   addCount: log(N) expected
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
//   max: log(N) expected
//   medianHigh: log(N) expected
//   medianLow: log(N) expected
//   mex: log(N) expected
//   min: log(N) expected
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
//   build: 1
// @memory:
//   layout: none
//   node: key[1*N] cnt[1*N] size[1*N] dn[1*N]
//   tags: none
//   other: children[2*N] prio[1*N]
//   note: N = most distinct values present at once (removed nodes are reused). C++: each multiset owns its node pool; Python: parallel lists per tree

// Ordered multiset (online: any values, nothing known ahead): a treap with one node per distinct value. Each node keeps
// its value, its copies, and totals over its subtree: copies, distinct values. Each multiset owns its node pool
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
    // what largestLtX, smallestGtX, ... return when nothing qualifies: compare with ms.NONE. It is the lowest T, so a
    // real value equal to it reads as "nothing"
    static inline const T NONE = noneOf<T>();

    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    struct Node { T key; long long c, z; long long dn; unsigned prio; int l, r; };  // copies; copies, distinct below
    FlatPool<Node> pool{1};
    FlatPool<int> freeList;
    static inline mt19937 rng{(unsigned)chrono::steady_clock::now().time_since_epoch().count()};
    int root = 0;
    long long n = 0, d = 0;
    struct Info { T v; long long before, c; };  // a value, copies before it, its copies
    T off = 0;  // every value v is stored as v - off: shiftAll only moves off

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
    LEETCODE_NO_SANITIZE long long insert(T x, long long c) {
        // returns x's new count; a value already present never needs a split or merge
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

    LEETCODE_NO_SANITIZE T kthAt(long long k) {
        int t = root;
        while (true) {
            long long zl = pool[pool[t].l].z;
            if (k <= zl) t = pool[t].l;
            else if (k <= zl + pool[t].c) return pool[t].key;
            else k -= zl + pool[t].c, t = pool[t].r;
        }
    }

    LEETCODE_NO_SANITIZE Info kthInfo(long long k) {  // the k-th smallest, copies before it, its copies
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

    LEETCODE_NO_SANITIZE long long distinctLt(T x) {  // distinct values < x
        int t = root;
        long long res = 0;
        while (t) {
            if (pool[t].key < x) res += pool[pool[t].l].dn + 1, t = pool[t].r;
            else t = pool[t].l;
        }
        return res;
    }

    // smallest non-negative integer not in the set. With c0 distinct negatives, the distinct values >= 0 in order v_0 <
    // v_1 < ... satisfy v_j >= j, and v_j == j means 0..v_j are all present; the answer is the first j with v_j > j (or
    // how many there are). One walk down: at a node of distinct rank c0 + j, go right if v_j == j.
    LEETCODE_NO_SANITIZE long long findMex() {
        T base = -off;  // (stored as v - off: the real values >= 0 are the stored ones >= -off)
        // before: distinct values >= 0 left of t's subtree
        long long c0 = distinctLt(base), before = -c0, res = d - c0;
        int t = root;
        while (t) {
            long long j = before + pool[pool[t].l].dn;
            if (pool[t].key < base || pool[t].key == T(base + j)) before = j + 1, t = pool[t].r;
            else res = j, t = pool[t].l;
        }
        return base + res;  // (a stored value)
    }

    LEETCODE_NO_SANITIZE void addRaw(T x, long long c) {  // c copies of x (c < 0 removes)
        n += c;
        insert(x, c);
    }

    LEETCODE_NO_SANITIZE void resetCached() {  // nothing counted: as newly built
        n = d = 0;
        off = 0;
    }

    LEETCODE_NO_SANITIZE void clearData() {  // drop every node but keep the pool's memory for the next adds
        pool.resize(1), freeList.clear(), root = 0;
    }

    // O(logN expected) -- add one copy of x
    LEETCODE_NO_SANITIZE void add(T x) {
        x -= off;
        addRaw(x, 1);
    }

    // O(logN expected) -- add cnt copies of val (nothing if cnt <= 0)
    LEETCODE_NO_SANITIZE void addCount(T val, long long cnt) {
        val -= off;
        if (cnt > 0) addRaw(val, cnt);
    }

    // O(1 amortized) -- remove everything (fine on an empty set): afterwards it is as if newly built (same constructor
    // arguments), so reuse it instead of building a new one
    LEETCODE_NO_SANITIZE void clear() {
        clearData();
        resetCached();
    }

    // O(logN expected) -- how many copies of x (0 if x isn't there, e.g. on an empty set)
    LEETCODE_NO_SANITIZE long long count(T x) {
        x -= off;
        return countOf(x);
    }

    // O(1) -- how many distinct values (0 if empty)
    LEETCODE_NO_SANITIZE long long countDistinct() {
        return d;
    }

    // O(logN expected) -- how many distinct values v with lo <= v <= hi (0 if lo > hi)
    LEETCODE_NO_SANITIZE long long countDistinctInValRange(T lo, T hi) {
        lo -= off, hi -= off;
        if (hi < lo) return 0;
        return distinctLt(hi) - distinctLt(lo) + (countOf(hi) ? 1 : 0);
    }

    // O(logN expected) -- how many values > x (0 if there are none, e.g. on an empty set)
    LEETCODE_NO_SANITIZE long long countGtX(T x) {
        x -= off;
        return n - le(x);
    }

    // O(logN expected) -- how many values >= x (0 if there are none, e.g. on an empty set)
    LEETCODE_NO_SANITIZE long long countGteX(T x) {
        x -= off;
        return n - lt(x);
    }

    // O(logN expected) -- how many values v with lo <= v <= hi (0 if lo > hi)
    LEETCODE_NO_SANITIZE long long countInValRange(T lo, T hi) {
        lo -= off, hi -= off;
        return lo <= hi ? le(hi) - lt(lo) : 0;
    }

    // O(logN expected) -- how many values < x (0 if there are none, e.g. on an empty set)
    LEETCODE_NO_SANITIZE long long countLtX(T x) {
        x -= off;
        return lt(x);
    }

    // O(logN expected) -- how many values <= x (0 if there are none, e.g. on an empty set)
    LEETCODE_NO_SANITIZE long long countLteX(T x) {
        x -= off;
        return le(x);
    }

    // O(logN expected) -- 0-indexed position of the first copy of x in sorted order (= how many values < x); -1 if x is
    // not in the set
    LEETCODE_NO_SANITIZE long long firstIndex(T x) {
        x -= off;
        return countOf(x) ? lt(x) : -1;
    }

    // O(logN expected) -- the value at sorted position i, 0-indexed: kth(0) is the smallest, kth(1) the 2nd smallest,
    // kth(size - 1) the largest (copies count: in {2, 2, 5}, kth(1) is 2); throws out_of_range unless 0 <= i < size
    LEETCODE_NO_SANITIZE T kth(long long i) {
        if (i < 0 || i >= n) throw out_of_range("kth: needs 0 <= i < size");
        return T(kthAt(i + 1) + off);
    }

    // O(logN expected) -- largest value < x; ms.NONE if there is none
    LEETCODE_NO_SANITIZE T largestLtX(T x) {
        x -= off;
        long long c = lt(x);
        if (!c) return NONE;
        return T(kthAt(c) + off);
    }

    // O(logN expected) -- largest value <= x; ms.NONE if there is none
    LEETCODE_NO_SANITIZE T largestLteX(T x) {
        x -= off;
        long long c = le(x);
        if (!c) return NONE;
        return T(kthAt(c) + off);
    }

    // O(logN expected) -- 0-indexed position of the last copy of x in sorted order (= how many values <= x, minus 1);
    // -1 if x is not in the set
    LEETCODE_NO_SANITIZE long long lastIndex(T x) {
        x -= off;
        return countOf(x) ? le(x) - 1 : -1;
    }

    // O(logN expected) -- largest value; throws out_of_range if empty
    LEETCODE_NO_SANITIZE T max() {
        if (!n) throw out_of_range("max: the set is empty");
        return T(kthAt(n) + off);
    }

    // O(logN expected) -- upper median: the (floor(size/2) + 1)-th smallest value; throws out_of_range if empty
    LEETCODE_NO_SANITIZE T medianHigh() {
        if (!n) throw out_of_range("medianHigh: the set is empty");
        return T(kthAt(n / 2 + 1) + off);
    }

    // O(logN expected) -- lower median: the ceil(size/2)-th smallest value; throws out_of_range if empty
    LEETCODE_NO_SANITIZE T medianLow() {
        if (!n) throw out_of_range("medianLow: the set is empty");
        return T(kthAt((n + 1) / 2) + off);
    }

    // O(logN expected) -- smallest non-negative integer not in the set (0 if empty)
    LEETCODE_NO_SANITIZE long long mex() {
        return findMex() + off;
    }

    // O(logN expected) -- smallest value; throws out_of_range if empty
    LEETCODE_NO_SANITIZE T min() {
        if (!n) throw out_of_range("min: the set is empty");
        return T(kthAt(1) + off);
    }

    // O(logN expected) -- remove and return the value at sorted position i, 0-indexed: pop(0) removes the smallest (=
    // popMin()), pop(size - 1) the largest (copies count); throws out_of_range unless 0 <= i < size
    LEETCODE_NO_SANITIZE T pop(long long i) {
        if (i < 0 || i >= n) throw out_of_range("pop: needs 0 <= i < size");
        T v = kthAt(i + 1);
        addRaw(v, -1);
        return T(v + off);
    }

    // O(logN expected) -- remove and return the largest value; throws out_of_range if empty
    LEETCODE_NO_SANITIZE T popMax() {
        if (!n) throw out_of_range("popMax: the set is empty");
        T v = kthAt(n);
        addRaw(v, -1);
        return T(v + off);
    }

    // O(logN expected) -- remove and return the smallest value; throws out_of_range if empty
    LEETCODE_NO_SANITIZE T popMin() {
        if (!n) throw out_of_range("popMin: the set is empty");
        T v = kthAt(1);
        addRaw(v, -1);
        return T(v + off);
    }

    // O(logN expected) -- remove one copy of x if present; returns how many were removed (0 or 1: 0 if x isn't there,
    // e.g. on an empty set)
    LEETCODE_NO_SANITIZE long long remove(T x) {
        x -= off;
        if (!countOf(x)) return 0;
        addRaw(x, -1);
        return 1;
    }

    // O(logN expected) -- remove every copy of val; returns how many were removed (0 if val isn't there, e.g. on an
    // empty set)
    LEETCODE_NO_SANITIZE long long removeAll(T val) {
        val -= off;
        long long k = countOf(val);
        if (k) addRaw(val, -k);
        return k;
    }

    // O(logN expected) -- remove min(cnt, count(val)) copies of val; returns how many were removed (0 if val isn't
    // there, e.g. on an empty set)
    LEETCODE_NO_SANITIZE long long removeCount(T val, long long cnt) {
        val -= off;
        long long k = std::min(cnt, countOf(val));
        if (k <= 0) return 0;
        addRaw(val, -k);
        return k;
    }

    // O(logN expected) -- remove every value v with lo <= v <= hi; returns how many copies were removed (0 if lo > hi)
    LEETCODE_NO_SANITIZE long long removeInValRange(T lo, T hi) {
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

    // O(1) -- add d to every value (d may be negative; nothing happens on an empty set)
    LEETCODE_NO_SANITIZE void shiftAll(T d) {
        off += d;
    }

    // O(1) -- how many values (copies count; 0 if empty)
    LEETCODE_NO_SANITIZE long long size() {
        return n;
    }

    // O(logN expected) -- smallest value > x; ms.NONE if there is none
    LEETCODE_NO_SANITIZE T smallestGtX(T x) {
        x -= off;
        long long c = le(x);
        if (c == n) return NONE;
        return T(kthAt(c + 1) + off);
    }

    // O(logN expected) -- smallest value >= x; ms.NONE if there is none
    LEETCODE_NO_SANITIZE T smallestGteX(T x) {
        x -= off;
        long long c = lt(x);
        if (c == n) return NONE;
        return T(kthAt(c + 1) + off);
    }
};
