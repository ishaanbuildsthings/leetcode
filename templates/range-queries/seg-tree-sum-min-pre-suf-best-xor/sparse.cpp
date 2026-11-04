// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/seg-tree-sum-min-pre-suf-best-xor/sparse.cpp
// @operations: leftmostLtX leftmostLteX leftmostPrefixSumGtX leftmostPrefixSumGteX maxPrefixSum maxSubarraySum maxSuffixSum pointAdd pointAssign pointChmax pointChmin pointGet rangeMin rangeSum rangeXorQuery rightmostLtX rightmostLteX rightmostSuffixSumGtX rightmostSuffixSumGteX
// @data-structure-type: seg-tree
// @complexities:
//   leftmostLtX: log(U)
//   leftmostLteX: log(U)
//   leftmostPrefixSumGtX: log(U)
//   leftmostPrefixSumGteX: log(U)
//   maxPrefixSum: log(U)
//   maxSubarraySum: log(U)
//   maxSuffixSum: log(U)
//   pointAdd: log(U)
//   pointAssign: log(U)
//   pointChmax: log(U)
//   pointChmin: log(U)
//   pointGet: log(U)
//   rangeMin: log(U)
//   rangeSum: log(U)
//   rangeXorQuery: log(U)
//   rightmostLtX: log(U)
//   rightmostLteX: log(U)
//   rightmostSuffixSumGtX: log(U)
//   rightmostSuffixSumGteX: log(U)
//   build: 1
// @memory:
//   layout: sparse
//   node: sm[4*log(U)] mn[4*log(U)] pre[4*log(U)] suf[4*log(U)] best[4*log(U)] xr[4*log(U)]
//   tags: none
//   other: children[8*log(U)]
//   note: per update, the nodes it visits (at most 4 per level, counting the children a push creates); node data per field, children L / R

// Segment tree with composable aggregates (sparse): any index range [lo, hi] (huge or negative is fine), every
// position starting at 0; point updates and range queries in O(logU), U = hi - lo + 1; each node keeps its sum, its
// min, its best prefix sum, its best suffix sum, its best subarray sum, its xor over its range. Ranges inclusive [l,
// r]; searches return lo - 1 when nothing qualifies. The root covers 2^D >= U positions from lo (the ones past hi are
// zeros nobody reads), so a node of level s covers 2^s positions; children are created on demand as blocks of zeros,
// right before anything descends past a node.
// T: int, long long, ...; sums are kept in S (long long for small T).
template <typename T>
struct SparseSegTree {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    long long first, last;  // the index range [lo, hi]
    int D;  // the root's level: 2^D >= hi - lo + 1
    struct Node {  // a node's fields side by side: a walk reads them together (faster than one array per field)
        S sm = 0;
        S pre = 0;
        S suf = 0;
        S best = 0;
        T mn = T(0);
        T xr = T(0);
        int L = 0;
        int R = 0;
    };
    vector<Node> nd{Node{}};  // node 0: none; node 1 is the root

    // O(1) -- all zeros over [lo, hi]; any long long range works (lo <= hi)
    SparseSegTree(long long lo, long long hi) : first(lo), last(hi),
        D(hi > lo ? 64 - __builtin_clzll((unsigned long long)(hi - lo)) : 0) {
        newZero(D);
    }

    // O(logU) -- the first i in [l, r] with a[i] < x, or lo - 1 (a walk pruned by the node min); needs
    // lo <= l <= r <= hi, else throws out_of_range
    long long leftmostLtX(long long l, long long r, T x) {
        if (l < first || l > r || r > last) throw out_of_range("leftmostLtX: needs lo <= l <= r <= hi");
        int ns[128], ls[128];
        long long ts[128];
        int c = cover(l, r, ns, ls, ts);
        for (int i = 0; i < c; i++) {
            int t = ns[i], s = ls[i];
            long long tl = ts[i];
            if (!(nd[t].mn < x)) continue;
            while (s) {  // walk down the passing node
                kids(t, s);
                s--;
                if (nd[nd[t].L].mn < x) t = nd[t].L;
                else t = nd[t].R, tl += 1LL << s;
            }
            return tl;
        }
        return first - 1;
    }

