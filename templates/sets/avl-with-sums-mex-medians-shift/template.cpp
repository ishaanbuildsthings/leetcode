// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/sets/avl-with-sums-mex-medians-shift/template.cpp
// @operations: add addCount clear count countDistinct countDistinctInValRange countGtX countGteX countInValRange countLtX countLteX firstIndex kth largestLtX largestLteX lastIndex max medianHigh medianLow mex min pop popMax popMin remove removeAll removeCount removeInValRange shiftAll size smallestGtX smallestGteX sumAbsDiffToMedian sumAbsDiffToX sumAll sumGtX sumGteX sumInValRange sumKthLargestRange sumKthSmallestRange sumLargestK sumLtX sumLteX sumSmallestK
// @data-structure-type: avl
// @values: online
// @keys: numbers
// @tracks: medians shift
// @complexities:
//   add: log(N)
//   addCount: log(N)
//   clear: N
//   count: log(N)
//   countDistinct: 1
//   countDistinctInValRange: log(N)
//   countGtX: log(N)
//   countGteX: log(N)
//   countInValRange: log(N)
//   countLtX: log(N)
//   countLteX: log(N)
//   firstIndex: log(N)
//   kth: log(N)
//   largestLtX: log(N)
//   largestLteX: log(N)
//   lastIndex: log(N)
//   max: log(N)
//   medianHigh: 1
//   medianLow: 1
//   mex: log(N)
//   min: log(N)
//   pop: log(N)
//   popMax: log(N)
//   popMin: log(N)
//   remove: log(N)
//   removeAll: log(N)
//   removeCount: log(N)
//   removeInValRange: log(N) amortized
//   shiftAll: 1
//   size: 1
//   smallestGtX: log(N)
//   smallestGteX: log(N)
//   sumAbsDiffToMedian: 1
//   sumAbsDiffToX: log(N)
//   sumAll: 1
//   sumGtX: log(N)
//   sumGteX: log(N)
//   sumInValRange: log(N)
//   sumKthLargestRange: log(N)
//   sumKthSmallestRange: log(N)
//   sumLargestK: log(N)
//   sumLtX: log(N)
//   sumLteX: log(N)
//   sumSmallestK: log(N)
//   build: 1
// @memory:
//   layout: none
//   node: key[1*N] cnt[1*N] size[1*N] dn[1*N] sum[1*N]
//   tags: none
//   other: children[2*N] height[1*N]
//   note: N = most distinct values present at once (removed nodes are reused). C++: one shared node pool, call resetPool() between test cases; Python: parallel lists per tree

// Ordered multiset (online: any values, nothing known ahead): an AVL tree with one node per distinct value, so every
// operation is O(log N) worst case (height <= 1.44 log2 N). Each node keeps its value, its copies, and the copies, sum
// and distinct values in its subtree. Nodes live in one pool shared by every AVLMultiset<T> (call resetPool() between
// test cases); node 0 is the empty tree and removed nodes are reused. T: an integer type; sums in S.
template <typename T>
struct AVLMultiset {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    struct Node { T key; long long c, z; S s; long long dn; int h, l, r; };  // copies; copies, sum, distinct below; height
    static inline vector<Node> pool{Node{}};
    static inline vector<int> freeList;
    int root = 0;
    long long n = 0, d = 0;
    struct Info { T v; long long before, c; S sb; };  // a value, copies before it, its copies, sum before it
    Info low{}, high{};  // both medians, kept current by addRaw while n > 0
    T off = 0;  // every value v is stored as v - off: shiftAll only moves off
    S total = 0;

    // O(1) -- an empty multiset
    AVLMultiset() {}

    // O(1) -- forget every node of every AVLMultiset<T>; call between test cases, then build new ones
    static void resetPool() { pool.resize(1), freeList.clear(); }

    // optional -- reserve room for this many nodes up front
    static void reservePool(size_t nodes) { pool.reserve(nodes); }

