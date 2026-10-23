// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/sets/splay-with-mex/template.cpp
// @operations: add addCount count countDistinct countGtX countGteX countInValRange countLtX countLteX kthLargest kthSmallest largestLtX largestLteX max medianHigh medianLow mex min popMax popMin remove removeAll removeCount size smallestGtX smallestGteX
// @data-structure-type: splay
// @values: online
// @complexities:
//   add: log(N) amortized
//   addCount: log(N) amortized
//   count: log(N) amortized
//   countDistinct: 1
//   countGtX: log(N) amortized
//   countGteX: log(N) amortized
//   countInValRange: log(N) amortized
//   countLtX: log(N) amortized
//   countLteX: log(N) amortized
//   kthLargest: log(N) amortized
//   kthSmallest: log(N) amortized
//   largestLtX: log(N) amortized
//   largestLteX: log(N) amortized
//   max: 1
//   medianHigh: 1 amortized
//   medianLow: 1 amortized
//   mex: 1 amortized
//   min: 1
//   popMax: log(N) amortized
//   popMin: log(N) amortized
//   remove: log(N) amortized
//   removeAll: log(N) amortized
//   removeCount: log(N) amortized
//   size: 1
//   smallestGtX: log(N) amortized
//   smallestGteX: log(N) amortized
//   build: 1
// @memory:
//   layout: none
//   node: key[1*N] cnt[1*N] size[1*N] dn[1*N]
//   tags: none
//   other: children[2*N] parent[1*N]
//   note: N = most distinct values present at once (removed nodes are reused). C++: one shared node pool, call resetPool() between test cases; Python: parallel lists per tree

// Ordered multiset (online: any values, nothing known ahead): a splay tree with one node per distinct value. Each node
// keeps its value, its copies, and the copies and distinct values in its subtree; every operation splays the
// last node it touched to the root, which makes each one O(log N) amortized. Nodes live in one pool shared by every
// SplayMultiset<T> (call resetPool() between test cases); node 0 is the empty tree and removed nodes are reused.
// T: an integer type; sums in S (long long for small T).
template <typename T>
struct SplayMultiset {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    struct Node { T key; long long c, z; long long dn; int l, r, p; };  // copies; copies, distinct below; parent
    static inline vector<Node> pool{Node{}};
    static inline vector<int> freeList;
    int root = 0;
    long long n = 0, d = 0;
    struct Info { T v; long long before, c; };  // a value, copies before it, its copies
    T mn{}, mx{};  // kept current by addRaw while n > 0
    bool med = false;  // medians (low, high) are tracked from the first median query on
    Info low{}, high{};
    long long mexV = -1;  // -1 until mex() is first called, then kept current

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

    void insert(T x, long long c) {
        int t = root;
        while (t && pool[t].key != x) {
            int nxt = x < pool[t].key ? pool[t].l : pool[t].r;
            if (!nxt) break;
            t = nxt;
        }
        if (t && pool[t].key == x) {  // x is already here
            pool[t].c += c;
            pull(t);
            root = splay(t);
            if (!pool[t].c) erase(t);
            return;
        }
        int u = make(x, t);
        pool[u].c = c;
        pull(u);
        if (t) (x < pool[t].key ? pool[t].l : pool[t].r) = u;
        root = splay(u);
        d++;
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

    long long le(T x) { return lt(x + 1); }

    long long countOf(T x) {
        int t = root, last = 0;
        while (t && pool[t].key != x) last = t, t = x < pool[t].key ? pool[t].l : pool[t].r;
        touch(t ? t : last);
        return pool[t].c;
    }

    T kth(long long k) {
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

    void addRaw(T x, long long c) {  // c copies of x (c < 0 removes); keeps min / max (and medians / mex once asked for) current
        n += c;
        insert(x, c);
        if (c > 0) {
            if (x == T(mexV) && mexV >= 0) mexV = findMex();  // x filled the mex (mexV is -1 until mex() is first called)
            if (n == c) {  // the set was empty
                mn = mx = x;
                if (med) low = high = Info{x, 0, c};
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
        // each median is a tracked rank: shift its (value, copies before, copies), and search again only
        // when the rank leaves the tracked value
        if (x < low.v) low.before += c;
        else if (x == low.v) low.c += c;
        long long r = (n + 1) / 2;
        if (r <= low.before || r > low.before + low.c) low = kthInfo(r);
        if (x < high.v) high.before += c;
        else if (x == high.v) high.c += c;
        r = n / 2 + 1;
        if (r <= high.before || r > high.before + high.c) high = kthInfo(r);
    }

    void startMedians() {  // the first median query (n > 0): from now on addRaw keeps both medians current
        med = true;
        low = kthInfo((n + 1) / 2), high = kthInfo(n / 2 + 1);
    }

    // O(logN amortized) -- add one copy of x
    void add(T x) {
        addRaw(x, 1);
    }

    // O(logN amortized) -- add c copies of x (nothing if c <= 0)
    void addCount(T x, long long c) {
        if (c > 0) addRaw(x, c);
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

    // O(logN amortized) -- k-th largest value (1-indexed); throws out_of_range unless 1 <= k <= size
    T kthLargest(long long k) {
        if (k < 1 || k > n) throw out_of_range("kthLargest: needs 1 <= k <= size");
        return kth(n - k + 1);
    }

    // O(logN amortized) -- k-th smallest value (1-indexed); throws out_of_range unless 1 <= k <= size
    T kthSmallest(long long k) {
        if (k < 1 || k > n) throw out_of_range("kthSmallest: needs 1 <= k <= size");
        return kth(k);
    }

    // O(logN amortized) -- largest value < x; nullopt if there is none
    optional<T> largestLtX(T x) {
        long long c = lt(x);
        if (!c) return nullopt;
        return kth(c);
    }

    // O(logN amortized) -- largest value <= x; nullopt if there is none
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

    // O(logN amortized) -- remove every copy of x; returns how many were removed
    long long removeAll(T x) {
        long long k = count(x);
        if (k) addRaw(x, -k);
        return k;
    }

    // O(logN amortized) -- remove min(c, count(x)) copies of x; returns how many were removed
    long long removeCount(T x, long long c) {
        long long k = std::min(c, count(x));
        if (k <= 0) return 0;
        addRaw(x, -k);
        return k;
    }

    // O(1) -- how many values (copies count)
    long long size() {
        return n;
    }

    // O(logN amortized) -- smallest value > x; nullopt if there is none
    optional<T> smallestGtX(T x) {
        long long c = le(x);
        if (c == n) return nullopt;
        return kth(c + 1);
    }

    // O(logN amortized) -- smallest value >= x; nullopt if there is none
    optional<T> smallestGteX(T x) {
        long long c = lt(x);
        if (c == n) return nullopt;
        return kth(c + 1);
    }
};