    // O(logU) -- the first i in [l, r] with a[i] <= x, or lo - 1 (a walk pruned by the node min); needs
    // lo <= l <= r <= hi, else throws out_of_range
    long long leftmostLteX(long long l, long long r, T x) {
        if (l < first || l > r || r > last) throw out_of_range("leftmostLteX: needs lo <= l <= r <= hi");
        int ns[128], ls[128];
        long long ts[128];
        int c = cover(l, r, ns, ls, ts);
        for (int i = 0; i < c; i++) {
            int t = ns[i], s = ls[i];
            long long tl = ts[i];
            if (!(nd[t].mn <= x)) continue;
            while (s) {  // walk down the passing node
                kids(t, s);
                s--;
                if (nd[nd[t].L].mn <= x) t = nd[t].L;
                else t = nd[t].R, tl += 1LL << s;
            }
            return tl;
        }
        return first - 1;
    }

    // O(logU) -- first i in [l, r] with a[l] + ... + a[i] > x, or lo - 1 (a walk pruned by best prefix sums); needs
    // lo <= l <= r <= hi, else throws out_of_range
    long long leftmostPrefixSumGtX(long long l, long long r, T x) {
        if (l < first || l > r || r > last) throw out_of_range("leftmostPrefixSumGtX: needs lo <= l <= r <= hi");
        int ns[128], ls[128];
        long long ts[128];
        int c = cover(l, r, ns, ls, ts);
        S acc = 0;
        for (int i = 0; i < c; i++) {
            int t = ns[i], s = ls[i];
            long long tl = ts[i];
            if (acc + nd[t].pre > S(x)) {
                while (s) {
                    kids(t, s);
                    s--;
                    if (acc + nd[nd[t].L].pre > S(x)) t = nd[t].L;
                    else acc += nd[nd[t].L].sm, t = nd[t].R, tl += 1LL << s;
                }
                return tl;
            }
            acc += nd[t].sm;
        }
        return first - 1;
    }

    // O(logU) -- first i in [l, r] with a[l] + ... + a[i] >= x, or lo - 1 (a walk pruned by best prefix sums); needs
    // lo <= l <= r <= hi, else throws out_of_range
    long long leftmostPrefixSumGteX(long long l, long long r, T x) {
        if (l < first || l > r || r > last) throw out_of_range("leftmostPrefixSumGteX: needs lo <= l <= r <= hi");
        int ns[128], ls[128];
        long long ts[128];
        int c = cover(l, r, ns, ls, ts);
        S acc = 0;
        for (int i = 0; i < c; i++) {
            int t = ns[i], s = ls[i];
            long long tl = ts[i];
            if (acc + nd[t].pre >= S(x)) {
                while (s) {
                    kids(t, s);
                    s--;
                    if (acc + nd[nd[t].L].pre >= S(x)) t = nd[t].L;
                    else acc += nd[nd[t].L].sm, t = nd[t].R, tl += 1LL << s;
                }
                return tl;
            }
            acc += nd[t].sm;
        }
        return first - 1;
    }

    // O(logN) -- max of a[l] + ... + a[i] over i in [l, r]; needs lo <= l <= r <= hi, else throws out_of_range
    S maxPrefixSum(long long l, long long r) {
        if (l < first || l > r || r > last) throw out_of_range("maxPrefixSum: needs lo <= l <= r <= hi");
        int ns[128]{}, ls[128]{}, c = cover(l, r, ns, ls);  // (zeroed: l <= r gives at least one node)
        S res = nd[ns[0]].pre, acc = nd[ns[0]].sm;
        for (int i = 1; i < c; i++) res = max(res, acc + nd[ns[i]].pre), acc += nd[ns[i]].sm;
        return res;
    }

