// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/bit-of-trees-order-stats-sums/fast.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: countGtX countGteX countInValRange countLtX countLteX countOccurrences getAll kthSmallest largestLtX largestLteX maxAll minAll pointAdd pointAssign pointChmax pointChmin pointGet rangeMax rangeMin rangeSum smallestGtX smallestGteX sumAbsDiffToX sumAll sumGtX sumGteX sumInValRange sumKthLargestRange sumKthSmallestRange sumLargestK sumLtX sumLteX sumSmallestK
// @data-structure-type: bit-of-trees
// @complexities:
//   countGtX: log(N)*log(U)
//   countGteX: log(N)*log(U)
//   countInValRange: log(N)*log(U)
//   countLtX: log(N)*log(U)
//   countLteX: log(N)*log(U)
//   countOccurrences: log(N)*log(U)
//   getAll: N
//   kthSmallest: log(N)*log(U)
//   largestLtX: log(N)*log(U)
//   largestLteX: log(N)*log(U)
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
//   sumAll: log(N)*log(U)
//   minAll: log(N)*log(U)
//   maxAll: log(N)*log(U)
//   build: N*log(N)*log(U)
// @memory:
//   layout: none
//   node: L[1*N*log(N)*log(U)] R[1*N*log(N)*log(U)] C[1*N*log(N)*log(U)] S[1*N*log(N)*log(U)]
//   tags: none
//   other: root[1*N] arr[1*N]
//   note: BIT over positions, each BIT node a dynamic value seg tree over [valLo, valHi] (U = its size); nodes are never freed, so each point update adds up to 2 log N log U of them

// a[l..r] as a sorted multiset, with point updates. A Fenwick tree (BIT) over positions: BIT node j is a dynamic
// value seg tree over [valLo, valHi] holding the values of a[j - lowbit(j) .. j - 1]. The multiset of a[l..r] is the
// BIT
// prefix of r + 1 minus the prefix of l, so a query walks down those ~2 log N value trees together (pos adds, neg
// subtracts). Values are integers; query arguments (x, lowVal, ...) can be anything.
// T: int, long long, ...; sums are kept in S (long long for small T).
// FAST MODE drawbacks compared with template.cpp:
//   - sanitizers are skipped inside this template, so a bad access in it goes unreported
// Same public operations and answers, same limits; it needs GCC or Clang and C++17.
#ifdef __SSE2__
#include <immintrin.h>
#endif

// LEETCODE_NO_SANITIZE skips sanitizers in a function. It only changes anything where sanitizers run, like LeetCode: on
// Codeforces it compiles and does nothing.
// This template already uses it. To go further, put it on the one function with your hot loop:
//   LEETCODE_NO_SANITIZE long long maxSum(vector<int>& nums, int k) {
// A lambda needs its own: [&](int x) LEETCODE_NO_SANITIZE { ... }. It does not carry into anything that function calls.
// Inside a marked function use raw pointers and plain comparisons, not vector[] and min / max, or it can get slower.
// Bad memory accesses in a marked function go unreported.
#ifndef LEETCODE_NO_SANITIZE
#define LEETCODE_NO_SANITIZE __attribute__((no_sanitize("address"), no_sanitize("undefined")))
#endif
#define LEETCODE_NO_SANITIZE_INLINE LEETCODE_NO_SANITIZE __attribute__((always_inline)) inline

// A vector whose [] and size() always inline, even with sanitizers skipped (libstdc++ only; elsewhere a plain vector)
template <typename U>
struct HotVector : vector<U> {
    using vector<U>::vector;
    HotVector() = default;
    HotVector(const vector<U>& other) : vector<U>(other) {}
    HotVector(vector<U>&& other) : vector<U>(move(other)) {}
#ifdef __GLIBCXX__
    LEETCODE_NO_SANITIZE_INLINE typename vector<U>::reference operator[](size_t i) { return this->_M_impl._M_start[i]; }
    LEETCODE_NO_SANITIZE_INLINE typename vector<U>::const_reference operator[](size_t i) const {
        return this->_M_impl._M_start[i];
    }
    LEETCODE_NO_SANITIZE_INLINE size_t size() const { return size_t(this->_M_impl._M_finish - this->_M_impl._M_start); }
#endif
};

