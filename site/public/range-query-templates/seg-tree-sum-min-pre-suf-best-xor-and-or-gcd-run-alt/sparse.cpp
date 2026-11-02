// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/seg-tree-sum-min-pre-suf-best-xor-and-or-gcd-run-alt/sparse.cpp
// @operations: leftmostLtX leftmostLteX leftmostPrefixSumGtX leftmostPrefixSumGteX longestEqualRun maxAltSubseqSum maxPrefixSum maxSubarraySum maxSuffixSum pointAdd pointAssign pointChmax pointChmin pointGet rangeAndQuery rangeGcd rangeMin rangeOrQuery rangeSum rangeXorQuery rightmostLtX rightmostLteX rightmostSuffixSumGtX rightmostSuffixSumGteX
// @data-structure-type: seg-tree
// @complexities:
//   leftmostLtX: log(U)
//   leftmostLteX: log(U)
//   leftmostPrefixSumGtX: log(U)
//   leftmostPrefixSumGteX: log(U)
//   longestEqualRun: log(U)
//   maxAltSubseqSum: log(U)
//   maxPrefixSum: log(U)
//   maxSubarraySum: log(U)
//   maxSuffixSum: log(U)
//   pointAdd: log(U)*log(U) ?
//   pointAssign: log(U)*log(U) ?
//   pointChmax: log(U)*log(U) ?
//   pointChmin: log(U)*log(U) ?
//   pointGet: log(U)
//   rangeAndQuery: log(U)
//   rangeGcd: log(U) ?
//   rangeMin: log(U)
//   rangeOrQuery: log(U)
//   rangeSum: log(U)
//   rangeXorQuery: log(U)
//   rightmostLtX: log(U)
//   rightmostLteX: log(U)
//   rightmostSuffixSumGtX: log(U)
//   rightmostSuffixSumGteX: log(U)
//   build: 1
// @memory:
//   layout: sparse
//   node: sm[4*log(U)] mn[4*log(U)] pre[4*log(U)] suf[4*log(U)] best[4*log(U)] xr[4*log(U)] an[4*log(U)] orr[4*log(U)] g[4*log(U)] fv[4*log(U)] lv[4*log(U)] pr[4*log(U)] sr[4*log(U)] br[4*log(U)] a00[4*log(U)] a01[4*log(U)] a10[4*log(U)] a11[4*log(U)]
//   tags: none
//   other: children[8*log(U)]
//   note: per update, the nodes it visits (at most 4 per level, counting the children a push creates); node data per field, children L / R

// Segment tree with composable aggregates (sparse): any index range [lo, hi] (huge or negative is fine), every
// position starting at 0; point updates and range queries in O(logU), U = hi - lo + 1; each node keeps its sum, its
// min, its best prefix sum, its best suffix sum, its best subarray sum, its xor, its AND, its OR, its gcd, its first
// / last value and the equal runs at its ends and inside, its best alternating (+ - + ...) subsequence sum for each
// start / end sign over its range. Ranges inclusive [l, r]; searches return lo - 1 when nothing qualifies. The root
// covers 2^D >= U positions from lo (the ones past hi are zeros nobody reads), so a node of level s covers 2^s
// positions; children are created on demand as blocks of zeros, right before anything descends past a node.
// T: int, long long, ...; sums are kept in S (long long for small T).
template <typename T>
struct SparseSegTree {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    static constexpr S NEG = numeric_limits<S>::lowest() / 4;  // (no alternating subsequence of that shape)
    long long first, last;  // the index range [lo, hi]
    int D;  // the root's level: 2^D >= hi - lo + 1
    vector<int> L{0}, R{0};  // children (node 0: none; node 1 is the root)
    vector<S> sm{0};
    vector<T> mn{T(0)};
    vector<S> pre{0};
    vector<S> suf{0};
    vector<S> best{0};
    vector<T> xr{T(0)};
    vector<T> an{~T(0)};
    vector<T> orr{T(0)};
    vector<T> g{T(0)};
    vector<T> fv{T(0)};
    vector<T> lv{T(0)};
    vector<long long> pr{0};
    vector<long long> sr{0};
    vector<long long> br{0};
    vector<S> a00{0};
    vector<S> a01{0};
    vector<S> a10{0};
    vector<S> a11{0};

