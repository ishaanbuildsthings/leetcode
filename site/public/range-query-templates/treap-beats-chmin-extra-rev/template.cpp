// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/treap-beats-chmin-extra-rev/template.cpp
// @operations: append appendLeft eraseRange getAll insertAt insertCopiesAt leftmostGtX leftmostGteX leftmostLtX leftmostLteX moveRange pointAdd pointAssign pointChmax pointChmin pointGet pop popLeft rangeAssign rangeChmin rangeMax rangeMin rangeReverse rangeRotateLeft rangeRotateRight rangeSum rightmostGtX rightmostGteX rightmostLtX rightmostLteX
// @data-structure-type: treap
// @complexities:
//   append: log(N) expected
//   appendLeft: log(N) expected
//   eraseRange: log(N) expected
//   getAll: N
//   insertAt: log(N) expected
//   insertCopiesAt: log(N) expected
//   leftmostGtX: log(N) expected
//   leftmostGteX: log(N) expected
//   leftmostLtX: log(N) expected
//   leftmostLteX: log(N) expected
//   moveRange: log(N) expected
//   pointAdd: log(N) expected
//   pointAssign: log(N) expected
//   pointChmax: log(N) expected
//   pointChmin: log(N) expected
//   pointGet: log(N) expected
//   pop: log(N) expected
//   popLeft: log(N) expected
//   rangeAssign: log(N) expected
//   rangeChmin: log(N) amortized ?
//   rangeMax: log(N) expected
//   rangeMin: log(N) expected
//   rangeReverse: log(N) expected
//   rangeRotateLeft: log(N) expected
//   rangeRotateRight: log(N) expected
//   rangeSum: log(N) expected
//   rightmostGtX: log(N) expected
//   rightmostGteX: log(N) expected
//   rightmostLtX: log(N) expected
//   rightmostLteX: log(N) expected
//   build: N
// @memory:
//   layout: none
//   node: val[1*N] sz[1*N] L[1*N] R[1*N] pri[1*N] sm[1*N] mx[1*N] mx2[1*N] cmx[1*N] mn[1*N]
//   tags: rev[1*N]
//   other: none
//   note: N = every value ever inserted; no chmin / chmax / assign tags: a node's own max / min are its pending clamp, and a node whose values are all equal pushes that value as an assign

// Implicit treap with segment tree beats: range chmin (a[i] = min(a[i], x)) and range assign with range sums, the
// range max, the range min, on an array you can insert into / erase from anywhere, reverse, rotate, move. Each node
// keeps its max, strict second max and copies of the max over its subtree (its own value included), plus the sum. A
// chmin x stops at a node with second max < x: only the copies of the max move (the sum drops by (max - x) * copies).
// A node's own max / min double as its pending clamp: push clamps each child to them, so there are no chmin / chmax
// tags; and when all of a node's values are equal, push hands that value to both children as an assign, so there is
// no assign tag. All indices 0-based, ranges inclusive [l, r], an index always the position in the CURRENT array;
// searches return -1 when nothing qualifies.
// T: int, long long, ...; sums are kept in S (long long for small T).
template <typename T>
struct ImplicitTreap {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    static constexpr T INF = numeric_limits<T>::max(), NEG = numeric_limits<T>::lowest();  // (no second max / min)
    int root = 0;
    vector<T> val{T(0)};
    vector<unsigned long long> pri{0};
    vector<int> L{0}, R{0}, sz{0};
    vector<S> sm{0};
    vector<T> mx{T(0)};
    vector<T> mx2{NEG};
    vector<int> cmx{0};
    vector<T> mn{T(0)};
    vector<char> rev{0};

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
            while (t) push(t), st.push_back(t), t = L[t];
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

