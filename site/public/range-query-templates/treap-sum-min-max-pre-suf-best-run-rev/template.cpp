// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/treap-sum-min-max-pre-suf-best-run-rev/template.cpp
// @operations: append appendLeft cut getAll insertAt insertCopiesAt leftmostGtX leftmostGteX leftmostLtX leftmostLteX leftmostPrefixSumGtX leftmostPrefixSumGteX longestEqualRun maxPrefixSum maxSubarraySum maxSuffixSum merge paste pointAdd pointAssign pointChmax pointChmin pointGet rangeMax rangeMin rangeReverse rangeRotateLeft rangeRotateRight rangeSum rightmostGtX rightmostGteX rightmostLtX rightmostLteX rightmostSuffixSumGtX rightmostSuffixSumGteX split trisect
// @data-structure-type: treap
// @complexities:
//   append: log(N) expected
//   appendLeft: log(N) expected
//   cut: log(N) expected
//   getAll: N
//   insertAt: log(N) expected
//   insertCopiesAt: log(N) expected
//   leftmostGtX: log(N) expected
//   leftmostGteX: log(N) expected
//   leftmostLtX: log(N) expected
//   leftmostLteX: log(N) expected
//   leftmostPrefixSumGtX: log(N) expected
//   leftmostPrefixSumGteX: log(N) expected
//   longestEqualRun: log(N) expected
//   maxPrefixSum: log(N) expected
//   maxSubarraySum: log(N) expected
//   maxSuffixSum: log(N) expected
//   merge: log(N) expected
//   paste: log(N) expected
//   pointAdd: log(N) expected
//   pointAssign: log(N) expected
//   pointChmax: log(N) expected
//   pointChmin: log(N) expected
//   pointGet: log(N) expected
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
//   rightmostSuffixSumGtX: log(N) expected
//   rightmostSuffixSumGteX: log(N) expected
//   split: log(N) expected
//   trisect: log(N) expected
//   build: N
// @memory:
//   layout: none
//   node: val[1*N] sz[1*N] L[1*N] R[1*N] pri[1*N] sm[1*N] mn[1*N] mx[1*N] pre[1*N] suf[1*N] best[1*N] fv[1*N] lv[1*N] pr[1*N] sr[1*N] br[1*N]
//   tags: rev[1*N]
//   other: none
//   note: N = every value ever inserted (the initial array plus each insert; erased nodes are not reused); every ImplicitTreap<T> shares one node pool (pieces move between any of them; nothing to reset)

// Implicit treap with composable aggregates: an array you can insert into anywhere, reverse, rotate, move, cut pieces
// out of (that is how to erase) and paste them back in O(logN) expected each; each node keeps its sum, its min, its
// max, its best prefix sum, its best suffix sum, its best subarray sum, its first / last value and the equal runs at
// its ends and inside over its subtree. All indices 0-based, ranges inclusive [l, r], an index always the position in
// the CURRENT array; searches return -1 when nothing qualifies. Lazy tags mean "already applied to this node, not yet
// to its children".
// T: int, long long, ...; sums are kept in S (long long for small T).
template <typename T>
struct ImplicitTreap {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    // one node pool shared by every ImplicitTreap<T>: cut / paste move nodes between them, so a piece from one can go
    // into any other (node 0 = the empty tree). Nodes are never freed (memory = every value ever inserted, over the
    // whole run), so there is nothing to reset between test cases
    static inline vector<T> val{T(0)};
    static inline vector<unsigned long long> pri{0};
    static inline vector<int> L{0};
    static inline vector<int> R{0};
    static inline vector<int> sz{0};
    static inline vector<S> sm{0};
    static inline vector<T> mn{T(0)};
    static inline vector<T> mx{T(0)};
    static inline vector<S> pre{0};
    static inline vector<S> suf{0};
    static inline vector<S> best{0};
    static inline vector<T> fv{T(0)};
    static inline vector<T> lv{T(0)};
    static inline vector<int> pr{0};
    static inline vector<int> sr{0};
    static inline vector<int> br{0};
    static inline vector<char> rev{0};
    int root = 0;

    // O(N) -- arr: the initial array (leave it out to start empty)
    explicit ImplicitTreap(const vector<T>& arr = {}) { root = build(arr); }

    ImplicitTreap makeEmpty() const { return ImplicitTreap(); }  // (a new, empty one)

