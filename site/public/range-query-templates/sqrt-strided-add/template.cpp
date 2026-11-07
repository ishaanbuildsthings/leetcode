// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/sqrt-strided-add/template.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: getAll pointAdd pointAssign pointChmax pointChmin pointGet stridedAdd
// @data-structure-type: sqrt
// @complexities:
//   getAll: N*sqrt(NlogN)
//   pointAdd: 1
//   pointAssign: sqrt(NlogN)
//   pointChmax: sqrt(NlogN)
//   pointChmin: sqrt(NlogN)
//   pointGet: sqrt(NlogN)
//   stridedAdd: sqrt(NlogN)
//   build: N*sqrt(N/logN)
// @memory:
//   layout: none
//   node: diffs[1*N*sqrt(N/logN)]
//   tags: none
//   other: A[1*N] offsets[1*N]
//   note: a small step is a range add on that step's Fenwick tree of differences, a big step walks its positions, and a point read adds up every small step

// Strided add with point reads and writes: stridedAdd(l, r, step, v) adds v to a[l], a[l + step], ... up to at most r
// (the last position used may be below r). A strided sum on top of this has no good bound: two different steps
// overlap in a pattern that depends on both. All indices 0-based, ranges inclusive.
template <typename T>
struct StridedQueries {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    int n, strides;
    vector<S> A;
    vector<int> offsets;  // offsets[step * (step - 1) / 2 + residue]: where that residue class starts in that stride's list
    vector<S> diffs;  // one Fenwick tree of differences per kept step, n + 2 slots each

    // O(build) -- arr: the initial array. cutoff: a Fenwick tree is kept for steps up to it (more memory and slower
    // reads, faster big-step adds); leave it out for sqrt(n / log n)
    explicit StridedQueries(const vector<T>& arr, int cutoff = -1) {
        n = (int)arr.size();
        A.assign(arr.begin(), arr.end());
        strides = cutoff != -1 ? cutoff : max(1, min(n, (int)sqrt(n / max(1.0, log2(n + 1.0)))));
        if (strides < 0 || strides > n) throw out_of_range("StridedQueries: needs 0 <= cutoff <= n");
        offsets.assign((size_t)strides * (strides + 1) / 2, 0);
        for (int step = 1; step <= strides; step++) {
            int used = 0;
            for (int residue = 0; residue < step; residue++) {
                offsets[step * (step - 1) / 2 + residue] = used;
                if (residue < n) used += (n - residue + step - 1) / step;
            }
        }
        diffs.assign((size_t)strides * (n + 2), 0);
    }

    // a[l] += v, a[l + step] += v, ... up to at most r; needs 0 <= l <= r < n and step >= 1, else throws out_of_range
    void stridedAdd(int l, int r, int step, T v) {
        if (l < 0 || l > r || r >= n) throw out_of_range("stridedAdd: needs 0 <= l <= r < n");
        if (step < 1) throw out_of_range("stridedAdd: needs step >= 1");
        int last = l + (r - l) / step * step;
        if (step > strides) {
            for (int i = l; i <= last; i += step) A[i] += v;
            return;
        }
        addDiff(step, listIndex(step, l), S(v));
        addDiff(step, listIndex(step, last) + 1, -S(v));
    }

    // the current a[i]; needs 0 <= i < n, else throws out_of_range
    S pointGet(int i) const {
        if (i < 0 || i >= n) throw out_of_range("pointGet: needs 0 <= i < n");
        S res = A[i];
        for (int step = 1; step <= strides; step++) {
            const S* tree = diffs.data() + (size_t)(step - 1) * (n + 2);
            for (int node = listIndex(step, i) + 1; node > 0; node -= node & -node) res += tree[node];
        }
        return res;
    }

    // a[i] += v; needs 0 <= i < n, else throws out_of_range
    void pointAdd(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointAdd: needs 0 <= i < n");
        A[i] += v;
    }

    // a[i] = v (overwrite); needs 0 <= i < n, else throws out_of_range
    void pointAssign(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointAssign: needs 0 <= i < n");
        A[i] += S(v) - pointGet(i);
    }

    // a[i] = max(a[i], v); needs 0 <= i < n, else throws out_of_range
    void pointChmax(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointChmax: needs 0 <= i < n");
        S current = pointGet(i);
        if (S(v) > current) A[i] += S(v) - current;
    }

    // a[i] = min(a[i], v); needs 0 <= i < n, else throws out_of_range
    void pointChmin(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointChmin: needs 0 <= i < n");
        S current = pointGet(i);
        if (S(v) < current) A[i] += S(v) - current;
    }

    // the whole array
    vector<S> getAll() const {
        vector<S> out(n);
        for (int i = 0; i < n; i++) out[i] = pointGet(i);
        return out;
    }

    // ---- internals ----

    int listIndex(int step, int i) const { return offsets[step * (step - 1) / 2 + i % step] + i / step; }

    void addDiff(int step, int index, S v) {
        S* tree = diffs.data() + (size_t)(step - 1) * (n + 2);
        for (int node = index + 1; node <= n + 1; node += node & -node) tree[node] += v;
    }
};
