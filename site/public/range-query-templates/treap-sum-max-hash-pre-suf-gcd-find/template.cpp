// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/treap-sum-max-hash-pre-suf-gcd-find/template.cpp
// @operations: append appendLeft cut find getAll insertAt insertCopiesAt isPalindrome leftmostGtX leftmostGteX leftmostPrefixSumGtX leftmostPrefixSumGteX maxPrefixSum maxSuffixSum merge paste pointAdd pointAssign pointChmax pointChmin pointGet rangeGcd rangeHash rangeHashReversed rangeMax rangeRotateLeft rangeRotateRight rangeSum rangesEqual rightmostGtX rightmostGteX rightmostSuffixSumGtX rightmostSuffixSumGteX split trisect
// @data-structure-type: treap
// @complexities:
//   append: log(N)*log(U) expected ?
//   appendLeft: log(N)*log(U) expected ?
//   cut: log(N)*log(U) expected ?
//   find: log(N)*log(U) expected ?
//   getAll: N
//   insertAt: log(N)*log(U) expected ?
//   insertCopiesAt: log(N)*log(U) expected ?
//   isPalindrome: log(N)*log(U) expected ?
//   leftmostGtX: log(N)*log(U) expected ?
//   leftmostGteX: log(N)*log(U) expected ?
//   leftmostPrefixSumGtX: log(N)*log(U) expected ?
//   leftmostPrefixSumGteX: log(N)*log(U) expected ?
//   maxPrefixSum: log(N)*log(U) expected ?
//   maxSuffixSum: log(N)*log(U) expected ?
//   merge: log(N)*log(U) expected ?
//   paste: log(N)*log(U) expected ?
//   pointAdd: log(N)*log(U) expected ?
//   pointAssign: log(N)*log(U) expected ?
//   pointChmax: log(N)*log(U) expected ?
//   pointChmin: log(N)*log(U) expected ?
//   pointGet: log(N) expected
//   rangeGcd: log(N)*log(U) expected ?
//   rangeHash: log(N)*log(U) expected ?
//   rangeHashReversed: log(N)*log(U) expected ?
//   rangeMax: log(N)*log(U) expected ?
//   rangeRotateLeft: log(N)*log(U) expected ?
//   rangeRotateRight: log(N)*log(U) expected ?
//   rangeSum: log(N)*log(U) expected ?
//   rangesEqual: log(N)*log(U) expected ?
//   rightmostGtX: log(N)*log(U) expected ?
//   rightmostGteX: log(N)*log(U) expected ?
//   rightmostSuffixSumGtX: log(N)*log(U) expected ?
//   rightmostSuffixSumGteX: log(N)*log(U) expected ?
//   split: log(N)*log(U) expected ?
//   trisect: log(N)*log(U) expected ?
//   build: N*log(U) ?
// @memory:
//   layout: none
//   node: val[1*N] sz[1*N] L[1*N] R[1*N] pri[1*N] sm[1*N] mx[1*N] fh[1*N] bh[1*N] pw[1*N] pre[1*N] suf[1*N] g[1*N] par[1*N]
//   tags: none
//   other: where[1*N]
//   note: N = every value ever inserted (the initial array plus each insert; erased nodes are not reused); every ImplicitTreap<T> shares one node pool (pieces move between any of them; nothing to reset); find: a parent per node and a map value -> node

