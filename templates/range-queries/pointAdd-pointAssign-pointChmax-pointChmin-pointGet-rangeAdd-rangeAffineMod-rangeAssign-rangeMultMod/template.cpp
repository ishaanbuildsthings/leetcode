// @operations: pointAdd pointAssign pointChmax pointChmin pointGet rangeAdd rangeAffineMod rangeAssign rangeMultMod
// @data-structure-type: lazy-seg-tree
// @complexities:
//   pointAdd: log(N)
//   pointAssign: log(N)
//   pointChmax: log(N)
//   pointChmin: log(N)
//   pointGet: log(N)
//   rangeAdd: log(N)
//   rangeAffineMod: log(N)
//   rangeAssign: log(N)
//   rangeMultMod: log(N)
//   build: N
// @memory:
//   layout: 2n-iterative
//   node: none
//   tags: M[1*N] K[1*N]
//   other: val[1*N]
//   note: each internal node holds one pending affine map x -> x * M + K (mod p); val holds the leaf values

// Range add / assign / multiply / affine mod p + point ops, no range aggregates. All indices 0-based, ranges
// inclusive. Every update is an affine map (m, k): x -> m * x + k (mod p):
//   add v -> (1, v)    mult m -> (m, 0)    assign v -> (0, v)    affine (m, b) -> (m, b)
// Affine maps compose but not commutatively, so the paths to l and r are pushed before tagging.
// Values are kept in [0, mod); pointChmax / pointChmin compare those stored residues. T: int, long long, ...
template <typename T>
struct AffineTree {
    using W = conditional_t<sizeof(T) <= 4, long long, __int128>;  // wide enough for a product of two residues
    int n;
    T mod;
    vector<T> M, K;  // internal nodes 1 .. n-1: pending map x -> x * M + K (mod p)
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

    // O(logN) -- a[i] = a[i] * m + b (mod p) for i in [l, r]
    void rangeAffineMod(int l, int r, T m, T b) { update(l, r, norm(m), norm(b)); }

    // O(logN) -- a[i] = a[i] * m (mod p) for i in [l, r]
    void rangeMultMod(int l, int r, T m) { update(l, r, norm(m), 0); }

    // O(logN) -- a[i] += v (mod p) for i in [l, r]
    void rangeAdd(int l, int r, T v) { update(l, r, 1, norm(v)); }

    // O(logN) -- a[i] = v (mod p) for i in [l, r]
    void rangeAssign(int l, int r, T v) { update(l, r, 0, norm(v)); }

    // O(logN) -- a[i], in [0, mod): apply ancestors' maps bottom-up (deeper tags are older)
    T pointGet(int i) const {
        T v = val[i];
        for (int p = (i + n) >> 1; p; p >>= 1) v = norm(W(v) * M[p] + K[p]);
        return v;
    }

    // O(logN) -- a[i] = v
    void pointAssign(int i, T v) { push(i + n); val[i] = norm(v); }

    // O(logN) -- a[i] += delta
    void pointAdd(int i, T delta) { push(i + n); val[i] = norm(W(val[i]) + delta); }

    // O(logN) -- a[i] = max(a[i], v)
    void pointChmax(int i, T v) { push(i + n); if (v > val[i]) val[i] = v; }

    // O(logN) -- a[i] = min(a[i], v)
    void pointChmin(int i, T v) { push(i + n); if (v < val[i]) val[i] = v; }
};
