// @operations: pointGet rangeLIS
// @data-structure-type: merge-sort-tree
// @complexities:
//   pointGet: log(N)
//   rangeLIS: log(N)
//   build: N*log^2(N)
// @memory:
//   layout: sparse
//   node: cnt[2*N*log(N)]
//   tags: none
//   other: idx[1*N] vals[1*N] starts[2*N] E[2*N] sortedVals[2*N]
//   note: built from N (index, value) points over any index range [lo, hi], every other index 0; the seaweed LIS structure runs on the points plus one 0 per gap (at most 2N + 1 elements)
// Static range LIS: length of the longest STRICTLY increasing subsequence of a[l..r], online, O(log N) per query.
// All indices 0-based, ranges inclusive. T: any type with <.
//
// HOW IT WORKS (Tiskin's "seaweed" algorithm)
// Turn a into a permutation (equal values ranked right-to-left, so "strictly increasing" survives). Draw the grid
// rows = values, cols = positions, with a "match" at (a[j], j). Seaweeds enter from the left and the top and walk
// down / right; two seaweeds cross at a non-match cell unless they have already crossed, and never cross at a match.
// Let E[s] = the bottom column where the seaweed entering at top column s leaves (n if it leaves on the right). Then
//     LIS(a[l..r]) = (r - l + 1) - #{s in [l, n) : E[s] <= r}
// which is one 2D count (a flat merge sort tree over E). The braid of the whole grid is the "distance product" of
// the braids of its top and bottom halves (split by value); the product takes O(n log n) with the "steady ant"
// walk, so the build is O(N log^2 N).
template <typename T>
struct RangeLIS {
    int n = 0, levels = 0;
    vector<T> arr;
    vector<int> sortedVals;  // sorted E
    vector<int> cnt;         // flat merge sort tree over E: cnt[d * n + tl + j] = # of the first j + 1 that go left

    // All scratch memory comes from one arena: a call takes what it needs from the top and gives it back on
    // return, so the O(N log N) recursive calls do no heap allocation at all.
    vector<int> arena;
    size_t top = 0;
    int* take(size_t k) { int* p = arena.data() + top; top += k; return p; }

    // distance product R = P (.) Q of permutations of size n:
    // sigma_R(i,k) = min_j sigma_P(i,j) + sigma_Q(j,k), sigma_X(i,k) = #{i' >= i : X[i'] < k}. Steady ant, O(n log n).
    void dmul(const int* P, const int* Q, int* R, int n) {
        if (n == 1) { R[0] = 0; return; }
        size_t mark = top;
        int m = n >> 1;
        int *rank = take(n), *colsLo = take(m), *colsHi = take(n - m), *rowsLo = take(m), *rowsHi = take(n - m);
        int *PLo = take(m), *PHi = take(n - m), *QLo = take(m), *QHi = take(n - m), *RLo = take(m), *RHi = take(n - m);
        int *rowCol = take(n), *colRow = take(n), *below = take(n + 2), *flags = take(n);  // flags: bit 0 row is lo, bit 1 col is lo
        fill(flags, flags + n, 0);
        for (int j = 0; j < m; j++) flags[Q[j]] |= 2;  // temporarily: column of Q is in the lo half
        int cl = 0, ch = 0, rl = 0, rh = 0;
        for (int c = 0; c < n; c++) {
            if (flags[c] & 2) rank[c] = cl, colsLo[cl++] = c;
            else rank[c] = ch, colsHi[ch++] = c;
        }
        for (int i = 0; i < n; i++) {
            if (P[i] < m) rowsLo[rl] = i, PLo[rl++] = P[i];
            else rowsHi[rh] = i, PHi[rh++] = P[i] - m;
        }
        for (int j = 0; j < m; j++) QLo[j] = rank[Q[j]];
        for (int j = m; j < n; j++) QHi[j - m] = rank[Q[j]];
        dmul(PLo, QLo, RLo, m), dmul(PHi, QHi, RHi, n - m);
        fill(flags, flags + n, 0);
        for (int t = 0; t < m; t++) {
            int i = rowsLo[t], c = colsLo[RLo[t]];
            flags[i] |= 1, flags[c] |= 2, rowCol[i] = c, colRow[c] = i;
        }
        for (int t = 0; t < n - m; t++) {
            int i = rowsHi[t], c = colsHi[RHi[t]];
            rowCol[i] = c, colRow[c] = i;
        }
        // delta(i,k) = #lo(row >= i, col >= k) - #hi(row < i, col < k). R keeps lo points where delta >= 0 and hi
        // points where delta < 0; boundary cells are fixed with the 2x2 cross-difference of min(0, delta).
        // bnd(i) = first k with delta(i,k) < 0 (n + 1 if none); walking rows upward it only moves right.
        int k = 0, d = 0;
        while (d >= 0) {
            if (k == n) { k = n + 1; break; }
            if (!(flags[k] & 2)) d--;
            k++;
        }
        int bndBelow = k;
        for (int i = n - 1; i >= 0; i--) {
            int k0 = bndBelow, bnd;
            bool isLo = flags[i] & 1;
            if (k0 == n + 1) {
                bnd = n + 1;
            } else {
                int dBelow = below[k0] = -1;
                int cur = ((rowCol[i] >= k0) == isLo) ? 0 : -1;
                k = k0;
                while (cur >= 0) {
                    if (k == n) { k = n + 1; break; }
                    int r = colRow[k];
                    if (flags[k] & 2) cur -= r >= i, dBelow -= r >= i + 1;
                    else cur -= r < i, dBelow -= r < i + 1;
                    below[++k] = dBelow;
                }
                bnd = k;
            }
            int p = rowCol[i];
            if ((isLo && p + 1 < k0) || (!isLo && p >= bnd)) {
                R[i] = p;
            } else {
                for (int kk = max(0, k0 - 1); kk <= min(bnd - 1, n - 1); kk++) {
                    int v = (isLo && p == kk) - (kk + 1 == bnd);
                    if (kk + 1 >= k0) v -= below[kk + 1];
                    if (kk >= k0) v += below[kk];
                    if (v == 1) { R[i] = kk; break; }
                }
            }
            bndBelow = bnd;
        }
        top = mark;
    }