    // O(1) -- all zeros over [lo, hi]; any long long range works (lo <= hi)
    SparseSegTree(long long lo, long long hi) : first(lo), last(hi), D(hi > lo ? 64 - __builtin_clzll((unsigned long long)(hi - lo)) : 0) {
        newZero(D);
    }

    // O(logU) -- the first i in [l, r] with a[i] < x, or lo - 1 (a walk pruned by the node min)
    long long leftmostLtX(long long l, long long r, T x) {
        int ns[128], ls[128];
        long long ts[128];
        int c = cover(l, r, ns, ls, ts);
        for (int i = 0; i < c; i++) {
            int t = ns[i], s = ls[i];
            long long tl = ts[i];
            if (!(mn[t] < x)) continue;
            while (s) {  // walk down the passing node
                kids(t, s);
                s--;
                if (mn[L[t]] < x) t = L[t];
                else t = R[t], tl += 1LL << s;
            }
            return tl;
        }
        return first - 1;
    }

    // O(logU) -- the first i in [l, r] with a[i] <= x, or lo - 1 (a walk pruned by the node min)
    long long leftmostLteX(long long l, long long r, T x) {
        int ns[128], ls[128];
        long long ts[128];
        int c = cover(l, r, ns, ls, ts);
        for (int i = 0; i < c; i++) {
            int t = ns[i], s = ls[i];
            long long tl = ts[i];
            if (!(mn[t] <= x)) continue;
            while (s) {  // walk down the passing node
                kids(t, s);
                s--;
                if (mn[L[t]] <= x) t = L[t];
                else t = R[t], tl += 1LL << s;
            }
            return tl;
        }
        return first - 1;
    }

