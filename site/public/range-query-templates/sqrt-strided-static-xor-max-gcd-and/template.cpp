// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/sqrt-strided-static-xor-max-gcd-and/template.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: stridedAndQuery stridedGcd stridedMax stridedXorQuery
// @data-structure-type: sqrt
// @complexities:
//   stridedAndQuery: N*log(N)
//   stridedGcd: N*log(N)+N*log(U) ?
//   stridedMax: N*log(N)
//   stridedXorQuery: N
//   build: N
// @memory:
//   layout: none
//   node: xorPre[1*N] maxTable[1*N*log(N)] gcdTable[1*N*log(N)] andTable[1*N*log(N)]
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
    vector<T> xorPre;
    int xorStep = 0;  // the step xorPre was built for
    vector<T> maxTable;
    int maxStep = 0;  // the step maxTable was built for
    vector<T> gcdTable;
    int gcdStep = 0;  // the step gcdTable was built for
    vector<T> andTable;
    int andStep = 0;  // the step andTable was built for

    // O(build) -- arr: the initial array
    explicit StridedQueries(const vector<T>& arr) {
        n = (int)arr.size();
        A = arr;
        while ((1 << levels) <= n) levels++;
        xorPre.assign(n, 0);
        maxTable.assign((size_t)levels * n, T(0));
        copy(A.begin(), A.end(), maxTable.begin());
        gcdTable.assign((size_t)levels * n, T(0));
        copy(A.begin(), A.end(), gcdTable.begin());
        andTable.assign((size_t)levels * n, T(0));
        copy(A.begin(), A.end(), andTable.begin());
    }

    // a[l] ^ a[l + step] ^ ..., up to at most r. O(1) when step is the last step this op built for, so ask queries grouped by
    // step; needs 0 <= l <= r < n and step >= 1, else throws out_of_range
    T stridedXorQuery(int l, int r, int step) {
        if (l < 0 || l > r || r >= n) throw out_of_range("stridedXorQuery: needs 0 <= l <= r < n");
        if (step < 1) throw out_of_range("stridedXorQuery: needs step >= 1");
        int last = l + (r - l) / step * step, count = (r - l) / step + 1;
        if (step != xorStep && (count <= 32 || (long long)step * step > n)) {
            T res = 0;
            for (int i = l; i <= last; i += step) res ^= A[i];
            return res;
        }
        if (step != xorStep) rebuildXor(step);
        return xorPre[last] ^ (l >= step ? xorPre[l - step] : T(0));
    }

    // max of a[l], a[l + step], ..., up to at most r. O(1) when step is the last step this op built for, so ask queries grouped by
    // step; needs 0 <= l <= r < n and step >= 1, else throws out_of_range
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

    // gcd of a[l], a[l + step], ..., up to at most r. O(1) when step is the last step this op built for, so ask queries grouped by
    // step; needs 0 <= l <= r < n and step >= 1, else throws out_of_range
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

    // ---- internals ----

    void rebuildXor(int step) {
        xorStep = step;
        for (int i = 0; i < n; i++) xorPre[i] = (i >= step ? xorPre[i - step] : T(0)) ^ A[i];
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
            for (int i = 0; i < n; i++) current[i] = i + jump < n ? std::gcd(previous[i], previous[i + jump]) : previous[i];
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
};
