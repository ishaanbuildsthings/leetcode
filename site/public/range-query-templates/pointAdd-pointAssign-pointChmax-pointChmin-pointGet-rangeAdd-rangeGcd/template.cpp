// @operations: pointAdd pointAssign pointChmax pointChmin pointGet rangeAdd rangeGcd
// @data-structure-type: seg-tree
// @complexities:
//   pointAdd: log(N)*log(U)
//   pointAssign: log(N)*log(U)
//   pointChmax: log(N)*log(U)
//   pointChmin: log(N)*log(U)
//   pointGet: log(N)
//   rangeAdd: log(N)*log(U)
//   rangeGcd: log(N)+log(U)
//   build: N
// @memory:
//   layout: 2n-iterative
//   node: seg[2*N]
//   tags: none
//   other: fen[1*N] diff[1*N]
//   note: seg is a gcd tree over adjacent differences; fen (a BIT over the differences) gives point values
// @original-file-url: https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/segment-trees/lazy/rangeAddRangeGcd.cpp

// Range add + range gcd + point ops. All indices 0-based, ranges inclusive [l, r]. T: int, long long, ...
// gcd(a[l], ..., a[r]) == gcd(a[l], a[l+1] - a[l], ..., a[r] - a[r-1]), and a range add only changes two
// adjacent differences. So: a Fenwick tree over the differences gives point values, and a 2N gcd tree over
// |differences| gives the rest. Result is always >= 0, and 0 only if every value in the range is 0.
template <typename T>
struct RangeAddRangeGcd {
    int n;
    vector<T> diff, fen, seg;  // diff[i] = a[i] - a[i-1] (diff[0] = a[0]); fen 1-indexed; seg[n + i] = |diff[i]|, i >= 1

    static T absT(T x) { return x < 0 ? -x : x; }

    // O(N logU)
    explicit RangeAddRangeGcd(const vector<T>& a) : n((int)a.size()), diff(a.size()), fen(a.size() + 1), seg(2 * a.size()) {
        for (int i = 0; i < n; i++) diff[i] = i ? a[i] - a[i - 1] : a[0];
        for (int i = 1; i <= n; i++) fen[i] = diff[i - 1];
        for (int i = 1; i <= n; i++) {
            int j = i + (i & -i);
            if (j <= n) fen[j] += fen[i];
        }
        for (int i = 1; i < n; i++) seg[n + i] = absT(diff[i]);
        for (int p = n - 1; p > 0; p--) seg[p] = std::gcd(seg[2 * p], seg[2 * p + 1]);
    }

    T prefix(int i) const {
        T s = 0;
        for (i++; i > 0; i &= i - 1) s += fen[i];
        return s;
    }

    T segQuery(int l, int r) const {
        T res = 0;
        for (l += n, r += n + 1; l < r; l >>= 1, r >>= 1) {
            if (l & 1) res = std::gcd(res, seg[l++]);
            if (r & 1) res = std::gcd(res, seg[--r]);
        }
        return res;
    }

    void shiftDiff(int i, T x) {
        diff[i] += x;
        for (int j = i + 1; j <= n; j += j & -j) fen[j] += x;
        if (i >= 1) {
            int p = i + n;
            seg[p] = absT(diff[i]);
            for (p >>= 1; p; p >>= 1) seg[p] = std::gcd(seg[2 * p], seg[2 * p + 1]);
        }
    }

    // O(logN logU) -- a[i] += x for i in [l, r]
    void rangeAdd(int l, int r, T x) {
        shiftDiff(l, x);
        if (r + 1 < n) shiftDiff(r + 1, -x);
    }

    // O(logN) -- a[i]
    T pointGet(int i) const { return prefix(i); }

    // O(logN + logU) -- gcd of a[l..r]
    T rangeGcd(int l, int r) const {
        T res = absT(prefix(l));
        if (l < r) res = std::gcd(res, segQuery(l + 1, r));
        return res;
    }

    // O(logN logU) -- a[i] += delta
    void pointAdd(int i, T delta) { rangeAdd(i, i, delta); }

    // O(logN logU) -- a[i] = v
    void pointAssign(int i, T v) { rangeAdd(i, i, v - pointGet(i)); }

    // O(logN logU) -- a[i] = max(a[i], v)
    void pointChmax(int i, T v) {
        T cur = pointGet(i);
        if (v > cur) rangeAdd(i, i, v - cur);
    }

    // O(logN logU) -- a[i] = min(a[i], v)
    void pointChmin(int i, T v) {
        T cur = pointGet(i);
        if (v < cur) rangeAdd(i, i, v - cur);
    }
};
