// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeSum__seg-tree/template.cpp
// @operations: pointAdd pointAssign pointChmax pointChmin pointGet rangeSum
// @data-structure-type: seg-tree
// @complexities:
//   pointAdd: log(N)
//   pointAssign: log(N)
//   pointChmax: log(N)
//   pointChmin: log(N)
//   pointGet: 1
//   rangeSum: log(N)
//   build: N
// @memory:
//   layout: 2n-iterative
//   node: tree[2*N]
//   tags: none
//   other: none
//   note: tree holds each node's sum; leaves are tree[n..2n), no power-of-two padding; arr is a reference
// @original-file-url: https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/segment-trees/normal/pointAssignRangeSum.cpp

// Point update + rangeSum segment tree, iterative over 2N slots (leaves at tree[n..2n)).
// All indices 0-based, ranges inclusive [l, r]. T: int, long long, ...
template <typename T>
struct SumSegTree {
    int n, size;
    vector<T> tree;  // tree[size + i] = a[i]; tree[x] = sum of x's children

    // O(N)
    explicit SumSegTree(const vector<T>& a) : n((int)a.size()), size(n) {
        tree.assign(2 * size, T(0));
        for (int i = 0; i < n; i++) tree[size + i] = a[i];
        for (int x = size - 1; x > 0; x--) tree[x] = tree[2 * x] + tree[2 * x + 1];
    }

    // O(logN) -- sum of a[l..r]
    T rangeSum(int l, int r) const {
        T res = T(0);
        for (l += size, r += size + 1; l < r; l >>= 1, r >>= 1) {
            if (l & 1) res = res + tree[l++];
            if (r & 1) res = res + tree[--r];
        }
        return res;
    }

    // O(logN) -- a[i] = v
    void pointAssign(int i, T v) {
        int p = size + i;
        tree[p] = v;
        for (p >>= 1; p; p >>= 1) tree[p] = tree[2 * p] + tree[2 * p + 1];
    }

    // O(logN) -- same as pointAssign, but also writes v into the array you pass in
    void pointAssignAndMutateArray(vector<T>& arr, int i, T v) {
        arr[i] = v;
        pointAssign(i, v);
    }

    // O(1) -- a[i]
    T pointGet(int i) const { return tree[size + i]; }

    // O(logN) -- a[i] = max(a[i], v)
    void pointChmax(int i, T v) { if (v > tree[size + i]) pointAssign(i, v); }

    // O(logN) -- a[i] = min(a[i], v)
    void pointChmin(int i, T v) { if (v < tree[size + i]) pointAssign(i, v); }

    // O(logN) -- a[i] += delta, by walking the delta up instead of recomputing nodes
    void pointAdd(int i, T delta) {
        for (int p = size + i; p; p >>= 1) tree[p] += delta;
    }
};
