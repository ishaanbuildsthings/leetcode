// @operations: countValue pointAdd pointAssign pointChmax pointChmin pointGet
// @data-structure-type: seg-tree
// @complexities:
//   countValue: log(N)
//   pointAdd: log(N)
//   pointAssign: log(N)
//   pointChmax: log(N)
//   pointChmin: log(N)
//   pointGet: 1
//   build: N
// @memory:
//   layout: 2n-iterative
//   node: tree[2*N]
//   tags: none
//   other: vals[1*N]
//   note: tree[n + i] is 1 when a[i] equals the value fixed at build, internal nodes sum their children

// Count occurrences of one value (fixed at build time) in a range, with point updates.
// All indices 0-based, ranges inclusive [l, r]. Iterative 2N tree of 0/1 counts. T: int, long long, ...
template <typename T>
struct CountValueTree {
    int n;
    T number;
    vector<T> vals;
    vector<int> tree;  // tree[n + i] = (a[i] == number); internal nodes sum their children

    // O(N)
    CountValueTree(const vector<T>& a, T number) : n((int)a.size()), number(number), vals(a), tree(2 * a.size()) {
        for (int i = 0; i < n; i++) tree[n + i] = a[i] == number;
        for (int x = n - 1; x > 0; x--) tree[x] = tree[2 * x] + tree[2 * x + 1];
    }

    // O(logN) -- how many i in [l, r] have a[i] == number
    int countValue(int l, int r) const {
        int res = 0;
        for (l += n, r += n + 1; l < r; l >>= 1, r >>= 1) {
            if (l & 1) res += tree[l++];
            if (r & 1) res += tree[--r];
        }
        return res;
    }

    // O(logN) -- a[i] = v; only walks up when the 0/1 at the leaf actually flips
    void pointAssign(int i, T v) {
        vals[i] = v;
        int p = i + n, delta = int(v == number) - tree[p];
        if (delta)
            for (; p; p >>= 1) tree[p] += delta;
    }

    // O(1) -- a[i]
    T pointGet(int i) const { return vals[i]; }

    // O(logN) -- a[i] = max(a[i], v)
    void pointChmax(int i, T v) { if (v > vals[i]) pointAssign(i, v); }

    // O(logN) -- a[i] = min(a[i], v)
    void pointChmin(int i, T v) { if (v < vals[i]) pointAssign(i, v); }

    // O(logN) -- a[i] += delta
    void pointAdd(int i, T delta) { pointAssign(i, vals[i] + delta); }
};
