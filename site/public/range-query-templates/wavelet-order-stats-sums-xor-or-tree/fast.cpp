// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/wavelet-order-stats-sums-xor-or-tree/fast.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: countGtX countGteX countInValRange countLtX countLteX countOccurrences kthSmallest largestLtX largestLteX orGtX orGteX orInValRange orLtX orLteX pointGet rangeMax rangeMin rangeSum smallestGtX smallestGteX sumAbsDiffToX sumGtX sumGteX sumInValRange sumKthLargestRange sumKthSmallestRange sumLargestK sumLtX sumLteX sumSmallestK xorGtX xorGteX xorInValRange xorLtX xorLteX
// @data-structure-type: wavelet
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
//   orGtX: log^2(N)
//   orGteX: log^2(N)
//   orInValRange: log^2(N)
//   orLtX: log^2(N)
//   orLteX: log^2(N)
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
//   xorGtX: log(N)
//   xorGteX: log(N)
//   xorInValRange: log(N)
//   xorLtX: log(N)
//   xorLteX: log(N)
//   build: N*log(N)
// @memory:
//   layout: none
//   node: zeros[1*N*log(N)] zsum[1*N*log(N)] arr[1*N] srt[1*N] xt[1*N*log(N)] ot[2*N*log(N)]
//   tags: none
//   other: none
//   note: wavelet matrix: one row of N + 1 prefix counts per bit of the compressed value, plus one row of prefix sums of the values that go left; xor by value: per level, prefix xors of its order; OR by value: per level, a segment tree over its order (O(log N) a window)

// Static array. Each query treats a[l..r] (0-indexed, inclusive) as a sorted multiset. Values are compressed to ranks
// 0..m-1 once, so costs are log of the number of distinct values, never of the value range; query arguments (x,
// lowVal, ...) can be anything. Level d of the wavelet matrix (top bit first) stably splits the current order into the
// ranks with that bit 0, then 1; zeros[d][i] = # of the first i elements of level d's order with the bit 0.
// zsum[d][i] = sum of the values among the first i elements of level d's order whose bit is 0.
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
    LEETCODE_NO_SANITIZE_INLINE typename vector<U>::const_reference operator[](size_t i) const { return this->_M_impl._M_start[i]; }
    LEETCODE_NO_SANITIZE_INLINE size_t size() const { return size_t(this->_M_impl._M_finish - this->_M_impl._M_start); }
#endif
};

template <typename T>
struct WaveletMatrix {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    int n, m, bits;
    HotVector<T> arr, srt;  // srt: sorted distinct values
    HotVector<int> zeros;   // level lv's row is zeros[lv * (n + 1) .. lv * (n + 1) + n]
    HotVector<S> zsum;      // same layout as zeros
    HotVector<vector<T>> xt;  // per level, xor over its order
    HotVector<vector<T>> ot;  // per level, OR over its order

    // O(N log N) -- arr: the initial array, 0-indexed
    explicit WaveletMatrix(const vector<T>& a) : n((int)a.size()), arr(a), srt(a) {
        sort(srt.begin(), srt.end());
        srt.erase(unique(srt.begin(), srt.end()), srt.end());
        m = (int)srt.size();
        bits = 1;
        while ((1 << bits) < m) bits++;
        zeros.assign((size_t)bits * (n + 1), 0);
        zsum.assign((size_t)bits * (n + 1), S(0));
        xt.resize(bits + 1);
        ot.resize(bits + 1);
        vector<int> cur(n), nxt(n);
        for (int i = 0; i < n; i++) cur[i] = lb(a[i]);
        vector<T> vals(n);
        auto order = [&](int lv) {  // the level's order, as values
            for (int i = 0; i < n; i++) vals[i] = srt[cur[i]];
            xorBuild(lv, vals);
            orBuild(lv, vals);
        };
        for (int lv = 0; lv < bits; lv++) {
            order(lv);
            int d = bits - 1 - lv, k = 0, *z = &zeros[(size_t)lv * (n + 1)];
            S* zs = &zsum[(size_t)lv * (n + 1)];
            for (int i = 0; i < n; i++) {
                bool one = (cur[i] >> d) & 1;
                z[i + 1] = z[i] + !one;
                zs[i + 1] = zs[i] + (one ? S(0) : S(srt[cur[i]]));
            }
            for (int v : cur) if (!((v >> d) & 1)) nxt[k++] = v;
            for (int v : cur) if ((v >> d) & 1) nxt[k++] = v;
            swap(cur, nxt);
        }
        order(bits);  // (the final order)
    }