    static int make(T x, long long c) {
        int t;
        if (!freeList.empty()) t = freeList.back(), freeList.pop_back();
        else pool.push_back(Node{}), t = (int)pool.size() - 1;
        pool[t] = Node{};
        pool[t].key = x, pool[t].c = c;
        pull(t);
        return t;
    }

    static void pull(int t) {
        Node& v = pool[t];
        const Node &a = pool[v.l], &b = pool[v.r];
        v.z = a.z + b.z + v.c, v.h = std::max(a.h, b.h) + 1;
        v.dn = a.dn + b.dn + 1;
        v.s = a.s + b.s + S(v.c) * v.key;
    }

    static int rotR(int t) {  // t's left child moves up
        int l = pool[t].l;
        pool[t].l = pool[l].r, pool[l].r = t;
        pull(t), pull(l);
        return l;
    }

    static int rotL(int t) {  // t's right child moves up
        int r = pool[t].r;
        pool[t].r = pool[r].l, pool[r].l = t;
        pull(t), pull(r);
        return r;
    }

    static int bal(int t) {  // pull t and restore |height(left) - height(right)| <= 1; returns the subtree's new root
        pull(t);
        int b = pool[pool[t].l].h - pool[pool[t].r].h;
        if (b > 1) {
            int l = pool[t].l;
            if (pool[pool[l].l].h < pool[pool[l].r].h) pool[t].l = rotL(l);
            return rotR(t);
        }
        if (b < -1) {
            int r = pool[t].r;
            if (pool[pool[r].r].h < pool[pool[r].l].h) pool[t].r = rotR(r);
            return rotL(t);
        }
        return t;
    }

    static int popMin(int t, int& m) {  // t without its smallest node, which goes to m
        if (!pool[t].l) {
            m = t;
            return pool[t].r;
        }
        int l = popMin(pool[t].l, m);
        pool[t].l = l;
        return bal(t);
    }

    int ins(int t, T x, long long c) {  // c copies of x into subtree t; returns its new root
        if (!t) {
            d++;
            return make(x, c);
        }
        if (x < pool[t].key) {
            int l = ins(pool[t].l, x, c);
            pool[t].l = l;
        } else if (pool[t].key < x) {
            int r = ins(pool[t].r, x, c);
            pool[t].r = r;
        } else if (!(pool[t].c += c)) {  // x is gone: replace its node by the smallest node on its right
            d--, freeList.push_back(t);
            int l = pool[t].l, r = pool[t].r, m;
            if (!l || !r) return l ? l : r;
            r = popMin(r, m);
            pool[m].l = l, pool[m].r = r;
            return bal(m);
        }
        return bal(t);
    }

    void insert(T x, long long c) { root = ins(root, x, c); }

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

