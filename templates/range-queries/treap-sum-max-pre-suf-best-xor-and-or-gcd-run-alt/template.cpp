// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/treap-sum-max-pre-suf-best-xor-and-or-gcd-run-alt/template.cpp
// @operations: append appendLeft eraseRange getAll insertAt insertCopiesAt leftmostGtX leftmostGteX leftmostPrefixSumGtX leftmostPrefixSumGteX longestEqualRun maxAltSubseqSum maxPrefixSum maxSubarraySum maxSuffixSum moveRange pointAdd pointAssign pointChmax pointChmin pointGet pop popLeft rangeAndQuery rangeGcd rangeMax rangeOrQuery rangeRotateLeft rangeRotateRight rangeSum rangeXorQuery rightmostGtX rightmostGteX rightmostSuffixSumGtX rightmostSuffixSumGteX
// @data-structure-type: treap
// @complexities:
//   append: log(N)*log(U) expected ?
//   appendLeft: log(N)*log(U) expected ?
//   eraseRange: log(N)*log(U) expected ?
//   getAll: N
//   insertAt: log(N)*log(U) expected ?
//   insertCopiesAt: log(N)*log(U) expected ?
//   leftmostGtX: log(N)*log(U) expected ?
//   leftmostGteX: log(N)*log(U) expected ?
//   leftmostPrefixSumGtX: log(N)*log(U) expected ?
//   leftmostPrefixSumGteX: log(N)*log(U) expected ?
//   longestEqualRun: log(N)*log(U) expected ?
//   maxAltSubseqSum: log(N)*log(U) expected ?
//   maxPrefixSum: log(N)*log(U) expected ?
//   maxSubarraySum: log(N)*log(U) expected ?
//   maxSuffixSum: log(N)*log(U) expected ?
//   moveRange: log(N)*log(U) expected ?
//   pointAdd: log(N)*log(U) expected ?
//   pointAssign: log(N)*log(U) expected ?
//   pointChmax: log(N)*log(U) expected ?
//   pointChmin: log(N)*log(U) expected ?
//   pointGet: log(N) expected
//   pop: log(N)*log(U) expected ?
//   popLeft: log(N)*log(U) expected ?
//   rangeAndQuery: log(N)*log(U) expected ?
//   rangeGcd: log(N)*log(U) expected ?
//   rangeMax: log(N)*log(U) expected ?
//   rangeOrQuery: log(N)*log(U) expected ?
//   rangeRotateLeft: log(N)*log(U) expected ?
//   rangeRotateRight: log(N)*log(U) expected ?
//   rangeSum: log(N)*log(U) expected ?
//   rangeXorQuery: log(N)*log(U) expected ?
//   rightmostGtX: log(N)*log(U) expected ?
//   rightmostGteX: log(N)*log(U) expected ?
//   rightmostSuffixSumGtX: log(N)*log(U) expected ?
//   rightmostSuffixSumGteX: log(N)*log(U) expected ?
//   build: N*log(U) ?
// @memory:
//   layout: none
//   node: val[1*N] sz[1*N] L[1*N] R[1*N] pri[1*N] sm[1*N] mx[1*N] pre[1*N] suf[1*N] best[1*N] xr[1*N] an[1*N] orr[1*N] g[1*N] fv[1*N] lv[1*N] pr[1*N] sr[1*N] br[1*N] a00[1*N] a01[1*N] a10[1*N] a11[1*N]
//   tags: none
//   other: none
//   note: N = every value ever inserted (the initial array plus each insert; erased nodes are not reused)

