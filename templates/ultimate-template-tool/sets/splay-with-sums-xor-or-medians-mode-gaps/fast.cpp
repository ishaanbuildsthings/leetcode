// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/sets/splay-with-sums-xor-or-medians-mode-gaps/fast.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: add addCount clear count countDistinct countGtX countGteX countInValRange countLtX countLteX firstIndex kth largestLtX largestLteX lastIndex max maxGap medianHigh medianLow min minAdjacentDiff mode orOfAll orOfGtX orOfGteX orOfInValRange orOfKthLargestRange orOfKthSmallestRange orOfLargestK orOfLtX orOfLteX orOfSmallestK pop popMax popMin remove removeAll removeCount removeInValRange size smallestGtX smallestGteX sumAbsDiffToMedian sumAbsDiffToX sumAll sumGtX sumGteX sumInValRange sumKthLargestRange sumKthSmallestRange sumLargestK sumLtX sumLteX sumSmallestK xorOfAll xorOfGtX xorOfGteX xorOfInValRange xorOfKthLargestRange xorOfKthSmallestRange xorOfLargestK xorOfLtX xorOfLteX xorOfSmallestK
// @data-structure-type: splay
// @values: online
// @keys: numbers
// @tracks: medians mode gaps
// @complexities:
//   add: log(N) amortized
//   addCount: log(N) amortized
//   clear: 1 amortized
//   count: log(N) amortized
//   countDistinct: 1
//   countGtX: log(N) amortized
//   countGteX: log(N) amortized
//   countInValRange: log(N) amortized
//   countLtX: log(N) amortized
//   countLteX: log(N) amortized
//   firstIndex: log(N) amortized
//   kth: log(N) amortized
//   largestLtX: log(N) amortized
//   largestLteX: log(N) amortized
//   lastIndex: log(N) amortized
//   max: log(N) amortized
//   maxGap: 1 amortized
//   medianHigh: 1
//   medianLow: 1
//   min: log(N) amortized
//   minAdjacentDiff: 1 amortized
//   mode: 1
//   orOfAll: 1
//   orOfGtX: log(N) amortized
//   orOfGteX: log(N) amortized
//   orOfInValRange: log(N) amortized
//   orOfKthLargestRange: log(N) amortized
//   orOfKthSmallestRange: log(N) amortized
//   orOfLargestK: log(N) amortized
//   orOfLtX: log(N) amortized
//   orOfLteX: log(N) amortized
//   orOfSmallestK: log(N) amortized
//   pop: log(N) amortized
//   popMax: log(N) amortized
//   popMin: log(N) amortized
//   remove: log(N) amortized
//   removeAll: log(N) amortized
//   removeCount: log(N) amortized
//   removeInValRange: log(N) amortized
//   size: 1
//   smallestGtX: log(N) amortized
//   smallestGteX: log(N) amortized
//   sumAbsDiffToMedian: 1
//   sumAbsDiffToX: log(N) amortized
//   sumAll: 1
//   sumGtX: log(N) amortized
//   sumGteX: log(N) amortized
//   sumInValRange: log(N) amortized
//   sumKthLargestRange: log(N) amortized
//   sumKthSmallestRange: log(N) amortized
//   sumLargestK: log(N) amortized
//   sumLtX: log(N) amortized
//   sumLteX: log(N) amortized
//   sumSmallestK: log(N) amortized
//   xorOfAll: 1
//   xorOfGtX: log(N) amortized
//   xorOfGteX: log(N) amortized
//   xorOfInValRange: log(N) amortized
//   xorOfKthLargestRange: log(N) amortized
//   xorOfKthSmallestRange: log(N) amortized
//   xorOfLargestK: log(N) amortized
//   xorOfLtX: log(N) amortized
//   xorOfLteX: log(N) amortized
//   xorOfSmallestK: log(N) amortized
//   build: 1
// @memory:
//   layout: none
//   node: key[1*N] cnt[1*N] size[1*N] sum[1*N] xor[1*N] or[1*N]
//   tags: none
//   other: children[2*N] parent[1*N]
//   note: N = most distinct values present at once (removed nodes are reused). C++: each multiset owns its node pool; Python: parallel lists per tree

