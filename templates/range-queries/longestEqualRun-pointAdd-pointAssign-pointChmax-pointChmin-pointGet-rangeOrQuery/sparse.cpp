// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/longestEqualRun-pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeOrQuery/sparse.cpp
// @operations: longestEqualRun pointAdd pointAssign pointChmax pointChmin pointGet rangeOrQuery
// @data-structure-type: seg-tree
// @complexities:
//   longestEqualRun: log(U)
//   pointAdd: log(U)
//   pointAssign: log(U)
//   pointChmax: log(U)
//   pointChmin: log(U)
//   pointGet: log(U)
//   rangeOrQuery: log(U)
//   build: 1
// @memory:
//   layout: sparse
//   node: orr[4*log(U)] fv[4*log(U)] lv[4*log(U)] pr[4*log(U)] sr[4*log(U)] br[4*log(U)]
//   tags: none
//   other: children[8*log(U)]
//   note: per update, the nodes it visits (at most 4 per level, counting the children a push creates); node data per field, children L / R

// Segment tree with composable aggregates (sparse): any index range [lo, hi] (huge or negative is fine), every
// position starting at 0; point updates and range queries in O(logU), U = hi - lo + 1; each node keeps its OR, its
// first / last value and the equal runs at its ends and inside over its range. Ranges inclusive [l, r]; searches
// return lo - 1 when nothing qualifies. The root covers 2^D >= U positions from lo (the ones past hi are zeros nobody
// reads), so a node of level s covers 2^s positions; children are created on demand as blocks of zeros, right before
// anything descends past a node.
// T: int, long long, ...
template <typename T>
struct SparseSegTree {
    long long first, last;  // the index range [lo, hi]
    int D;  // the root's level: 2^D >= hi - lo + 1
    vector<int> L{0}, R{0};  // children (node 0: none; node 1 is the root)
    vector<T> orr{T(0)};
    vector<T> fv{T(0)};
    vector<T> lv{T(0)};
    vector<long long> pr{0};
    vector<long long> sr{0};
    vector<long long> br{0};

    // O(1) -- all zeros over [lo, hi]; any long long range works (lo <= hi)
    SparseSegTree(long long lo, long long hi) : first(lo), last(hi), D(hi > lo ? 64 - __builtin_clzll((unsigned long long)(hi - lo)) : 0) {
        newZero(D);
    }

    // O(logN) -- the longest run of equal adjacent values in a[l..r]; needs lo <= l <= r <= hi, else throws
    // out_of_range
    long long longestEqualRun(long long l, long long r) {
        if (l < first || l > r || r > last) throw out_of_range("longestEqualRun: needs lo <= l <= r <= hi");
        int ns[128]{}, ls[128]{}, c = cover(l, r, ns, ls);  // (zeroed: l <= r gives at least one node)
        int t = ns[0];
        long long p = pr[t], q = sr[t], res = br[t], k = 1LL << ls[0];  // (prefix run, suffix run, best, length)
        T last = lv[t];
        for (int i = 1; i < c; i++) {
            t = ns[i];
            long long w = 1LL << ls[i];
            bool j = last == fv[t];
            res = max({res, br[t], j ? q + pr[t] : 0LL});
            if (j && p == k) p += pr[t];
            q = j && sr[t] == w ? q + sr[t] : sr[t];
            k += w, last = lv[t];
        }
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

    // O(logU) -- a[l] | ... | a[r]; needs lo <= l <= r <= hi, else throws out_of_range
    T rangeOrQuery(long long l, long long r) {
        if (l < first || l > r || r > last) throw out_of_range("rangeOrQuery: needs lo <= l <= r <= hi");
        int ns[128], ls[128], c = cover(l, r, ns, ls);
        T res = T(0);
        for (int i = 0; i < c; i++) res |= orr[ns[i]];
        return res;
    }

    // ---- internals ----

    int newZero(int s) {  // a new node: a block of 2^s zeros
        L.push_back(0), R.push_back(0), orr.push_back(T(0)), fv.push_back(T(0)), lv.push_back(T(0)),
        pr.push_back(1LL << s), sr.push_back(1LL << s), br.push_back(1LL << s);
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
        for (int k = D - 1; k >= 0; k--) pull(path[k], D - k);
    }

    void setLeaf(int p, T v) {  // leaf p holds v alone
        orr[p] = v, fv[p] = v, lv[p] = v, pr[p] = 1, sr[p] = 1, br[p] = 1;
    }

    T leaf(int p) const { return T(orr[p]); }  // the value at leaf p

    void pull(int x, int s) {  // recompute node x (level s) from its children
        int a = L[x], b = R[x];
        orr[x] = orr[a] | orr[b];
        long long hl = 1LL << (s - 1);
        bool j = lv[a] == fv[b];
        br[x] = max({br[a], br[b], j ? sr[a] + pr[b] : 0LL});
        pr[x] = j && pr[a] == hl ? pr[a] + pr[b] : pr[a];
        sr[x] = j && sr[b] == hl ? sr[b] + sr[a] : sr[b];
        fv[x] = fv[a], lv[x] = lv[b];
    }
};
