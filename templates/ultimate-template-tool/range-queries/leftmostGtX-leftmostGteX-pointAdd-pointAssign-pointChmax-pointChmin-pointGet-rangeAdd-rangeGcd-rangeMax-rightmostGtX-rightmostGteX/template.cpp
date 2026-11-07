// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/leftmostGtX-leftmostGteX-pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAdd-rangeGcd-rangeMax-rightmostGtX-rightmostGteX/template.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: gcdAll getAll leftmostGtX leftmostGteX maxAll pointAdd pointAssign pointChmax pointChmin pointGet rangeAdd rangeGcd rangeMax rightmostGtX rightmostGteX
// @data-structure-type: lazy-seg-tree
// @complexities:
//   getAll: N
//   leftmostGtX: log(N)
//   leftmostGteX: log(N)
//   pointAdd: log(N)*log(U) ?
//   pointAssign: log(N)*log(U) ?
//   pointChmax: log(N)*log(U) ?
//   pointChmin: log(N)*log(U) ?
//   pointGet: log(N)
//   rangeAdd: log(N)*log(U) ?
//   rangeGcd: log(N)+log(U) ?
//   rangeMax: log(N)
//   rightmostGtX: log(N)
//   rightmostGteX: log(N)
//   maxAll: log(N)
//   gcdAll: log(N)+log(U) ?
//   build: N*log(U) ?
// @memory:
//   layout: 2n-iterative
//   node: mx[2*N] g[2*N] fv[2*N] lv[2*N]
//   tags: add[1*N]
//   other: none
//   note: leaves [n, 2n) hold each value's own aggregates; tags live on the N internal nodes only

// Lazy segment tree with composable aggregates (2N iterative): range updates (rangeAdd) and range queries in O(logN);
// each node keeps its max, its gcd over its range. All indices 0-based, ranges inclusive [l, r]; searches return -1
// when nothing qualifies. Leaves tree[n..2n); a node used by a query or update is a perfect subtree of 2^s leaves (s
// = its level), and every internal node holds its pending tags ("applied here, not yet to my children"): an update
// pushes the tags on its two boundary leaf paths, tags the covering nodes, then rebuilds both paths, each node
// redoing its own pending tag.
// T: int, long long, ...
template <typename T>
struct LazySegTree {
    int n, h;
    vector<T> mx;
    vector<T> g;
    vector<T> fv;
    vector<T> lv;
    vector<T> add;

    // O(N log U) -- arr: the initial array (non-empty)
    explicit LazySegTree(const vector<T>& arr) : n((int)arr.size()), h(n ? 32 - __builtin_clz(n) : 0) {
        mx.assign(2 * n, T(0));
        g.assign(2 * n, T(0));
        fv.assign(2 * n, T(0));
        lv.assign(2 * n, T(0));
        add.assign(n, T(0));
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

    // O(logN) -- the first i in [l, r] with a[i] > x, or -1 (a walk pruned by the node max); needs 0 <= l <= r < n,
    // else throws out_of_range
    int leftmostGtX(int l, int r, T x) {
        if (l < 0 || l > r || r >= n) throw out_of_range("leftmostGtX: needs 0 <= l <= r < n");
        int ns[64]{}, ls[64]{}, c = cover(l, r, ns, ls);  // (zeroed: l <= r gives at least one node)
        for (int i = 0; i < c; i++) {
            int t = ns[i];
            if (!(mx[t] > x)) continue;
            while (t < n) push(t), t = mx[2 * t] > x ? 2 * t : 2 * t + 1;  // walk down the passing node
            return t - n;
        }
        return -1;
    }

    // O(logN) -- the first i in [l, r] with a[i] >= x, or -1 (a walk pruned by the node max); needs 0 <= l <= r < n,
    // else throws out_of_range
    int leftmostGteX(int l, int r, T x) {
        if (l < 0 || l > r || r >= n) throw out_of_range("leftmostGteX: needs 0 <= l <= r < n");
        int ns[64]{}, ls[64]{}, c = cover(l, r, ns, ls);  // (zeroed: l <= r gives at least one node)
        for (int i = 0; i < c; i++) {
            int t = ns[i];
            if (!(mx[t] >= x)) continue;
            while (t < n) push(t), t = mx[2 * t] >= x ? 2 * t : 2 * t + 1;  // walk down the passing node
            return t - n;
        }
        return -1;
    }

    // O(logN * logU) -- a[i] += v; needs 0 <= i < n, else throws out_of_range
    void pointAdd(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointAdd: needs 0 <= i < n");
        int p = i + n;
        pushPath(p);
        setLeaf(p, T(leaf(p) + v)), rebuild(p);
    }

    // O(logN * logU) -- a[i] = v; needs 0 <= i < n, else throws out_of_range
    void pointAssign(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointAssign: needs 0 <= i < n");
        int p = i + n;
        pushPath(p);
        setLeaf(p, v), rebuild(p);
    }

    // O(logN * logU) -- a[i] = max(a[i], v); needs 0 <= i < n, else throws out_of_range
    void pointChmax(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointChmax: needs 0 <= i < n");
        int p = i + n;
        pushPath(p);
        setLeaf(p, max(leaf(p), v)), rebuild(p);
    }

    // O(logN * logU) -- a[i] = min(a[i], v); needs 0 <= i < n, else throws out_of_range
    void pointChmin(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointChmin: needs 0 <= i < n");
        int p = i + n;
        pushPath(p);
        setLeaf(p, min(leaf(p), v)), rebuild(p);
    }

    // O(logN) -- a[i]; needs 0 <= i < n, else throws out_of_range
    T pointGet(int i) {
        if (i < 0 || i >= n) throw out_of_range("pointGet: needs 0 <= i < n");
        int p = i + n;
        pushPath(p);
        return leaf(p);
    }

    // O(logN * logU) -- a[i] += v for i in [l, r]; needs 0 <= l <= r < n, else throws out_of_range
    void rangeAdd(int l, int r, T v) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeAdd: needs 0 <= l <= r < n");
        pushPath(l + n), pushPath(r + n);
        for (int lo = l + n, hi = r + n + 1; lo < hi; lo >>= 1, hi >>= 1) {
            if (lo & 1) applyAdd(lo, v), lo++;
            if (hi & 1) hi--, applyAdd(hi, v);
        }
        rebuild(l + n), rebuild(r + n);
    }

