// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/wavelet-order-stats-xor-or-tree-and-tree/template.cpp
// @operations: andGtX andGteX andInValRange andLtX andLteX countGtX countGteX countInValRange countLtX countLteX countOccurrences kthSmallest largestLtX largestLteX orGtX orGteX orInValRange orLtX orLteX pointGet rangeMax rangeMin smallestGtX smallestGteX xorGtX xorGteX xorInValRange xorLtX xorLteX
// @data-structure-type: wavelet
// @complexities:
//   andGtX: log^2(N)
//   andGteX: log^2(N)
//   andInValRange: log^2(N)
//   andLtX: log^2(N)
//   andLteX: log^2(N)
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
//   smallestGtX: log(N)
//   smallestGteX: log(N)
//   xorGtX: log(N)
//   xorGteX: log(N)
//   xorInValRange: log(N)
//   xorLtX: log(N)
//   xorLteX: log(N)
//   build: N*log(N)
// @memory:
//   layout: none
//   node: zeros[1*N*log(N)] arr[1*N] srt[1*N] xt[1*N*log(N)] ot[2*N*log(N)] at[2*N*log(N)]
//   tags: none
//   other: none
//   note: wavelet matrix: one row of N + 1 prefix counts per bit of the compressed value; xor by value: per level, prefix xors of its order; OR by value: per level, a segment tree over its order (O(log N) a window); AND by value: per level, a segment tree over its order (O(log N) a window)

// Static array. Each query treats a[l..r] (0-indexed, inclusive) as a sorted multiset. Values are compressed to ranks
// 0..m-1 once, so costs are log of the number of distinct values, never of the value range; query arguments (x,
// lowVal, ...) can be anything. Level d of the wavelet matrix (top bit first) stably splits the current order into the
// ranks with that bit 0, then 1; zeros[d][i] = # of the first i elements of level d's order with the bit 0.
// T: int, long long, ....
template <typename T>
struct WaveletMatrix {
    int n, m, bits;
    vector<T> arr, srt;  // srt: sorted distinct values
    vector<int> zeros;   // level lv's row is zeros[lv * (n + 1) .. lv * (n + 1) + n]
    vector<vector<T>> xt;  // per level, xor over its order
    vector<vector<T>> ot;  // per level, OR over its order
    vector<vector<T>> at;  // per level, AND over its order