    // O(logU) -- first i in [l, r] with a[l] + ... + a[i] > x, or lo - 1 (a walk pruned by best prefix sums)
    long long leftmostPrefixSumGtX(long long l, long long r, T x) {
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

    // O(logU) -- first i in [l, r] with a[l] + ... + a[i] >= x, or lo - 1 (a walk pruned by best prefix sums)
    long long leftmostPrefixSumGteX(long long l, long long r, T x) {
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

    // O(logN) -- the longest run of equal adjacent values in a[l..r]
    long long longestEqualRun(long long l, long long r) {
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

    // O(logN) -- max of +b1 - b2 + b3 - ... over non-empty subsequences b of a[l..r]
    S maxAltSubseqSum(long long l, long long r) {
        int ns[128]{}, ls[128]{}, c = cover(l, r, ns, ls);  // (zeroed: l <= r gives at least one node)
        array<S, 4> a{a00[ns[0]], a01[ns[0]], a10[ns[0]], a11[ns[0]]};
        for (int i = 1; i < c; i++) a = altJoin(a, {a00[ns[i]], a01[ns[i]], a10[ns[i]], a11[ns[i]]});
        return max(a[0], a[1]);
    }

    // O(logN) -- max of a[l] + ... + a[i] over i in [l, r]
    S maxPrefixSum(long long l, long long r) {
        int ns[128]{}, ls[128]{}, c = cover(l, r, ns, ls);  // (zeroed: l <= r gives at least one node)
        S res = pre[ns[0]], acc = sm[ns[0]];
        for (int i = 1; i < c; i++) res = max(res, acc + pre[ns[i]]), acc += sm[ns[i]];
        return res;
    }

    // O(logN) -- max sum of a non-empty contiguous subarray of a[l..r]
    S maxSubarraySum(long long l, long long r) {
        int ns[128]{}, ls[128]{}, c = cover(l, r, ns, ls);  // (zeroed: l <= r gives at least one node)
        S res = best[ns[0]], q = suf[ns[0]];  // (q: the best sum ending at the right edge so far)
        for (int i = 1; i < c; i++) {
            int t = ns[i];
            res = max({res, best[t], q + pre[t]}), q = max(suf[t], sm[t] + q);
        }
        return res;
    }

    // O(logN) -- max of a[i] + ... + a[r] over i in [l, r]
    S maxSuffixSum(long long l, long long r) {
        int ns[128]{}, ls[128]{}, c = cover(l, r, ns, ls);  // (zeroed: l <= r gives at least one node)
        S res = suf[ns[c - 1]], acc = sm[ns[c - 1]];
        for (int i = c - 2; i >= 0; i--) res = max(res, acc + suf[ns[i]]), acc += sm[ns[i]];
        return res;
    }

    // O(logU * logU) -- a[i] += v
    void pointAdd(long long i, T v) {
        int path[64], x = leafOf(i, path);
        setLeaf(x, T(leaf(x) + v)), up(path);
    }

    // O(logU * logU) -- a[i] = v
    void pointAssign(long long i, T v) {
        int path[64], x = leafOf(i, path);
        setLeaf(x, v), up(path);
    }

    // O(logU * logU) -- a[i] = max(a[i], v)
    void pointChmax(long long i, T v) {
        int path[64], x = leafOf(i, path);
        setLeaf(x, max(leaf(x), v)), up(path);
    }

    // O(logU * logU) -- a[i] = min(a[i], v)
    void pointChmin(long long i, T v) {
        int path[64], x = leafOf(i, path);
        setLeaf(x, min(leaf(x), v)), up(path);
    }

    // O(logU) -- a[i]
    T pointGet(long long i) {
        int path[64];
        return leaf(leafOf(i, path));
    }

    // O(logU) -- a[l] & ... & a[r]
    T rangeAndQuery(long long l, long long r) {
        int ns[128], ls[128], c = cover(l, r, ns, ls);
        T res = ~T(0);
        for (int i = 0; i < c; i++) res &= an[ns[i]];
        return res;
    }

    // O(logU + logU) -- gcd of |a[l]|, ..., |a[r]|
    T rangeGcd(long long l, long long r) {
        int ns[128], ls[128], c = cover(l, r, ns, ls);
        T res = T(0);
        for (int i = 0; i < c; i++) res = gcd(res, g[ns[i]]);
        return res;
    }

    // O(logU) -- min of a[l..r]
    T rangeMin(long long l, long long r) {
        int ns[128], ls[128], c = cover(l, r, ns, ls);
        T res = numeric_limits<T>::max();
        for (int i = 0; i < c; i++) res = min(res, mn[ns[i]]);
        return res;
    }

    // O(logU) -- a[l] | ... | a[r]
    T rangeOrQuery(long long l, long long r) {
        int ns[128], ls[128], c = cover(l, r, ns, ls);
        T res = T(0);
        for (int i = 0; i < c; i++) res |= orr[ns[i]];
        return res;
    }

    // O(logU) -- a[l] + ... + a[r]
    S rangeSum(long long l, long long r) {
        int ns[128], ls[128], c = cover(l, r, ns, ls);
        S res = S(0);
        for (int i = 0; i < c; i++) res += sm[ns[i]];
        return res;
    }

    // O(logU) -- a[l] ^ ... ^ a[r]
    T rangeXorQuery(long long l, long long r) {
        int ns[128], ls[128], c = cover(l, r, ns, ls);
        T res = T(0);
        for (int i = 0; i < c; i++) res ^= xr[ns[i]];
        return res;
    }

    // O(logU) -- the last i in [l, r] with a[i] < x, or lo - 1 (a walk pruned by the node min)
    long long rightmostLtX(long long l, long long r, T x) {
        int ns[128], ls[128];
        long long ts[128];
        int c = cover(l, r, ns, ls, ts);
        for (int i = c - 1; i >= 0; i--) {
            int t = ns[i], s = ls[i];
            long long tl = ts[i];
            if (!(mn[t] < x)) continue;
            while (s) {  // walk down the passing node
                kids(t, s);
                s--;
                if (mn[R[t]] < x) t = R[t], tl += 1LL << s;
                else t = L[t];
            }
            return tl;
        }
        return first - 1;
    }

    // O(logU) -- the last i in [l, r] with a[i] <= x, or lo - 1 (a walk pruned by the node min)
    long long rightmostLteX(long long l, long long r, T x) {
        int ns[128], ls[128];
        long long ts[128];
        int c = cover(l, r, ns, ls, ts);
        for (int i = c - 1; i >= 0; i--) {
            int t = ns[i], s = ls[i];
            long long tl = ts[i];
            if (!(mn[t] <= x)) continue;
            while (s) {  // walk down the passing node
                kids(t, s);
                s--;
                if (mn[R[t]] <= x) t = R[t], tl += 1LL << s;
                else t = L[t];
            }
            return tl;
        }
        return first - 1;
    }

    // O(logU) -- last i in [l, r] with a[i] + ... + a[r] > x, or lo - 1 (a walk pruned by best suffix sums)
    long long rightmostSuffixSumGtX(long long l, long long r, T x) {
        int ns[128], ls[128];
        long long ts[128];
        int c = cover(l, r, ns, ls, ts);
        S acc = 0;
        for (int i = c - 1; i >= 0; i--) {
            int t = ns[i], s = ls[i];
            long long tl = ts[i];
            if (acc + suf[t] > S(x)) {
                while (s) {
                    kids(t, s);
                    s--;
                    if (acc + suf[R[t]] > S(x)) t = R[t], tl += 1LL << s;
                    else acc += sm[R[t]], t = L[t];
                }
                return tl;
            }
            acc += sm[t];
        }
        return first - 1;
    }

    // O(logU) -- last i in [l, r] with a[i] + ... + a[r] >= x, or lo - 1 (a walk pruned by best suffix sums)
    long long rightmostSuffixSumGteX(long long l, long long r, T x) {
        int ns[128], ls[128];
        long long ts[128];
        int c = cover(l, r, ns, ls, ts);
        S acc = 0;
        for (int i = c - 1; i >= 0; i--) {
            int t = ns[i], s = ls[i];
            long long tl = ts[i];
            if (acc + suf[t] >= S(x)) {
                while (s) {
                    kids(t, s);
                    s--;
                    if (acc + suf[R[t]] >= S(x)) t = R[t], tl += 1LL << s;
                    else acc += sm[R[t]], t = L[t];
                }
                return tl;
            }
            acc += sm[t];
        }
        return first - 1;
    }

    // ---- internals ----

    // A's part, then B's: the best alternating sums by (start sign, end sign) = (++, +-, -+, --)
    static array<S, 4> altJoin(const array<S, 4>& A, const array<S, 4>& B) {
        return {max({A[0], B[0], A[0] + B[2], A[1] + B[0]}), max({A[1], B[1], A[0] + B[3], A[1] + B[1]}),
                max({A[2], B[2], A[2] + B[2], A[3] + B[0]}), max({A[3], B[3], A[2] + B[3], A[3] + B[1]})};
    }

    int newZero(int s) {  // a new node: a block of 2^s zeros
        L.push_back(0), R.push_back(0), sm.push_back(S(0)), mn.push_back(T(0)), pre.push_back(S(0)),
        suf.push_back(S(0)), best.push_back(S(0)), xr.push_back(T(0)), an.push_back(T(0)), orr.push_back(T(0)),
        g.push_back(T(0)), fv.push_back(T(0)), lv.push_back(T(0)), pr.push_back(1LL << s), sr.push_back(1LL << s),
        br.push_back(1LL << s), a00.push_back(S(0)), a01.push_back(s ? S(0) : NEG), a10.push_back(s ? S(0) : NEG),
        a11.push_back(S(0));
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
        sm[p] = S(v), mn[p] = v, pre[p] = S(v), suf[p] = S(v), best[p] = S(v), xr[p] = v, an[p] = v, orr[p] = v,
        g[p] = v, fv[p] = v, lv[p] = v, pr[p] = 1, sr[p] = 1, br[p] = 1, a00[p] = S(v), a01[p] = NEG, a10[p] = NEG,
        a11[p] = -S(v);
    }

    T leaf(int p) const { return T(sm[p]); }  // the value at leaf p

    void pull(int x, int s) {  // recompute node x (level s) from its children
        int a = L[x], b = R[x];
        pre[x] = max(pre[a], sm[a] + pre[b]);
        suf[x] = max(suf[b], sm[b] + suf[a]);
        best[x] = max({best[a], best[b], suf[a] + pre[b]});
        sm[x] = sm[a] + sm[b];
        mn[x] = min(mn[a], mn[b]);
        xr[x] = xr[a] ^ xr[b];
        an[x] = an[a] & an[b];
        orr[x] = orr[a] | orr[b];
        g[x] = gcd(g[a], g[b]);
        long long hl = 1LL << (s - 1);
        bool j = lv[a] == fv[b];
        br[x] = max({br[a], br[b], j ? sr[a] + pr[b] : 0LL});
        pr[x] = j && pr[a] == hl ? pr[a] + pr[b] : pr[a];
        sr[x] = j && sr[b] == hl ? sr[b] + sr[a] : sr[b];
        fv[x] = fv[a], lv[x] = lv[b];
        array<S, 4> c = altJoin({a00[a], a01[a], a10[a], a11[a]}, {a00[b], a01[b], a10[b], a11[b]});
        a00[x] = c[0], a01[x] = c[1], a10[x] = c[2], a11[x] = c[3];
    }
};
