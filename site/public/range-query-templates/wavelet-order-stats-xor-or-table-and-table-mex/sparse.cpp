// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/wavelet-order-stats-xor-or-table-and-table-mex/sparse.cpp
// @operations: andGtX andGteX andInValRange andLtX andLteX countGtX countGteX countInValRange countLtX countLteX countOccurrences kthLargest kthSmallest largestLtX largestLteX medianHigh medianLow orGtX orGteX orInValRange orLtX orLteX pointGet rangeMax rangeMex rangeMin smallestGtX smallestGteX xorGtX xorGteX xorInValRange xorLtX xorLteX
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
//   kthLargest: log(N)
//   kthSmallest: log(N)
//   largestLtX: log(N)
//   largestLteX: log(N)
//   medianHigh: log(N)
//   medianLow: log(N)
//   orGtX: log(N)
//   orGteX: log(N)
//   orInValRange: log(N)
//   orLtX: log(N)
//   orLteX: log(N)
//   pointGet: log(N)
//   rangeMax: log(N)
//   rangeMex: log(N)
//   rangeMin: log(N)
//   smallestGtX: log(N)
//   smallestGteX: log(N)
//   xorGtX: log(N)
//   xorGteX: log(N)
//   xorInValRange: log(N)
//   xorLtX: log(N)
//   xorLteX: log(N)
//   build: N*log^2(N)
// @memory:
//   layout: sparse
//   node: idx[1*N] vals[1*N] zeros[1*N*log(N)] arr[1*N] srt[1*N] mexRoot[1*N] ML[1*N*log(N)] MR[1*N*log(N)] MN[1*N*log(N)] xt[1*N*log(N)] ot[1*N*log^2(N)] at[1*N*log^2(N)]
//   tags: none
//   other: none
//   note: built from N given values (index, value pairs) over any index range [lo, hi], every other index 0; costs are in N; wavelet matrix: one row of N + 1 prefix counts per bit of the compressed value; rangeMex uses a persistent seg tree over the values 0..N+1 holding each value's last index; xor by value: per level, prefix xors of its order; OR by value: per level, a sparse table over its order (O(1) a window); AND by value: per level, a sparse table over its order (O(1) a window); the structure is over the given values only, and the zeros of [l, r] are added in closed form (they sit between the negatives and the positives)

// Static array. Each query treats a[l..r] (0-indexed, inclusive) as a sorted multiset. Values are compressed to ranks
// 0..m-1 once, so costs are log of the number of distinct values, never of the value range; query arguments (x,
// lowVal, ...) can be anything. Level d of the wavelet matrix (top bit first) stably splits the current order into the
// ranks with that bit 0, then 1; zeros[d][i] = # of the first i elements of level d's order with the bit 0.
// rangeMex: a persistent seg tree over the values 0..N+1; version p holds, per value, its last index before p (-1 if
// none). The mex of a[l..r] is the first value whose last index in version r + 1 is < l.
// T: int, long long, ....
template <typename T>
struct WaveletMatrix {
    int n, m, bits;
    vector<T> arr, srt;  // srt: sorted distinct values
    vector<int> zeros;   // level lv's row is zeros[lv * (n + 1) .. lv * (n + 1) + n]
    vector<int> mexRoot, ML, MR, MN;  // the persistent mex tree
    vector<vector<T>> xt;  // per level, xor over its order
    vector<vector<vector<T>>> ot;  // per level, OR over its order
    vector<vector<vector<T>>> at;  // per level, AND over its order

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
        buildMex();
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

    // O(logN) -- smallest integer >= 0 that is not in a[l..r]
    int rangeMex(int l, int r) const { return mexFrom(l, r, 0); }

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

    // O(logN) -- OR of the values < x in a[l..r]; 0 if there are none
    T orLtX(int l, int r, T x) const {
        return orRanks(l, r, 0, lb(x));
    }

    // O(logN) -- OR of the values <= x in a[l..r]; 0 if there are none
    T orLteX(int l, int r, T x) const {
        return orRanks(l, r, 0, ub(x));
    }