    // O(N log N) -- arr: the initial array, 0-indexed
    explicit WaveletMatrix(const vector<T>& a) : n((int)a.size()), arr(a), srt(a) {
        sort(srt.begin(), srt.end());
        srt.erase(unique(srt.begin(), srt.end()), srt.end());
        m = (int)srt.size();
        bits = 1;
        while ((1 << bits) < m) bits++;
        zeros.assign((size_t)bits * (n + 1), 0);
        xt.resize(bits + 1);
        ot.resize(bits + 1);
        at.resize(bits + 1);
        vector<int> cur(n), nxt(n);
        for (int i = 0; i < n; i++) cur[i] = lb(a[i]);
        vector<T> vals(n);
        auto order = [&](int lv) {  // the level's order, as values
            for (int i = 0; i < n; i++) vals[i] = srt[cur[i]];
            xorBuild(lv, vals);
            orBuild(lv, vals);
            andBuild(lv, vals);
        };
        for (int lv = 0; lv < bits; lv++) {
            order(lv);
            int d = bits - 1 - lv, k = 0, *z = &zeros[(size_t)lv * (n + 1)];
            for (int i = 0; i < n; i++) {
                bool one = (cur[i] >> d) & 1;
                z[i + 1] = z[i] + !one;
            }
            for (int v : cur) if (!((v >> d) & 1)) nxt[k++] = v;
            for (int v : cur) if ((v >> d) & 1) nxt[k++] = v;
            swap(cur, nxt);
        }
        order(bits);  // (the final order)
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

    // O(logN) -- xor of the values < x in a[l..r] (copies count); 0 if there are none
    T xorLtX(int l, int r, T x) const {
        return xorRanks(l, r, 0, lb(x));
    }

    // O(logN) -- xor of the values <= x in a[l..r] (copies count); 0 if there are none
    T xorLteX(int l, int r, T x) const {
        return xorRanks(l, r, 0, ub(x));
    }

    // O(logN) -- xor of the values > x in a[l..r] (copies count); 0 if there are none
    T xorGtX(int l, int r, T x) const {
        return xorRanks(l, r, ub(x), m);
    }

    // O(logN) -- xor of the values >= x in a[l..r] (copies count); 0 if there are none
    T xorGteX(int l, int r, T x) const {
        return xorRanks(l, r, lb(x), m);
    }

    // O(logN) -- xor of the a[i] with lowVal <= a[i] <= highVal in a[l..r] (copies count); 0 if there are none
    T xorInValRange(int l, int r, T lowVal, T highVal) const {
        if (highVal < lowVal) return T(0);
        return xorRanks(l, r, lb(lowVal), ub(highVal));
    }

    // O(log^2 N) -- OR of the values < x in a[l..r]; 0 if there are none
    T orLtX(int l, int r, T x) const {
        return orRanks(l, r, 0, lb(x));
    }

    // O(log^2 N) -- OR of the values <= x in a[l..r]; 0 if there are none
    T orLteX(int l, int r, T x) const {
        return orRanks(l, r, 0, ub(x));
    }

    // O(log^2 N) -- OR of the values > x in a[l..r]; 0 if there are none
    T orGtX(int l, int r, T x) const {
        return orRanks(l, r, ub(x), m);
    }

    // O(log^2 N) -- OR of the values >= x in a[l..r]; 0 if there are none
    T orGteX(int l, int r, T x) const {
        return orRanks(l, r, lb(x), m);
    }

    // O(log^2 N) -- OR of the a[i] with lowVal <= a[i] <= highVal in a[l..r]; 0 if there are none
    T orInValRange(int l, int r, T lowVal, T highVal) const {
        if (highVal < lowVal) return T(0);
        return orRanks(l, r, lb(lowVal), ub(highVal));
    }

    // O(log^2 N) -- AND of the values < x in a[l..r]; -1 (every bit) if there are none
    T andLtX(int l, int r, T x) const {
        return andRanks(l, r, 0, lb(x));
    }

    // O(log^2 N) -- AND of the values <= x in a[l..r]; -1 (every bit) if there are none
    T andLteX(int l, int r, T x) const {
        return andRanks(l, r, 0, ub(x));
    }

    // O(log^2 N) -- AND of the values > x in a[l..r]; -1 (every bit) if there are none
    T andGtX(int l, int r, T x) const {
        return andRanks(l, r, ub(x), m);
    }

    // O(log^2 N) -- AND of the values >= x in a[l..r]; -1 (every bit) if there are none
    T andGteX(int l, int r, T x) const {
        return andRanks(l, r, lb(x), m);
    }

    // O(log^2 N) -- AND of the a[i] with lowVal <= a[i] <= highVal in a[l..r]; -1 (every bit) if there are none
    T andInValRange(int l, int r, T lowVal, T highVal) const {
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
            if ((x >> (bits - 1 - lv)) & 1) res += zh - zl, lo = z[n] + lo - zl, hi = z[n] + hi - zh;  // all 0s are below x
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

    void andBuild(int lv, const vector<T>& vals) {  // bottom-up segment tree: leaves at n..2n-1
        auto& t = at[lv];
        t.assign(2 * n, ~T(0));
        for (int i = 0; i < n; i++) t[n + i] = vals[i];
        for (int i = n - 1; i > 0; i--) t[i] = t[2 * i] & t[2 * i + 1];
    }
    T andQ(int lv, int lo, int hi) const {
        const vector<T>& t = at[lv];
        T res = ~T(0);
        for (lo += n, hi += n; lo < hi; lo >>= 1, hi >>= 1) {
            if (lo & 1) res &= t[lo++];
            if (hi & 1) res &= t[--hi];
        }
        return res;
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
