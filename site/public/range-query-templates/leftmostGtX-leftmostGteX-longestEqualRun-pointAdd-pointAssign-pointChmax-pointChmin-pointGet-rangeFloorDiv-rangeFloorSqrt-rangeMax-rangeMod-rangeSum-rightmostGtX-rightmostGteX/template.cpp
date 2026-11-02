// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/leftmostGtX-leftmostGteX-longestEqualRun-pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeFloorDiv-rangeFloorSqrt-rangeMax-rangeMod-rangeSum-rightmostGtX-rightmostGteX/template.cpp
// @operations: getAll leftmostGtX leftmostGteX longestEqualRun pointAdd pointAssign pointChmax pointChmin pointGet rangeFloorDiv rangeFloorSqrt rangeMax rangeMod rangeSum rightmostGtX rightmostGteX
// @data-structure-type: beats
// @complexities:
//   getAll: N
//   leftmostGtX: log(N)
//   leftmostGteX: log(N)
//   longestEqualRun: log(N)
//   pointAdd: log(N)
//   pointAssign: log(N)
//   pointChmax: log(N)
//   pointChmin: log(N)
//   pointGet: log(N)
//   rangeFloorDiv: log(N)*log(U) amortized
//   rangeFloorSqrt: log(N)*log(log(U)) amortized
//   rangeMax: log(N)
//   rangeMod: log(N)*log(U) amortized
//   rangeSum: log(N)
//   rightmostGtX: log(N)
//   rightmostGteX: log(N)
//   build: N
// @memory:
//   layout: 2n-iterative
//   node: sm[2*N] mx[2*N] fv[2*N] lv[2*N] pr[2*N] sr[2*N] br[2*N]
//   tags: none
//   other: none
//   note: leaves [n, 2n) hold each value's own aggregates

// Shrink segment tree with composable aggregates (2N iterative): range updates (rangeFloorDiv, rangeMod,
// rangeFloorSqrt; mod / floor div / floor sqrt walk down every node whose max still changes, and each value can only
// shrink O(logU) times) and range queries in O(logN); each node keeps its sum, its max, its first / last value and
// the equal runs at its ends and inside over its range. All indices 0-based, ranges inclusive [l, r]; searches return
// -1 when nothing qualifies. Leaves tree[n..2n); a node used by a query or update is a perfect subtree of 2^s leaves
// (s = its level); an update rewrites a leaf, then its ancestors.
// T: int, long long, ...; sums are kept in S (long long for small T).
template <typename T>
struct ShrinkSegTree {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    int n, h;
    vector<S> sm;
    vector<T> mx;
    vector<T> fv;
    vector<T> lv;
    vector<int> pr;
    vector<int> sr;
    vector<int> br;

    // O(N) -- arr: the initial array (non-empty)
    explicit ShrinkSegTree(const vector<T>& arr) : n((int)arr.size()), h(n ? 32 - __builtin_clz(n) : 0) {
        sm.assign(2 * n, 0);
        mx.assign(2 * n, T(0));
        fv.assign(2 * n, T(0));
        lv.assign(2 * n, T(0));
        pr.assign(2 * n, 0);
        sr.assign(2 * n, 0);
        br.assign(2 * n, 0);
        for (int i = 0; i < n; i++) setLeaf(n + i, arr[i]);
        for (int x = n - 1; x > 0; x--) {
            int s = 0;
            for (int y = x; y < n; y <<= 1) s++;  // (x's level: down its left edge to the leaves)
            pull(x, s);
        }
    }

    // O(N) -- the whole array
    vector<T> getAll() const {
        vector<T> out(n);
        for (int i = 0; i < n; i++) out[i] = leaf(n + i);
        return out;
    }

    // O(logN) -- the first i in [l, r] with a[i] > x, or -1 (a walk pruned by the node max)
    int leftmostGtX(int l, int r, T x) {
        int ns[64]{}, ls[64]{}, c = cover(l, r, ns, ls);  // (zeroed: l <= r gives at least one node)
        for (int i = 0; i < c; i++) {
            int t = ns[i];
            if (!(mx[t] > x)) continue;
            while (t < n) t = mx[2 * t] > x ? 2 * t : 2 * t + 1;  // walk down the passing node
            return t - n;
        }
        return -1;
    }

