// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/rangeSum/template.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: rangeSum sumAll
// @data-structure-type: prefix-sum
// @complexities:
//   rangeSum: 1
//   sumAll: 1
//   build: N
// @memory:
//   layout: none
//   node: P[1*N]
//   tags: none
//   other: none
//   note: P[i] = a[0] + ... + a[i-1], one more entry than the array

// Static range sum with a prefix sum array: O(N) build, O(1) per query, no updates. All indices 0-based, ranges
// inclusive [l, r].
// T: int, long long, ...; sums are kept in S (long long for small T).
template <typename T>
struct PrefixSums {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    int n;
    vector<S> P;  // P[i] = a[0] + ... + a[i-1]

    // O(N) -- a: the array (can be empty)
    explicit PrefixSums(const vector<T>& a) : n((int)a.size()), P(n + 1) {
        for (int i = 0; i < n; i++) P[i + 1] = P[i] + S(a[i]);
    }

    // O(1) -- a[l] + ... + a[r]; needs 0 <= l <= r < n, else throws out_of_range
    S rangeSum(int l, int r) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeSum: needs 0 <= l <= r < n");
        return P[r + 1] - P[l];
    }

    // O(1) -- a[0] + ... + a[n-1] (rangeSum(0, n - 1)); needs n >= 1, else throws out_of_range
    auto sumAll() const {
        if (n < 1) throw out_of_range("sumAll: needs n >= 1");
        return P[n];
    }
};
