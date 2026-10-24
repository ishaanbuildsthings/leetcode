// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/bit-of-trees-order-stats-sums/template.cpp
// @operations: countGtX countGteX countInValRange countLtX countLteX countOccurrences kthLargest kthSmallest largestLtX largestLteX medianHigh medianLow pointAdd pointAssign pointChmax pointChmin pointGet rangeMax rangeMin rangeSum smallestGtX smallestGteX sumAbsDiffToMedian sumAbsDiffToX sumGtX sumGteX sumInValRange sumKthLargestRange sumKthSmallestRange sumLargestK sumLtX sumLteX sumSmallestK
// @data-structure-type: bit-of-trees
// @complexities:
//   countGtX: log(N)*log(U)
//   countGteX: log(N)*log(U)
//   countInValRange: log(N)*log(U)
//   countLtX: log(N)*log(U)
//   countLteX: log(N)*log(U)
//   countOccurrences: log(N)*log(U)
//   kthLargest: log(N)*log(U)
//   kthSmallest: log(N)*log(U)
//   largestLtX: log(N)*log(U)
//   largestLteX: log(N)*log(U)
//   medianHigh: log(N)*log(U)
//   medianLow: log(N)*log(U)
//   pointAdd: log(N)*log(U)
//   pointAssign: log(N)*log(U)
//   pointChmax: log(N)*log(U)
//   pointChmin: log(N)*log(U)
//   pointGet: 1
//   rangeMax: log(N)*log(U)
//   rangeMin: log(N)*log(U)
//   rangeSum: log(N)*log(U)
//   smallestGtX: log(N)*log(U)
//   smallestGteX: log(N)*log(U)
//   sumAbsDiffToMedian: log(N)*log(U)
//   sumAbsDiffToX: log(N)*log(U)
//   sumGtX: log(N)*log(U)
//   sumGteX: log(N)*log(U)
//   sumInValRange: log(N)*log(U)
//   sumKthLargestRange: log(N)*log(U)
//   sumKthSmallestRange: log(N)*log(U)
//   sumLargestK: log(N)*log(U)
//   sumLtX: log(N)*log(U)
//   sumLteX: log(N)*log(U)
//   sumSmallestK: log(N)*log(U)
//   build: N*log(N)*log(U)
// @memory:
//   layout: none
//   node: L[1*N*log(N)*log(U)] R[1*N*log(N)*log(U)] C[1*N*log(N)*log(U)] S[1*N*log(N)*log(U)]
//   tags: none
//   other: root[1*N] arr[1*N]
//   note: BIT over positions, each BIT node a dynamic value seg tree over [valLo, valHi] (U = its size); nodes are never freed, so each point update adds up to 2 log N log U of them

// a[l..r] as a sorted multiset, with point updates. A Fenwick tree (BIT) over positions: BIT node j is a dynamic
// value seg tree over [valLo, valHi] holding the values of a[j - lowbit(j) .. j - 1]. The multiset of a[l..r] is the BIT
// prefix of r + 1 minus the prefix of l, so a query walks down those ~2 log N value trees together (pos adds, neg
// subtracts). Values are integers; query arguments (x, lowVal, ...) can be anything.
// T: int, long long, ...; sums are kept in S (long long for small T).
template <typename T>
struct DynamicOrderStats {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    int n;
    long long vlo, vhi;
    vector<T> arr;
    vector<int> root, L, R, C;  // root[j]: BIT node j's value tree; node 0 = the empty tree
    vector<S> Sm;

    // O(N log N log U) -- arr: the initial array, 0-indexed; every value a[i] ever holds must lie in [valLo, valHi]
    // (any integers, negative is fine; U = valHi - valLo + 1)
    DynamicOrderStats(const vector<T>& a, long long valLo, long long valHi)
        : n((int)a.size()), vlo(valLo), vhi(valHi), arr(a), root(n + 1, 0), L(1, 0), R(1, 0), C(1, 0), Sm(1, S(0)) {
        for (int i = 0; i < n; i++) add(i, a[i], 1);
    }

    // O(1) -- a[i]
    T pointGet(long long i) const { return arr[i]; }

    // O(logN logU) -- a[i] = v
    void pointAssign(long long i, T v) {
        T old = pointGet(i);
        if (v == old) return;
        add(i, old, -1), add(i, v, 1), arr[i] = v;
    }

    // O(logN logU) -- a[i] += v
    void pointAdd(long long i, T v) { pointAssign(i, pointGet(i) + v); }

    // O(logN logU) -- a[i] = max(a[i], v)
    void pointChmax(long long i, T v) { pointAssign(i, max(pointGet(i), v)); }