    // O(logN) -- the first i in [l, r] with a[i] >= x, or -1 (a walk pruned by the node max)
    int leftmostGteX(int l, int r, T x) {
        int ns[64]{}, ls[64]{}, c = cover(l, r, ns, ls);  // (zeroed: l <= r gives at least one node)
        for (int i = 0; i < c; i++) {
            int t = ns[i];
            if (!(mx[t] >= x)) continue;
            while (t < n) t = mx[2 * t] >= x ? 2 * t : 2 * t + 1;  // walk down the passing node
            return t - n;
        }
        return -1;
    }

    // O(logN) -- the longest run of equal adjacent values in a[l..r]
    int longestEqualRun(int l, int r) {
        int ns[64]{}, ls[64]{}, c = cover(l, r, ns, ls);  // (zeroed: l <= r gives at least one node)
        int t = ns[0], p = pr[t], q = sr[t], res = br[t], k = 1 << ls[0];  // (prefix run, suffix run, best, length)
        T last = lv[t];
        for (int i = 1; i < c; i++) {
            t = ns[i];
            int w = 1 << ls[i];
            bool j = last == fv[t];
            res = max({res, br[t], j ? q + pr[t] : 0});
            if (j && p == k) p += pr[t];
            q = j && sr[t] == w ? q + sr[t] : sr[t];
            k += w, last = lv[t];
        }
        return res;
    }

    // O(logN) -- a[i] += v
    void pointAdd(int i, T v) {
        int p = i + n;
        setLeaf(p, T(leaf(p) + v)), rebuild(p);
    }

    // O(logN) -- a[i] = v
    void pointAssign(int i, T v) {
        int p = i + n;
        setLeaf(p, v), rebuild(p);
    }

    // O(logN) -- a[i] = max(a[i], v)
    void pointChmax(int i, T v) {
        int p = i + n;
        setLeaf(p, max(leaf(p), v)), rebuild(p);
    }

    // O(logN) -- a[i] = min(a[i], v)
    void pointChmin(int i, T v) {
        int p = i + n;
        setLeaf(p, min(leaf(p), v)), rebuild(p);
    }

    // O(logN) -- a[i]
    T pointGet(int i) {
        int p = i + n;
        return leaf(p);
    }

    // amortized O(logN * logU) -- a[i] //= x for i in [l, r] (values >= 0; x >= 2, x = 1 does nothing)
    void rangeFloorDiv(int l, int r, T x) {
        if (x >= 2) shrinkRange(l, r, T(1), [x](T v) { return T(v / x); });
    }

    // amortized O(logN * loglogU) -- a[i] = floor(sqrt(a[i])) for i in [l, r] (values >= 0)
    void rangeFloorSqrt(int l, int r) {
        shrinkRange(l, r, T(2), isqrtT);
    }

    // O(logN) -- max of a[l..r]
    T rangeMax(int l, int r) {
        T res = numeric_limits<T>::lowest();
        for (int lo = l + n, hi = r + n + 1; lo < hi; lo >>= 1, hi >>= 1) {
            if (lo & 1) res = max(res, mx[lo++]);
            if (hi & 1) res = max(res, mx[--hi]);
        }
        return res;
    }

    // amortized O(logN * logU) -- a[i] %= x for i in [l, r] (values >= 0, x >= 1)
    void rangeMod(int l, int r, T x) {
        if (x >= 1) shrinkRange(l, r, x, [x](T v) { return T(v % x); });
    }

    // O(logN) -- a[l] + ... + a[r]
    S rangeSum(int l, int r) {
        S res = S(0);
        for (int lo = l + n, hi = r + n + 1; lo < hi; lo >>= 1, hi >>= 1) {
            if (lo & 1) res += sm[lo++];
            if (hi & 1) res += sm[--hi];
        }
        return res;
    }

