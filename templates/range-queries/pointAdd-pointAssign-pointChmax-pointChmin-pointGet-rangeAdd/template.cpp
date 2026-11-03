// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAdd/template.cpp
// @operations: getAll pointAdd pointAssign pointChmax pointChmin pointGet rangeAdd
// @data-structure-type: BIT
// @complexities:
//   getAll: N
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

    // O(logN) -- a[i] += v for i in [l, r]; needs 0 <= l <= r < n, else throws out_of_range
    void rangeAdd(int l, int r, T v) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeAdd: needs 0 <= l <= r < n");
        add(l, v);
        if (r + 1 < n) add(r + 1, -v);
    }

    // O(logN) -- a[i]; needs 0 <= i < n, else throws out_of_range
    T pointGet(int i) const {
        if (i < 0 || i >= n) throw out_of_range("pointGet: needs 0 <= i < n");
        T s = 0;
        for (i++; i > 0; i &= i - 1) s += tree[i];
        return s;
    }

    // O(N) -- the whole array: undo the Fenwick sums on a copy (last index first: entry i was added into
    // i + lowbit(i) once complete), then one pass of running prefix sums
    vector<T> getAll() const {
        vector<T> d(tree), out(n);
        for (int i = n; i > 0; i--) {
            int j = i + (i & -i);
            if (j <= n) d[j] -= d[i];
        }
        T s = 0;
        for (int i = 0; i < n; i++) out[i] = s += d[i + 1];
        return out;
    }

    // O(logN) -- a[i] += delta; needs 0 <= i < n, else throws out_of_range
    void pointAdd(int i, T delta) {
        if (i < 0 || i >= n) throw out_of_range("pointAdd: needs 0 <= i < n");
        rangeAdd(i, i, delta);
    }

    // O(logN) -- a[i] = v; needs 0 <= i < n, else throws out_of_range
    void pointAssign(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointAssign: needs 0 <= i < n");
        rangeAdd(i, i, v - pointGet(i));
    }

    // O(logN) -- a[i] = max(a[i], v); needs 0 <= i < n, else throws out_of_range
    void pointChmax(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointChmax: needs 0 <= i < n");
        T cur = pointGet(i);
        if (v > cur) rangeAdd(i, i, v - cur);
    }

    // O(logN) -- a[i] = min(a[i], v); needs 0 <= i < n, else throws out_of_range
    void pointChmin(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointChmin: needs 0 <= i < n");
        T cur = pointGet(i);
        if (v < cur) rangeAdd(i, i, v - cur);
    }
};
