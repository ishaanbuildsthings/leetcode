// @operations: pointAdd pointAssign pointChmax pointChmin pointGet rangeChmax
// @data-structure-type: seg-tree
// @complexities:
//   pointAdd: log(N)
//   pointAssign: log(N)
//   pointChmax: 1
//   pointChmin: log(N)
//   pointGet: log(N)
//   rangeChmax: log(N)
//   build: N
// @memory:
//   layout: 2n-iterative
//   node: tree[1*N]
//   tags: tree[1*N]
//   other: none
//   note: tree[n:] holds the values, tree[1:n] holds each node's pending rangeChmax tag (no aggregates); leaves count as node data, internal nodes as tags

// rangeChmax + point ops with no range aggregates. All indices 0-based, ranges inclusive [l, r].
// rangeChmax composes with itself in any order, so a range update only tags the O(logN) covering nodes and
// pointGet folds the tags on the leaf-to-root path. Only overwrites (pointAssign etc.) push those tags off
// the path first, so they aren't re-applied to the new value. T: int, long long, ...
template <typename T>
struct RangeChmaxTree {
    int n;
    vector<T> tree;  // tree[n + i] = a[i]; tree[1 .. n-1] = pending tag (identity numeric_limits<T>::lowest())

    // O(N)
    explicit RangeChmaxTree(const vector<T>& a) : n((int)a.size()), tree(2 * a.size(), numeric_limits<T>::lowest()) {
        for (int i = 0; i < n; i++) tree[n + i] = a[i];
    }

    // O(logN) -- a[i] = max(a[i], v) for i in [l, r]
    void rangeChmax(int l, int r, T v) {
        for (l += n, r += n + 1; l < r; l >>= 1, r >>= 1) {
            if (l & 1) { tree[l] = (tree[l] > v ? tree[l] : v); l++; }
            if (r & 1) { --r; tree[r] = (tree[r] > v ? tree[r] : v); }
        }
    }

    // O(logN) -- move the tags on leaf p's root-to-leaf path down, so nothing above p is pending
    void push(int p) {
        for (int h = 31 - __builtin_clz(p); h > 0; h--) {
            int x = p >> h;
            T t = tree[x];
            if (t != numeric_limits<T>::lowest()) {
                tree[2 * x] = (tree[2 * x] > t ? tree[2 * x] : t);
                tree[2 * x + 1] = (tree[2 * x + 1] > t ? tree[2 * x + 1] : t);
                tree[x] = numeric_limits<T>::lowest();
            }
        }
    }

    // O(logN) -- a[i]
    T pointGet(int i) const {
        int p = i + n;
        T a = tree[p];
        for (p >>= 1; p; p >>= 1) a = (a > tree[p] ? a : tree[p]);
        return a;
    }

    // O(logN) -- a[i] = val
    void pointAssign(int i, T val) {
        int p = i + n;
        push(p);
        tree[p] = val;
    }

    // O(logN) -- a[i] += delta
    void pointAdd(int i, T delta) {
        int p = i + n;
        push(p);
        tree[p] = tree[p] + delta;
    }

    // O(1) -- a[i] = max(a[i], v); a leaf-level chmax tag commutes with the pending ones above it
    void pointChmax(int i, T v) {
        int p = i + n;
        if (v > tree[p]) tree[p] = v;
    }

    // O(logN) -- a[i] = min(a[i], v)
    void pointChmin(int i, T v) {
        int p = i + n;
        push(p);
        if (v < tree[p]) tree[p] = v;
    }
};