// Ordered multiset (online: any values, nothing known ahead): a splay tree with one node per distinct value. Each node
// keeps its value, its copies, and the copies, sum, xor, OR in its subtree; every operation splays the
// last node it touched to the root, which makes each one O(log N) amortized. Each multiset owns its node pool
// (freed when it goes out of scope; clear() keeps it for reuse); node 0 is the empty tree and removed nodes are reused.
// T: an integer type; sums in S (long long for small T).
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
struct SplayMultiset {
    template <class K>
    LEETCODE_NO_SANITIZE static K noneOf() {  // the lowest value of K, part by part for pairs and tuples
        if constexpr (is_arithmetic_v<K>) return numeric_limits<K>::lowest();
        else return apply([](auto... parts) { return K{noneOf<decltype(parts)>()...}; }, K{});
    }
    static inline const T NONE = noneOf<T>();  // what largestLtX, smallestGtX, ... return when nothing qualifies: compare with ms.NONE

    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    struct Node { T key; long long c, z; S s; T xr; T orv; int l, r, p; };  // copies; copies, sum below; parent
    FlatPool<Node> pool{1};
    FlatPool<int> freeList;
    int root = 0;
    long long n = 0, d = 0;
    struct Info { T v; long long before, c; S sb; };  // a value, copies before it, its copies, sum before it
    Info low{}, high{};  // both medians, kept current by addRaw while n > 0
    map<long long, set<T>> bk;  // mode: count -> the values with that many copies
    multiset<long long> gaps;  // differences between neighbouring distinct values
    long long dups = 0;  // values with 2+ copies
    T xtotal = 0;  // xor of all values (copies count)
    S total = 0;

    // O(1) -- an empty multiset
    SplayMultiset() {}


    // optional -- reserve room for this many nodes up front
    LEETCODE_NO_SANITIZE void reservePool(size_t nodes) { pool.reserve(nodes); }

    LEETCODE_NO_SANITIZE int make(T x, int parent) {
        int t;
        if (!freeList.empty()) t = freeList.back(), freeList.pop_back();
        else pool.push_back(Node{}), t = (int)pool.size() - 1;
        pool[t] = Node{};
        pool[t].key = x, pool[t].p = parent;
        return t;
    }

    LEETCODE_NO_SANITIZE void pull(int t) {
        Node& v = pool[t];
        const Node &a = pool[v.l], &b = pool[v.r];
        v.z = a.z + b.z + v.c;
        v.xr = a.xr ^ b.xr ^ (v.c & 1 ? v.key : T(0));
        v.orv = a.orv | b.orv | v.key;
        v.s = a.s + b.s + S(v.c) * v.key;
    }

    LEETCODE_NO_SANITIZE void rotate(int x) {  // x moves above its parent
        int p = pool[x].p, g = pool[p].p, b;
        if (pool[p].l == x) b = pool[x].r, pool[p].l = b, pool[x].r = p;
        else b = pool[x].l, pool[p].r = b, pool[x].l = p;
        if (b) pool[b].p = p;
        pool[p].p = x, pool[x].p = g;
        if (g) (pool[g].l == p ? pool[g].l : pool[g].r) = x;
        pull(p);  // (x is pulled once, when it reaches the root)
    }

    LEETCODE_NO_SANITIZE int splay(int x) {  // x becomes the root of its tree
        while (int p = pool[x].p) {
            if (int g = pool[p].p) rotate((pool[g].l == p) == (pool[p].l == x) ? p : x);
            rotate(x);
        }
        pull(x);
        return x;
    }

    LEETCODE_NO_SANITIZE void touch(int t) {
        if (t) root = splay(t);
    }

    LEETCODE_NO_SANITIZE long long insert(T x, long long c) {  // returns x's new count
        int t = root;
        while (t && pool[t].key != x) {
            int nxt = x < pool[t].key ? pool[t].l : pool[t].r;
            if (!nxt) break;
            t = nxt;
        }
        if (t && pool[t].key == x) {  // x is already here
            long long f = pool[t].c += c;
            pull(t);
            root = splay(t);
            if (!f) erase(t);
            return f;
        }
        int u = make(x, t);
        pool[u].c = c;
        pull(u);
        if (t) (x < pool[t].key ? pool[t].l : pool[t].r) = u;
        root = splay(u);
        d++;
        return c;
    }

