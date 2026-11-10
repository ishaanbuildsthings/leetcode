// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/persistent-order-stats/sparse.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: countGtX countGteX countInValRange countLtX countLteX countOccurrences kthSmallest largestLtX largestLteX pointGet rangeMax rangeMin smallestGtX smallestGteX
// @data-structure-type: persistent
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
//   pointGet: log(N)
//   rangeMax: log(N)
//   rangeMin: log(N)
//   smallestGtX: log(N)
//   smallestGteX: log(N)
//   build: N*log(N)
// @memory:
//   layout: sparse
//   node: L[1*N*log(N)] R[1*N*log(N)] C[1*N*log(N)]
//   tags: none
//   other: idx[1*N] vals[1*N] root[1*N] arr[1*N] srt[1*N]
//   note: built from N given values (index, value pairs) over any index range [lo, hi], every other index 0; costs are in N; persistent seg tree over the compressed values: about N log N nodes; L/R are child pointers, C counts; the tree is over the given values only, and the zeros of [l, r] are added in closed form (they sit between the negatives and the positives)

// Static array. Persistent seg tree over the values' compressed ranks: version p holds a[0..p-1], so a[l..r] is
// version r + 1 minus version l, and every query walks down those two versions together. Costs are log of the number
// of distinct values, never of the value range; query arguments (x, lowVal, ...) can be anything. 0-indexed, inclusive.
// T: int, long long, ....
template <typename T>
struct PersistentOrderStats {
    int n, m;
    long long klo, khi;            // the tree is over ranks 0..m-1
    vector<T> arr, srt;            // srt: sorted distinct values
    vector<int> root;     // node 0 = the empty tree
    struct Node {  // a node's fields side by side: a walk reads them together (faster than one array per field)
        int L = 0;
        int R = 0;
        int C = 0;
    };
    vector<Node> nd;  // node 0 = the empty tree

    // O(N log N) -- arr: the initial array, 0-indexed
    explicit PersistentOrderStats(const vector<T>& a) : n((int)a.size()), arr(a), srt(a), root(1, 0), nd(1) {
        sort(srt.begin(), srt.end());
        srt.erase(unique(srt.begin(), srt.end()), srt.end());
        m = (int)srt.size();
        klo = 0, khi = max(m - 1, 0);
        for (const T& v : a) root.push_back(ins(root.back(), lb(v), v));
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

    int lb(const T& v) const { return int(lower_bound(srt.begin(), srt.end(), v) - srt.begin()); }
    int ub(const T& v) const { return int(upper_bound(srt.begin(), srt.end(), v) - srt.begin()); }

    // ---- internals ----

    // copy of version node with one more value (key = its compressed rank)
    int ins(int node, long long key, T v) {
        vector<pair<int, bool>> path;
        long long nl = klo, nh = khi;
        while (nl != nh) {
            long long mid = nl + (nh - nl) / 2;
            if (key <= mid) path.push_back({node, true}), node = nd[node].L, nh = mid;
            else path.push_back({node, false}), node = nd[node].R, nl = mid + 1;
        }
        Node n;
        n.L = 0, n.R = 0, n.C = nd[node].C + 1;
        nd.push_back(n);
        int cur = (int)nd.size() - 1;
        for (int k = (int)path.size() - 1; k >= 0; k--) {
            auto [old, left] = path[k];
            int lc = left ? cur : nd[old].L, rc = left ? nd[old].R : cur;
            Node n;
            n.L = lc, n.R = rc, n.C = nd[lc].C + nd[rc].C;
            nd.push_back(n);
            cur = (int)nd.size() - 1;
        }
        return cur;
    }

    // the k-th smallest of a[l..r], 1 <= k <= r - l + 1: walk version r + 1 minus version l
    T kth(long long l, long long r, long long k) const {
        int a = root[r + 1], b = root[l];
        long long nl = klo, nh = khi;
        while (nl != nh) {
            long long mid = nl + (nh - nl) / 2, c = nd[nd[a].L].C - nd[nd[b].L].C;
            if (k <= c) a = nd[a].L, b = nd[b].L, nh = mid;
            else k -= c, a = nd[a].R, b = nd[b].R, nl = mid + 1;
        }
        return srt[nl];
    }

    // # of i in [l, r] whose compressed rank is < x
    long long countBelow(long long l, long long r, long long x) const {
        if (x <= klo) return 0;
        if (x > khi) return r - l + 1;
        int a = root[r + 1], b = root[l];
        long long nl = klo, nh = khi, res = 0;
        while (nl != nh) {
            long long mid = nl + (nh - nl) / 2;
            if (x <= mid) a = nd[a].L, b = nd[b].L, nh = mid;
            // the whole left half is below x
            else res += nd[nd[a].L].C - nd[nd[b].L].C, a = nd[a].R, b = nd[b].R, nl = mid + 1;
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
template <typename T>
struct SparsePersistentOrderStats {
    long long lo, hi;
    vector<long long> idx;
    vector<T> vals;
    PersistentOrderStats<T> inner;

    // O(N log N) -- [lo, hi] all 0 except the given values: (index, value) pairs with distinct indices; N = len(values)
    SparsePersistentOrderStats(long long lo, long long hi, vector<pair<long long, T>> values) : lo(lo), hi(hi),
        inner(split(values)) {}

    vector<T> split(vector<pair<long long, T>>& pts) {
        sort(pts.begin(), pts.end());
        for (auto& [i, v] : pts) idx.push_back(i), vals.push_back(v);
        // (a dummy element when there are no given values; never queried)
        return vals.empty() ? vector<T>{T(0)} : vals;
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
        return (i0 <= i1 ? inner.countInValRange(i0, i1, lowVal,
            highVal) : 0) + (lowVal <= T(0) && T(0) <= highVal ? zeros : 0);
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

    // the k-th smallest of a[l..r], 1 <= k <= r - l + 1
    T kth(long long l, long long r, long long k) const {
        auto [i0, i1, zeros] = span(l, r);
        long long neg = i0 <= i1 ? inner.countLtX(i0, i1, T(0)) : 0;
        if (k <= neg) return inner.kthSmallest(i0, i1, int(k));
        if (k <= neg + zeros) return T(0);
        return inner.kthSmallest(i0, i1, int(k - zeros));
    }
};
