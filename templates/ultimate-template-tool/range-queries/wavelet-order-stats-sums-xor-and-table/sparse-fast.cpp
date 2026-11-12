// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/wavelet-order-stats-sums-xor-and-table/sparse-fast.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: andGtX andGteX andInValRange andLtX andLteX countGtX countGteX countInValRange countLtX countLteX countOccurrences kthSmallest largestLtX largestLteX pointGet rangeMax rangeMin rangeSum smallestGtX smallestGteX sumAbsDiffToX sumGtX sumGteX sumInValRange sumKthLargestRange sumKthSmallestRange sumLargestK sumLtX sumLteX sumSmallestK xorGtX xorGteX xorInValRange xorLtX xorLteX
// @data-structure-type: wavelet
// @complexities:
//   andGtX: log(N)
//   andGteX: log(N)
//   andInValRange: log(N)
//   andLtX: log(N)
//   andLteX: log(N)
//   countGtX: log(N)
//   countGteX: log(N)
//   countInValRange: log(N)
//   countLtX: log(N)
//   countLteX: log(N)
//   countOccurrences: log(N)
//   kthSmallest: log(N)
//   largestLtX: log(N)
//   largestLteX: log(N)
//   pointGet: log(N)
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
//   build: N*log^2(N)
// @memory:
//   layout: sparse
//   node: idx[1*N] vals[1*N] zeros[1*N*log(N)] zsum[1*N*log(N)] arr[1*N] srt[1*N] xt[1*N*log(N)] at[1*N*log^2(N)]
//   tags: none
//   other: none
//   note: built from N given values (index, value pairs) over any index range [lo, hi], every other index 0; costs are in N; wavelet matrix: one row of N + 1 prefix counts per bit of the compressed value, plus one row of prefix sums of the values that go left; xor by value: per level, prefix xors of its order; AND by value: per level, a sparse table over its order (O(1) a window); the structure is over the given values only, and the zeros of [l, r] are added in closed form (they sit between the negatives and the positives)

// Static array. Each query treats a[l..r] (0-indexed, inclusive) as a sorted multiset. Values are compressed to ranks
// 0..m-1 once, so costs are log of the number of distinct values, never of the value range; query arguments (x,
// lowVal, ...) can be anything. Level d of the wavelet matrix (top bit first) stably splits the current order into the
// ranks with that bit 0, then 1; zeros[d][i] = # of the first i elements of level d's order with the bit 0.
// zsum[d][i] = sum of the values among the first i elements of level d's order whose bit is 0.
// T: int, long long, ...; sums are kept in S (long long for small T).
template <typename T>
struct WaveletMatrix {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    int n, m, bits;
    vector<T> arr, srt;  // srt: sorted distinct values
    vector<int> zeros;   // level lv's row is zeros[lv * (n + 1) .. lv * (n + 1) + n]
    vector<S> zsum;      // same layout as zeros
    vector<vector<T>> xt;  // per level, xor over its order
    vector<vector<vector<T>>> at;  // per level, AND over its order

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
        at.resize(bits + 1);
        vector<int> cur(n), nxt(n);
        for (int i = 0; i < n; i++) cur[i] = lb(a[i]);
        vector<T> vals(n);
        auto order = [&](int lv) {  // the level's order, as values
            for (int i = 0; i < n; i++) vals[i] = srt[cur[i]];
            xorBuild(lv, vals);
            andBuild(lv, vals);
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

    // O(logN) -- a[i]; needs 0 <= i < n, else throws out_of_range
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

    // O(logN) -- xor of the values < x in a[l..r] (copies count); 0 if there are none; needs 0 <= l <= r < n, else
    // throws out_of_range
    T xorLtX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("xorLtX: needs 0 <= l <= r < n");
        return xorRanks(l, r, 0, lb(x));
    }

