// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/persistent-order-stats-sums/sparse.cpp
// @operations: countGtX countGteX countInValRange countLtX countLteX countOccurrences kthLargest kthSmallest largestLtX largestLteX medianHigh medianLow pointGet rangeMax rangeMin rangeSum smallestGtX smallestGteX sumAbsDiffToMedian sumAbsDiffToX sumGtX sumGteX sumInValRange sumKthLargestRange sumKthSmallestRange sumLargestK sumLtX sumLteX sumSmallestK
// @data-structure-type: persistent
// @complexities:
//   countGtX: log(N)
//   countGteX: log(N)
//   countInValRange: log(N)
//   countLtX: log(N)
//   countLteX: log(N)
//   countOccurrences: log(N)
//   kthLargest: log(N)
//   kthSmallest: log(N)
//   largestLtX: log(N)
//   largestLteX: log(N)
//   medianHigh: log(N)
//   medianLow: log(N)
//   pointGet: log(N)
//   rangeMax: log(N)
//   rangeMin: log(N)
//   rangeSum: log(N)
//   smallestGtX: log(N)
//   smallestGteX: log(N)
//   sumAbsDiffToMedian: log(N)
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
//   layout: sparse
//   node: L[1*N*log(N)] R[1*N*log(N)] C[1*N*log(N)] S[1*N*log(N)]
//   tags: none
//   other: idx[1*N] vals[1*N] root[1*N] arr[1*N] srt[1*N]
//   note: built from N given values (index, value pairs) over any index range [lo, hi], every other index 0; costs are in N; persistent seg tree over the compressed values: about N log N nodes; L/R are child pointers, C counts, S sums; the tree is over the given values only, and the zeros of [l, r] are added in closed form (they sit between the negatives and the positives)

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

    // O(1) -- a[i]
    T pointGet(int i) const { return arr[i]; }

    // O(logN) -- # of i in [l, r] with a[i] == x
    int countOccurrences(int l, int r, T x) const { return countInValRange(l, r, x, x); }

    // O(logN) -- # of i in [l, r] with lowVal <= a[i] <= highVal
    int countInValRange(int l, int r, T lowVal, T highVal) const {
        if (highVal < lowVal) return 0;
        return countBelow(l, r, ub(highVal)) - countBelow(l, r, lb(lowVal));
    }

    // O(logN) -- # of values < x in a[l..r]
    int countLtX(int l, int r, T x) const { return countBelow(l, r, lb(x)); }

    // O(logN) -- # of values <= x in a[l..r]
    int countLteX(int l, int r, T x) const { return countBelow(l, r, ub(x)); }

    // O(logN) -- # of values > x in a[l..r]
    int countGtX(int l, int r, T x) const { return r - l + 1 - countBelow(l, r, ub(x)); }

    // O(logN) -- # of values >= x in a[l..r]
    int countGteX(int l, int r, T x) const { return r - l + 1 - countBelow(l, r, lb(x)); }

    // O(logN) -- the k-th smallest of a[l..r] (k = 1 is the min); needs 1 <= k <= r - l + 1, else throws out_of_range
    T kthSmallest(int l, int r, int k) const {
        if (k < 1 || k > r - l + 1) throw out_of_range("kthSmallest: needs 1 <= k <= r - l + 1");
        return kth(l, r, k);
    }

    // O(logN) -- the k-th largest of a[l..r] (k = 1 is the max); needs 1 <= k <= r - l + 1, else throws out_of_range
    T kthLargest(int l, int r, int k) const {
        if (k < 1 || k > r - l + 1) throw out_of_range("kthLargest: needs 1 <= k <= r - l + 1");
        return kth(l, r, r - l + 2 - k);
    }

    // O(logN) -- lower median of a[l..r]: its ceil(len / 2)-th smallest
    T medianLow(int l, int r) const { return kth(l, r, (r - l + 2) / 2); }

    // O(logN) -- upper median of a[l..r]: its (floor(len / 2) + 1)-th smallest
    T medianHigh(int l, int r) const { return kth(l, r, (r - l + 1) / 2 + 1); }

    // O(logN) -- min of a[l..r]
    T rangeMin(int l, int r) const { return kth(l, r, 1); }

    // O(logN) -- max of a[l..r]
    T rangeMax(int l, int r) const { return kth(l, r, r - l + 1); }

    // O(logN) -- smallest value >= x in a[l..r], or nullopt
    optional<T> smallestGteX(int l, int r, T x) const {
        int c = countBelow(l, r, lb(x));
        if (c == r - l + 1) return nullopt;
        return kth(l, r, c + 1);
    }

    // O(logN) -- smallest value > x in a[l..r], or nullopt
    optional<T> smallestGtX(int l, int r, T x) const {
        int c = countBelow(l, r, ub(x));
        if (c == r - l + 1) return nullopt;
        return kth(l, r, c + 1);
    }

    // O(logN) -- largest value <= x in a[l..r], or nullopt
    optional<T> largestLteX(int l, int r, T x) const {
        int c = countBelow(l, r, ub(x));
        if (c == 0) return nullopt;
        return kth(l, r, c);
    }

    // O(logN) -- largest value < x in a[l..r], or nullopt
    optional<T> largestLtX(int l, int r, T x) const {
        int c = countBelow(l, r, lb(x));
        if (c == 0) return nullopt;
        return kth(l, r, c);
    }

    // O(logN) -- a[l] + ... + a[r]
    S rangeSum(int l, int r) const { return sumFirst(l, r, r - l + 1); }

    // O(logN) -- sum of the a[i] in [l, r] with lowVal <= a[i] <= highVal
    S sumInValRange(int l, int r, T lowVal, T highVal) const {
        if (highVal < lowVal) return 0;
        return sumBelow(l, r, ub(highVal)) - sumBelow(l, r, lb(lowVal));
    }

    // O(logN) -- sum of the values < x in a[l..r]
    S sumLtX(int l, int r, T x) const { return sumBelow(l, r, lb(x)); }

    // O(logN) -- sum of the values <= x in a[l..r]
    S sumLteX(int l, int r, T x) const { return sumBelow(l, r, ub(x)); }

    // O(logN) -- sum of the values > x in a[l..r]
    S sumGtX(int l, int r, T x) const { return sumFirst(l, r, r - l + 1) - sumBelow(l, r, ub(x)); }

    // O(logN) -- sum of the values >= x in a[l..r]
    S sumGteX(int l, int r, T x) const { return sumFirst(l, r, r - l + 1) - sumBelow(l, r, lb(x)); }

    // O(logN) -- sum of the k smallest values in a[l..r]; needs 0 <= k <= r - l + 1, else throws out_of_range
    S sumSmallestK(int l, int r, int k) const {
        if (k < 0 || k > r - l + 1) throw out_of_range("sumSmallestK: needs 0 <= k <= r - l + 1");
        return sumFirst(l, r, k);
    }

    // O(logN) -- sum of the k largest values in a[l..r]; needs 0 <= k <= r - l + 1, else throws out_of_range
    S sumLargestK(int l, int r, int k) const {
        int n = r - l + 1;
        if (k < 0 || k > n) throw out_of_range("sumLargestK: needs 0 <= k <= r - l + 1");
        return sumFirst(l, r, n) - sumFirst(l, r, n - k);
    }

    // O(logN) -- sum of the i-th..j-th smallest values of a[l..r] (1-indexed, inclusive); needs 1 <= i <= j <= r - l + 1,
    // else throws out_of_range
    S sumKthSmallestRange(int l, int r, int i, int j) const {
        if (i < 1 || i > j || j > r - l + 1) throw out_of_range("sumKthSmallestRange: needs 1 <= i <= j <= r - l + 1");
        return sumFirst(l, r, j) - sumFirst(l, r, i - 1);
    }

    // O(logN) -- sum of the i-th..j-th largest values of a[l..r] (1-indexed, inclusive; (1, 3) = the 3 biggest); needs
    // 1 <= i <= j <= r - l + 1, else throws out_of_range
    S sumKthLargestRange(int l, int r, int i, int j) const {
        int n = r - l + 1;
        if (i < 1 || i > j || j > n) throw out_of_range("sumKthLargestRange: needs 1 <= i <= j <= r - l + 1");
        return sumFirst(l, r, n - i + 1) - sumFirst(l, r, n - j);
    }

    // O(logN) -- sum of |a[i] - x| over i in [l, r]
    S sumAbsDiffToX(int l, int r, T x) const {
        int rk = lb(x), c = countBelow(l, r, rk);
        S s = sumBelow(l, r, rk);
        return S(x) * c - s + (sumFirst(l, r, r - l + 1) - s) - S(x) * (r - l + 1 - c);
    }

    // O(logN) -- sum of |a[i] - medianLow(l, r)| over i in [l, r]: the min total +-1 moves to make a[l..r] all equal
    S sumAbsDiffToMedian(int l, int r) const { return sumAbsDiffToX(l, r, kth(l, r, (r - l + 2) / 2)); }

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

