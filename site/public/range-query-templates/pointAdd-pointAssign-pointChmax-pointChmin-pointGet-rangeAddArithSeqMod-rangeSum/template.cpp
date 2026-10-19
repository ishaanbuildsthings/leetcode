// @operations: pointAdd pointAssign pointChmax pointChmin pointGet rangeAddArithSeqMod rangeSum
// @data-structure-type: lazy-seg-tree
// @complexities:
//   pointAdd: log(N)
//   pointAssign: log(N)
//   pointChmax: log(N)
//   pointChmin: log(N)
//   pointGet: log(N)
//   rangeAddArithSeqMod: log(N)
//   rangeSum: log(N)
//   build: N
// @memory:
//   layout: pow2-iterative
//   node: sum[4*N] length[4*N] sumIdx[4*N]
//   tags: lazyConst[4*N] lazyIdx[4*N]
//   other: none
//   note: each tag is a pending line const + idx*i (mod p); arrays are 2*size, size the next power of two >= n
// @original-file-url: https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/segment-trees/lazy/ArithmeticProgressionSTWithMod.cpp

// Range add of an arithmetic sequence mod p, range sum mod p, point ops. All indices 0-based, ranges inclusive.
// Lazy tag (c, d) means "add c + d * i to every position i under this node"; tags compose by plain addition.
// Every stored value is a residue in [0, mod); start / step may be negative. Iterative over a power-of-two layout.
// T: int, long long, ...; products go through W, which is wide enough for a product of two residues.
template <typename T>
struct APSegTreeMod {
    using W = conditional_t<sizeof(T) <= 4, long long, __int128>;
    int n, size, H;
    T mod;
    vector<T> sum, length, sumIdx, lazyConst, lazyIdx;  // length / sumIdx are also stored mod p

    T norm(W x) const { x %= mod; return T(x < 0 ? x + mod : x); }

    // O(N)
    explicit APSegTreeMod(const vector<T>& a, T mod = 1000000007) : n((int)a.size()), size(1), H(0), mod(mod) {
        while (size < max(n, 1)) size <<= 1, H++;
        sum.assign(2 * size, 0), length.assign(2 * size, 0), sumIdx.assign(2 * size, 0);
        lazyConst.assign(2 * size, 0), lazyIdx.assign(2 * size, 0);
        for (int i = 0; i < size; i++) length[size + i] = norm(1), sumIdx[size + i] = norm(i);
        for (int i = 0; i < n; i++) sum[size + i] = norm(a[i]);
        for (int x = size - 1; x > 0; x--) {
            length[x] = norm(W(length[2 * x]) + length[2 * x + 1]);
            sumIdx[x] = norm(W(sumIdx[2 * x]) + sumIdx[2 * x + 1]);
            sum[x] = norm(W(sum[2 * x]) + sum[2 * x + 1]);
        }
    }

    void apply(int x, T c, T d) {
        sum[x] = norm(W(sum[x]) + W(c) * length[x] % mod + W(d) * sumIdx[x] % mod);
        lazyConst[x] = norm(W(lazyConst[x]) + c), lazyIdx[x] = norm(W(lazyIdx[x]) + d);
    }

    void push(int x) {
        if (lazyConst[x] || lazyIdx[x]) {
            apply(2 * x, lazyConst[x], lazyIdx[x]);
            apply(2 * x + 1, lazyConst[x], lazyIdx[x]);
            lazyConst[x] = lazyIdx[x] = 0;
        }
    }

    void pushToRoot(int p) {
        for (int s = H; s > 0; s--) push(p >> s);
    }

    void recomputeToRoot(int p) {
        for (p >>= 1; p; p >>= 1)
            sum[p] = norm(W(sum[2 * p]) + sum[2 * p + 1] + W(lazyConst[p]) * length[p] % mod + W(lazyIdx[p]) * sumIdx[p] % mod);
    }

    // O(logN) -- a[l + j] += start + j * step (mod p) for j in [0, r - l]
    void rangeAddArithSeqMod(int l, int r, T start, T step) {
        if (l > r) return;
        T d = norm(step), c = norm(W(start) - W(d) * l % mod);
        int l0 = l + size, r0 = r + size;
        pushToRoot(l0), pushToRoot(r0);
        for (int lo = l0, hi = r0 + 1; lo < hi; lo >>= 1, hi >>= 1) {
            if (lo & 1) apply(lo++, c, d);
            if (hi & 1) apply(--hi, c, d);
        }
        recomputeToRoot(l0), recomputeToRoot(r0);
    }

    // O(logN) -- (a[l] + ... + a[r]) mod p (0 if l > r)
    T rangeSum(int l, int r) {
        if (l > r) return 0;
        int l0 = l + size, r0 = r + size;
        pushToRoot(l0), pushToRoot(r0);
        W res = 0;
        for (int lo = l0, hi = r0 + 1; lo < hi; lo >>= 1, hi >>= 1) {
            if (lo & 1) res += sum[lo++];
            if (hi & 1) res += sum[--hi];
        }
        return norm(res);
    }

    // O(logN) -- a[i], in [0, mod)
    T pointGet(int i) {
        pushToRoot(i + size);
        return sum[i + size];
    }

    // O(N) -- push every tag to the leaves; afterwards leafValue(i) == a[i] until the next update
    void pushAllDown() {
        for (int x = 1; x < size; x++) push(x);
    }

    // O(1) -- a[i], only valid right after pushAllDown()
    T leafValue(int i) const { return sum[i + size]; }

    // O(logN) -- a[i] += delta (mod p)
    void pointAdd(int i, T delta) { rangeAddArithSeqMod(i, i, delta, 0); }

    // O(logN) -- a[i] = v (mod p)
    void pointAssign(int i, T v) { rangeAddArithSeqMod(i, i, norm(W(v) - pointGet(i)), 0); }

    // O(logN) -- a[i] = max(a[i], v), comparing residues; v should be in [0, mod)
    void pointChmax(int i, T v) {
        T cur = pointGet(i);
        if (v > cur) rangeAddArithSeqMod(i, i, v - cur, 0);
    }

    // O(logN) -- a[i] = min(a[i], v), comparing residues; v should be in [0, mod)
    void pointChmin(int i, T v) {
        T cur = pointGet(i);
        if (v < cur) rangeAddArithSeqMod(i, i, norm(W(v) - cur), 0);
    }
};
