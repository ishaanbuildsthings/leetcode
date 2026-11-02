// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/append-appendLeft-concat-cut-insertAt-paste-pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeSum-rangeTwinSpin-split-trisect/template.cpp
// @operations: append appendLeft concat cut getAll insertAt paste pointAdd pointAssign pointChmax pointChmin pointGet rangeSum rangeTwinSpin split trisect
// @data-structure-type: pair-treap
// @complexities:
//   append: log(N) expected
//   appendLeft: log(N) expected
//   concat: log(N) expected
//   cut: log(N) expected
//   getAll: N
//   insertAt: log(N) expected
//   paste: log(N) expected
//   pointAdd: log(N) expected
//   pointAssign: log(N) expected
//   pointChmax: log(N) expected
//   pointChmin: log(N) expected
//   pointGet: log(N) expected
//   rangeSum: log(N) expected
//   rangeTwinSpin: log(N) expected
//   split: log(N) expected
//   trisect: log(N) expected
//   build: N
// @memory:
//   layout: none
//   node: val[1*N] sz[1*N] L[1*N] R[1*N] pri[1*N] sm[1*N]
//   tags: none
//   other: none
//   note: N = every value ever inserted (erased nodes are not reused); two treaps (even / odd positions) share one node pool

// Implicit treap pair: an array you can insert into / erase from anywhere, swap adjacent pairs in a range (a[l] <->
// a[l + 1], a[l + 2] <-> a[l + 3], ...), each in O(logN) expected, plus point ops, rangeSum. The even positions a[0],
// a[2], ... are one treap (E) and the odd ones another (O), in one node pool; a range [l, r] is a slice of each. All
// indices 0-based, ranges inclusive, always positions in the CURRENT array.
// T: int, long long, ...; sums are kept in S (long long for small T).
template <typename T>
struct PairSwapTreap {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    struct Pool {  // the node arrays (node 0 = the empty tree), shared with every piece cut from this treap
        vector<T> val{T(0)};  // node 0 is the empty tree
        vector<unsigned long long> pri{0};
        vector<int> L{0}, R{0}, sz{0};
        vector<S> sm{S(0)};
    };
    shared_ptr<Pool> pool;  // (freed with the last treap using it)
    vector<T>& val;
    vector<unsigned long long>& pri;
    vector<int>& L;
    vector<int>& R;
    vector<int>& sz;
    vector<S>& sm;
    int rE = 0, rO = 0;  // the even positions a[0], a[2], ... and the odd ones


    static unsigned long long rnd() {
        static mt19937_64 g(chrono::steady_clock::now().time_since_epoch().count());
        return g();
    }

    // O(N) -- arr: the initial array (may be empty). No reset between test cases: a treap's nodes are freed with it
    explicit PairSwapTreap(const vector<T>& arr = {}) : PairSwapTreap(make_shared<Pool>()) { buildLanes(arr); }

    // O(N) -- a PairSwapTreap over arr that shares other's nodes, so pieces can move between the two (pieces cut from
    // it share them already)
    PairSwapTreap(const vector<T>& arr, const PairSwapTreap& other) : PairSwapTreap(other.pool) { buildLanes(arr); }

    // an empty PairSwapTreap on pool p
    explicit PairSwapTreap(shared_ptr<Pool> p)
        : pool(p), val(p->val), pri(p->pri), L(p->L), R(p->R), sz(p->sz), sm(p->sm) {}

    // O(1) -- the current length of the array
    int size() const { return sz[rE] + sz[rO]; }

    // O(logN) expected -- append v to the end
    void append(T v) { insertAt(size(), v); }

    // O(logN) expected -- insert v at the front (it becomes a[0]; everything else shifts right by one)
    void appendLeft(T v) { insertAt(0, v); }

    // O(logN) expected -- append all of other at the end, leaving it empty (it must share this treap's nodes)
    void concat(PairSwapTreap& other) { paste(size(), other); }

    // O(logN) expected -- remove a[l..r] and return it as a PairSwapTreap of its own (indices from 0; drop it to
    // erase); the tail moves r - l + 1 places, so with an odd count the two tails trade places
    PairSwapTreap cut(int l, int r) {
        int a, b, c, d, e, f;
        parts(l, r, a, b, c, d, e, f);
        if ((r - l + 1) % 2 == 0) rE = merge(a, c), rO = merge(d, f);
        else rE = merge(a, f), rO = merge(d, c);
        PairSwapTreap piece(pool);
        piece.rE = l % 2 == 0 ? b : e, piece.rO = l % 2 == 0 ? e : b;
        return piece;
    }

    // O(N) -- the whole current array, every pending tag applied on the way
    vector<T> getAll() {
        vector<T> ev = inorder(rE), od = inorder(rO), out(ev.size() + od.size());
        for (size_t i = 0; i < ev.size(); i++) out[2 * i] = ev[i];
        for (size_t i = 0; i < od.size(); i++) out[2 * i + 1] = od[i];
        return out;
    }

