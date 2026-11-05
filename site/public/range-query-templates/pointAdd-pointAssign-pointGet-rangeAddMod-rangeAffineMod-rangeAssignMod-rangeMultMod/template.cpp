// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/pointAdd-pointAssign-pointGet-rangeAddMod-rangeAffineMod-rangeAssignMod-rangeMultMod/template.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: getAll pointAdd pointAssign pointGet rangeAddMod rangeAffineMod rangeAssignMod rangeMultMod
// @data-structure-type: lazy-seg-tree
// @complexities:
//   getAll: N
//   pointAdd: log(N)
//   pointAssign: log(N)
//   pointGet: log(N)
//   rangeAddMod: log(N)
//   rangeAffineMod: log(N)
//   rangeAssignMod: log(N)
//   rangeMultMod: log(N)
//   build: N
// @memory:
//   layout: 2n-iterative
//   node: val[1*N]
//   tags: M[1*N] K[1*N]
//   other: none
//   note: each internal node holds one pending affine map x -> x * M + K (% MOD); val holds the leaf values

// Range add / assign / multiply / affine % MOD + point ops, no range aggregates. All indices 0-based, ranges
// inclusive. Every update is an affine map (m, k): x -> m * x + k (% MOD):
//   add v -> (1, v)    mult m -> (m, 0)    assign v -> (0, v)    affine (m, b) -> (m, b)
// Affine maps compose but not commutatively, so the paths to l and r are pushed before tagging.
// Values are kept in [0, mod); T: int, long long, ...
template <typename T>
struct AffineTree {
    using W = conditional_t<sizeof(T) <= 4, long long, __int128>;  // wide enough for a product of two residues
    int n;
    T mod;
    vector<T> M, K;  // internal nodes 1 .. n-1: pending map x -> x * M + K (% MOD)
    vector<T> val;   // leaf values, in [0, mod)

    T norm(W x) const { x %= mod; return T(x < 0 ? x + mod : x); }

    // O(N)
    explicit AffineTree(const vector<T>& a, T mod = 1000000007) : n((int)a.size()), mod(mod), M(a.size(), 1), K(a.size(), 0), val(a.size()) {
        for (int i = 0; i < n; i++) val[i] = norm(a[i]);
    }

    // apply (m, k) on top of whatever node x already holds
    void apply(int x, T m, T k) {
        if (x >= n) {
            val[x - n] = norm(W(val[x - n]) * m + k);
            return;
        }
        M[x] = norm(W(M[x]) * m);
        K[x] = norm(W(K[x]) * m + k);
    }

    // O(logN) -- push every pending tag on leaf p's root-to-leaf path down to its children
    void push(int p) {
        for (int h = 31 - __builtin_clz(p); h > 0; h--) {
            int x = p >> h;
            
            if (!(M[x] == 1 && K[x] == 0)) {
                apply(2 * x, M[x], K[x]);
                apply(2 * x + 1, M[x], K[x]);
                M[x] = 1, K[x] = 0;
            }
        }
    }
    void update(int l, int r, T m, T k) {
        l += n, r += n;
        push(l), push(r);
        for (r++; l < r; l >>= 1, r >>= 1) {
            if (l & 1) apply(l++, m, k);
            if (r & 1) apply(--r, m, k);
        }
    }

    // O(logN) -- a[i] = a[i] * mult + add (% MOD) for i in [l, r]; needs 0 <= l <= r < n, else throws out_of_range
    void rangeAffineMod(int l, int r, T mult, T add) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeAffineMod: needs 0 <= l <= r < n");
        update(l, r, norm(mult), norm(add));
    }

    // O(logN) -- a[i] = a[i] * m (% MOD) for i in [l, r]; needs 0 <= l <= r < n, else throws out_of_range
    void rangeMultMod(int l, int r, T m) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeMultMod: needs 0 <= l <= r < n");
        update(l, r, norm(m), 0);
    }

    // O(logN) -- a[i] += v (% MOD) for i in [l, r]; needs 0 <= l <= r < n, else throws out_of_range
    void rangeAddMod(int l, int r, T v) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeAddMod: needs 0 <= l <= r < n");
        update(l, r, 1, norm(v));
    }

    // O(logN) -- a[i] = v (% MOD) for i in [l, r]; needs 0 <= l <= r < n, else throws out_of_range
    void rangeAssignMod(int l, int r, T v) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeAssignMod: needs 0 <= l <= r < n");
        update(l, r, 0, norm(v));
    }

    // O(logN) -- a[i], in [0, mod): apply ancestors' maps bottom-up (deeper tags are older); needs 0 <= i < n, else
    // throws out_of_range
    T pointGet(int i) const {
        if (i < 0 || i >= n) throw out_of_range("pointGet: needs 0 <= i < n");
        T v = val[i];
        for (int p = (i + n) >> 1; p; p >>= 1) v = norm(W(v) * M[p] + K[p]);
        return v;
    }

    // O(N) -- the whole array: push every tag down (a parent's index is below its children's, so in index order
    // each node's tag is complete when it is pushed), then read the leaves
    vector<T> getAll() {
        for (int x = 1; x < n; x++)
            if (!(M[x] == 1 && K[x] == 0)) {
                apply(2 * x, M[x], K[x]), apply(2 * x + 1, M[x], K[x]);
                M[x] = 1, K[x] = 0;
            }
        return val;
    }

    // O(logN) -- a[i] = v; needs 0 <= i < n, else throws out_of_range
    void pointAssign(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointAssign: needs 0 <= i < n");
        push(i + n); val[i] = norm(v);
    }

    // O(logN) -- a[i] += delta; needs 0 <= i < n, else throws out_of_range
    void pointAdd(int i, T delta) {
        if (i < 0 || i >= n) throw out_of_range("pointAdd: needs 0 <= i < n");
        push(i + n); val[i] = norm(W(val[i]) + delta);
    }
};
