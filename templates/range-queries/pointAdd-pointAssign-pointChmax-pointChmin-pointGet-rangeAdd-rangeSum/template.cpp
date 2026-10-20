// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAdd-rangeSum/template.cpp
// @operations: pointAdd pointAssign pointChmax pointChmin pointGet rangeAdd rangeSum
// @data-structure-type: BIT
// @complexities:
//   pointAdd: log(N)
//   pointAssign: log(N)
//   pointChmax: log(N)
//   pointChmin: log(N)
//   pointGet: log(N)
//   rangeAdd: log(N)
//   rangeSum: log(N)
//   build: N
// @memory:
//   layout: none
//   node: b1[1*N] b2[1*N]
//   tags: none
//   other: none
//   note: two Fenwick trees over the difference array d (d[i] = a[i] - a[i-1]): b1 over d[i], b2 over d[i] * i

// Range add + range sum with two Fenwick trees, no lazy tags. All indices 0-based, ranges inclusive [l, r].
// With d the difference array, a[0] + ... + a[x] = (x + 1) * sum(d[0..x]) - sum(d[i] * i for i in 0..x),
// so one BIT over d[i] and one over d[i] * i answer any prefix sum, and a range add touches two entries of d.
// T: int, long long, ...; sums are kept in S (long long for small T).
template <typename T>
struct RangeAddSumBIT {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    int n;
    vector<S> b1, b2;  // 1-indexed

    // O(N)
    explicit RangeAddSumBIT(const vector<T>& a) : n((int)a.size()), b1(n + 1), b2(n + 1) {
        for (int i = 0; i < n; i++) {
            S d = S(a[i]) - (i ? S(a[i - 1]) : S(0));
            b1[i + 1] = d, b2[i + 1] = d * i;
        }
        for (int i = 1; i <= n; i++) {
            int j = i + (i & -i);
            if (j <= n) b1[j] += b1[i], b2[j] += b2[i];
        }
    }

    void addDiff(int i, S d) {
        S di = d * i;
        for (i++; i <= n; i += i & -i) b1[i] += d, b2[i] += di;
    }

    // O(logN) -- a[0] + ... + a[x] (0 for x = -1)
    S prefix(int x) const {
        S s1 = 0, s2 = 0;
        for (int i = x + 1; i > 0; i &= i - 1) s1 += b1[i], s2 += b2[i];
        return s1 * (x + 1) - s2;
    }

    // O(logN) -- a[i] += v for i in [l, r]
    void rangeAdd(int l, int r, T v) {
        if (l > r) return;
        addDiff(l, v);
        if (r + 1 < n) addDiff(r + 1, -S(v));
    }

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
