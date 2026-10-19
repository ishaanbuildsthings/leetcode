// @operations: pointAddMod pointAssignMod pointGet rangeMultMod rangeSumMod
// @data-structure-type: lazy-seg-tree
// @complexities:
//   pointAddMod: log(N)
//   pointAssignMod: log(N)
//   pointGet: log(N)
//   rangeMultMod: log(N)
//   rangeSumMod: log(N)
//   build: N
// @memory:
//   layout: 2n-iterative
//   node: tot[2*N]
//   tags: mul[1*N]
//   other: none
//   note: tags live on the N internal nodes only; each is a pending multiplier (mod p)

// Range multiply + range sum, all mod p, plus point ops. All indices 0-based, ranges inclusive [l, r].
// One tag per internal node: a pending multiplier ("applied here, not yet pushed"). Multipliers compose by
// multiplying, and v -> v * m turns a node's sum into sum * m. Leaner than the affine tree: one tag instead of two.
// Values are residues in [0, mod). T: int, long long, ...
template <typename T>
struct MultSumTree {
    using W = conditional_t<sizeof(T) <= 4, long long, __int128>;  // wide enough for a product of two residues
    int n, h;
    T mod;
    vector<T> tot;  // 2N: leaves are tot[n..2n)
    vector<T> mul;  // N: tags on internal nodes

    T norm(W x) const { x %= mod; return T(x < 0 ? x + mod : x); }

    // O(N)
    explicit MultSumTree(const vector<T>& a, T mod = 1000000007)
        : n((int)a.size()), h(a.empty() ? 0 : 32 - __builtin_clz((unsigned)a.size())), mod(mod), tot(2 * a.size()) {
        for (int i = 0; i < n; i++) tot[n + i] = norm(a[i]);
        for (int x = n - 1; x > 0; x--) tot[x] = norm(W(tot[2 * x]) + tot[2 * x + 1]);
        mul.assign(n, 1);
    }

    // v -> v * m on node x (k is unused: a product doesn't care how many slots the node covers)
    void apply(int x, int, T m) {
        tot[x] = norm(W(tot[x]) * m);
        if (x < n) mul[x] = norm(W(mul[x]) * m);
    }

    // push every tag on the root-to-leaf path of leaf p down one level
    void push(int p) {
        for (int s = h; s > 0; s--) {
            int x = p >> s, k = 1 << (s - 1);
            if (mul[x] != 1) apply(2 * x, k, mul[x]), apply(2 * x + 1, k, mul[x]), mul[x] = 1;
        }
    }

    // recompute the ancestors of leaf p; each keeps the effect of its own pending tag
    void rebuild(int p) {
        for (int k = 2; p > 1; k <<= 1) {
            p >>= 1;
            tot[p] = norm((W(tot[2 * p]) + tot[2 * p + 1]) * mul[p]);
        }
    }

    void update(int l, int r, T m) {
        if (l > r) return;
        int l0 = l + n, r0 = r + n;
        push(l0), push(r0);
        for (int i = l0, j = r0 + 1, k = 1; i < j; i >>= 1, j >>= 1, k <<= 1) {
            if (i & 1) apply(i++, k, m);
            if (j & 1) apply(--j, k, m);
        }
        rebuild(l0), rebuild(r0);
    }

    // O(logN) -- (a[l] + ... + a[r]) mod p
    T rangeSumMod(int l, int r) {
        if (l > r) return 0;
        l += n, r += n;
        push(l), push(r);
        W res = 0;
        for (r++; l < r; l >>= 1, r >>= 1) {
            if (l & 1) res += tot[l++];
            if (r & 1) res += tot[--r];
        }
        return norm(res);
    }

    // O(logN) -- a[i], in [0, mod)
    T pointGet(int i) {
        push(i + n);
        return tot[i + n];
    }

    // O(logN) -- a[i] *= m (mod p) for i in [l, r]
    void rangeMultMod(int l, int r, T m) { update(l, r, norm(m)); }

    // O(logN) -- a[i] = v (mod p)
    void pointAssignMod(int i, T v) {
        int p = i + n;
        push(p);
        tot[p] = norm(v);
        rebuild(p);
    }

    // O(logN) -- a[i] += delta (mod p)
    void pointAddMod(int i, T delta) { pointAssignMod(i, norm(W(pointGet(i)) + delta)); }
};