    // O(logN logU) -- a[i] = min(a[i], v)
    void pointChmin(long long i, T v) { pointAssign(i, min(pointGet(i), v)); }

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
        long long rk = lb(x), c = countBelow(l, r, rk);
        S s = sumBelow(l, r, rk);
        return S(x) * c - s + (sumFirst(l, r, r - l + 1) - s) - S(x) * (r - l + 1 - c);
    }

    // O(logN) -- sum of |a[i] - medianLow(l, r)| over i in [l, r]: the min total +-1 moves to make a[l..r] all equal
    S sumAbsDiffToMedian(long long l, long long r) const { return sumAbsDiffToX(l, r, kth(l, r, (r - l + 2) / 2)); }

    // ---- internals ----

    // a[i] = v gains d copies in every BIT node covering i
    void add(long long i, T v, int d) {
        for (long long j = i + 1; j <= n; j += j & -j) root[j] = ins(root[j], v, d);
    }

    // trees to add / subtract for a[l..r]
    void sides(long long l, long long r, vector<int>& pos, vector<int>& neg) const {
        for (long long j = r + 1; j; j &= j - 1) pos.push_back(root[j]);
        for (long long j = l; j; j &= j - 1) neg.push_back(root[j]);
    }

    // the k-th smallest of a[l..r], 1 <= k <= r - l + 1
    T kth(long long l, long long r, long long k) const {
        vector<int> pos, neg;
        sides(l, r, pos, neg);
        return kthIn(pos, neg, k);
    }

    // # of values < x in a[l..r]
    long long countBelow(long long l, long long r, long long x) const {
        if (x <= vlo) return 0;
        if (x > vhi) return r - l + 1;
        vector<int> pos, neg;
        sides(l, r, pos, neg);
        return belowIn(pos, neg, x).first;
    }

    // sum of the k smallest of a[l..r], 0 <= k <= r - l + 1
    S sumFirst(long long l, long long r, long long k) const {
        vector<int> pos, neg;
        sides(l, r, pos, neg);
        return sumFirstIn(pos, neg, k);
    }

    // sum of the values < x in a[l..r]
    S sumBelow(long long l, long long r, long long x) const {
        if (x <= vlo) return 0;
        vector<int> pos, neg;
        sides(l, r, pos, neg);
        return x > vhi ? total(pos, neg, Sm) : belowIn(pos, neg, x).second;
    }

    // ---- internals: walks over the value trees in pos (added) and neg (subtracted) ----

    // a value threshold as "values < this": lb(x) = x, ub(x) = x + 1 (integers)
    static long long lb(T x) { return (long long)x; }
    static long long ub(T x) { return (long long)x + 1; }

    int newNode() {
        L.push_back(0), R.push_back(0), C.push_back(0), Sm.push_back(S(0));
        return (int)C.size() - 1;
    }

    // tree t (0: a new one) with d more copies of v
    int ins(int t, T v, int d) {
        if (!t) t = newNode();
        int top = t;
        long long nl = vlo, nh = vhi;
        while (true) {
            C[t] += d;
            Sm[t] += S(v) * d;
            if (nl == nh) return top;
            long long mid = nl + (nh - nl) / 2;
            if (v <= mid) {
                if (!L[t]) { int x = newNode(); L[t] = x; }
                t = L[t], nh = mid;
            } else {
                if (!R[t]) { int x = newNode(); R[t] = x; }
                t = R[t], nl = mid + 1;
            }
        }
    }

    template <class A> auto total(const vector<int>& pos, const vector<int>& neg, const vector<A>& a) const {
        A s = 0;
        for (int t : pos) s += a[t];
        for (int t : neg) s -= a[t];
        return s;
    }
    void goLeft(vector<int>& v) const { for (int& t : v) t = L[t]; }
    void goRight(vector<int>& v) const { for (int& t : v) t = R[t]; }
    long long leftCount(const vector<int>& pos, const vector<int>& neg) const {
        long long c = 0;
        for (int t : pos) c += C[L[t]];
        for (int t : neg) c -= C[L[t]];
        return c;
    }

    // the k-th smallest value, 1 <= k <= the trees' count
    T kthIn(vector<int> pos, vector<int> neg, long long k) const {
        long long nl = vlo, nh = vhi;
        while (nl != nh) {
            long long mid = nl + (nh - nl) / 2, c = leftCount(pos, neg);
            if (k <= c) goLeft(pos), goLeft(neg), nh = mid;
            else k -= c, goRight(pos), goRight(neg), nl = mid + 1;
        }
        return T(nl);
    }

    // # of values < x, valLo < x <= valHi, and their sum
    pair<long long, S> belowIn(vector<int> pos, vector<int> neg, long long x) const {
        long long nl = vlo, nh = vhi, cnt = 0;
        S sm = 0;
        while (nl != nh) {
            long long mid = nl + (nh - nl) / 2;
            if (x <= mid) goLeft(pos), goLeft(neg), nh = mid;
            else {  // the whole left half is below x
                cnt += leftCount(pos, neg);
                for (int t : pos) sm += Sm[L[t]];
                for (int t : neg) sm -= Sm[L[t]];
                goRight(pos), goRight(neg), nl = mid + 1;
            }
        }
        return {cnt, sm};
    }

    // sum of the k smallest values, 0 <= k <= the trees' count
    S sumFirstIn(vector<int> pos, vector<int> neg, long long k) const {
        if (k <= 0) return 0;
        long long nl = vlo, nh = vhi;
        S res = 0;
        while (nl != nh) {
            long long mid = nl + (nh - nl) / 2, c = leftCount(pos, neg);
            if (k <= c) goLeft(pos), goLeft(neg), nh = mid;
            else {  // the whole left half is among the k smallest
                k -= c;
                for (int t : pos) res += Sm[L[t]];
                for (int t : neg) res -= Sm[L[t]];
                goRight(pos), goRight(neg), nl = mid + 1;
            }
        }
        return res + S(k) * S(nl);
    }
};
