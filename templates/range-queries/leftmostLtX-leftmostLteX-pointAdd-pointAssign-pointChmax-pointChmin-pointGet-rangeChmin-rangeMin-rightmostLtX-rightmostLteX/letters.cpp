// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/leftmostLtX-leftmostLteX-pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeChmin-rangeMin-rightmostLtX-rightmostLteX/letters.cpp
// @operations: getAll leftmostLtX leftmostLteX pointAssign pointChmax pointChmin pointGet rangeChmin rangeMin rightmostLtX rightmostLteX
// @data-structure-type: lazy-seg-tree
// @complexities:
//   getAll: N
//   leftmostLtX: log(N)
//   leftmostLteX: log(N)
//   pointAssign: log(N)
//   pointChmax: log(N)
//   pointChmin: log(N)
//   pointGet: log(N)
//   rangeChmin: log(N)
//   rangeMin: log(N)
//   rightmostLtX: log(N)
//   rightmostLteX: log(N)
//   build: N
// @memory:
//   layout: 2n-iterative
//   node: mn[2*N]
//   tags: hi[1*N]
//   other: none
//   note: leaves [n, 2n) hold each value's own aggregates; tags live on the N internal nodes only

// Letters version: the values are characters (Python: a list of characters, e.g. list(s); C++: T = char), and only the
// operations that make sense on characters are listed.
// Lazy segment tree with composable aggregates (2N iterative): range updates (rangeChmin) and range queries in
// O(logN); each node keeps its min over its range. All indices 0-based, ranges inclusive [l, r]; searches return -1
// when nothing qualifies. Leaves tree[n..2n); a node used by a query or update is a perfect subtree of 2^s leaves (s
// = its level), and every internal node holds its pending tags ("applied here, not yet to my children"): an update
// pushes the tags on its two boundary leaf paths, tags the covering nodes, then rebuilds both paths, each node
// redoing its own pending tag.
// T: int, long long, ...
template <typename T>
struct LazySegTree {
    static constexpr T INF = numeric_limits<T>::max(), NEG = numeric_limits<T>::lowest();
    int n, h;
    vector<T> mn;
    vector<T> hi;

    // O(N) -- arr: the initial array (non-empty)
    explicit LazySegTree(const vector<T>& arr) : n((int)arr.size()), h(n ? 32 - __builtin_clz(n) : 0) {
        mn.assign(2 * n, T(0));
        hi.assign(n, INF);
        for (int i = 0; i < n; i++) mn[n + i] = arr[i];
        for (int x = n - 1; x > 0; x--) pull(x);
    }

    // O(N) -- the whole array, every pending tag pushed down on the way
    vector<T> getAll() {
        for (int x = 1; x < n; x++) push(x);  // (parents before children)
        vector<T> out(n);
        for (int i = 0; i < n; i++) out[i] = leaf(n + i);
        return out;
    }

    // O(logN) -- the first i in [l, r] with a[i] < x, or -1 (a walk pruned by the node min)
    int leftmostLtX(int l, int r, T x) {
        int ns[64]{}, ls[64]{}, c = cover(l, r, ns, ls);  // (zeroed: l <= r gives at least one node)
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
        int ns[64]{}, ls[64]{}, c = cover(l, r, ns, ls);  // (zeroed: l <= r gives at least one node)
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

    // O(logN) -- a[i] = min(a[i], v) for i in [l, r]
    void rangeChmin(int l, int r, T v) {
        pushPath(l + n), pushPath(r + n);
        for (int lo = l + n, hi = r + n + 1; lo < hi; lo >>= 1, hi >>= 1) {
            if (lo & 1) applyClamp(lo, v), lo++;
            if (hi & 1) hi--, applyClamp(hi, v);
        }
        rebuild(l + n), rebuild(r + n);
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

    // O(logN) -- the last i in [l, r] with a[i] < x, or -1 (a walk pruned by the node min)
    int rightmostLtX(int l, int r, T x) {
        int ns[64]{}, ls[64]{}, c = cover(l, r, ns, ls);  // (zeroed: l <= r gives at least one node)
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
        int ns[64]{}, ls[64]{}, c = cover(l, r, ns, ls);  // (zeroed: l <= r gives at least one node)
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
        mn[p] = v;
    }

    T leaf(int p) const { return T(mn[p]); }  // the value at leaf p

    void pull(int x) {  // recompute node x from its children, then redo its own pending tags
        int a = 2 * x, b = 2 * x + 1;
        mn[x] = min(mn[a], mn[b]);
        if (hi[x] != INF) setClamp(x, hi[x]);
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

    void setClamp(int x, T H) {  // every value v under node x becomes min(H, v)
        mn[x] = min(H, mn[x]);
    }

    void applyClamp(int x, T H) {
        setClamp(x, H);
        if (x >= n) return;
        T hh = min(H, hi[x]);
        hi[x] = hh;
    }

    void push(int x) {  // hand node x's pending tags to its children
        int a = 2 * x, b = 2 * x + 1;
        if (hi[x] != INF) {
            applyClamp(a, hi[x]), applyClamp(b, hi[x]);
            hi[x] = INF;
        }
    }

    void pushPath(int p) {  // hand down every pending tag on the path from the root to leaf p
        for (int s = h; s > 0; s--) push(p >> s);
    }
};
