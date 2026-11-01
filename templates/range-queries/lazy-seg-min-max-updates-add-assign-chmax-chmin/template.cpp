// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/lazy-seg-min-max-updates-add-assign-chmax-chmin/template.cpp
// @operations: getAll leftmostGtX leftmostGteX leftmostLtX leftmostLteX pointAdd pointAssign pointChmax pointChmin pointGet rangeAdd rangeAssign rangeChmax rangeChmin rangeMax rangeMin rightmostGtX rightmostGteX rightmostLtX rightmostLteX
// @data-structure-type: lazy-seg-tree
// @complexities:
//   getAll: N
//   leftmostGtX: log(N)
//   leftmostGteX: log(N)
//   leftmostLtX: log(N)
//   leftmostLteX: log(N)
//   pointAdd: log(N)
//   pointAssign: log(N)
//   pointChmax: log(N)
//   pointChmin: log(N)
//   pointGet: log(N)
//   rangeAdd: log(N)
//   rangeAssign: log(N)
//   rangeChmax: log(N)
//   rangeChmin: log(N)
//   rangeMax: log(N)
//   rangeMin: log(N)
//   rightmostGtX: log(N)
//   rightmostGteX: log(N)
//   rightmostLtX: log(N)
//   rightmostLteX: log(N)
//   build: N
// @memory:
//   layout: 2n-iterative
//   node: mn[2*N] mx[2*N]
//   tags: hi[1*N] lo[1*N] c[1*N]
//   other: none
//   note: leaves [n, 2n) hold each value's own aggregates; tags live on the N internal nodes only

// Lazy segment tree with composable aggregates (2N iterative): range updates (rangeAdd, rangeAssign, rangeChmax,
// rangeChmin) and range queries in O(logN); each node keeps its min, its max over its range. All indices 0-based,
// ranges inclusive [l, r]; searches return -1 when nothing qualifies. Leaves tree[n..2n); a node used by a query or
// update is a perfect subtree of 2^s leaves (s = its level), and every internal node holds its pending tags ("applied
// here, not yet to my children"): an update pushes the tags on its two boundary leaf paths, tags the covering nodes,
// then rebuilds both paths, each node redoing its own pending tag.
// T: int, long long, ...
template <typename T>
struct LazySegTree {
    static constexpr T INF = numeric_limits<T>::max(), NEG = numeric_limits<T>::lowest();
    int n, h;
    vector<T> mn;
    vector<T> mx;
    vector<T> hi;
    vector<T> lo;
    vector<T> c;
    // O(N) -- arr: the initial array (non-empty)
    explicit LazySegTree(const vector<T>& arr) : n((int)arr.size()), h(n ? 32 - __builtin_clz(n) : 0) {
        mn.assign(2 * n, T(0));
        mx.assign(2 * n, T(0));
        hi.assign(n, INF);
        lo.assign(n, NEG);
        c.assign(n, T(0));
        for (int i = 0; i < n; i++) setLeaf(n + i, arr[i]);
        for (int x = n - 1; x > 0; x--) pull(x);
    }

    // O(N) -- the whole array, every pending tag pushed down on the way
    vector<T> getAll() {
        for (int x = 1; x < n; x++) push(x);  // (parents before children)
        vector<T> out(n);
        for (int i = 0; i < n; i++) out[i] = leaf(n + i);
        return out;
    }

    // O(logN) -- the first i in [l, r] with a[i] > x, or -1 (a walk pruned by the node max)
    int leftmostGtX(int l, int r, T x) {
        int ns[64], ls[64], c = cover(l, r, ns, ls);
        for (int i = 0; i < c; i++) {
            int t = ns[i];
            if (!(mx[t] > x)) continue;
            while (t < n) push(t), t = mx[2 * t] > x ? 2 * t : 2 * t + 1;  // walk down the passing node
            return t - n;
        }
        return -1;
    }

    // O(logN) -- the first i in [l, r] with a[i] >= x, or -1 (a walk pruned by the node max)
    int leftmostGteX(int l, int r, T x) {
        int ns[64], ls[64], c = cover(l, r, ns, ls);
        for (int i = 0; i < c; i++) {
            int t = ns[i];
            if (!(mx[t] >= x)) continue;
            while (t < n) push(t), t = mx[2 * t] >= x ? 2 * t : 2 * t + 1;  // walk down the passing node
            return t - n;
        }
        return -1;
    }

    // O(logN) -- the first i in [l, r] with a[i] < x, or -1 (a walk pruned by the node min)
    int leftmostLtX(int l, int r, T x) {
        int ns[64], ls[64], c = cover(l, r, ns, ls);
        for (int i = 0; i < c; i++) {
            int t = ns[i];
            if (!(mn[t] < x)) continue;
            while (t < n) push(t), t = mn[2 * t] < x ? 2 * t : 2 * t + 1;  // walk down the passing node
            return t - n;
        }
        return -1;
    }

