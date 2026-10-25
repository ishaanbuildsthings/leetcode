// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/persistent-online-order-stats-sums/template.cpp
// @operations: countGtX countGteX countInValRange countLtX countLteX countOccurrences kthLargest kthSmallest largestLtX largestLteX medianHigh medianLow pointGet pushBack rangeMax rangeMin rangeSum smallestGtX smallestGteX sumAbsDiffToMedian sumAbsDiffToX sumGtX sumGteX sumInValRange sumKthLargestRange sumKthSmallestRange sumLargestK sumLtX sumLteX sumSmallestK
// @data-structure-type: persistent
// @complexities:
//   countGtX: log(U)
//   countGteX: log(U)
//   countInValRange: log(U)
//   countLtX: log(U)
//   countLteX: log(U)
//   countOccurrences: log(U)
//   kthLargest: log(U)
//   kthSmallest: log(U)
//   largestLtX: log(U)
//   largestLteX: log(U)
//   medianHigh: log(U)
//   medianLow: log(U)
//   pointGet: 1
//   pushBack: log(U)
//   rangeMax: log(U)
//   rangeMin: log(U)
//   rangeSum: log(U)
//   smallestGtX: log(U)
//   smallestGteX: log(U)
//   sumAbsDiffToMedian: log(U)
//   sumAbsDiffToX: log(U)
//   sumGtX: log(U)
//   sumGteX: log(U)
//   sumInValRange: log(U)
//   sumKthLargestRange: log(U)
//   sumKthSmallestRange: log(U)
//   sumLargestK: log(U)
//   sumLtX: log(U)
//   sumLteX: log(U)
//   sumSmallestK: log(U)
//   build: N*log(U)
// @memory:
//   layout: none
//   node: L[1*N*log(U)] R[1*N*log(U)] C[1*N*log(U)] S[1*N*log(U)]
//   tags: none
//   other: root[1*N] arr[1*N]
//   note: N = every value ever added (initial array plus each pushBack); each adds one root-to-leaf path of log U nodes over the value range [valLo, valHi]

// An array that grows: pushBack(v) appends, and queries on any a[l..r] can come in between. Nothing is known up
// front, so the persistent seg tree is over the value range [valLo, valHi]: version p holds a[0..p-1], a[l..r] is
// version r + 1 minus version l, and each append adds one version. Values are integers; query arguments (x, lowVal,
// ...) can be anything. 0-indexed, inclusive.
// T: int, long long, ...; sums are kept in S (long long for small T).
template <typename T>
struct PersistentOnlineOrderStats {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    int n = 0;
    long long klo, khi;            // the tree is over the values valLo..valHi
    vector<T> arr;
    vector<int> root, L, R, C;     // node 0 = the empty tree
    vector<S> Sm;

    // O(N log U) -- arr: the initial array (may be empty), 0-indexed; every value ever added must lie in [valLo, valHi]
    // (any integers, negative is fine; U = valHi - valLo + 1)
    PersistentOnlineOrderStats(const vector<T>& a, long long valLo, long long valHi)
        : klo(valLo), khi(valHi), root(1, 0), L(1, 0), R(1, 0), C(1, 0), Sm(1, S(0)) {
        for (const T& v : a) pushBack(v);
    }

    // O(logU) -- append v (valLo <= v <= valHi): it becomes a[n], and n grows by 1
    void pushBack(T v) {
        root.push_back(ins(root.back(), (long long)v, v));
        arr.push_back(v), n++;
    }

    // O(1) -- a[i]
    T pointGet(int i) const { return arr[i]; }

    // O(logN) -- # of i in [l, r] with a[i] == x
    long long countOccurrences(long long l, long long r, T x) const { return countInValRange(l, r, x, x); }

    // O(logN) -- # of i in [l, r] with lowVal <= a[i] <= highVal
    long long countInValRange(long long l, long long r, T lowVal, T highVal) const {
        if (highVal < lowVal) return 0;
        return countBelow(l, r, ub(highVal)) - countBelow(l, r, lb(lowVal));
    }

    // O(logN) -- # of values < x in a[l..r]
    long long countLtX(long long l, long long r, T x) const { return countBelow(l, r, lb(x)); }

    // O(logN) -- # of values <= x in a[l..r]
    long long countLteX(long long l, long long r, T x) const { return countBelow(l, r, ub(x)); }

    // O(logN) -- # of values > x in a[l..r]
    long long countGtX(long long l, long long r, T x) const { return r - l + 1 - countBelow(l, r, ub(x)); }

