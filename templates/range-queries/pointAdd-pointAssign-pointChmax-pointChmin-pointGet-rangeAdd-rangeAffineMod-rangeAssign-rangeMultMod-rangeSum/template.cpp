// @operations: pointAdd pointAssign pointChmax pointChmin pointGet rangeAdd rangeAffineMod rangeAssign rangeMultMod rangeSum
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
//   rangeSum: log(N)
//   build: N
// @memory:
//   layout: pow2-iterative
//   node: tot[4*N]
//   tags: mult[2*N] add[2*N]
//   other: none
//   note: one affine tag (mult, add) per node: x -> x*mult + add (mod p)
// @original-file-url: https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/segment-trees/lazy/Range-Add-Assign-Sum-MultFixedMod-AffineFixedMod-PointSet.cpp

// Range affine (a[i] = a[i] * m + x), add, mult, assign, range sum, all mod p, plus point ops.
// All indices 0-based, ranges inclusive [l, r]. Every update is one affine tag (mult, add):
//   add x -> (1, x)   mult m -> (m, 0)   assign x -> (0, x)
// Composing f = (m1, a1) then g = (m2, a2) gives (m1 * m2, a1 * m2 + a2): the OLD add is scaled by the NEW mult.
// Iterative over a power-of-two layout: push the two boundary paths, tag the covering nodes, recompute the paths.
// Values are residues in [0, mod). T: int, long long, ...; products go through W (wide enough for two residues).
template <typename T>
struct AffineSegTree {
    using W = conditional_t<sizeof(T) <= 4, long long, __int128>;
    int n, size, H;
    T mod;
    vector<T> tot, mult, add;  // tot over 2 * size slots; mult / add tags on internal nodes only

    T norm(W x) const { x %= mod; return T(x < 0 ? x + mod : x); }

    // O(N)
    explicit AffineSegTree(const vector<T>& a, T mod = 1000000007) : n((int)a.size()), size(1), H(0), mod(mod) {
        while (size < max(n, 1)) size <<= 1, H++;
        tot.assign(2 * size, 0), mult.assign(size, 1), add.assign(size, 0);
        for (int i = 0; i < n; i++) tot[size + i] = norm(a[i]);
        for (int x = size - 1; x > 0; x--) tot[x] = norm(W(tot[2 * x]) + tot[2 * x + 1]);
    }

    // v -> v * m + x on every slot of node i, which covers `len` slots
    void apply(int i, int len, T m, T x) {
        tot[i] = norm(W(tot[i]) * m + W(x) * len % mod);
        if (i < size) mult[i] = norm(W(mult[i]) * m), add[i] = norm(W(add[i]) * m + x);
    }

    void push(int i, int childLen) {
        if (mult[i] == 1 && add[i] == 0) return;
        apply(2 * i, childLen, mult[i], add[i]), apply(2 * i + 1, childLen, mult[i], add[i]);
        mult[i] = 1, add[i] = 0;
    }

    void pushToRoot(int p) {
        for (int s = H; s > 0; s--) push(p >> s, 1 << (s - 1));
    }

    // a node tagged during this update keeps its own tag's effect on top of its children
    void recomputeToRoot(int p) {
        int len = 2;
        for (p >>= 1; p; p >>= 1, len <<= 1) tot[p] = norm((W(tot[2 * p]) + tot[2 * p + 1]) * mult[p] + W(add[p]) * len % mod);
    }

    // O(logN) -- a[i] = a[i] * mult + add (mod p) for i in [l, r]; every other range update is this one
    void rangeAffineMod(int l, int r, T mult, T add) {
        if (l > r) return;
        T m = norm(mult), x = norm(add);
        int l0 = l + size, r0 = r + size;
        pushToRoot(l0), pushToRoot(r0);
        for (int lo = l0, hi = r0 + 1, len = 1; lo < hi; lo >>= 1, hi >>= 1, len <<= 1) {
            if (lo & 1) apply(lo++, len, m, x);
            if (hi & 1) apply(--hi, len, m, x);
        }
        recomputeToRoot(l0), recomputeToRoot(r0);
    }

    // O(logN) -- a[i] += x (mod p) for i in [l, r]
    void rangeAdd(int l, int r, T x) { rangeAffineMod(l, r, 1, x); }

    // O(logN) -- a[i] *= m (mod p) for i in [l, r]
    void rangeMultMod(int l, int r, T m) { rangeAffineMod(l, r, m, 0); }

    // O(logN) -- a[i] = x for i in [l, r]: multiply by 0, then add x
    void rangeAssign(int l, int r, T x) { rangeAffineMod(l, r, 0, x); }

    // O(logN) -- (a[l] + ... + a[r]) mod p (0 if l > r)
    T rangeSum(int l, int r) {
        if (l > r) return 0;
        l += size, r += size;
        pushToRoot(l), pushToRoot(r);
        W res = 0;
        for (r++; l < r; l >>= 1, r >>= 1) {
            if (l & 1) res += tot[l++];
            if (r & 1) res += tot[--r];
        }
        return norm(res);
    }

    // O(logN) -- a[i] = v
    void pointAssign(int i, T v) { rangeAffineMod(i, i, 0, v); }

    // O(logN) -- a[i], in [0, mod)
    T pointGet(int i) {
        pushToRoot(i + size);
        return tot[i + size];
    }

    // O(logN) -- a[i] = max(a[i], v), comparing residues; v should be in [0, mod)
    void pointChmax(int i, T v) { if (v > pointGet(i)) pointAssign(i, v); }

    // O(logN) -- a[i] = min(a[i], v), comparing residues; v should be in [0, mod)
    void pointChmin(int i, T v) { if (v < pointGet(i)) pointAssign(i, v); }

    // O(logN) -- a[i] += delta (mod p)
    void pointAdd(int i, T delta) { rangeAdd(i, i, delta); }
};
