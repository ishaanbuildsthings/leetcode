// @operations: pointAdd pointAssign pointGet rangeAddMod rangeAffineMod rangeAssignMod rangeMultMod rangeSumMod
// @data-structure-type: lazy-seg-tree
// @complexities:
//   pointAdd: log(N)
//   pointAssign: log(N)
//   pointGet: log(N)
//   rangeAddMod: log(N)
//   rangeAffineMod: log(N)
//   rangeAssignMod: log(N)
//   rangeMultMod: log(N)
//   rangeSumMod: log(N)
//   build: N
// @memory:
//   layout: 2n-iterative
//   node: tot[2*N]
//   tags: mul[1*N] add[1*N]
//   other: none
//   note: tags live on the N internal nodes only; each is one affine map x -> x*mul + add (mod p)

// Range affine (a[i] = a[i] * mult + add), add, mult, assign, and range sum, all mod p, plus point ops.
// All indices 0-based, ranges inclusive [l, r]. Every update is one affine tag (mult, add):
//   add x -> (1, x)   mult m -> (m, 0)   assign x -> (0, x)
// Composing f = (m1, a1) then g = (m2, a2) gives (m1 * m2, a1 * m2 + a2): the OLD add is scaled by the NEW mult.
// Iterative 2N lazy tree: values on the leaves, a tag on each internal node ("applied here, not yet pushed"). A
// covering node at level s is a perfect subtree of 2^s leaves, so v -> v * m + a turns its sum into sum * m + a * 2^s.
// Values are residues in [0, mod). T: int, long long, ...
template <typename T>
struct AffineSumTree {
    using W = conditional_t<sizeof(T) <= 4, long long, __int128>;  // wide enough for a product of two residues
    int n, h;
    T mod;
    vector<T> tot;  // 2N: leaves are tot[n..2n)
    vector<T> mul, add;  // N: tags on internal nodes

    T norm(W x) const { x %= mod; return T(x < 0 ? x + mod : x); }

    // O(N)
    explicit AffineSumTree(const vector<T>& a, T mod = 1000000007)
        : n((int)a.size()), h(a.empty() ? 0 : 32 - __builtin_clz((unsigned)a.size())), mod(mod), tot(2 * a.size()) {
        for (int i = 0; i < n; i++) tot[n + i] = norm(a[i]);
        for (int x = n - 1; x > 0; x--) tot[x] = norm(W(tot[2 * x]) + tot[2 * x + 1]);
        mul.assign(n, 1), add.assign(n, 0);
    }

    // v -> v * m + a on node x, which covers k slots
    void apply(int x, int k, T m, T a) {
        tot[x] = norm(W(tot[x]) * m + W(a) * k % mod);
        if (x < n) mul[x] = norm(W(mul[x]) * m), add[x] = norm(W(add[x]) * m + a);
    }

    // push every tag on the root-to-leaf path of leaf p down one level
    void push(int p) {
        for (int s = h; s > 0; s--) {
            int x = p >> s, k = 1 << (s - 1);
            if (mul[x] != 1 || add[x]) apply(2 * x, k, mul[x], add[x]), apply(2 * x + 1, k, mul[x], add[x]), mul[x] = 1, add[x] = 0;
        }
    }

    // recompute the ancestors of leaf p; each keeps the effect of its own pending tag
    void rebuild(int p) {
        for (int k = 2; p > 1; k <<= 1) {
            p >>= 1;
            tot[p] = norm((W(tot[2 * p]) + tot[2 * p + 1]) * mul[p] + W(add[p]) * k % mod);
        }
    }

    void update(int l, int r, T m, T a) {
        if (l > r) return;
        int l0 = l + n, r0 = r + n;
        push(l0), push(r0);
        for (int i = l0, j = r0 + 1, k = 1; i < j; i >>= 1, j >>= 1, k <<= 1) {
            if (i & 1) apply(i++, k, m, a);
            if (j & 1) apply(--j, k, m, a);
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

    // O(logN) -- a[i] = a[i] * mult + add (mod p) for i in [l, r]; every other update is this one
    void rangeAffineMod(int l, int r, T mult, T add) { update(l, r, norm(mult), norm(add)); }

    // O(logN) -- a[i] += v (mod p) for i in [l, r]
    void rangeAddMod(int l, int r, T v) { update(l, r, 1, norm(v)); }

    // O(logN) -- a[i] *= m (mod p) for i in [l, r]
    void rangeMultMod(int l, int r, T m) { update(l, r, norm(m), 0); }

    // O(logN) -- a[i] = v for i in [l, r]: multiply by 0, then add v
    void rangeAssignMod(int l, int r, T v) { update(l, r, 0, norm(v)); }

    // O(logN) -- a[i] = v (mod p)
    void pointAssign(int i, T v) { update(i, i, 0, norm(v)); }

    // O(logN) -- a[i] += delta (mod p)
    void pointAdd(int i, T delta) { update(i, i, 1, norm(delta)); }
};