// Implicit treap with composable aggregates: an array you can insert into anywhere, rotate, move, cut pieces out of
// (that is how to erase) and paste them back in O(logN) expected each, and find any value's index (values distinct);
// each node keeps its sum, its max, its forward / backward hash (and B^size), its best prefix sum, its best suffix
// sum, its gcd over its subtree. All indices 0-based, ranges inclusive [l, r], an index always the position in the
// CURRENT array; searches return -1 when nothing qualifies.
// T: int, long long, ...; sums are kept in S (long long for small T).
template <typename T>
struct ImplicitTreap {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    using U64 = unsigned long long;
    struct SafeHash {  // splitmix64 with a seed random per run (the default hash of an integer is easy to attack)
        size_t operator()(const T& x) const {
            static const unsigned long long seed = chrono::steady_clock::now().time_since_epoch().count();
            unsigned long long z = (unsigned long long)x + seed + 0x9e3779b97f4a7c15ULL;
            z = (z ^ (z >> 30)) * 0xbf58476d1ce4e5b9ULL;
            z = (z ^ (z >> 27)) * 0x94d049bb133111ebULL;
            return z ^ (z >> 31);
        }
    };
    // one node pool shared by every ImplicitTreap<T>: cut / paste move nodes between them, so a piece from one can go
    // into any other (node 0 = the empty tree). Nodes are never freed (memory = every value ever inserted, over the
    // whole run), so there is nothing to reset between test cases
    static inline vector<T> val{T(0)};
    static inline vector<unsigned long long> pri{0};
    static inline vector<int> L{0};
    static inline vector<int> R{0};
    static inline vector<int> sz{0};
    static inline vector<S> sm{0};
    static inline vector<T> mx{T(0)};
    static inline vector<U64> fh{0};
    static inline vector<U64> bh{0};
    static inline vector<U64> pw{1};
    static inline vector<S> pre{0};
    static inline vector<S> suf{0};
    static inline vector<T> g{T(0)};
    static inline vector<int> par{0};
    static inline unordered_map<T, int, SafeHash> where;
    int root = 0;

    // O(N) -- arr: the initial array (leave it out to start empty)
    explicit ImplicitTreap(const vector<T>& arr = {}) { root = build(arr); }

    ImplicitTreap makeEmpty() const { return ImplicitTreap(); }  // (a new, empty one)

    static unsigned long long rnd() {
        static mt19937_64 g(chrono::steady_clock::now().time_since_epoch().count());
        return g();
    }
    // range hashes: mod the prime 2^61 - 1, with a base picked at random each run (so no test can be built against it)
    static constexpr unsigned long long HP = (1ULL << 61) - 1;
    static unsigned long long HB() {
        static unsigned long long b = (1ULL << 40) + rnd() % (HP - (1ULL << 41));
        return b;
    }
    static unsigned long long hmul(unsigned long long a, unsigned long long b) {
        __uint128_t c = (__uint128_t)a * b;
        unsigned long long r = (unsigned long long)(c & HP) + (unsigned long long)(c >> 61);
        r = (r & HP) + (r >> 61);
        return r >= HP ? r - HP : r;
    }
    static unsigned long long hadd(unsigned long long a, unsigned long long b) {
        return a + b >= HP ? a + b - HP : a + b;
    }
    static unsigned long long hraw(T v) {  // v as a residue (what an add changes a hash by, per position)
        long long r = (long long)v % (long long)HP;
        return r < 0 ? (unsigned long long)(r + (long long)HP) : (unsigned long long)r;
    }
    static unsigned long long hval(T v) {  // the hash of value v: v + an offset random per run, so no common value is 0
        static unsigned long long off = 1 + rnd() % (HP - 1);
        return hadd(hraw(v), off);
    }


    // O(1) -- the current length of the array
    int size() const { return sz[root]; }

    // O(logN * logU) expected -- append v to the end
    void append(T v) { root = merge(root, newNode(v)); }

    // O(logN * logU) expected -- insert v at the front (it becomes a[0]; everything else shifts right by one)
    void appendLeft(T v) { insertAt(0, v); }

    // O(logN * logU) expected -- remove a[l..r] and return it as a treap of its own (indices from 0)
    ImplicitTreap cut(int l, int r) {
        int a, b, c;
        cut(l, r, a, b, c);
        root = merge(a, c);
        ImplicitTreap piece = makeEmpty();
        piece.root = b;
        return piece;
    }

    // O(logN * logU) expected -- the index of x, or -1 if x isn't in this treap (values distinct across all treaps)
    int find(T x) {
        auto it = where.find(x);
        if (it == where.end() || val[it->second] != x) return -1;
        int t = it->second;
        vector<int> path{t};
        while (true) {  // up to the root (a parent counts only while it still has the node as a child)
            int c = path.back(), p = par[c];
            if (!p || (L[p] != c && R[p] != c)) break;
            path.push_back(p);
        }
        if (path.back() != root) return -1;  // (erased, or in another treap)
        int i = sz[L[t]];
        for (size_t k = 1; k < path.size(); k++)
            if (R[path[k]] == path[k - 1]) i += sz[L[path[k]]] + 1;
        return i;
    }