    // O(logN) -- OR of the values > x in a[l..r]; 0 if there are none
    T orGtX(int l, int r, T x) const {
        return orRanks(l, r, ub(x), m);
    }

    // O(logN) -- OR of the values >= x in a[l..r]; 0 if there are none
    T orGteX(int l, int r, T x) const {
        return orRanks(l, r, lb(x), m);
    }

    // O(logN) -- OR of the a[i] with lowVal <= a[i] <= highVal in a[l..r]; 0 if there are none
    T orInValRange(int l, int r, T lowVal, T highVal) const {
        if (highVal < lowVal) return T(0);
        return orRanks(l, r, lb(lowVal), ub(highVal));
    }

    // O(logN) -- AND of the values < x in a[l..r]; -1 (every bit) if there are none
    T andLtX(int l, int r, T x) const {
        return andRanks(l, r, 0, lb(x));
    }

    // O(logN) -- AND of the values <= x in a[l..r]; -1 (every bit) if there are none
    T andLteX(int l, int r, T x) const {
        return andRanks(l, r, 0, ub(x));
    }

    // O(logN) -- AND of the values > x in a[l..r]; -1 (every bit) if there are none
    T andGtX(int l, int r, T x) const {
        return andRanks(l, r, ub(x), m);
    }

    // O(logN) -- AND of the values >= x in a[l..r]; -1 (every bit) if there are none
    T andGteX(int l, int r, T x) const {
        return andRanks(l, r, lb(x), m);
    }

    // O(logN) -- AND of the a[i] with lowVal <= a[i] <= highVal in a[l..r]; -1 (every bit) if there are none
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

