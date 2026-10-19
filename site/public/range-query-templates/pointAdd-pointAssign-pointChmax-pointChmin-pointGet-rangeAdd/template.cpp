// @operations: pointAdd pointAssign pointChmax pointChmin pointGet rangeAdd
// @data-structure-type: BIT
// @complexities:
//   pointAdd: log(N)
//   pointAssign: log(N)
//   pointChmax: log(N)
//   pointChmin: log(N)
//   pointGet: log(N)
//   rangeAdd: log(N)
//   build: N
// @memory:
//   layout: none
//   node: tree[1*N]
//   tags: none
//   other: none
//   note: a Fenwick tree over the difference array; a[i] is the prefix sum of differences up to i

// Range add, point get: a Fenwick tree over the difference array. 0-based, inclusive. T: int, long long, ...
template <typename T>
struct RangeAddBIT {
    int n;
    vector<T> tree;  // 1-indexed, over d[i] = a[i] - a[i - 1]

    // O(N)
    explicit RangeAddBIT(const vector<T>& a) : n((int)a.size()), tree(n + 1) {
        T prev = 0;
        for (int i = 1; i <= n; i++) {
            tree[i] += a[i - 1] - prev;
            prev = a[i - 1];
            int j = i + (i & -i);
            if (j <= n) tree[j] += tree[i];
        }
    }

    void add(int i, T v) {
        for (i++; i <= n; i += i & -i) tree[i] += v;
    }

    // O(logN) -- a[i] += v for i in [l, r]
    void rangeAdd(int l, int r, T v) {
        add(l, v);
        if (r + 1 < n) add(r + 1, -v);
    }

    // O(logN) -- a[i]
    T pointGet(int i) const {
        T s = 0;
        for (i++; i > 0; i &= i - 1) s += tree[i];
        return s;
    }

    // O(logN) -- a[i] += delta
    void pointAdd(int i, T delta) { rangeAdd(i, i, delta); }

    // O(logN) -- a[i] = v
    void pointAssign(int i, T v) { rangeAdd(i, i, v - pointGet(i)); }

    // O(logN) -- a[i] = max(a[i], v)
    void pointChmax(int i, T v) {
        T cur = pointGet(i);
        if (v > cur) rangeAdd(i, i, v - cur);
    }

    // O(logN) -- a[i] = min(a[i], v)
    void pointChmin(int i, T v) {
        T cur = pointGet(i);
        if (v < cur) rangeAdd(i, i, v - cur);
    }
};
