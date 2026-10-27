// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/sets/splay-with-sums-cachedmex-mode-gaps-shift/template.cpp
// @operations: add addCount clear count countDistinct countDistinctInValRange countGtX countGteX countInValRange countLtX countLteX firstIndex kth largestLtX largestLteX lastIndex max maxGap medianHigh medianLow mex min minAdjacentDiff mode pop popMax popMin remove removeAll removeCount removeInValRange shiftAll size smallestGtX smallestGteX sumAbsDiffToMedian sumAbsDiffToX sumAll sumGtX sumGteX sumInValRange sumKthLargestRange sumKthSmallestRange sumLargestK sumLtX sumLteX sumSmallestK
// @data-structure-type: splay
// @values: online
// @keys: numbers
// @tracks: mex mode gaps shift
// @complexities:
//   add: log(N) amortized
//   addCount: log(N) amortized
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
//   mode: 1
//   pop: log(N) amortized
//   popMax: log(N) amortized
//   popMin: log(N) amortized
//   remove: log(N) amortized
//   removeAll: log(N) amortized
//   removeCount: log(N) amortized
//   removeInValRange: log(N) amortized
//   shiftAll: log(N) amortized
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
//   node: key[1*N] cnt[1*N] size[1*N] dn[1*N] sum[1*N]
//   tags: none
//   other: children[2*N] parent[1*N]
//   note: N = most distinct values present at once (removed nodes are reused). C++: one shared node pool, call resetPool() between test cases; Python: parallel lists per tree