// ======================================================================================== sparse wrapper

// The same queries over any index range [lo, hi], built from given values (index, value pairs); every other index is 0.
// The structure above runs on the given values alone (in index order). [l, r] covers given values i0..i1 and
// zeros = (r - l + 1) - (i1 - i0 + 1) zeros, and in sorted order those zeros sit right after the given negatives, so the
// k-th smallest of [l, r] is the given k-th while k <= neg, 0 while k <= neg + zeros, then the given (k - zeros)-th.
template <typename T>
struct SparsePersistentOrderStats {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    long long lo, hi;
    vector<long long> idx;
    vector<T> vals;
    PersistentOrderStats<T> inner;

    // O(N log N) -- [lo, hi] all 0 except the given values: (index, value) pairs with distinct indices; N = len(values)
    SparsePersistentOrderStats(long long lo, long long hi, vector<pair<long long, T>> values) : lo(lo), hi(hi), inner(split(values)) {}

    vector<T> split(vector<pair<long long, T>>& pts) {
        sort(pts.begin(), pts.end());
        for (auto& [i, v] : pts) idx.push_back(i), vals.push_back(v);
        return vals.empty() ? vector<T>{T(0)} : vals;  // (a dummy element when there are no given values; never queried)
    }

    // {i0, i1, zeros}: the given values inside [l, r] are i0..i1, and the rest of [l, r] is that many zeros
    tuple<int, int, long long> span(long long l, long long r) const {
        int i0 = int(lower_bound(idx.begin(), idx.end(), l) - idx.begin());
        int i1 = int(upper_bound(idx.begin(), idx.end(), r) - idx.begin()) - 1;
        return {i0, i1, (r - l + 1) - (i1 - i0 + 1)};
    }

