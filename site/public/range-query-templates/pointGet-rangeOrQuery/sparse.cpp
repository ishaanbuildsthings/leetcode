// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/pointGet-rangeOrQuery/sparse.cpp
// @operations: pointGet rangeOrQuery
// @data-structure-type: sparse-table
// @complexities:
//   pointGet: log(N)
//   rangeOrQuery: log(N)
//   build: N*log(N)
// @memory:
//   layout: sparse
//   node: sparse[2*N*log(N)]
//   tags: none
//   other: idx[1*N] vals[1*N] starts[2*N]
//   note: built from N (index, value) points over any index range [lo, hi], every other index 0; the sparse table runs on the points plus one 0 per gap (at most 2N + 1 elements)
// Static rangeOrQuery: sparse table, overlapping power-of-two windows. All indices 0-based, ranges inclusive.
// T is any integral type (int, long long, ...).
template <typename T>
struct SparseOr {
    int n;
    vector<vector<T>> sp;  // sp[k][i] = combine of a[i .. i + 2^k - 1]

    static T combine(T a, T b) { return a | b; }

    // O(N log N)
    explicit SparseOr(const vector<T>& a) : n((int)a.size()) {
        int levels = n ? 32 - __builtin_clz(n) : 1;
        sp.assign(levels, vector<T>());
        sp[0] = a;
        for (int k = 1; k < levels; k++) {
            int half = 1 << (k - 1), len = n - (1 << k) + 1;
            sp[k].resize(max(len, 0));
            for (int i = 0; i < len; i++) sp[k][i] = combine(sp[k - 1][i], sp[k - 1][i + half]);
        }
    }

    // O(1) -- a[l] | ... | a[r]
    T rangeOrQuery(int l, int r) const {
        int k = 31 - __builtin_clz(r - l + 1);
        return combine(sp[k][l], sp[k][r - (1 << k) + 1]);
    }

    // O(1) -- a[i]
    T pointGet(int i) const { return sp[0][i]; }
};

// ======================================================================================== sparse wrapper

// Range or over any index range [lo, hi], built from (index, value) points; every other index is 0. A maximal gap
// of zeros adds nothing more than a single 0, so SparseOr runs on the compressed array of points with one 0 per gap,
// and a query maps l and r to the compressed elements containing them.
template <typename T>
struct SparseStaticOr {
    long long lo, hi;
    vector<long long> idx, starts;  // point indices; starts[k] = first index of compressed element k
    vector<T> vals;
    SparseOr<T> inner;

    // O(N log N) -- [lo, hi] all 0 except the given (index, value) points (distinct indices)
    SparseStaticOr(long long lo, long long hi, vector<pair<long long, T>> points) : lo(lo), hi(hi), inner(compress(points)) {}

    vector<T> compress(vector<pair<long long, T>>& pts) {
        sort(pts.begin(), pts.end());
        vector<T> arr;
        long long prev = lo - 1;
        for (auto& [i, v] : pts) {
            if (i > prev + 1) starts.push_back(prev + 1), arr.push_back(T(0));
            starts.push_back(i), arr.push_back(v);
            idx.push_back(i), vals.push_back(v);
            prev = i;
        }
        if (prev < hi) starts.push_back(prev + 1), arr.push_back(T(0));
        return arr;
    }

    int element(long long i) const { return int(upper_bound(starts.begin(), starts.end(), i) - starts.begin()) - 1; }

    // O(logN) -- range or of a[l..r]
    T rangeOrQuery(long long l, long long r) const { return inner.rangeOrQuery(element(l), element(r)); }

    // O(logN) -- a[i]
    T pointGet(long long i) const {
        auto it = lower_bound(idx.begin(), idx.end(), i);
        return it != idx.end() && *it == i ? vals[it - idx.begin()] : T(0);
    }
};