// Ordered multiset (online: any values, nothing known ahead): a splay tree with one node per distinct value. Each node
// keeps its value, its copies, and the copies, sum and distinct values in its subtree; every operation splays the
// last node it touched to the root, which makes each one O(log N) amortized. Nodes live in one pool shared by every
// SplayMultiset<T> (call resetPool() between test cases); node 0 is the empty tree and removed nodes are reused.
// T: an integer type; sums in S (long long for small T).
template <typename T>
struct SplayMultiset {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    struct Node { T key; long long c, z; S s; long long dn; int l, r, p; };  // copies; copies, sum, distinct below; parent
    static inline vector<Node> pool{Node{}};
    static inline vector<int> freeList;
    int root = 0;
    long long n = 0, d = 0;
    struct Info { T v; long long before, c; S sb; };  // a value, copies before it, its copies, sum before it
    long long mexV = 0;  // the mex, kept current (0 for the empty set)
    map<long long, set<T>> bk;  // mode: count -> the values with that many copies
    multiset<long long> gaps;  // differences between neighbouring distinct values
    long long dups = 0;  // values with 2+ copies
    T off = 0;  // every value v is stored as v - off: shiftAll only moves off
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
        v.dn = a.dn + b.dn + 1;
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
        T base = -off;  // (stored as v - off: the real values >= 0 are the stored ones >= -off)
        long long c0 = distinctLt(base), before = -c0, res = d - c0;  // before: distinct values >= 0 left of t's subtree
        int t = root, last = 0;
        while (t) {
            last = t;
            long long j = before + pool[pool[t].l].dn;
            if (pool[t].key < base || pool[t].key == T(base + j)) before = j + 1, t = pool[t].r;
            else res = j, t = pool[t].l;
        }
        touch(last);
        return base + res;  // (a stored value)
    }

    void addRaw(T x, long long c) {  // c copies of x (c < 0 removes); keeps the mex current
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
        {  // gaps
            if ((g >= 2) != (f >= 2)) dups += f >= 2 ? 1 : -1;  // values with 2+ copies (then the smallest difference is 0)
            if (!g || !f) {  // x appeared or disappeared: the gap between its neighbours splits or comes back
                long long cl = lt(x), ce = le(x);  // (stored values: the public ops would shift x again)
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
            if constexpr (is_integral_v<T>) if (x == T(mexV)) mexV = findMex();  // x filled the mex
        } else {
            if constexpr (is_integral_v<T>) if (x >= -off && x < T(mexV) && !f) mexV = x;  // the last copy of a value below the mex
        }
    }

    S sumFirst(long long k) {  // sum of the k smallest values
        if (k <= 0) return 0;
        Info f = kthInfo(k);
        return f.sb + S(k - f.before) * f.v;
    }

    void resetCached() {  // nothing counted: as newly built
        mexV = 0;
        bk.clear();
        gaps.clear(), dups = 0;
        n = d = 0;
        total = 0;
        off = 0;
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

    // O(logN amortized) -- add one copy of x
    void add(T x) {
        x -= off;
        addRaw(x, 1);
    }

    // O(logN amortized) -- add cnt copies of val (nothing if cnt <= 0)
    void addCount(T val, long long cnt) {
        val -= off;
        if (cnt > 0) addRaw(val, cnt);
    }

    // O(N) -- remove everything: afterwards it is as if newly built (same constructor arguments), so reuse it instead of building a new one
    void clear() {
        clearData();
        resetCached();
    }

    // O(logN amortized) -- how many copies of x
    long long count(T x) {
        x -= off;
        return countOf(x);
    }

    // O(1) -- how many distinct values
    long long countDistinct() {
        return d;
    }

    // O(logN amortized) -- how many distinct values v with lo <= v <= hi (0 if lo > hi)
    long long countDistinctInValRange(T lo, T hi) {
        lo -= off, hi -= off;
        if (hi < lo) return 0;
        return distinctLt(hi) - distinctLt(lo) + (countOf(hi) ? 1 : 0);
    }

    // O(logN amortized) -- how many values > x
    long long countGtX(T x) {
        x -= off;
        return n - le(x);
    }

    // O(logN amortized) -- how many values >= x
    long long countGteX(T x) {
        x -= off;
        return n - lt(x);
    }

    // O(logN amortized) -- how many values v with lo <= v <= hi (0 if lo > hi)
    long long countInValRange(T lo, T hi) {
        lo -= off, hi -= off;
        return lo <= hi ? le(hi) - lt(lo) : 0;
    }

    // O(logN amortized) -- how many values < x
    long long countLtX(T x) {
        x -= off;
        return lt(x);
    }

    // O(logN amortized) -- how many values <= x
    long long countLteX(T x) {
        x -= off;
        return le(x);
    }

    // O(logN amortized) -- 0-indexed position of the first copy of x in sorted order (= how many values < x); -1 if x is not in the set
    long long firstIndex(T x) {
        x -= off;
        return countOf(x) ? lt(x) : -1;
    }

    // O(logN amortized) -- the value at sorted position i (0-indexed: kth(0) is the min); throws out_of_range unless 0 <= i < size
    T kth(long long i) {
        if (i < 0 || i >= n) throw out_of_range("kth: needs 0 <= i < size");
        return T(kthAt(i + 1) + off);
    }

    // O(logN amortized) -- largest value < x; nullopt if there is none
    optional<T> largestLtX(T x) {
        x -= off;
        long long c = lt(x);
        if (!c) return nullopt;
        return T(kthAt(c) + off);
    }

    // O(logN amortized) -- largest value <= x; nullopt if there is none
    optional<T> largestLteX(T x) {
        x -= off;
        long long c = le(x);
        if (!c) return nullopt;
        return T(kthAt(c) + off);
    }

    // O(logN amortized) -- 0-indexed position of the last copy of x in sorted order (= how many values <= x, minus 1); -1 if x is not in the set
    long long lastIndex(T x) {
        x -= off;
        return countOf(x) ? le(x) - 1 : -1;
    }

    // O(logN amortized) -- largest value; nullopt if empty
    optional<T> max() {
        if (!n) return nullopt;
        return T(kthAt(n) + off);
    }

    // O(1 amortized) -- largest difference between two neighbouring distinct values; nullopt if fewer than 2 distinct values
    optional<long long> maxGap() {
        if (d < 2) return nullopt;
        return *gaps.rbegin();
    }

    // O(logN amortized) -- upper median: the (floor(size/2) + 1)-th smallest value; nullopt if empty
    optional<T> medianHigh() {
        if (!n) return nullopt;
        return T(kthAt(n / 2 + 1) + off);
    }

    // O(logN amortized) -- lower median: the ceil(size/2)-th smallest value; nullopt if empty
    optional<T> medianLow() {
        if (!n) return nullopt;
        return T(kthAt((n + 1) / 2) + off);
    }

    // O(1) -- smallest non-negative integer not in the set
    long long mex() {
        return mexV + off;
    }

    // O(logN amortized) -- smallest value; nullopt if empty
    optional<T> min() {
        if (!n) return nullopt;
        return T(kthAt(1) + off);
    }

    // O(1 amortized) -- smallest difference between two values in the set (0 if some value has 2+ copies); nullopt if fewer than 2 values
    optional<long long> minAdjacentDiff() {
        if (n < 2) return nullopt;
        if (dups) return 0LL;
        return *gaps.begin();
    }

    // O(1) -- (a most frequent value, its count); nullopt if empty. C++ returns the smallest of the most frequent values
    optional<pair<T, long long>> mode() {
        if (!n) return nullopt;
        auto& [f, vs] = *bk.rbegin();
        return pair<T, long long>{T(*vs.begin() + off), f};
    }

    // O(logN amortized) -- remove and return the value at sorted position i (0-indexed: pop(0) is popMin()); throws out_of_range unless 0 <= i < size
    T pop(long long i) {
        if (i < 0 || i >= n) throw out_of_range("pop: needs 0 <= i < size");
        T v = kthAt(i + 1);
        addRaw(v, -1);
        return T(v + off);
    }

    // O(logN amortized) -- remove and return the largest value; nullopt if empty
    optional<T> popMax() {
        if (!n) return nullopt;
        T v = kthAt(n);
        addRaw(v, -1);
        return T(v + off);
    }

    // O(logN amortized) -- remove and return the smallest value; nullopt if empty
    optional<T> popMin() {
        if (!n) return nullopt;
        T v = kthAt(1);
        addRaw(v, -1);
        return T(v + off);
    }

    // O(logN amortized) -- remove one copy of x if present; returns how many were removed (0 or 1)
    long long remove(T x) {
        x -= off;
        if (!countOf(x)) return 0;
        addRaw(x, -1);
        return 1;
    }

    // O(logN amortized) -- remove every copy of val; returns how many were removed
    long long removeAll(T val) {
        val -= off;
        long long k = countOf(val);
        if (k) addRaw(val, -k);
        return k;
    }

    // O(logN amortized) -- remove min(cnt, count(val)) copies of val; returns how many were removed
    long long removeCount(T val, long long cnt) {
        val -= off;
        long long k = std::min(cnt, countOf(val));
        if (k <= 0) return 0;
        addRaw(val, -k);
        return k;
    }

    // O(logN amortized) -- remove every value v with lo <= v <= hi; returns how many copies were removed (0 if lo > hi)
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

    // O(logN amortized) -- add d to every value (d may be negative)
    void shiftAll(T d) {
        off += d;
        mexV = findMex();  // (the mex of the shifted values)
    }

    // O(1) -- how many values (copies count)
    long long size() {
        return n;
    }

    // O(logN amortized) -- smallest value > x; nullopt if there is none
    optional<T> smallestGtX(T x) {
        x -= off;
        long long c = le(x);
        if (c == n) return nullopt;
        return T(kthAt(c + 1) + off);
    }

    // O(logN amortized) -- smallest value >= x; nullopt if there is none
    optional<T> smallestGteX(T x) {
        x -= off;
        long long c = lt(x);
        if (c == n) return nullopt;
        return T(kthAt(c + 1) + off);
    }

    // O(logN amortized) -- sum of |v - medianLow()| over all values (min total moves to make all equal); 0 if empty
    S sumAbsDiffToMedian() {
        if (!n) return 0;
        Info m = kthInfo((n + 1) / 2);
        return S(m.v) * m.before - m.sb + (total - m.sb - S(m.v) * m.c) - S(m.v) * (n - m.before - m.c);
    }

    // O(logN amortized) -- sum of |v - x| over all values
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

    // O(logN amortized) -- sum of the values > x
    S sumGtX(T x) {
        x -= off;
        return total - sle(x) + S(off) * (n - le(x));
    }

    // O(logN amortized) -- sum of the values >= x
    S sumGteX(T x) {
        x -= off;
        return total - slt(x) + S(off) * (n - lt(x));
    }

    // O(logN amortized) -- sum of the values v with lo <= v <= hi (0 if lo > hi)
    S sumInValRange(T lo, T hi) {
        if (hi < lo) return 0;
        lo -= off, hi -= off;
        return sle(hi) - slt(lo) + S(off) * (le(hi) - lt(lo));
    }

    // O(logN amortized) -- sum of the kFrom-th..kTo-th largest values (1-indexed, inclusive; (5, 8) = 5th..8th biggest); throws out_of_range unless 1 <= kFrom <= kTo <= size
    S sumKthLargestRange(long long kFrom, long long kTo) {
        if (kFrom < 1 || kFrom > kTo || kTo > n) throw out_of_range("sumKthLargestRange: needs 1 <= kFrom <= kTo <= size");
        return sumFirst(n - kFrom + 1) - sumFirst(n - kTo) + S(off) * (kTo - kFrom + 1);
    }

    // O(logN amortized) -- sum of the kFrom-th..kTo-th smallest values (1-indexed, inclusive); throws out_of_range unless 1 <= kFrom <= kTo <= size
    S sumKthSmallestRange(long long kFrom, long long kTo) {
        if (kFrom < 1 || kFrom > kTo || kTo > n) throw out_of_range("sumKthSmallestRange: needs 1 <= kFrom <= kTo <= size");
        return sumFirst(kTo) - sumFirst(kFrom - 1) + S(off) * (kTo - kFrom + 1);
    }

    // O(logN amortized) -- sum of the k largest values; throws out_of_range unless 0 <= k <= size
    S sumLargestK(long long k) {
        if (k < 0 || k > n) throw out_of_range("sumLargestK: needs 0 <= k <= size");
        return total - sumFirst(n - k) + S(off) * k;
    }

    // O(logN amortized) -- sum of the values < x
    S sumLtX(T x) {
        x -= off;
        return slt(x) + S(off) * lt(x);
    }

    // O(logN amortized) -- sum of the values <= x
    S sumLteX(T x) {
        x -= off;
        return sle(x) + S(off) * le(x);
    }

    // O(logN amortized) -- sum of the k smallest values; throws out_of_range unless 0 <= k <= size
    S sumSmallestK(long long k) {
        if (k < 0 || k > n) throw out_of_range("sumSmallestK: needs 0 <= k <= size");
        return sumFirst(k) + S(off) * k;
    }
};
