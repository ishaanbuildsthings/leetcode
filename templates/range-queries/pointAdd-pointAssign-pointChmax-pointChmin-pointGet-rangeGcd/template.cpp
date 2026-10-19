// @operations: pointAdd pointAssign pointChmax pointChmin pointGet rangeGcd
// @data-structure-type: seg-tree
// @complexities:
//   pointAdd: log(N)*log(U) ?
//   pointAssign: log(N)*log(U) ?
//   pointChmax: log(N)*log(U) ?
//   pointChmin: log(N)*log(U) ?
//   pointGet: 1
//   rangeGcd: log(N)+log(U) ?
//   build: N*log(U) ?
// @memory:
//   layout: 2n-iterative
//   node: tree[2*N]
//   tags: none
//   other: none
//   note: tree holds each node's gcd; arr is a reference
// @original-file-url: https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/segment-trees/normal/GcdSegTree.cpp

// Point update + range gcd, iterative 2N segment tree (n leaves, no padding).
// All indices 0-based, ranges inclusive [l, r]. T: int, long long, ...
template <typename T>
struct GcdSegmentTree {
    int n;
    vector<T> tree;  // tree[n + i] = a[i]; tree[x] = gcd of x's children

    // O(N logU)
    explicit GcdSegmentTree(const vector<T>& a) : n((int)a.size()), tree(2 * a.size()) {
        for (int i = 0; i < n; i++) tree[n + i] = a[i];
        for (int x = n - 1; x > 0; x--) tree[x] = std::gcd(tree[2 * x], tree[2 * x + 1]);
    }

    // O(logN logU) -- a[i] = v; stops early once a node's gcd doesn't change
    void pointAssign(int i, T v) {
        int p = i + n;
        tree[p] = v;
        for (p >>= 1; p; p >>= 1) {
            T g = std::gcd(tree[2 * p], tree[2 * p + 1]);
            if (tree[p] == g) break;
            tree[p] = g;
        }
    }

    // O(logN logU) -- same as pointAssign, but also writes v into the array you pass in
    void pointAssignAndMutateArray(vector<T>& arr, int i, T v) {
        arr[i] = v;
        pointAssign(i, v);
    }

    // O(logN + logU) -- gcd of a[l..r]; the gcds telescope, so the whole fold costs one log U
    T rangeGcd(int l, int r) const {
        T res = 0;
        for (l += n, r += n + 1; l < r; l >>= 1, r >>= 1) {
            if (l & 1) res = std::gcd(res, tree[l++]);
            if (r & 1) res = std::gcd(res, tree[--r]);
        }
        return res;
    }

    // O(1) -- a[i]
    T pointGet(int i) const { return tree[n + i]; }

    // O(logN logU) -- a[i] = max(a[i], v)
    void pointChmax(int i, T v) { if (v > tree[n + i]) pointAssign(i, v); }

    // O(logN logU) -- a[i] = min(a[i], v)
    void pointChmin(int i, T v) { if (v < tree[n + i]) pointAssign(i, v); }

    // O(logN logU) -- a[i] += delta
    void pointAdd(int i, T delta) { pointAssign(i, tree[n + i] + delta); }
};