    // O(N) -- the whole current array, every pending tag applied on the way
    vector<T> getAll() {
        vector<T> out;
        out.reserve(size());
        vector<int> st;
        int t = root;
        while (!st.empty() || t) {
            while (t) st.push_back(t), t = L[t];
            t = st.back(), st.pop_back();
            out.push_back(val[t]);
            t = R[t];
        }
        return out;
    }

    // O(logN * logU) expected -- insert v so it becomes a[i]; 0 <= i <= size() (i = size() appends)
    void insertAt(int i, T v) {
        int a, c;
        split(root, i, a, c);
        root = merge(merge(a, newNode(v)), c);
    }

    // O(k + logN * logU) expected -- insert k copies of v so they become a[i..i+k-1] (nothing if k <= 0)
    void insertCopiesAt(int i, T v, long long k) {
        if (k <= 0) return;
        int a, c;
        split(root, i, a, c);
        root = merge(merge(a, build(vector<T>(k, v))), c);
    }

    // O(logN * logU) expected -- is a[l..r] a palindrome (its two hashes agree)
    bool isPalindrome(int l, int r) {
        int a, b, c;
        cut(l, r, a, b, c);
        bool res = fh[b] == bh[b];
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN * logU) expected -- the first i in [l, r] with a[i] > x, or -1 (pruned by the subtree max)
    int leftmostGtX(int l, int r, T x) {
        int a, b, c;
        cut(l, r, a, b, c);
        int t = b, i = 0, res = -1;
        if (t && mx[t] > x) {  // some value in a[l..r] passes
            while (true) {
                if (L[t] && mx[L[t]] > x) t = L[t];
                else if (val[t] > x) { res = l + i + sz[L[t]]; break; }
                else i += sz[L[t]] + 1, t = R[t];
            }
        }
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN * logU) expected -- the first i in [l, r] with a[i] >= x, or -1 (pruned by the subtree max)
    int leftmostGteX(int l, int r, T x) {
        int a, b, c;
        cut(l, r, a, b, c);
        int t = b, i = 0, res = -1;
        if (t && mx[t] >= x) {  // some value in a[l..r] passes
            while (true) {
                if (L[t] && mx[L[t]] >= x) t = L[t];
                else if (val[t] >= x) { res = l + i + sz[L[t]]; break; }
                else i += sz[L[t]] + 1, t = R[t];
            }
        }
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN * logU) expected -- first i in [l, r] with a[l] + ... + a[i] > x, or -1 (pruned by best prefix sums)
    int leftmostPrefixSumGtX(int l, int r, T x) {
        int a, b, c;
        cut(l, r, a, b, c);
        int t = b, i = 0, res = -1;
        S acc = 0;
        if (t && pre[t] > S(x)) {
            while (true) {
                int lt = L[t];
                if (lt && acc + pre[lt] > S(x)) { t = lt; continue; }
                acc += sm[lt];
                if (acc + S(val[t]) > S(x)) { res = l + i + sz[lt]; break; }
                acc += S(val[t]), i += sz[lt] + 1, t = R[t];
            }
        }
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN * logU) expected -- first i in [l, r] with a[l] + ... + a[i] >= x, or -1 (pruned by best prefix sums)
    int leftmostPrefixSumGteX(int l, int r, T x) {
        int a, b, c;
        cut(l, r, a, b, c);
        int t = b, i = 0, res = -1;
        S acc = 0;
        if (t && pre[t] >= S(x)) {
            while (true) {
                int lt = L[t];
                if (lt && acc + pre[lt] >= S(x)) { t = lt; continue; }
                acc += sm[lt];
                if (acc + S(val[t]) >= S(x)) { res = l + i + sz[lt]; break; }
                acc += S(val[t]), i += sz[lt] + 1, t = R[t];
            }
        }
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN * logU) expected -- max of a[l] + ... + a[i] over i in [l, r]
    S maxPrefixSum(int l, int r) {
        int a, b, c;
        cut(l, r, a, b, c);
        S res = pre[b];
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN * logU) expected -- max of a[i] + ... + a[r] over i in [l, r]
    S maxSuffixSum(int l, int r) {
        int a, b, c;
        cut(l, r, a, b, c);
        S res = suf[b];
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN * logU) expected -- append all of other at the end; other is left empty
    void merge(ImplicitTreap& other) { root = merge(root, other.root), other.root = 0; }