    // O(logN) -- the first i in [l, r] with a[i] <= x, or -1 (a walk pruned by the node min)
    int leftmostLteX(int l, int r, T x) {
        int ns[64], ls[64], c = cover(l, r, ns, ls);
        for (int i = 0; i < c; i++) {
            int t = ns[i];
            if (!(mn[t] <= x)) continue;
            while (t < n) push(t), t = mn[2 * t] <= x ? 2 * t : 2 * t + 1;  // walk down the passing node
            return t - n;
        }
        return -1;
    }

    // O(logN) -- a[i] += v
    void pointAdd(int i, T v) {
        int p = i + n;
        pushPath(p);
        setLeaf(p, T(leaf(p) + v)), rebuild(p);
    }

    // O(logN) -- a[i] = v
    void pointAssign(int i, T v) {
        int p = i + n;
        pushPath(p);
        setLeaf(p, v), rebuild(p);
    }

    // O(logN) -- a[i] = max(a[i], v)
    void pointChmax(int i, T v) {
        int p = i + n;
        pushPath(p);
        setLeaf(p, max(leaf(p), v)), rebuild(p);
    }

    // O(logN) -- a[i] = min(a[i], v)
    void pointChmin(int i, T v) {
        int p = i + n;
        pushPath(p);
        setLeaf(p, min(leaf(p), v)), rebuild(p);
    }

    // O(logN) -- a[i]
    T pointGet(int i) {
        int p = i + n;
        pushPath(p);
        return leaf(p);
    }

    // O(logN) -- a[i] += v for i in [l, r]
    void rangeAdd(int l, int r, T v) {
        pushPath(l + n), pushPath(r + n);
        for (int lo = l + n, hi = r + n + 1; lo < hi; lo >>= 1, hi >>= 1) {
            if (lo & 1) applyClamp(lo, INF, NEG, v), lo++;
            if (hi & 1) hi--, applyClamp(hi, INF, NEG, v);
        }
        rebuild(l + n), rebuild(r + n);
    }

    // O(logN) -- a[i] = v for i in [l, r]
    void rangeAssign(int l, int r, T v) {
        pushPath(l + n), pushPath(r + n);
        for (int lo = l + n, hi = r + n + 1; lo < hi; lo >>= 1, hi >>= 1) {
            if (lo & 1) applyClamp(lo, v, v, T(0)), lo++;
            if (hi & 1) hi--, applyClamp(hi, v, v, T(0));
        }
        rebuild(l + n), rebuild(r + n);
    }

    // O(logN) -- a[i] = max(a[i], v) for i in [l, r]
    void rangeChmax(int l, int r, T v) {
        pushPath(l + n), pushPath(r + n);
        for (int lo = l + n, hi = r + n + 1; lo < hi; lo >>= 1, hi >>= 1) {
            if (lo & 1) applyClamp(lo, INF, v, T(0)), lo++;
            if (hi & 1) hi--, applyClamp(hi, INF, v, T(0));
        }
        rebuild(l + n), rebuild(r + n);
    }

    // O(logN) -- a[i] = min(a[i], v) for i in [l, r]
    void rangeChmin(int l, int r, T v) {
        pushPath(l + n), pushPath(r + n);
        for (int lo = l + n, hi = r + n + 1; lo < hi; lo >>= 1, hi >>= 1) {
            if (lo & 1) applyClamp(lo, v, NEG, T(0)), lo++;
            if (hi & 1) hi--, applyClamp(hi, v, NEG, T(0));
        }
        rebuild(l + n), rebuild(r + n);
    }

    // O(logN) -- max of a[l..r]
    T rangeMax(int l, int r) {
        pushPath(l + n), pushPath(r + n);
        T res = numeric_limits<T>::lowest();
        for (int lo = l + n, hi = r + n + 1; lo < hi; lo >>= 1, hi >>= 1) {
            if (lo & 1) res = max(res, mx[lo++]);
            if (hi & 1) res = max(res, mx[--hi]);
        }
        return res;
    }

    // O(logN) -- min of a[l..r]
    T rangeMin(int l, int r) {
        pushPath(l + n), pushPath(r + n);
        T res = numeric_limits<T>::max();
        for (int lo = l + n, hi = r + n + 1; lo < hi; lo >>= 1, hi >>= 1) {
            if (lo & 1) res = min(res, mn[lo++]);
            if (hi & 1) res = min(res, mn[--hi]);
        }
        return res;
    }

