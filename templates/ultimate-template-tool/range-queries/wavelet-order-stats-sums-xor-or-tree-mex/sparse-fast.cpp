// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/wavelet-order-stats-sums-xor-or-tree-mex/sparse-fast.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: countGtX countGteX countInValRange countLtX countLteX countOccurrences kthSmallest largestLtX largestLteX orGtX orGteX orInValRange orLtX orLteX pointGet rangeMax rangeMex rangeMin rangeSum smallestGtX smallestGteX sumAbsDiffToX sumGtX sumGteX sumInValRange sumKthLargestRange sumKthSmallestRange sumLargestK sumLtX sumLteX sumSmallestK xorGtX xorGteX xorInValRange xorLtX xorLteX
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
//   pointGet: log(N)
//   rangeMax: log(N)
//   rangeMex: log(N)
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
//   layout: sparse
//   node: idx[1*N] vals[1*N] zeros[1*N*log(N)] zsum[1*N*log(N)] arr[1*N] srt[1*N] mexRoot[1*N] ML[1*N*log(N)] MR[1*N*log(N)] MN[1*N*log(N)] xt[1*N*log(N)] ot[2*N*log(N)]
//   tags: none
//   other: none
//   note: built from N given values (index, value pairs) over any index range [lo, hi], every other index 0; costs are in N; wavelet matrix: one row of N + 1 prefix counts per bit of the compressed value, plus one row of prefix sums of the values that go left; rangeMex uses a persistent seg tree over the values 0..N+1 holding each value's last index; xor by value: per level, prefix xors of its order; OR by value: per level, a segment tree over its order (O(log N) a window); the structure is over the given values only, and the zeros of [l, r] are added in closed form (they sit between the negatives and the positives)

// Static array. Each query treats a[l..r] (0-indexed, inclusive) as a sorted multiset. Values are compressed to ranks
// 0..m-1 once, so costs are log of the number of distinct values, never of the value range; query arguments (x,
// lowVal, ...) can be anything. Level d of the wavelet matrix (top bit first) stably splits the current order into the
// ranks with that bit 0, then 1; zeros[d][i] = # of the first i elements of level d's order with the bit 0.
// zsum[d][i] = sum of the values among the first i elements of level d's order whose bit is 0.
// rangeMex: a persistent seg tree over the values 0..N+1; version p holds, per value, its last index before p (-1 if
// none). The mex of a[l..r] is the first value whose last index in version r + 1 is < l.
// T: int, long long, ...; sums are kept in S (long long for small T).
template <typename T>
struct WaveletMatrix {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    int n, m, bits;
    vector<T> arr, srt;  // srt: sorted distinct values
    vector<int> zeros;   // level lv's row is zeros[lv * (n + 1) .. lv * (n + 1) + n]
    vector<S> zsum;      // same layout as zeros
    vector<int> mexRoot, ML, MR, MN;  // the persistent mex tree
    vector<vector<T>> xt;  // per level, xor over its order
    vector<vector<T>> ot;  // per level, OR over its order

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
        buildMex();
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

    // O(logN) -- smallest integer >= 0 that is not in a[l..r]; needs 0 <= l <= r < n, else throws out_of_range
    int rangeMex(int l, int r) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeMex: needs 0 <= l <= r < n");
        return mexFrom(l, r, 0);
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

