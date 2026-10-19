// @operations: leftmostLtX leftmostLteX pointAdd pointAssign pointChmax pointChmin pointGet rangeMin rightmostLtX rightmostLteX
// @data-structure-type: seg-tree
// @complexities:
//   leftmostLtX: log(N)
//   leftmostLteX: log(N)
//   pointAdd: log(N)
//   pointAssign: log(N)
//   pointChmax: log(N)
//   pointChmin: log(N)
//   pointGet: 1
//   rangeMin: log(N)
//   rightmostLtX: log(N)
//   rightmostLteX: log(N)
//   build: N
// @memory:
//   layout: pow2-iterative
//   node: tree[4*N]
//   tags: none
//   other: none
//   note: tree holds each node's min; tree is 2*size where size is the next power of two >= n, so between 2N and 4N slots; arr is a reference

// Point update + rangeMin segment tree, iterative over 2 * size slots (size = next power of two >= n).
// All indices 0-based, ranges inclusive [l, r]. T: int, long long, ...
template <typename T>
struct MinSegTree {
    int n, size;
    vector<T> tree;  // tree[size + i] = a[i]; tree[x] = min of x's children

    // O(N)
    explicit MinSegTree(const vector<T>& a) : n((int)a.size()), size(1) {
        while (size < n) size <<= 1;
        tree.assign(2 * size, numeric_limits<T>::max());
        for (int i = 0; i < n; i++) tree[size + i] = a[i];
        for (int x = size - 1; x > 0; x--) tree[x] = min(tree[2 * x], tree[2 * x + 1]);
    }

    // O(logN) -- min of a[l..r]
    T rangeMin(int l, int r) const {
        T res = numeric_limits<T>::max();
        for (l += size, r += size + 1; l < r; l >>= 1, r >>= 1) {
            if (l & 1) res = min(res, tree[l++]);
            if (r & 1) res = min(res, tree[--r]);
        }
        return res;
    }

    // O(logN) -- a[i] = v
    void pointAssign(int i, T v) {
        int p = size + i;
        tree[p] = v;
        for (p >>= 1; p; p >>= 1) tree[p] = min(tree[2 * p], tree[2 * p + 1]);
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

    // O(logN) -- first i in [l, r] with a[i] <= x, or -1; climbs from l, then descends into the first hit
    int leftmostLteX(int l, int r, T x) const {
        int p = l + size;
        for (;;) {
            while (!(p & 1)) p >>= 1;
            if (tree[p] <= x) {
                while (p < size) {
                    p <<= 1;
                    if (!(tree[p] <= x)) p++;
                }
                return p - size <= r ? p - size : -1;
            }
            p++;
            if (!(p & (p - 1))) return -1;
        }
    }

    // O(logN) -- first i in [l, r] with a[i] < x, or -1; climbs from l, then descends into the first hit
    int leftmostLtX(int l, int r, T x) const {
        int p = l + size;
        for (;;) {
            while (!(p & 1)) p >>= 1;
            if (tree[p] < x) {
                while (p < size) {
                    p <<= 1;
                    if (!(tree[p] < x)) p++;
                }
                return p - size <= r ? p - size : -1;
            }
            p++;
            if (!(p & (p - 1))) return -1;
        }
    }

    // O(logN) -- last i in [l, r] with a[i] <= x, or -1; climbs from r, then descends into the last hit
    int rightmostLteX(int l, int r, T x) const {
        int p = r + size + 1;
        for (;;) {
            p--;
            while (p > 1 && (p & 1)) p >>= 1;
            if (tree[p] <= x) {
                while (p < size) {
                    p = 2 * p + 1;
                    if (!(tree[p] <= x)) p--;
                }
                return p - size >= l ? p - size : -1;
            }
            if (!(p & (p - 1))) return -1;
        }
    }

    // O(logN) -- last i in [l, r] with a[i] < x, or -1; climbs from r, then descends into the last hit
    int rightmostLtX(int l, int r, T x) const {
        int p = r + size + 1;
        for (;;) {
            p--;
            while (p > 1 && (p & 1)) p >>= 1;
            if (tree[p] < x) {
                while (p < size) {
                    p = 2 * p + 1;
                    if (!(tree[p] < x)) p--;
                }
                return p - size >= l ? p - size : -1;
            }
            if (!(p & (p - 1))) return -1;
        }
    }
};
