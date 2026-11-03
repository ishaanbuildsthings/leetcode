// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/leftmostPrefixSumGtX-leftmostPrefixSumGteX-maxPrefixSum-pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeGcd-rangeSum/sparse.cpp
// @operations: leftmostPrefixSumGtX leftmostPrefixSumGteX maxPrefixSum pointAdd pointAssign pointChmax pointChmin pointGet rangeGcd rangeSum
// @data-structure-type: seg-tree
// @complexities:
//   leftmostPrefixSumGtX: log(U)
//   leftmostPrefixSumGteX: log(U)
//   maxPrefixSum: log(U)
//   pointAdd: log(U)*log(U) ?
//   pointAssign: log(U)*log(U) ?
//   pointChmax: log(U)*log(U) ?
//   pointChmin: log(U)*log(U) ?
//   pointGet: log(U)
//   rangeGcd: log(U) ?
//   rangeSum: log(U)
//   build: 1
// @memory:
//   layout: sparse
//   node: sm[4*log(U)] pre[4*log(U)] g[4*log(U)]
//   tags: none
//   other: children[8*log(U)]
//   note: per update, the nodes it visits (at most 4 per level, counting the children a push creates); node data per field, children L / R

// Segment tree with composable aggregates (sparse): any index range [lo, hi] (huge or negative is fine), every
// position starting at 0; point updates and range queries in O(logU), U = hi - lo + 1; each node keeps its sum, its
// best prefix sum, its gcd over its range. Ranges inclusive [l, r]; searches return lo - 1 when nothing qualifies.
// The root covers 2^D >= U positions from lo (the ones past hi are zeros nobody reads), so a node of level s covers
// 2^s positions; children are created on demand as blocks of zeros, right before anything descends past a node.
// T: int, long long, ...; sums are kept in S (long long for small T).
template <typename T>
struct SparseSegTree {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    long long first, last;  // the index range [lo, hi]
    int D;  // the root's level: 2^D >= hi - lo + 1
    vector<int> L{0}, R{0};  // children (node 0: none; node 1 is the root)
    vector<S> sm{0};
    vector<S> pre{0};
    vector<T> g{T(0)};

    // O(1) -- all zeros over [lo, hi]; any long long range works (lo <= hi)
    SparseSegTree(long long lo, long long hi) : first(lo), last(hi), D(hi > lo ? 64 - __builtin_clzll((unsigned long long)(hi - lo)) : 0) {
        newZero(D);
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
            if (acc + pre[t] > S(x)) {
                while (s) {
                    kids(t, s);
                    s--;
                    if (acc + pre[L[t]] > S(x)) t = L[t];
                    else acc += sm[L[t]], t = R[t], tl += 1LL << s;
                }
                return tl;
            }
            acc += sm[t];
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
            if (acc + pre[t] >= S(x)) {
                while (s) {
                    kids(t, s);
                    s--;
                    if (acc + pre[L[t]] >= S(x)) t = L[t];
                    else acc += sm[L[t]], t = R[t], tl += 1LL << s;
                }
                return tl;
            }
            acc += sm[t];
        }
        return first - 1;
    }

    // O(logN) -- max of a[l] + ... + a[i] over i in [l, r]; needs lo <= l <= r <= hi, else throws out_of_range
    S maxPrefixSum(long long l, long long r) {
        if (l < first || l > r || r > last) throw out_of_range("maxPrefixSum: needs lo <= l <= r <= hi");
        int ns[128]{}, ls[128]{}, c = cover(l, r, ns, ls);  // (zeroed: l <= r gives at least one node)
        S res = pre[ns[0]], acc = sm[ns[0]];
        for (int i = 1; i < c; i++) res = max(res, acc + pre[ns[i]]), acc += sm[ns[i]];
        return res;
    }

    // O(logU * logU) -- a[i] += v; needs lo <= i <= hi, else throws out_of_range
    void pointAdd(long long i, T v) {
        if (i < first || i > last) throw out_of_range("pointAdd: needs lo <= i <= hi");
        int path[64], x = leafOf(i, path);
        setLeaf(x, T(leaf(x) + v)), up(path);
    }

    // O(logU * logU) -- a[i] = v; needs lo <= i <= hi, else throws out_of_range
    void pointAssign(long long i, T v) {
        if (i < first || i > last) throw out_of_range("pointAssign: needs lo <= i <= hi");
        int path[64], x = leafOf(i, path);
        setLeaf(x, v), up(path);
    }

    // O(logU * logU) -- a[i] = max(a[i], v); needs lo <= i <= hi, else throws out_of_range
    void pointChmax(long long i, T v) {
        if (i < first || i > last) throw out_of_range("pointChmax: needs lo <= i <= hi");
        int path[64], x = leafOf(i, path);
        setLeaf(x, max(leaf(x), v)), up(path);
    }

    // O(logU * logU) -- a[i] = min(a[i], v); needs lo <= i <= hi, else throws out_of_range
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

    // O(logU + logU) -- gcd of |a[l]|, ..., |a[r]|; needs lo <= l <= r <= hi, else throws out_of_range
    T rangeGcd(long long l, long long r) {
        if (l < first || l > r || r > last) throw out_of_range("rangeGcd: needs lo <= l <= r <= hi");
        int ns[128], ls[128], c = cover(l, r, ns, ls);
        T res = T(0);
        for (int i = 0; i < c; i++) res = gcd(res, g[ns[i]]);
        return res;
    }

    // O(logU) -- a[l] + ... + a[r]; needs lo <= l <= r <= hi, else throws out_of_range
    S rangeSum(long long l, long long r) {
        if (l < first || l > r || r > last) throw out_of_range("rangeSum: needs lo <= l <= r <= hi");
        int ns[128], ls[128], c = cover(l, r, ns, ls);
        S res = S(0);
        for (int i = 0; i < c; i++) res += sm[ns[i]];
        return res;
    }

    // ---- internals ----

    int newZero(int s) {  // a new node: a block of 2^s zeros
        L.push_back(0), R.push_back(0), sm.push_back(S(0)), pre.push_back(S(0)), g.push_back(T(0));
        return (int)L.size() - 1;
    }

    void kids(int x, int s) {  // create node x's children (blocks of zeros) if it has none yet
        if (L[x]) return;
        int a = newZero(s - 1), b = newZero(s - 1);
        L[x] = a, R[x] = b;
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
        if (l < m) collect(L[x], s - 1, tl, l, r, ns, ls, ts, c);
        if (r >= m) collect(R[x], s - 1, m, l, r, ns, ls, ts, c);
    }

    int leafOf(long long i, int* path) {  // the leaf holding a[i]; path: the nodes above it top-down, every tag pushed
        int x = 1;
        long long tl = first;
        for (int s = D; s > 0; s--) {
            kids(x, s);
            path[D - s] = x;
            if (i >= tl + (1LL << (s - 1))) tl += 1LL << (s - 1), x = R[x];
            else x = L[x];
        }
        return x;
    }

    void up(const int* path) {  // recompute the nodes of path, deepest first (path[k] has level D - k)
        for (int k = D - 1; k >= 0; k--) pull(path[k]);
    }

    void setLeaf(int p, T v) {  // leaf p holds v alone
        sm[p] = S(v), pre[p] = S(v), g[p] = v;
    }

    T leaf(int p) const { return T(sm[p]); }  // the value at leaf p

    void pull(int x) {  // recompute node x from its children
        int a = L[x], b = R[x];
        pre[x] = max(pre[a], sm[a] + pre[b]);
        sm[x] = sm[a] + sm[b];
        g[x] = gcd(g[a], g[b]);
    }
};