    // O(logN) -- xor of the values <= x in a[l..r] (copies count); 0 if there are none; needs 0 <= l <= r < n, else
    // throws out_of_range
    T xorLteX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("xorLteX: needs 0 <= l <= r < n");
        return xorRanks(l, r, 0, ub(x));
    }

    // O(logN) -- xor of the values > x in a[l..r] (copies count); 0 if there are none; needs 0 <= l <= r < n, else
    // throws out_of_range
    T xorGtX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("xorGtX: needs 0 <= l <= r < n");
        return xorRanks(l, r, ub(x), m);
    }

    // O(logN) -- xor of the values >= x in a[l..r] (copies count); 0 if there are none; needs 0 <= l <= r < n, else
    // throws out_of_range
    T xorGteX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("xorGteX: needs 0 <= l <= r < n");
        return xorRanks(l, r, lb(x), m);
    }

    // O(logN) -- xor of the a[i] with lowVal <= a[i] <= highVal in a[l..r] (copies count); 0 if there are none; needs
    // 0 <= l <= r < n, else throws out_of_range
    T xorInValRange(int l, int r, T lowVal, T highVal) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("xorInValRange: needs 0 <= l <= r < n");
        if (highVal < lowVal) return T(0);
        return xorRanks(l, r, lb(lowVal), ub(highVal));
    }

    // O(logN) -- AND of the values < x in a[l..r]; -1 (every bit) if there are none; needs 0 <= l <= r < n, else
    // throws out_of_range
    T andLtX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("andLtX: needs 0 <= l <= r < n");
        return andRanks(l, r, 0, lb(x));
    }

    // O(logN) -- AND of the values <= x in a[l..r]; -1 (every bit) if there are none; needs 0 <= l <= r < n, else
    // throws out_of_range
    T andLteX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("andLteX: needs 0 <= l <= r < n");
        return andRanks(l, r, 0, ub(x));
    }

    // O(logN) -- AND of the values > x in a[l..r]; -1 (every bit) if there are none; needs 0 <= l <= r < n, else
    // throws out_of_range
    T andGtX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("andGtX: needs 0 <= l <= r < n");
        return andRanks(l, r, ub(x), m);
    }

    // O(logN) -- AND of the values >= x in a[l..r]; -1 (every bit) if there are none; needs 0 <= l <= r < n, else
    // throws out_of_range
    T andGteX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("andGteX: needs 0 <= l <= r < n");
        return andRanks(l, r, lb(x), m);
    }

    // O(logN) -- AND of the a[i] with lowVal <= a[i] <= highVal in a[l..r]; -1 (every bit) if there are none; needs
    // 0 <= l <= r < n, else throws out_of_range
    T andInValRange(int l, int r, T lowVal, T highVal) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("andInValRange: needs 0 <= l <= r < n");
        if (highVal < lowVal) return ~T(0);
        return andRanks(l, r, lb(lowVal), ub(highVal));
    }

    // ---- internals ----

    int lb(const T& v) const { return int(lower_bound(srt.begin(), srt.end(), v) - srt.begin()); }
    int ub(const T& v) const { return int(upper_bound(srt.begin(), srt.end(), v) - srt.begin()); }
    const int* row(int lv) const { return &zeros[(size_t)lv * (n + 1)]; }

    // the k-th smallest of a[l..r], 1 <= k <= r - l + 1
    T kth(int l, int r, int k) const {
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
    int countBelow(int l, int r, int x) const {
        if (x <= 0) return 0;
        if (x >= m) return r - l + 1;
        int lo = l, hi = r + 1, res = 0;
        for (int lv = 0; lv < bits; lv++) {
            const int* z = row(lv);
            int zl = z[lo], zh = z[hi];
            // all 0s are below x
            if ((x >> (bits - 1 - lv)) & 1) res += zh - zl, lo = z[n] + lo - zl, hi = z[n] + hi - zh;
            else lo = zl, hi = zh;
        }
        return res;
    }

    // sum of the k smallest of a[l..r], 0 <= k <= r - l + 1
    S sumFirst(int l, int r, int k) const {
        if (k <= 0) return 0;
        int lo = l, hi = r + 1, rank = 0;
        S res = 0;
        for (int lv = 0; lv < bits; lv++) {
            const int* z = row(lv);
            const S* zs = &zsum[(size_t)lv * (n + 1)];
            int zl = z[lo], zh = z[hi];
            if (k <= zh - zl) lo = zl, hi = zh;
            else k -= zh - zl, res += zs[hi] - zs[lo], rank |= 1 << (bits - 1 - lv), lo = z[n] + lo - zl,
                hi = z[n] + hi - zh;
        }
        return res + S(k) * srt[rank];  // the last k all equal the k-th smallest
    }

    // sum of the a[i], i in [l, r], whose rank is < x
    S sumBelow(int l, int r, int x) const {
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

    void xorBuild(int lv, const vector<T>& vals) {  // prefix xors of level lv's order
        auto& t = xt[lv];
        t.assign(n + 1, T(0));
        for (int i = 0; i < n; i++) t[i + 1] = t[i] ^ vals[i];
    }
    T xorQ(int lv, int lo, int hi) const { return xt[lv][hi] ^ xt[lv][lo]; }

    // xor of the a[i], i in [l, r], whose rank is in [a, b): whole windows of the levels' orders
    T xorRanks(int l, int r, int a, int b) const {
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

    void andBuild(int lv, const vector<T>& vals) {  // sparse table: row j = AND of every window of 2^j
        auto& rows = at[lv];
        rows.assign(1, vals);
        for (int h = 1; 2 * h <= n; h *= 2) {
            const vector<T>& p = rows.back();
            vector<T> q(p.size() - h);
            for (size_t i = 0; i < q.size(); i++) q[i] = p[i] & p[i + h];
            rows.push_back(move(q));
        }
    }
    T andQ(int lv, int lo, int hi) const {  // lo < hi
        int j = 31 - __builtin_clz(hi - lo);
        return at[lv][j][lo] & at[lv][j][hi - (1 << j)];
    }

    // AND of the a[i], i in [l, r], whose rank is in [a, b): whole windows of the levels' orders
    T andRanks(int l, int r, int a, int b) const {
        T res = ~T(0);
        if (a >= b) return res;
        array<int, 4> st[2 * 64];  // (level, window [lo, hi) of its order, first rank under it)
        int sp = 0;
        st[sp++] = {0, l, r + 1, 0};
        while (sp) {
            auto [lv, lo, hi, nl] = st[--sp];
            int nr = nl + (1 << (bits - lv));
            if (lo >= hi || nr <= a || b <= nl) continue;
            if (a <= nl && nr <= b) {  // every rank under it counts: one window
                res &= andQ(lv, lo, hi);
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

// ======================================================================================== sparse wrapper

// The same queries over any index range [lo, hi], built from given values (index, value pairs); every other index is 0.
// The structure above runs on the given values alone (in index order). [l, r] covers given values i0..i1 and
// zeros = (r - l + 1) - (i1 - i0 + 1) zeros, and in sorted order those zeros sit right after the given negatives, so
// the k-th smallest of [l, r] is the given k-th while k <= neg, 0 while k <= neg + zeros, then the given (k -
// zeros)-th.
// FAST MODE drawbacks compared with sparse.cpp:
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
struct SparseWaveletMatrix {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    long long lo, hi;
    HotVector<long long> idx;
    HotVector<T> vals;
    WaveletMatrix<T> inner;

    // O(N log N) -- [lo, hi] all 0 except the given values: (index, value) pairs with distinct indices; N = len(values)
    SparseWaveletMatrix(long long lo, long long hi, vector<pair<long long, T>> values) : lo(lo), hi(hi),
        inner(split(values)) {}

    LEETCODE_NO_SANITIZE vector<T> split(vector<pair<long long, T>>& pts) {
        sort(pts.begin(), pts.end());
        for (auto& [i, v] : pts) idx.push_back(i), vals.push_back(v);
        // (a dummy element when there are no given values; never queried)
        return vals.empty() ? vector<T>{T(0)} : vals;
    }

    // {i0, i1, zeros}: the given values inside [l, r] are i0..i1, and the rest of [l, r] is that many zeros
    LEETCODE_NO_SANITIZE tuple<int, int, long long> span(long long l, long long r) const {
        int i0 = int(lower_bound(idx.begin(), idx.end(), l) - idx.begin());
        int i1 = int(upper_bound(idx.begin(), idx.end(), r) - idx.begin()) - 1;
        return {i0, i1, (r - l + 1) - (i1 - i0 + 1)};
    }

    // O(logN) -- a[i]; needs lo <= i <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE T pointGet(long long i) const {
        if (i < lo || i > hi) throw out_of_range("pointGet: needs lo <= i <= hi");
        auto it = lower_bound(idx.begin(), idx.end(), i);
        return it != idx.end() && *it == i ? vals[it - idx.begin()] : T(0);
    }

    // O(logN) -- # of i in [l, r] with a[i] == x; needs lo <= l <= r <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE long long countOccurrences(long long l, long long r, T x) const {
        if (l < lo || l > r || r > hi) throw out_of_range("countOccurrences: needs lo <= l <= r <= hi");
        auto [i0, i1, zeros] = span(l, r);
        return (i0 <= i1 ? inner.countOccurrences(i0, i1, x) : 0) + (x == T(0) ? zeros : 0);
    }

    // O(logN) -- # of i in [l, r] with lowVal <= a[i] <= highVal; needs lo <= l <= r <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE long long countInValRange(long long l, long long r, T lowVal, T highVal) const {
        if (l < lo || l > r || r > hi) throw out_of_range("countInValRange: needs lo <= l <= r <= hi");
        auto [i0, i1, zeros] = span(l, r);
        return (i0 <= i1 ? inner.countInValRange(i0, i1, lowVal,
            highVal) : 0) + (lowVal <= T(0) && T(0) <= highVal ? zeros : 0);
    }

    // O(logN) -- # of values < x in a[l..r]; needs lo <= l <= r <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE long long countLtX(long long l, long long r, T x) const {
        if (l < lo || l > r || r > hi) throw out_of_range("countLtX: needs lo <= l <= r <= hi");
        auto [i0, i1, zeros] = span(l, r);
        return (i0 <= i1 ? inner.countLtX(i0, i1, x) : 0) + (T(0) < x ? zeros : 0);
    }

    // O(logN) -- # of values <= x in a[l..r]; needs lo <= l <= r <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE long long countLteX(long long l, long long r, T x) const {
        if (l < lo || l > r || r > hi) throw out_of_range("countLteX: needs lo <= l <= r <= hi");
        auto [i0, i1, zeros] = span(l, r);
        return (i0 <= i1 ? inner.countLteX(i0, i1, x) : 0) + (T(0) <= x ? zeros : 0);
    }

    // O(logN) -- # of values > x in a[l..r]; needs lo <= l <= r <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE long long countGtX(long long l, long long r, T x) const {
        if (l < lo || l > r || r > hi) throw out_of_range("countGtX: needs lo <= l <= r <= hi");
        auto [i0, i1, zeros] = span(l, r);
        return (i0 <= i1 ? inner.countGtX(i0, i1, x) : 0) + (x < T(0) ? zeros : 0);
    }

    // O(logN) -- # of values >= x in a[l..r]; needs lo <= l <= r <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE long long countGteX(long long l, long long r, T x) const {
        if (l < lo || l > r || r > hi) throw out_of_range("countGteX: needs lo <= l <= r <= hi");
        auto [i0, i1, zeros] = span(l, r);
        return (i0 <= i1 ? inner.countGteX(i0, i1, x) : 0) + (x <= T(0) ? zeros : 0);
    }

    // O(logN) -- the k-th smallest of a[l..r] (k = 1 is the min); needs lo <= l <= r <= hi and 1 <= k <= r - l + 1,
    // else throws out_of_range
    LEETCODE_NO_SANITIZE T kthSmallest(long long l, long long r, long long k) const {
        if (l < lo || l > r || r > hi) throw out_of_range("kthSmallest: needs lo <= l <= r <= hi");
        if (k < 1 || k > r - l + 1) throw out_of_range("kthSmallest: needs 1 <= k <= r - l + 1");
        return kth(l, r, k);
    }

    // O(logN) -- min of a[l..r]; needs lo <= l <= r <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE T rangeMin(long long l, long long r) const {
        if (l < lo || l > r || r > hi) throw out_of_range("rangeMin: needs lo <= l <= r <= hi");
        return kth(l, r, 1);
    }

    // O(logN) -- max of a[l..r]; needs lo <= l <= r <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE T rangeMax(long long l, long long r) const {
        if (l < lo || l > r || r > hi) throw out_of_range("rangeMax: needs lo <= l <= r <= hi");
        return kth(l, r, r - l + 1);
    }

    // O(logN) -- smallest value >= x in a[l..r], or nullopt; needs lo <= l <= r <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE optional<T> smallestGteX(long long l, long long r, T x) const {
        if (l < lo || l > r || r > hi) throw out_of_range("smallestGteX: needs lo <= l <= r <= hi");
        auto [i0, i1, zeros] = span(l, r);
        optional<T> a = i0 <= i1 ? inner.smallestGteX(i0, i1, x) : nullopt;
        if (zeros && x <= T(0)) a = a ? min(*a, T(0)) : T(0);
        return a;
    }

    // O(logN) -- smallest value > x in a[l..r], or nullopt; needs lo <= l <= r <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE optional<T> smallestGtX(long long l, long long r, T x) const {
        if (l < lo || l > r || r > hi) throw out_of_range("smallestGtX: needs lo <= l <= r <= hi");
        auto [i0, i1, zeros] = span(l, r);
        optional<T> a = i0 <= i1 ? inner.smallestGtX(i0, i1, x) : nullopt;
        if (zeros && x < T(0)) a = a ? min(*a, T(0)) : T(0);
        return a;
    }

    // O(logN) -- largest value <= x in a[l..r], or nullopt; needs lo <= l <= r <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE optional<T> largestLteX(long long l, long long r, T x) const {
        if (l < lo || l > r || r > hi) throw out_of_range("largestLteX: needs lo <= l <= r <= hi");
        auto [i0, i1, zeros] = span(l, r);
        optional<T> a = i0 <= i1 ? inner.largestLteX(i0, i1, x) : nullopt;
        if (zeros && T(0) <= x) a = a ? max(*a, T(0)) : T(0);
        return a;
    }

    // O(logN) -- largest value < x in a[l..r], or nullopt; needs lo <= l <= r <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE optional<T> largestLtX(long long l, long long r, T x) const {
        if (l < lo || l > r || r > hi) throw out_of_range("largestLtX: needs lo <= l <= r <= hi");
        auto [i0, i1, zeros] = span(l, r);
        optional<T> a = i0 <= i1 ? inner.largestLtX(i0, i1, x) : nullopt;
        if (zeros && T(0) < x) a = a ? max(*a, T(0)) : T(0);
        return a;
    }

    // O(logN) -- a[l] + ... + a[r]; needs lo <= l <= r <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE S rangeSum(long long l, long long r) const {
        if (l < lo || l > r || r > hi) throw out_of_range("rangeSum: needs lo <= l <= r <= hi");
        auto [i0, i1, zeros] = span(l, r);
        return i0 <= i1 ? S(inner.rangeSum(i0, i1)) : S(0);
    }

    // O(logN) -- sum of the a[i] in [l, r] with lowVal <= a[i] <= highVal (the zeros add nothing); needs
    // lo <= l <= r <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE S sumInValRange(long long l, long long r, T lowVal, T highVal) const {
        if (l < lo || l > r || r > hi) throw out_of_range("sumInValRange: needs lo <= l <= r <= hi");
        auto [i0, i1, zeros] = span(l, r);
        return i0 <= i1 ? S(inner.sumInValRange(i0, i1, lowVal, highVal)) : S(0);
    }

    // O(logN) -- sum of the values < x in a[l..r] (the zeros add nothing); needs lo <= l <= r <= hi, else throws
    // out_of_range
    LEETCODE_NO_SANITIZE S sumLtX(long long l, long long r, T x) const {
        if (l < lo || l > r || r > hi) throw out_of_range("sumLtX: needs lo <= l <= r <= hi");
        auto [i0, i1, zeros] = span(l, r);
        return i0 <= i1 ? S(inner.sumLtX(i0, i1, x)) : S(0);
    }

    // O(logN) -- sum of the values <= x in a[l..r] (the zeros add nothing); needs lo <= l <= r <= hi, else throws
    // out_of_range
    LEETCODE_NO_SANITIZE S sumLteX(long long l, long long r, T x) const {
        if (l < lo || l > r || r > hi) throw out_of_range("sumLteX: needs lo <= l <= r <= hi");
        auto [i0, i1, zeros] = span(l, r);
        return i0 <= i1 ? S(inner.sumLteX(i0, i1, x)) : S(0);
    }

    // O(logN) -- sum of the values > x in a[l..r] (the zeros add nothing); needs lo <= l <= r <= hi, else throws
    // out_of_range
    LEETCODE_NO_SANITIZE S sumGtX(long long l, long long r, T x) const {
        if (l < lo || l > r || r > hi) throw out_of_range("sumGtX: needs lo <= l <= r <= hi");
        auto [i0, i1, zeros] = span(l, r);
        return i0 <= i1 ? S(inner.sumGtX(i0, i1, x)) : S(0);
    }

    // O(logN) -- sum of the values >= x in a[l..r] (the zeros add nothing); needs lo <= l <= r <= hi, else throws
    // out_of_range
    LEETCODE_NO_SANITIZE S sumGteX(long long l, long long r, T x) const {
        if (l < lo || l > r || r > hi) throw out_of_range("sumGteX: needs lo <= l <= r <= hi");
        auto [i0, i1, zeros] = span(l, r);
        return i0 <= i1 ? S(inner.sumGteX(i0, i1, x)) : S(0);
    }

    // O(logN) -- sum of the k smallest values in a[l..r]; needs lo <= l <= r <= hi and 0 <= k <= r - l + 1, else
    // throws out_of_range
    LEETCODE_NO_SANITIZE S sumSmallestK(long long l, long long r, long long k) const {
        if (l < lo || l > r || r > hi) throw out_of_range("sumSmallestK: needs lo <= l <= r <= hi");
        if (k < 0 || k > r - l + 1) throw out_of_range("sumSmallestK: needs 0 <= k <= r - l + 1");
        return sumFirst(l, r, k);
    }

    // O(logN) -- sum of the k largest values in a[l..r]; needs lo <= l <= r <= hi and 0 <= k <= r - l + 1, else
    // throws out_of_range
    LEETCODE_NO_SANITIZE S sumLargestK(long long l, long long r, long long k) const {
        if (l < lo || l > r || r > hi) throw out_of_range("sumLargestK: needs lo <= l <= r <= hi");
        long long n = r - l + 1;
        if (k < 0 || k > n) throw out_of_range("sumLargestK: needs 0 <= k <= r - l + 1");
        return sumFirst(l, r, n) - sumFirst(l, r, n - k);
    }

    // O(logN) -- sum of the kFrom-th..kTo-th smallest values of a[l..r] (1-indexed, inclusive); needs
    // lo <= l <= r <= hi and 1 <= kFrom <= kTo <= r - l + 1, else throws out_of_range
    LEETCODE_NO_SANITIZE S sumKthSmallestRange(long long l, long long r, long long kFrom, long long kTo) const {
        if (l < lo || l > r || r > hi) throw out_of_range("sumKthSmallestRange: needs lo <= l <= r <= hi");
        if (kFrom < 1 || kFrom > kTo || kTo > r - l + 1)
            throw out_of_range("sumKthSmallestRange: needs 1 <= kFrom <= kTo <= r - l + 1");
        return sumFirst(l, r, kTo) - sumFirst(l, r, kFrom - 1);
    }

    // O(logN) -- sum of the kFrom-th..kTo-th largest values of a[l..r] (1-indexed, inclusive; (1, 3) = the 3
    // biggest); needs lo <= l <= r <= hi and 1 <= kFrom <= kTo <= r - l + 1, else throws out_of_range
    LEETCODE_NO_SANITIZE S sumKthLargestRange(long long l, long long r, long long kFrom, long long kTo) const {
        if (l < lo || l > r || r > hi) throw out_of_range("sumKthLargestRange: needs lo <= l <= r <= hi");
        long long n = r - l + 1;
        if (kFrom < 1 || kFrom > kTo || kTo > n)
            throw out_of_range("sumKthLargestRange: needs 1 <= kFrom <= kTo <= r - l + 1");
        return sumFirst(l, r, n - kFrom + 1) - sumFirst(l, r, n - kTo);
    }

    // O(logN) -- sum of |a[i] - x| over i in [l, r]; needs lo <= l <= r <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE S sumAbsDiffToX(long long l, long long r, T x) const {
        if (l < lo || l > r || r > hi) throw out_of_range("sumAbsDiffToX: needs lo <= l <= r <= hi");
        auto [i0, i1, zeros] = span(l, r);
        return (i0 <= i1 ? S(inner.sumAbsDiffToX(i0, i1, x)) : S(0)) + S(zeros) * S(x < T(0) ? -x : x);
    }

    // O(logN) -- xor of the values < x in a[l..r] (copies count); 0 if there are none (the zeros add nothing); needs
    // lo <= l <= r <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE T xorLtX(long long l, long long r, T x) const {
        if (l < lo || l > r || r > hi) throw out_of_range("xorLtX: needs lo <= l <= r <= hi");
        auto [i0, i1, zeros] = span(l, r);
        return i0 <= i1 ? inner.xorLtX(i0, i1, x) : T(0);
    }

    // O(logN) -- xor of the values <= x in a[l..r] (copies count); 0 if there are none (the zeros add nothing); needs
    // lo <= l <= r <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE T xorLteX(long long l, long long r, T x) const {
        if (l < lo || l > r || r > hi) throw out_of_range("xorLteX: needs lo <= l <= r <= hi");
        auto [i0, i1, zeros] = span(l, r);
        return i0 <= i1 ? inner.xorLteX(i0, i1, x) : T(0);
    }

    // O(logN) -- xor of the values > x in a[l..r] (copies count); 0 if there are none (the zeros add nothing); needs
    // lo <= l <= r <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE T xorGtX(long long l, long long r, T x) const {
        if (l < lo || l > r || r > hi) throw out_of_range("xorGtX: needs lo <= l <= r <= hi");
        auto [i0, i1, zeros] = span(l, r);
        return i0 <= i1 ? inner.xorGtX(i0, i1, x) : T(0);
    }

    // O(logN) -- xor of the values >= x in a[l..r] (copies count); 0 if there are none (the zeros add nothing); needs
    // lo <= l <= r <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE T xorGteX(long long l, long long r, T x) const {
        if (l < lo || l > r || r > hi) throw out_of_range("xorGteX: needs lo <= l <= r <= hi");
        auto [i0, i1, zeros] = span(l, r);
        return i0 <= i1 ? inner.xorGteX(i0, i1, x) : T(0);
    }

    // O(logN) -- xor of the a[i] with lowVal <= a[i] <= highVal in a[l..r] (copies count); 0 if there are none (the
    // zeros add nothing); needs lo <= l <= r <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE T xorInValRange(long long l, long long r, T lowVal, T highVal) const {
        if (l < lo || l > r || r > hi) throw out_of_range("xorInValRange: needs lo <= l <= r <= hi");
        auto [i0, i1, zeros] = span(l, r);
        return i0 <= i1 ? inner.xorInValRange(i0, i1, lowVal, highVal) : T(0);
    }

    // O(logN) -- AND of the values < x in a[l..r]; -1 (every bit) if there are none; needs lo <= l <= r <= hi, else
    // throws out_of_range
    LEETCODE_NO_SANITIZE T andLtX(long long l, long long r, T x) const {
        if (l < lo || l > r || r > hi) throw out_of_range("andLtX: needs lo <= l <= r <= hi");
        auto [i0, i1, zeros] = span(l, r);
        if (zeros && T(0) < x) return T(0);  // a 0 in range makes the AND 0
        return i0 <= i1 ? inner.andLtX(i0, i1, x) : ~T(0);
    }

    // O(logN) -- AND of the values <= x in a[l..r]; -1 (every bit) if there are none; needs lo <= l <= r <= hi, else
    // throws out_of_range
    LEETCODE_NO_SANITIZE T andLteX(long long l, long long r, T x) const {
        if (l < lo || l > r || r > hi) throw out_of_range("andLteX: needs lo <= l <= r <= hi");
        auto [i0, i1, zeros] = span(l, r);
        if (zeros && T(0) <= x) return T(0);  // a 0 in range makes the AND 0
        return i0 <= i1 ? inner.andLteX(i0, i1, x) : ~T(0);
    }

    // O(logN) -- AND of the values > x in a[l..r]; -1 (every bit) if there are none; needs lo <= l <= r <= hi, else
    // throws out_of_range
    LEETCODE_NO_SANITIZE T andGtX(long long l, long long r, T x) const {
        if (l < lo || l > r || r > hi) throw out_of_range("andGtX: needs lo <= l <= r <= hi");
        auto [i0, i1, zeros] = span(l, r);
        if (zeros && x < T(0)) return T(0);  // a 0 in range makes the AND 0
        return i0 <= i1 ? inner.andGtX(i0, i1, x) : ~T(0);
    }

    // O(logN) -- AND of the values >= x in a[l..r]; -1 (every bit) if there are none; needs lo <= l <= r <= hi, else
    // throws out_of_range
    LEETCODE_NO_SANITIZE T andGteX(long long l, long long r, T x) const {
        if (l < lo || l > r || r > hi) throw out_of_range("andGteX: needs lo <= l <= r <= hi");
        auto [i0, i1, zeros] = span(l, r);
        if (zeros && x <= T(0)) return T(0);  // a 0 in range makes the AND 0
        return i0 <= i1 ? inner.andGteX(i0, i1, x) : ~T(0);
    }

    // O(logN) -- AND of the a[i] with lowVal <= a[i] <= highVal in a[l..r]; -1 (every bit) if there are none; needs
    // lo <= l <= r <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE T andInValRange(long long l, long long r, T lowVal, T highVal) const {
        if (l < lo || l > r || r > hi) throw out_of_range("andInValRange: needs lo <= l <= r <= hi");
        auto [i0, i1, zeros] = span(l, r);
        if (zeros && lowVal <= T(0) && T(0) <= highVal) return T(0);  // a 0 in range makes the AND 0
        return i0 <= i1 ? inner.andInValRange(i0, i1, lowVal, highVal) : ~T(0);
    }

    // the k-th smallest of a[l..r], 1 <= k <= r - l + 1
    LEETCODE_NO_SANITIZE T kth(long long l, long long r, long long k) const {
        auto [i0, i1, zeros] = span(l, r);
        long long neg = i0 <= i1 ? inner.countLtX(i0, i1, T(0)) : 0;
        if (k <= neg) return inner.kthSmallest(i0, i1, int(k));
        if (k <= neg + zeros) return T(0);
        return inner.kthSmallest(i0, i1, int(k - zeros));
    }

    // how many of the k smallest of [l, r] are given values (the rest are zeros), with i0, i1 from span
    LEETCODE_NO_SANITIZE long long given(int i0, int i1, long long zeros, long long k) const {
        long long neg = i0 <= i1 ? inner.countLtX(i0, i1, T(0)) : 0;
        return k <= neg ? k : max(neg, k - zeros);
    }
    // sum of the k smallest of a[l..r], 0 <= k <= r - l + 1 (zeros add nothing)
    LEETCODE_NO_SANITIZE S sumFirst(long long l, long long r, long long k) const {
        auto [i0, i1, zeros] = span(l, r);
        return i0 <= i1 ? S(inner.sumSmallestK(i0, i1, int(given(i0, i1, zeros, k)))) : S(0);
    }
};
