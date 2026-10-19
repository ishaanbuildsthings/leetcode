// @operations: pointGet rangeLIS
// @data-structure-type: merge-sort-tree
// @complexities:
//   pointGet: 1
//   rangeLIS: log(N)
//   build: N*log^2(N)
// @memory:
//   layout: none
//   node: cnt[1*N*log(N)]
//   tags: none
//   other: arr[1*N] E[1*N] sortedVals[1*N]
//   note: the build is Tiskin's seaweed algorithm (permutations of size 2N per recursion level, freed after); queries count points in a flat merge sort tree over E

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

    // distance product: sigma_R(i,k) = min_j sigma_P(i,j) + sigma_Q(j,k), sigma_X(i,k) = #{i' >= i : X[i'] < k}
    static vector<int> dmul(const vector<int>& P, const vector<int>& Q) {
        int n = (int)P.size();
        if (n == 1) return {0};
        int m = n >> 1;
        vector<char> isLoCol(n, 0);
        for (int j = 0; j < m; j++) isLoCol[Q[j]] = 1;
        vector<int> rank(n), colsLo, colsHi, rowsLo, rowsHi, PLo, PHi, QLo(m), QHi(n - m);
        for (int c = 0; c < n; c++) {
            if (isLoCol[c]) rank[c] = (int)colsLo.size(), colsLo.push_back(c);
            else rank[c] = (int)colsHi.size(), colsHi.push_back(c);
        }
        for (int i = 0; i < n; i++) {
            if (P[i] < m) rowsLo.push_back(i), PLo.push_back(P[i]);
            else rowsHi.push_back(i), PHi.push_back(P[i] - m);
        }
        for (int j = 0; j < m; j++) QLo[j] = rank[Q[j]];
        for (int j = m; j < n; j++) QHi[j - m] = rank[Q[j]];
        vector<int> RLo = dmul(PLo, QLo), RHi = dmul(PHi, QHi);
        vector<char> rowIsLo(n, 0), colIsLo(n, 0);
        vector<int> rowCol(n), colRow(n);
        for (size_t t = 0; t < rowsLo.size(); t++) {
            int i = rowsLo[t], c = colsLo[RLo[t]];
            rowIsLo[i] = colIsLo[c] = 1, rowCol[i] = c, colRow[c] = i;
        }
        for (size_t t = 0; t < rowsHi.size(); t++) {
            int i = rowsHi[t], c = colsHi[RHi[t]];
            rowCol[i] = c, colRow[c] = i;
        }
        // delta(i,k) = #lo(row >= i, col >= k) - #hi(row < i, col < k). R keeps lo points where delta >= 0 and hi
        // points where delta < 0; boundary cells are fixed with the 2x2 cross-difference of min(0, delta).
        // bnd(i) = first k with delta(i,k) < 0 (n + 1 if none); walking rows upward it only moves right.
        vector<int> R(n), below(n + 2, 0);
        int k = 0, d = 0;
        while (d >= 0) {
            if (k == n) { k = n + 1; break; }
            if (!colIsLo[k]) d--;
            k++;
        }
        int bndBelow = k;
        for (int i = n - 1; i >= 0; i--) {
            int k0 = bndBelow, bnd;
            if (k0 == n + 1) {
                bnd = n + 1;
            } else {
                int dBelow = below[k0] = -1;
                int cur = ((rowCol[i] >= k0) == (bool)rowIsLo[i]) ? 0 : -1;
                k = k0;
                while (cur >= 0) {
                    if (k == n) { k = n + 1; break; }
                    int r = colRow[k];
                    if (colIsLo[k]) cur -= r >= i, dBelow -= r >= i + 1;
                    else cur -= r < i, dBelow -= r < i + 1;
                    below[++k] = dBelow;
                }
                bnd = k;
            }
            int p = rowCol[i];
            bool isLo = rowIsLo[i];
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
        return R;
    }

    // seaweed braid of the grid (rows = values, cols = positions of permutation a). Size 2n: inputs are
    // [left rows bottom->top | top cols], outputs are [bottom cols | right rows bottom->top]
    static vector<int> braid(const vector<int>& a) {
        int n = (int)a.size();
        if (n == 1) return {0, 1};
        int m = n >> 1;
        vector<int> colsLo, colsHi, subLo, subHi;
        for (int j = 0; j < n; j++) {
            if (a[j] < m) colsLo.push_back(j), subLo.push_back(a[j]);
            else colsHi.push_back(j), subHi.push_back(a[j] - m);
        }
        // a k-row strip over all n columns; columns without a match in it pass straight down
        auto strip = [n](const vector<int>& cols, const vector<int>& sub, int k) {
            vector<int> pi(k + n), matched(n, -1);
            for (int t = 0; t < k; t++) matched[cols[t]] = t;
            auto out = [&](int y) { return y < k ? cols[y] : n + y - k; };
            for (int x = 0; x < k; x++) pi[x] = out(sub[x]);
            for (int j = 0; j < n; j++) pi[k + j] = matched[j] < 0 ? j : out(sub[k + matched[j]]);
            return pi;
        };
        int k1 = m, k2 = n - m;
        vector<int> piT = strip(colsLo, braid(subLo), k1), piB = strip(colsHi, braid(subHi), k2);
        // stack the strips: extend each to all 2n seaweeds, then multiply (top strip first)
        vector<int> Tm(2 * n), Bm(2 * n);
        for (int r = 0; r < k2; r++) Tm[r] = r;
        for (int x = 0; x < k1 + n; x++) Tm[k2 + x] = k2 + piT[x];
        for (int x = 0; x < k2 + n; x++) Bm[x] = piB[x];
        for (int t = 0; t < k1; t++) Bm[k2 + n + t] = n + k2 + t;
        return dmul(Tm, Bm);
    }

    // O(N log^2 N)
    explicit RangeLIS(const vector<T>& a) : n((int)a.size()), arr(a) {
        if (!n) return;
        vector<int> order(n), perm(n);
        iota(order.begin(), order.end(), 0);
        sort(order.begin(), order.end(), [&](int i, int j) { return a[i] < a[j] || (!(a[j] < a[i]) && i > j); });
        for (int r = 0; r < n; r++) perm[order[r]] = r;  // equal values ranked right-to-left => strict LIS
        vector<int> pi = braid(perm), E(n);
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
