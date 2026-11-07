// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/sets/treap-with-sums-xor-or-mex-minmax-mode-gaps/template.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: add addCount clear count countDistinct countDistinctInValRange countGtX countGteX countInValRange countLtX countLteX firstIndex kth largestLtX largestLteX lastIndex max maxGap medianHigh medianLow mex min minAdjacentDiff mode orOfAll orOfGtX orOfGteX orOfInValRange orOfKthLargestRange orOfKthSmallestRange orOfLargestK orOfLtX orOfLteX orOfSmallestK pop popMax popMin remove removeAll removeCount removeInValRange size smallestGtX smallestGteX sumAbsDiffToMedian sumAbsDiffToX sumAll sumGtX sumGteX sumInValRange sumKthLargestRange sumKthSmallestRange sumLargestK sumLtX sumLteX sumSmallestK xorOfAll xorOfGtX xorOfGteX xorOfInValRange xorOfKthLargestRange xorOfKthSmallestRange xorOfLargestK xorOfLtX xorOfLteX xorOfSmallestK
// @data-structure-type: treap
// @values: online
// @keys: numbers
// @tracks: minmax mode gaps
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
//   max: 1
//   maxGap: 1 amortized
//   medianHigh: log(N) expected
//   medianLow: log(N) expected
//   mex: log(N) expected
//   min: 1
//   minAdjacentDiff: 1 amortized
//   mode: 1
//   orOfAll: 1
//   orOfGtX: log(N) expected
//   orOfGteX: log(N) expected
//   orOfInValRange: log(N) expected
//   orOfKthLargestRange: log(N) expected
//   orOfKthSmallestRange: log(N) expected
//   orOfLargestK: log(N) expected
//   orOfLtX: log(N) expected
//   orOfLteX: log(N) expected
//   orOfSmallestK: log(N) expected
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
//   node: key[1*N] cnt[1*N] size[1*N] dn[1*N] sum[1*N] xor[1*N] or[1*N]
//   tags: none
//   other: children[2*N] prio[1*N]
//   note: N = most distinct values present at once (removed nodes are reused). C++: each multiset owns its node pool; Python: parallel lists per tree

