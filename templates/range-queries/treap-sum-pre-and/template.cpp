// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/treap-sum-pre-and/template.cpp
// @operations: append appendLeft eraseRange getAll insertAt insertCopiesAt leftmostPrefixSumGtX leftmostPrefixSumGteX maxPrefixSum moveRange pointAdd pointAssign pointChmax pointChmin pointGet pop popLeft rangeAndQuery rangeRotateLeft rangeRotateRight rangeSum
// @data-structure-type: treap
// @complexities:
//   append: log(N) expected
//   appendLeft: log(N) expected
//   eraseRange: log(N) expected
//   getAll: N
//   insertAt: log(N) expected
//   insertCopiesAt: log(N) expected
//   leftmostPrefixSumGtX: log(N) expected
//   leftmostPrefixSumGteX: log(N) expected
//   maxPrefixSum: log(N) expected
//   moveRange: log(N) expected
//   pointAdd: log(N) expected
//   pointAssign: log(N) expected
//   pointChmax: log(N) expected
//   pointChmin: log(N) expected
//   pointGet: log(N) expected
//   pop: log(N) expected
//   popLeft: log(N) expected
//   rangeAndQuery: log(N) expected
//   rangeRotateLeft: log(N) expected
//   rangeRotateRight: log(N) expected
//   rangeSum: log(N) expected
//   build: N
// @memory:
//   layout: none
//   node: val[1*N] sz[1*N] L[1*N] R[1*N] pri[1*N] sm[1*N] pre[1*N] an[1*N]
//   tags: none
//   other: none
//   note: N = every value ever inserted (the initial array plus each insert; erased nodes are not reused)

// Implicit treap with composable aggregates: an array you can insert into / erase from anywhere, rotate, move in
// O(logN) expected each; each node keeps its sum, its best prefix sum, its AND over its subtree. All indices 0-based,
// ranges inclusive [l, r], an index always the position in the CURRENT array; searches return -1 when nothing
// qualifies.
// T: int, long long, ...; sums are kept in S (long long for small T).
template <typename T>
struct ImplicitTreap {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    int root = 0;
    vector<T> val{T(0)};
    vector<unsigned long long> pri{0};
    vector<int> L{0}, R{0}, sz{0};
    vector<S> sm{0};
    vector<S> pre{0};
    vector<T> an{~T(0)};

    static unsigned long long rnd() {
        static mt19937_64 g(chrono::steady_clock::now().time_since_epoch().count());
        return g();
    }

    // O(N) -- arr: the initial array (may be empty)
    explicit ImplicitTreap(const vector<T>& arr = {}) { root = build(arr); }

    // O(1) -- the current length of the array
    int size() const { return sz[root]; }

    // O(logN) expected -- append v to the end
    void append(T v) { root = merge(root, newNode(v)); }

    // O(logN) expected -- insert v at the front (it becomes a[0]; everything else shifts right by one)
    void appendLeft(T v) { insertAt(0, v); }

