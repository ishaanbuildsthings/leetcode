// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeGcd-rangeXorQuery/template.cpp
// @operations: getAll pointAdd pointAssign pointChmax pointChmin pointGet rangeGcd rangeXorQuery
// @data-structure-type: seg-tree
// @complexities:
//   getAll: N
//   pointAdd: log(N)*log(U) ?
//   pointAssign: log(N)*log(U) ?
//   pointChmax: log(N)*log(U) ?
//   pointChmin: log(N)*log(U) ?
//   pointGet: log(N)
//   rangeGcd: log(N)+log(U) ?
//   rangeXorQuery: log(N)
//   build: N*log(U) ?
// @memory:
//   layout: 2n-iterative
//   node: xr[2*N] g[2*N]
//   tags: none
//   other: none
//   note: leaves [n, 2n) hold each value's own aggregates

// Segment tree with composable aggregates (2N iterative): point updates and range queries in O(logN); each node keeps
// its xor, its gcd over its range. All indices 0-based, ranges inclusive [l, r]; searches return -1 when nothing
// qualifies. Leaves tree[n..2n); a node used by a query or update is a perfect subtree of 2^s leaves (s = its level);
// an update rewrites a leaf, then its ancestors.
// T: int, long long, ...
template <typename T>
struct SegTree {
    int n, h;
    vector<T> xr;
    vector<T> g;

    // O(N log U) -- arr: the initial array (non-empty)
    explicit SegTree(const vector<T>& arr) : n((int)arr.size()), h(n ? 32 - __builtin_clz(n) : 0) {
        xr.assign(2 * n, T(0));
        g.assign(2 * n, T(0));
        for (int i = 0; i < n; i++) setLeaf(n + i, arr[i]);
        for (int x = n - 1; x > 0; x--) pull(x);
    }

    // O(N) -- the whole array
    vector<T> getAll() const {
        vector<T> out(n);
        for (int i = 0; i < n; i++) out[i] = leaf(n + i);
        return out;
    }

    // O(logN * logU) -- a[i] += v; needs 0 <= i < n, else throws out_of_range
    void pointAdd(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointAdd: needs 0 <= i < n");
        int p = i + n;
        setLeaf(p, T(leaf(p) + v)), rebuild(p);
    }

    // O(logN * logU) -- a[i] = v; needs 0 <= i < n, else throws out_of_range
    void pointAssign(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointAssign: needs 0 <= i < n");
        int p = i + n;
        setLeaf(p, v), rebuild(p);
    }

    // O(logN * logU) -- a[i] = max(a[i], v); needs 0 <= i < n, else throws out_of_range
    void pointChmax(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointChmax: needs 0 <= i < n");
        int p = i + n;
        setLeaf(p, max(leaf(p), v)), rebuild(p);
    }

    // O(logN * logU) -- a[i] = min(a[i], v); needs 0 <= i < n, else throws out_of_range
    void pointChmin(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointChmin: needs 0 <= i < n");
        int p = i + n;
        setLeaf(p, min(leaf(p), v)), rebuild(p);
    }

    // O(logN) -- a[i]; needs 0 <= i < n, else throws out_of_range
    T pointGet(int i) {
        if (i < 0 || i >= n) throw out_of_range("pointGet: needs 0 <= i < n");
        int p = i + n;
        return leaf(p);
    }

    // O(logN + logU) -- gcd of |a[l]|, ..., |a[r]|; needs 0 <= l <= r < n, else throws out_of_range
    T rangeGcd(int l, int r) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeGcd: needs 0 <= l <= r < n");
        T res = T(0);
        for (int lo = l + n, hi = r + n + 1; lo < hi; lo >>= 1, hi >>= 1) {
            if (lo & 1) res = gcd(res, g[lo++]);
            if (hi & 1) res = gcd(res, g[--hi]);
        }
        return res;
    }

    // O(logN) -- a[l] ^ ... ^ a[r]; needs 0 <= l <= r < n, else throws out_of_range
    T rangeXorQuery(int l, int r) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeXorQuery: needs 0 <= l <= r < n");
        T res = T(0);
        for (int lo = l + n, hi = r + n + 1; lo < hi; lo >>= 1, hi >>= 1) {
            if (lo & 1) res ^= xr[lo++];
            if (hi & 1) res ^= xr[--hi];
        }
        return res;
    }

    // ---- internals ----

    void setLeaf(int p, T v) {  // leaf p holds v alone
        xr[p] = v, g[p] = v;
    }

    T leaf(int p) const { return T(xr[p]); }  // the value at leaf p

    void pull(int x) {  // recompute node x from its children
        int a = 2 * x, b = 2 * x + 1;
        xr[x] = xr[a] ^ xr[b];
        g[x] = gcd(g[a], g[b]);
    }

    void rebuild(int p) {  // recompute every ancestor of leaf p
        while (p > 1) p >>= 1, pull(p);
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
};