    LEETCODE_NO_SANITIZE void erase(int t) {  // t is the root
        int l = pool[t].l, r = pool[t].r;
        if (l) pool[l].p = 0;
        if (r) pool[r].p = 0;
        if (!l) root = r;
        else {
            int m = l;
            while (pool[m].r) m = pool[m].r;
            m = splay(m);  // the largest key on the left becomes the left tree's root, with no right child
            pool[m].r = r;
            if (r) pool[r].p = m;
            pull(m);
            root = m;
        }
        freeList.push_back(t);
        d--;
    }

    LEETCODE_NO_SANITIZE long long lt(T x) {  // copies of values < x
        int t = root, last = 0;
        long long res = 0;
        while (t) {
            last = t;
            if (pool[t].key < x) res += pool[pool[t].l].z + pool[t].c, t = pool[t].r;
            else t = pool[t].l;
        }
        touch(last);
        return res;
    }

    LEETCODE_NO_SANITIZE long long le(T x) {  // copies of values <= x
        int t = root, last = 0;
        long long res = 0;
        while (t) {
            last = t;
            if (x < pool[t].key) t = pool[t].l;
            else res += pool[pool[t].l].z + pool[t].c, t = pool[t].r;
        }
        touch(last);
        return res;
    }

    LEETCODE_NO_SANITIZE long long countOf(T x) {
        int t = root, last = 0;
        while (t && pool[t].key != x) last = t, t = x < pool[t].key ? pool[t].l : pool[t].r;
        touch(t ? t : last);
        return pool[t].c;
    }

    LEETCODE_NO_SANITIZE S slt(T x) {  // sum of the values < x
        int t = root, last = 0;
        S res = 0;
        while (t) {
            last = t;
            if (pool[t].key < x) res += pool[pool[t].l].s + S(pool[t].c) * pool[t].key, t = pool[t].r;
            else t = pool[t].l;
        }
        touch(last);
        return res;
    }

    LEETCODE_NO_SANITIZE S sle(T x) {  // sum of the values <= x
        int t = root, last = 0;
        S res = 0;
        while (t) {
            last = t;
            if (x < pool[t].key) t = pool[t].l;
            else res += pool[pool[t].l].s + S(pool[t].c) * pool[t].key, t = pool[t].r;
        }
        touch(last);
        return res;
    }

    LEETCODE_NO_SANITIZE T kthAt(long long k) {
        int t = root;
        while (true) {
            long long zl = pool[pool[t].l].z;
            if (k <= zl) t = pool[t].l;
            else if (k <= zl + pool[t].c) {
                touch(t);
                return pool[t].key;
            } else k -= zl + pool[t].c, t = pool[t].r;
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
            else if (k <= zl + v.c) {
                Info res{v.key, zl, v.c, acc + pool[v.l].s};
                touch(t);
                return res;
            } else before = zl + v.c, acc += pool[v.l].s + S(v.c) * v.key, t = v.r;
        }
    }