    // O(logN) -- max sum of a non-empty contiguous subarray of a[l..r]; needs lo <= l <= r <= hi, else throws
    // out_of_range
    S maxSubarraySum(long long l, long long r) {
        if (l < first || l > r || r > last) throw out_of_range("maxSubarraySum: needs lo <= l <= r <= hi");
        int ns[128]{}, ls[128]{}, c = cover(l, r, ns, ls);  // (zeroed: l <= r gives at least one node)
        S res = nd[ns[0]].best, q = nd[ns[0]].suf;  // (q: the best sum ending at the right edge so far)
        for (int i = 1; i < c; i++) {
            int t = ns[i];
            res = max({res, nd[t].best, q + nd[t].pre}), q = max(nd[t].suf, nd[t].sm + q);
        }
        return res;
    }

    // O(logN) -- max of a[i] + ... + a[r] over i in [l, r]; needs lo <= l <= r <= hi, else throws out_of_range
    S maxSuffixSum(long long l, long long r) {
        if (l < first || l > r || r > last) throw out_of_range("maxSuffixSum: needs lo <= l <= r <= hi");
        int ns[128]{}, ls[128]{}, c = cover(l, r, ns, ls);  // (zeroed: l <= r gives at least one node)
        S res = nd[ns[c - 1]].suf, acc = nd[ns[c - 1]].sm;
        for (int i = c - 2; i >= 0; i--) res = max(res, acc + nd[ns[i]].suf), acc += nd[ns[i]].sm;
        return res;
    }

    // O(logU) -- a[i] += v; needs lo <= i <= hi, else throws out_of_range
    void pointAdd(long long i, T v) {
        if (i < first || i > last) throw out_of_range("pointAdd: needs lo <= i <= hi");
        int path[64], x = leafOf(i, path);
        setLeaf(x, T(leaf(x) + v)), up(path);
    }

    // O(logU) -- a[i] = v; needs lo <= i <= hi, else throws out_of_range
    void pointAssign(long long i, T v) {
        if (i < first || i > last) throw out_of_range("pointAssign: needs lo <= i <= hi");
        int path[64], x = leafOf(i, path);
        setLeaf(x, v), up(path);
    }

    // O(logU) -- a[i] = max(a[i], v); needs lo <= i <= hi, else throws out_of_range
    void pointChmax(long long i, T v) {
        if (i < first || i > last) throw out_of_range("pointChmax: needs lo <= i <= hi");
        int path[64], x = leafOf(i, path);
        setLeaf(x, max(leaf(x), v)), up(path);
    }

    // O(logU) -- a[i] = min(a[i], v); needs lo <= i <= hi, else throws out_of_range
    void pointChmin(long long i, T v) {
        if (i < first || i > last) throw out_of_range("pointChmin: needs lo <= i <= hi");
        int path[64], x = leafOf(i, path);
        setLeaf(x, min(leaf(x), v)), up(path);
    }

    // O(logU) -- a[i]; needs lo <= i <= hi, else throws out_of_range
    T pointGet(long long i) {
        if (i < first || i > last) throw out_of_range("pointGet: needs lo <= i <= hi");
        int path[64];
        return leaf(leafOf(i, path));
    }

    // O(logU) -- min of a[l..r]; needs lo <= l <= r <= hi, else throws out_of_range
    T rangeMin(long long l, long long r) {
        if (l < first || l > r || r > last) throw out_of_range("rangeMin: needs lo <= l <= r <= hi");
        int ns[128], ls[128], c = cover(l, r, ns, ls);
        T res = numeric_limits<T>::max();
        for (int i = 0; i < c; i++) res = min(res, nd[ns[i]].mn);
        return res;
    }

