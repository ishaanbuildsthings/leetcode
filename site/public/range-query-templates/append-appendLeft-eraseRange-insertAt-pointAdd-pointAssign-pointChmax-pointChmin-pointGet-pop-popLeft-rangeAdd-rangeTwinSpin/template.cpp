// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/append-appendLeft-eraseRange-insertAt-pointAdd-pointAssign-pointChmax-pointChmin-pointGet-pop-popLeft-rangeAdd-rangeTwinSpin/template.cpp
// @operations: append appendLeft eraseRange getAll insertAt pointAdd pointAssign pointChmax pointChmin pointGet pop popLeft rangeAdd rangeTwinSpin
// @data-structure-type: pair-treap
// @letters: same
// @complexities:
//   append: log(N) expected
//   appendLeft: log(N) expected
//   eraseRange: log(N) expected
//   getAll: N
//   insertAt: log(N) expected
//   pointAdd: log(N) expected
//   pointAssign: log(N) expected
//   pointChmax: log(N) expected
//   pointChmin: log(N) expected
//   pointGet: log(N) expected
//   pop: log(N) expected
//   popLeft: log(N) expected
//   rangeAdd: log(N) expected
//   rangeTwinSpin: log(N) expected
//   build: N
// @memory:
//   layout: none
//   node: val[1*N] sz[1*N] L[1*N] R[1*N] pri[1*N]
//   tags: add[1*N]
//   other: none
//   note: N = every value ever inserted (erased nodes are not reused); two treaps (even / odd positions) share one node pool

// Implicit treap pair: an array you can insert into / erase from anywhere, swap adjacent pairs in a range (a[l] <->
// a[l + 1], a[l + 2] <-> a[l + 3], ...), each in O(logN) expected, plus point ops, rangeAdd. The even positions a[0],
// a[2], ... are one treap (E) and the odd ones another (O), in one node pool; a range [l, r] is a slice of each. All
// indices 0-based, ranges inclusive, always positions in the CURRENT array.
// T: int, long long, ....
template <typename T>
struct PairSwapTreap {
    int rE = 0, rO = 0;  // the even positions a[0], a[2], ... and the odd ones
    vector<T> val{T(0)};  // node 0 is the empty tree
    vector<unsigned long long> pri{0};
    vector<int> L{0}, R{0}, sz{0};
    vector<T> add{T(0)};

    static unsigned long long rnd() {
        static mt19937_64 g(chrono::steady_clock::now().time_since_epoch().count());
        return g();
    }

    // O(N) -- arr: the initial array (may be empty)
    explicit PairSwapTreap(const vector<T>& arr) {
        vector<T> ev, od;
        for (size_t i = 0; i < arr.size(); i++) (i % 2 ? od : ev).push_back(arr[i]);
        rE = build(ev), rO = build(od);
    }

    // O(1) -- the current length of the array
    int size() const { return sz[rE] + sz[rO]; }

    // O(logN) expected -- append v to the end
    void append(T v) { insertAt(size(), v); }

    // O(logN) expected -- insert v at the front (it becomes a[0]; everything else shifts right by one)
    void appendLeft(T v) { insertAt(0, v); }

    // O(logN) expected -- remove a[l..r]; the tail moves r - l + 1 places, so with an odd count the tails trade places
    void eraseRange(int l, int r) {
        int a, b, c, d, e, f;
        parts(l, r, a, b, c, d, e, f);
        if ((r - l + 1) % 2 == 0) rE = merge(a, c), rO = merge(d, f);
        else rE = merge(a, f), rO = merge(d, c);
    }

    // O(N) -- the whole current array, every pending tag applied on the way
    vector<T> getAll() {
        vector<T> ev = inorder(rE), od = inorder(rO), out(ev.size() + od.size());
        for (size_t i = 0; i < ev.size(); i++) out[2 * i] = ev[i];
        for (size_t i = 0; i < od.size(); i++) out[2 * i + 1] = od[i];
        return out;
    }

