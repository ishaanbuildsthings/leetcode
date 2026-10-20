// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/countDistinct-countInValRange-kthGtX-kthGteX-kthLtX-kthLteX-pointGet/template.cpp
// @operations: countDistinct countInValRange kthGtX kthGteX kthLtX kthLteX pointGet
// @data-structure-type: merge-sort-tree
// @complexities:
//   countDistinct: log(N)
//   countInValRange: log(N)
//   kthGtX: log(N)
//   kthGteX: log(N)
//   kthLtX: log(N)
//   kthLteX: log(N)
//   pointGet: 1
//   build: N*log(N)
// @memory:
//   layout: none
//   node: cnt[2*N*log(N)]
//   tags: none
//   other: sortedVals[2*N] nxt[1*N]
//   note: two flat merge sort trees (one row of N prefix counts per level): one over the values for count / kth, one over nxt[i] for countDistinct
// @original-file-url: https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/segment-trees/merge/rangeDistinct_LogN_NoUpdates.cpp

// Static merge sort tree with fractional cascading, in a flat wavelet-style layout. All indices 0-based, inclusive.
// Only the root's sorted values are kept (one binary search per query); below that, cnt routes the "p smallest"
// count down each level in O(1). At any depth the nodes partition [0, n), and the node [tl, tr] owns slots tl..tr
// of that depth's row, so (depth, tl) addresses a node with no per-node vectors and no node index.
// Build O(N log N), every query O(log N), memory N * ceil(log2 N) ints + N values. T: any type with <.
template <typename T>
struct MergeSortTree {
    int n = 0, levels = 0;
    vector<T> arr, sortedVals;
    vector<int> cnt;  // cnt[d * n + tl + j] = # of the first j + 1 elements of the depth-d node at tl that live in its left child

    // O(N log N)
    explicit MergeSortTree(const vector<T>& a) : n((int)a.size()), arr(a), sortedVals(a) {
        if (!n) return;
        while ((1 << levels) < n) levels++;
        cnt.assign((size_t)levels * n, 0);
        // indices ordered by value, ties by index; splitting such a list on "index <= mid" keeps it ordered
        vector<int> cur(n), buf(n);
        iota(cur.begin(), cur.end(), 0);
        stable_sort(cur.begin(), cur.end(), [&](int i, int j) { return a[i] < a[j]; });
        for (int i = 0; i < n; i++) sortedVals[i] = a[cur[i]];
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

    // # of the first p elements (in global sorted order) of the depth-d node starting at tl that live in its left child
    int leftCount(int d, int tl, int p) const { return p ? cnt[(size_t)d * n + tl + p - 1] : 0; }

    // Over the canonical nodes covering [ql, qr], how many of the p globally-smallest elements live in them.
    // Descend while [ql, qr] sits in one child, then walk both boundary paths, adding whole siblings as they peel off.
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
        while (a < b && ql > a) {  // left boundary: cover [ql, mid] inside the left child
            int m = (a + b) >> 1, lp = leftCount(da, a, pa);
            if (ql <= m) res += pa - lp, b = m, pa = lp;  // entire right child is inside [ql, qr]
            else a = m + 1, pa -= lp;
            da++;
        }
        res += pa;
        a = mid + 1, b = tr, pa = p - leftP, da = d + 1;
        while (a < b && qr < b) {  // right boundary: cover [mid + 1, qr] inside the right child
            int m = (a + b) >> 1, lp = leftCount(da, a, pa);
            if (qr > m) res += lp, a = m + 1, pa -= lp;  // entire left child is inside [ql, qr]
            else b = m, pa = lp;
            da++;
        }
        return res + pa;
    }

    struct Part { int d, tl, tr, p; };

    // Same walk as countPrefix, but writes the canonical nodes out left to right (at most 2 * levels + 2 of them)
    int decompose(int ql, int qr, int p, Part* out) const {
        int tl = 0, tr = n - 1, d = 0, mid, leftP;
        for (;;) {
            if (ql <= tl && tr <= qr) { out[0] = {d, tl, tr, p}; return 1; }
            mid = (tl + tr) >> 1;
            leftP = leftCount(d, tl, p);
            if (qr <= mid) tr = mid, p = leftP, d++;
            else if (ql > mid) tl = mid + 1, p -= leftP, d++;
            else break;
        }
        int k = 0, a = tl, b = mid, pa = leftP, da = d + 1;
        while (a < b && ql > a) {
            int m = (a + b) >> 1, lp = leftCount(da, a, pa);
            if (ql <= m) out[k++] = {da + 1, m + 1, b, pa - lp}, b = m, pa = lp;
            else a = m + 1, pa -= lp;
            da++;
        }
        out[k++] = {da, a, b, pa};
        reverse(out, out + k);  // the left walk collected right to left
        a = mid + 1, b = tr, pa = p - leftP, da = d + 1;
        while (a < b && qr < b) {
            int m = (a + b) >> 1, lp = leftCount(da, a, pa);
            if (qr > m) out[k++] = {da + 1, a, m, lp}, a = m + 1, pa -= lp;
            else b = m, pa = lp;
            da++;
        }
        out[k++] = {da, a, b, pa};
        return k;
    }

