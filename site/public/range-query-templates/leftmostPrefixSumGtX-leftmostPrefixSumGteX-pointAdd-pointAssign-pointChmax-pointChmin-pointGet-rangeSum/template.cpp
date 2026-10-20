// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/leftmostPrefixSumGtX-leftmostPrefixSumGteX-pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeSum/template.cpp
// @operations: leftmostPrefixSumGtX leftmostPrefixSumGteX pointAdd pointAssign pointChmax pointChmin pointGet rangeSum
// @data-structure-type: BIT
// @complexities:
//   leftmostPrefixSumGtX: log(N)
//   leftmostPrefixSumGteX: log(N)
//   pointAdd: log(N)
//   pointAssign: log(N)
//   pointChmax: log(N)
//   pointChmin: log(N)
//   pointGet: log(N)
//   rangeSum: log(N)
//   build: N
// @memory:
//   layout: none
//   node: tree[1*N]
//   tags: none
//   other: none
//   note: the prefix-sum searches binary-lift over the tree, so they need every a[i] >= 0

// Point add, range sum (Fenwick tree). All indices 0-based, ranges inclusive [l, r]. T: int, long long, ...
template <typename T>
struct BIT {
    int n;
    vector<T> tree;  // 1-indexed

    // O(N) -- push each node into its parent once
    explicit BIT(const vector<T>& a) : n((int)a.size()), tree(n + 1) {
        for (int i = 1; i <= n; i++) tree[i] = a[i - 1];
        for (int i = 1; i <= n; i++) {
            int j = i + (i & -i);
            if (j <= n) tree[j] += tree[i];
        }
    }

    // O(logN) -- a[i] += delta
    void pointAdd(int i, T delta) {
        for (i++; i <= n; i += i & -i) tree[i] += delta;
    }

    // O(logN) -- a[0] + ... + a[i]
    T prefixSum(int i) const {
        T s = 0;
        for (i++; i > 0; i &= i - 1) s += tree[i];
        return s;
    }

    // O(logN) -- a[l] + ... + a[r]
    T rangeSum(int l, int r) const { return l > r ? T(0) : prefixSum(r) - (l ? prefixSum(l - 1) : T(0)); }

    // O(logN) -- a[i] in one walk instead of two prefix sums
    T pointGet(int i) const {
        i++;
        T v = tree[i];
        int stop = i - (i & -i);
        for (i--; i > stop; i &= i - 1) v -= tree[i];
        return v;
    }

    // O(logN) -- a[i] = v
    void pointAssign(int i, T v) { pointAdd(i, v - pointGet(i)); }

    // O(logN) -- a[i] = max(a[i], v)
    void pointChmax(int i, T v) {
        T cur = pointGet(i);
        if (v > cur) pointAdd(i, v - cur);
    }

    // O(logN) -- a[i] = min(a[i], v)
    void pointChmin(int i, T v) {
        T cur = pointGet(i);
        if (v < cur) pointAdd(i, v - cur);
    }

    // O(logN) -- smallest i with a[0] + ... + a[i] >= target (> target if strict), or n if none.
    // Binary lifting: grow pos by powers of two while the prefix stays below target. Needs every a[i] >= 0.
    int prefixLowerBound(T target, bool strict) const {
        int pos = 0;
        T acc = 0;
        for (int step = n ? 1 << (31 - __builtin_clz(n)) : 0; step; step >>= 1) {
            int nxt = pos + step;
            if (nxt <= n) {
                T v = acc + tree[nxt];
                if (v < target || (strict && v == target)) pos = nxt, acc = v;
            }
        }
        return pos;
    }

    // O(logN) -- first i in [l, r] with a[l] + ... + a[i] >= x, or -1. Needs every a[i] >= 0.
    // e.g. on a 0/1 array, leftmostPrefixSumGteX(0, n - 1, k) is the index of the k-th one.
    int leftmostPrefixSumGteX(int l, int r, T x) const {
        int i = max(l, prefixLowerBound((l ? prefixSum(l - 1) : T(0)) + x, false));
        return i <= r ? i : -1;
    }

    // O(logN) -- first i in [l, r] with a[l] + ... + a[i] > x, or -1. Needs every a[i] >= 0.
    int leftmostPrefixSumGtX(int l, int r, T x) const {
        int i = max(l, prefixLowerBound((l ? prefixSum(l - 1) : T(0)) + x, true));
        return i <= r ? i : -1;
    }
};
