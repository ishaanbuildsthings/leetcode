// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAdd-rangeSum/template.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: getAll pointAdd pointAssign pointChmax pointChmin pointGet rangeAdd rangeSum sumAll
// @data-structure-type: BIT
// @complexities:
//   getAll: N
//   pointAdd: log(N)
//   pointAssign: log(N)
//   pointChmax: log(N)
//   pointChmin: log(N)
//   pointGet: log(N)
//   rangeAdd: log(N)
//   rangeSum: log(N)
//   sumAll: log(N)
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

    // O(logN) -- a[i] += v for i in [l, r]; needs 0 <= l <= r < n, else throws out_of_range
    void rangeAdd(int l, int r, T v) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeAdd: needs 0 <= l <= r < n");
        if (l > r) return;
        addDiff(l, v);
        if (r + 1 < n) addDiff(r + 1, -S(v));
    }

    // O(logN) -- a[l] + ... + a[r]; needs 0 <= l <= r < n, else throws out_of_range
    S rangeSum(int l, int r) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeSum: needs 0 <= l <= r < n");
        return l <= r ? prefix(r) - prefix(l - 1) : S(0);
    }

    // O(logN) -- a[i]; needs 0 <= i < n, else throws out_of_range
    T pointGet(int i) const {
        if (i < 0 || i >= n) throw out_of_range("pointGet: needs 0 <= i < n");
        return T(rangeSum(i, i));
    }

    // O(N) -- the whole array: undo the Fenwick sums on a copy (last index first: entry i was added into
    // i + lowbit(i) once complete), then one pass of running prefix sums
    vector<T> getAll() const {
        vector<S> B1(b1), B2(b2);
        for (int i = n; i > 0; i--) {
            int j = i + (i & -i);
            if (j <= n) B1[j] -= B1[i], B2[j] -= B2[i];
        }
        vector<T> out(n);
        S s1 = 0, s2 = 0, prev = 0;
        for (int x = 0; x < n; x++) {
            s1 += B1[x + 1], s2 += B2[x + 1];
            S p = s1 * (x + 1) - s2;
            out[x] = T(p - prev), prev = p;
        }
        return out;
    }

    // O(logN) -- a[i] += delta; needs 0 <= i < n, else throws out_of_range
    void pointAdd(int i, T delta) {
        if (i < 0 || i >= n) throw out_of_range("pointAdd: needs 0 <= i < n");
        rangeAdd(i, i, delta);
    }

    // O(logN) -- a[i] = v; needs 0 <= i < n, else throws out_of_range
    void pointAssign(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointAssign: needs 0 <= i < n");
        rangeAdd(i, i, v - pointGet(i));
    }

    // O(logN) -- a[i] = max(a[i], v); needs 0 <= i < n, else throws out_of_range
    void pointChmax(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointChmax: needs 0 <= i < n");
        T cur = pointGet(i);
        if (v > cur) rangeAdd(i, i, v - cur);
    }

    // O(logN) -- a[i] = min(a[i], v); needs 0 <= i < n, else throws out_of_range
    void pointChmin(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointChmin: needs 0 <= i < n");
        T cur = pointGet(i);
        if (v < cur) rangeAdd(i, i, v - cur);
    }

    // O(log(N)) -- sum of the whole array a[0..n-1] (rangeSum(0, n - 1)); needs n >= 1, else throws out_of_range
    auto sumAll() {
        if (n < 1) throw out_of_range("sumAll: needs n >= 1");
        return rangeSum(0, n - 1);
    }

};
