// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/pointGet-rangeAndQuery/template.cpp
// @operations: pointGet rangeAndQuery
// @data-structure-type: sparse-table
// @complexities:
//   pointGet: 1
//   rangeAndQuery: 1
//   build: N*log(N)
// @memory:
//   layout: none
//   node: sparse[1*N*log(N)]
//   tags: none
//   other: none
//   note: log(N) levels of N values each; level 0 is the array itself
// @original-file-url: https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/sparse-tables/SparseAND.cpp

// Static rangeAndQuery: sparse table, overlapping power-of-two windows. All indices 0-based, ranges inclusive.
// T is any integral type (int, long long, ...).
template <typename T>
struct SparseAnd {
    int n;
    vector<vector<T>> sp;  // sp[k][i] = combine of a[i .. i + 2^k - 1]

    static T combine(T a, T b) { return a & b; }

    // O(N log N)
    explicit SparseAnd(const vector<T>& a) : n((int)a.size()) {
        int levels = n ? 32 - __builtin_clz(n) : 1;
        sp.assign(levels, vector<T>());
        sp[0] = a;
        for (int k = 1; k < levels; k++) {
            int half = 1 << (k - 1), len = n - (1 << k) + 1;
            sp[k].resize(max(len, 0));
            for (int i = 0; i < len; i++) sp[k][i] = combine(sp[k - 1][i], sp[k - 1][i + half]);
        }
    }

    // O(1) -- a[l] & ... & a[r]
    T rangeAndQuery(int l, int r) const {
        int k = 31 - __builtin_clz(r - l + 1);
        return combine(sp[k][l], sp[k][r - (1 << k) + 1]);
    }

    // O(1) -- a[i]
    T pointGet(int i) const { return sp[0][i]; }
};