    static unsigned long long rnd() {
        static mt19937_64 g(chrono::steady_clock::now().time_since_epoch().count());
        return g();
    }

    // O(1) -- the current length of the array
    int size() const { return sz[root]; }

    // O(logN) expected -- append v to the end
    void append(T v) { root = merge(root, newNode(v)); }

    // O(logN) expected -- insert v at the front (it becomes a[0]; everything else shifts right by one)
    void appendLeft(T v) { insertAt(0, v); }

    // O(logN) expected -- remove a[l..r] and return it as a treap of its own (indices from 0)
    ImplicitTreap cut(int l, int r) {
        int a, b, c;
        cut(l, r, a, b, c);
        root = merge(a, c);
        ImplicitTreap piece = makeEmpty();
        piece.root = b;
        return piece;
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

    // O(logN) expected -- first i in [l, r] with a[l] + ... + a[i] > x, or -1 (a walk pruned by best prefix sums)
    int leftmostPrefixSumGtX(int l, int r, T x) {
        int a, b, c;
        cut(l, r, a, b, c);
        int t = b, i = 0, res = -1;
        S acc = 0;
        if (t && pre[t] > S(x)) {
            while (true) {
                push(t);
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
                push(t);
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

    // O(logN) expected -- the longest run of equal adjacent values in a[l..r]
    int longestEqualRun(int l, int r) {
        int a, b, c;
        cut(l, r, a, b, c);
        int res = br[b];
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

    // O(logN) expected -- max sum of a non-empty contiguous subarray of a[l..r]
    S maxSubarraySum(int l, int r) {
        int a, b, c;
        cut(l, r, a, b, c);
        S res = best[b];
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN) expected -- max of a[i] + ... + a[r] over i in [l, r]
    S maxSuffixSum(int l, int r) {
        int a, b, c;
        cut(l, r, a, b, c);
        S res = suf[b];
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN) expected -- append all of other at the end; other is left empty
    void merge(ImplicitTreap& other) { root = merge(root, other.root), other.root = 0; }

    // O(logN) expected -- insert all of other (any ImplicitTreap, e.g. a cut piece) so it starts at a[i]
    // (0 <= i <= size()); other is left empty
    void paste(int i, ImplicitTreap& other) {
        int a, c;
        split(root, i, a, c);
        root = merge(merge(a, other.root), c);
        other.root = 0;
    }

    // O(logN) expected -- a[i] += v
    void pointAdd(int i, T v) {
        vector<int> path;
        int t = locate(i, &path);
        val[t] = val[t] + v;
        pull(t);
        for (int k = (int)path.size() - 1; k >= 0; k--) pull(path[k]);
    }

    // O(logN) expected -- a[i] = v
    void pointAssign(int i, T v) {
        vector<int> path;
        int t = locate(i, &path);
        val[t] = v;
        pull(t);
        for (int k = (int)path.size() - 1; k >= 0; k--) pull(path[k]);
    }

    // O(logN) expected -- a[i] = max(a[i], v)
    void pointChmax(int i, T v) {
        vector<int> path;
        int t = locate(i, &path);
        val[t] = max(val[t], v);
        pull(t);
        for (int k = (int)path.size() - 1; k >= 0; k--) pull(path[k]);
    }

    // O(logN) expected -- a[i] = min(a[i], v)
    void pointChmin(int i, T v) {
        vector<int> path;
        int t = locate(i, &path);
        val[t] = min(val[t], v);
        pull(t);
        for (int k = (int)path.size() - 1; k >= 0; k--) pull(path[k]);
    }

    // O(logN) expected -- a[i]
    T pointGet(int i) { return val[locate(i)]; }

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

    // O(logN) expected -- cyclic shift a[l..r] left by k (a[l + k] moves to l); k can be huge or negative:
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

    // O(logN) expected -- cyclic shift a[l..r] right by k; k can be huge or negative: it is taken mod the
    // length (negative shifts left)
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

    // O(logN) expected -- last i in [l, r] with a[i] + ... + a[r] > x, or -1 (a walk pruned by best suffix sums)
    int rightmostSuffixSumGtX(int l, int r, T x) {
        int a, b, c;
        cut(l, r, a, b, c);
        int t = b, i = 0, res = -1;
        S acc = 0;
        if (t && suf[t] > S(x)) {
            while (true) {
                push(t);
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

    // O(logN) expected -- last i in [l, r] with a[i] + ... + a[r] >= x, or -1 (a walk pruned by best suffix sums)
    int rightmostSuffixSumGteX(int l, int r, T x) {
        int a, b, c;
        cut(l, r, a, b, c);
        int t = b, i = 0, res = -1;
        S acc = 0;
        if (t && suf[t] >= S(x)) {
            while (true) {
                push(t);
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

    // O(logN) expected -- (a[0..k-1], a[k..]) as two treaps of their own; this one is left empty
    pair<ImplicitTreap, ImplicitTreap> split(int k) {
        ImplicitTreap left = makeEmpty(), right = makeEmpty();
        split(root, k, left.root, right.root);
        root = 0;
        return {left, right};
    }

    // O(logN) expected -- (a[0..l-1], a[l..r], a[r+1..]) as three treaps of their own; this one is left empty
    tuple<ImplicitTreap, ImplicitTreap, ImplicitTreap> trisect(int l, int r) {
        ImplicitTreap left = makeEmpty(), mid = makeEmpty(), right = makeEmpty();
        cut(l, r, left.root, mid.root, right.root);
        root = 0;
        return {left, mid, right};
    }

    // ---- internals ----

    int newNode(T v) {
        val.push_back(v), pri.push_back(rnd()), L.push_back(0), R.push_back(0), sz.push_back(1);
        sm.push_back(S(v)), mn.push_back(v), mx.push_back(v), pre.push_back(S(v)), suf.push_back(S(v));
        best.push_back(S(v)), fv.push_back(v), lv.push_back(v), pr.push_back(1), sr.push_back(1), br.push_back(1);
        rev.push_back(0);
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
        S s = S(v), p = S(v), q = S(v), b = S(v);  // the node alone, then with its left / right parts
        if (l) {
            S ls = sm[l], lp = pre[l], lq = suf[l], lb = best[l];
            S ns = ls + s, np = max(lp, ls + p), nq = max(q, s + lq), nb = max({lb, b, lq + p});
            s = ns, p = np, q = nq, b = nb;
        }
        if (r) {
            S rs = sm[r], rp = pre[r], rq = suf[r], rb = best[r];
            S ns = s + rs, np = max(p, s + rp), nq = max(rq, rs + q), nb = max({b, rb, q + rp});
            s = ns, p = np, q = nq, b = nb;
        }
        sm[x] = s, pre[x] = p, suf[x] = q, best[x] = b;
        mn[x] = v;
        if (l && mn[l] < mn[x]) mn[x] = mn[l];
        if (r && mn[r] < mn[x]) mn[x] = mn[r];
        mx[x] = v;
        if (l && mx[l] > mx[x]) mx[x] = mx[l];
        if (r && mx[r] > mx[x]) mx[x] = mx[r];
        int rp = 1, rq = 1, bb = 1;
        if (l) {
            bool j = lv[l] == v;
            rp = pr[l] + (j && pr[l] == sz[l]);
            rq = j ? sr[l] + 1 : 1;
            bb = max(br[l], rq);
        }
        if (r) {
            bool j = v == fv[r];
            bb = max({bb, br[r], j ? rq + pr[r] : 0});
            if (j && rp == sz[l] + 1) rp += pr[r];
            rq = j && sr[r] == sz[r] ? sr[r] + rq : sr[r];
        }
        pr[x] = rp, sr[x] = rq, br[x] = bb;
        fv[x] = l ? fv[l] : v;
        lv[x] = r ? lv[r] : v;
    }

    void applyRev(int x) {  // reverse x's subtree
        if (!x) return;
        swap(L[x], R[x]), rev[x] ^= 1, swap(pre[x], suf[x]), swap(fv[x], lv[x]), swap(pr[x], sr[x]);
    }

    void push(int x) {  // hand x's pending tags to its children
        if (rev[x]) applyRev(L[x]), applyRev(R[x]), rev[x] = 0;
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

    int locate(int i, vector<int>* path = nullptr) {  // the node holding a[i], every tag on the way pushed
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

// Example (pieces move between treaps; merge appends and leaves its argument empty):
//     ImplicitTreap<int> t({1, 2, 3, 4, 5});
//     auto [left, mid, right] = t.trisect(1, 3);  // left = [1], mid = [2, 3, 4], right = [5]; t is empty now
//     t.merge(right);                             // t = [5]
//     t.merge(mid);                               // t = [5, 2, 3, 4]
//     t.merge(left);                              // t = [5, 2, 3, 4, 1]