    // seaweed braid of the grid (rows = values, cols = positions of permutation a, size n) into out[0..2n):
    // inputs are [left rows bottom->top | top cols], outputs are [bottom cols | right rows bottom->top]
    void braid(const int* a, int n, int* out) {
        if (n == 1) { out[0] = 0, out[1] = 1; return; }
        size_t mark = top;
        int m = n >> 1, k1 = m, k2 = n - m;
        int *colsLo = take(k1), *colsHi = take(k2), *subLo = take(k1), *subHi = take(k2);
        int *brLo = take(2 * k1), *brHi = take(2 * k2), *matched = take(n), *Tm = take(2 * n), *Bm = take(2 * n);
        int cl = 0, ch = 0;
        for (int j = 0; j < n; j++) {
            if (a[j] < m) colsLo[cl] = j, subLo[cl++] = a[j];
            else colsHi[ch] = j, subHi[ch++] = a[j] - m;
        }
        braid(subLo, k1, brLo), braid(subHi, k2, brHi);
        // a k-row strip over all n columns; columns without a match in it pass straight down. Written as pi[0..k+n).
        auto strip = [&](const int* cols, const int* sub, int k, int* pi) {
            fill(matched, matched + n, -1);
            for (int t = 0; t < k; t++) matched[cols[t]] = t;
            auto outIdx = [&](int y) { return y < k ? cols[y] : n + y - k; };
            for (int x = 0; x < k; x++) pi[x] = outIdx(sub[x]);
            for (int j = 0; j < n; j++) pi[k + j] = matched[j] < 0 ? j : outIdx(sub[k + matched[j]]);
        };
        // stack the strips: extend each to all 2n seaweeds, then multiply (top strip first)
        for (int r = 0; r < k2; r++) Tm[r] = r;
        strip(colsLo, brLo, k1, Tm + k2);
        for (int x = k2; x < k2 + k1 + n; x++) Tm[x] += k2;
        strip(colsHi, brHi, k2, Bm);
        for (int t = 0; t < k1; t++) Bm[k2 + n + t] = n + k2 + t;
        dmul(Tm, Bm, out, 2 * n);
        top = mark;
    }