    void addRaw(T x, long long c) {  // c copies of x (c < 0 removes); keeps both medians current
        n += c;
        total += S(c) * x;
        insert(x, c);
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

    S sumFirst(long long k) {  // sum of the k smallest values
        if (k <= 0) return 0;
        Info f = kthInfo(k);
        return f.sb + S(k - f.before) * f.v;
    }

    void resetCached() {  // nothing counted: as newly built
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

    // O(logN) -- add one copy of x
    void add(T x) {
        x -= off;
        addRaw(x, 1);
    }

    // O(logN) -- add cnt copies of val (nothing if cnt <= 0)
    void addCount(T val, long long cnt) {
        val -= off;
        if (cnt > 0) addRaw(val, cnt);
    }

    // O(N) -- remove everything: afterwards it is as if newly built (same constructor arguments), so reuse it instead of building a new one
    void clear() {
        clearData();
        resetCached();
    }

    // O(logN) -- how many copies of x
    long long count(T x) {
        x -= off;
        return countOf(x);
    }

    // O(1) -- how many distinct values
    long long countDistinct() {
        return d;
    }

    // O(logN) -- how many distinct values v with lo <= v <= hi (0 if lo > hi)
    long long countDistinctInValRange(T lo, T hi) {
        lo -= off, hi -= off;
        if (hi < lo) return 0;
        return distinctLt(hi) - distinctLt(lo) + (countOf(hi) ? 1 : 0);
    }

    // O(logN) -- how many values > x
    long long countGtX(T x) {
        x -= off;
        return n - le(x);
    }

    // O(logN) -- how many values >= x
    long long countGteX(T x) {
        x -= off;
        return n - lt(x);
    }

    // O(logN) -- how many values v with lo <= v <= hi (0 if lo > hi)
    long long countInValRange(T lo, T hi) {
        lo -= off, hi -= off;
        return lo <= hi ? le(hi) - lt(lo) : 0;
    }

    // O(logN) -- how many values < x
    long long countLtX(T x) {
        x -= off;
        return lt(x);
    }

    // O(logN) -- how many values <= x
    long long countLteX(T x) {
        x -= off;
        return le(x);
    }

    // O(logN) -- 0-indexed position of the first copy of x in sorted order (= how many values < x); -1 if x is not in the set
    long long firstIndex(T x) {
        x -= off;
        return countOf(x) ? lt(x) : -1;
    }

    // O(logN) -- the value at sorted position i (0-indexed: kth(0) is the min); throws out_of_range unless 0 <= i < size
    T kth(long long i) {
        if (i < 0 || i >= n) throw out_of_range("kth: needs 0 <= i < size");
        return T(kthAt(i + 1) + off);
    }

    // O(logN) -- largest value < x; nullopt if there is none
    optional<T> largestLtX(T x) {
        x -= off;
        long long c = lt(x);
        if (!c) return nullopt;
        return T(kthAt(c) + off);
    }

    // O(logN) -- largest value <= x; nullopt if there is none
    optional<T> largestLteX(T x) {
        x -= off;
        long long c = le(x);
        if (!c) return nullopt;
        return T(kthAt(c) + off);
    }

    // O(logN) -- 0-indexed position of the last copy of x in sorted order (= how many values <= x, minus 1); -1 if x is not in the set
    long long lastIndex(T x) {
        x -= off;
        return countOf(x) ? le(x) - 1 : -1;
    }

    // O(logN) -- largest value; nullopt if empty
    optional<T> max() {
        if (!n) return nullopt;
        return T(kthAt(n) + off);
    }

    // O(1) -- upper median: the (floor(size/2) + 1)-th smallest value; nullopt if empty
    optional<T> medianHigh() {
        if (!n) return nullopt;
        return T(high.v + off);
    }

    // O(1) -- lower median: the ceil(size/2)-th smallest value; nullopt if empty
    optional<T> medianLow() {
        if (!n) return nullopt;
        return T(low.v + off);
    }

    // O(logN) -- smallest non-negative integer not in the set
    long long mex() {
        return findMex() + off;
    }

    // O(logN) -- smallest value; nullopt if empty
    optional<T> min() {
        if (!n) return nullopt;
        return T(kthAt(1) + off);
    }

    // O(logN) -- remove and return the value at sorted position i (0-indexed: pop(0) is popMin()); throws out_of_range unless 0 <= i < size
    T pop(long long i) {
        if (i < 0 || i >= n) throw out_of_range("pop: needs 0 <= i < size");
        T v = kthAt(i + 1);
        addRaw(v, -1);
        return T(v + off);
    }

    // O(logN) -- remove and return the largest value; nullopt if empty
    optional<T> popMax() {
        if (!n) return nullopt;
        T v = kthAt(n);
        addRaw(v, -1);
        return T(v + off);
    }

    // O(logN) -- remove and return the smallest value; nullopt if empty
    optional<T> popMin() {
        if (!n) return nullopt;
        T v = kthAt(1);
        addRaw(v, -1);
        return T(v + off);
    }

    // O(logN) -- remove one copy of x if present; returns how many were removed (0 or 1)
    long long remove(T x) {
        x -= off;
        if (!countOf(x)) return 0;
        addRaw(x, -1);
        return 1;
    }

    // O(logN) -- remove every copy of val; returns how many were removed
    long long removeAll(T val) {
        val -= off;
        long long k = countOf(val);
        if (k) addRaw(val, -k);
        return k;
    }

    // O(logN) -- remove min(cnt, count(val)) copies of val; returns how many were removed
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

    // O(1) -- add d to every value (d may be negative)
    void shiftAll(T d) {
        off += d;
    }

    // O(1) -- how many values (copies count)
    long long size() {
        return n;
    }

    // O(logN) -- smallest value > x; nullopt if there is none
    optional<T> smallestGtX(T x) {
        x -= off;
        long long c = le(x);
        if (c == n) return nullopt;
        return T(kthAt(c + 1) + off);
    }

    // O(logN) -- smallest value >= x; nullopt if there is none
    optional<T> smallestGteX(T x) {
        x -= off;
        long long c = lt(x);
        if (c == n) return nullopt;
        return T(kthAt(c + 1) + off);
    }

    // O(1) -- sum of |v - medianLow()| over all values (min total moves to make all equal); 0 if empty
    S sumAbsDiffToMedian() {
        if (!n) return 0;
        const Info& m = low;
        return S(m.v) * m.before - m.sb + (total - m.sb - S(m.v) * m.c) - S(m.v) * (n - m.before - m.c);
    }

    // O(logN) -- sum of |v - x| over all values
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

    // O(logN) -- sum of the values > x
    S sumGtX(T x) {
        x -= off;
        return total - sle(x) + S(off) * (n - le(x));
    }

    // O(logN) -- sum of the values >= x
    S sumGteX(T x) {
        x -= off;
        return total - slt(x) + S(off) * (n - lt(x));
    }

    // O(logN) -- sum of the values v with lo <= v <= hi (0 if lo > hi)
    S sumInValRange(T lo, T hi) {
        if (hi < lo) return 0;
        lo -= off, hi -= off;
        return sle(hi) - slt(lo) + S(off) * (le(hi) - lt(lo));
    }

    // O(logN) -- sum of the kFrom-th..kTo-th largest values (1-indexed, inclusive; (5, 8) = 5th..8th biggest); throws out_of_range unless 1 <= kFrom <= kTo <= size
    S sumKthLargestRange(long long kFrom, long long kTo) {
        if (kFrom < 1 || kFrom > kTo || kTo > n) throw out_of_range("sumKthLargestRange: needs 1 <= kFrom <= kTo <= size");
        return sumFirst(n - kFrom + 1) - sumFirst(n - kTo) + S(off) * (kTo - kFrom + 1);
    }

    // O(logN) -- sum of the kFrom-th..kTo-th smallest values (1-indexed, inclusive); throws out_of_range unless 1 <= kFrom <= kTo <= size
    S sumKthSmallestRange(long long kFrom, long long kTo) {
        if (kFrom < 1 || kFrom > kTo || kTo > n) throw out_of_range("sumKthSmallestRange: needs 1 <= kFrom <= kTo <= size");
        return sumFirst(kTo) - sumFirst(kFrom - 1) + S(off) * (kTo - kFrom + 1);
    }

    // O(logN) -- sum of the k largest values; throws out_of_range unless 0 <= k <= size
    S sumLargestK(long long k) {
        if (k < 0 || k > n) throw out_of_range("sumLargestK: needs 0 <= k <= size");
        return total - sumFirst(n - k) + S(off) * k;
    }

    // O(logN) -- sum of the values < x
    S sumLtX(T x) {
        x -= off;
        return slt(x) + S(off) * lt(x);
    }

    // O(logN) -- sum of the values <= x
    S sumLteX(T x) {
        x -= off;
        return sle(x) + S(off) * le(x);
    }

    // O(logN) -- sum of the k smallest values; throws out_of_range unless 0 <= k <= size
    S sumSmallestK(long long k) {
        if (k < 0 || k > n) throw out_of_range("sumSmallestK: needs 0 <= k <= size");
        return sumFirst(k) + S(off) * k;
    }
};
