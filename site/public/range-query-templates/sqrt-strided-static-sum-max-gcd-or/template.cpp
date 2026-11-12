// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/sqrt-strided-static-sum-max-gcd-or/template.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: stridedGcd stridedMax stridedOrQuery stridedSum
// @data-structure-type: sqrt
// @complexities:
//   stridedGcd: N*log(N)+N*log(U) ?
//   stridedMax: N*log(N)
//   stridedOrQuery: N*log(N)
//   stridedSum: N
//   build: N
// @memory:
//   layout: none
//   node: sumPre[1*N] maxTable[1*N*log(N)] gcdTable[1*N*log(N)] orTable[1*N*log(N)]
//   tags: none
//   other: A[1*N]
//   note: the listed cost is a rebuild. Each op keeps one table, for the last step it saw; a repeat of that step is O(1) and a step above sqrt(N) walks, so sorting queries by step offline costs one rebuild per distinct step

// Static strided queries in linear memory: each query covers a[l], a[l + step], a[l + 2 * step], ... up to at most r
// (the last position used may be below r). Each op keeps a single table for the last step it saw, rebuilt when the
// step changes, so the expected use is offline: sort the queries by step, then ask them in that order. All indices
// 0-based, ranges inclusive.
template <typename T>
struct StridedQueries {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    int n, levels = 1;
    vector<T> A;
    vector<S> sumPre;
    int sumStep = 0;  // the step sumPre was built for
    vector<T> maxTable;
    int maxStep = 0;  // the step maxTable was built for
    vector<T> gcdTable;
    int gcdStep = 0;  // the step gcdTable was built for
    vector<T> orTable;
    int orStep = 0;  // the step orTable was built for

    // O(build) -- arr: the initial array
    explicit StridedQueries(const vector<T>& arr) {
        n = (int)arr.size();
        A = arr;
        while ((1 << levels) <= n) levels++;
        sumPre.assign(n, 0);
        maxTable.assign((size_t)levels * n, T(0));
        copy(A.begin(), A.end(), maxTable.begin());
        gcdTable.assign((size_t)levels * n, T(0));
        copy(A.begin(), A.end(), gcdTable.begin());
        orTable.assign((size_t)levels * n, T(0));
        copy(A.begin(), A.end(), orTable.begin());
    }

    // a[l] + a[l + step] + ..., up to at most r. O(1) when step is the last step this op built for, so ask queries
    // grouped by step; needs 0 <= l <= r < n and step >= 1, else throws out_of_range
    S stridedSum(int l, int r, int step) {
        if (l < 0 || l > r || r >= n) throw out_of_range("stridedSum: needs 0 <= l <= r < n");
        if (step < 1) throw out_of_range("stridedSum: needs step >= 1");
        int last = l + (r - l) / step * step, count = (r - l) / step + 1;
        if (step != sumStep && (count <= 32 || (long long)step * step > n)) {
            S res = 0;
            for (int i = l; i <= last; i += step) res += A[i];
            return res;
        }
        if (step != sumStep) rebuildSum(step);
        return sumPre[last] - (l >= step ? sumPre[l - step] : S(0));
    }

    // max of a[l], a[l + step], ..., up to at most r. O(1) when step is the last step this op built for, so ask queries
    // grouped by step; needs 0 <= l <= r < n and step >= 1, else throws out_of_range
    T stridedMax(int l, int r, int step) {
        if (l < 0 || l > r || r >= n) throw out_of_range("stridedMax: needs 0 <= l <= r < n");
        if (step < 1) throw out_of_range("stridedMax: needs step >= 1");
        int last = l + (r - l) / step * step, count = (r - l) / step + 1;
        if (step != maxStep && (count <= 32 || (long long)step * step > n)) {
            T res = A[l];
            for (int i = l + step; i <= last; i += step) res = max(res, A[i]);
            return res;
        }
        if (step != maxStep) rebuildMax(step);
        int level = 31 - __builtin_clz(count);
        size_t base = (size_t)level * n;
        return max(maxTable[base + l], maxTable[base + last - ((1 << level) - 1) * step]);
    }

    // gcd of a[l], a[l + step], ..., up to at most r. O(1) when step is the last step this op built for, so ask queries
    // grouped by step; needs 0 <= l <= r < n and step >= 1, else throws out_of_range
    T stridedGcd(int l, int r, int step) {
        if (l < 0 || l > r || r >= n) throw out_of_range("stridedGcd: needs 0 <= l <= r < n");
        if (step < 1) throw out_of_range("stridedGcd: needs step >= 1");
        int last = l + (r - l) / step * step, count = (r - l) / step + 1;
        if (step != gcdStep && (count <= 32 || (long long)step * step > n)) {
            T res = A[l];
            for (int i = l + step; i <= last; i += step) res = std::gcd(res, A[i]);
            return res;
        }
        if (step != gcdStep) rebuildGcd(step);
        int level = 31 - __builtin_clz(count);
        size_t base = (size_t)level * n;
        return std::gcd(gcdTable[base + l], gcdTable[base + last - ((1 << level) - 1) * step]);
    }

    // a[l] | a[l + step] | ..., up to at most r. O(1) when step is the last step this op built for, so ask queries
    // grouped by step; needs 0 <= l <= r < n and step >= 1, else throws out_of_range
    T stridedOrQuery(int l, int r, int step) {
        if (l < 0 || l > r || r >= n) throw out_of_range("stridedOrQuery: needs 0 <= l <= r < n");
        if (step < 1) throw out_of_range("stridedOrQuery: needs step >= 1");
        int last = l + (r - l) / step * step, count = (r - l) / step + 1;
        if (step != orStep && (count <= 32 || (long long)step * step > n)) {
            T res = A[l];
            for (int i = l + step; i <= last; i += step) res = (res | A[i]);
            return res;
        }
        if (step != orStep) rebuildOr(step);
        int level = 31 - __builtin_clz(count);
        size_t base = (size_t)level * n;
        return (orTable[base + l] | orTable[base + last - ((1 << level) - 1) * step]);
    }

    // ---- internals ----

    void rebuildSum(int step) {
        sumStep = step;
        for (int i = 0; i < n; i++) sumPre[i] = (i >= step ? sumPre[i - step] : S(0)) + A[i];
    }

    void rebuildMax(int step) {
        maxStep = step;
        for (int level = 1; level < levels; level++) {
            long long jump = (long long)step << (level - 1);
            if (jump >= n) break;
            const T* previous = maxTable.data() + (size_t)(level - 1) * n;
            T* current = maxTable.data() + (size_t)level * n;
            for (int i = 0; i < n; i++) current[i] = i + jump < n ? max(previous[i], previous[i + jump]) : previous[i];
        }
    }

    void rebuildGcd(int step) {
        gcdStep = step;
        for (int level = 1; level < levels; level++) {
            long long jump = (long long)step << (level - 1);
            if (jump >= n) break;
            const T* previous = gcdTable.data() + (size_t)(level - 1) * n;
            T* current = gcdTable.data() + (size_t)level * n;
            for (int i = 0; i < n; i++) current[i] = i + jump < n ? std::gcd(previous[i],
                previous[i + jump]) : previous[i];
        }
    }

    void rebuildOr(int step) {
        orStep = step;
        for (int level = 1; level < levels; level++) {
            long long jump = (long long)step << (level - 1);
            if (jump >= n) break;
            const T* previous = orTable.data() + (size_t)(level - 1) * n;
            T* current = orTable.data() + (size_t)level * n;
            for (int i = 0; i < n; i++) current[i] = i + jump < n ? (previous[i] | previous[i + jump]) : previous[i];
        }
    }
};