    // O(logN * logU) expected -- insert all of other (any ImplicitTreap, e.g. a cut piece) so it starts at a[i]
    // (0 <= i <= size()); other is left empty
    void paste(int i, ImplicitTreap& other) {
        int a, c;
        split(root, i, a, c);
        root = merge(merge(a, other.root), c);
        other.root = 0;
    }

    // O(logN * logU) expected -- a[i] += v
    void pointAdd(int i, T v) {
        vector<int> path;
        int t = locate(i, &path);
        T old = val[t];
        val[t] = val[t] + v;
        rekey(t, old);
        pull(t);
        for (int k = (int)path.size() - 1; k >= 0; k--) pull(path[k]);
    }

    // O(logN * logU) expected -- a[i] = v
    void pointAssign(int i, T v) {
        vector<int> path;
        int t = locate(i, &path);
        T old = val[t];
        val[t] = v;
        rekey(t, old);
        pull(t);
        for (int k = (int)path.size() - 1; k >= 0; k--) pull(path[k]);
    }

    // O(logN * logU) expected -- a[i] = max(a[i], v)
    void pointChmax(int i, T v) {
        vector<int> path;
        int t = locate(i, &path);
        T old = val[t];
        val[t] = max(val[t], v);
        rekey(t, old);
        pull(t);
        for (int k = (int)path.size() - 1; k >= 0; k--) pull(path[k]);
    }

    // O(logN * logU) expected -- a[i] = min(a[i], v)
    void pointChmin(int i, T v) {
        vector<int> path;
        int t = locate(i, &path);
        T old = val[t];
        val[t] = min(val[t], v);
        rekey(t, old);
        pull(t);
        for (int k = (int)path.size() - 1; k >= 0; k--) pull(path[k]);
    }

    // O(logN) expected -- a[i]
    T pointGet(int i) { return val[locate(i)]; }

    // O(logN * logU) expected -- gcd of |a[l]|, ..., |a[r]|
    T rangeGcd(int l, int r) {
        int a, b, c;
        cut(l, r, a, b, c);
        T res = g[b];
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN * logU) expected -- hash of a[l..r] left to right (mod 2^61 - 1, random base): equal ranges hash equal
    U64 rangeHash(int l, int r) {
        int a, b, c;
        cut(l, r, a, b, c);
        U64 res = fh[b];
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN * logU) expected -- hash of a[l..r] read right to left (= rangeHash of the reversed range)
    U64 rangeHashReversed(int l, int r) {
        int a, b, c;
        cut(l, r, a, b, c);
        U64 res = bh[b];
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN * logU) expected -- max of a[l..r]
    T rangeMax(int l, int r) {
        int a, b, c;
        cut(l, r, a, b, c);
        T res = mx[b];
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN * logU) expected -- cyclic shift a[l..r] left by k (a[l + k] moves to l); k can be huge or negative:
    // it is taken mod the length (negative shifts right)
    void rangeRotateLeft(int l, int r, long long k) {
        int a, b, c, len = r - l + 1;
        cut(l, r, a, b, c);
        k = ((k % len) + len) % len;
        if (k) {
            int b1, b2;
            split(b, (int)k, b1, b2);
            b = merge(b2, b1);
        }
        root = merge(merge(a, b), c);
    }

    // O(logN * logU) expected -- cyclic shift a[l..r] right by k; k can be huge or negative: it is taken mod the
    // length (negative shifts left)
    void rangeRotateRight(int l, int r, long long k) { rangeRotateLeft(l, r, -k); }

    // O(logN * logU) expected -- a[l] + ... + a[r]
    S rangeSum(int l, int r) {
        int a, b, c;
        cut(l, r, a, b, c);
        S res = sm[b];
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN * logU) expected -- are a[l1..r1] and a[l2..r2] equal (same length and hash)
    bool rangesEqual(int l1, int r1, int l2, int r2) {
        return r1 - l1 == r2 - l2 && rangeHash(l1, r1) == rangeHash(l2, r2);
    }