    LEETCODE_NO_SANITIZE void addRaw(T x, long long c) {  // c copies of x (c < 0 removes); keeps both medians current
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

    LEETCODE_NO_SANITIZE S sumFirst(long long k) {  // sum of the k smallest values
        if (k <= 0) return 0;
        Info f = kthInfo(k);
        return f.sb + S(k - f.before) * f.v;
    }

    LEETCODE_NO_SANITIZE void resetCached() {  // nothing counted: as newly built
        bk.clear();
        gaps.clear(), dups = 0;
        n = d = 0;
        total = 0;
        xtotal = 0;
    }

    LEETCODE_NO_SANITIZE void clearData() {  // drop every node but keep the pool's memory for the next adds
        pool.resize(1), freeList.clear(), root = 0;
    }

    LEETCODE_NO_SANITIZE T xlt(T x) {  // xor of the values < x (copies count)
        int t = root;
        int last = 0;
        T res = 0;
        while (t) {
            last = t;
            const Node& v = pool[t];
            if (v.key < x) res ^= pool[v.l].xr ^ (v.c & 1 ? v.key : T(0)), t = v.r;
            else t = v.l;
        }
        touch(last);
        return res;
    }

    LEETCODE_NO_SANITIZE T xle(T x) {  // xor of the values <= x (copies count)
        int t = root;
        int last = 0;
        T res = 0;
        while (t) {
            last = t;
            const Node& v = pool[t];
            if (x < v.key) t = v.l;
            else res ^= pool[v.l].xr ^ (v.c & 1 ? v.key : T(0)), t = v.r;
        }
        touch(last);
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
                touch(t);
                return res;
            } else k -= zl + v.c, res ^= pool[v.l].xr ^ (v.c & 1 ? v.key : T(0)), t = v.r;
        }
    }

    LEETCODE_NO_SANITIZE T orLe(T x) {  // OR of the values <= x
        int t = root;
        int last = 0;
        T res = T(0);
        while (t) {
            last = t;
            if (x < pool[t].key) t = pool[t].l;
            else res |= pool[pool[t].l].orv | pool[t].key, t = pool[t].r;
        }
        touch(last);
        return res;
    }

    LEETCODE_NO_SANITIZE T orGe(T x) {  // OR of the values >= x
        int t = root;
        int last = 0;
        T res = T(0);
        while (t) {
            last = t;
            if (pool[t].key < x) t = pool[t].r;
            else res |= pool[pool[t].r].orv | pool[t].key, t = pool[t].l;
        }
        touch(last);
        return res;
    }

    LEETCODE_NO_SANITIZE T orIn(T lo, T hi) {  // OR of the values in [lo, hi] (lo <= hi)
        int t = root;
        int last = 0;
        while (t && (pool[t].key < lo || hi < pool[t].key)) {  // down to the highest node inside [lo, hi]
            last = t;
            t = hi < pool[t].key ? pool[t].l : pool[t].r;
        }
        if (!t) {
            touch(last);
            return T(0);
        }
        T res = pool[t].key;
        int a = t, na = 0, b = t, nb = 0;
        for (int u = pool[t].l; u;) {  // its left side is <= hi: keep what is >= lo
            a = u, na++;
            if (lo <= pool[u].key) res |= pool[u].key | pool[pool[u].r].orv, u = pool[u].l;
            else u = pool[u].r;
        }
        for (int u = pool[t].r; u;) {  // its right side is >= lo: keep what is <= hi
            b = u, nb++;
            if (pool[u].key <= hi) res |= pool[u].key | pool[pool[u].l].orv, u = pool[u].r;
            else u = pool[u].l;
        }
        touch(na >= nb ? a : b);  // the end of the longer path pays for both
        return res;
    }

    // O(logN amortized) -- add one copy of x
    LEETCODE_NO_SANITIZE void add(T x) {
        addRaw(x, 1);
    }

    // O(logN amortized) -- add cnt copies of val (nothing if cnt <= 0)
    LEETCODE_NO_SANITIZE void addCount(T val, long long cnt) {
        if (cnt > 0) addRaw(val, cnt);
    }

    // O(1 amortized) -- remove everything: afterwards it is as if newly built (same constructor arguments), so reuse it
    // instead of building a new one
    LEETCODE_NO_SANITIZE void clear() {
        clearData();
        resetCached();
    }

    // O(logN amortized) -- how many copies of x
    LEETCODE_NO_SANITIZE long long count(T x) {
        return countOf(x);
    }

    // O(1) -- how many distinct values
    LEETCODE_NO_SANITIZE long long countDistinct() {
        return d;
    }

    // O(logN amortized) -- how many values > x
    LEETCODE_NO_SANITIZE long long countGtX(T x) {
        return n - le(x);
    }

    // O(logN amortized) -- how many values >= x
    LEETCODE_NO_SANITIZE long long countGteX(T x) {
        return n - lt(x);
    }

    // O(logN amortized) -- how many values v with lo <= v <= hi (0 if lo > hi)
    LEETCODE_NO_SANITIZE long long countInValRange(T lo, T hi) {
        return lo <= hi ? le(hi) - lt(lo) : 0;
    }

    // O(logN amortized) -- how many values < x
    LEETCODE_NO_SANITIZE long long countLtX(T x) {
        return lt(x);
    }

    // O(logN amortized) -- how many values <= x
    LEETCODE_NO_SANITIZE long long countLteX(T x) {
        return le(x);
    }

    // O(logN amortized) -- 0-indexed position of the first copy of x in sorted order (= how many values < x); -1 if x
    // is not in the set
    LEETCODE_NO_SANITIZE long long firstIndex(T x) {
        return countOf(x) ? lt(x) : -1;
    }

    // O(logN amortized) -- the value at sorted position i, 0-indexed: kth(0) is the smallest, kth(1) the 2nd smallest,
    // kth(size - 1) the largest (copies count: in {2, 2, 5}, kth(1) is 2); throws out_of_range unless 0 <= i < size
    LEETCODE_NO_SANITIZE T kth(long long i) {
        if (i < 0 || i >= n) throw out_of_range("kth: needs 0 <= i < size");
        return kthAt(i + 1);
    }

    // O(logN amortized) -- largest value < x; ms.NONE if there is none
    LEETCODE_NO_SANITIZE T largestLtX(T x) {
        long long c = lt(x);
        if (!c) return NONE;
        return kthAt(c);
    }

    // O(logN amortized) -- largest value <= x; ms.NONE if there is none
    LEETCODE_NO_SANITIZE T largestLteX(T x) {
        long long c = le(x);
        if (!c) return NONE;
        return kthAt(c);
    }

    // O(logN amortized) -- 0-indexed position of the last copy of x in sorted order (= how many values <= x, minus 1);
    // -1 if x is not in the set
    LEETCODE_NO_SANITIZE long long lastIndex(T x) {
        return countOf(x) ? le(x) - 1 : -1;
    }

    // O(logN amortized) -- largest value; throws out_of_range if empty
    LEETCODE_NO_SANITIZE T max() {
        if (!n) throw out_of_range("max: the set is empty");
        return kthAt(n);
    }

    // O(1 amortized) -- largest difference between two neighbouring distinct values; -1 if fewer than 2 distinct values
    LEETCODE_NO_SANITIZE long long maxGap() {
        if (d < 2) return -1;
        return *gaps.rbegin();
    }

    // O(1) -- upper median: the (floor(size/2) + 1)-th smallest value; throws out_of_range if empty
    LEETCODE_NO_SANITIZE T medianHigh() {
        if (!n) throw out_of_range("medianHigh: the set is empty");
        return high.v;
    }

    // O(1) -- lower median: the ceil(size/2)-th smallest value; throws out_of_range if empty
    LEETCODE_NO_SANITIZE T medianLow() {
        if (!n) throw out_of_range("medianLow: the set is empty");
        return low.v;
    }

    // O(logN amortized) -- smallest value; throws out_of_range if empty
    LEETCODE_NO_SANITIZE T min() {
        if (!n) throw out_of_range("min: the set is empty");
        return kthAt(1);
    }

    // O(1 amortized) -- smallest difference between two values in the set (0 if some value has 2+ copies); -1 if fewer
    // than 2 values
    LEETCODE_NO_SANITIZE long long minAdjacentDiff() {
        if (n < 2) return -1;
        if (dups) return 0LL;
        return *gaps.begin();
    }

    // O(1) -- (a most frequent value, its count); throws out_of_range if empty. C++ returns the smallest of the most
    // frequent values
    LEETCODE_NO_SANITIZE pair<T, long long> mode() {
        if (!n) throw out_of_range("mode: the set is empty");
        auto& [f, vs] = *bk.rbegin();
        return pair<T, long long>{*vs.begin(), f};
    }

    // O(1) -- bitwise OR of all values; 0 if empty
    LEETCODE_NO_SANITIZE T orOfAll() {
        return pool[root].orv;
    }

    // O(logN amortized) -- bitwise OR of the values > x; 0 if there are none
    LEETCODE_NO_SANITIZE T orOfGtX(T x) {
        if (x == numeric_limits<T>::max()) return T(0);
        return orGe(x + 1);
    }

    // O(logN amortized) -- bitwise OR of the values >= x; 0 if there are none
    LEETCODE_NO_SANITIZE T orOfGteX(T x) {
        return orGe(x);
    }

    // O(logN amortized) -- bitwise OR of the values v with lo <= v <= hi; 0 if there are none
    LEETCODE_NO_SANITIZE T orOfInValRange(T lo, T hi) {
        return lo <= hi ? orIn(lo, hi) : T(0);
    }

    // O(logN amortized) -- bitwise OR of the kFrom-th through kTo-th largest values; RANKS, 1-indexed and inclusive:
    // (1, 1) is just the largest, (5, 8) the 5th, 6th, 7th and 8th largest, (1, size) every value (copies count);
    // throws out_of_range unless 1 <= kFrom <= kTo <= size
    LEETCODE_NO_SANITIZE T orOfKthLargestRange(long long kFrom, long long kTo) {
        if (kFrom < 1 || kFrom > kTo || kTo > n) throw out_of_range("orOfKthLargestRange: needs 1 <= kFrom <= kTo <= size");
        T a = kthAt(n - kTo + 1);
        return orIn(a, kthAt(n - kFrom + 1));
    }

    // O(logN amortized) -- bitwise OR of the kFrom-th through kTo-th smallest values; RANKS, 1-indexed and inclusive:
    // (1, 1) is just the smallest, (2, 4) the 2nd, 3rd and 4th smallest, (1, size) every value (copies count); throws
    // out_of_range unless 1 <= kFrom <= kTo <= size
    LEETCODE_NO_SANITIZE T orOfKthSmallestRange(long long kFrom, long long kTo) {
        if (kFrom < 1 || kFrom > kTo || kTo > n) throw out_of_range("orOfKthSmallestRange: needs 1 <= kFrom <= kTo <= size");
        T a = kthAt(kFrom);
        return orIn(a, kthAt(kTo));
    }

    // O(logN amortized) -- bitwise OR of the k largest values; k is a COUNT, not an index: k = 0 takes no values
    // (returns 0), k = 1 just the largest, k = size every value (copies count: in {2, 5, 5}, k = 2 takes 5 and 5);
    // throws out_of_range unless 0 <= k <= size
    LEETCODE_NO_SANITIZE T orOfLargestK(long long k) {
        if (k < 0 || k > n) throw out_of_range("orOfLargestK: needs 0 <= k <= size");
        return k ? orGe(kthAt(n - k + 1)) : T(0);
    }

    // O(logN amortized) -- bitwise OR of the values < x; 0 if there are none
    LEETCODE_NO_SANITIZE T orOfLtX(T x) {
        if (x == numeric_limits<T>::min()) return T(0);
        return orLe(x - 1);
    }

    // O(logN amortized) -- bitwise OR of the values <= x; 0 if there are none
    LEETCODE_NO_SANITIZE T orOfLteX(T x) {
        return orLe(x);
    }

    // O(logN amortized) -- bitwise OR of the k smallest values; k is a COUNT, not an index: k = 0 takes no values
    // (returns 0), k = 1 just the smallest, k = size every value (copies count: in {2, 2, 5}, k = 2 takes 2 and 2);
    // throws out_of_range unless 0 <= k <= size
    LEETCODE_NO_SANITIZE T orOfSmallestK(long long k) {
        if (k < 0 || k > n) throw out_of_range("orOfSmallestK: needs 0 <= k <= size");
        return k ? orLe(kthAt(k)) : T(0);
    }

    // O(logN amortized) -- remove and return the value at sorted position i, 0-indexed: pop(0) removes the smallest (=
    // popMin()), pop(size - 1) the largest (copies count); throws out_of_range unless 0 <= i < size
    LEETCODE_NO_SANITIZE T pop(long long i) {
        if (i < 0 || i >= n) throw out_of_range("pop: needs 0 <= i < size");
        T v = kthAt(i + 1);
        addRaw(v, -1);
        return v;
    }

    // O(logN amortized) -- remove and return the largest value; throws out_of_range if empty
    LEETCODE_NO_SANITIZE T popMax() {
        if (!n) throw out_of_range("popMax: the set is empty");
        T v = kthAt(n);
        addRaw(v, -1);
        return v;
    }

    // O(logN amortized) -- remove and return the smallest value; throws out_of_range if empty
    LEETCODE_NO_SANITIZE T popMin() {
        if (!n) throw out_of_range("popMin: the set is empty");
        T v = kthAt(1);
        addRaw(v, -1);
        return v;
    }

    // O(logN amortized) -- remove one copy of x if present; returns how many were removed (0 or 1)
    LEETCODE_NO_SANITIZE long long remove(T x) {
        if (!count(x)) return 0;
        addRaw(x, -1);
        return 1;
    }

    // O(logN amortized) -- remove every copy of val; returns how many were removed
    LEETCODE_NO_SANITIZE long long removeAll(T val) {
        long long k = count(val);
        if (k) addRaw(val, -k);
        return k;
    }

    // O(logN amortized) -- remove min(cnt, count(val)) copies of val; returns how many were removed
    LEETCODE_NO_SANITIZE long long removeCount(T val, long long cnt) {
        long long k = std::min(cnt, count(val));
        if (k <= 0) return 0;
        addRaw(val, -k);
        return k;
    }

    // O(logN amortized) -- remove every value v with lo <= v <= hi; returns how many copies were removed (0 if lo > hi)
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

    // O(logN amortized) -- smallest value > x; ms.NONE if there is none
    LEETCODE_NO_SANITIZE T smallestGtX(T x) {
        long long c = le(x);
        if (c == n) return NONE;
        return kthAt(c + 1);
    }

    // O(logN amortized) -- smallest value >= x; ms.NONE if there is none
    LEETCODE_NO_SANITIZE T smallestGteX(T x) {
        long long c = lt(x);
        if (c == n) return NONE;
        return kthAt(c + 1);
    }

    // O(1) -- sum of |v - medianLow()| over all values (min total moves to make all equal); 0 if empty
    LEETCODE_NO_SANITIZE S sumAbsDiffToMedian() {
        if (!n) return 0;
        const Info& m = low;
        return S(m.v) * m.before - m.sb + (total - m.sb - S(m.v) * m.c) - S(m.v) * (n - m.before - m.c);
    }

    // O(logN amortized) -- sum of |v - x| over all values
    LEETCODE_NO_SANITIZE S sumAbsDiffToX(T x) {
        long long c = lt(x);
        S s = slt(x);
        return S(x) * c - s + (total - s) - S(x) * (n - c);
    }

    // O(1) -- sum of all values
    LEETCODE_NO_SANITIZE S sumAll() {
        return total;
    }

    // O(logN amortized) -- sum of the values > x
    LEETCODE_NO_SANITIZE S sumGtX(T x) {
        return total - sle(x);
    }

    // O(logN amortized) -- sum of the values >= x
    LEETCODE_NO_SANITIZE S sumGteX(T x) {
        return total - slt(x);
    }

    // O(logN amortized) -- sum of the values v with lo <= v <= hi (0 if lo > hi)
    LEETCODE_NO_SANITIZE S sumInValRange(T lo, T hi) {
        return lo <= hi ? sle(hi) - slt(lo) : S(0);
    }

    // O(logN amortized) -- sum of the kFrom-th through kTo-th largest values; RANKS, 1-indexed and inclusive: (1, 1) is
    // just the largest, (5, 8) the 5th, 6th, 7th and 8th largest, (1, size) every value (copies count); throws
    // out_of_range unless 1 <= kFrom <= kTo <= size
    LEETCODE_NO_SANITIZE S sumKthLargestRange(long long kFrom, long long kTo) {
        if (kFrom < 1 || kFrom > kTo || kTo > n) throw out_of_range("sumKthLargestRange: needs 1 <= kFrom <= kTo <= size");
        return sumFirst(n - kFrom + 1) - sumFirst(n - kTo);
    }

    // O(logN amortized) -- sum of the kFrom-th through kTo-th smallest values; RANKS, 1-indexed and inclusive: (1, 1)
    // is just the smallest, (2, 4) the 2nd, 3rd and 4th smallest, (1, size) every value (copies count); throws
    // out_of_range unless 1 <= kFrom <= kTo <= size
    LEETCODE_NO_SANITIZE S sumKthSmallestRange(long long kFrom, long long kTo) {
        if (kFrom < 1 || kFrom > kTo || kTo > n) throw out_of_range("sumKthSmallestRange: needs 1 <= kFrom <= kTo <= size");
        return sumFirst(kTo) - sumFirst(kFrom - 1);
    }

    // O(logN amortized) -- sum of the k largest values; k is a COUNT, not an index: k = 0 takes no values (returns 0),
    // k = 1 just the largest, k = size every value (copies count: in {2, 5, 5}, k = 2 takes 5 and 5); throws
    // out_of_range unless 0 <= k <= size
    LEETCODE_NO_SANITIZE S sumLargestK(long long k) {
        if (k < 0 || k > n) throw out_of_range("sumLargestK: needs 0 <= k <= size");
        return total - sumFirst(n - k);
    }

    // O(logN amortized) -- sum of the values < x
    LEETCODE_NO_SANITIZE S sumLtX(T x) {
        return slt(x);
    }

    // O(logN amortized) -- sum of the values <= x
    LEETCODE_NO_SANITIZE S sumLteX(T x) {
        return sle(x);
    }

    // O(logN amortized) -- sum of the k smallest values; k is a COUNT, not an index: k = 0 takes no values (returns 0),
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

    // O(logN amortized) -- xor of the values > x (copies count)
    LEETCODE_NO_SANITIZE T xorOfGtX(T x) {
        return xtotal ^ xle(x);
    }

    // O(logN amortized) -- xor of the values >= x (copies count)
    LEETCODE_NO_SANITIZE T xorOfGteX(T x) {
        return xtotal ^ xlt(x);
    }

    // O(logN amortized) -- xor of the values v with lo <= v <= hi (copies count; 0 if lo > hi)
    LEETCODE_NO_SANITIZE T xorOfInValRange(T lo, T hi) {
        return lo <= hi ? T(xle(hi) ^ xlt(lo)) : T(0);
    }

    // O(logN amortized) -- xor of the kFrom-th through kTo-th largest values; RANKS, 1-indexed and inclusive: (1, 1) is
    // just the largest, (5, 8) the 5th, 6th, 7th and 8th largest, (1, size) every value (copies count); throws
    // out_of_range unless 1 <= kFrom <= kTo <= size
    LEETCODE_NO_SANITIZE T xorOfKthLargestRange(long long kFrom, long long kTo) {
        if (kFrom < 1 || kFrom > kTo || kTo > n) throw out_of_range("xorOfKthLargestRange: needs 1 <= kFrom <= kTo <= size");
        return xorFirst(n - kFrom + 1) ^ xorFirst(n - kTo);
    }

    // O(logN amortized) -- xor of the kFrom-th through kTo-th smallest values; RANKS, 1-indexed and inclusive: (1, 1)
    // is just the smallest, (2, 4) the 2nd, 3rd and 4th smallest, (1, size) every value (copies count); throws
    // out_of_range unless 1 <= kFrom <= kTo <= size
    LEETCODE_NO_SANITIZE T xorOfKthSmallestRange(long long kFrom, long long kTo) {
        if (kFrom < 1 || kFrom > kTo || kTo > n) throw out_of_range("xorOfKthSmallestRange: needs 1 <= kFrom <= kTo <= size");
        return xorFirst(kTo) ^ xorFirst(kFrom - 1);
    }

    // O(logN amortized) -- xor of the k largest values; k is a COUNT, not an index: k = 0 takes no values (returns 0),
    // k = 1 just the largest, k = size every value (copies count: in {2, 5, 5}, k = 2 takes 5 and 5); throws
    // out_of_range unless 0 <= k <= size
    LEETCODE_NO_SANITIZE T xorOfLargestK(long long k) {
        if (k < 0 || k > n) throw out_of_range("xorOfLargestK: needs 0 <= k <= size");
        return xtotal ^ xorFirst(n - k);
    }

    // O(logN amortized) -- xor of the values < x (copies count)
    LEETCODE_NO_SANITIZE T xorOfLtX(T x) {
        return xlt(x);
    }

    // O(logN amortized) -- xor of the values <= x (copies count)
    LEETCODE_NO_SANITIZE T xorOfLteX(T x) {
        return xle(x);
    }

    // O(logN amortized) -- xor of the k smallest values; k is a COUNT, not an index: k = 0 takes no values (returns 0),
    // k = 1 just the smallest, k = size every value (copies count: in {2, 2, 5}, k = 2 takes 2 and 2); throws
    // out_of_range unless 0 <= k <= size
    LEETCODE_NO_SANITIZE T xorOfSmallestK(long long k) {
        if (k < 0 || k > n) throw out_of_range("xorOfSmallestK: needs 0 <= k <= size");
        return xorFirst(k);
    }
};