    // persistent seg tree over the values 0..n+1: version p holds, per value, its last index before p (-1: none)
    void buildMex() {
        ML.assign(1, 0), MR.assign(1, 0), MN.assign(1, -1);  // node 0 = the empty tree (every last index -1)
        mexRoot.assign(n + 1, 0);
        for (int i = 0; i < n; i++)
            mexRoot[i + 1] = T(0) <= arr[i] && arr[i] <= T(n + 1) ? mexSet(mexRoot[i], 0, n + 1, int(arr[i]), i) : mexRoot[i];
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

    void orBuild(int lv, const vector<T>& vals) {  // sparse table: row j = OR of every window of 2^j
        auto& rows = ot[lv];
        rows.assign(1, vals);
        for (int h = 1; 2 * h <= n; h *= 2) {
            const vector<T>& p = rows.back();
            vector<T> q(p.size() - h);
            for (size_t i = 0; i < q.size(); i++) q[i] = p[i] | p[i + h];
            rows.push_back(move(q));
        }
    }
    T orQ(int lv, int lo, int hi) const {  // lo < hi
        int j = 31 - __builtin_clz(hi - lo);
        return ot[lv][j][lo] | ot[lv][j][hi - (1 << j)];
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

    // O(logN) -- a[i]
    T pointGet(long long i) const {
        auto it = lower_bound(idx.begin(), idx.end(), i);
        return it != idx.end() && *it == i ? vals[it - idx.begin()] : T(0);
    }

    // O(logN) -- # of i in [l, r] with a[i] == x
    long long countOccurrences(long long l, long long r, T x) const {
        auto [i0, i1, zeros] = span(l, r);
        return (i0 <= i1 ? inner.countOccurrences(i0, i1, x) : 0) + (x == T(0) ? zeros : 0);
    }

    // O(logN) -- # of i in [l, r] with lowVal <= a[i] <= highVal
    long long countInValRange(long long l, long long r, T lowVal, T highVal) const {
        auto [i0, i1, zeros] = span(l, r);
        return (i0 <= i1 ? inner.countInValRange(i0, i1, lowVal, highVal) : 0) + (lowVal <= T(0) && T(0) <= highVal ? zeros : 0);
    }

    // O(logN) -- # of values < x in a[l..r]
    long long countLtX(long long l, long long r, T x) const {
        auto [i0, i1, zeros] = span(l, r);
        return (i0 <= i1 ? inner.countLtX(i0, i1, x) : 0) + (T(0) < x ? zeros : 0);
    }

    // O(logN) -- # of values <= x in a[l..r]
    long long countLteX(long long l, long long r, T x) const {
        auto [i0, i1, zeros] = span(l, r);
        return (i0 <= i1 ? inner.countLteX(i0, i1, x) : 0) + (T(0) <= x ? zeros : 0);
    }

    // O(logN) -- # of values > x in a[l..r]
    long long countGtX(long long l, long long r, T x) const {
        auto [i0, i1, zeros] = span(l, r);
        return (i0 <= i1 ? inner.countGtX(i0, i1, x) : 0) + (x < T(0) ? zeros : 0);
    }

    // O(logN) -- # of values >= x in a[l..r]
    long long countGteX(long long l, long long r, T x) const {
        auto [i0, i1, zeros] = span(l, r);
        return (i0 <= i1 ? inner.countGteX(i0, i1, x) : 0) + (x <= T(0) ? zeros : 0);
    }

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
        auto [i0, i1, zeros] = span(l, r);
        optional<T> a = i0 <= i1 ? inner.smallestGteX(i0, i1, x) : nullopt;
        if (zeros && x <= T(0)) a = a ? min(*a, T(0)) : T(0);
        return a;
    }

    // O(logN) -- smallest value > x in a[l..r], or nullopt
    optional<T> smallestGtX(long long l, long long r, T x) const {
        auto [i0, i1, zeros] = span(l, r);
        optional<T> a = i0 <= i1 ? inner.smallestGtX(i0, i1, x) : nullopt;
        if (zeros && x < T(0)) a = a ? min(*a, T(0)) : T(0);
        return a;
    }

    // O(logN) -- largest value <= x in a[l..r], or nullopt
    optional<T> largestLteX(long long l, long long r, T x) const {
        auto [i0, i1, zeros] = span(l, r);
        optional<T> a = i0 <= i1 ? inner.largestLteX(i0, i1, x) : nullopt;
        if (zeros && T(0) <= x) a = a ? max(*a, T(0)) : T(0);
        return a;
    }

    // O(logN) -- largest value < x in a[l..r], or nullopt
    optional<T> largestLtX(long long l, long long r, T x) const {
        auto [i0, i1, zeros] = span(l, r);
        optional<T> a = i0 <= i1 ? inner.largestLtX(i0, i1, x) : nullopt;
        if (zeros && T(0) < x) a = a ? max(*a, T(0)) : T(0);
        return a;
    }

    // O(logN) -- smallest integer >= 0 that is not in a[l..r]
    long long rangeMex(long long l, long long r) const {
        auto [i0, i1, zeros] = span(l, r);
        if (i0 > i1) return 1;  // all zeros
        return zeros ? inner.mexFrom(i0, i1, 1) : inner.rangeMex(i0, i1);
    }

    // O(logN) -- xor of the values < x in a[l..r] (copies count); 0 if there are none (the zeros add nothing)
    T xorLtX(long long l, long long r, T x) const {
        auto [i0, i1, zeros] = span(l, r);
        return i0 <= i1 ? inner.xorLtX(i0, i1, x) : T(0);
    }

    // O(logN) -- xor of the values <= x in a[l..r] (copies count); 0 if there are none (the zeros add nothing)
    T xorLteX(long long l, long long r, T x) const {
        auto [i0, i1, zeros] = span(l, r);
        return i0 <= i1 ? inner.xorLteX(i0, i1, x) : T(0);
    }

    // O(logN) -- xor of the values > x in a[l..r] (copies count); 0 if there are none (the zeros add nothing)
    T xorGtX(long long l, long long r, T x) const {
        auto [i0, i1, zeros] = span(l, r);
        return i0 <= i1 ? inner.xorGtX(i0, i1, x) : T(0);
    }

    // O(logN) -- xor of the values >= x in a[l..r] (copies count); 0 if there are none (the zeros add nothing)
    T xorGteX(long long l, long long r, T x) const {
        auto [i0, i1, zeros] = span(l, r);
        return i0 <= i1 ? inner.xorGteX(i0, i1, x) : T(0);
    }

    // O(logN) -- xor of the a[i] with lowVal <= a[i] <= highVal in a[l..r] (copies count); 0 if there are none (the zeros add nothing)
    T xorInValRange(long long l, long long r, T lowVal, T highVal) const {
        auto [i0, i1, zeros] = span(l, r);
        return i0 <= i1 ? inner.xorInValRange(i0, i1, lowVal, highVal) : T(0);
    }

    // O(logN) -- OR of the values < x in a[l..r]; 0 if there are none (the zeros add nothing)
    T orLtX(long long l, long long r, T x) const {
        auto [i0, i1, zeros] = span(l, r);
        return i0 <= i1 ? inner.orLtX(i0, i1, x) : T(0);
    }

    // O(logN) -- OR of the values <= x in a[l..r]; 0 if there are none (the zeros add nothing)
    T orLteX(long long l, long long r, T x) const {
        auto [i0, i1, zeros] = span(l, r);
        return i0 <= i1 ? inner.orLteX(i0, i1, x) : T(0);
    }

    // O(logN) -- OR of the values > x in a[l..r]; 0 if there are none (the zeros add nothing)
    T orGtX(long long l, long long r, T x) const {
        auto [i0, i1, zeros] = span(l, r);
        return i0 <= i1 ? inner.orGtX(i0, i1, x) : T(0);
    }

    // O(logN) -- OR of the values >= x in a[l..r]; 0 if there are none (the zeros add nothing)
    T orGteX(long long l, long long r, T x) const {
        auto [i0, i1, zeros] = span(l, r);
        return i0 <= i1 ? inner.orGteX(i0, i1, x) : T(0);
    }

    // O(logN) -- OR of the a[i] with lowVal <= a[i] <= highVal in a[l..r]; 0 if there are none (the zeros add nothing)
    T orInValRange(long long l, long long r, T lowVal, T highVal) const {
        auto [i0, i1, zeros] = span(l, r);
        return i0 <= i1 ? inner.orInValRange(i0, i1, lowVal, highVal) : T(0);
    }

    // O(logN) -- AND of the values < x in a[l..r]; -1 (every bit) if there are none
    T andLtX(long long l, long long r, T x) const {
        auto [i0, i1, zeros] = span(l, r);
        if (zeros && T(0) < x) return T(0);  // a 0 in range makes the AND 0
        return i0 <= i1 ? inner.andLtX(i0, i1, x) : ~T(0);
    }

    // O(logN) -- AND of the values <= x in a[l..r]; -1 (every bit) if there are none
    T andLteX(long long l, long long r, T x) const {
        auto [i0, i1, zeros] = span(l, r);
        if (zeros && T(0) <= x) return T(0);  // a 0 in range makes the AND 0
        return i0 <= i1 ? inner.andLteX(i0, i1, x) : ~T(0);
    }

    // O(logN) -- AND of the values > x in a[l..r]; -1 (every bit) if there are none
    T andGtX(long long l, long long r, T x) const {
        auto [i0, i1, zeros] = span(l, r);
        if (zeros && x < T(0)) return T(0);  // a 0 in range makes the AND 0
        return i0 <= i1 ? inner.andGtX(i0, i1, x) : ~T(0);
    }

    // O(logN) -- AND of the values >= x in a[l..r]; -1 (every bit) if there are none
    T andGteX(long long l, long long r, T x) const {
        auto [i0, i1, zeros] = span(l, r);
        if (zeros && x <= T(0)) return T(0);  // a 0 in range makes the AND 0
        return i0 <= i1 ? inner.andGteX(i0, i1, x) : ~T(0);
    }

    // O(logN) -- AND of the a[i] with lowVal <= a[i] <= highVal in a[l..r]; -1 (every bit) if there are none
    T andInValRange(long long l, long long r, T lowVal, T highVal) const {
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