    // O(logN) expected -- remove a[l..r]
    void eraseRange(int l, int r) {
        int a, b, c;
        cut(l, r, a, b, c);
        root = merge(a, c);
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

    // O(logN) expected -- insert v so it becomes a[i]; 0 <= i <= size() (i = size() appends)
    void insertAt(int i, T v) {
        int a, c;
        split(root, i, a, c);
        root = merge(merge(a, newNode(v)), c);
    }

    // O(k + logN) expected -- insert k copies of v so they become a[i..i+k-1] (nothing if k <= 0)
    void insertCopiesAt(int i, T v, long long k) {
        if (k <= 0) return;
        int a, c;
        split(root, i, a, c);
        root = merge(merge(a, build(vector<T>(k, v))), c);
    }

    // O(logN) expected -- first i in [l, r] with a[l] + ... + a[i] > x, or -1 (a walk pruned by best prefix sums)
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

    // O(logN) expected -- first i in [l, r] with a[l] + ... + a[i] >= x, or -1 (a walk pruned by best prefix sums)
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

    // O(logN) expected -- max of a[l] + ... + a[i] over i in [l, r]
    S maxPrefixSum(int l, int r) {
        int a, b, c;
        cut(l, r, a, b, c);
        S res = pre[b];
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN) expected -- cut a[l..r] out, then paste it back so it starts at index i of the array without it
    void moveRange(int l, int r, int i) {
        int a, b, c, x, y;
        cut(l, r, a, b, c);
        split(merge(a, c), i, x, y);
        root = merge(merge(x, b), y);
    }

    // O(logN) expected -- a[i] += v
    void pointAdd(int i, T v) {
        vector<int> path;
        int t = find(i, &path);
        val[t] = val[t] + v;
        pull(t);
        for (int k = (int)path.size() - 1; k >= 0; k--) pull(path[k]);
    }

    // O(logN) expected -- a[i] = v
    void pointAssign(int i, T v) {
        vector<int> path;
        int t = find(i, &path);
        val[t] = v;
        pull(t);
        for (int k = (int)path.size() - 1; k >= 0; k--) pull(path[k]);
    }

    // O(logN) expected -- a[i] = max(a[i], v)
    void pointChmax(int i, T v) {
        vector<int> path;
        int t = find(i, &path);
        val[t] = max(val[t], v);
        pull(t);
        for (int k = (int)path.size() - 1; k >= 0; k--) pull(path[k]);
    }

    // O(logN) expected -- a[i] = min(a[i], v)
    void pointChmin(int i, T v) {
        vector<int> path;
        int t = find(i, &path);
        val[t] = min(val[t], v);
        pull(t);
        for (int k = (int)path.size() - 1; k >= 0; k--) pull(path[k]);
    }

    // O(logN) expected -- a[i]
    T pointGet(int i) { return val[find(i)]; }

    // O(logN) expected -- remove a[i] and return it; everything after it shifts left by one
    T pop(int i) {
        T v = pointGet(i);
        eraseRange(i, i);
        return v;
    }

    // O(logN) expected -- remove a[0] and return it
    T popLeft() { return pop(0); }

    // O(logN) expected -- a[l] & ... & a[r]
    T rangeAndQuery(int l, int r) {
        int a, b, c;
        cut(l, r, a, b, c);
        T res = an[b];
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN) expected -- cyclic shift a[l..r] left by k (a[l + k] moves to l); any integer k, negative shifts right
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

    // O(logN) expected -- cyclic shift a[l..r] right by k; any integer k, negative shifts left
    void rangeRotateRight(int l, int r, long long k) { rangeRotateLeft(l, r, -k); }

    // O(logN) expected -- a[l] + ... + a[r]
    S rangeSum(int l, int r) {
        int a, b, c;
        cut(l, r, a, b, c);
        S res = sm[b];
        root = merge(merge(a, b), c);
        return res;
    }

    // ---- internals ----

    int newNode(T v) {
        val.push_back(v), pri.push_back(rnd()), L.push_back(0), R.push_back(0), sz.push_back(1);
        sm.push_back(S(v)), pre.push_back(S(v)), an.push_back(v);
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
        T v = val[x];
        S s = S(v), p = S(v);  // the node alone, then with its left / right parts
        if (l) {
            S ls = sm[l], lp = pre[l];
            S ns = ls + s, np = max(lp, ls + p);
            s = ns, p = np;
        }
        if (r) {
            S rs = sm[r], rp = pre[r];
            S ns = s + rs, np = max(p, s + rp);
            s = ns, p = np;
        }
        sm[x] = s, pre[x] = p;
        an[x] = an[l] & v & an[r];  // (node 0: the AND of nothing, ~0)
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

    int find(int i, vector<int>* path = nullptr) {  // the node holding a[i], every tag on the way pushed
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