// Implicit treap with composable aggregates: an array you can insert into / erase from anywhere, rotate, move in
// O(logN) expected each; each node keeps its sum, its max, its best prefix sum, its best suffix sum, its best
// subarray sum, its xor, its AND, its OR, its gcd, its first / last value and the equal runs at its ends and inside,
// its best alternating (+ - + ...) subsequence sum for each start / end sign over its subtree. All indices 0-based,
// ranges inclusive [l, r], an index always the position in the CURRENT array; searches return -1 when nothing
// qualifies.
// T: int, long long, ...; sums are kept in S (long long for small T).
template <typename T>
struct ImplicitTreap {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    static constexpr S NEG = numeric_limits<S>::lowest() / 4;  // (no alternating subsequence of that shape)
    int root = 0;
    vector<T> val{T(0)};
    vector<unsigned long long> pri{0};
    vector<int> L{0}, R{0}, sz{0};
    vector<S> sm{0};
    vector<T> mx{T(0)};
    vector<S> pre{0};
    vector<S> suf{0};
    vector<S> best{0};
    vector<T> xr{T(0)};
    vector<T> an{~T(0)};
    vector<T> orr{T(0)};
    vector<T> g{T(0)};
    vector<T> fv{T(0)};
    vector<T> lv{T(0)};
    vector<int> pr{0};
    vector<int> sr{0};
    vector<int> br{0};
    vector<S> a00{0};
    vector<S> a01{0};
    vector<S> a10{0};
    vector<S> a11{0};

    static unsigned long long rnd() {
        static mt19937_64 g(chrono::steady_clock::now().time_since_epoch().count());
        return g();
    }

    // O(N) -- arr: the initial array (may be empty)
    explicit ImplicitTreap(const vector<T>& arr = {}) { root = build(arr); }

    // O(1) -- the current length of the array
    int size() const { return sz[root]; }

    // O(logN * logU) expected -- append v to the end
    void append(T v) { root = merge(root, newNode(v)); }

    // O(logN * logU) expected -- insert v at the front (it becomes a[0]; everything else shifts right by one)
    void appendLeft(T v) { insertAt(0, v); }

    // O(logN * logU) expected -- remove a[l..r]
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