    // O(logN) expected -- the first i in [l, r] with a[i] > x, or -1 (a walk pruned by the subtree max)
    int leftmostGtX(int l, int r, T x) {
        int a, b, c;
        cut(l, r, a, b, c);
        int t = b, i = 0, res = -1;
        if (t && mx[t] > x) {  // some value in a[l..r] passes
            while (true) {
                push(t);
                if (L[t] && mx[L[t]] > x) t = L[t];
                else if (val[t] > x) { res = l + i + sz[L[t]]; break; }
                else i += sz[L[t]] + 1, t = R[t];
            }
        }
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN) expected -- the first i in [l, r] with a[i] >= x, or -1 (a walk pruned by the subtree max)
    int leftmostGteX(int l, int r, T x) {
        int a, b, c;
        cut(l, r, a, b, c);
        int t = b, i = 0, res = -1;
        if (t && mx[t] >= x) {  // some value in a[l..r] passes
            while (true) {
                push(t);
                if (L[t] && mx[L[t]] >= x) t = L[t];
                else if (val[t] >= x) { res = l + i + sz[L[t]]; break; }
                else i += sz[L[t]] + 1, t = R[t];
            }
        }
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN) expected -- the first i in [l, r] with a[i] < x, or -1 (a walk pruned by the subtree min)
    int leftmostLtX(int l, int r, T x) {
        int a, b, c;
        cut(l, r, a, b, c);
        int t = b, i = 0, res = -1;
        if (t && mn[t] < x) {  // some value in a[l..r] passes
            while (true) {
                push(t);
                if (L[t] && mn[L[t]] < x) t = L[t];
                else if (val[t] < x) { res = l + i + sz[L[t]]; break; }
                else i += sz[L[t]] + 1, t = R[t];
            }
        }
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN) expected -- the first i in [l, r] with a[i] <= x, or -1 (a walk pruned by the subtree min)
    int leftmostLteX(int l, int r, T x) {
        int a, b, c;
        cut(l, r, a, b, c);
        int t = b, i = 0, res = -1;
        if (t && mn[t] <= x) {  // some value in a[l..r] passes
            while (true) {
                push(t);
                if (L[t] && mn[L[t]] <= x) t = L[t];
                else if (val[t] <= x) { res = l + i + sz[L[t]]; break; }
                else i += sz[L[t]] + 1, t = R[t];
            }
        }
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

    // O(logN) expected -- a[i] = v for i in [l, r]
    void rangeAssign(int l, int r, T v) {
        int a, b, c;
        cut(l, r, a, b, c);
        applyAssign(b, v);
        root = merge(merge(a, b), c);
    }

    // amortized O(logN) expected -- a[i] = min(a[i], v) for i in [l, r]
    void rangeChmin(int l, int r, T v) {
        int a, b, c;
        cut(l, r, a, b, c);
        chmin(b, v);
        root = merge(merge(a, b), c);
    }

    // O(logN) expected -- max of a[l..r]
    T rangeMax(int l, int r) {
        int a, b, c;
        cut(l, r, a, b, c);
        T res = mx[b];
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN) expected -- min of a[l..r]
    T rangeMin(int l, int r) {
        int a, b, c;
        cut(l, r, a, b, c);
        T res = mn[b];
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN) expected -- reverse a[l..r] in place
    void rangeReverse(int l, int r) {
        int a, b, c;
        cut(l, r, a, b, c);
        applyRev(b);
        root = merge(merge(a, b), c);
    }

    // O(logN) expected -- cyclic shift a[l..r] left by k (a[l + k] moves to l); any k, negative shifts right
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

    // O(logN) expected -- the last i in [l, r] with a[i] > x, or -1 (a walk pruned by the subtree max)
    int rightmostGtX(int l, int r, T x) {
        int a, b, c;
        cut(l, r, a, b, c);
        int t = b, i = 0, res = -1;
        if (t && mx[t] > x) {  // some value in a[l..r] passes
            while (true) {
                push(t);
                if (R[t] && mx[R[t]] > x) i += sz[L[t]] + 1, t = R[t];
                else if (val[t] > x) { res = l + i + sz[L[t]]; break; }
                else t = L[t];
            }
        }
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN) expected -- the last i in [l, r] with a[i] >= x, or -1 (a walk pruned by the subtree max)
    int rightmostGteX(int l, int r, T x) {
        int a, b, c;
        cut(l, r, a, b, c);
        int t = b, i = 0, res = -1;
        if (t && mx[t] >= x) {  // some value in a[l..r] passes
            while (true) {
                push(t);
                if (R[t] && mx[R[t]] >= x) i += sz[L[t]] + 1, t = R[t];
                else if (val[t] >= x) { res = l + i + sz[L[t]]; break; }
                else t = L[t];
            }
        }
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN) expected -- the last i in [l, r] with a[i] < x, or -1 (a walk pruned by the subtree min)
    int rightmostLtX(int l, int r, T x) {
        int a, b, c;
        cut(l, r, a, b, c);
        int t = b, i = 0, res = -1;
        if (t && mn[t] < x) {  // some value in a[l..r] passes
            while (true) {
                push(t);
                if (R[t] && mn[R[t]] < x) i += sz[L[t]] + 1, t = R[t];
                else if (val[t] < x) { res = l + i + sz[L[t]]; break; }
                else t = L[t];
            }
        }
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN) expected -- the last i in [l, r] with a[i] <= x, or -1 (a walk pruned by the subtree min)
    int rightmostLteX(int l, int r, T x) {
        int a, b, c;
        cut(l, r, a, b, c);
        int t = b, i = 0, res = -1;
        if (t && mn[t] <= x) {  // some value in a[l..r] passes
            while (true) {
                push(t);
                if (R[t] && mn[R[t]] <= x) i += sz[L[t]] + 1, t = R[t];
                else if (val[t] <= x) { res = l + i + sz[L[t]]; break; }
                else t = L[t];
            }
        }
        root = merge(merge(a, b), c);
        return res;
    }

    // ---- internals ----

    int newNode(T v) {
        val.push_back(v), pri.push_back(rnd()), L.push_back(0), R.push_back(0), sz.push_back(1);
        sm.push_back(S(v)), mx.push_back(v), mn.push_back(v), mx2.push_back(NEG), cmx.push_back(1), rev.push_back(0);
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

    void pull(int x) {  // recompute x from its children (its own value is one more value of the subtree)
        int l = L[x], r = R[x];
        sz[x] = sz[l] + sz[r] + 1;
        T v = val[x];
        sm[x] = sm[l] + S(v) + sm[r];
        {
            T m = v, m2 = NEG;
            int k = 1;
            for (int y : {l, r}) {
                if (!y) continue;
                T a = mx[y], a2 = mx2[y];
                if (a > m) m2 = a2 > m ? a2 : m, m = a, k = cmx[y];
                else if (a == m) k += cmx[y], m2 = a2 > m2 ? a2 : m2;
                else if (a > m2) m2 = a;
            }
            mx[x] = m, mx2[x] = m2, cmx[x] = k;
        }
        mn[x] = v;
        if (l && mn[l] < mn[x]) mn[x] = mn[l];
        if (r && mn[r] < mn[x]) mn[x] = mn[r];
    }

    void applyAssign(int t, T v) {  // every value of t's subtree becomes v
        if (!t) return;
        int n = sz[t];
        val[t] = v, sm[t] = S(v) * n;
        mx[t] = v;
        mn[t] = v;
        mx2[t] = NEG, cmx[t] = n;
    }

    void applyChmin(int t, T v) {  // chmin by v on t, with mx2 < v < mx: only the copies of the max move
        if (mx2[t] == NEG) { applyAssign(t, v); return; }  // (all equal)
        if (val[t] == mx[t]) val[t] = v;
        sm[t] -= S(mx[t] - v) * cmx[t];
        mx[t] = v;
    }

    void chmin(int t, T x) {  // a[i] = min(a[i], x) over t's subtree, walking down only where x <= the second max
        if (!t || mx[t] <= x) return;
        if (mx2[t] < x) { applyChmin(t, x); return; }
        push(t);
        if (val[t] > x) val[t] = x;
        chmin(L[t], x), chmin(R[t], x);
        pull(t);
    }

    void applyRev(int x) {  // reverse x's subtree (every kept aggregate reads the same both ways)
        if (x) swap(L[x], R[x]), rev[x] ^= 1;
    }

    void push(int t) {  // hand t's pending changes to its children: all one value (an assign), else the add, then its clamp
        int l = L[t], r = R[t];
        if (rev[t]) applyRev(l), applyRev(r), rev[t] = 0;
        if (mx2[t] == NEG) {
            applyAssign(l, mx[t]), applyAssign(r, mx[t]);
            return;
        }
        for (int y : {l, r})
            if (y && mx[y] > mx[t]) applyChmin(y, mx[t]);
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

    void cut(int l, int r, int& a, int& b, int& c) {  // a[0..l-1], a[l..r], a[r+1..]
        split(root, l, a, b);
        split(b, r - l + 1, b, c);
    }

    int find(int i, vector<int>* path = nullptr) {  // the node holding a[i], every tag on the way pushed
        int t = root;
        while (true) {
            push(t);
            int ls = sz[L[t]];
            if (i == ls) return t;
            if (path) path->push_back(t);
            if (i < ls) t = L[t];
            else i -= ls + 1, t = R[t];
        }
    }
};
