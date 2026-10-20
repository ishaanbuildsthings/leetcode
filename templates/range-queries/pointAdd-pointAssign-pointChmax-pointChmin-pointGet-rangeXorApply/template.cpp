// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeXorApply/template.cpp
// @operations: pointAdd pointAssign pointChmax pointChmin pointGet rangeXorApply
// @data-structure-type: BIT
// @complexities:
//   pointAdd: log(N)
//   pointAssign: log(N)
//   pointChmax: log(N)
//   pointChmin: log(N)
//   pointGet: log(N)
//   rangeXorApply: log(N)
//   build: N
// @memory:
//   layout: none
//   node: tree[1*N]
//   tags: none
//   other: none
//   note: a Fenwick tree over the xor-difference array; a[i] is the prefix xor of differences up to i

// Range xor, point get: a Fenwick tree over the xor-difference array. 0-based, inclusive. T: integral.
template <typename T>
struct RangeXorBIT {
    int n;
    vector<T> tree;  // 1-indexed, over d[i] = a[i] ^ a[i - 1]

    // O(N)
    explicit RangeXorBIT(const vector<T>& a) : n((int)a.size()), tree(n + 1) {
        T prev = 0;
        for (int i = 1; i <= n; i++) {
            tree[i] ^= a[i - 1] ^ prev;
            prev = a[i - 1];
            int j = i + (i & -i);
            if (j <= n) tree[j] ^= tree[i];
        }
    }

    void apply(int i, T x) {
        for (i++; i <= n; i += i & -i) tree[i] ^= x;
    }

    // O(logN) -- a[i] ^= x for i in [l, r]
    void rangeXorApply(int l, int r, T x) {
        apply(l, x);
        if (r + 1 < n) apply(r + 1, x);
    }

    // O(logN) -- a[i]
    T pointGet(int i) const {
        T s = 0;
        for (i++; i > 0; i &= i - 1) s ^= tree[i];
        return s;
    }

    // O(logN) -- a[i] = v
    void pointAssign(int i, T v) {
        T d = pointGet(i) ^ v;
        if (d) rangeXorApply(i, i, d);
    }

    // O(logN) -- a[i] += delta
    void pointAdd(int i, T delta) { pointAssign(i, pointGet(i) + delta); }

    // O(logN) -- a[i] = max(a[i], v)
    void pointChmax(int i, T v) {
        T cur = pointGet(i);
        if (v > cur) rangeXorApply(i, i, cur ^ v);
    }

    // O(logN) -- a[i] = min(a[i], v)
    void pointChmin(int i, T v) {
        T cur = pointGet(i);
        if (v < cur) rangeXorApply(i, i, cur ^ v);
    }
};
