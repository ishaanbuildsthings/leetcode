// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/countInValRange-kthGtX-kthGteX-kthLtX-kthLteX-pointGet/sparse.cpp
// @operations: countInValRange kthGtX kthGteX kthLtX kthLteX pointGet
// @data-structure-type: merge-sort-tree
// @fractional-cascading: yes
// @complexities:
//   countInValRange: log(N)
//   kthGtX: log^2(N)
//   kthGteX: log^2(N)
//   kthLtX: log^2(N)
//   kthLteX: log^2(N)
//   pointGet: log(N)
//   build: N*log(N)
// @memory:
//   layout: sparse
//   node: cnt[1*N*log(N)]
//   tags: none
//   other: idx[1*N] vals[1*N] sortedVals[1*N]
//   note: built from N given values (index, value pairs) over any index range [lo, hi], every other index 0; costs are in N; the merge sort tree is over the given values only; a k-th whose test 0 passes binary-searches the gap it falls in
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

// ======================================================================================== sparse wrapper

// Count values in a value range / k-th index whose value passes a test, over any index range [lo, hi], built
// from given values (index, value pairs); every other index is 0. The merge sort tree runs on the given values alone; the zeros
// of [l, r] are its length minus the given values inside, and they count wherever 0 passes the test.
template <typename T>
struct SparseStaticMergeSortTree {
    long long lo, hi;
    vector<long long> idx;
    vector<T> vals;
    MergeSortTree<T> inner;

    // O(N log N) -- [lo, hi] all 0 except the given values: (index, value) pairs with distinct indices; N = len(values)
    SparseStaticMergeSortTree(long long lo, long long hi, vector<pair<long long, T>> values) : lo(lo), hi(hi), inner(split(values)) {}

    vector<T> split(vector<pair<long long, T>>& pts) {
        sort(pts.begin(), pts.end());
        for (auto& [i, v] : pts) idx.push_back(i), vals.push_back(v);
        return vals.empty() ? vector<T>{T(0)} : vals;  // (a dummy element when there are no given values; never queried)
    }

    // the given values inside [l, r] are i0..i1, and the rest of [l, r] is zeros = (r - l + 1) - (i1 - i0 + 1) zeros
    void span(long long l, long long r, int& i0, int& i1, long long& zeros) const {
        i0 = int(lower_bound(idx.begin(), idx.end(), l) - idx.begin());
        i1 = int(upper_bound(idx.begin(), idx.end(), r) - idx.begin()) - 1;
        zeros = (r - l + 1) - (i1 - i0 + 1);
    }

    // O(logN) -- # of i in [l, r] with valLow <= a[i] <= valHigh
    long long countInValRange(long long l, long long r, T valLow, T valHigh) const {
        int i0, i1;
        long long zeros;
        span(l, r, i0, i1, zeros);
        long long inside = i0 <= i1 ? inner.countInValRange(i0, i1, valLow, valHigh) : 0;
        return inside + (valLow <= T(0) && T(0) <= valHigh ? zeros : 0);
    }

    // the k-th i in [l, r] whose value passes the test; qual(t) = qualifying given values among i0..t-1; zeroOk: 0 passes;
    // denseKth(i0, i1, k) = the dense k-th among the given values (-1 if none)
    template <class Q, class K>
    long long kthWithZeros(long long l, long long r, long long k, bool zeroOk, Q qual, K denseKth) const {
        int i0, i1;
        long long zeros;
        span(l, r, i0, i1, zeros);
        if (k <= 0) return lo - 1;
        if (!zeroOk) {
            if (k > i1 - i0 + 1) return lo - 1;
            int j = denseKth(i0, i1, int(k));
            return j != -1 ? idx[j] : lo - 1;
        }
        auto g = [&](int t) {  // qualifying indices in [l, (given value t) - 1]; given value i1 + 1 stands for r + 1
            return ((t <= i1 ? idx[t] : r + 1) - l) - (t - i0) + qual(i0, t);
        };
        if (g(i1 + 1) < k) return lo - 1;
        int a = i0, b = i1 + 1;  // smallest t with g(t) >= k
        while (a < b) {
            int m = a + (b - a) / 2;
            if (g(m) >= k) b = m;
            else a = m + 1;
        }
        int t = a;
        if (t == i0) return l - 1 + k;
        long long c = g(t - 1) + qual(i0, t) - qual(i0, t - 1);  // qualifying indices in [l, given value t - 1]
        return c >= k ? idx[t - 1] : idx[t - 1] + (k - c);
    }

    // O(log^2 N) -- index of the k-th (1-indexed) i in [l, r] with a[i] >= x, or lo - 1
    long long kthGteX(long long l, long long r, long long k, T x) const {
        return kthWithZeros(l, r, k, T(0) >= x, [&](int i0, int t) -> long long { return t > i0 ? inner.countGteX(i0, t - 1, x) : 0; },
                            [&](int a, int b, int kk) { return inner.kthGteX(a, b, kk, x); });
    }

    // O(log^2 N) -- index of the k-th (1-indexed) i in [l, r] with a[i] > x, or lo - 1
    long long kthGtX(long long l, long long r, long long k, T x) const {
        return kthWithZeros(l, r, k, T(0) > x, [&](int i0, int t) -> long long { return t > i0 ? inner.countGteX(i0, t - 1, x + 1) : 0; },
                            [&](int a, int b, int kk) { return inner.kthGtX(a, b, kk, x); });
    }

    // O(log^2 N) -- index of the k-th (1-indexed) i in [l, r] with a[i] <= x, or lo - 1
    long long kthLteX(long long l, long long r, long long k, T x) const {
        return kthWithZeros(l, r, k, T(0) <= x, [&](int i0, int t) -> long long { return t > i0 ? inner.countLteX(i0, t - 1, x) : 0; },
                            [&](int a, int b, int kk) { return inner.kthLteX(a, b, kk, x); });
    }

    // O(log^2 N) -- index of the k-th (1-indexed) i in [l, r] with a[i] < x, or lo - 1
    long long kthLtX(long long l, long long r, long long k, T x) const {
        return kthWithZeros(l, r, k, T(0) < x, [&](int i0, int t) -> long long { return t > i0 ? inner.countLteX(i0, t - 1, x - 1) : 0; },
                            [&](int a, int b, int kk) { return inner.kthLtX(a, b, kk, x); });
    }

    // O(logN) -- a[i]
    T pointGet(long long i) const {
        auto it = lower_bound(idx.begin(), idx.end(), i);
        return it != idx.end() && *it == i ? vals[it - idx.begin()] : T(0);
    }
};