    // O(logN) -- a[i]
    T pointGet(long long i) const {
        auto it = lower_bound(idx.begin(), idx.end(), i);
        return it != idx.end() && *it == i ? vals[it - idx.begin()] : T(0);
    }

    // O(logN) -- # of i in [l, r] with a[i] == x
    long long countOccurrences(long long l, long long r, T x) const {
        auto [i0, i1, zeros] = span(l, r);
        return (i0 <= i1 ? inner.countOccurrences(i0, i1, x) : 0) + (x == T(0) ? zeros : 0);
    }

    // O(logN) -- # of i in [l, r] with lowVal <= a[i] <= highVal
    long long countInValRange(long long l, long long r, T lowVal, T highVal) const {
        auto [i0, i1, zeros] = span(l, r);
        return (i0 <= i1 ? inner.countInValRange(i0, i1, lowVal, highVal) : 0) + (lowVal <= T(0) && T(0) <= highVal ? zeros : 0);
    }

    // O(logN) -- # of values < x in a[l..r]
    long long countLtX(long long l, long long r, T x) const {
        auto [i0, i1, zeros] = span(l, r);
        return (i0 <= i1 ? inner.countLtX(i0, i1, x) : 0) + (T(0) < x ? zeros : 0);
    }

    // O(logN) -- # of values <= x in a[l..r]
    long long countLteX(long long l, long long r, T x) const {
        auto [i0, i1, zeros] = span(l, r);
        return (i0 <= i1 ? inner.countLteX(i0, i1, x) : 0) + (T(0) <= x ? zeros : 0);
    }

    // O(logN) -- # of values > x in a[l..r]
    long long countGtX(long long l, long long r, T x) const {
        auto [i0, i1, zeros] = span(l, r);
        return (i0 <= i1 ? inner.countGtX(i0, i1, x) : 0) + (x < T(0) ? zeros : 0);
    }

    // O(logN) -- # of values >= x in a[l..r]
    long long countGteX(long long l, long long r, T x) const {
        auto [i0, i1, zeros] = span(l, r);
        return (i0 <= i1 ? inner.countGteX(i0, i1, x) : 0) + (x <= T(0) ? zeros : 0);
    }

