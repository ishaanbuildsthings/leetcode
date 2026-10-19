// @operations: pointAdd pointAssign pointChmax pointChmin pointGet rangeAdd rangeAddArithSeq rangeSum
// @data-structure-type: BIT
// @complexities:
//   pointAdd: log(N)
//   pointAssign: log(N)
//   pointChmax: log(N)
//   pointChmin: log(N)
//   pointGet: log(N)
//   rangeAdd: log(N)
//   rangeAddArithSeq: log(N)
//   rangeSum: log(N)
//   build: N
// @memory:
//   layout: none
//   node: bA[1*N] bB[1*N] bC[1*N]
//   tags: none
//   other: none
//   note: prefix sums are kept as A(x) + B(x) * x + C(x) * x(x+1)/2 with A, B, C three Fenwick trees

// Range add of an arithmetic sequence (and plain range add) + range sum with three Fenwick trees, no lazy tags.
// All indices 0-based, ranges inclusive [l, r].
// Adding c0 + c1 * i to every i in [l, r] changes the prefix sum P(x) = a[0] + ... + a[x] by
//   x in [l, r]:  c0 * (x - l + 1) + c1 * (T(x) - T(l - 1))        T(k) = k * (k + 1) / 2
//   x > r:        the whole added total
// so keep P(x) = A(x) + B(x) * x + C(x) * T(x), where A, B, C are prefix sums of point updates made at l and r + 1.
// Using T(x) instead of x^2 keeps every coefficient an integer (no division by 2).
// T: int, long long, ...; sums are kept in S (long long for small T).
template <typename T>
struct ArithSeqSumBIT {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    int n;
    vector<S> bA, bB, bC;  // 1-indexed

    static S tri(S k) { return k * (k + 1) / 2; }

    // O(N)
    explicit ArithSeqSumBIT(const vector<T>& a) : n((int)a.size()), bA(n + 1), bB(n + 1), bC(n + 1) {
        for (int i = 0; i < n; i++) bA[i + 1] = a[i];  // a[i] alone adds a[i] to every P(x) with x >= i
        for (int i = 1; i <= n; i++) {
            int j = i + (i & -i);
            if (j <= n) bA[j] += bA[i];
        }
    }

    void point(int i, S a, S b, S c) {
        for (i++; i <= n; i += i & -i) bA[i] += a, bB[i] += b, bC[i] += c;
    }

    // O(logN) -- a[0] + ... + a[x] (0 for x = -1)
    S prefix(int x) const {
        S sa = 0, sb = 0, sc = 0;
        for (int i = x + 1; i > 0; i &= i - 1) sa += bA[i], sb += bB[i], sc += bC[i];
        return sa + sb * x + sc * tri(x);
    }

    // O(logN) -- a[l + j] += start + j * step for j in [0, r - l]
    void rangeAddArithSeq(int l, int r, T start, T step) {
        if (l > r) return;
        S c0 = S(start) - S(step) * l, c1 = step;  // adding c0 + c1 * i at index i
        S a = c0 * (1 - l) - c1 * tri(l - 1);
        point(l, a, c0, c1);
        if (r + 1 < n) {
            S total = c0 * (r - l + 1) + c1 * (tri(r) - tri(l - 1));
            point(r + 1, total - a, -c0, -c1);
        }
    }

    // O(logN) -- a[i] += v for i in [l, r]
    void rangeAdd(int l, int r, T v) { rangeAddArithSeq(l, r, v, 0); }

    // O(logN) -- a[l] + ... + a[r]
    S rangeSum(int l, int r) const { return l <= r ? prefix(r) - prefix(l - 1) : S(0); }

    // O(logN) -- a[i]
    T pointGet(int i) const { return T(rangeSum(i, i)); }

    // O(logN) -- a[i] += delta
    void pointAdd(int i, T delta) { rangeAdd(i, i, delta); }

    // O(logN) -- a[i] = v
    void pointAssign(int i, T v) { rangeAdd(i, i, v - pointGet(i)); }

    // O(logN) -- a[i] = max(a[i], v)
    void pointChmax(int i, T v) {
        T cur = pointGet(i);
        if (v > cur) rangeAdd(i, i, v - cur);
    }

    // O(logN) -- a[i] = min(a[i], v)
    void pointChmin(int i, T v) {
        T cur = pointGet(i);
        if (v < cur) rangeAdd(i, i, v - cur);
    }
};
