// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/sets/splay-with-sums-or-and-minmax-gaps/template.cpp
// @operations: add addCount andOfAll andOfGtX andOfGteX andOfInValRange andOfKthLargestRange andOfKthSmallestRange andOfLargestK andOfLtX andOfLteX andOfSmallestK clear count countDistinct countGtX countGteX countInValRange countLtX countLteX firstIndex kth largestLtX largestLteX lastIndex max maxGap medianHigh medianLow min minAdjacentDiff orOfAll orOfGtX orOfGteX orOfInValRange orOfKthLargestRange orOfKthSmallestRange orOfLargestK orOfLtX orOfLteX orOfSmallestK pop popMax popMin remove removeAll removeCount removeInValRange size smallestGtX smallestGteX sumAbsDiffToMedian sumAbsDiffToX sumAll sumGtX sumGteX sumInValRange sumKthLargestRange sumKthSmallestRange sumLargestK sumLtX sumLteX sumSmallestK
// @data-structure-type: splay
// @values: online
// @keys: numbers
// @tracks: minmax gaps
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
//   max: 1
//   maxGap: 1 amortized
//   medianHigh: log(N) amortized
//   medianLow: log(N) amortized
//   min: 1
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
//   sumAbsDiffToMedian: log(N) amortized
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
//   build: 1
// @memory:
//   layout: none
//   node: key[1*N] cnt[1*N] size[1*N] sum[1*N] or[1*N] and[1*N]
//   tags: none
//   other: children[2*N] parent[1*N]
//   note: N = most distinct values present at once (removed nodes are reused). C++: one shared node pool, call resetPool() between test cases; Python: parallel lists per tree

// Ordered multiset (online: any values, nothing known ahead): a splay tree with one node per distinct value. Each node
// keeps its value, its copies, and the copies, sum, OR, AND in its subtree; every operation splays the
// last node it touched to the root, which makes each one O(log N) amortized. Nodes live in one pool shared by every
// SplayMultiset<T> (call resetPool() between test cases); node 0 is the empty tree and removed nodes are reused.
// T: an integer type; sums in S (long long for small T).
template <typename T>
struct SplayMultiset {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    struct Node { T key; long long c, z; S s; T orv; T andv = ~T(0); int l, r, p; };  // copies; copies, sum below; parent
    static inline vector<Node> pool{Node{}};
    static inline vector<int> freeList;
    int root = 0;
    long long n = 0, d = 0;
    struct Info { T v; long long before, c; S sb; };  // a value, copies before it, its copies, sum before it
    T mn{}, mx{};  // kept current by addRaw while n > 0
    multiset<long long> gaps;  // differences between neighbouring distinct values
    long long dups = 0;  // values with 2+ copies
    S total = 0;

    // O(1) -- an empty multiset
    SplayMultiset() {}

    // O(1) -- forget every node of every SplayMultiset<T>; call between test cases, then build new ones
    static void resetPool() { pool.resize(1), freeList.clear(); }

    // optional -- reserve room for this many nodes up front
    static void reservePool(size_t nodes) { pool.reserve(nodes); }

    static int make(T x, int parent) {
        int t;
        if (!freeList.empty()) t = freeList.back(), freeList.pop_back();
        else pool.push_back(Node{}), t = (int)pool.size() - 1;
        pool[t] = Node{};
        pool[t].key = x, pool[t].p = parent;
        return t;
    }

    static void pull(int t) {
        Node& v = pool[t];
        const Node &a = pool[v.l], &b = pool[v.r];
        v.z = a.z + b.z + v.c;
        v.orv = a.orv | b.orv | v.key;
        v.andv = a.andv & b.andv & v.key;
        v.s = a.s + b.s + S(v.c) * v.key;
    }

    static void rotate(int x) {  // x moves above its parent
        int p = pool[x].p, g = pool[p].p, b;
        if (pool[p].l == x) b = pool[x].r, pool[p].l = b, pool[x].r = p;
        else b = pool[x].l, pool[p].r = b, pool[x].l = p;
        if (b) pool[b].p = p;
        pool[p].p = x, pool[x].p = g;
        if (g) (pool[g].l == p ? pool[g].l : pool[g].r) = x;
        pull(p), pull(x);
    }

