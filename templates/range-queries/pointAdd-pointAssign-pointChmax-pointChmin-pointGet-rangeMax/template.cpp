// @operations: pointAdd pointAssign pointChmax pointChmin pointGet rangeMax
// @data-structure-type: seg-tree
// @complexities:
//   pointAdd: log(N)
//   pointAssign: log(N)
//   pointChmax: log(N)
//   pointChmin: log(N)
//   pointGet: 1
//   rangeMax: log(N)
//   build: N
// @memory:
//   layout: 2n-iterative
//   node: tree[2*N]
//   tags: none
//   other: none
//   note: tree holds each node's max; leaves are tree[n..2n), no power-of-two padding; arr is a reference
// @original-file-url: https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/segment-trees/normal/pointAssignRangeMax.cpp

// Point update + rangeMax segment tree, iterative over 2N slots (leaves at tree[n..2n)).
// All indices 0-based, ranges inclusive [l, r]. T: int, long long, ...
template <typename T>
struct MaxSegTree {
    int n, size;
    vector<T> tree;  // tree[size + i] = a[i]; tree[x] = max of x's children

    // O(N)
    explicit MaxSegTree(const vector<T>& a) : n((int)a.size()), size(n) {
        tree.assign(2 * size, numeric_limits<T>::lowest());
        for (int i = 0; i < n; i++) tree[size + i] = a[i];
        for (int x = size - 1; x > 0; x--) tree[x] = max(tree[2 * x], tree[2 * x + 1]);
    }

    // O(logN) -- max of a[l..r]
    T rangeMax(int l, int r) const {
        T res = numeric_limits<T>::lowest();
        for (l += size, r += size + 1; l < r; l >>= 1, r >>= 1) {
            if (l & 1) res = max(res, tree[l++]);
            if (r & 1) res = max(res, tree[--r]);
        }
        return res;
    }

    // O(logN) -- a[i] = v
    void pointAssign(int i, T v) {
        int p = size + i;
        tree[p] = v;
        for (p >>= 1; p; p >>= 1) {
            T v = max(tree[2 * p], tree[2 * p + 1]);
            if (tree[p] == v) break;
            tree[p] = v;
        }
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

    // O(logN) -- a[i] += delta
    void pointAdd(int i, T delta) { pointAssign(i, tree[size + i] + delta); }
};