    // O(logN) -- the last i in [l, r] with a[i] > x, or -1 (a walk pruned by the node max)
    int rightmostGtX(int l, int r, T x) {
        int ns[64]{}, ls[64]{}, c = cover(l, r, ns, ls);  // (zeroed: l <= r gives at least one node)
        for (int i = c - 1; i >= 0; i--) {
            int t = ns[i];
            if (!(mx[t] > x)) continue;
            while (t < n) t = mx[2 * t + 1] > x ? 2 * t + 1 : 2 * t;  // walk down the passing node
            return t - n;
        }
        return -1;
    }

    // O(logN) -- the last i in [l, r] with a[i] >= x, or -1 (a walk pruned by the node max)
    int rightmostGteX(int l, int r, T x) {
        int ns[64]{}, ls[64]{}, c = cover(l, r, ns, ls);  // (zeroed: l <= r gives at least one node)
        for (int i = c - 1; i >= 0; i--) {
            int t = ns[i];
            if (!(mx[t] >= x)) continue;
            while (t < n) t = mx[2 * t + 1] >= x ? 2 * t + 1 : 2 * t;  // walk down the passing node
            return t - n;
        }
        return -1;
    }

    // ---- internals ----

    void setLeaf(int p, T v) {  // leaf p holds v alone
        sm[p] = S(v), mx[p] = v, fv[p] = v, lv[p] = v, pr[p] = 1, sr[p] = 1, br[p] = 1;
    }

    T leaf(int p) const { return T(sm[p]); }  // the value at leaf p

    void pull(int x, int s) {  // recompute node x (level s) from its children
        int a = 2 * x, b = 2 * x + 1;
        sm[x] = sm[a] + sm[b];
        mx[x] = max(mx[a], mx[b]);
        int hl = 1 << (s - 1);
        bool j = lv[a] == fv[b];
        br[x] = max({br[a], br[b], j ? sr[a] + pr[b] : 0});
        pr[x] = j && pr[a] == hl ? pr[a] + pr[b] : pr[a];
        sr[x] = j && sr[b] == hl ? sr[b] + sr[a] : sr[b];
        fv[x] = fv[a], lv[x] = lv[b];
    }

    void rebuild(int p) {  // recompute every ancestor of leaf p
        for (int s = 1; p > 1; s++) p >>= 1, pull(p, s);
    }

    int cover(int l, int r, int* ns, int* ls) {  // the nodes covering a[l..r] left to right (ns) and their levels (ls)
        int c = 0, rc = 0, rn[32], rl[32];
        for (int lo = l + n, hi = r + n + 1, s = 0; lo < hi; lo >>= 1, hi >>= 1, s++) {
            if (lo & 1) ns[c] = lo++, ls[c++] = s;
            if (hi & 1) rn[rc] = --hi, rl[rc++] = s;
        }
        while (rc) rc--, ns[c] = rn[rc], ls[c++] = rl[rc];
        return c;
    }

    // floor(sqrt(v)) for v >= 0, exact for every 64-bit value
    static T isqrtT(T v) {
        T r = (T)sqrtl((long double)v);
        while (r > 0 && (__int128)r * r > v) r--;
        while ((__int128)(r + 1) * (r + 1) <= v) r++;
        return r;
    }

    template <class F>
    void shrinkRange(int l, int r, T lim, const F& f) {  // every value v >= lim in a[l..r] becomes f(v)
        for (int lo = l + n, hi = r + n + 1, s = 0; lo < hi; lo >>= 1, hi >>= 1, s++) {
            if (lo & 1) shrink(lo, s, lim, f), lo++;
            if (hi & 1) hi--, shrink(hi, s, lim, f);
        }
        rebuild(l + n), rebuild(r + n);
    }

    template <class F>
    void shrink(int x, int s, T lim, const F& f) {  // every value v >= lim under node x (level s) becomes f(v)
        if (mx[x] < lim) return;
        if (x >= n) { setLeaf(x, f(mx[x])); return; }
        shrink(2 * x, s - 1, lim, f), shrink(2 * x + 1, s - 1, lim, f);
        pull(x, s);
    }
};