    // O(1) -- a[i]; needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE T pointGet(int i) const {
        if (i < 0 || i >= n) throw out_of_range("pointGet: needs 0 <= i < n");
        return arr[i];
    }

    // O(logN) -- # of i in [l, r] with a[i] == x; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE int countOccurrences(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("countOccurrences: needs 0 <= l <= r < n");
        return countInValRange(l, r, x, x);
    }

    // O(logN) -- # of i in [l, r] with lowVal <= a[i] <= highVal; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE int countInValRange(int l, int r, T lowVal, T highVal) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("countInValRange: needs 0 <= l <= r < n");
        if (highVal < lowVal) return 0;
        return countBelow(l, r, ub(highVal)) - countBelow(l, r, lb(lowVal));
    }

    // O(logN) -- # of values < x in a[l..r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE int countLtX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("countLtX: needs 0 <= l <= r < n");
        return countBelow(l, r, lb(x));
    }

    // O(logN) -- # of values <= x in a[l..r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE int countLteX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("countLteX: needs 0 <= l <= r < n");
        return countBelow(l, r, ub(x));
    }

    // O(logN) -- # of values > x in a[l..r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE int countGtX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("countGtX: needs 0 <= l <= r < n");
        return r - l + 1 - countBelow(l, r, ub(x));
    }

    // O(logN) -- # of values >= x in a[l..r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE int countGteX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("countGteX: needs 0 <= l <= r < n");
        return r - l + 1 - countBelow(l, r, lb(x));
    }

    // O(logN) -- the k-th smallest of a[l..r] (k = 1 is the min); needs 0 <= l <= r < n and 1 <= k <= r - l + 1, else
    // throws out_of_range
    LEETCODE_NO_SANITIZE T kthSmallest(int l, int r, int k) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("kthSmallest: needs 0 <= l <= r < n");
        if (k < 1 || k > r - l + 1) throw out_of_range("kthSmallest: needs 1 <= k <= r - l + 1");
        return kth(l, r, k);
    }

    // O(logN) -- min of a[l..r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE T rangeMin(int l, int r) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeMin: needs 0 <= l <= r < n");
        return kth(l, r, 1);
    }

    // O(logN) -- max of a[l..r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE T rangeMax(int l, int r) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeMax: needs 0 <= l <= r < n");
        return kth(l, r, r - l + 1);
    }

    // O(logN) -- smallest value >= x in a[l..r], or nullopt; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE optional<T> smallestGteX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("smallestGteX: needs 0 <= l <= r < n");
        int c = countBelow(l, r, lb(x));
        if (c == r - l + 1) return nullopt;
        return kth(l, r, c + 1);
    }

    // O(logN) -- smallest value > x in a[l..r], or nullopt; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE optional<T> smallestGtX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("smallestGtX: needs 0 <= l <= r < n");
        int c = countBelow(l, r, ub(x));
        if (c == r - l + 1) return nullopt;
        return kth(l, r, c + 1);
    }

    // O(logN) -- largest value <= x in a[l..r], or nullopt; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE optional<T> largestLteX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("largestLteX: needs 0 <= l <= r < n");
        int c = countBelow(l, r, ub(x));
        if (c == 0) return nullopt;
        return kth(l, r, c);
    }

    // O(logN) -- largest value < x in a[l..r], or nullopt; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE optional<T> largestLtX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("largestLtX: needs 0 <= l <= r < n");
        int c = countBelow(l, r, lb(x));
        if (c == 0) return nullopt;
        return kth(l, r, c);
    }

    // O(logN) -- a[l] + ... + a[r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE S rangeSum(int l, int r) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeSum: needs 0 <= l <= r < n");
        return sumFirst(l, r, r - l + 1);
    }

    // O(logN) -- sum of the a[i] in [l, r] with lowVal <= a[i] <= highVal; needs 0 <= l <= r < n, else throws
    // out_of_range
    LEETCODE_NO_SANITIZE S sumInValRange(int l, int r, T lowVal, T highVal) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("sumInValRange: needs 0 <= l <= r < n");
        if (highVal < lowVal) return 0;
        return sumBelow(l, r, ub(highVal)) - sumBelow(l, r, lb(lowVal));
    }

    // O(logN) -- sum of the values < x in a[l..r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE S sumLtX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("sumLtX: needs 0 <= l <= r < n");
        return sumBelow(l, r, lb(x));
    }

    // O(logN) -- sum of the values <= x in a[l..r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE S sumLteX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("sumLteX: needs 0 <= l <= r < n");
        return sumBelow(l, r, ub(x));
    }

    // O(logN) -- sum of the values > x in a[l..r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE S sumGtX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("sumGtX: needs 0 <= l <= r < n");
        return sumFirst(l, r, r - l + 1) - sumBelow(l, r, ub(x));
    }

    // O(logN) -- sum of the values >= x in a[l..r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE S sumGteX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("sumGteX: needs 0 <= l <= r < n");
        return sumFirst(l, r, r - l + 1) - sumBelow(l, r, lb(x));
    }

    // O(logN) -- sum of the k smallest values in a[l..r]; needs 0 <= l <= r < n and 0 <= k <= r - l + 1, else throws
    // out_of_range
    LEETCODE_NO_SANITIZE S sumSmallestK(int l, int r, int k) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("sumSmallestK: needs 0 <= l <= r < n");
        if (k < 0 || k > r - l + 1) throw out_of_range("sumSmallestK: needs 0 <= k <= r - l + 1");
        return sumFirst(l, r, k);
    }

    // O(logN) -- sum of the k largest values in a[l..r]; needs 0 <= l <= r < n and 0 <= k <= r - l + 1, else throws
    // out_of_range
    LEETCODE_NO_SANITIZE S sumLargestK(int l, int r, int k) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("sumLargestK: needs 0 <= l <= r < n");
        int n = r - l + 1;
        if (k < 0 || k > n) throw out_of_range("sumLargestK: needs 0 <= k <= r - l + 1");
        return sumFirst(l, r, n) - sumFirst(l, r, n - k);
    }

    // O(logN) -- sum of the kFrom-th..kTo-th smallest values of a[l..r] (1-indexed, inclusive); needs 0 <= l <= r < n
    // and 1 <= kFrom <= kTo <= r - l + 1, else throws out_of_range
    LEETCODE_NO_SANITIZE S sumKthSmallestRange(int l, int r, int kFrom, int kTo) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("sumKthSmallestRange: needs 0 <= l <= r < n");
        if (kFrom < 1 || kFrom > kTo || kTo > r - l + 1)
            throw out_of_range("sumKthSmallestRange: needs 1 <= kFrom <= kTo <= r - l + 1");
        return sumFirst(l, r, kTo) - sumFirst(l, r, kFrom - 1);
    }

    // O(logN) -- sum of the kFrom-th..kTo-th largest values of a[l..r] (1-indexed, inclusive; (1, 3) = the 3
    // biggest); needs 0 <= l <= r < n and 1 <= kFrom <= kTo <= r - l + 1, else throws out_of_range
    LEETCODE_NO_SANITIZE S sumKthLargestRange(int l, int r, int kFrom, int kTo) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("sumKthLargestRange: needs 0 <= l <= r < n");
        int n = r - l + 1;
        if (kFrom < 1 || kFrom > kTo || kTo > n)
            throw out_of_range("sumKthLargestRange: needs 1 <= kFrom <= kTo <= r - l + 1");
        return sumFirst(l, r, n - kFrom + 1) - sumFirst(l, r, n - kTo);
    }

    // O(logN) -- sum of |a[i] - x| over i in [l, r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE S sumAbsDiffToX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("sumAbsDiffToX: needs 0 <= l <= r < n");
        int rk = lb(x), c = countBelow(l, r, rk);
        S s = sumBelow(l, r, rk);
        return S(x) * c - s + (sumFirst(l, r, r - l + 1) - s) - S(x) * (r - l + 1 - c);
    }

    // O(logN) -- xor of the values < x in a[l..r] (copies count); 0 if there are none; needs 0 <= l <= r < n, else
    // throws out_of_range
    LEETCODE_NO_SANITIZE T xorLtX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("xorLtX: needs 0 <= l <= r < n");
        return xorRanks(l, r, 0, lb(x));
    }

    // O(logN) -- xor of the values <= x in a[l..r] (copies count); 0 if there are none; needs 0 <= l <= r < n, else
    // throws out_of_range
    LEETCODE_NO_SANITIZE T xorLteX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("xorLteX: needs 0 <= l <= r < n");
        return xorRanks(l, r, 0, ub(x));
    }

    // O(logN) -- xor of the values > x in a[l..r] (copies count); 0 if there are none; needs 0 <= l <= r < n, else
    // throws out_of_range
    LEETCODE_NO_SANITIZE T xorGtX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("xorGtX: needs 0 <= l <= r < n");
        return xorRanks(l, r, ub(x), m);
    }

    // O(logN) -- xor of the values >= x in a[l..r] (copies count); 0 if there are none; needs 0 <= l <= r < n, else
    // throws out_of_range
    LEETCODE_NO_SANITIZE T xorGteX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("xorGteX: needs 0 <= l <= r < n");
        return xorRanks(l, r, lb(x), m);
    }

    // O(logN) -- xor of the a[i] with lowVal <= a[i] <= highVal in a[l..r] (copies count); 0 if there are none; needs
    // 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE T xorInValRange(int l, int r, T lowVal, T highVal) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("xorInValRange: needs 0 <= l <= r < n");
        if (highVal < lowVal) return T(0);
        return xorRanks(l, r, lb(lowVal), ub(highVal));
    }

    // O(log^2 N) -- OR of the values < x in a[l..r]; 0 if there are none; needs 0 <= l <= r < n, else throws
    // out_of_range
    LEETCODE_NO_SANITIZE T orLtX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("orLtX: needs 0 <= l <= r < n");
        return orRanks(l, r, 0, lb(x));
    }

    // O(log^2 N) -- OR of the values <= x in a[l..r]; 0 if there are none; needs 0 <= l <= r < n, else throws
    // out_of_range
    LEETCODE_NO_SANITIZE T orLteX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("orLteX: needs 0 <= l <= r < n");
        return orRanks(l, r, 0, ub(x));
    }

    // O(log^2 N) -- OR of the values > x in a[l..r]; 0 if there are none; needs 0 <= l <= r < n, else throws
    // out_of_range
    LEETCODE_NO_SANITIZE T orGtX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("orGtX: needs 0 <= l <= r < n");
        return orRanks(l, r, ub(x), m);
    }

    // O(log^2 N) -- OR of the values >= x in a[l..r]; 0 if there are none; needs 0 <= l <= r < n, else throws
    // out_of_range
    LEETCODE_NO_SANITIZE T orGteX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("orGteX: needs 0 <= l <= r < n");
        return orRanks(l, r, lb(x), m);
    }

    // O(log^2 N) -- OR of the a[i] with lowVal <= a[i] <= highVal in a[l..r]; 0 if there are none; needs
    // 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE T orInValRange(int l, int r, T lowVal, T highVal) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("orInValRange: needs 0 <= l <= r < n");
        if (highVal < lowVal) return T(0);
        return orRanks(l, r, lb(lowVal), ub(highVal));
    }

    // ---- internals ----

    LEETCODE_NO_SANITIZE int lb(const T& v) const { return int(lower_bound(srt.begin(), srt.end(), v) - srt.begin()); }
    LEETCODE_NO_SANITIZE int ub(const T& v) const { return int(upper_bound(srt.begin(), srt.end(), v) - srt.begin()); }
    LEETCODE_NO_SANITIZE const int* row(int lv) const { return &zeros[(size_t)lv * (n + 1)]; }

    // the k-th smallest of a[l..r], 1 <= k <= r - l + 1
    LEETCODE_NO_SANITIZE T kth(int l, int r, int k) const {
        int lo = l, hi = r + 1, rank = 0;
        for (int lv = 0; lv < bits; lv++) {
            const int* z = row(lv);
            int zl = z[lo], zh = z[hi];
            if (k <= zh - zl) lo = zl, hi = zh;  // enough 0s at this bit: the answer has it 0
            else k -= zh - zl, rank |= 1 << (bits - 1 - lv), lo = z[n] + lo - zl, hi = z[n] + hi - zh;
        }
        return srt[rank];
    }

    // # of i in [l, r] whose rank is < x
    LEETCODE_NO_SANITIZE int countBelow(int l, int r, int x) const {
        if (x <= 0) return 0;
        if (x >= m) return r - l + 1;
        int lo = l, hi = r + 1, res = 0;
        for (int lv = 0; lv < bits; lv++) {
            const int* z = row(lv);
            int zl = z[lo], zh = z[hi];
            if ((x >> (bits - 1 - lv)) & 1) res += zh - zl, lo = z[n] + lo - zl, hi = z[n] + hi - zh;  // all 0s are below x
            else lo = zl, hi = zh;
        }
        return res;
    }

    // sum of the k smallest of a[l..r], 0 <= k <= r - l + 1
    LEETCODE_NO_SANITIZE S sumFirst(int l, int r, int k) const {
        if (k <= 0) return 0;
        int lo = l, hi = r + 1, rank = 0;
        S res = 0;
        for (int lv = 0; lv < bits; lv++) {
            const int* z = row(lv);
            const S* zs = &zsum[(size_t)lv * (n + 1)];
            int zl = z[lo], zh = z[hi];
            if (k <= zh - zl) lo = zl, hi = zh;
            else k -= zh - zl, res += zs[hi] - zs[lo], rank |= 1 << (bits - 1 - lv), lo = z[n] + lo - zl, hi = z[n] + hi - zh;
        }
        return res + S(k) * srt[rank];  // the last k all equal the k-th smallest
    }

    // sum of the a[i], i in [l, r], whose rank is < x
    LEETCODE_NO_SANITIZE S sumBelow(int l, int r, int x) const {
        if (x <= 0) return 0;
        if (x >= m) return sumFirst(l, r, r - l + 1);
        int lo = l, hi = r + 1;
        S res = 0;
        for (int lv = 0; lv < bits; lv++) {
            const int* z = row(lv);
            const S* zs = &zsum[(size_t)lv * (n + 1)];
            int zl = z[lo], zh = z[hi];
            if ((x >> (bits - 1 - lv)) & 1) res += zs[hi] - zs[lo], lo = z[n] + lo - zl, hi = z[n] + hi - zh;
            else lo = zl, hi = zh;
        }
        return res;
    }

    LEETCODE_NO_SANITIZE void xorBuild(int lv, const vector<T>& vals) {  // prefix xors of level lv's order
        auto& t = xt[lv];
        t.assign(n + 1, T(0));
        for (int i = 0; i < n; i++) t[i + 1] = t[i] ^ vals[i];
    }
    LEETCODE_NO_SANITIZE T xorQ(int lv, int lo, int hi) const { return xt[lv][hi] ^ xt[lv][lo]; }

    // xor of the a[i], i in [l, r], whose rank is in [a, b): whole windows of the levels' orders
    LEETCODE_NO_SANITIZE T xorRanks(int l, int r, int a, int b) const {
        T res = T(0);
        if (a >= b) return res;
        array<int, 4> st[2 * 64];  // (level, window [lo, hi) of its order, first rank under it)
        int sp = 0;
        st[sp++] = {0, l, r + 1, 0};
        while (sp) {
            auto [lv, lo, hi, nl] = st[--sp];
            int nr = nl + (1 << (bits - lv));
            if (lo >= hi || nr <= a || b <= nl) continue;
            if (a <= nl && nr <= b) {  // every rank under it counts: one window
                res ^= xorQ(lv, lo, hi);
                continue;
            }
            const int* z = row(lv);
            int zl = z[lo], zh = z[hi];
            st[sp++] = {lv + 1, zl, zh, nl};
            st[sp++] = {lv + 1, z[n] + lo - zl, z[n] + hi - zh, nl + (1 << (bits - lv - 1))};
        }
        return res;
    }

    LEETCODE_NO_SANITIZE void orBuild(int lv, const vector<T>& vals) {  // bottom-up segment tree: leaves at n..2n-1
        auto& t = ot[lv];
        t.assign(2 * n, T(0));
        for (int i = 0; i < n; i++) t[n + i] = vals[i];
        for (int i = n - 1; i > 0; i--) t[i] = t[2 * i] | t[2 * i + 1];
    }
    LEETCODE_NO_SANITIZE T orQ(int lv, int lo, int hi) const {
        const vector<T>& t = ot[lv];
        T res = T(0);
        for (lo += n, hi += n; lo < hi; lo >>= 1, hi >>= 1) {
            if (lo & 1) res |= t[lo++];
            if (hi & 1) res |= t[--hi];
        }
        return res;
    }

    // OR of the a[i], i in [l, r], whose rank is in [a, b): whole windows of the levels' orders
    LEETCODE_NO_SANITIZE T orRanks(int l, int r, int a, int b) const {
        T res = T(0);
        if (a >= b) return res;
        array<int, 4> st[2 * 64];  // (level, window [lo, hi) of its order, first rank under it)
        int sp = 0;
        st[sp++] = {0, l, r + 1, 0};
        while (sp) {
            auto [lv, lo, hi, nl] = st[--sp];
            int nr = nl + (1 << (bits - lv));
            if (lo >= hi || nr <= a || b <= nl) continue;
            if (a <= nl && nr <= b) {  // every rank under it counts: one window
                res |= orQ(lv, lo, hi);
                continue;
            }
            const int* z = row(lv);
            int zl = z[lo], zh = z[hi];
            st[sp++] = {lv + 1, zl, zh, nl};
            st[sp++] = {lv + 1, z[n] + lo - zl, z[n] + hi - zh, nl + (1 << (bits - lv - 1))};
        }
        return res;
    }
};
