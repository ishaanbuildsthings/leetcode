// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/bit-of-trees-order-stats-sums/sparse.cpp
// @operations: countGtX countGteX countInValRange countLtX countLteX countOccurrences kthLargest kthSmallest largestLtX largestLteX medianHigh medianLow pointAdd pointAssign pointChmax pointChmin pointGet rangeMax rangeMin rangeSum smallestGtX smallestGteX sumAbsDiffToMedian sumAbsDiffToX sumGtX sumGteX sumInValRange sumKthLargestRange sumKthSmallestRange sumLargestK sumLtX sumLteX sumSmallestK
// @data-structure-type: bit-of-trees
// @complexities:
//   countGtX: log(U)*log(U)
//   countGteX: log(U)*log(U)
//   countInValRange: log(U)*log(U)
//   countLtX: log(U)*log(U)
//   countLteX: log(U)*log(U)
//   countOccurrences: log(U)*log(U)
//   kthLargest: log(U)*log(U)
//   kthSmallest: log(U)*log(U)
//   largestLtX: log(U)*log(U)
//   largestLteX: log(U)*log(U)
//   medianHigh: log(U)*log(U)
//   medianLow: log(U)*log(U)
//   pointAdd: log(U)*log(U)
//   pointAssign: log(U)*log(U)
//   pointChmax: log(U)*log(U)
//   pointChmin: log(U)*log(U)
//   pointGet: 1
//   rangeMax: log(U)*log(U)
//   rangeMin: log(U)*log(U)
//   rangeSum: log(U)*log(U)
//   smallestGtX: log(U)*log(U)
//   smallestGteX: log(U)*log(U)
//   sumAbsDiffToMedian: log(U)*log(U)
//   sumAbsDiffToX: log(U)*log(U)
//   sumGtX: log(U)*log(U)
//   sumGteX: log(U)*log(U)
//   sumInValRange: log(U)*log(U)
//   sumKthLargestRange: log(U)*log(U)
//   sumKthSmallestRange: log(U)*log(U)
//   sumLargestK: log(U)*log(U)
//   sumLtX: log(U)*log(U)
//   sumLteX: log(U)*log(U)
//   sumSmallestK: log(U)*log(U)
//   build: 1
// @memory:
//   layout: sparse
//   node: L[1*log(U)*log(U)] R[1*log(U)*log(U)] C[1*log(U)*log(U)] S[1*log(U)*log(U)]
//   tags: none
//   other: root[1*log(U)] vals[1]
//   note: any index range [lo, hi], every position starting at 0; only nonzero values are stored, and the zeros of [l, r] are counted in closed form; U = the larger of the index range and the value range [valLo, valHi]; sizes are per point update

// a[l..r] as a sorted multiset, with point updates. A Fenwick tree (BIT) over the index range [lo, hi]: BIT node j is a dynamic
// value seg tree over [valLo, valHi] holding the values of a[j - lowbit(j) .. j - 1]. The multiset of a[l..r] is the BIT
// prefix of r + 1 minus the prefix of l, so a query walks down those ~2 log N value trees together (pos adds, neg
// subtracts). Values are integers; query arguments (x, lowVal, ...) can be anything.
// Sparse: every position of [lo, hi] starts at 0 and only nonzero values are stored; the zeros of [l, r] (its length
// minus the stored values in it) sit between the stored negatives and positives.
// T: int, long long, ...; sums are kept in S (long long for small T).
template <typename T>
struct SparseDynamicOrderStats {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    struct SafeHash {
        size_t operator()(long long x) const {
            static const unsigned long long seed = chrono::steady_clock::now().time_since_epoch().count();
            unsigned long long z = (unsigned long long)x + seed + 0x9e3779b97f4a7c15ULL;
            z = (z ^ (z >> 30)) * 0xbf58476d1ce4e5b9ULL;
            z = (z ^ (z >> 27)) * 0x94d049bb133111ebULL;
            return z ^ (z >> 31);
        }
    };
    long long lo, hi, vlo, vhi;
    unordered_map<long long, T, SafeHash> vals;     // nonzero values only
    unordered_map<long long, int, SafeHash> root;   // BIT node -> its value tree (missing: empty)
    vector<int> L, R, C;                            // node 0 = the empty tree
    vector<S> Sm;

    // O(1) -- indices: any integers in [lo, hi], every position starting at 0; every value a[i] ever holds must lie in
    // [valLo, valHi] (U = the larger of the two ranges' sizes)
    SparseDynamicOrderStats(long long lo, long long hi, long long valLo, long long valHi)
        : lo(lo), hi(hi), vlo(valLo), vhi(valHi), L(1, 0), R(1, 0), C(1, 0), Sm(1, S(0)) {}

    // O(1) -- a[i]
    T pointGet(long long i) const { return vals.count(i) ? vals.at(i) : T(0); }

    // O(logN logU) -- a[i] = v
    void pointAssign(long long i, T v) {
        T old = pointGet(i);
        if (v == old) return;
        if (old != T(0)) add(i, old, -1);
        if (v != T(0)) add(i, v, 1), vals[i] = v;
        else vals.erase(i);
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

    // ---- internals ----

    // a[i] = v gains d copies in every BIT node covering i
    void add(long long i, T v, int d) {
        for (long long j = i - lo + 1, m = hi - lo + 1; j <= m; j += j & -j) {
            auto it = root.find(j);
            int t = ins(it == root.end() ? 0 : it->second, v, d);
            root[j] = t;
        }
    }

    // trees to add / subtract for a[l..r]; returns the zeros in a[l..r]
    long long sides(long long l, long long r, vector<int>& pos, vector<int>& neg) const {
        for (long long j = r - lo + 1; j; j &= j - 1) if (auto it = root.find(j); it != root.end()) pos.push_back(it->second);
        for (long long j = l - lo; j; j &= j - 1) if (auto it = root.find(j); it != root.end()) neg.push_back(it->second);
        return (r - l + 1) - total(pos, neg, C);
    }

    // # of stored (nonzero) values < x
    long long storedBelow(const vector<int>& pos, const vector<int>& neg, long long x) const {
        if (x <= vlo) return 0;
        if (x > vhi) return total(pos, neg, C);
        return belowIn(pos, neg, x).first;
    }

    // the k-th smallest of a[l..r], 1 <= k <= r - l + 1
    T kth(long long l, long long r, long long k) const {
        vector<int> pos, neg;
        long long zeros = sides(l, r, pos, neg), negs = storedBelow(pos, neg, 0);
        if (k <= negs) return kthIn(pos, neg, k);
        if (k <= negs + zeros) return T(0);
        return kthIn(pos, neg, k - zeros);
    }

    // # of values < x in a[l..r]
    long long countBelow(long long l, long long r, long long x) const {
        vector<int> pos, neg;
        long long zeros = sides(l, r, pos, neg);
        return storedBelow(pos, neg, x) + (0 < x ? zeros : 0);
    }

    // sum of the k smallest of a[l..r], 0 <= k <= r - l + 1 (zeros add nothing)
    S sumFirst(long long l, long long r, long long k) const {
        vector<int> pos, neg;
        long long zeros = sides(l, r, pos, neg), negs = storedBelow(pos, neg, 0);
        return sumFirstIn(pos, neg, k <= negs ? k : max(negs, k - zeros));
    }

    // sum of the values < x in a[l..r] (zeros add nothing)
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