    // O(logN * logU) expected -- the longest run of equal adjacent values in a[l..r]
    int longestEqualRun(int l, int r) {
        int a, b, c;
        cut(l, r, a, b, c);
        int res = br[b];
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN * logU) expected -- max of +b1 - b2 + b3 - ... over non-empty subsequences b of a[l..r]
    S maxAltSubseqSum(int l, int r) {
        int a, b, c;
        cut(l, r, a, b, c);
        S res = max(a00[b], a01[b]);
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

    // O(logN * logU) expected -- max sum of a non-empty contiguous subarray of a[l..r]
    S maxSubarraySum(int l, int r) {
        int a, b, c;
        cut(l, r, a, b, c);
        S res = best[b];
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

    // O(logN * logU) expected -- cut a[l..r] out, then paste it back so it starts at index i of the array without it
    void moveRange(int l, int r, int i) {
        int a, b, c, x, y;
        cut(l, r, a, b, c);
        split(merge(a, c), i, x, y);
        root = merge(merge(x, b), y);
    }

    // O(logN * logU) expected -- a[i] += v
    void pointAdd(int i, T v) {
        vector<int> path;
        int t = find(i, &path);
        val[t] = val[t] + v;
        pull(t);
        for (int k = (int)path.size() - 1; k >= 0; k--) pull(path[k]);
    }

    // O(logN * logU) expected -- a[i] = v
    void pointAssign(int i, T v) {
        vector<int> path;
        int t = find(i, &path);
        val[t] = v;
        pull(t);
        for (int k = (int)path.size() - 1; k >= 0; k--) pull(path[k]);
    }

    // O(logN * logU) expected -- a[i] = max(a[i], v)
    void pointChmax(int i, T v) {
        vector<int> path;
        int t = find(i, &path);
        val[t] = max(val[t], v);
        pull(t);
        for (int k = (int)path.size() - 1; k >= 0; k--) pull(path[k]);
    }

    // O(logN * logU) expected -- a[i] = min(a[i], v)
    void pointChmin(int i, T v) {
        vector<int> path;
        int t = find(i, &path);
        val[t] = min(val[t], v);
        pull(t);
        for (int k = (int)path.size() - 1; k >= 0; k--) pull(path[k]);
    }

    // O(logN) expected -- a[i]
    T pointGet(int i) { return val[find(i)]; }

    // O(logN * logU) expected -- remove a[i] and return it; everything after it shifts left by one
    T pop(int i) {
        T v = pointGet(i);
        eraseRange(i, i);
        return v;
    }

    // O(logN * logU) expected -- remove a[0] and return it
    T popLeft() { return pop(0); }

    // O(logN * logU) expected -- a[l] & ... & a[r]
    T rangeAndQuery(int l, int r) {
        int a, b, c;
        cut(l, r, a, b, c);
        T res = an[b];
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN * logU) expected -- gcd of |a[l]|, ..., |a[r]|
    T rangeGcd(int l, int r) {
        int a, b, c;
        cut(l, r, a, b, c);
        T res = g[b];
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

    // O(logN * logU) expected -- a[l] | ... | a[r]
    T rangeOrQuery(int l, int r) {
        int a, b, c;
        cut(l, r, a, b, c);
        T res = orr[b];
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN * logU) expected -- cyclic shift a[l..r] left by k (a[l + k] moves to l); any k, negative shifts right
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

    // O(logN * logU) expected -- cyclic shift a[l..r] right by k; any integer k, negative shifts left
    void rangeRotateRight(int l, int r, long long k) { rangeRotateLeft(l, r, -k); }

    // O(logN * logU) expected -- a[l] + ... + a[r]
    S rangeSum(int l, int r) {
        int a, b, c;
        cut(l, r, a, b, c);
        S res = sm[b];
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN * logU) expected -- a[l] ^ ... ^ a[r]
    T rangeXorQuery(int l, int r) {
        int a, b, c;
        cut(l, r, a, b, c);
        T res = xr[b];
        root = merge(merge(a, b), c);
        return res;
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

    // ---- internals ----

    int newNode(T v) {
        val.push_back(v), pri.push_back(rnd()), L.push_back(0), R.push_back(0), sz.push_back(1);
        sm.push_back(S(v)), mx.push_back(v), pre.push_back(S(v)), suf.push_back(S(v)), best.push_back(S(v));
        xr.push_back(v), an.push_back(v), orr.push_back(v), g.push_back(v < T(0) ? T(-v) : v), fv.push_back(v);
        lv.push_back(v), pr.push_back(1), sr.push_back(1), br.push_back(1), a00.push_back(S(v)), a01.push_back(NEG);
        a10.push_back(NEG), a11.push_back(-S(v));
        return (int)val.size() - 1;
    }

    // A's part, then B's: the best alternating sums by (start sign, end sign) = (++, +-, -+, --)
    static array<S, 4> altJoin(const array<S, 4>& A, const array<S, 4>& B) {
        return {max({A[0], B[0], A[0] + B[2], A[1] + B[0]}), max({A[1], B[1], A[0] + B[3], A[1] + B[1]}),
                max({A[2], B[2], A[2] + B[2], A[3] + B[0]}), max({A[3], B[3], A[2] + B[3], A[3] + B[1]})};
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
        mx[x] = v;
        if (l && mx[l] > mx[x]) mx[x] = mx[l];
        if (r && mx[r] > mx[x]) mx[x] = mx[r];
        xr[x] = xr[l] ^ v ^ xr[r];
        an[x] = an[l] & v & an[r];  // (node 0: the AND of nothing, ~0)
        orr[x] = orr[l] | v | orr[r];
        g[x] = gcd(gcd(g[l], v), g[r]);
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
        array<S, 4> c{S(v), NEG, NEG, -S(v)};
        if (l) c = altJoin({a00[l], a01[l], a10[l], a11[l]}, c);
        if (r) c = altJoin(c, {a00[r], a01[r], a10[r], a11[r]});
        a00[x] = c[0], a01[x] = c[1], a10[x] = c[2], a11[x] = c[3];
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
