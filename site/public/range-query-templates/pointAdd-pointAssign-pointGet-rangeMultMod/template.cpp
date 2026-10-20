// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/pointAdd-pointAssign-pointGet-rangeMultMod/template.cpp
// @operations: pointAdd pointAssign pointGet rangeMultMod
// @data-structure-type: seg-tree
// @complexities:
//   pointAdd: log(N)
//   pointAssign: log(N)
//   pointGet: log(N)
//   rangeMultMod: log(N)
//   build: N
// @memory:
//   layout: 2n-iterative
//   node: tree[1*N]
//   tags: tree[1*N]
//   other: none
//   note: tree[n:] holds the values, tree[1:n] holds each node's pending rangeMultMod tag (no aggregates); leaves count as node data, internal nodes as tags

// rangeMultMod + point ops with no range aggregates. All indices 0-based, ranges inclusive [l, r].
// rangeMultMod composes with itself in any order, so a range update only tags the O(logN) covering nodes and
// pointGet folds the tags on the leaf-to-root path. Only overwrites (pointAssign etc.) push those tags off
// the path first, so they aren't re-applied to the new value. T: int, long long, ...
template <typename T>
struct RangeMultModTree {
    using W = conditional_t<sizeof(T) <= 4, long long, __int128>;
    int n;
    T mod;
    vector<T> tree;  // tree[n + i] = a[i]; tree[1 .. n-1] = pending tag (identity T(1))

    // O(N)
    explicit RangeMultModTree(const vector<T>& a, T mod = 1000000007) : n((int)a.size()), mod(mod), tree(2 * a.size(), T(1)) {
        for (int i = 0; i < n; i++) tree[n + i] = T((a[i] % mod + mod) % mod);
    }

    // O(logN) -- a[i] = a[i] * m (mod p) for i in [l, r]
    void rangeMultMod(int l, int r, T m) {
        m = T((m % mod + mod) % mod);
        for (l += n, r += n + 1; l < r; l >>= 1, r >>= 1) {
            if (l & 1) { tree[l] = T(W(tree[l]) * m % mod); l++; }
            if (r & 1) { --r; tree[r] = T(W(tree[r]) * m % mod); }
        }
    }

    // O(logN) -- move the tags on leaf p's root-to-leaf path down, so nothing above p is pending
    void push(int p) {
        for (int h = 31 - __builtin_clz(p); h > 0; h--) {
            int x = p >> h;
            T t = tree[x];
            if (t != T(1)) {
                tree[2 * x] = T(W(tree[2 * x]) * t % mod);
                tree[2 * x + 1] = T(W(tree[2 * x + 1]) * t % mod);
                tree[x] = T(1);
            }
        }
    }

    // O(logN) -- a[i], in [0, mod)
    T pointGet(int i) const {
        int p = i + n;
        T a = tree[p];
        for (p >>= 1; p; p >>= 1) a = T(W(a) * tree[p] % mod);
        return a;
    }

    // O(logN) -- a[i] = val
    void pointAssign(int i, T val) {
        val = T((val % mod + mod) % mod);
        int p = i + n;
        push(p);
        tree[p] = val;
    }

    // O(logN) -- a[i] += delta
    void pointAdd(int i, T delta) {
        int p = i + n;
        push(p);
        tree[p] = T(((W(tree[p]) + delta) % mod + mod) % mod);
    }
};
