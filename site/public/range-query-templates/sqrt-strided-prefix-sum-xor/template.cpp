// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/sqrt-strided-prefix-sum-xor/template.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: stridedSum stridedXorQuery
// @data-structure-type: sqrt
// @complexities:
//   stridedSum: sqrt(N)
//   stridedXorQuery: sqrt(N)
//   build: 2*N*sqrt(N)
// @memory:
//   layout: none
//   node: sumPre[1*N*sqrt(N)] xorPre[1*N*sqrt(N)]
//   tags: none
//   other: A[1*N]
//   note: O(1) for a step up to the cutoff, sqrt(N) only for a bigger one. The default cutoff is about 90 million values at N = 2e5, so pass a lower one when memory is tight

// Static strided queries, every small stride's prefix array built up front: each query covers a[l], a[l + step],
// a[l + 2 * step], ... up to at most r (the last position used may be below r). All indices 0-based, ranges inclusive.
template <typename T>
struct StridedQueries {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    int n, strides;
    vector<T> A;
    vector<S> sumPre;
    vector<T> xorPre;

    // O(build) -- arr: the initial array. cutoff: prefix arrays are kept for steps up to it; leave it out for sqrt(n), and
    // lower it when memory is tight (each kept step costs n values)
    explicit StridedQueries(const vector<T>& arr, int cutoff = -1) {
        n = (int)arr.size();
        A = arr;
        strides = cutoff != -1 ? cutoff : max(1, min(n, (int)sqrt((double)n)));
        if (strides < 0 || strides > n) throw out_of_range("StridedQueries: needs 0 <= cutoff <= n");
        sumPre.assign((size_t)strides * n, 0);
        for (int step = 1; step <= strides; step++) {
            S* pre = sumPre.data() + (size_t)(step - 1) * n;
            for (int i = 0; i < n; i++) pre[i] = (i >= step ? pre[i - step] : S(0)) + A[i];
        }
        xorPre.assign((size_t)strides * n, 0);
        for (int step = 1; step <= strides; step++) {
            T* pre = xorPre.data() + (size_t)(step - 1) * n;
            for (int i = 0; i < n; i++) pre[i] = (i >= step ? pre[i - step] : T(0)) ^ A[i];
        }
    }

    // a[l] + a[l + step] + ..., up to at most r. O(1) for a kept step; needs 0 <= l <= r < n and step >= 1, else throws out_of_range
    S stridedSum(int l, int r, int step) {
        if (l < 0 || l > r || r >= n) throw out_of_range("stridedSum: needs 0 <= l <= r < n");
        if (step < 1) throw out_of_range("stridedSum: needs step >= 1");
        int last = l + (r - l) / step * step;
        if (step > strides) {
            S res = 0;
            for (int i = l; i <= last; i += step) res += A[i];
            return res;
        }
        const S* pre = sumPre.data() + (size_t)(step - 1) * n;
        return pre[last] - (l >= step ? pre[l - step] : S(0));
    }

    // a[l] ^ a[l + step] ^ ..., up to at most r. O(1) for a kept step; needs 0 <= l <= r < n and step >= 1, else throws out_of_range
    T stridedXorQuery(int l, int r, int step) {
        if (l < 0 || l > r || r >= n) throw out_of_range("stridedXorQuery: needs 0 <= l <= r < n");
        if (step < 1) throw out_of_range("stridedXorQuery: needs step >= 1");
        int last = l + (r - l) / step * step;
        if (step > strides) {
            T res = 0;
            for (int i = l; i <= last; i += step) res ^= A[i];
            return res;
        }
        const T* pre = xorPre.data() + (size_t)(step - 1) * n;
        return pre[last] ^ (l >= step ? pre[l - step] : T(0));
    }
};