    // O(logN + logU) -- gcd of |a[l]|, ..., |a[r]|; needs 0 <= l <= r < n, else throws out_of_range
    T rangeGcd(int l, int r) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeGcd: needs 0 <= l <= r < n");
        int ns[64]{}, ls[64]{}, c = cover(l, r, ns, ls);  // (zeroed: l <= r gives at least one node)
        T res = gcd(fv[ns[0]], g[ns[0]]), last = lv[ns[0]];  // the first value, then every adjacent difference
        for (int i = 1; i < c; i++) res = gcd(gcd(res, T(fv[ns[i]] - last)), g[ns[i]]), last = lv[ns[i]];
        return res;
    }

    // O(logN) -- max of a[l..r]; needs 0 <= l <= r < n, else throws out_of_range
    T rangeMax(int l, int r) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeMax: needs 0 <= l <= r < n");
        pushPath(l + n), pushPath(r + n);
        T res = numeric_limits<T>::lowest();
        for (int lo = l + n, hi = r + n + 1; lo < hi; lo >>= 1, hi >>= 1) {
            if (lo & 1) res = max(res, mx[lo++]);
            if (hi & 1) res = max(res, mx[--hi]);
        }
        return res;
    }

    // O(logN) -- the last i in [l, r] with a[i] > x, or -1 (a walk pruned by the node max); needs 0 <= l <= r < n,
    // else throws out_of_range
    int rightmostGtX(int l, int r, T x) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rightmostGtX: needs 0 <= l <= r < n");
        int ns[64]{}, ls[64]{}, c = cover(l, r, ns, ls);  // (zeroed: l <= r gives at least one node)
        for (int i = c - 1; i >= 0; i--) {
            int t = ns[i];
            if (!(mx[t] > x)) continue;
            while (t < n) push(t), t = mx[2 * t + 1] > x ? 2 * t + 1 : 2 * t;  // walk down the passing node
            return t - n;
        }
        return -1;
    }

    // O(logN) -- the last i in [l, r] with a[i] >= x, or -1 (a walk pruned by the node max); needs 0 <= l <= r < n,
    // else throws out_of_range
    int rightmostGteX(int l, int r, T x) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rightmostGteX: needs 0 <= l <= r < n");
        int ns[64]{}, ls[64]{}, c = cover(l, r, ns, ls);  // (zeroed: l <= r gives at least one node)
        for (int i = c - 1; i >= 0; i--) {
            int t = ns[i];
            if (!(mx[t] >= x)) continue;
            while (t < n) push(t), t = mx[2 * t + 1] >= x ? 2 * t + 1 : 2 * t;  // walk down the passing node
            return t - n;
        }
        return -1;
    }

    // O(log(N)) -- max of the whole array a[0..n-1] (rangeMax(0, n - 1)); needs n >= 1, else throws out_of_range
    auto maxAll() {
        if (n < 1) throw out_of_range("maxAll: needs n >= 1");
        return rangeMax(0, n - 1);
    }

    // O(log(N)+log(U) ?) -- gcd of the whole array a[0..n-1] (rangeGcd(0, n - 1)); needs n >= 1, else throws out_of_range
    auto gcdAll() {
        if (n < 1) throw out_of_range("gcdAll: needs n >= 1");
        return rangeGcd(0, n - 1);
    }

    // ---- internals ----

    void setLeaf(int p, T v) {  // leaf p holds v alone
        mx[p] = v, g[p] = T(0), fv[p] = v, lv[p] = v;
    }

    T leaf(int p) const { return T(mx[p]); }  // the value at leaf p

    void pull(int x) {  // recompute node x from its children, then redo its own pending tags
        int a = 2 * x, b = 2 * x + 1;
        mx[x] = max(mx[a], mx[b]);
        g[x] = gcd(gcd(g[a], g[b]), T(fv[b] - lv[a]));  // (the adjacent differences)
        fv[x] = fv[a], lv[x] = lv[b];
        if (add[x] != T(0)) setAdd(x, add[x]);
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

    void setAdd(int x, T v) {  // every value under node x gains v
        mx[x] += v;
        fv[x] += v, lv[x] += v;
    }

    void applyAdd(int x, T v) {
        setAdd(x, v);
        if (x < n) add[x] += v;
    }

    void push(int x) {  // hand node x's pending tags to its children
        int a = 2 * x, b = 2 * x + 1;
        if (add[x] != T(0)) applyAdd(a, add[x]), applyAdd(b, add[x]), add[x] = T(0);
    }

    void pushPath(int p) {  // hand down every pending tag on the path from the root to leaf p
        for (int s = h; s > 0; s--) push(p >> s);
    }
};
