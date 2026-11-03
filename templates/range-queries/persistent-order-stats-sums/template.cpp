// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/persistent-order-stats-sums/template.cpp
// @operations: countGtX countGteX countInValRange countLtX countLteX countOccurrences kthSmallest largestLtX largestLteX pointGet rangeMax rangeMin rangeSum smallestGtX smallestGteX sumAbsDiffToX sumGtX sumGteX sumInValRange sumKthLargestRange sumKthSmallestRange sumLargestK sumLtX sumLteX sumSmallestK
// @data-structure-type: persistent
// @complexities:
//   countGtX: log(N)
//   countGteX: log(N)
//   countInValRange: log(N)
//   countLtX: log(N)
//   countLteX: log(N)
//   countOccurrences: log(N)
//   kthSmallest: log(N)
//   largestLtX: log(N)
//   largestLteX: log(N)
//   pointGet: 1
//   rangeMax: log(N)
//   rangeMin: log(N)
//   rangeSum: log(N)
//   smallestGtX: log(N)
//   smallestGteX: log(N)
//   sumAbsDiffToX: log(N)
//   sumGtX: log(N)
//   sumGteX: log(N)
//   sumInValRange: log(N)
//   sumKthLargestRange: log(N)
//   sumKthSmallestRange: log(N)
//   sumLargestK: log(N)
//   sumLtX: log(N)
//   sumLteX: log(N)
//   sumSmallestK: log(N)
//   build: N*log(N)
// @memory:
//   layout: none
//   node: L[1*N*log(N)] R[1*N*log(N)] C[1*N*log(N)] S[1*N*log(N)]
//   tags: none
//   other: root[1*N] arr[1*N] srt[1*N]
//   note: persistent seg tree over the compressed values: about N log N nodes; L/R are child pointers, C counts, S sums

// Static array. Persistent seg tree over the values' compressed ranks: version p holds a[0..p-1], so a[l..r] is
// version r + 1 minus version l, and every query walks down those two versions together. Costs are log of the number
// of distinct values, never of the value range; query arguments (x, lowVal, ...) can be anything. 0-indexed, inclusive.
// T: int, long long, ...; sums are kept in S (long long for small T).
template <typename T>
struct PersistentOrderStats {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    int n, m;
    long long klo, khi;            // the tree is over ranks 0..m-1
    vector<T> arr, srt;            // srt: sorted distinct values
    vector<int> root, L, R, C;     // node 0 = the empty tree
    vector<S> Sm;

    // O(N log N) -- arr: the initial array, 0-indexed
    explicit PersistentOrderStats(const vector<T>& a) : n((int)a.size()), arr(a), srt(a), root(1, 0), L(1, 0), R(1, 0), C(1, 0), Sm(1, S(0)) {
        sort(srt.begin(), srt.end());
        srt.erase(unique(srt.begin(), srt.end()), srt.end());
        m = (int)srt.size();
        klo = 0, khi = max(m - 1, 0);
        for (const T& v : a) root.push_back(ins(root.back(), lb(v), v));
    }

    // O(1) -- a[i]; needs 0 <= i < n, else throws out_of_range
    T pointGet(int i) const {
        if (i < 0 || i >= n) throw out_of_range("pointGet: needs 0 <= i < n");
        return arr[i];
    }

    // O(logN) -- # of i in [l, r] with a[i] == x; needs 0 <= l <= r < n, else throws out_of_range
    int countOccurrences(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("countOccurrences: needs 0 <= l <= r < n");
        return countInValRange(l, r, x, x);
    }