    // O(logN) expected -- insert v so it becomes a[i] (0 <= i <= size()); the tail after it moves one place, so its parity
    // flips: E's tail and O's tail trade places
    void insertAt(int i, T v) {
        int a, b, c, d, e, f, x = newNode(v);
        parts(i, i - 1, a, b, c, d, e, f);
        if (i % 2 == 0) rE = merge(merge(a, x), f), rO = merge(d, c);
        else rE = merge(a, f), rO = merge(merge(d, x), c);
    }

    // O(logN) expected -- a[i] += v
    void pointAdd(int i, T v) {
        int t = find(i);
        val[t] = val[t] + v;
    }

    // O(logN) expected -- a[i] = v
    void pointAssign(int i, T v) {
        int t = find(i);
        val[t] = v;
    }

    // O(logN) expected -- a[i] = max(a[i], v)
    void pointChmax(int i, T v) {
        int t = find(i);
        val[t] = max(val[t], v);
    }

    // O(logN) expected -- a[i] = min(a[i], v)
    void pointChmin(int i, T v) {
        int t = find(i);
        val[t] = min(val[t], v);
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

    // O(logN) expected -- a[i] += v for i in [l, r]
    void rangeAdd(int l, int r, T v) {
        int a, b, c, d, e, f;
        parts(l, r, a, b, c, d, e, f);
        applyAdd(b, v), applyAdd(e, v);
        join(a, b, c, d, e, f);
    }

    // O(logN) expected -- swap a[l] <-> a[l + 1], a[l + 2] <-> a[l + 3], ... over [l, r] (with an odd length a[r] stays):
    // the pairs' even and odd halves are two slices of equal length, which trade places
    void rangeTwinSpin(int l, int r) {
        int k = (r - l + 1) / 2, a, b, c, d, e, f;
        if (!k) return;
        parts(l, l + 2 * k - 1, a, b, c, d, e, f);
        join(a, e, c, d, b, f);
    }

    // ---- internals ----

    // E before, E in [l, r], E after, O before, O in [l, r], O after; even / odd positions below x: (x + 1) / 2 and x / 2
    void parts(int l, int r, int& a, int& b, int& c, int& d, int& e, int& f) {
        int e1 = (l + 1) / 2, e2 = (r + 2) / 2, o1 = l / 2, o2 = (r + 1) / 2;
        split(rE, e1, a, b), split(b, e2 - e1, b, c);
        split(rO, o1, d, e), split(e, o2 - o1, e, f);
    }

    void join(int a, int b, int c, int d, int e, int f) { rE = merge(merge(a, b), c), rO = merge(merge(d, e), f); }

    // the node holding a[i], every tag on the way pushed; path (if given) gets the nodes above it
    int find(int i, vector<int>* path = nullptr) {
        int t = i % 2 ? rO : rE, k = i / 2;
        while (true) {
            push(t);
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
            while (t) push(t), st.push_back(t), t = L[t];
            t = st.back(), st.pop_back();
            out.push_back(val[t]);
            t = R[t];
        }
        return out;
    }

    int newNode(T v) {
        val.push_back(v), pri.push_back(rnd()), L.push_back(0), R.push_back(0), sz.push_back(1);
        add.push_back(T(0));
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
    }

    void applyAdd(int x, T v) {
        if (!x) return;
        val[x] += v;
        add[x] += v;
    }

    void push(int x) {  // hand x's pending tags to its children
        if (add[x] != T(0)) applyAdd(L[x], add[x]), applyAdd(R[x], add[x]), add[x] = 0;
    }

    void split(int t, int k, int& a, int& b) {  // a = first k of t, b = the rest
        if (!t) { a = b = 0; return; }
        push(t);
        if (sz[L[t]] >= k) split(L[t], k, a, L[t]), b = t;
        else split(R[t], k - sz[L[t]] - 1, R[t], b), a = t;
        pull(t);
    }

    int merge(int a, int b) {  // a's elements, then b's
        if (!a || !b) return a | b;
        if (pri[a] > pri[b]) {
            push(a);
            R[a] = merge(R[a], b);
            pull(a);
            return a;
        }
        push(b);
        L[b] = merge(a, L[b]);
        pull(b);
        return b;
    }
};