    // O(logN) -- the k-th smallest of a[l..r] (k = 1 is the min); needs 1 <= k <= r - l + 1, else throws out_of_range
    T kthSmallest(long long l, long long r, long long k) const {
        if (k < 1 || k > r - l + 1) throw out_of_range("kthSmallest: needs 1 <= k <= r - l + 1");
        return kth(l, r, k);
    }

    // O(logN) -- the k-th largest of a[l..r] (k = 1 is the max); needs 1 <= k <= r - l + 1, else throws out_of_range
    T kthLargest(long long l, long long r, long long k) const {
        if (k < 1 || k > r - l + 1) throw out_of_range("kthLargest: needs 1 <= k <= r - l + 1");
        return kth(l, r, r - l + 2 - k);
    }

    // O(logN) -- lower median of a[l..r]: its ceil(len / 2)-th smallest
    T medianLow(long long l, long long r) const { return kth(l, r, (r - l + 2) / 2); }

    // O(logN) -- upper median of a[l..r]: its (floor(len / 2) + 1)-th smallest
    T medianHigh(long long l, long long r) const { return kth(l, r, (r - l + 1) / 2 + 1); }

    // O(logN) -- min of a[l..r]
    T rangeMin(long long l, long long r) const { return kth(l, r, 1); }

    // O(logN) -- max of a[l..r]
    T rangeMax(long long l, long long r) const { return kth(l, r, r - l + 1); }

    // O(logN) -- smallest value >= x in a[l..r], or nullopt
    optional<T> smallestGteX(long long l, long long r, T x) const {
        auto [i0, i1, zeros] = span(l, r);
        optional<T> a = i0 <= i1 ? inner.smallestGteX(i0, i1, x) : nullopt;
        if (zeros && x <= T(0)) a = a ? min(*a, T(0)) : T(0);
        return a;
    }

    // O(logN) -- smallest value > x in a[l..r], or nullopt
    optional<T> smallestGtX(long long l, long long r, T x) const {
        auto [i0, i1, zeros] = span(l, r);
        optional<T> a = i0 <= i1 ? inner.smallestGtX(i0, i1, x) : nullopt;
        if (zeros && x < T(0)) a = a ? min(*a, T(0)) : T(0);
        return a;
    }

    // O(logN) -- largest value <= x in a[l..r], or nullopt
    optional<T> largestLteX(long long l, long long r, T x) const {
        auto [i0, i1, zeros] = span(l, r);
        optional<T> a = i0 <= i1 ? inner.largestLteX(i0, i1, x) : nullopt;
        if (zeros && T(0) <= x) a = a ? max(*a, T(0)) : T(0);
        return a;
    }

    // O(logN) -- largest value < x in a[l..r], or nullopt
    optional<T> largestLtX(long long l, long long r, T x) const {
        auto [i0, i1, zeros] = span(l, r);
        optional<T> a = i0 <= i1 ? inner.largestLtX(i0, i1, x) : nullopt;
        if (zeros && T(0) < x) a = a ? max(*a, T(0)) : T(0);
        return a;
    }

    // O(logN) -- a[l] + ... + a[r]
    S rangeSum(long long l, long long r) const {
        auto [i0, i1, zeros] = span(l, r);
        return i0 <= i1 ? S(inner.rangeSum(i0, i1)) : S(0);
    }

    // O(logN) -- sum of the a[i] in [l, r] with lowVal <= a[i] <= highVal (the zeros add nothing)
    S sumInValRange(long long l, long long r, T lowVal, T highVal) const {
        auto [i0, i1, zeros] = span(l, r);
        return i0 <= i1 ? S(inner.sumInValRange(i0, i1, lowVal, highVal)) : S(0);
    }

    // O(logN) -- sum of the values < x in a[l..r] (the zeros add nothing)
    S sumLtX(long long l, long long r, T x) const {
        auto [i0, i1, zeros] = span(l, r);
        return i0 <= i1 ? S(inner.sumLtX(i0, i1, x)) : S(0);
    }

    // O(logN) -- sum of the values <= x in a[l..r] (the zeros add nothing)
    S sumLteX(long long l, long long r, T x) const {
        auto [i0, i1, zeros] = span(l, r);
        return i0 <= i1 ? S(inner.sumLteX(i0, i1, x)) : S(0);
    }