    // O(logN) -- the last i in [l, r] with a[i] > x, or -1 (a walk pruned by the node max)
    int rightmostGtX(int l, int r, T x) {
        int ns[64], ls[64], c = cover(l, r, ns, ls);
        for (int i = c - 1; i >= 0; i--) {
            int t = ns[i];
            if (!(mx[t] > x)) continue;
            while (t < n) push(t), t = mx[2 * t + 1] > x ? 2 * t + 1 : 2 * t;  // walk down the passing node
            return t - n;
        }
        return -1;
    }

    // O(logN) -- the last i in [l, r] with a[i] >= x, or -1 (a walk pruned by the node max)
    int rightmostGteX(int l, int r, T x) {
        int ns[64], ls[64], c = cover(l, r, ns, ls);
        for (int i = c - 1; i >= 0; i--) {
            int t = ns[i];
            if (!(mx[t] >= x)) continue;
            while (t < n) push(t), t = mx[2 * t + 1] >= x ? 2 * t + 1 : 2 * t;  // walk down the passing node
            return t - n;
        }
        return -1;
    }

    // O(logN) -- the last i in [l, r] with a[i] < x, or -1 (a walk pruned by the node min)
    int rightmostLtX(int l, int r, T x) {
        int ns[64], ls[64], c = cover(l, r, ns, ls);
        for (int i = c - 1; i >= 0; i--) {
            int t = ns[i];
            if (!(mn[t] < x)) continue;
            while (t < n) push(t), t = mn[2 * t + 1] < x ? 2 * t + 1 : 2 * t;  // walk down the passing node
            return t - n;
        }
        return -1;
    }

    // O(logN) -- the last i in [l, r] with a[i] <= x, or -1 (a walk pruned by the node min)
    int rightmostLteX(int l, int r, T x) {
        int ns[64], ls[64], c = cover(l, r, ns, ls);
        for (int i = c - 1; i >= 0; i--) {
            int t = ns[i];
            if (!(mn[t] <= x)) continue;
            while (t < n) push(t), t = mn[2 * t + 1] <= x ? 2 * t + 1 : 2 * t;  // walk down the passing node
            return t - n;
        }
        return -1;
    }

    // ---- internals ----

    void setLeaf(int p, T v) {  // leaf p holds v alone
        mn[p] = v, mx[p] = v;
    }

    T leaf(int p) const { return T(mn[p]); }  // the value at leaf p

    void pull(int x) {  // recompute node x from its children, then redo its own pending tags
        int a = 2 * x, b = 2 * x + 1;
        mn[x] = min(mn[a], mn[b]);
        mx[x] = max(mx[a], mx[b]);
        if (hi[x] != INF || lo[x] != NEG || c[x] != T(0)) setClamp(x, hi[x], lo[x], c[x]);
    }

    void rebuild(int p) {  // recompute every ancestor of leaf p
        while (p > 1) p >>= 1, pull(p);
    }

    int cover(int l, int r, int* ns, int* ls) {  // the nodes covering a[l..r] left to right (ns) and their levels (ls)
        pushPath(l + n), pushPath(r + n);
        int c = 0, rc = 0, rn[32], rl[32];
        for (int lo = l + n, hi = r + n + 1, s = 0; lo < hi; lo >>= 1, hi >>= 1, s++) {
            if (lo & 1) ns[c] = lo++, ls[c++] = s;
            if (hi & 1) rn[rc] = --hi, rl[rc++] = s;
        }
        while (rc) rc--, ns[c] = rn[rc], ls[c++] = rl[rc];
        return c;
    }

    void setClamp(int x, T H, T Lo, T C) {  // every value v under node x becomes min(H, max(Lo, v + C))
        mn[x] = min(H, max(Lo, mn[x] + C));
        mx[x] = min(H, max(Lo, mx[x] + C));
    }

    void applyClamp(int x, T H, T Lo, T C) {
        setClamp(x, H, Lo, C);
        if (x >= n) return;
        T hh = min(H, max(Lo, (hi[x] == INF ? INF : T(hi[x] + C))));
        lo[x] = min(max(Lo, lo[x] == NEG ? NEG : T(lo[x] + C)), hh);
        hi[x] = hh;
        c[x] += C;
    }

    void push(int x) {  // hand node x's pending tags to its children
        int a = 2 * x, b = 2 * x + 1;
        if (hi[x] != INF || lo[x] != NEG || c[x] != T(0)) {
            applyClamp(a, hi[x], lo[x], c[x]), applyClamp(b, hi[x], lo[x], c[x]);
            hi[x] = INF, lo[x] = NEG, c[x] = T(0);
        }
    }

    void pushPath(int p) {  // hand down every pending tag on the path from the root to leaf p
        for (int s = h; s > 0; s--) push(p >> s);
    }
};