template <typename T>
struct DynamicOrderStats {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    int n;
    long long vlo, vhi;
    HotVector<T> arr;
    HotVector<int> root;  // root[j]: BIT node j's value tree; node 0 = the empty tree
    struct Node {  // a node's fields side by side: a walk reads them together (faster than one array per field)
        S Sm = S(0);
        int L = 0;
        int R = 0;
        int C = 0;
    };
    HotVector<Node> nd;  // node 0 = the empty tree

    // O(N log N log U) -- arr: the initial array, 0-indexed; every value a[i] ever holds must lie in [valLo, valHi]
    // (any integers, negative is fine; U = valHi - valLo + 1)
    DynamicOrderStats(const vector<T>& a, long long valLo, long long valHi)
        : n((int)a.size()), vlo(valLo), vhi(valHi), arr(a), root(n + 1, 0), nd(1) {
        for (int i = 0; i < n; i++) add(i, a[i], 1);
    }

    // O(1) -- a[i]; needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE T pointGet(long long i) const {
        if (i < 0 || i >= n) throw out_of_range("pointGet: needs 0 <= i < n");
        return arr[i];
    }

    // O(N) -- the whole array (a copy)
    LEETCODE_NO_SANITIZE vector<T> getAll() const { return arr; }

    // O(logN logU) -- a[i] = v; needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAssign(long long i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointAssign: needs 0 <= i < n");
        T old = pointGet(i);
        if (v == old) return;
        add(i, old, -1), add(i, v, 1), arr[i] = v;
    }

    // O(logN logU) -- a[i] += v; needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAdd(long long i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointAdd: needs 0 <= i < n");
        pointAssign(i, pointGet(i) + v);
    }

    // O(logN logU) -- a[i] = max(a[i], v); needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointChmax(long long i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointChmax: needs 0 <= i < n");
        pointAssign(i, max(pointGet(i), v));
    }

    // O(logN logU) -- a[i] = min(a[i], v); needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointChmin(long long i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointChmin: needs 0 <= i < n");
        pointAssign(i, min(pointGet(i), v));
    }

    // O(logN) -- # of i in [l, r] with a[i] == x; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE long long countOccurrences(long long l, long long r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("countOccurrences: needs 0 <= l <= r < n");
        return countInValRange(l, r, x, x);
    }

    // O(logN) -- # of i in [l, r] with lowVal <= a[i] <= highVal; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE long long countInValRange(long long l, long long r, T lowVal, T highVal) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("countInValRange: needs 0 <= l <= r < n");
        if (highVal < lowVal) return 0;
        return countBelow(l, r, ub(highVal)) - countBelow(l, r, lb(lowVal));
    }

    // O(logN) -- # of values < x in a[l..r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE long long countLtX(long long l, long long r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("countLtX: needs 0 <= l <= r < n");
        return countBelow(l, r, lb(x));
    }

    // O(logN) -- # of values <= x in a[l..r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE long long countLteX(long long l, long long r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("countLteX: needs 0 <= l <= r < n");
        return countBelow(l, r, ub(x));
    }

    // O(logN) -- # of values > x in a[l..r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE long long countGtX(long long l, long long r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("countGtX: needs 0 <= l <= r < n");
        return r - l + 1 - countBelow(l, r, ub(x));
    }

    // O(logN) -- # of values >= x in a[l..r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE long long countGteX(long long l, long long r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("countGteX: needs 0 <= l <= r < n");
        return r - l + 1 - countBelow(l, r, lb(x));
    }

    // O(logN) -- the k-th smallest of a[l..r] (k = 1 is the min); needs 0 <= l <= r < n and 1 <= k <= r - l + 1, else
    // throws out_of_range
    LEETCODE_NO_SANITIZE T kthSmallest(long long l, long long r, long long k) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("kthSmallest: needs 0 <= l <= r < n");
        if (k < 1 || k > r - l + 1) throw out_of_range("kthSmallest: needs 1 <= k <= r - l + 1");
        return kth(l, r, k);
    }

    // O(logN) -- min of a[l..r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE T rangeMin(long long l, long long r) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeMin: needs 0 <= l <= r < n");
        return kth(l, r, 1);
    }

    // O(logN) -- max of a[l..r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE T rangeMax(long long l, long long r) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeMax: needs 0 <= l <= r < n");
        return kth(l, r, r - l + 1);
    }

    // O(logN) -- smallest value >= x in a[l..r], or nullopt; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE optional<T> smallestGteX(long long l, long long r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("smallestGteX: needs 0 <= l <= r < n");
        long long c = countBelow(l, r, lb(x));
        if (c == r - l + 1) return nullopt;
        return kth(l, r, c + 1);
    }

    // O(logN) -- smallest value > x in a[l..r], or nullopt; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE optional<T> smallestGtX(long long l, long long r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("smallestGtX: needs 0 <= l <= r < n");
        long long c = countBelow(l, r, ub(x));
        if (c == r - l + 1) return nullopt;
        return kth(l, r, c + 1);
    }

    // O(logN) -- largest value <= x in a[l..r], or nullopt; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE optional<T> largestLteX(long long l, long long r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("largestLteX: needs 0 <= l <= r < n");
        long long c = countBelow(l, r, ub(x));
        if (c == 0) return nullopt;
        return kth(l, r, c);
    }

    // O(logN) -- largest value < x in a[l..r], or nullopt; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE optional<T> largestLtX(long long l, long long r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("largestLtX: needs 0 <= l <= r < n");
        long long c = countBelow(l, r, lb(x));
        if (c == 0) return nullopt;
        return kth(l, r, c);
    }

    // O(logN) -- a[l] + ... + a[r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE S rangeSum(long long l, long long r) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeSum: needs 0 <= l <= r < n");
        return sumFirst(l, r, r - l + 1);
    }

    // O(logN) -- sum of the a[i] in [l, r] with lowVal <= a[i] <= highVal; needs 0 <= l <= r < n, else throws
    // out_of_range
    LEETCODE_NO_SANITIZE S sumInValRange(long long l, long long r, T lowVal, T highVal) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("sumInValRange: needs 0 <= l <= r < n");
        if (highVal < lowVal) return 0;
        return sumBelow(l, r, ub(highVal)) - sumBelow(l, r, lb(lowVal));
    }

    // O(logN) -- sum of the values < x in a[l..r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE S sumLtX(long long l, long long r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("sumLtX: needs 0 <= l <= r < n");
        return sumBelow(l, r, lb(x));
    }

    // O(logN) -- sum of the values <= x in a[l..r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE S sumLteX(long long l, long long r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("sumLteX: needs 0 <= l <= r < n");
        return sumBelow(l, r, ub(x));
    }

    // O(logN) -- sum of the values > x in a[l..r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE S sumGtX(long long l, long long r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("sumGtX: needs 0 <= l <= r < n");
        return sumFirst(l, r, r - l + 1) - sumBelow(l, r, ub(x));
    }

    // O(logN) -- sum of the values >= x in a[l..r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE S sumGteX(long long l, long long r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("sumGteX: needs 0 <= l <= r < n");
        return sumFirst(l, r, r - l + 1) - sumBelow(l, r, lb(x));
    }

    // O(logN) -- sum of the k smallest values in a[l..r]; needs 0 <= l <= r < n and 0 <= k <= r - l + 1, else throws
    // out_of_range
    LEETCODE_NO_SANITIZE S sumSmallestK(long long l, long long r, long long k) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("sumSmallestK: needs 0 <= l <= r < n");
        if (k < 0 || k > r - l + 1) throw out_of_range("sumSmallestK: needs 0 <= k <= r - l + 1");
        return sumFirst(l, r, k);
    }

    // O(logN) -- sum of the k largest values in a[l..r]; needs 0 <= l <= r < n and 0 <= k <= r - l + 1, else throws
    // out_of_range
    LEETCODE_NO_SANITIZE S sumLargestK(long long l, long long r, long long k) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("sumLargestK: needs 0 <= l <= r < n");
        long long n = r - l + 1;
        if (k < 0 || k > n) throw out_of_range("sumLargestK: needs 0 <= k <= r - l + 1");
        return sumFirst(l, r, n) - sumFirst(l, r, n - k);
    }

    // O(logN) -- sum of the kFrom-th..kTo-th smallest values of a[l..r] (1-indexed, inclusive); needs 0 <= l <= r < n
    // and 1 <= kFrom <= kTo <= r - l + 1, else throws out_of_range
    LEETCODE_NO_SANITIZE S sumKthSmallestRange(long long l, long long r, long long kFrom, long long kTo) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("sumKthSmallestRange: needs 0 <= l <= r < n");
        if (kFrom < 1 || kFrom > kTo || kTo > r - l + 1)
            throw out_of_range("sumKthSmallestRange: needs 1 <= kFrom <= kTo <= r - l + 1");
        return sumFirst(l, r, kTo) - sumFirst(l, r, kFrom - 1);
    }

    // O(logN) -- sum of the kFrom-th..kTo-th largest values of a[l..r] (1-indexed, inclusive; (1, 3) = the 3
    // biggest); needs 0 <= l <= r < n and 1 <= kFrom <= kTo <= r - l + 1, else throws out_of_range
    LEETCODE_NO_SANITIZE S sumKthLargestRange(long long l, long long r, long long kFrom, long long kTo) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("sumKthLargestRange: needs 0 <= l <= r < n");
        long long n = r - l + 1;
        if (kFrom < 1 || kFrom > kTo || kTo > n)
            throw out_of_range("sumKthLargestRange: needs 1 <= kFrom <= kTo <= r - l + 1");
        return sumFirst(l, r, n - kFrom + 1) - sumFirst(l, r, n - kTo);
    }

    // O(logN) -- sum of |a[i] - x| over i in [l, r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE S sumAbsDiffToX(long long l, long long r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("sumAbsDiffToX: needs 0 <= l <= r < n");
        long long rk = lb(x), c = countBelow(l, r, rk);
        S s = sumBelow(l, r, rk);
        return S(x) * c - s + (sumFirst(l, r, r - l + 1) - s) - S(x) * (r - l + 1 - c);
    }

    // O(log(N)*log(U)) -- sum of the whole array a[0..n-1] (rangeSum(0, n - 1)); needs n >= 1, else throws out_of_range
    LEETCODE_NO_SANITIZE auto sumAll() {
        if (n < 1) throw out_of_range("sumAll: needs n >= 1");
        return rangeSum(0, n - 1);
    }

    // O(log(N)*log(U)) -- min of the whole array a[0..n-1] (rangeMin(0, n - 1)); needs n >= 1, else throws out_of_range
    LEETCODE_NO_SANITIZE auto minAll() {
        if (n < 1) throw out_of_range("minAll: needs n >= 1");
        return rangeMin(0, n - 1);
    }

    // O(log(N)*log(U)) -- max of the whole array a[0..n-1] (rangeMax(0, n - 1)); needs n >= 1, else throws out_of_range
    LEETCODE_NO_SANITIZE auto maxAll() {
        if (n < 1) throw out_of_range("maxAll: needs n >= 1");
        return rangeMax(0, n - 1);
    }

    // ---- internals ----

    // a[i] = v gains d copies in every BIT node covering i
    LEETCODE_NO_SANITIZE void add(long long i, T v, int d) {
        for (long long j = i + 1; j <= n; j += j & -j) root[j] = ins(root[j], v, d);
    }

    // trees to add / subtract for a[l..r]
    LEETCODE_NO_SANITIZE void sides(long long l, long long r, vector<int>& pos, vector<int>& neg) const {
        for (long long j = r + 1; j; j &= j - 1) pos.push_back(root[j]);
        for (long long j = l; j; j &= j - 1) neg.push_back(root[j]);
    }

    // the k-th smallest of a[l..r], 1 <= k <= r - l + 1
    LEETCODE_NO_SANITIZE T kth(long long l, long long r, long long k) const {
        vector<int> pos, neg;
        sides(l, r, pos, neg);
        return kthIn(pos, neg, k);
    }

    // # of values < x in a[l..r]
    LEETCODE_NO_SANITIZE long long countBelow(long long l, long long r, long long x) const {
        if (x <= vlo) return 0;
        if (x > vhi) return r - l + 1;
        vector<int> pos, neg;
        sides(l, r, pos, neg);
        return belowIn(pos, neg, x).first;
    }

    // sum of the k smallest of a[l..r], 0 <= k <= r - l + 1
    LEETCODE_NO_SANITIZE S sumFirst(long long l, long long r, long long k) const {
        vector<int> pos, neg;
        sides(l, r, pos, neg);
        return sumFirstIn(pos, neg, k);
    }

    // sum of the values < x in a[l..r]
    LEETCODE_NO_SANITIZE S sumBelow(long long l, long long r, long long x) const {
        if (x <= vlo) return 0;
        vector<int> pos, neg;
        sides(l, r, pos, neg);
        return x > vhi ? total(pos, neg, [&](int t) { return nd[t].Sm; }) : belowIn(pos, neg, x).second;
    }

    // ---- internals: walks over the value trees in pos (added) and neg (subtracted) ----

    // a value threshold as "values < this": lb(x) = x, ub(x) = x + 1 (integers)
    LEETCODE_NO_SANITIZE static long long lb(T x) { return (long long)x; }
    LEETCODE_NO_SANITIZE static long long ub(T x) { return (long long)x + 1; }

    LEETCODE_NO_SANITIZE int newNode() {
        Node n;
        n.L = 0, n.R = 0, n.C = 0, n.Sm = S(0);
        nd.push_back(n);
        return (int)nd.size() - 1;
    }

    // tree t (0: a new one) with d more copies of v
    LEETCODE_NO_SANITIZE int ins(int t, T v, int d) {
        if (!t) t = newNode();
        int top = t;
        long long nl = vlo, nh = vhi;
        while (true) {
            nd[t].C += d;
            nd[t].Sm += S(v) * d;
            if (nl == nh) return top;
            long long mid = nl + (nh - nl) / 2;
            if (v <= mid) {
                if (!nd[t].L) { int x = newNode(); nd[t].L = x; }
                t = nd[t].L, nh = mid;
            } else {
                if (!nd[t].R) { int x = newNode(); nd[t].R = x; }
                t = nd[t].R, nl = mid + 1;
            }
        }
    }

    // get(t): node t's field
    template <class F> auto total(const vector<int>& pos, const vector<int>& neg, F get) const {
        decltype(get(0)) s = 0;
        for (int t : pos) s += get(t);
        for (int t : neg) s -= get(t);
        return s;
    }
    LEETCODE_NO_SANITIZE void goLeft(vector<int>& v) const { for (int& t : v) t = nd[t].L; }
    LEETCODE_NO_SANITIZE void goRight(vector<int>& v) const { for (int& t : v) t = nd[t].R; }
    LEETCODE_NO_SANITIZE long long leftCount(const vector<int>& pos, const vector<int>& neg) const {
        long long c = 0;
        for (int t : pos) c += nd[nd[t].L].C;
        for (int t : neg) c -= nd[nd[t].L].C;
        return c;
    }

    // the k-th smallest value, 1 <= k <= the trees' count
    LEETCODE_NO_SANITIZE T kthIn(vector<int> pos, vector<int> neg, long long k) const {
        long long nl = vlo, nh = vhi;
        while (nl != nh) {
            long long mid = nl + (nh - nl) / 2, c = leftCount(pos, neg);
            if (k <= c) goLeft(pos), goLeft(neg), nh = mid;
            else k -= c, goRight(pos), goRight(neg), nl = mid + 1;
        }
        return T(nl);
    }

    // # of values < x, valLo < x <= valHi, and their sum
    LEETCODE_NO_SANITIZE pair<long long, S> belowIn(vector<int> pos, vector<int> neg, long long x) const {
        long long nl = vlo, nh = vhi, cnt = 0;
        S sm = 0;
        while (nl != nh) {
            long long mid = nl + (nh - nl) / 2;
            if (x <= mid) goLeft(pos), goLeft(neg), nh = mid;
            else {  // the whole left half is below x
                cnt += leftCount(pos, neg);
                for (int t : pos) sm += nd[nd[t].L].Sm;
                for (int t : neg) sm -= nd[nd[t].L].Sm;
                goRight(pos), goRight(neg), nl = mid + 1;
            }
        }
        return {cnt, sm};
    }

    // sum of the k smallest values, 0 <= k <= the trees' count
    LEETCODE_NO_SANITIZE S sumFirstIn(vector<int> pos, vector<int> neg, long long k) const {
        if (k <= 0) return 0;
        long long nl = vlo, nh = vhi;
        S res = 0;
        while (nl != nh) {
            long long mid = nl + (nh - nl) / 2, c = leftCount(pos, neg);
            if (k <= c) goLeft(pos), goLeft(neg), nh = mid;
            else {  // the whole left half is among the k smallest
                k -= c;
                for (int t : pos) res += nd[nd[t].L].Sm;
                for (int t : neg) res -= nd[nd[t].L].Sm;
                goRight(pos), goRight(neg), nl = mid + 1;
            }
        }
        return res + S(k) * S(nl);
    }
};