    // O(logN) -- sum of the values > x in a[l..r] (the zeros add nothing)
    S sumGtX(long long l, long long r, T x) const {
        auto [i0, i1, zeros] = span(l, r);
        return i0 <= i1 ? S(inner.sumGtX(i0, i1, x)) : S(0);
    }

    // O(logN) -- sum of the values >= x in a[l..r] (the zeros add nothing)
    S sumGteX(long long l, long long r, T x) const {
        auto [i0, i1, zeros] = span(l, r);
        return i0 <= i1 ? S(inner.sumGteX(i0, i1, x)) : S(0);
    }

    // O(logN) -- sum of the k smallest values in a[l..r]; needs 0 <= k <= r - l + 1, else throws out_of_range
    S sumSmallestK(long long l, long long r, long long k) const {
        if (k < 0 || k > r - l + 1) throw out_of_range("sumSmallestK: needs 0 <= k <= r - l + 1");
        return sumFirst(l, r, k);
    }

    // O(logN) -- sum of the k largest values in a[l..r]; needs 0 <= k <= r - l + 1, else throws out_of_range
    S sumLargestK(long long l, long long r, long long k) const {
        long long n = r - l + 1;
        if (k < 0 || k > n) throw out_of_range("sumLargestK: needs 0 <= k <= r - l + 1");
        return sumFirst(l, r, n) - sumFirst(l, r, n - k);
    }

    // O(logN) -- sum of the i-th..j-th smallest values of a[l..r] (1-indexed, inclusive); needs 1 <= i <= j <= r - l + 1,
    // else throws out_of_range
    S sumKthSmallestRange(long long l, long long r, long long i, long long j) const {
        if (i < 1 || i > j || j > r - l + 1) throw out_of_range("sumKthSmallestRange: needs 1 <= i <= j <= r - l + 1");
        return sumFirst(l, r, j) - sumFirst(l, r, i - 1);
    }

    // O(logN) -- sum of the i-th..j-th largest values of a[l..r] (1-indexed, inclusive; (1, 3) = the 3 biggest); needs
    // 1 <= i <= j <= r - l + 1, else throws out_of_range
    S sumKthLargestRange(long long l, long long r, long long i, long long j) const {
        long long n = r - l + 1;
        if (i < 1 || i > j || j > n) throw out_of_range("sumKthLargestRange: needs 1 <= i <= j <= r - l + 1");
        return sumFirst(l, r, n - i + 1) - sumFirst(l, r, n - j);
    }

    // O(logN) -- sum of |a[i] - x| over i in [l, r]
    S sumAbsDiffToX(long long l, long long r, T x) const {
        auto [i0, i1, zeros] = span(l, r);
        return (i0 <= i1 ? S(inner.sumAbsDiffToX(i0, i1, x)) : S(0)) + S(zeros) * S(x < T(0) ? -x : x);
    }

    // O(logN) -- sum of |a[i] - medianLow(l, r)| over i in [l, r]: the min total +-1 moves to make a[l..r] all equal
    S sumAbsDiffToMedian(long long l, long long r) const { return sumAbsDiffToX(l, r, kth(l, r, (r - l + 2) / 2)); }

    // the k-th smallest of a[l..r], 1 <= k <= r - l + 1
    T kth(long long l, long long r, long long k) const {
        auto [i0, i1, zeros] = span(l, r);
        long long neg = i0 <= i1 ? inner.countLtX(i0, i1, T(0)) : 0;
        if (k <= neg) return inner.kthSmallest(i0, i1, int(k));
        if (k <= neg + zeros) return T(0);
        return inner.kthSmallest(i0, i1, int(k - zeros));
    }

    // how many of the k smallest of [l, r] are given values (the rest are zeros), with i0, i1 from span
    long long given(int i0, int i1, long long zeros, long long k) const {
        long long neg = i0 <= i1 ? inner.countLtX(i0, i1, T(0)) : 0;
        return k <= neg ? k : max(neg, k - zeros);
    }
    // sum of the k smallest of a[l..r], 0 <= k <= r - l + 1 (zeros add nothing)
    S sumFirst(long long l, long long r, long long k) const {
        auto [i0, i1, zeros] = span(l, r);
        return i0 <= i1 ? S(inner.sumSmallestK(i0, i1, int(given(i0, i1, zeros, k)))) : S(0);
    }
};