// Ordered multiset (online: any values, nothing known ahead): a treap with one node per distinct value. Each node keeps
// its value, its copies, and the copies, sum, xor, OR and distinct values in its subtree. Each multiset owns its node pool
// (freed when it goes out of scope; clear() keeps it for reuse); node 0 is the empty tree and removed nodes are reused.
// Updates split around x and merge back. T: an integer type; sums in S (long long for small T).
template <typename T>
struct TreapMultiset {
    template <class K>
    static K noneOf() {  // the lowest value of K, part by part for pairs and tuples
        if constexpr (is_arithmetic_v<K>) return numeric_limits<K>::lowest();
        else return apply([](auto... parts) { return K{noneOf<decltype(parts)>()...}; }, K{});
    }
    static inline const T NONE = noneOf<T>();  // what largestLtX, smallestGtX, ... return when nothing qualifies: compare with ms.NONE

    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    struct Node { T key; long long c, z; S s; long long dn; T xr; T orv; unsigned prio; int l, r; };  // copies; copies, sum, distinct below
    vector<Node> pool{Node{}};
    vector<int> freeList;
    static inline mt19937 rng{(unsigned)chrono::steady_clock::now().time_since_epoch().count()};
    int root = 0;
    long long n = 0, d = 0;
    struct Info { T v; long long before, c; S sb; };  // a value, copies before it, its copies, sum before it
    T mn{}, mx{};  // kept current by addRaw while n > 0
    map<long long, set<T>> bk;  // mode: count -> the values with that many copies
    multiset<long long> gaps;  // differences between neighbouring distinct values
    long long dups = 0;  // values with 2+ copies
    T xtotal = 0;  // xor of all values (copies count)
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
        v.xr = a.xr ^ b.xr ^ (v.c & 1 ? v.key : T(0));
        v.orv = a.orv | b.orv | v.key;
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
        long long c0 = distinctLt(0), before = -c0, res = d - c0;  // before: distinct values >= 0 left of t's subtree
        int t = root;
        while (t) {
            long long j = before + pool[pool[t].l].dn;
            if (pool[t].key < 0 || pool[t].key == T(j)) before = j + 1, t = pool[t].r;
            else res = j, t = pool[t].l;
        }
        return res;
    }

    void addRaw(T x, long long c) {  // c copies of x (c < 0 removes); keeps min / max current
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
        {  // gaps
            if ((g >= 2) != (f >= 2)) dups += f >= 2 ? 1 : -1;  // values with 2+ copies (then the smallest difference is 0)
            if (!g || !f) {  // x appeared or disappeared: the gap between its neighbours splits or comes back
                long long cl = lt(x), ce = cl + f;  // (ranks, not the public ops: a real value may equal NONE)
                optional<T> p, q;
                if (cl) p = kthAt(cl);
                if (ce < n) q = kthAt(ce + 1);
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
        gaps.clear(), dups = 0;
        n = d = 0;
        total = 0;
        xtotal = 0;
    }

    void clearData() {  // drop every node but keep the pool's memory for the next adds
        pool.resize(1), freeList.clear(), root = 0;
    }

    T xlt(T x) {  // xor of the values < x (copies count)
        int t = root;
        T res = 0;
        while (t) {
            const Node& v = pool[t];
            if (v.key < x) res ^= pool[v.l].xr ^ (v.c & 1 ? v.key : T(0)), t = v.r;
            else t = v.l;
        }
        return res;
    }

    T xle(T x) {  // xor of the values <= x (copies count)
        int t = root;
        T res = 0;
        while (t) {
            const Node& v = pool[t];
            if (x < v.key) t = v.l;
            else res ^= pool[v.l].xr ^ (v.c & 1 ? v.key : T(0)), t = v.r;
        }
        return res;
    }

    T xorFirst(long long k) {  // xor of the k smallest values (copies count)
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

    T orLe(T x) {  // OR of the values <= x
        int t = root;
        T res = T(0);
        while (t) {
            if (x < pool[t].key) t = pool[t].l;
            else res |= pool[pool[t].l].orv | pool[t].key, t = pool[t].r;
        }
        return res;
    }

    T orGe(T x) {  // OR of the values >= x
        int t = root;
        T res = T(0);
        while (t) {
            if (pool[t].key < x) t = pool[t].r;
            else res |= pool[pool[t].r].orv | pool[t].key, t = pool[t].l;
        }
        return res;
    }

    T orIn(T lo, T hi) {  // OR of the values in [lo, hi] (lo <= hi)
        int t = root;
        while (t && (pool[t].key < lo || hi < pool[t].key)) {  // down to the highest node inside [lo, hi]
            t = hi < pool[t].key ? pool[t].l : pool[t].r;
        }
        if (!t) {
            return T(0);
        }
        T res = pool[t].key;
        for (int u = pool[t].l; u;) {  // its left side is <= hi: keep what is >= lo
            if (lo <= pool[u].key) res |= pool[u].key | pool[pool[u].r].orv, u = pool[u].l;
            else u = pool[u].r;
        }
        for (int u = pool[t].r; u;) {  // its right side is >= lo: keep what is <= hi
            if (pool[u].key <= hi) res |= pool[u].key | pool[pool[u].l].orv, u = pool[u].r;
            else u = pool[u].l;
        }
        return res;
    }

    // O(logN expected) -- add one copy of x
    void add(T x) {
        addRaw(x, 1);
    }

    // O(logN expected) -- add cnt copies of val (nothing if cnt <= 0)
    void addCount(T val, long long cnt) {
        if (cnt > 0) addRaw(val, cnt);
    }

    // O(1 amortized) -- remove everything: afterwards it is as if newly built (same constructor arguments), so reuse it
    // instead of building a new one
    void clear() {
        clearData();
        resetCached();
    }

    // O(logN expected) -- how many copies of x
    long long count(T x) {
        return countOf(x);
    }

    // O(1) -- how many distinct values
    long long countDistinct() {
        return d;
    }

    // O(logN expected) -- how many distinct values v with lo <= v <= hi (0 if lo > hi)
    long long countDistinctInValRange(T lo, T hi) {
        if (hi < lo) return 0;
        return distinctLt(hi) - distinctLt(lo) + (countOf(hi) ? 1 : 0);
    }

    // O(logN expected) -- how many values > x
    long long countGtX(T x) {
        return n - le(x);
    }

    // O(logN expected) -- how many values >= x
    long long countGteX(T x) {
        return n - lt(x);
    }

    // O(logN expected) -- how many values v with lo <= v <= hi (0 if lo > hi)
    long long countInValRange(T lo, T hi) {
        return lo <= hi ? le(hi) - lt(lo) : 0;
    }

    // O(logN expected) -- how many values < x
    long long countLtX(T x) {
        return lt(x);
    }

    // O(logN expected) -- how many values <= x
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

    // O(1) -- largest value; throws out_of_range if empty
    T max() {
        if (!n) throw out_of_range("max: the set is empty");
        return mx;
    }

    // O(1 amortized) -- largest difference between two neighbouring distinct values; -1 if fewer than 2 distinct values
    long long maxGap() {
        if (d < 2) return -1;
        return *gaps.rbegin();
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

    // O(logN expected) -- smallest non-negative integer not in the set
    long long mex() {
        return findMex();
    }

    // O(1) -- smallest value; throws out_of_range if empty
    T min() {
        if (!n) throw out_of_range("min: the set is empty");
        return mn;
    }

    // O(1 amortized) -- smallest difference between two values in the set (0 if some value has 2+ copies); -1 if fewer
    // than 2 values
    long long minAdjacentDiff() {
        if (n < 2) return -1;
        if (dups) return 0LL;
        return *gaps.begin();
    }

    // O(1) -- (a most frequent value, its count); throws out_of_range if empty. C++ returns the smallest of the most
    // frequent values
    pair<T, long long> mode() {
        if (!n) throw out_of_range("mode: the set is empty");
        auto& [f, vs] = *bk.rbegin();
        return pair<T, long long>{*vs.begin(), f};
    }

    // O(1) -- bitwise OR of all values; 0 if empty
    T orOfAll() {
        return pool[root].orv;
    }

    // O(logN expected) -- bitwise OR of the values > x; 0 if there are none
    T orOfGtX(T x) {
        if (x == numeric_limits<T>::max()) return T(0);
        return orGe(x + 1);
    }

    // O(logN expected) -- bitwise OR of the values >= x; 0 if there are none
    T orOfGteX(T x) {
        return orGe(x);
    }

    // O(logN expected) -- bitwise OR of the values v with lo <= v <= hi; 0 if there are none
    T orOfInValRange(T lo, T hi) {
        return lo <= hi ? orIn(lo, hi) : T(0);
    }

    // O(logN expected) -- bitwise OR of the kFrom-th through kTo-th largest values; RANKS, 1-indexed and inclusive:
    // (1, 1) is just the largest, (5, 8) the 5th, 6th, 7th and 8th largest, (1, size) every value (copies count);
    // throws out_of_range unless 1 <= kFrom <= kTo <= size
    T orOfKthLargestRange(long long kFrom, long long kTo) {
        if (kFrom < 1 || kFrom > kTo || kTo > n) throw out_of_range("orOfKthLargestRange: needs 1 <= kFrom <= kTo <= size");
        T a = kthAt(n - kTo + 1);
        return orIn(a, kthAt(n - kFrom + 1));
    }

    // O(logN expected) -- bitwise OR of the kFrom-th through kTo-th smallest values; RANKS, 1-indexed and inclusive:
    // (1, 1) is just the smallest, (2, 4) the 2nd, 3rd and 4th smallest, (1, size) every value (copies count); throws
    // out_of_range unless 1 <= kFrom <= kTo <= size
    T orOfKthSmallestRange(long long kFrom, long long kTo) {
        if (kFrom < 1 || kFrom > kTo || kTo > n) throw out_of_range("orOfKthSmallestRange: needs 1 <= kFrom <= kTo <= size");
        T a = kthAt(kFrom);
        return orIn(a, kthAt(kTo));
    }

    // O(logN expected) -- bitwise OR of the k largest values; k is a COUNT, not an index: k = 0 takes no values
    // (returns 0), k = 1 just the largest, k = size every value (copies count: in {2, 5, 5}, k = 2 takes 5 and 5);
    // throws out_of_range unless 0 <= k <= size
    T orOfLargestK(long long k) {
        if (k < 0 || k > n) throw out_of_range("orOfLargestK: needs 0 <= k <= size");
        return k ? orGe(kthAt(n - k + 1)) : T(0);
    }

    // O(logN expected) -- bitwise OR of the values < x; 0 if there are none
    T orOfLtX(T x) {
        if (x == numeric_limits<T>::min()) return T(0);
        return orLe(x - 1);
    }

    // O(logN expected) -- bitwise OR of the values <= x; 0 if there are none
    T orOfLteX(T x) {
        return orLe(x);
    }

    // O(logN expected) -- bitwise OR of the k smallest values; k is a COUNT, not an index: k = 0 takes no values
    // (returns 0), k = 1 just the smallest, k = size every value (copies count: in {2, 2, 5}, k = 2 takes 2 and 2);
    // throws out_of_range unless 0 <= k <= size
    T orOfSmallestK(long long k) {
        if (k < 0 || k > n) throw out_of_range("orOfSmallestK: needs 0 <= k <= size");
        return k ? orLe(kthAt(k)) : T(0);
    }

    // O(logN expected) -- remove and return the value at sorted position i, 0-indexed: pop(0) removes the smallest (=
    // popMin()), pop(size - 1) the largest (copies count); throws out_of_range unless 0 <= i < size
    T pop(long long i) {
        if (i < 0 || i >= n) throw out_of_range("pop: needs 0 <= i < size");
        T v = kthAt(i + 1);
        addRaw(v, -1);
        return v;
    }

    // O(logN expected) -- remove and return the largest value; throws out_of_range if empty
    T popMax() {
        if (!n) throw out_of_range("popMax: the set is empty");
        T v = mx;
        addRaw(v, -1);
        return v;
    }

    // O(logN expected) -- remove and return the smallest value; throws out_of_range if empty
    T popMin() {
        if (!n) throw out_of_range("popMin: the set is empty");
        T v = mn;
        addRaw(v, -1);
        return v;
    }

    // O(logN expected) -- remove one copy of x if present; returns how many were removed (0 or 1)
    long long remove(T x) {
        if (!count(x)) return 0;
        addRaw(x, -1);
        return 1;
    }

    // O(logN expected) -- remove every copy of val; returns how many were removed
    long long removeAll(T val) {
        long long k = count(val);
        if (k) addRaw(val, -k);
        return k;
    }

    // O(logN expected) -- remove min(cnt, count(val)) copies of val; returns how many were removed
    long long removeCount(T val, long long cnt) {
        long long k = std::min(cnt, count(val));
        if (k <= 0) return 0;
        addRaw(val, -k);
        return k;
    }

    // O(logN expected) -- remove every value v with lo <= v <= hi; returns how many copies were removed (0 if lo > hi)
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

    // O(logN expected) -- sum of |v - medianLow()| over all values (min total moves to make all equal); 0 if empty
    S sumAbsDiffToMedian() {
        if (!n) return 0;
        Info m = kthInfo((n + 1) / 2);
        return S(m.v) * m.before - m.sb + (total - m.sb - S(m.v) * m.c) - S(m.v) * (n - m.before - m.c);
    }

    // O(logN expected) -- sum of |v - x| over all values
    S sumAbsDiffToX(T x) {
        long long c = lt(x);
        S s = slt(x);
        return S(x) * c - s + (total - s) - S(x) * (n - c);
    }

    // O(1) -- sum of all values
    S sumAll() {
        return total;
    }

    // O(logN expected) -- sum of the values > x
    S sumGtX(T x) {
        return total - sle(x);
    }

    // O(logN expected) -- sum of the values >= x
    S sumGteX(T x) {
        return total - slt(x);
    }

    // O(logN expected) -- sum of the values v with lo <= v <= hi (0 if lo > hi)
    S sumInValRange(T lo, T hi) {
        return lo <= hi ? sle(hi) - slt(lo) : S(0);
    }

    // O(logN expected) -- sum of the kFrom-th through kTo-th largest values; RANKS, 1-indexed and inclusive: (1, 1) is
    // just the largest, (5, 8) the 5th, 6th, 7th and 8th largest, (1, size) every value (copies count); throws
    // out_of_range unless 1 <= kFrom <= kTo <= size
    S sumKthLargestRange(long long kFrom, long long kTo) {
        if (kFrom < 1 || kFrom > kTo || kTo > n) throw out_of_range("sumKthLargestRange: needs 1 <= kFrom <= kTo <= size");
        return sumFirst(n - kFrom + 1) - sumFirst(n - kTo);
    }

    // O(logN expected) -- sum of the kFrom-th through kTo-th smallest values; RANKS, 1-indexed and inclusive: (1, 1) is
    // just the smallest, (2, 4) the 2nd, 3rd and 4th smallest, (1, size) every value (copies count); throws
    // out_of_range unless 1 <= kFrom <= kTo <= size
    S sumKthSmallestRange(long long kFrom, long long kTo) {
        if (kFrom < 1 || kFrom > kTo || kTo > n) throw out_of_range("sumKthSmallestRange: needs 1 <= kFrom <= kTo <= size");
        return sumFirst(kTo) - sumFirst(kFrom - 1);
    }

    // O(logN expected) -- sum of the k largest values; k is a COUNT, not an index: k = 0 takes no values (returns 0), k
    // = 1 just the largest, k = size every value (copies count: in {2, 5, 5}, k = 2 takes 5 and 5); throws out_of_range
    // unless 0 <= k <= size
    S sumLargestK(long long k) {
        if (k < 0 || k > n) throw out_of_range("sumLargestK: needs 0 <= k <= size");
        return total - sumFirst(n - k);
    }

    // O(logN expected) -- sum of the values < x
    S sumLtX(T x) {
        return slt(x);
    }

    // O(logN expected) -- sum of the values <= x
    S sumLteX(T x) {
        return sle(x);
    }

    // O(logN expected) -- sum of the k smallest values; k is a COUNT, not an index: k = 0 takes no values (returns 0),
    // k = 1 just the smallest, k = size every value (copies count: in {2, 2, 5}, k = 2 takes 2 and 2); throws
    // out_of_range unless 0 <= k <= size
    S sumSmallestK(long long k) {
        if (k < 0 || k > n) throw out_of_range("sumSmallestK: needs 0 <= k <= size");
        return sumFirst(k);
    }

    // O(1) -- xor of all values (copies count: a value with an even count cancels out); 0 if empty
    T xorOfAll() {
        return xtotal;
    }

    // O(logN expected) -- xor of the values > x (copies count)
    T xorOfGtX(T x) {
        return xtotal ^ xle(x);
    }

    // O(logN expected) -- xor of the values >= x (copies count)
    T xorOfGteX(T x) {
        return xtotal ^ xlt(x);
    }

    // O(logN expected) -- xor of the values v with lo <= v <= hi (copies count; 0 if lo > hi)
    T xorOfInValRange(T lo, T hi) {
        return lo <= hi ? T(xle(hi) ^ xlt(lo)) : T(0);
    }

    // O(logN expected) -- xor of the kFrom-th through kTo-th largest values; RANKS, 1-indexed and inclusive: (1, 1) is
    // just the largest, (5, 8) the 5th, 6th, 7th and 8th largest, (1, size) every value (copies count); throws
    // out_of_range unless 1 <= kFrom <= kTo <= size
    T xorOfKthLargestRange(long long kFrom, long long kTo) {
        if (kFrom < 1 || kFrom > kTo || kTo > n) throw out_of_range("xorOfKthLargestRange: needs 1 <= kFrom <= kTo <= size");
        return xorFirst(n - kFrom + 1) ^ xorFirst(n - kTo);
    }

    // O(logN expected) -- xor of the kFrom-th through kTo-th smallest values; RANKS, 1-indexed and inclusive: (1, 1) is
    // just the smallest, (2, 4) the 2nd, 3rd and 4th smallest, (1, size) every value (copies count); throws
    // out_of_range unless 1 <= kFrom <= kTo <= size
    T xorOfKthSmallestRange(long long kFrom, long long kTo) {
        if (kFrom < 1 || kFrom > kTo || kTo > n) throw out_of_range("xorOfKthSmallestRange: needs 1 <= kFrom <= kTo <= size");
        return xorFirst(kTo) ^ xorFirst(kFrom - 1);
    }

    // O(logN expected) -- xor of the k largest values; k is a COUNT, not an index: k = 0 takes no values (returns 0), k
    // = 1 just the largest, k = size every value (copies count: in {2, 5, 5}, k = 2 takes 5 and 5); throws out_of_range
    // unless 0 <= k <= size
    T xorOfLargestK(long long k) {
        if (k < 0 || k > n) throw out_of_range("xorOfLargestK: needs 0 <= k <= size");
        return xtotal ^ xorFirst(n - k);
    }

    // O(logN expected) -- xor of the values < x (copies count)
    T xorOfLtX(T x) {
        return xlt(x);
    }

    // O(logN expected) -- xor of the values <= x (copies count)
    T xorOfLteX(T x) {
        return xle(x);
    }

    // O(logN expected) -- xor of the k smallest values; k is a COUNT, not an index: k = 0 takes no values (returns 0),
    // k = 1 just the smallest, k = size every value (copies count: in {2, 2, 5}, k = 2 takes 2 and 2); throws
    // out_of_range unless 0 <= k <= size
    T xorOfSmallestK(long long k) {
        if (k < 0 || k > n) throw out_of_range("xorOfSmallestK: needs 0 <= k <= size");
        return xorFirst(k);
    }
};
