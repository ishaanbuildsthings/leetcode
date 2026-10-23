// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/countInValRange-kthLargestInRange-kthSmallestInRange-pointGet/sparse.cpp
// @operations: countInValRange kthLargestInRange kthSmallestInRange pointGet
// @data-structure-type: wavelet
// @complexities:
//   countInValRange: log(N)
//   kthLargestInRange: log(N)
//   kthSmallestInRange: log(N)
//   pointGet: log(N)
//   build: N*log(N)
// @memory:
//   layout: sparse
//   node: zeros[1*N*log(N)]
//   tags: none
//   other: idx[1*N] vals[1*N] arr[1*N] srt[1*N]
//   note: built from N given values (index, value pairs) over any index range [lo, hi], every other index 0; costs are in N; the wavelet matrix is over the given values only; zeros add to counts and sit between the negatives and the positives for a k-th
// Static "k-th smallest / largest of a[l..r]" and "count of a[l..r] in [lowVal, highVal]" via a wavelet matrix over
// compressed values (costs are log of the number of distinct values, never of the value range). Level d (top bit
// first) stably splits the current order into ranks with that bit 0, then bit 1; zeros[d][i] = # of the first i
// elements of level d's order with the bit 0. Indices 0-based, ranges inclusive. Everything is iterative.
// T: int, long long, ...
template <typename T>
struct WaveletMatrix {
    int n, m, bits;
    vector<T> arr, srt;  // srt: sorted distinct values
    vector<int> zeros;   // level d's row is zeros[d * (n + 1) .. d * (n + 1) + n]

    // O(N log N)
    explicit WaveletMatrix(const vector<T>& a) : n((int)a.size()), arr(a), srt(a) {
        sort(srt.begin(), srt.end());
        srt.erase(unique(srt.begin(), srt.end()), srt.end());
        m = (int)srt.size();
        bits = 1;
        while ((1 << bits) < m) bits++;
        zeros.assign((size_t)bits * (n + 1), 0);
        vector<int> cur(n), nxt(n);
        for (int i = 0; i < n; i++) cur[i] = int(lower_bound(srt.begin(), srt.end(), a[i]) - srt.begin());
        for (int lv = 0; lv < bits; lv++) {
            int d = bits - 1 - lv, *z = &zeros[(size_t)lv * (n + 1)], k = 0;
            for (int i = 0; i < n; i++) z[i + 1] = z[i] + !((cur[i] >> d) & 1);
            for (int v : cur) if (!((v >> d) & 1)) nxt[k++] = v;
            for (int v : cur) if ((v >> d) & 1) nxt[k++] = v;
            swap(cur, nxt);
        }
    }

    // O(logN) -- the k-th smallest of a[l..r] (k = 1 is the min); needs 1 <= k <= r - l + 1, else throws out_of_range
    T kthSmallestInRange(int l, int r, int k) const {
        if (k < 1 || k > r - l + 1) throw out_of_range("kthSmallestInRange: k outside [1, r - l + 1]");
        int lo = l, hi = r + 1, rank = 0;
        for (int lv = 0; lv < bits; lv++) {
            const int* z = &zeros[(size_t)lv * (n + 1)];
            int zl = z[lo], zh = z[hi];
            if (k <= zh - zl) lo = zl, hi = zh;  // enough 0s at this bit: the answer has it 0
            else k -= zh - zl, rank |= 1 << (bits - 1 - lv), lo = z[n] + lo - zl, hi = z[n] + hi - zh;
        }
        return srt[rank];
    }

    // O(logN) -- the k-th largest of a[l..r] (k = 1 is the max); needs 1 <= k <= r - l + 1, else throws out_of_range
    T kthLargestInRange(int l, int r, int k) const {
        if (k < 1 || k > r - l + 1) throw out_of_range("kthLargestInRange: k outside [1, r - l + 1]");
        return kthSmallestInRange(l, r, r - l + 2 - k);
    }

    // O(logN) -- # of i in [l, r] with lowVal <= a[i] <= highVal
    int countInValRange(int l, int r, const T& lowVal, const T& highVal) const {
        if (highVal < lowVal) return 0;
        return countBelow(l, r, int(upper_bound(srt.begin(), srt.end(), highVal) - srt.begin())) -
               countBelow(l, r, int(lower_bound(srt.begin(), srt.end(), lowVal) - srt.begin()));
    }