    // O(N log^2 N)
    explicit RangeLIS(const vector<T>& a) : n((int)a.size()), arr(a) {
        if (!n) return;
        vector<int> order(n), perm(n);
        iota(order.begin(), order.end(), 0);
        sort(order.begin(), order.end(), [&](int i, int j) { return a[i] < a[j] || (!(a[j] < a[i]) && i > j); });
        for (int r = 0; r < n; r++) perm[order[r]] = r;  // equal values ranked right-to-left => strict LIS
        // peak scratch use measured at ~51 N ints (the braid levels plus the multiply under them); freed right after
        arena.assign((size_t)56 * n + 64, 0);
        vector<int> pi(2 * n), E(n);
        braid(perm.data(), n, pi.data());
        vector<int>().swap(arena);
        for (int s = 0; s < n; s++) E[s] = pi[n + s] < n ? pi[n + s] : n;
        // flat merge sort tree over E
        while ((1 << levels) < n) levels++;
        cnt.assign((size_t)levels * n, 0);
        vector<int> cur(n), buf(n);
        iota(cur.begin(), cur.end(), 0);
        stable_sort(cur.begin(), cur.end(), [&](int i, int j) { return E[i] < E[j]; });
        sortedVals.resize(n);
        for (int i = 0; i < n; i++) sortedVals[i] = E[cur[i]];
        vector<pair<int, int>> nodes{{0, n - 1}}, next;
        for (int d = 0; d < levels; d++) {
            int* C = cnt.data() + (size_t)d * n;
            next.clear();
            for (auto [tl, tr] : nodes) {
                if (tl == tr) continue;
                int mid = (tl + tr) >> 1, lp = tl, rp = mid + 1, run = 0;
                for (int j = tl; j <= tr; j++) {
                    int id = cur[j];
                    if (id <= mid) buf[lp++] = id, run++;
                    else buf[rp++] = id;
                    C[j] = run;
                }
                next.push_back({tl, mid}), next.push_back({mid + 1, tr});
            }
            swap(cur, buf), swap(nodes, next);
        }
    }

    int leftCount(int d, int tl, int p) const { return p ? cnt[(size_t)d * n + tl + p - 1] : 0; }

    // # of s in [ql, qr] whose E[s] is among the p smallest E values
    int countPrefix(int ql, int qr, int p) const {
        int tl = 0, tr = n - 1, d = 0, mid, leftP;
        for (;;) {
            if (ql <= tl && tr <= qr) return p;
            mid = (tl + tr) >> 1;
            leftP = leftCount(d, tl, p);
            if (qr <= mid) tr = mid, p = leftP, d++;
            else if (ql > mid) tl = mid + 1, p -= leftP, d++;
            else break;
        }
        int res = 0, a = tl, b = mid, pa = leftP, da = d + 1;
        while (a < b && ql > a) {
            int mm = (a + b) >> 1, lp = leftCount(da, a, pa);
            if (ql <= mm) res += pa - lp, b = mm, pa = lp;
            else a = mm + 1, pa -= lp;
            da++;
        }
        res += pa;
        a = mid + 1, b = tr, pa = p - leftP, da = d + 1;
        while (a < b && qr < b) {
            int mm = (a + b) >> 1, lp = leftCount(da, a, pa);
            if (qr > mm) res += lp, a = mm + 1, pa -= lp;
            else b = mm, pa = lp;
            da++;
        }
        return res + pa;
    }

    // O(logN) -- length of the longest strictly increasing subsequence of a[l..r]
    int rangeLIS(int l, int r) const {
        if (l > r) return 0;
        int p = int(upper_bound(sortedVals.begin(), sortedVals.end(), r) - sortedVals.begin());
        return (r - l + 1) - countPrefix(l, n - 1, p);
    }

    // O(1) -- a[i]
    T pointGet(int i) const { return arr[i]; }
};

// ======================================================================================== sparse wrapper

// Range LIS (longest strictly increasing subsequence; a run of zeros adds at most one element) over any index range [lo, hi], built from (index, value) points; every other index is 0. A maximal gap
// of zeros adds nothing more than a single 0, so RangeLIS runs on the compressed array of points with one 0 per gap,
// and a query maps l and r to the compressed elements containing them.
template <typename T>
struct SparseStaticLIS {
    long long lo, hi;
    vector<long long> idx, starts;  // point indices; starts[k] = first index of compressed element k
    vector<T> vals;
    RangeLIS<T> inner;

    // O(N log N) -- [lo, hi] all 0 except the given (index, value) points (distinct indices)
    SparseStaticLIS(long long lo, long long hi, vector<pair<long long, T>> points) : lo(lo), hi(hi), inner(compress(points)) {}

    vector<T> compress(vector<pair<long long, T>>& pts) {
        sort(pts.begin(), pts.end());
        vector<T> arr;
        long long prev = lo - 1;
        for (auto& [i, v] : pts) {
            if (i > prev + 1) starts.push_back(prev + 1), arr.push_back(T(0));
            starts.push_back(i), arr.push_back(v);
            idx.push_back(i), vals.push_back(v);
            prev = i;
        }
        if (prev < hi) starts.push_back(prev + 1), arr.push_back(T(0));
        return arr;
    }

    int element(long long i) const { return int(upper_bound(starts.begin(), starts.end(), i) - starts.begin()) - 1; }

    // O(logN) -- range lis of a[l..r]
    int rangeLIS(long long l, long long r) const { return inner.rangeLIS(element(l), element(r)); }

    // O(logN) -- a[i]
    T pointGet(long long i) const {
        auto it = lower_bound(idx.begin(), idx.end(), i);
        return it != idx.end() && *it == i ? vals[it - idx.begin()] : T(0);
    }
};
