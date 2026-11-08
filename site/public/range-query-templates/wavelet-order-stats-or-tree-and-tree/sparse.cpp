// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/wavelet-order-stats-or-tree-and-tree/sparse.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: andGtX andGteX andInValRange andLtX andLteX countGtX countGteX countInValRange countLtX countLteX countOccurrences kthSmallest largestLtX largestLteX orGtX orGteX orInValRange orLtX orLteX pointGet rangeMax rangeMin smallestGtX smallestGteX
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
//   pointGet: log(N)
//   rangeMax: log(N)
//   rangeMin: log(N)
//   smallestGtX: log(N)
//   smallestGteX: log(N)
//   build: N*log(N)
// @memory:
//   layout: sparse
//   node: idx[1*N] vals[1*N] zeros[1*N*log(N)] arr[1*N] srt[1*N] ot[2*N*log(N)] at[2*N*log(N)]
//   tags: none
//   other: none
//   note: built from N given values (index, value pairs) over any index range [lo, hi], every other index 0; costs are in N; wavelet matrix: one row of N + 1 prefix counts per bit of the compressed value; OR by value: per level, a segment tree over its order (O(log N) a window); AND by value: per level, a segment tree over its order (O(log N) a window); the structure is over the given values only, and the zeros of [l, r] are added in closed form (they sit between the negatives and the positives)

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
        ot.resize(bits + 1);
        at.resize(bits + 1);
        vector<int> cur(n), nxt(n);
        for (int i = 0; i < n; i++) cur[i] = lb(a[i]);
        vector<T> vals(n);
        auto order = [&](int lv) {  // the level's order, as values
            for (int i = 0; i < n; i++) vals[i] = srt[cur[i]];
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

    // O(log^2 N) -- AND of the values < x in a[l..r]; -1 (every bit) if there are none; needs 0 <= l <= r < n, else
    // throws out_of_range
    T andLtX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("andLtX: needs 0 <= l <= r < n");
        return andRanks(l, r, 0, lb(x));
    }

    // O(log^2 N) -- AND of the values <= x in a[l..r]; -1 (every bit) if there are none; needs 0 <= l <= r < n, else
    // throws out_of_range
    T andLteX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("andLteX: needs 0 <= l <= r < n");
        return andRanks(l, r, 0, ub(x));
    }

    // O(log^2 N) -- AND of the values > x in a[l..r]; -1 (every bit) if there are none; needs 0 <= l <= r < n, else
    // throws out_of_range
    T andGtX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("andGtX: needs 0 <= l <= r < n");
        return andRanks(l, r, ub(x), m);
    }

    // O(log^2 N) -- AND of the values >= x in a[l..r]; -1 (every bit) if there are none; needs 0 <= l <= r < n, else
    // throws out_of_range
    T andGteX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("andGteX: needs 0 <= l <= r < n");
        return andRanks(l, r, lb(x), m);
    }

    // O(log^2 N) -- AND of the a[i] with lowVal <= a[i] <= highVal in a[l..r]; -1 (every bit) if there are none;
    // needs 0 <= l <= r < n, else throws out_of_range
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
            if ((x >> (bits - 1 - lv)) & 1) res += zh - zl, lo = z[n] + lo - zl, hi = z[n] + hi - zh;  // all 0s are below x
            else lo = zl, hi = zh;
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

// ======================================================================================== sparse wrapper