    // O(logN) -- # of values >= x in a[l..r]
    long long countGteX(long long l, long long r, T x) const { return r - l + 1 - countBelow(l, r, lb(x)); }

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
        long long c = countBelow(l, r, lb(x));
        if (c == r - l + 1) return nullopt;
        return kth(l, r, c + 1);
    }

    // O(logN) -- smallest value > x in a[l..r], or nullopt
    optional<T> smallestGtX(long long l, long long r, T x) const {
        long long c = countBelow(l, r, ub(x));
        if (c == r - l + 1) return nullopt;
        return kth(l, r, c + 1);
    }

    // O(logN) -- largest value <= x in a[l..r], or nullopt
    optional<T> largestLteX(long long l, long long r, T x) const {
        long long c = countBelow(l, r, ub(x));
        if (c == 0) return nullopt;
        return kth(l, r, c);
    }

    // O(logN) -- largest value < x in a[l..r], or nullopt
    optional<T> largestLtX(long long l, long long r, T x) const {
        long long c = countBelow(l, r, lb(x));
        if (c == 0) return nullopt;
        return kth(l, r, c);
    }

    // O(logN) -- a[l] + ... + a[r]
    S rangeSum(long long l, long long r) const { return sumFirst(l, r, r - l + 1); }

    // O(logN) -- sum of the a[i] in [l, r] with lowVal <= a[i] <= highVal
    S sumInValRange(long long l, long long r, T lowVal, T highVal) const {
        if (highVal < lowVal) return 0;
        return sumBelow(l, r, ub(highVal)) - sumBelow(l, r, lb(lowVal));
    }

    // O(logN) -- sum of the values < x in a[l..r]
    S sumLtX(long long l, long long r, T x) const { return sumBelow(l, r, lb(x)); }

    // O(logN) -- sum of the values <= x in a[l..r]
    S sumLteX(long long l, long long r, T x) const { return sumBelow(l, r, ub(x)); }

    // O(logN) -- sum of the values > x in a[l..r]
    S sumGtX(long long l, long long r, T x) const { return sumFirst(l, r, r - l + 1) - sumBelow(l, r, ub(x)); }

    // O(logN) -- sum of the values >= x in a[l..r]
    S sumGteX(long long l, long long r, T x) const { return sumFirst(l, r, r - l + 1) - sumBelow(l, r, lb(x)); }

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

    // O(logN) -- sum of the kFrom-th..kTo-th smallest values of a[l..r] (1-indexed, inclusive); needs 1 <= kFrom <= kTo <= r - l + 1,
    // else throws out_of_range
    S sumKthSmallestRange(long long l, long long r, long long kFrom, long long kTo) const {
        if (kFrom < 1 || kFrom > kTo || kTo > r - l + 1) throw out_of_range("sumKthSmallestRange: needs 1 <= kFrom <= kTo <= r - l + 1");
        return sumFirst(l, r, kTo) - sumFirst(l, r, kFrom - 1);
    }

    // O(logN) -- sum of the kFrom-th..kTo-th largest values of a[l..r] (1-indexed, inclusive; (1, 3) = the 3 biggest); needs
    // 1 <= kFrom <= kTo <= r - l + 1, else throws out_of_range
    S sumKthLargestRange(long long l, long long r, long long kFrom, long long kTo) const {
        long long n = r - l + 1;
        if (kFrom < 1 || kFrom > kTo || kTo > n) throw out_of_range("sumKthLargestRange: needs 1 <= kFrom <= kTo <= r - l + 1");
        return sumFirst(l, r, n - kFrom + 1) - sumFirst(l, r, n - kTo);
    }

    // O(logN) -- sum of |a[i] - x| over i in [l, r]
    S sumAbsDiffToX(long long l, long long r, T x) const {
        long long rk = lb(x), c = countBelow(l, r, rk);
        S s = sumBelow(l, r, rk);
        return S(x) * c - s + (sumFirst(l, r, r - l + 1) - s) - S(x) * (r - l + 1 - c);
    }

    // O(logN) -- sum of |a[i] - medianLow(l, r)| over i in [l, r]: the min total +-1 moves to make a[l..r] all equal
    S sumAbsDiffToMedian(long long l, long long r) const { return sumAbsDiffToX(l, r, kth(l, r, (r - l + 2) / 2)); }

    static long long lb(T x) { return (long long)x; }       // "values < this" for < x
    static long long ub(T x) { return (long long)x + 1; }   // "values < this" for <= x (integers)

    // ---- internals ----

    // copy of version node with one more value (key = its value)
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
        return T(nl);
    }

    // # of i in [l, r] whose value is < x
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
        return res + S(k) * S(T(nl));
    }

    // sum of the a[i], i in [l, r], whose value is < x
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