    // O(logN * logU) expected -- the last i in [l, r] with a[i] > x, or -1 (pruned by the subtree max)
    int rightmostGtX(int l, int r, T x) {
        int a, b, c;
        cut(l, r, a, b, c);
        int t = b, i = 0, res = -1;
        if (t && mx[t] > x) {  // some value in a[l..r] passes
            while (true) {
                if (R[t] && mx[R[t]] > x) i += sz[L[t]] + 1, t = R[t];
                else if (val[t] > x) { res = l + i + sz[L[t]]; break; }
                else t = L[t];
            }
        }
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN * logU) expected -- the last i in [l, r] with a[i] >= x, or -1 (pruned by the subtree max)
    int rightmostGteX(int l, int r, T x) {
        int a, b, c;
        cut(l, r, a, b, c);
        int t = b, i = 0, res = -1;
        if (t && mx[t] >= x) {  // some value in a[l..r] passes
            while (true) {
                if (R[t] && mx[R[t]] >= x) i += sz[L[t]] + 1, t = R[t];
                else if (val[t] >= x) { res = l + i + sz[L[t]]; break; }
                else t = L[t];
            }
        }
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN * logU) expected -- last i in [l, r] with a[i] + ... + a[r] > x, or -1 (pruned by best suffix sums)
    int rightmostSuffixSumGtX(int l, int r, T x) {
        int a, b, c;
        cut(l, r, a, b, c);
        int t = b, i = 0, res = -1;
        S acc = 0;
        if (t && suf[t] > S(x)) {
            while (true) {
                int rt = R[t];
                if (rt && acc + suf[rt] > S(x)) { i += sz[L[t]] + 1, t = rt; continue; }
                acc += sm[rt];
                if (acc + S(val[t]) > S(x)) { res = l + i + sz[L[t]]; break; }
                acc += S(val[t]), t = L[t];
            }
        }
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN * logU) expected -- last i in [l, r] with a[i] + ... + a[r] >= x, or -1 (pruned by best suffix sums)
    int rightmostSuffixSumGteX(int l, int r, T x) {
        int a, b, c;
        cut(l, r, a, b, c);
        int t = b, i = 0, res = -1;
        S acc = 0;
        if (t && suf[t] >= S(x)) {
            while (true) {
                int rt = R[t];
                if (rt && acc + suf[rt] >= S(x)) { i += sz[L[t]] + 1, t = rt; continue; }
                acc += sm[rt];
                if (acc + S(val[t]) >= S(x)) { res = l + i + sz[L[t]]; break; }
                acc += S(val[t]), t = L[t];
            }
        }
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN * logU) expected -- (a[0..k-1], a[k..]) as two treaps of their own; this one is left empty
    pair<ImplicitTreap, ImplicitTreap> split(int k) {
        ImplicitTreap left = makeEmpty(), right = makeEmpty();
        split(root, k, left.root, right.root);
        root = 0;
        return {left, right};
    }

    // O(logN * logU) expected -- (a[0..l-1], a[l..r], a[r+1..]) as three treaps of their own; this one is left empty
    tuple<ImplicitTreap, ImplicitTreap, ImplicitTreap> trisect(int l, int r) {
        ImplicitTreap left = makeEmpty(), mid = makeEmpty(), right = makeEmpty();
        cut(l, r, left.root, mid.root, right.root);
        root = 0;
        return {left, mid, right};
    }

    // ---- internals ----

    int newNode(T v) {
        val.push_back(v), pri.push_back(rnd()), L.push_back(0), R.push_back(0), sz.push_back(1);
        sm.push_back(S(v)), mx.push_back(v), fh.push_back(hval(v)), bh.push_back(hval(v)), pw.push_back(HB());
        pre.push_back(S(v)), suf.push_back(S(v)), g.push_back(v < T(0) ? T(-v) : v), par.push_back(0);
        where[v] = (int)val.size() - 1;
        return (int)val.size() - 1;
    }

