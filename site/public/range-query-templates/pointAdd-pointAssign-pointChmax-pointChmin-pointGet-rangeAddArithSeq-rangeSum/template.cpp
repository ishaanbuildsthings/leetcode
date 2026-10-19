// @operations: pointAdd pointAssign pointChmax pointChmin pointGet rangeAddArithSeq rangeSum
// @data-structure-type: lazy-seg-tree
// @complexities:
//   pointAdd: log(N)
//   pointAssign: log(N)
//   pointChmax: log(N)
//   pointChmin: log(N)
//   pointGet: log(N)
//   rangeAddArithSeq: log(N)
//   rangeSum: log(N)
//   build: N
// @memory:
//   layout: pow2-iterative
//   node: sum[4*N] length[4*N] sumIdx[4*N]
//   tags: lazyConst[4*N] lazyIdx[4*N]
//   other: none
//   note: each tag is a pending line const + idx*i; arrays are 2*size, size the next power of two >= n
// @original-file-url: https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/segment-trees/lazy/ArithmeticProgressionST.cpp

// Range add of an arithmetic sequence, range sum, point ops. All indices 0-based, ranges inclusive [l, r].
// Lazy tag (c, d) means "add c + d * i to every position i under this node"; tags compose by plain addition.
// Iterative over a power-of-two layout. T: int, long long, ...; sums are kept in T, so use long long unless
// every range sum (and sum of indices, ~N^2 / 2) fits in int.
template <typename T>
struct APSegTree {
    int n, size, H;
    vector<T> sum, length, sumIdx, lazyConst, lazyIdx;

    // O(N)
    explicit APSegTree(const vector<T>& a) : n((int)a.size()), size(1), H(0) {
        while (size < max(n, 1)) size <<= 1, H++;
        sum.assign(2 * size, 0), length.assign(2 * size, 0), sumIdx.assign(2 * size, 0);
        lazyConst.assign(2 * size, 0), lazyIdx.assign(2 * size, 0);
        for (int i = 0; i < size; i++) length[size + i] = 1, sumIdx[size + i] = i;
        for (int i = 0; i < n; i++) sum[size + i] = a[i];
        for (int x = size - 1; x > 0; x--) {
            length[x] = length[2 * x] + length[2 * x + 1];
            sumIdx[x] = sumIdx[2 * x] + sumIdx[2 * x + 1];
            sum[x] = sum[2 * x] + sum[2 * x + 1];
        }
    }

    void apply(int x, T c, T d) {
        sum[x] += c * length[x] + d * sumIdx[x];
        lazyConst[x] += c, lazyIdx[x] += d;
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
        for (p >>= 1; p; p >>= 1) sum[p] = sum[2 * p] + sum[2 * p + 1] + lazyConst[p] * length[p] + lazyIdx[p] * sumIdx[p];
    }

    // O(logN) -- a[l + j] += start + j * step for j in [0, r - l]
    void rangeAddArithSeq(int l, int r, T start, T step) {
        if (l > r) return;
        T c = start - step * l, d = step;
        int l0 = l + size, r0 = r + size;
        pushToRoot(l0), pushToRoot(r0);
        for (int lo = l0, hi = r0 + 1; lo < hi; lo >>= 1, hi >>= 1) {
            if (lo & 1) apply(lo++, c, d);
            if (hi & 1) apply(--hi, c, d);
        }
        recomputeToRoot(l0), recomputeToRoot(r0);
    }

    // O(logN) -- a[l] + ... + a[r] (0 if l > r)
    T rangeSum(int l, int r) {
        if (l > r) return 0;
        int l0 = l + size, r0 = r + size;
        pushToRoot(l0), pushToRoot(r0);
        T res = 0;
        for (int lo = l0, hi = r0 + 1; lo < hi; lo >>= 1, hi >>= 1) {
            if (lo & 1) res += sum[lo++];
            if (hi & 1) res += sum[--hi];
        }
        return res;
    }

    // O(logN) -- a[i]
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

    // O(logN) -- a[i] += delta
    void pointAdd(int i, T delta) { rangeAddArithSeq(i, i, delta, 0); }

    // O(logN) -- a[i] = v
    void pointAssign(int i, T v) { rangeAddArithSeq(i, i, v - pointGet(i), 0); }

    // O(logN) -- a[i] = max(a[i], v)
    void pointChmax(int i, T v) {
        T cur = pointGet(i);
        if (v > cur) rangeAddArithSeq(i, i, v - cur, 0);
    }

    // O(logN) -- a[i] = min(a[i], v)
    void pointChmin(int i, T v) {
        T cur = pointGet(i);
        if (v < cur) rangeAddArithSeq(i, i, v - cur, 0);
    }
};