    // # of i in [l, r] whose rank is < x
    int countBelow(int l, int r, int x) const {
        if (x <= 0) return 0;
        if (x >= m) return r - l + 1;
        int lo = l, hi = r + 1, res = 0;
        for (int lv = 0; lv < bits; lv++) {
            const int* z = &zeros[(size_t)lv * (n + 1)];
            int zl = z[lo], zh = z[hi];
            if ((x >> (bits - 1 - lv)) & 1) res += zh - zl, lo = z[n] + lo - zl, hi = z[n] + hi - zh;  // all 0s are below x
            else lo = zl, hi = zh;
        }
        return res;
    }

    // O(1) -- a[i]
    T pointGet(int i) const { return arr[i]; }
};

// ======================================================================================== sparse wrapper

// Count of values in a value range and k-th smallest / largest, over any index range [lo, hi], built from given values
// (index, value pairs); every other index is 0. The wavelet matrix runs on the given values alone; the zeros of [l, r]
// (its length minus the given values inside) add to a count when 0 is in the value range, and sit between the given
// negatives and positives for a k-th.
template <typename T>
struct SparseWaveletMatrix {
    long long lo, hi;
    vector<long long> idx;
    vector<T> vals;
    WaveletMatrix<T> inner;

    // O(N log N) -- [lo, hi] all 0 except the given values: (index, value) pairs with distinct indices; N = len(values)
    SparseWaveletMatrix(long long lo, long long hi, vector<pair<long long, T>> values) : lo(lo), hi(hi), inner(split(values)) {}

    vector<T> split(vector<pair<long long, T>>& pts) {
        sort(pts.begin(), pts.end());
        for (auto& [i, v] : pts) idx.push_back(i), vals.push_back(v);
        return vals.empty() ? vector<T>{T(0)} : vals;  // (a dummy element when there are no given values; never queried)
    }

    // the given values inside [l, r] are i0..i1, and the rest of [l, r] is zeros = (r - l + 1) - (i1 - i0 + 1) zeros
    void span(long long l, long long r, int& i0, int& i1, long long& zeros) const {
        i0 = int(lower_bound(idx.begin(), idx.end(), l) - idx.begin());
        i1 = int(upper_bound(idx.begin(), idx.end(), r) - idx.begin()) - 1;
        zeros = (r - l + 1) - (i1 - i0 + 1);
    }

    // O(logN) -- # of i in [l, r] with valLow <= a[i] <= valHigh
    long long countInValRange(long long l, long long r, T valLow, T valHigh) const {
        int i0, i1;
        long long zeros;
        span(l, r, i0, i1, zeros);
        long long inside = i0 <= i1 ? inner.countInValRange(i0, i1, valLow, valHigh) : 0;
        return inside + (valLow <= T(0) && T(0) <= valHigh ? zeros : 0);
    }

    // O(logN) -- the k-th smallest of a[l..r] (k = 1 is the min); needs 1 <= k <= r - l + 1, else throws out_of_range
    T kthSmallestInRange(long long l, long long r, long long k) const {
        if (k < 1 || k > r - l + 1) throw out_of_range("kthSmallestInRange: k outside [1, r - l + 1]");
        int i0, i1;
        long long zeros;
        span(l, r, i0, i1, zeros);
        long long neg = i0 <= i1 ? inner.countInValRange(i0, i1, numeric_limits<T>::lowest(), T(-1)) : 0;
        if (k <= neg) return inner.kthSmallestInRange(i0, i1, int(k));
        if (k <= neg + zeros) return T(0);
        return inner.kthSmallestInRange(i0, i1, int(k - zeros));
    }

    // O(logN) -- the k-th largest of a[l..r] (k = 1 is the max); needs 1 <= k <= r - l + 1, else throws out_of_range
    T kthLargestInRange(long long l, long long r, long long k) const {
        if (k < 1 || k > r - l + 1) throw out_of_range("kthLargestInRange: k outside [1, r - l + 1]");
        return kthSmallestInRange(l, r, r - l + 2 - k);
    }

    // O(logN) -- a[i]
    T pointGet(long long i) const {
        auto it = lower_bound(idx.begin(), idx.end(), i);
        return it != idx.end() && *it == i ? vals[it - idx.begin()] : T(0);
    }
};