// The same queries over any index range [lo, hi], built from given values (index, value pairs); every other index is 0.
// The structure above runs on the given values alone (in index order). [l, r] covers given values i0..i1 and
// zeros = (r - l + 1) - (i1 - i0 + 1) zeros, and in sorted order those zeros sit right after the given negatives, so the
// k-th smallest of [l, r] is the given k-th while k <= neg, 0 while k <= neg + zeros, then the given (k - zeros)-th.
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

    // {i0, i1, zeros}: the given values inside [l, r] are i0..i1, and the rest of [l, r] is that many zeros
    tuple<int, int, long long> span(long long l, long long r) const {
        int i0 = int(lower_bound(idx.begin(), idx.end(), l) - idx.begin());
        int i1 = int(upper_bound(idx.begin(), idx.end(), r) - idx.begin()) - 1;
        return {i0, i1, (r - l + 1) - (i1 - i0 + 1)};
    }

    // O(logN) -- a[i]; needs lo <= i <= hi, else throws out_of_range
    T pointGet(long long i) const {
        if (i < lo || i > hi) throw out_of_range("pointGet: needs lo <= i <= hi");
        auto it = lower_bound(idx.begin(), idx.end(), i);
        return it != idx.end() && *it == i ? vals[it - idx.begin()] : T(0);
    }

    // O(logN) -- # of i in [l, r] with a[i] == x; needs lo <= l <= r <= hi, else throws out_of_range
    long long countOccurrences(long long l, long long r, T x) const {
        if (l < lo || l > r || r > hi) throw out_of_range("countOccurrences: needs lo <= l <= r <= hi");
        auto [i0, i1, zeros] = span(l, r);
        return (i0 <= i1 ? inner.countOccurrences(i0, i1, x) : 0) + (x == T(0) ? zeros : 0);
    }

    // O(logN) -- # of i in [l, r] with lowVal <= a[i] <= highVal; needs lo <= l <= r <= hi, else throws out_of_range
    long long countInValRange(long long l, long long r, T lowVal, T highVal) const {
        if (l < lo || l > r || r > hi) throw out_of_range("countInValRange: needs lo <= l <= r <= hi");
        auto [i0, i1, zeros] = span(l, r);
        return (i0 <= i1 ? inner.countInValRange(i0, i1, lowVal, highVal) : 0) + (lowVal <= T(0) && T(0) <= highVal ? zeros : 0);
    }

    // O(logN) -- # of values < x in a[l..r]; needs lo <= l <= r <= hi, else throws out_of_range
    long long countLtX(long long l, long long r, T x) const {
        if (l < lo || l > r || r > hi) throw out_of_range("countLtX: needs lo <= l <= r <= hi");
        auto [i0, i1, zeros] = span(l, r);
        return (i0 <= i1 ? inner.countLtX(i0, i1, x) : 0) + (T(0) < x ? zeros : 0);
    }

    // O(logN) -- # of values <= x in a[l..r]; needs lo <= l <= r <= hi, else throws out_of_range
    long long countLteX(long long l, long long r, T x) const {
        if (l < lo || l > r || r > hi) throw out_of_range("countLteX: needs lo <= l <= r <= hi");
        auto [i0, i1, zeros] = span(l, r);
        return (i0 <= i1 ? inner.countLteX(i0, i1, x) : 0) + (T(0) <= x ? zeros : 0);
    }

    // O(logN) -- # of values > x in a[l..r]; needs lo <= l <= r <= hi, else throws out_of_range
    long long countGtX(long long l, long long r, T x) const {
        if (l < lo || l > r || r > hi) throw out_of_range("countGtX: needs lo <= l <= r <= hi");
        auto [i0, i1, zeros] = span(l, r);
        return (i0 <= i1 ? inner.countGtX(i0, i1, x) : 0) + (x < T(0) ? zeros : 0);
    }

    // O(logN) -- # of values >= x in a[l..r]; needs lo <= l <= r <= hi, else throws out_of_range
    long long countGteX(long long l, long long r, T x) const {
        if (l < lo || l > r || r > hi) throw out_of_range("countGteX: needs lo <= l <= r <= hi");
        auto [i0, i1, zeros] = span(l, r);
        return (i0 <= i1 ? inner.countGteX(i0, i1, x) : 0) + (x <= T(0) ? zeros : 0);
    }

    // O(logN) -- the k-th smallest of a[l..r] (k = 1 is the min); needs lo <= l <= r <= hi and 1 <= k <= r - l + 1,
    // else throws out_of_range
    T kthSmallest(long long l, long long r, long long k) const {
        if (l < lo || l > r || r > hi) throw out_of_range("kthSmallest: needs lo <= l <= r <= hi");
        if (k < 1 || k > r - l + 1) throw out_of_range("kthSmallest: needs 1 <= k <= r - l + 1");
        return kth(l, r, k);
    }

    // O(logN) -- min of a[l..r]; needs lo <= l <= r <= hi, else throws out_of_range
    T rangeMin(long long l, long long r) const {
        if (l < lo || l > r || r > hi) throw out_of_range("rangeMin: needs lo <= l <= r <= hi");
        return kth(l, r, 1);
    }

    // O(logN) -- max of a[l..r]; needs lo <= l <= r <= hi, else throws out_of_range
    T rangeMax(long long l, long long r) const {
        if (l < lo || l > r || r > hi) throw out_of_range("rangeMax: needs lo <= l <= r <= hi");
        return kth(l, r, r - l + 1);
    }

    // O(logN) -- smallest value >= x in a[l..r], or nullopt; needs lo <= l <= r <= hi, else throws out_of_range
    optional<T> smallestGteX(long long l, long long r, T x) const {
        if (l < lo || l > r || r > hi) throw out_of_range("smallestGteX: needs lo <= l <= r <= hi");
        auto [i0, i1, zeros] = span(l, r);
        optional<T> a = i0 <= i1 ? inner.smallestGteX(i0, i1, x) : nullopt;
        if (zeros && x <= T(0)) a = a ? min(*a, T(0)) : T(0);
        return a;
    }

    // O(logN) -- smallest value > x in a[l..r], or nullopt; needs lo <= l <= r <= hi, else throws out_of_range
    optional<T> smallestGtX(long long l, long long r, T x) const {
        if (l < lo || l > r || r > hi) throw out_of_range("smallestGtX: needs lo <= l <= r <= hi");
        auto [i0, i1, zeros] = span(l, r);
        optional<T> a = i0 <= i1 ? inner.smallestGtX(i0, i1, x) : nullopt;
        if (zeros && x < T(0)) a = a ? min(*a, T(0)) : T(0);
        return a;
    }

    // O(logN) -- largest value <= x in a[l..r], or nullopt; needs lo <= l <= r <= hi, else throws out_of_range
    optional<T> largestLteX(long long l, long long r, T x) const {
        if (l < lo || l > r || r > hi) throw out_of_range("largestLteX: needs lo <= l <= r <= hi");
        auto [i0, i1, zeros] = span(l, r);
        optional<T> a = i0 <= i1 ? inner.largestLteX(i0, i1, x) : nullopt;
        if (zeros && T(0) <= x) a = a ? max(*a, T(0)) : T(0);
        return a;
    }

    // O(logN) -- largest value < x in a[l..r], or nullopt; needs lo <= l <= r <= hi, else throws out_of_range
    optional<T> largestLtX(long long l, long long r, T x) const {
        if (l < lo || l > r || r > hi) throw out_of_range("largestLtX: needs lo <= l <= r <= hi");
        auto [i0, i1, zeros] = span(l, r);
        optional<T> a = i0 <= i1 ? inner.largestLtX(i0, i1, x) : nullopt;
        if (zeros && T(0) < x) a = a ? max(*a, T(0)) : T(0);
        return a;
    }

    // O(log^2 N) -- OR of the values < x in a[l..r]; 0 if there are none (the zeros add nothing); needs
    // lo <= l <= r <= hi, else throws out_of_range
    T orLtX(long long l, long long r, T x) const {
        if (l < lo || l > r || r > hi) throw out_of_range("orLtX: needs lo <= l <= r <= hi");
        auto [i0, i1, zeros] = span(l, r);
        return i0 <= i1 ? inner.orLtX(i0, i1, x) : T(0);
    }

    // O(log^2 N) -- OR of the values <= x in a[l..r]; 0 if there are none (the zeros add nothing); needs
    // lo <= l <= r <= hi, else throws out_of_range
    T orLteX(long long l, long long r, T x) const {
        if (l < lo || l > r || r > hi) throw out_of_range("orLteX: needs lo <= l <= r <= hi");
        auto [i0, i1, zeros] = span(l, r);
        return i0 <= i1 ? inner.orLteX(i0, i1, x) : T(0);
    }

    // O(log^2 N) -- OR of the values > x in a[l..r]; 0 if there are none (the zeros add nothing); needs
    // lo <= l <= r <= hi, else throws out_of_range
    T orGtX(long long l, long long r, T x) const {
        if (l < lo || l > r || r > hi) throw out_of_range("orGtX: needs lo <= l <= r <= hi");
        auto [i0, i1, zeros] = span(l, r);
        return i0 <= i1 ? inner.orGtX(i0, i1, x) : T(0);
    }

    // O(log^2 N) -- OR of the values >= x in a[l..r]; 0 if there are none (the zeros add nothing); needs
    // lo <= l <= r <= hi, else throws out_of_range
    T orGteX(long long l, long long r, T x) const {
        if (l < lo || l > r || r > hi) throw out_of_range("orGteX: needs lo <= l <= r <= hi");
        auto [i0, i1, zeros] = span(l, r);
        return i0 <= i1 ? inner.orGteX(i0, i1, x) : T(0);
    }

    // O(log^2 N) -- OR of the a[i] with lowVal <= a[i] <= highVal in a[l..r]; 0 if there are none (the zeros add
    // nothing); needs lo <= l <= r <= hi, else throws out_of_range
    T orInValRange(long long l, long long r, T lowVal, T highVal) const {
        if (l < lo || l > r || r > hi) throw out_of_range("orInValRange: needs lo <= l <= r <= hi");
        auto [i0, i1, zeros] = span(l, r);
        return i0 <= i1 ? inner.orInValRange(i0, i1, lowVal, highVal) : T(0);
    }

    // O(log^2 N) -- AND of the values < x in a[l..r]; -1 (every bit) if there are none; needs lo <= l <= r <= hi, else
    // throws out_of_range
    T andLtX(long long l, long long r, T x) const {
        if (l < lo || l > r || r > hi) throw out_of_range("andLtX: needs lo <= l <= r <= hi");
        auto [i0, i1, zeros] = span(l, r);
        if (zeros && T(0) < x) return T(0);  // a 0 in range makes the AND 0
        return i0 <= i1 ? inner.andLtX(i0, i1, x) : ~T(0);
    }

    // O(log^2 N) -- AND of the values <= x in a[l..r]; -1 (every bit) if there are none; needs lo <= l <= r <= hi, else
    // throws out_of_range
    T andLteX(long long l, long long r, T x) const {
        if (l < lo || l > r || r > hi) throw out_of_range("andLteX: needs lo <= l <= r <= hi");
        auto [i0, i1, zeros] = span(l, r);
        if (zeros && T(0) <= x) return T(0);  // a 0 in range makes the AND 0
        return i0 <= i1 ? inner.andLteX(i0, i1, x) : ~T(0);
    }

    // O(log^2 N) -- AND of the values > x in a[l..r]; -1 (every bit) if there are none; needs lo <= l <= r <= hi, else
    // throws out_of_range
    T andGtX(long long l, long long r, T x) const {
        if (l < lo || l > r || r > hi) throw out_of_range("andGtX: needs lo <= l <= r <= hi");
        auto [i0, i1, zeros] = span(l, r);
        if (zeros && x < T(0)) return T(0);  // a 0 in range makes the AND 0
        return i0 <= i1 ? inner.andGtX(i0, i1, x) : ~T(0);
    }

    // O(log^2 N) -- AND of the values >= x in a[l..r]; -1 (every bit) if there are none; needs lo <= l <= r <= hi, else
    // throws out_of_range
    T andGteX(long long l, long long r, T x) const {
        if (l < lo || l > r || r > hi) throw out_of_range("andGteX: needs lo <= l <= r <= hi");
        auto [i0, i1, zeros] = span(l, r);
        if (zeros && x <= T(0)) return T(0);  // a 0 in range makes the AND 0
        return i0 <= i1 ? inner.andGteX(i0, i1, x) : ~T(0);
    }

    // O(log^2 N) -- AND of the a[i] with lowVal <= a[i] <= highVal in a[l..r]; -1 (every bit) if there are none; needs
    // lo <= l <= r <= hi, else throws out_of_range
    T andInValRange(long long l, long long r, T lowVal, T highVal) const {
        if (l < lo || l > r || r > hi) throw out_of_range("andInValRange: needs lo <= l <= r <= hi");
        auto [i0, i1, zeros] = span(l, r);
        if (zeros && lowVal <= T(0) && T(0) <= highVal) return T(0);  // a 0 in range makes the AND 0
        return i0 <= i1 ? inner.andInValRange(i0, i1, lowVal, highVal) : ~T(0);
    }

    // the k-th smallest of a[l..r], 1 <= k <= r - l + 1
    T kth(long long l, long long r, long long k) const {
        auto [i0, i1, zeros] = span(l, r);
        long long neg = i0 <= i1 ? inner.countLtX(i0, i1, T(0)) : 0;
        if (k <= neg) return inner.kthSmallest(i0, i1, int(k));
        if (k <= neg + zeros) return T(0);
        return inner.kthSmallest(i0, i1, int(k - zeros));
    }
};