    // a treap of new nodes holding vals in order: a Cartesian tree in one pass, O(len)
    int build(const vector<T>& vals) {
        vector<int> stk, order, todo;
        for (const T& v : vals) {
            int x = newNode(v), last = 0;
            while (!stk.empty() && pri[stk.back()] < pri[x]) last = stk.back(), stk.pop_back();
            L[x] = last;
            if (!stk.empty()) R[stk.back()] = x;
            stk.push_back(x);
        }
        int rt = stk.empty() ? 0 : stk[0];
        if (rt) todo.push_back(rt);
        while (!todo.empty()) {
            int x = todo.back();
            todo.pop_back(), order.push_back(x);
            if (L[x]) todo.push_back(L[x]);
            if (R[x]) todo.push_back(R[x]);
        }
        for (int k = (int)order.size() - 1; k >= 0; k--) pull(order[k]);
        return rt;
    }

    void pull(int x) {  // recompute x from its children
        int l = L[x], r = R[x];
        sz[x] = sz[l] + sz[r] + 1;
        par[l] = par[r] = x;
        T v = val[x];
        S s = S(v), p = S(v), q = S(v);  // the node alone, then with its left / right parts
        if (l) {
            S ls = sm[l], lp = pre[l], lq = suf[l];
            S ns = ls + s, np = max(lp, ls + p), nq = max(q, s + lq);
            s = ns, p = np, q = nq;
        }
        if (r) {
            S rs = sm[r], rp = pre[r], rq = suf[r];
            S ns = s + rs, np = max(p, s + rp), nq = max(rq, rs + q);
            s = ns, p = np, q = nq;
        }
        sm[x] = s, pre[x] = p, suf[x] = q;
        mx[x] = v;
        if (l && mx[l] > mx[x]) mx[x] = mx[l];
        if (r && mx[r] > mx[x]) mx[x] = mx[r];
        U64 B = HB(), hv = hval(v);
        pw[x] = hmul(hmul(pw[l], B), pw[r]);
        fh[x] = hadd(hmul(hadd(hmul(fh[l], B), hv), pw[r]), fh[r]);
        bh[x] = hadd(hmul(hadd(hmul(bh[r], B), hv), pw[l]), bh[l]);
        g[x] = gcd(gcd(g[l], v), g[r]);
    }

    void rekey(int t, T old) {  // t's value changed from old: the map follows (find needs distinct values)
        auto it = where.find(old);
        if (it != where.end() && it->second == t) where.erase(it);
        where[val[t]] = t;
    }

    void split(int t, int k, int& a, int& b) {  // a = first k of t, b = the rest
        if (!t) { a = b = 0; return; }
        if (sz[L[t]] >= k) split(L[t], k, a, L[t]), b = t;
        else split(R[t], k - sz[L[t]] - 1, R[t], b), a = t;
        pull(t);
    }

    int merge(int a, int b) {  // a's elements, then b's
        if (!a || !b) return a | b;
        if (pri[a] > pri[b]) {
            R[a] = merge(R[a], b);
            pull(a);
            return a;
        }
        L[b] = merge(a, L[b]);
        pull(b);
        return b;
    }

    void cut(int l, int r, int& a, int& b, int& c) {  // a[0..l-1], a[l..r], a[r+1..]
        split(root, l, a, b);
        split(b, r - l + 1, b, c);
    }

    int locate(int i, vector<int>* path = nullptr) {  // the node holding a[i], every tag on the way pushed
        int t = root;
        while (true) {
            int ls = sz[L[t]];
            if (i == ls) return t;
            if (path) path->push_back(t);
            if (i < ls) t = L[t];
            else i -= ls + 1, t = R[t];
        }
    }
};

// Example (pieces move between treaps; merge appends and leaves its argument empty):
//     ImplicitTreap<int> t({1, 2, 3, 4, 5});
//     auto [left, mid, right] = t.trisect(1, 3);  // left = [1], mid = [2, 3, 4], right = [5]; t is empty now
//     t.merge(right);                             // t = [5]
//     t.merge(mid);                               // t = [5, 2, 3, 4]
//     t.merge(left);                              // t = [5, 2, 3, 4, 1]
