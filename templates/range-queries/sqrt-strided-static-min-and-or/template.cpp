// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/sqrt-strided-static-min-and-or/template.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: stridedAndQuery stridedMin stridedOrQuery
// @data-structure-type: sqrt
// @complexities:
//   stridedAndQuery: N*log(N)
//   stridedMin: N*log(N)
//   stridedOrQuery: N*log(N)
//   build: N
// @memory:
//   layout: none
//   node: minTable[1*N*log(N)] andTable[1*N*log(N)] orTable[1*N*log(N)]
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
    vector<T> minTable;
    int minStep = 0;  // the step minTable was built for
    vector<T> andTable;
    int andStep = 0;  // the step andTable was built for
    vector<T> orTable;
    int orStep = 0;  // the step orTable was built for

    // O(build) -- arr: the initial array
    explicit StridedQueries(const vector<T>& arr) {
        n = (int)arr.size();
        A = arr;
        while ((1 << levels) <= n) levels++;
        minTable.assign((size_t)levels * n, T(0));
        copy(A.begin(), A.end(), minTable.begin());
        andTable.assign((size_t)levels * n, T(0));
        copy(A.begin(), A.end(), andTable.begin());
        orTable.assign((size_t)levels * n, T(0));
        copy(A.begin(), A.end(), orTable.begin());
    }

    // min of a[l], a[l + step], ..., up to at most r. O(1) when step is the last step this op built for, so ask queries grouped by
    // step; needs 0 <= l <= r < n and step >= 1, else throws out_of_range
    T stridedMin(int l, int r, int step) {
        if (l < 0 || l > r || r >= n) throw out_of_range("stridedMin: needs 0 <= l <= r < n");
        if (step < 1) throw out_of_range("stridedMin: needs step >= 1");
        int last = l + (r - l) / step * step, count = (r - l) / step + 1;
        if (step != minStep && (count <= 32 || (long long)step * step > n)) {
            T res = A[l];
            for (int i = l + step; i <= last; i += step) res = min(res, A[i]);
            return res;
        }
        if (step != minStep) rebuildMin(step);
        int level = 31 - __builtin_clz(count);
        size_t base = (size_t)level * n;
        return min(minTable[base + l], minTable[base + last - ((1 << level) - 1) * step]);
    }

    // a[l] & a[l + step] & ..., up to at most r. O(1) when step is the last step this op built for, so ask queries grouped by
    // step; needs 0 <= l <= r < n and step >= 1, else throws out_of_range
    T stridedAndQuery(int l, int r, int step) {
        if (l < 0 || l > r || r >= n) throw out_of_range("stridedAndQuery: needs 0 <= l <= r < n");
        if (step < 1) throw out_of_range("stridedAndQuery: needs step >= 1");
        int last = l + (r - l) / step * step, count = (r - l) / step + 1;
        if (step != andStep && (count <= 32 || (long long)step * step > n)) {
            T res = A[l];
            for (int i = l + step; i <= last; i += step) res = (res & A[i]);
            return res;
        }
        if (step != andStep) rebuildAnd(step);
        int level = 31 - __builtin_clz(count);
        size_t base = (size_t)level * n;
        return (andTable[base + l] & andTable[base + last - ((1 << level) - 1) * step]);
    }

    // a[l] | a[l + step] | ..., up to at most r. O(1) when step is the last step this op built for, so ask queries grouped by
    // step; needs 0 <= l <= r < n and step >= 1, else throws out_of_range
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

    void rebuildMin(int step) {
        minStep = step;
        for (int level = 1; level < levels; level++) {
            long long jump = (long long)step << (level - 1);
            if (jump >= n) break;
            const T* previous = minTable.data() + (size_t)(level - 1) * n;
            T* current = minTable.data() + (size_t)level * n;
            for (int i = 0; i < n; i++) current[i] = i + jump < n ? min(previous[i], previous[i + jump]) : previous[i];
        }
    }

    void rebuildAnd(int step) {
        andStep = step;
        for (int level = 1; level < levels; level++) {
            long long jump = (long long)step << (level - 1);
            if (jump >= n) break;
            const T* previous = andTable.data() + (size_t)(level - 1) * n;
            T* current = andTable.data() + (size_t)level * n;
            for (int i = 0; i < n; i++) current[i] = i + jump < n ? (previous[i] & previous[i + jump]) : previous[i];
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