    // O(logU) -- a[l] + ... + a[r]; needs lo <= l <= r <= hi, else throws out_of_range
    S rangeSum(long long l, long long r) {
        if (l < first || l > r || r > last) throw out_of_range("rangeSum: needs lo <= l <= r <= hi");
        int ns[128], ls[128], c = cover(l, r, ns, ls);
        S res = S(0);
        for (int i = 0; i < c; i++) res += nd[ns[i]].sm;
        return res;
    }

    // O(logU) -- a[l] ^ ... ^ a[r]; needs lo <= l <= r <= hi, else throws out_of_range
    T rangeXorQuery(long long l, long long r) {
        if (l < first || l > r || r > last) throw out_of_range("rangeXorQuery: needs lo <= l <= r <= hi");
        int ns[128], ls[128], c = cover(l, r, ns, ls);
        T res = T(0);
        for (int i = 0; i < c; i++) res ^= nd[ns[i]].xr;
        return res;
    }

    // O(logU) -- the last i in [l, r] with a[i] < x, or lo - 1 (a walk pruned by the node min); needs
    // lo <= l <= r <= hi, else throws out_of_range
    long long rightmostLtX(long long l, long long r, T x) {
        if (l < first || l > r || r > last) throw out_of_range("rightmostLtX: needs lo <= l <= r <= hi");
        int ns[128], ls[128];
        long long ts[128];
        int c = cover(l, r, ns, ls, ts);
        for (int i = c - 1; i >= 0; i--) {
            int t = ns[i], s = ls[i];
            long long tl = ts[i];
            if (!(nd[t].mn < x)) continue;
            while (s) {  // walk down the passing node
                kids(t, s);
                s--;
                if (nd[nd[t].R].mn < x) t = nd[t].R, tl += 1LL << s;
                else t = nd[t].L;
            }
            return tl;
        }
        return first - 1;
    }

    // O(logU) -- the last i in [l, r] with a[i] <= x, or lo - 1 (a walk pruned by the node min); needs
    // lo <= l <= r <= hi, else throws out_of_range
    long long rightmostLteX(long long l, long long r, T x) {
        if (l < first || l > r || r > last) throw out_of_range("rightmostLteX: needs lo <= l <= r <= hi");
        int ns[128], ls[128];
        long long ts[128];
        int c = cover(l, r, ns, ls, ts);
        for (int i = c - 1; i >= 0; i--) {
            int t = ns[i], s = ls[i];
            long long tl = ts[i];
            if (!(nd[t].mn <= x)) continue;
            while (s) {  // walk down the passing node
                kids(t, s);
                s--;
                if (nd[nd[t].R].mn <= x) t = nd[t].R, tl += 1LL << s;
                else t = nd[t].L;
            }
            return tl;
        }
        return first - 1;
    }

    // O(logU) -- last i in [l, r] with a[i] + ... + a[r] > x, or lo - 1 (a walk pruned by best suffix sums); needs
    // lo <= l <= r <= hi, else throws out_of_range
    long long rightmostSuffixSumGtX(long long l, long long r, T x) {
        if (l < first || l > r || r > last) throw out_of_range("rightmostSuffixSumGtX: needs lo <= l <= r <= hi");
        int ns[128], ls[128];
        long long ts[128];
        int c = cover(l, r, ns, ls, ts);
        S acc = 0;
        for (int i = c - 1; i >= 0; i--) {
            int t = ns[i], s = ls[i];
            long long tl = ts[i];
            if (acc + nd[t].suf > S(x)) {
                while (s) {
                    kids(t, s);
                    s--;
                    if (acc + nd[nd[t].R].suf > S(x)) t = nd[t].R, tl += 1LL << s;
                    else acc += nd[nd[t].R].sm, t = nd[t].L;
                }
                return tl;
            }
            acc += nd[t].sm;
        }
        return first - 1;
    }