    // O(log^2 N) -- OR of the values < x in a[l..r]; 0 if there are none; needs 0 <= l <= r < n, else throws
    // out_of_range
    T orLtX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("orLtX: needs 0 <= l <= r < n");
        return orRanks(l, r, 0, lb(x));
    }

    // O(log^2 N) -- OR of the values <= x in a[l..r]; 0 if there are none; needs 0 <= l <= r < n, else throws
    // out_of_range
    T orLteX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("orLteX: needs 0 <= l <= r < n");
        return orRanks(l, r, 0, ub(x));
    }

    // O(log^2 N) -- OR of the values > x in a[l..r]; 0 if there are none; needs 0 <= l <= r < n, else throws
    // out_of_range
    T orGtX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("orGtX: needs 0 <= l <= r < n");
        return orRanks(l, r, ub(x), m);
    }

    // O(log^2 N) -- OR of the values >= x in a[l..r]; 0 if there are none; needs 0 <= l <= r < n, else throws
    // out_of_range
    T orGteX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("orGteX: needs 0 <= l <= r < n");
        return orRanks(l, r, lb(x), m);
    }

    // O(log^2 N) -- OR of the a[i] with lowVal <= a[i] <= highVal in a[l..r]; 0 if there are none; needs
    // 0 <= l <= r < n, else throws out_of_range
    T orInValRange(int l, int r, T lowVal, T highVal) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("orInValRange: needs 0 <= l <= r < n");
        if (highVal < lowVal) return T(0);
        return orRanks(l, r, lb(lowVal), ub(highVal));
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

    // persistent seg tree over the values 0..n+1: version p holds, per value, its last index before p (-1: none)
    void buildMex() {
        ML.assign(1, 0), MR.assign(1, 0), MN.assign(1, -1);  // node 0 = the empty tree (every last index -1)
        mexRoot.assign(n + 1, 0);
        for (int i = 0; i < n; i++)
            mexRoot[i + 1] = T(0) <= arr[i] && arr[i] <= T(n + 1) ? mexSet(mexRoot[i], 0, n + 1, int(arr[i]),
                i) : mexRoot[i];
    }

    // copy of node with value v's last index set to i
    int mexSet(int node, int nl, int nh, int v, int i) {
        int l = ML[node], r = MR[node], x;
        if (nl == nh) x = i;
        else {
            int mid = (nl + nh) >> 1;
            if (v <= mid) l = mexSet(l, nl, mid, v, i);
            else r = mexSet(r, mid + 1, nh, v, i);
            x = min(MN[l], MN[r]);
        }
        ML.push_back(nl == nh ? 0 : l), MR.push_back(nl == nh ? 0 : r), MN.push_back(x);
        return (int)MN.size() - 1;
    }

    // smallest value >= s that is not in a[l..r]: the leftmost value >= s whose last index (as of r) is < l
    int mexFrom(int l, int r, int s) const {
        auto go = [&](auto&& self, int t, int nl, int nh) -> int {
            if (nh < s || MN[t] >= l) return -1;  // nothing allowed here, or every value here is in a[l..r]
            if (!t) return max(nl, s);            // no value here was ever seen
            if (nl == nh) return nl;
            int mid = (nl + nh) >> 1, res = self(self, ML[t], nl, mid);
            return res >= 0 ? res : self(self, MR[t], mid + 1, nh);
        };
        return go(go, mexRoot[r + 1], 0, n + 1);
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

    void orBuild(int lv, const vector<T>& vals) {  // bottom-up segment tree: leaves at n..2n-1
        auto& t = ot[lv];
        t.assign(2 * n, T(0));
        for (int i = 0; i < n; i++) t[n + i] = vals[i];
        for (int i = n - 1; i > 0; i--) t[i] = t[2 * i] | t[2 * i + 1];
    }
    T orQ(int lv, int lo, int hi) const {
        const vector<T>& t = ot[lv];
        T res = T(0);
        for (lo += n, hi += n; lo < hi; lo >>= 1, hi >>= 1) {
            if (lo & 1) res |= t[lo++];
            if (hi & 1) res |= t[--hi];
        }
        return res;
    }

    // OR of the a[i], i in [l, r], whose rank is in [a, b): whole windows of the levels' orders
    T orRanks(int l, int r, int a, int b) const {
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

// ======================================================================================== sparse wrapper

// The same queries over any index range [lo, hi], built from given values (index, value pairs); every other index is 0.
// The structure above runs on the given values alone (in index order). [l, r] covers given values i0..i1 and
// zeros = (r - l + 1) - (i1 - i0 + 1) zeros, and in sorted order those zeros sit right after the given negatives, so
// the
// k-th smallest of [l, r] is the given k-th while k <= neg, 0 while k <= neg + zeros, then the given (k - zeros)-th.
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

    // O(logN) -- smallest integer >= 0 that is not in a[l..r]; needs lo <= l <= r <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE long long rangeMex(long long l, long long r) const {
        if (l < lo || l > r || r > hi) throw out_of_range("rangeMex: needs lo <= l <= r <= hi");
        auto [i0, i1, zeros] = span(l, r);
        if (i0 > i1) return 1;  // all zeros
        return zeros ? inner.mexFrom(i0, i1, 1) : inner.rangeMex(i0, i1);
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

    // O(logN) -- OR of the values < x in a[l..r]; 0 if there are none (the zeros add nothing); needs
    // lo <= l <= r <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE T orLtX(long long l, long long r, T x) const {
        if (l < lo || l > r || r > hi) throw out_of_range("orLtX: needs lo <= l <= r <= hi");
        auto [i0, i1, zeros] = span(l, r);
        return i0 <= i1 ? inner.orLtX(i0, i1, x) : T(0);
    }

    // O(logN) -- OR of the values <= x in a[l..r]; 0 if there are none (the zeros add nothing); needs
    // lo <= l <= r <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE T orLteX(long long l, long long r, T x) const {
        if (l < lo || l > r || r > hi) throw out_of_range("orLteX: needs lo <= l <= r <= hi");
        auto [i0, i1, zeros] = span(l, r);
        return i0 <= i1 ? inner.orLteX(i0, i1, x) : T(0);
    }

    // O(logN) -- OR of the values > x in a[l..r]; 0 if there are none (the zeros add nothing); needs
    // lo <= l <= r <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE T orGtX(long long l, long long r, T x) const {
        if (l < lo || l > r || r > hi) throw out_of_range("orGtX: needs lo <= l <= r <= hi");
        auto [i0, i1, zeros] = span(l, r);
        return i0 <= i1 ? inner.orGtX(i0, i1, x) : T(0);
    }

    // O(logN) -- OR of the values >= x in a[l..r]; 0 if there are none (the zeros add nothing); needs
    // lo <= l <= r <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE T orGteX(long long l, long long r, T x) const {
        if (l < lo || l > r || r > hi) throw out_of_range("orGteX: needs lo <= l <= r <= hi");
        auto [i0, i1, zeros] = span(l, r);
        return i0 <= i1 ? inner.orGteX(i0, i1, x) : T(0);
    }

    // O(logN) -- OR of the a[i] with lowVal <= a[i] <= highVal in a[l..r]; 0 if there are none (the zeros add
    // nothing); needs lo <= l <= r <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE T orInValRange(long long l, long long r, T lowVal, T highVal) const {
        if (l < lo || l > r || r > hi) throw out_of_range("orInValRange: needs lo <= l <= r <= hi");
        auto [i0, i1, zeros] = span(l, r);
        return i0 <= i1 ? inner.orInValRange(i0, i1, lowVal, highVal) : T(0);
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
