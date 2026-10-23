// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/sets/avl-with-sums-mex/template.cpp
// @operations: add addCount count countDistinct countGtX countGteX countInValRange countLtX countLteX kthLargest kthSmallest largestLtX largestLteX max medianHigh medianLow mex min popMax popMin remove removeAll removeCount size smallestGtX smallestGteX sumAbsDiffToMedian sumAbsDiffToX sumAll sumGtX sumGteX sumInValRange sumKthLargestRange sumKthSmallestRange sumLargestK sumLtX sumLteX sumSmallestK
// @data-structure-type: avl
// @values: online
// @complexities:
//   add: log(N)
//   addCount: log(N)
//   count: log(N)
//   countDistinct: 1
//   countGtX: log(N)
//   countGteX: log(N)
//   countInValRange: log(N)
//   countLtX: log(N)
//   countLteX: log(N)
//   kthLargest: log(N)
//   kthSmallest: log(N)
//   largestLtX: log(N)
//   largestLteX: log(N)
//   max: 1
//   medianHigh: 1 amortized
//   medianLow: 1 amortized
//   mex: 1 amortized
//   min: 1
//   popMax: log(N)
//   popMin: log(N)
//   remove: log(N)
//   removeAll: log(N)
//   removeCount: log(N)
//   size: 1
//   smallestGtX: log(N)
//   smallestGteX: log(N)
//   sumAbsDiffToMedian: 1 amortized
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
    T mn{}, mx{};  // kept current by addRaw while n > 0
    bool med = false;  // medians (low, high) are tracked from the first median query on
    Info low{}, high{};
    long long mexV = -1;  // -1 until mex() is first called, then kept current
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

    long long le(T x) { return lt(x + 1); }

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

    S sle(T x) { return slt(x + 1); }

    T kth(long long k) {
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

    void addRaw(T x, long long c) {  // c copies of x (c < 0 removes); keeps min / max (and medians / mex once asked for) current
        n += c;
        total += S(c) * x;
        insert(x, c);
        if (c > 0) {
            if (x == T(mexV) && mexV >= 0) mexV = findMex();  // x filled the mex (mexV is -1 until mex() is first called)
            if (n == c) {  // the set was empty
                mn = mx = x;
                if (med) low = high = Info{x, 0, c, 0};
                return;
            }
            if (x < mn) mn = x;
            if (x > mx) mx = x;
        } else {
            if (x >= 0 && x < T(mexV) && !countOf(x)) mexV = x;  // the last copy of a value below the mex
            if (!n) return;
            if (x == mn) mn = kth(1);
            if (x == mx) mx = kth(n);
        }
        if (!med) return;
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

    void startMedians() {  // the first median query (n > 0): from now on addRaw keeps both medians current
        med = true;
        low = kthInfo((n + 1) / 2), high = kthInfo(n / 2 + 1);
    }

    S sumFirst(long long k) {  // sum of the k smallest values
        if (k <= 0) return 0;
        Info f = kthInfo(k);
        return f.sb + S(k - f.before) * f.v;
    }

    // O(logN) -- add one copy of x
    void add(T x) {
        addRaw(x, 1);
    }

    // O(logN) -- add cnt copies of val (nothing if cnt <= 0)
    void addCount(T val, long long cnt) {
        if (cnt > 0) addRaw(val, cnt);
    }

    // O(logN) -- how many copies of x
    long long count(T x) {
        return countOf(x);
    }

    // O(1) -- how many distinct values
    long long countDistinct() {
        return d;
    }

    // O(logN) -- how many values > x
    long long countGtX(T x) {
        return n - le(x);
    }

    // O(logN) -- how many values >= x
    long long countGteX(T x) {
        return n - lt(x);
    }

    // O(logN) -- how many values v with lo <= v <= hi (0 if lo > hi)
    long long countInValRange(T lo, T hi) {
        return lo <= hi ? le(hi) - lt(lo) : 0;
    }

    // O(logN) -- how many values < x
    long long countLtX(T x) {
        return lt(x);
    }

    // O(logN) -- how many values <= x
    long long countLteX(T x) {
        return le(x);
    }

    // O(logN) -- k-th largest value (1-indexed); throws out_of_range unless 1 <= k <= size
    T kthLargest(long long k) {
        if (k < 1 || k > n) throw out_of_range("kthLargest: needs 1 <= k <= size");
        return kth(n - k + 1);
    }

    // O(logN) -- k-th smallest value (1-indexed); throws out_of_range unless 1 <= k <= size
    T kthSmallest(long long k) {
        if (k < 1 || k > n) throw out_of_range("kthSmallest: needs 1 <= k <= size");
        return kth(k);
    }

    // O(logN) -- largest value < x; nullopt if there is none
    optional<T> largestLtX(T x) {
        long long c = lt(x);
        if (!c) return nullopt;
        return kth(c);
    }

    // O(logN) -- largest value <= x; nullopt if there is none
    optional<T> largestLteX(T x) {
        long long c = le(x);
        if (!c) return nullopt;
        return kth(c);
    }

    // O(1) -- largest value; nullopt if empty
    optional<T> max() {
        if (!n) return nullopt;
        return mx;
    }

    // O(1 amortized) -- upper median: the (floor(size/2) + 1)-th smallest value; nullopt if empty
    optional<T> medianHigh() {
        if (!n) return nullopt;
        if (!med) startMedians();
        return high.v;
    }

    // O(1 amortized) -- lower median: the ceil(size/2)-th smallest value; nullopt if empty
    optional<T> medianLow() {
        if (!n) return nullopt;
        if (!med) startMedians();
        return low.v;
    }

    // O(1 amortized) -- smallest non-negative integer not in the set
    long long mex() {
        if (mexV < 0) mexV = findMex();  // the first call: from now on addRaw keeps it current
        return mexV;
    }

    // O(1) -- smallest value; nullopt if empty
    optional<T> min() {
        if (!n) return nullopt;
        return mn;
    }

    // O(logN) -- remove and return the largest value; nullopt if empty
    optional<T> popMax() {
        if (!n) return nullopt;
        T v = mx;
        addRaw(v, -1);
        return v;
    }

    // O(logN) -- remove and return the smallest value; nullopt if empty
    optional<T> popMin() {
        if (!n) return nullopt;
        T v = mn;
        addRaw(v, -1);
        return v;
    }

    // O(logN) -- remove one copy of x if present; returns how many were removed (0 or 1)
    long long remove(T x) {
        if (!count(x)) return 0;
        addRaw(x, -1);
        return 1;
    }

    // O(logN) -- remove every copy of val; returns how many were removed
    long long removeAll(T val) {
        long long k = count(val);
        if (k) addRaw(val, -k);
        return k;
    }

    // O(logN) -- remove min(cnt, count(val)) copies of val; returns how many were removed
    long long removeCount(T val, long long cnt) {
        long long k = std::min(cnt, count(val));
        if (k <= 0) return 0;
        addRaw(val, -k);
        return k;
    }

    // O(1) -- how many values (copies count)
    long long size() {
        return n;
    }

    // O(logN) -- smallest value > x; nullopt if there is none
    optional<T> smallestGtX(T x) {
        long long c = le(x);
        if (c == n) return nullopt;
        return kth(c + 1);
    }

    // O(logN) -- smallest value >= x; nullopt if there is none
    optional<T> smallestGteX(T x) {
        long long c = lt(x);
        if (c == n) return nullopt;
        return kth(c + 1);
    }

    // O(1 amortized) -- sum of |v - medianLow()| over all values (min total moves to make all equal); 0 if empty
    S sumAbsDiffToMedian() {
        if (!n) return 0;
        if (!med) startMedians();
        const Info& m = low;
        return S(m.v) * m.before - m.sb + (total - m.sb - S(m.v) * m.c) - S(m.v) * (n - m.before - m.c);
    }

    // O(logN) -- sum of |v - x| over all values
    S sumAbsDiffToX(T x) {
        long long c = lt(x);
        S s = slt(x);
        return S(x) * c - s + (total - s) - S(x) * (n - c);
    }

    // O(1) -- sum of all values
    S sumAll() {
        return total;
    }

    // O(logN) -- sum of the values > x
    S sumGtX(T x) {
        return total - sle(x);
    }

    // O(logN) -- sum of the values >= x
    S sumGteX(T x) {
        return total - slt(x);
    }

    // O(logN) -- sum of the values v with lo <= v <= hi (0 if lo > hi)
    S sumInValRange(T lo, T hi) {
        return lo <= hi ? sle(hi) - slt(lo) : S(0);
    }

    // O(logN) -- sum of the i-th..j-th largest values (1-indexed, inclusive; (5, 8) = 5th..8th biggest); throws out_of_range unless 1 <= i <= j <= size
    S sumKthLargestRange(long long i, long long j) {
        if (i < 1 || i > j || j > n) throw out_of_range("sumKthLargestRange: needs 1 <= i <= j <= size");
        return sumFirst(n - i + 1) - sumFirst(n - j);
    }

    // O(logN) -- sum of the i-th..j-th smallest values (1-indexed, inclusive); throws out_of_range unless 1 <= i <= j <= size
    S sumKthSmallestRange(long long i, long long j) {
        if (i < 1 || i > j || j > n) throw out_of_range("sumKthSmallestRange: needs 1 <= i <= j <= size");
        return sumFirst(j) - sumFirst(i - 1);
    }

    // O(logN) -- sum of the k largest values; throws out_of_range unless 0 <= k <= size
    S sumLargestK(long long k) {
        if (k < 0 || k > n) throw out_of_range("sumLargestK: needs 0 <= k <= size");
        return total - sumFirst(n - k);
    }

    // O(logN) -- sum of the values < x
    S sumLtX(T x) {
        return slt(x);
    }

    // O(logN) -- sum of the values <= x
    S sumLteX(T x) {
        return sle(x);
    }

    // O(logN) -- sum of the k smallest values; throws out_of_range unless 0 <= k <= size
    S sumSmallestK(long long k) {
        if (k < 0 || k > n) throw out_of_range("sumSmallestK: needs 0 <= k <= size");
        return sumFirst(k);
    }
};
