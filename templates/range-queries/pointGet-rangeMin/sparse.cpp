// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/pointGet-rangeMin/sparse.cpp
// @operations: pointGet rangeMin
// @data-structure-type: sparse-table
// @complexities:
//   pointGet: log(N)
//   rangeMin: log(N)
//   build: N*log(N)
// @memory:
//   layout: sparse
//   node: sparse[2*N*log(N)]
//   tags: none
//   other: idx[1*N] vals[1*N] starts[2*N]
//   note: built from N given values (index, value pairs) over any index range [lo, hi], every other index 0; costs are in N; the sparse table runs on the given values plus one 0 per gap (at most 2N + 1 elements)
// Static rangeMin: sparse table, overlapping power-of-two windows. All indices 0-based, ranges inclusive.
// T is any integral type (int, long long, ...).
template <typename T>
struct SparseMin {
    int n;
    vector<vector<T>> sp;  // sp[k][i] = combine of a[i .. i + 2^k - 1]

    static T combine(T a, T b) { return a < b ? a : b; }

    // O(N log N)
    explicit SparseMin(const vector<T>& a) : n((int)a.size()) {
        int levels = n ? 32 - __builtin_clz(n) : 1;
        sp.assign(levels, vector<T>());
        sp[0] = a;
        for (int k = 1; k < levels; k++) {
            int half = 1 << (k - 1), len = n - (1 << k) + 1;
            sp[k].resize(max(len, 0));
            for (int i = 0; i < len; i++) sp[k][i] = combine(sp[k - 1][i], sp[k - 1][i + half]);
        }
    }

    // O(1) -- min of a[l..r]
    T rangeMin(int l, int r) const {
        int k = 31 - __builtin_clz(r - l + 1);
        return combine(sp[k][l], sp[k][r - (1 << k) + 1]);
    }

    // O(1) -- a[i]
    T pointGet(int i) const { return sp[0][i]; }
};

// ======================================================================================== sparse wrapper

// Range min over any index range [lo, hi], built from given values (index, value pairs); every other index is 0. A maximal gap
// of zeros adds nothing more than a single 0, so SparseMin runs on the compressed array of given values with one 0 per gap,
// and a query maps l and r to the compressed elements containing them.
template <typename T>
struct SparseStaticMin {
    long long lo, hi;
    vector<long long> idx, starts;  // given value indices; starts[k] = first index of compressed element k
    vector<T> vals;
    SparseMin<T> inner;

    // O(N log N) -- [lo, hi] all 0 except the given values: (index, value) pairs with distinct indices; N = len(values)
    SparseStaticMin(long long lo, long long hi, vector<pair<long long, T>> values) : lo(lo), hi(hi), inner(compress(values)) {}

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

    // O(logN) -- range min of a[l..r]
    T rangeMin(long long l, long long r) const { return inner.rangeMin(element(l), element(r)); }

    // O(logN) -- a[i]
    T pointGet(long long i) const {
        auto it = lower_bound(idx.begin(), idx.end(), i);
        return it != idx.end() && *it == i ? vals[it - idx.begin()] : T(0);
    }
};