    // O(logU) -- last i in [l, r] with a[i] + ... + a[r] >= x, or lo - 1 (a walk pruned by best suffix sums); needs
    // lo <= l <= r <= hi, else throws out_of_range
    long long rightmostSuffixSumGteX(long long l, long long r, T x) {
        if (l < first || l > r || r > last) throw out_of_range("rightmostSuffixSumGteX: needs lo <= l <= r <= hi");
        int ns[128], ls[128];
        long long ts[128];
        int c = cover(l, r, ns, ls, ts);
        S acc = 0;
        for (int i = c - 1; i >= 0; i--) {
            int t = ns[i], s = ls[i];
            long long tl = ts[i];
            if (acc + nd[t].suf >= S(x)) {
                while (s) {
                    kids(t, s);
                    s--;
                    if (acc + nd[nd[t].R].suf >= S(x)) t = nd[t].R, tl += 1LL << s;
                    else acc += nd[nd[t].R].sm, t = nd[t].L;
                }
                return tl;
            }
            acc += nd[t].sm;
        }
        return first - 1;
    }

    // ---- internals ----

    int newZero(int s) {  // a new node: a block of 2^s zeros
        Node n;
        n.L = 0, n.R = 0, n.sm = S(0), n.mn = T(0), n.pre = S(0), n.suf = S(0), n.best = S(0), n.xr = T(0);
        nd.push_back(n);
        return (int)nd.size() - 1;
    }

    void kids(int x, int s) {  // create node x's children (blocks of zeros) if it has none yet
        if (nd[x].L) return;
        int a = newZero(s - 1), b = newZero(s - 1);
        nd[x].L = a, nd[x].R = b;
    }

    // the nodes covering a[l..r] left to right: ns, their levels ls, their first indices ts
    int cover(long long l, long long r, int* ns, int* ls, long long* ts) {
        int c = 0;
        collect(1, D, first, l, r, ns, ls, ts, c);
        return c;
    }

    int cover(long long l, long long r, int* ns, int* ls) {
        long long ts[128];
        return cover(l, r, ns, ls, ts);
    }

    void collect(int x, int s, long long tl, long long l, long long r, int* ns, int* ls, long long* ts, int& c) {
        if (l <= tl && tl + (1LL << s) - 1 <= r) {
            ns[c] = x, ls[c] = s, ts[c++] = tl;
            return;
        }
        kids(x, s);
        long long m = tl + (1LL << (s - 1));
        if (l < m) collect(nd[x].L, s - 1, tl, l, r, ns, ls, ts, c);
        if (r >= m) collect(nd[x].R, s - 1, m, l, r, ns, ls, ts, c);
    }

    int leafOf(long long i, int* path) {  // the leaf holding a[i]; path: the nodes above it top-down, every tag pushed
        int x = 1;
        long long tl = first;
        for (int s = D; s > 0; s--) {
            kids(x, s);
            path[D - s] = x;
            if (i >= tl + (1LL << (s - 1))) tl += 1LL << (s - 1), x = nd[x].R;
            else x = nd[x].L;
        }
        return x;
    }

    void up(const int* path) {  // recompute the nodes of path, deepest first (path[k] has level D - k)
        for (int k = D - 1; k >= 0; k--) pull(path[k]);
    }

    void setLeaf(int p, T v) {  // leaf p holds v alone
        nd[p].sm = S(v), nd[p].mn = v, nd[p].pre = S(v), nd[p].suf = S(v), nd[p].best = S(v), nd[p].xr = v;
    }

    T leaf(int p) const { return T(nd[p].sm); }  // the value at leaf p

    void pull(int x) {  // recompute node x from its children
        int a = nd[x].L, b = nd[x].R;
        nd[x].pre = max(nd[a].pre, nd[a].sm + nd[b].pre);
        nd[x].suf = max(nd[b].suf, nd[b].sm + nd[a].suf);
        nd[x].best = max({nd[a].best, nd[b].best, nd[a].suf + nd[b].pre});
        nd[x].sm = nd[a].sm + nd[b].sm;
        nd[x].mn = min(nd[a].mn, nd[b].mn);
        nd[x].xr = nd[a].xr ^ nd[b].xr;
    }
};
