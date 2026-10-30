// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/sets/splay-with-or-and-cachedmex-gaps/template.cpp
// @operations: add addCount andOfAll andOfGtX andOfGteX andOfInValRange andOfKthLargestRange andOfKthSmallestRange andOfLargestK andOfLtX andOfLteX andOfSmallestK clear count countDistinct countDistinctInValRange countGtX countGteX countInValRange countLtX countLteX firstIndex kth largestLtX largestLteX lastIndex max maxGap medianHigh medianLow mex min minAdjacentDiff orOfAll orOfGtX orOfGteX orOfInValRange orOfKthLargestRange orOfKthSmallestRange orOfLargestK orOfLtX orOfLteX orOfSmallestK pop popMax popMin remove removeAll removeCount removeInValRange size smallestGtX smallestGteX
// @data-structure-type: splay
// @values: online
// @keys: numbers
// @tracks: mex gaps
// @complexities:
//   add: log(N) amortized
//   addCount: log(N) amortized
//   andOfAll: 1
//   andOfGtX: log(N) amortized
//   andOfGteX: log(N) amortized
//   andOfInValRange: log(N) amortized
//   andOfKthLargestRange: log(N) amortized
//   andOfKthSmallestRange: log(N) amortized
//   andOfLargestK: log(N) amortized
//   andOfLtX: log(N) amortized
//   andOfLteX: log(N) amortized
//   andOfSmallestK: log(N) amortized
//   clear: N
//   count: log(N) amortized
//   countDistinct: 1
//   countDistinctInValRange: log(N) amortized
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
//   medianHigh: log(N) amortized
//   medianLow: log(N) amortized
//   mex: 1
//   min: log(N) amortized
//   minAdjacentDiff: 1 amortized
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
//   build: 1
// @memory:
//   layout: none
//   node: key[1*N] cnt[1*N] size[1*N] dn[1*N] or[1*N] and[1*N]
//   tags: none
//   other: children[2*N] parent[1*N]
//   note: N = most distinct values present at once (removed nodes are reused). C++: each multiset owns its node pool; Python: parallel lists per tree

// Ordered multiset (online: any values, nothing known ahead): a splay tree with one node per distinct value. Each node
// keeps its value, its copies, and the copies, OR, AND and distinct values in its subtree; every operation splays the
// last node it touched to the root, which makes each one O(log N) amortized. Each multiset owns its node pool
// (freed when it goes out of scope; clear() keeps it for reuse); node 0 is the empty tree and removed nodes are reused.
// T: an integer type; sums in S (long long for small T).
template <typename T>
struct SplayMultiset {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    struct Node { T key; long long c, z; long long dn; T orv; T andv = ~T(0); int l, r, p; };  // copies; copies, distinct below; parent
    vector<Node> pool{Node{}};
    vector<int> freeList;
    int root = 0;
    long long n = 0, d = 0;
    struct Info { T v; long long before, c; };  // a value, copies before it, its copies
    long long mexV = 0;  // the mex, kept current (0 for the empty set)
    multiset<long long> gaps;  // differences between neighbouring distinct values
    long long dups = 0;  // values with 2+ copies

    // O(1) -- an empty multiset
    SplayMultiset() {}


    // optional -- reserve room for this many nodes up front
    void reservePool(size_t nodes) { pool.reserve(nodes); }

    int make(T x, int parent) {
        int t;
        if (!freeList.empty()) t = freeList.back(), freeList.pop_back();
        else pool.push_back(Node{}), t = (int)pool.size() - 1;
        pool[t] = Node{};
        pool[t].key = x, pool[t].p = parent;
        return t;
    }

    void pull(int t) {
        Node& v = pool[t];
        const Node &a = pool[v.l], &b = pool[v.r];
        v.z = a.z + b.z + v.c;
        v.dn = a.dn + b.dn + 1;
        v.orv = a.orv | b.orv | v.key;
        v.andv = a.andv & b.andv & v.key;
    }

    void rotate(int x) {  // x moves above its parent
        int p = pool[x].p, g = pool[p].p, b;
        if (pool[p].l == x) b = pool[x].r, pool[p].l = b, pool[x].r = p;
        else b = pool[x].l, pool[p].r = b, pool[x].l = p;
        if (b) pool[b].p = p;
        pool[p].p = x, pool[x].p = g;
        if (g) (pool[g].l == p ? pool[g].l : pool[g].r) = x;
        pull(p), pull(x);
    }