    // k-th (1-indexed, left to right) index in [ql, qr] among the elements NOT in the p smallest (gte) or in them (lte)
    int kth(int ql, int qr, int k, int p0, bool gte) const {
        ql = max(ql, 0), qr = min(qr, n - 1);
        if (ql > qr || k <= 0) return -1;
        Part parts[2 * 32 + 4];
        int m = decompose(ql, qr, p0, parts);
        for (int i = 0; i < m; i++) {
            auto [d, tl, tr, p] = parts[i];
            int inNode = gte ? (tr - tl + 1) - p : p;
            if (k > inNode) { k -= inNode; continue; }
            while (tl < tr) {
                int mid = (tl + tr) >> 1, lp = leftCount(d, tl, p), inLeft = gte ? (mid - tl + 1) - lp : lp;
                if (k <= inLeft) tr = mid, p = lp;
                else k -= inLeft, tl = mid + 1, p -= lp;
                d++;
            }
            return tl;
        }
        return -1;
    }

    int lessThan(const T& x) const { return int(lower_bound(sortedVals.begin(), sortedVals.end(), x) - sortedVals.begin()); }
    int atMost(const T& x) const { return int(upper_bound(sortedVals.begin(), sortedVals.end(), x) - sortedVals.begin()); }

    // O(logN) -- how many i in [ql, qr] have a[i] >= x
    int countGteX(int ql, int qr, const T& x) const {
        ql = max(ql, 0), qr = min(qr, n - 1);
        return ql > qr ? 0 : (qr - ql + 1) - countPrefix(ql, qr, lessThan(x));
    }

    // O(logN) -- how many i in [ql, qr] have a[i] <= x
    int countLteX(int ql, int qr, const T& x) const {
        ql = max(ql, 0), qr = min(qr, n - 1);
        return ql > qr ? 0 : countPrefix(ql, qr, atMost(x));
    }

    // O(logN) -- how many i in [ql, qr] have valLow <= a[i] <= valHigh
    int countInValRange(int ql, int qr, const T& valLow, const T& valHigh) const {
        ql = max(ql, 0), qr = min(qr, n - 1);
        if (ql > qr || valHigh < valLow) return 0;
        return countPrefix(ql, qr, atMost(valHigh)) - countPrefix(ql, qr, lessThan(valLow));
    }

    // O(logN) -- index of the k-th (1-indexed, left to right) i in [ql, qr] with a[i] >= x, or -1
    int kthGteX(int ql, int qr, int k, const T& x) const { return kth(ql, qr, k, lessThan(x), true); }

    // O(logN) -- index of the k-th (1-indexed, left to right) i in [ql, qr] with a[i] <= x, or -1
    int kthLteX(int ql, int qr, int k, const T& x) const { return kth(ql, qr, k, atMost(x), false); }

    // O(logN) -- index of the k-th (1-indexed, left to right) i in [ql, qr] with a[i] > x, or -1
    int kthGtX(int ql, int qr, int k, const T& x) const { return kth(ql, qr, k, atMost(x), true); }

    // O(logN) -- index of the k-th (1-indexed, left to right) i in [ql, qr] with a[i] < x, or -1
    int kthLtX(int ql, int qr, int k, const T& x) const { return kth(ql, qr, k, lessThan(x), false); }

    // O(1) -- a[i]
    T pointGet(int i) const { return arr[i]; }
};

// Static range count distinct: countDistinct(l, r) = # of i in [l, r] whose next occurrence nxt[i] > r,
// a count-gte query on the MergeSortTree above built over nxt[].
template <typename T>
struct StaticDistinct {
    vector<T> arr;
    MergeSortTree<int> mst;  // over nxt[i] = next index holding the same value, or n

    // O(N log N) -- sort (value, index) pairs once: equal values end up adjacent, in index order
    static vector<int> nextOccurrence(const vector<T>& a) {
        int n = (int)a.size();
        vector<pair<T, int>> byValue(n);
        for (int i = 0; i < n; i++) byValue[i] = {a[i], i};
        sort(byValue.begin(), byValue.end());
        vector<int> nxt(n, n);
        for (int k = 0; k + 1 < n; k++)
            if (byValue[k].first == byValue[k + 1].first) nxt[byValue[k].second] = byValue[k + 1].second;
        return nxt;
    }

    // O(N log N)
    explicit StaticDistinct(const vector<T>& a) : arr(a), mst(nextOccurrence(a)) {}

    // O(logN) -- # of distinct values in a[l..r]
    int countDistinct(int l, int r) const { return mst.countGteX(l, r, r + 1); }

    // O(1) -- a[i]
    T pointGet(int i) const { return arr[i]; }
};
