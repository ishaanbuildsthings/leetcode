// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/wavelet-order-stats-sums/template.cpp
// @operations: countGtX countGteX countInValRange countLtX countLteX countOccurrences kthLargest kthSmallest largestLtX largestLteX medianHigh medianLow pointGet rangeMax rangeMin rangeSum smallestGtX smallestGteX sumAbsDiffToMedian sumAbsDiffToX sumGtX sumGteX sumInValRange sumKthLargestRange sumKthSmallestRange sumLargestK sumLtX sumLteX sumSmallestK
// @data-structure-type: wavelet
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
//   pointGet: 1
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
//   layout: none
//   node: zeros[1*N*log(N)] zsum[1*N*log(N)] arr[1*N] srt[1*N]
//   tags: none
//   other: none
//   note: wavelet matrix: one row of N + 1 prefix counts per bit of the compressed value, plus one row of prefix sums of the values that go left

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

    // O(N log N) -- arr: the initial array, 0-indexed
    explicit WaveletMatrix(const vector<T>& a) : n((int)a.size()), arr(a), srt(a) {
        sort(srt.begin(), srt.end());
        srt.erase(unique(srt.begin(), srt.end()), srt.end());
        m = (int)srt.size();
        bits = 1;
        while ((1 << bits) < m) bits++;
        zeros.assign((size_t)bits * (n + 1), 0);
        zsum.assign((size_t)bits * (n + 1), S(0));
        vector<int> cur(n), nxt(n);
        for (int i = 0; i < n; i++) cur[i] = lb(a[i]);
        for (int lv = 0; lv < bits; lv++) {
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

    // O(logN) -- sum of the kFrom-th..kTo-th smallest values of a[l..r] (1-indexed, inclusive); needs 1 <= kFrom <= kTo <= r - l + 1,
    // else throws out_of_range
    S sumKthSmallestRange(int l, int r, int kFrom, int kTo) const {
        if (kFrom < 1 || kFrom > kTo || kTo > r - l + 1) throw out_of_range("sumKthSmallestRange: needs 1 <= kFrom <= kTo <= r - l + 1");
        return sumFirst(l, r, kTo) - sumFirst(l, r, kFrom - 1);
    }

    // O(logN) -- sum of the kFrom-th..kTo-th largest values of a[l..r] (1-indexed, inclusive; (1, 3) = the 3 biggest); needs
    // 1 <= kFrom <= kTo <= r - l + 1, else throws out_of_range
    S sumKthLargestRange(int l, int r, int kFrom, int kTo) const {
        int n = r - l + 1;
        if (kFrom < 1 || kFrom > kTo || kTo > n) throw out_of_range("sumKthLargestRange: needs 1 <= kFrom <= kTo <= r - l + 1");
        return sumFirst(l, r, n - kFrom + 1) - sumFirst(l, r, n - kTo);
    }

    // O(logN) -- sum of |a[i] - x| over i in [l, r]
    S sumAbsDiffToX(int l, int r, T x) const {
        int rk = lb(x), c = countBelow(l, r, rk);
        S s = sumBelow(l, r, rk);
        return S(x) * c - s + (sumFirst(l, r, r - l + 1) - s) - S(x) * (r - l + 1 - c);
    }

    // O(logN) -- sum of |a[i] - medianLow(l, r)| over i in [l, r]: the min total +-1 moves to make a[l..r] all equal
    S sumAbsDiffToMedian(int l, int r) const { return sumAbsDiffToX(l, r, kth(l, r, (r - l + 2) / 2)); }

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
            if ((x >> (bits - 1 - lv)) & 1) res += zh - zl, lo = z[n] + lo - zl, hi = z[n] + hi - zh;  // all 0s are below x
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
            else k -= zh - zl, res += zs[hi] - zs[lo], rank |= 1 << (bits - 1 - lv), lo = z[n] + lo - zl, hi = z[n] + hi - zh;
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
};
