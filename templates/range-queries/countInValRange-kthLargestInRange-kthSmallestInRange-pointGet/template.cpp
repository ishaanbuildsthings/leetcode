// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/countInValRange-kthLargestInRange-kthSmallestInRange-pointGet/template.cpp
// @operations: countInValRange kthLargestInRange kthSmallestInRange pointGet
// @data-structure-type: wavelet
// @complexities:
//   countInValRange: log(N)
//   kthLargestInRange: log(N)
//   kthSmallestInRange: log(N)
//   pointGet: 1
//   build: N*log(N)
// @memory:
//   layout: none
//   node: zeros[1*N*log(N)]
//   tags: none
//   other: arr[1*N] srt[1*N]
//   note: one row of N + 1 prefix counts per bit of the compressed value (wavelet matrix); no pointers, no per-node lists

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