    // O(logN) -- # of i in [l, r] with lowVal <= a[i] <= highVal; needs 0 <= l <= r < n, else throws out_of_range
    int countInValRange(int l, int r, T lowVal, T highVal) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("countInValRange: needs 0 <= l <= r < n");
        if (highVal < lowVal) return 0;
        return countBelow(l, r, ub(highVal)) - countBelow(l, r, lb(lowVal));
    }

    // O(logN) -- # of values < x in a[l..r]; needs 0 <= l <= r < n, else throws out_of_range
    int countLtX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("countLtX: needs 0 <= l <= r < n");
        return countBelow(l, r, lb(x));
    }

    // O(logN) -- # of values <= x in a[l..r]; needs 0 <= l <= r < n, else throws out_of_range
    int countLteX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("countLteX: needs 0 <= l <= r < n");
        return countBelow(l, r, ub(x));
    }

    // O(logN) -- # of values > x in a[l..r]; needs 0 <= l <= r < n, else throws out_of_range
    int countGtX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("countGtX: needs 0 <= l <= r < n");
        return r - l + 1 - countBelow(l, r, ub(x));
    }

    // O(logN) -- # of values >= x in a[l..r]; needs 0 <= l <= r < n, else throws out_of_range
    int countGteX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("countGteX: needs 0 <= l <= r < n");
        return r - l + 1 - countBelow(l, r, lb(x));
    }

    // O(logN) -- the k-th smallest of a[l..r] (k = 1 is the min); needs 0 <= l <= r < n and 1 <= k <= r - l + 1, else
    // throws out_of_range
    T kthSmallest(int l, int r, int k) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("kthSmallest: needs 0 <= l <= r < n");
        if (k < 1 || k > r - l + 1) throw out_of_range("kthSmallest: needs 1 <= k <= r - l + 1");
        return kth(l, r, k);
    }

    // O(logN) -- min of a[l..r]; needs 0 <= l <= r < n, else throws out_of_range
    T rangeMin(int l, int r) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeMin: needs 0 <= l <= r < n");
        return kth(l, r, 1);
    }

    // O(logN) -- max of a[l..r]; needs 0 <= l <= r < n, else throws out_of_range
    T rangeMax(int l, int r) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeMax: needs 0 <= l <= r < n");
        return kth(l, r, r - l + 1);
    }

    // O(logN) -- smallest value >= x in a[l..r], or nullopt; needs 0 <= l <= r < n, else throws out_of_range
    optional<T> smallestGteX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("smallestGteX: needs 0 <= l <= r < n");
        int c = countBelow(l, r, lb(x));
        if (c == r - l + 1) return nullopt;
        return kth(l, r, c + 1);
    }

    // O(logN) -- smallest value > x in a[l..r], or nullopt; needs 0 <= l <= r < n, else throws out_of_range
    optional<T> smallestGtX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("smallestGtX: needs 0 <= l <= r < n");
        int c = countBelow(l, r, ub(x));
        if (c == r - l + 1) return nullopt;
        return kth(l, r, c + 1);
    }

    // O(logN) -- largest value <= x in a[l..r], or nullopt; needs 0 <= l <= r < n, else throws out_of_range
    optional<T> largestLteX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("largestLteX: needs 0 <= l <= r < n");
        int c = countBelow(l, r, ub(x));
        if (c == 0) return nullopt;
        return kth(l, r, c);
    }

    // O(logN) -- largest value < x in a[l..r], or nullopt; needs 0 <= l <= r < n, else throws out_of_range
    optional<T> largestLtX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("largestLtX: needs 0 <= l <= r < n");
        int c = countBelow(l, r, lb(x));
        if (c == 0) return nullopt;
        return kth(l, r, c);
    }

    // O(logN) -- a[l] + ... + a[r]; needs 0 <= l <= r < n, else throws out_of_range
    S rangeSum(int l, int r) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeSum: needs 0 <= l <= r < n");
        return sumFirst(l, r, r - l + 1);
    }

    // O(logN) -- sum of the a[i] in [l, r] with lowVal <= a[i] <= highVal; needs 0 <= l <= r < n, else throws
    // out_of_range
    S sumInValRange(int l, int r, T lowVal, T highVal) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("sumInValRange: needs 0 <= l <= r < n");
        if (highVal < lowVal) return 0;
        return sumBelow(l, r, ub(highVal)) - sumBelow(l, r, lb(lowVal));
    }

    // O(logN) -- sum of the values < x in a[l..r]; needs 0 <= l <= r < n, else throws out_of_range
    S sumLtX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("sumLtX: needs 0 <= l <= r < n");
        return sumBelow(l, r, lb(x));
    }

    // O(logN) -- sum of the values <= x in a[l..r]; needs 0 <= l <= r < n, else throws out_of_range
    S sumLteX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("sumLteX: needs 0 <= l <= r < n");
        return sumBelow(l, r, ub(x));
    }

    // O(logN) -- sum of the values > x in a[l..r]; needs 0 <= l <= r < n, else throws out_of_range
    S sumGtX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("sumGtX: needs 0 <= l <= r < n");
        return sumFirst(l, r, r - l + 1) - sumBelow(l, r, ub(x));
    }

    // O(logN) -- sum of the values >= x in a[l..r]; needs 0 <= l <= r < n, else throws out_of_range
    S sumGteX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("sumGteX: needs 0 <= l <= r < n");
        return sumFirst(l, r, r - l + 1) - sumBelow(l, r, lb(x));
    }

    // O(logN) -- sum of the k smallest values in a[l..r]; needs 0 <= l <= r < n and 0 <= k <= r - l + 1, else throws
    // out_of_range
    S sumSmallestK(int l, int r, int k) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("sumSmallestK: needs 0 <= l <= r < n");
        if (k < 0 || k > r - l + 1) throw out_of_range("sumSmallestK: needs 0 <= k <= r - l + 1");
        return sumFirst(l, r, k);
    }

    // O(logN) -- sum of the k largest values in a[l..r]; needs 0 <= l <= r < n and 0 <= k <= r - l + 1, else throws
    // out_of_range
    S sumLargestK(int l, int r, int k) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("sumLargestK: needs 0 <= l <= r < n");
        int n = r - l + 1;
        if (k < 0 || k > n) throw out_of_range("sumLargestK: needs 0 <= k <= r - l + 1");
        return sumFirst(l, r, n) - sumFirst(l, r, n - k);
    }

    // O(logN) -- sum of the kFrom-th..kTo-th smallest values of a[l..r] (1-indexed, inclusive); needs 0 <= l <= r < n
    // and 1 <= kFrom <= kTo <= r - l + 1, else throws out_of_range
    S sumKthSmallestRange(int l, int r, int kFrom, int kTo) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("sumKthSmallestRange: needs 0 <= l <= r < n");
        if (kFrom < 1 || kFrom > kTo || kTo > r - l + 1)
            throw out_of_range("sumKthSmallestRange: needs 1 <= kFrom <= kTo <= r - l + 1");
        return sumFirst(l, r, kTo) - sumFirst(l, r, kFrom - 1);
    }

    // O(logN) -- sum of the kFrom-th..kTo-th largest values of a[l..r] (1-indexed, inclusive; (1, 3) = the 3
    // biggest); needs 0 <= l <= r < n and 1 <= kFrom <= kTo <= r - l + 1, else throws out_of_range
    S sumKthLargestRange(int l, int r, int kFrom, int kTo) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("sumKthLargestRange: needs 0 <= l <= r < n");
        int n = r - l + 1;
        if (kFrom < 1 || kFrom > kTo || kTo > n)
            throw out_of_range("sumKthLargestRange: needs 1 <= kFrom <= kTo <= r - l + 1");
        return sumFirst(l, r, n - kFrom + 1) - sumFirst(l, r, n - kTo);
    }

    // O(logN) -- sum of |a[i] - x| over i in [l, r]; needs 0 <= l <= r < n, else throws out_of_range
    S sumAbsDiffToX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("sumAbsDiffToX: needs 0 <= l <= r < n");
        int rk = lb(x), c = countBelow(l, r, rk);
        S s = sumBelow(l, r, rk);
        return S(x) * c - s + (sumFirst(l, r, r - l + 1) - s) - S(x) * (r - l + 1 - c);
    }

    int lb(const T& v) const { return int(lower_bound(srt.begin(), srt.end(), v) - srt.begin()); }
    int ub(const T& v) const { return int(upper_bound(srt.begin(), srt.end(), v) - srt.begin()); }

    // ---- internals ----

    // copy of version node with one more value (key = its compressed rank)
    int ins(int node, long long key, T v) {
        vector<pair<int, bool>> path;
        long long nl = klo, nh = khi;
        while (nl != nh) {
            long long mid = nl + (nh - nl) / 2;
            if (key <= mid) path.push_back({node, true}), node = L[node], nh = mid;
            else path.push_back({node, false}), node = R[node], nl = mid + 1;
        }
        L.push_back(0), R.push_back(0), C.push_back(C[node] + 1), Sm.push_back(Sm[node] + S(v));
        int cur = (int)C.size() - 1;
        for (int k = (int)path.size() - 1; k >= 0; k--) {
            auto [old, left] = path[k];
            int lc = left ? cur : L[old], rc = left ? R[old] : cur;
            L.push_back(lc), R.push_back(rc), C.push_back(C[lc] + C[rc]), Sm.push_back(Sm[lc] + Sm[rc]);
            cur = (int)C.size() - 1;
        }
        return cur;
    }

    // the k-th smallest of a[l..r], 1 <= k <= r - l + 1: walk version r + 1 minus version l
    T kth(long long l, long long r, long long k) const {
        int a = root[r + 1], b = root[l];
        long long nl = klo, nh = khi;
        while (nl != nh) {
            long long mid = nl + (nh - nl) / 2, c = C[L[a]] - C[L[b]];
            if (k <= c) a = L[a], b = L[b], nh = mid;
            else k -= c, a = R[a], b = R[b], nl = mid + 1;
        }
        return srt[nl];
    }

    // # of i in [l, r] whose compressed rank is < x
    long long countBelow(long long l, long long r, long long x) const {
        if (x <= klo) return 0;
        if (x > khi) return r - l + 1;
        int a = root[r + 1], b = root[l];
        long long nl = klo, nh = khi, res = 0;
        while (nl != nh) {
            long long mid = nl + (nh - nl) / 2;
            if (x <= mid) a = L[a], b = L[b], nh = mid;
            else res += C[L[a]] - C[L[b]], a = R[a], b = R[b], nl = mid + 1;  // the whole left half is below x
        }
        return res;
    }

    // sum of the k smallest of a[l..r], 0 <= k <= r - l + 1
    S sumFirst(long long l, long long r, long long k) const {
        if (k <= 0) return 0;
        int a = root[r + 1], b = root[l];
        long long nl = klo, nh = khi;
        S res = 0;
        while (nl != nh) {
            long long mid = nl + (nh - nl) / 2, c = C[L[a]] - C[L[b]];
            if (k <= c) a = L[a], b = L[b], nh = mid;
            else k -= c, res += Sm[L[a]] - Sm[L[b]], a = R[a], b = R[b], nl = mid + 1;  // the left half is among them
        }
        return res + S(k) * S(srt[nl]);
    }

    // sum of the a[i], i in [l, r], whose compressed rank is < x
    S sumBelow(long long l, long long r, long long x) const {
        if (x <= klo) return 0;
        int a = root[r + 1], b = root[l];
        if (x > khi) return Sm[a] - Sm[b];
        long long nl = klo, nh = khi;
        S res = 0;
        while (nl != nh) {
            long long mid = nl + (nh - nl) / 2;
            if (x <= mid) a = L[a], b = L[b], nh = mid;
            else res += Sm[L[a]] - Sm[L[b]], a = R[a], b = R[b], nl = mid + 1;
        }
        return res;
    }
};
