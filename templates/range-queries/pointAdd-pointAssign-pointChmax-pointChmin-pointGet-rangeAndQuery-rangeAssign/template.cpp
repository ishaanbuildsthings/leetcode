// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAndQuery-rangeAssign/template.cpp
// @operations: getAll pointAdd pointAssign pointChmax pointChmin pointGet rangeAndQuery rangeAssign
// @data-structure-type: lazy-seg-tree
// @complexities:
//   getAll: N
//   pointAdd: log(N)
//   pointAssign: log(N)
//   pointChmax: log(N)
//   pointChmin: log(N)
//   pointGet: log(N)
//   rangeAndQuery: log(N)
//   rangeAssign: log(N)
//   build: N
// @memory:
//   layout: 2n-iterative
//   node: an[2*N]
//   tags: asg[1*N] hasAsg[1*N]
//   other: none
//   note: leaves [n, 2n) hold each value's own aggregates; tags live on the N internal nodes only

// Lazy segment tree with composable aggregates (2N iterative): range updates (rangeAssign) and range queries in
// O(logN); each node keeps its AND over its range. All indices 0-based, ranges inclusive [l, r]; searches return -1
// when nothing qualifies. Leaves tree[n..2n); a node used by a query or update is a perfect subtree of 2^s leaves (s
// = its level), and every internal node holds its pending tags ("applied here, not yet to my children"): an update
// pushes the tags on its two boundary leaf paths, tags the covering nodes, then rebuilds both paths, each node
// redoing its own pending tag.
// T: int, long long, ...
template <typename T>
struct LazySegTree {
    int n, h;
    vector<T> an;
    vector<T> asg;
    vector<char> hasAsg;
    // O(N) -- arr: the initial array (non-empty)
    explicit LazySegTree(const vector<T>& arr) : n((int)arr.size()), h(n ? 32 - __builtin_clz(n) : 0) {
        an.assign(2 * n, ~T(0));
        asg.assign(n, T(0));
        hasAsg.assign(n, 0);
        for (int i = 0; i < n; i++) an[n + i] = arr[i];
        for (int x = n - 1; x > 0; x--) pull(x);
    }

    // O(N) -- the whole array, every pending tag pushed down on the way
    vector<T> getAll() {
        for (int x = 1; x < n; x++) push(x);  // (parents before children)
        vector<T> out(n);
        for (int i = 0; i < n; i++) out[i] = leaf(n + i);
        return out;
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

    // O(logN) -- a[l] & ... & a[r]
    T rangeAndQuery(int l, int r) {
        pushPath(l + n), pushPath(r + n);
        T res = ~T(0);
        for (int lo = l + n, hi = r + n + 1; lo < hi; lo >>= 1, hi >>= 1) {
            if (lo & 1) res &= an[lo++];
            if (hi & 1) res &= an[--hi];
        }
        return res;
    }

    // O(logN) -- a[i] = v for i in [l, r]
    void rangeAssign(int l, int r, T v) {
        pushPath(l + n), pushPath(r + n);
        for (int lo = l + n, hi = r + n + 1; lo < hi; lo >>= 1, hi >>= 1) {
            if (lo & 1) applyAssign(lo, v), lo++;
            if (hi & 1) hi--, applyAssign(hi, v);
        }
        rebuild(l + n), rebuild(r + n);
    }

    // ---- internals ----

    void setLeaf(int p, T v) {  // leaf p holds v alone
        an[p] = v;
    }

    T leaf(int p) const { return T(an[p]); }  // the value at leaf p

    void pull(int x) {  // recompute node x from its children, then redo its own pending tags
        int a = 2 * x, b = 2 * x + 1;
        an[x] = an[a] & an[b];
        if (hasAsg[x]) setAssign(x, asg[x]);
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

    void setAssign(int x, T v) {  // every value under node x becomes v
        an[x] = v;
    }

    void applyAssign(int x, T v) {
        setAssign(x, v);
        if (x < n) asg[x] = v, hasAsg[x] = 1;
    }

    void push(int x) {  // hand node x's pending tags to its children
        int a = 2 * x, b = 2 * x + 1;
        if (hasAsg[x]) applyAssign(a, asg[x]), applyAssign(b, asg[x]), hasAsg[x] = 0;
    }

    void pushPath(int p) {  // hand down every pending tag on the path from the root to leaf p
        for (int s = h; s > 0; s--) push(p >> s);
    }
};