    int splay(int x) {  // x becomes the root of its tree
        while (int p = pool[x].p) {
            if (int g = pool[p].p) rotate((pool[g].l == p) == (pool[p].l == x) ? p : x);
            rotate(x);
        }
        return x;
    }

    void touch(int t) {
        if (t) root = splay(t);
    }

    long long insert(T x, long long c) {  // returns x's new count
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

    void erase(int t) {  // t is the root
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

    long long lt(T x) {  // copies of values < x
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

    long long le(T x) {  // copies of values <= x
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

    long long countOf(T x) {
        int t = root, last = 0;
        while (t && pool[t].key != x) last = t, t = x < pool[t].key ? pool[t].l : pool[t].r;
        touch(t ? t : last);
        return pool[t].c;
    }

    T kthAt(long long k) {
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
    Info kthInfo(long long k) {  // the k-th smallest, copies before it, its copies
        int t = root;
        long long before = 0;
        while (true) {
            const Node& v = pool[t];
            long long zl = before + pool[v.l].z;
            if (k <= zl) t = v.l;
            else if (k <= zl + v.c) {
                Info res{v.key, zl, v.c};
                touch(t);
                return res;
            } else before = zl + v.c, t = v.r;
        }
    }
    long long distinctLt(T x) {  // distinct values < x
        int t = root, last = 0;
        long long res = 0;
        while (t) {
            last = t;
            if (pool[t].key < x) res += pool[pool[t].l].dn + 1, t = pool[t].r;
            else t = pool[t].l;
        }
        touch(last);
        return res;
    }

    // smallest non-negative integer not in the set. With c0 distinct negatives, the distinct values >= 0
    // in order v_0 < v_1 < ... satisfy v_j >= j, and v_j == j means 0..v_j are all present; the answer is the first j
    // with v_j > j (or how many there are). One walk down: at a node of distinct rank c0 + j, go right if v_j == j.
    long long findMex() {
        long long c0 = distinctLt(0), before = -c0, res = d - c0;  // before: distinct values >= 0 left of t's subtree
        int t = root, last = 0;
        while (t) {
            last = t;
            long long j = before + pool[pool[t].l].dn;
            if (pool[t].key < 0 || pool[t].key == T(j)) before = j + 1, t = pool[t].r;
            else res = j, t = pool[t].l;
        }
        touch(last);
        return res;
    }

    void addRaw(T x, long long c) {  // c copies of x (c < 0 removes); keeps the mex current
        n += c;
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
            if constexpr (is_integral_v<T>) if (x == T(mexV)) mexV = findMex();  // x filled the mex
        } else {
            if constexpr (is_integral_v<T>) if (x >= 0 && x < T(mexV) && !f) mexV = x;  // the last copy of a value below the mex
        }
    }

    void resetCached() {  // nothing counted: as newly built
        mexV = 0;
        gaps.clear(), dups = 0;
        n = d = 0;
    }

    void clearData() {  // drop every node but keep the pool's memory for the next adds
        pool.resize(1), freeList.clear(), root = 0;
    }

    T orLe(T x) {  // OR of the values <= x
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

    T orGe(T x) {  // OR of the values >= x
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

    T orIn(T lo, T hi) {  // OR of the values in [lo, hi] (lo <= hi)
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

    T andLe(T x) {  // AND of the values <= x
        int t = root;
        int last = 0;
        T res = ~T(0);
        while (t) {
            last = t;
            if (x < pool[t].key) t = pool[t].l;
            else res &= pool[pool[t].l].andv & pool[t].key, t = pool[t].r;
        }
        touch(last);
        return res;
    }

    T andGe(T x) {  // AND of the values >= x
        int t = root;
        int last = 0;
        T res = ~T(0);
        while (t) {
            last = t;
            if (pool[t].key < x) t = pool[t].r;
            else res &= pool[pool[t].r].andv & pool[t].key, t = pool[t].l;
        }
        touch(last);
        return res;
    }

    T andIn(T lo, T hi) {  // AND of the values in [lo, hi] (lo <= hi)
        int t = root;
        int last = 0;
        while (t && (pool[t].key < lo || hi < pool[t].key)) {  // down to the highest node inside [lo, hi]
            last = t;
            t = hi < pool[t].key ? pool[t].l : pool[t].r;
        }
        if (!t) {
            touch(last);
            return ~T(0);
        }
        T res = pool[t].key;
        int a = t, na = 0, b = t, nb = 0;
        for (int u = pool[t].l; u;) {  // its left side is <= hi: keep what is >= lo
            a = u, na++;
            if (lo <= pool[u].key) res &= pool[u].key & pool[pool[u].r].andv, u = pool[u].l;
            else u = pool[u].r;
        }
        for (int u = pool[t].r; u;) {  // its right side is >= lo: keep what is <= hi
            b = u, nb++;
            if (pool[u].key <= hi) res &= pool[u].key & pool[pool[u].l].andv, u = pool[u].r;
            else u = pool[u].l;
        }
        touch(na >= nb ? a : b);  // the end of the longer path pays for both
        return res;
    }

    // O(logN amortized) -- add one copy of x
    void add(T x) {
        addRaw(x, 1);
    }

    // O(logN amortized) -- add cnt copies of val (nothing if cnt <= 0)
    void addCount(T val, long long cnt) {
        if (cnt > 0) addRaw(val, cnt);
    }

    // O(1) -- bitwise AND of all values; -1 (every bit set) if empty
    T andOfAll() {
        return pool[root].andv;
    }

    // O(logN amortized) -- bitwise AND of the values > x; -1 (every bit set) if there are none
    T andOfGtX(T x) {
        if (x == numeric_limits<T>::max()) return ~T(0);
        return andGe(x + 1);
    }

    // O(logN amortized) -- bitwise AND of the values >= x; -1 (every bit set) if there are none
    T andOfGteX(T x) {
        return andGe(x);
    }

    // O(logN amortized) -- bitwise AND of the values v with lo <= v <= hi; -1 (every bit set) if there are none
    T andOfInValRange(T lo, T hi) {
        return lo <= hi ? andIn(lo, hi) : ~T(0);
    }

    // O(logN amortized) -- bitwise AND of the kFrom-th..kTo-th largest values (1-indexed, inclusive); throws out_of_range unless 1 <= kFrom <= kTo <= size
    T andOfKthLargestRange(long long kFrom, long long kTo) {
        if (kFrom < 1 || kFrom > kTo || kTo > n) throw out_of_range("andOfKthLargestRange: needs 1 <= kFrom <= kTo <= size");
        T a = kthAt(n - kTo + 1);
        return andIn(a, kthAt(n - kFrom + 1));
    }

    // O(logN amortized) -- bitwise AND of the kFrom-th..kTo-th smallest values (1-indexed, inclusive); throws out_of_range unless 1 <= kFrom <= kTo <= size
    T andOfKthSmallestRange(long long kFrom, long long kTo) {
        if (kFrom < 1 || kFrom > kTo || kTo > n) throw out_of_range("andOfKthSmallestRange: needs 1 <= kFrom <= kTo <= size");
        T a = kthAt(kFrom);
        return andIn(a, kthAt(kTo));
    }

    // O(logN amortized) -- bitwise AND of the k largest values (-1 (every bit set) for k = 0); throws out_of_range unless 0 <= k <= size
    T andOfLargestK(long long k) {
        if (k < 0 || k > n) throw out_of_range("andOfLargestK: needs 0 <= k <= size");
        return k ? andGe(kthAt(n - k + 1)) : ~T(0);
    }

    // O(logN amortized) -- bitwise AND of the values < x; -1 (every bit set) if there are none
    T andOfLtX(T x) {
        if (x == numeric_limits<T>::min()) return ~T(0);
        return andLe(x - 1);
    }

    // O(logN amortized) -- bitwise AND of the values <= x; -1 (every bit set) if there are none
    T andOfLteX(T x) {
        return andLe(x);
    }

    // O(logN amortized) -- bitwise AND of the k smallest values (-1 (every bit set) for k = 0); throws out_of_range unless 0 <= k <= size
    T andOfSmallestK(long long k) {
        if (k < 0 || k > n) throw out_of_range("andOfSmallestK: needs 0 <= k <= size");
        return k ? andLe(kthAt(k)) : ~T(0);
    }

    // O(N) -- remove everything: afterwards it is as if newly built (same constructor arguments), so reuse it instead of building a new one
    void clear() {
        clearData();
        resetCached();
    }

    // O(logN amortized) -- how many copies of x
    long long count(T x) {
        return countOf(x);
    }

    // O(1) -- how many distinct values
    long long countDistinct() {
        return d;
    }

    // O(logN amortized) -- how many distinct values v with lo <= v <= hi (0 if lo > hi)
    long long countDistinctInValRange(T lo, T hi) {
        if (hi < lo) return 0;
        return distinctLt(hi) - distinctLt(lo) + (countOf(hi) ? 1 : 0);
    }

    // O(logN amortized) -- how many values > x
    long long countGtX(T x) {
        return n - le(x);
    }

    // O(logN amortized) -- how many values >= x
    long long countGteX(T x) {
        return n - lt(x);
    }

    // O(logN amortized) -- how many values v with lo <= v <= hi (0 if lo > hi)
    long long countInValRange(T lo, T hi) {
        return lo <= hi ? le(hi) - lt(lo) : 0;
    }

    // O(logN amortized) -- how many values < x
    long long countLtX(T x) {
        return lt(x);
    }

    // O(logN amortized) -- how many values <= x
    long long countLteX(T x) {
        return le(x);
    }

    // O(logN amortized) -- 0-indexed position of the first copy of x in sorted order (= how many values < x); -1 if x is not in the set
    long long firstIndex(T x) {
        return countOf(x) ? lt(x) : -1;
    }

    // O(logN amortized) -- the value at sorted position i (0-indexed: kth(0) is the min); throws out_of_range unless 0 <= i < size
    T kth(long long i) {
        if (i < 0 || i >= n) throw out_of_range("kth: needs 0 <= i < size");
        return kthAt(i + 1);
    }

    // O(logN amortized) -- largest value < x; nullopt if there is none
    optional<T> largestLtX(T x) {
        long long c = lt(x);
        if (!c) return nullopt;
        return kthAt(c);
    }

    // O(logN amortized) -- largest value <= x; nullopt if there is none
    optional<T> largestLteX(T x) {
        long long c = le(x);
        if (!c) return nullopt;
        return kthAt(c);
    }

    // O(logN amortized) -- 0-indexed position of the last copy of x in sorted order (= how many values <= x, minus 1); -1 if x is not in the set
    long long lastIndex(T x) {
        return countOf(x) ? le(x) - 1 : -1;
    }

    // O(logN amortized) -- largest value; nullopt if empty
    optional<T> max() {
        if (!n) return nullopt;
        return kthAt(n);
    }

    // O(1 amortized) -- largest difference between two neighbouring distinct values; nullopt if fewer than 2 distinct values
    optional<long long> maxGap() {
        if (d < 2) return nullopt;
        return *gaps.rbegin();
    }

    // O(logN amortized) -- upper median: the (floor(size/2) + 1)-th smallest value; nullopt if empty
    optional<T> medianHigh() {
        if (!n) return nullopt;
        return kthAt(n / 2 + 1);
    }

    // O(logN amortized) -- lower median: the ceil(size/2)-th smallest value; nullopt if empty
    optional<T> medianLow() {
        if (!n) return nullopt;
        return kthAt((n + 1) / 2);
    }

    // O(1) -- smallest non-negative integer not in the set
    long long mex() {
        return mexV;
    }

    // O(logN amortized) -- smallest value; nullopt if empty
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

    // O(logN amortized) -- bitwise OR of the values > x; 0 if there are none
    T orOfGtX(T x) {
        if (x == numeric_limits<T>::max()) return T(0);
        return orGe(x + 1);
    }

    // O(logN amortized) -- bitwise OR of the values >= x; 0 if there are none
    T orOfGteX(T x) {
        return orGe(x);
    }

    // O(logN amortized) -- bitwise OR of the values v with lo <= v <= hi; 0 if there are none
    T orOfInValRange(T lo, T hi) {
        return lo <= hi ? orIn(lo, hi) : T(0);
    }

    // O(logN amortized) -- bitwise OR of the kFrom-th..kTo-th largest values (1-indexed, inclusive); throws out_of_range unless 1 <= kFrom <= kTo <= size
    T orOfKthLargestRange(long long kFrom, long long kTo) {
        if (kFrom < 1 || kFrom > kTo || kTo > n) throw out_of_range("orOfKthLargestRange: needs 1 <= kFrom <= kTo <= size");
        T a = kthAt(n - kTo + 1);
        return orIn(a, kthAt(n - kFrom + 1));
    }

    // O(logN amortized) -- bitwise OR of the kFrom-th..kTo-th smallest values (1-indexed, inclusive); throws out_of_range unless 1 <= kFrom <= kTo <= size
    T orOfKthSmallestRange(long long kFrom, long long kTo) {
        if (kFrom < 1 || kFrom > kTo || kTo > n) throw out_of_range("orOfKthSmallestRange: needs 1 <= kFrom <= kTo <= size");
        T a = kthAt(kFrom);
        return orIn(a, kthAt(kTo));
    }

    // O(logN amortized) -- bitwise OR of the k largest values (0 for k = 0); throws out_of_range unless 0 <= k <= size
    T orOfLargestK(long long k) {
        if (k < 0 || k > n) throw out_of_range("orOfLargestK: needs 0 <= k <= size");
        return k ? orGe(kthAt(n - k + 1)) : T(0);
    }

    // O(logN amortized) -- bitwise OR of the values < x; 0 if there are none
    T orOfLtX(T x) {
        if (x == numeric_limits<T>::min()) return T(0);
        return orLe(x - 1);
    }

    // O(logN amortized) -- bitwise OR of the values <= x; 0 if there are none
    T orOfLteX(T x) {
        return orLe(x);
    }

    // O(logN amortized) -- bitwise OR of the k smallest values (0 for k = 0); throws out_of_range unless 0 <= k <= size
    T orOfSmallestK(long long k) {
        if (k < 0 || k > n) throw out_of_range("orOfSmallestK: needs 0 <= k <= size");
        return k ? orLe(kthAt(k)) : T(0);
    }

    // O(logN amortized) -- remove and return the value at sorted position i (0-indexed: pop(0) is popMin()); throws out_of_range unless 0 <= i < size
    T pop(long long i) {
        if (i < 0 || i >= n) throw out_of_range("pop: needs 0 <= i < size");
        T v = kthAt(i + 1);
        addRaw(v, -1);
        return v;
    }

    // O(logN amortized) -- remove and return the largest value; nullopt if empty
    optional<T> popMax() {
        if (!n) return nullopt;
        T v = kthAt(n);
        addRaw(v, -1);
        return v;
    }

    // O(logN amortized) -- remove and return the smallest value; nullopt if empty
    optional<T> popMin() {
        if (!n) return nullopt;
        T v = kthAt(1);
        addRaw(v, -1);
        return v;
    }

    // O(logN amortized) -- remove one copy of x if present; returns how many were removed (0 or 1)
    long long remove(T x) {
        if (!count(x)) return 0;
        addRaw(x, -1);
        return 1;
    }

    // O(logN amortized) -- remove every copy of val; returns how many were removed
    long long removeAll(T val) {
        long long k = count(val);
        if (k) addRaw(val, -k);
        return k;
    }

    // O(logN amortized) -- remove min(cnt, count(val)) copies of val; returns how many were removed
    long long removeCount(T val, long long cnt) {
        long long k = std::min(cnt, count(val));
        if (k <= 0) return 0;
        addRaw(val, -k);
        return k;
    }

    // O(logN amortized) -- remove every value v with lo <= v <= hi; returns how many copies were removed (0 if lo > hi)
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

    // O(logN amortized) -- smallest value > x; nullopt if there is none
    optional<T> smallestGtX(T x) {
        long long c = le(x);
        if (c == n) return nullopt;
        return kthAt(c + 1);
    }

    // O(logN amortized) -- smallest value >= x; nullopt if there is none
    optional<T> smallestGteX(T x) {
        long long c = lt(x);
        if (c == n) return nullopt;
        return kthAt(c + 1);
    }
};