    // O(logN) expected -- insert v so it becomes a[i] (i <= size()); the tail after it moves one place, so its parity
    // flips: E's tail and O's tail trade places
    void insertAt(int i, T v) {
        int a, b, c, d, e, f, x = newNode(v);
        parts(i, i - 1, a, b, c, d, e, f);
        if (i % 2 == 0) rE = merge(merge(a, x), f), rO = merge(d, c);
        else rE = merge(a, f), rO = merge(merge(d, x), c);
    }

    // O(logN) expected -- insert other so it starts at a[i] (0 <= i <= size()), leaving it empty; it must share this
    // treap's nodes (a piece cut from it, or built with PairSwapTreap(arr, this one)). other's a[0] lands at parity
    // i % 2, and the tail after i moves other's length on: with an odd length the tails trade places
    void paste(int i, PairSwapTreap& other) {
        int a, b, c, d, e, f;
        parts(i, i - 1, a, b, c, d, e, f);
        int x = i % 2 == 0 ? other.rE : other.rO, y = i % 2 == 0 ? other.rO : other.rE;
        if (other.size() % 2) swap(c, f);
        rE = merge(merge(a, x), c), rO = merge(merge(d, y), f);
        other.rE = other.rO = 0;
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

    // O(logN) expected -- a[l] + ... + a[r]
    S rangeSum(int l, int r) {
        int a, b, c, d, e, f;
        parts(l, r, a, b, c, d, e, f);
        S res = sm[b] + sm[e];
        join(a, b, c, d, e, f);
        return res;
    }

    // O(logN) expected -- swap a[l] <-> a[l + 1], a[l + 2] <-> a[l + 3], ... over [l, r] (odd length: a[r] stays):
    // the pairs' even and odd halves are two slices of equal length, which trade places
    void rangeTwinSpin(int l, int r) {
        int k = (r - l + 1) / 2, a, b, c, d, e, f;
        if (!k) return;
        parts(l, l + 2 * k - 1, a, b, c, d, e, f);
        join(a, e, c, d, b, f);
    }

    // O(logN) expected -- (a[0..k-1], a[k..]) as two PairSwapTreaps of their own; this one is left empty
    pair<PairSwapTreap, PairSwapTreap> split(int k) {
        PairSwapTreap left(pool);
        left.rE = rE, left.rO = rO, rE = rO = 0;
        PairSwapTreap right = k < left.size() ? left.cut(k, left.size() - 1) : PairSwapTreap(pool);
        return {left, right};
    }

    // O(logN) expected -- (a[0..l-1], a[l..r], a[r+1..]) as three PairSwapTreaps of their own; this one is left empty
    tuple<PairSwapTreap, PairSwapTreap, PairSwapTreap> trisect(int l, int r) {
        auto [left, right] = split(r + 1);
        auto [first, mid] = left.split(l);
        return {first, mid, right};
    }

    // ---- internals ----

    // E before, E in [l, r], E after, O before, O in [l, r], O after; evens / odds below x: (x + 1) / 2, x / 2
    void parts(int l, int r, int& a, int& b, int& c, int& d, int& e, int& f) {
        int e1 = (l + 1) / 2, e2 = (r + 2) / 2, o1 = l / 2, o2 = (r + 1) / 2;
        split(rE, e1, a, b), split(b, e2 - e1, b, c);
        split(rO, o1, d, e), split(e, o2 - o1, e, f);
    }

    void join(int a, int b, int c, int d, int e, int f) { rE = merge(merge(a, b), c), rO = merge(merge(d, e), f); }

    void buildLanes(const vector<T>& arr) {  // a[0], a[2], ... into E and a[1], a[3], ... into O
        vector<T> ev, od;
        for (size_t i = 0; i < arr.size(); i++) (i % 2 ? od : ev).push_back(arr[i]);
        rE = build(ev), rO = build(od);
    }

    // the node holding a[i], every tag on the way pushed; path (if given) gets the nodes above it
    int find(int i, vector<int>* path = nullptr) {
        int t = i % 2 ? rO : rE, k = i / 2;
        while (true) {
            int ls = sz[L[t]];
            if (k == ls) return t;
            if (path) path->push_back(t);
            if (k < ls) t = L[t];
            else k -= ls + 1, t = R[t];
        }
    }

    vector<T> inorder(int t) {
        vector<T> out;
        vector<int> st;
        while (!st.empty() || t) {
            while (t) st.push_back(t), t = L[t];
            t = st.back(), st.pop_back();
            out.push_back(val[t]);
            t = R[t];
        }
        return out;
    }

    int newNode(T v) {
        val.push_back(v), pri.push_back(rnd()), L.push_back(0), R.push_back(0), sz.push_back(1);
        sm.push_back(S(v));
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

    void pull(int x) {
        int l = L[x], r = R[x];
        sz[x] = sz[l] + sz[r] + 1;
        sm[x] = sm[l] + S(val[x]) + sm[r];
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
};