    static int splay(int x) {  // x becomes the root of its tree
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

    S slt(T x) {  // sum of the values < x
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

    S sle(T x) {  // sum of the values <= x
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
    Info kthInfo(long long k) {  // the k-th smallest, copies before it, its copies, sum before it
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

    void addRaw(T x, long long c) {  // c copies of x (c < 0 removes); keeps min / max current
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
        gaps.clear(), dups = 0;
        n = d = 0;
        total = 0;
    }

    void clearData() {  // hand this tree's nodes back to the shared pool's free list
        vector<int> st;
        if (root) st.push_back(root);
        while (!st.empty()) {
            int t = st.back();
            st.pop_back();
            if (pool[t].l) st.push_back(pool[t].l);
            if (pool[t].r) st.push_back(pool[t].r);
            freeList.push_back(t);
        }
        root = 0;
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

    // O(1) -- largest value; nullopt if empty
    optional<T> max() {
        if (!n) return nullopt;
        return mx;
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

    // O(1) -- smallest value; nullopt if empty
    optional<T> min() {
        if (!n) return nullopt;
        return mn;
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
        T v = mx;
        addRaw(v, -1);
        return v;
    }

    // O(logN amortized) -- remove and return the smallest value; nullopt if empty
    optional<T> popMin() {
        if (!n) return nullopt;
        T v = mn;
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

    // O(logN amortized) -- sum of |v - medianLow()| over all values (min total moves to make all equal); 0 if empty
    S sumAbsDiffToMedian() {
        if (!n) return 0;
        Info m = kthInfo((n + 1) / 2);
        return S(m.v) * m.before - m.sb + (total - m.sb - S(m.v) * m.c) - S(m.v) * (n - m.before - m.c);
    }

    // O(logN amortized) -- sum of |v - x| over all values
    S sumAbsDiffToX(T x) {
        long long c = lt(x);
        S s = slt(x);
        return S(x) * c - s + (total - s) - S(x) * (n - c);
    }

    // O(1) -- sum of all values
    S sumAll() {
        return total;
    }

    // O(logN amortized) -- sum of the values > x
    S sumGtX(T x) {
        return total - sle(x);
    }

    // O(logN amortized) -- sum of the values >= x
    S sumGteX(T x) {
        return total - slt(x);
    }

    // O(logN amortized) -- sum of the values v with lo <= v <= hi (0 if lo > hi)
    S sumInValRange(T lo, T hi) {
        return lo <= hi ? sle(hi) - slt(lo) : S(0);
    }

    // O(logN amortized) -- sum of the kFrom-th..kTo-th largest values (1-indexed, inclusive; (5, 8) = 5th..8th biggest); throws out_of_range unless 1 <= kFrom <= kTo <= size
    S sumKthLargestRange(long long kFrom, long long kTo) {
        if (kFrom < 1 || kFrom > kTo || kTo > n) throw out_of_range("sumKthLargestRange: needs 1 <= kFrom <= kTo <= size");
        return sumFirst(n - kFrom + 1) - sumFirst(n - kTo);
    }

    // O(logN amortized) -- sum of the kFrom-th..kTo-th smallest values (1-indexed, inclusive); throws out_of_range unless 1 <= kFrom <= kTo <= size
    S sumKthSmallestRange(long long kFrom, long long kTo) {
        if (kFrom < 1 || kFrom > kTo || kTo > n) throw out_of_range("sumKthSmallestRange: needs 1 <= kFrom <= kTo <= size");
        return sumFirst(kTo) - sumFirst(kFrom - 1);
    }

    // O(logN amortized) -- sum of the k largest values; throws out_of_range unless 0 <= k <= size
    S sumLargestK(long long k) {
        if (k < 0 || k > n) throw out_of_range("sumLargestK: needs 0 <= k <= size");
        return total - sumFirst(n - k);
    }

    // O(logN amortized) -- sum of the values < x
    S sumLtX(T x) {
        return slt(x);
    }

    // O(logN amortized) -- sum of the values <= x
    S sumLteX(T x) {
        return sle(x);
    }

    // O(logN amortized) -- sum of the k smallest values; throws out_of_range unless 0 <= k <= size
    S sumSmallestK(long long k) {
        if (k < 0 || k > n) throw out_of_range("sumSmallestK: needs 0 <= k <= size");
        return sumFirst(k);
    }
};
