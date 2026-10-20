// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/countOccurrences-pointGet/sparse.cpp
// @operations: countOccurrences pointGet
// @data-structure-type: positions
// @complexities:
//   countOccurrences: log(N)
//   pointGet: log(N)
//   build: N*log(N)
// @memory:
//   layout: sparse
//   node: pos[1*N]
//   tags: none
//   other: idx[1*N] vals[1*N]
//   note: built from N (index, value) points over any index range [lo, hi], every other index 0; pos maps each value to its sorted indices; 0 also counts the zeros of [l, r] (its length minus the points inside)

// "How many times does x appear in a[l..r]?" over any index range [lo, hi], built from (index, value) points; every
// other index is 0. Each value keeps its sorted indices; x == 0 also counts the zeros of [l, r] (its length minus the
// points inside). T: any type usable as a std::map key.
template <typename T>
struct SparseStaticOccurrences {
    long long lo, hi;
    vector<long long> idx;
    vector<T> vals;
    map<T, vector<long long>> pos;

    // O(N log N) -- [lo, hi] all 0 except the given (index, value) points (distinct indices)
    SparseStaticOccurrences(long long lo, long long hi, vector<pair<long long, T>> points) : lo(lo), hi(hi) {
        sort(points.begin(), points.end());
        for (auto& [i, v] : points) idx.push_back(i), vals.push_back(v), pos[v].push_back(i);
    }

    static long long countIn(const vector<long long>& p, long long l, long long r) {
        return (long long)(upper_bound(p.begin(), p.end(), r) - lower_bound(p.begin(), p.end(), l));
    }

    // O(logN) -- # of i in [l, r] with a[i] == x
    long long countOccurrences(long long l, long long r, const T& x) const {
        if (l > r) return 0;
        auto it = pos.find(x);
        long long res = it == pos.end() ? 0 : countIn(it->second, l, r);
        if (x == T(0)) res += (r - l + 1) - countIn(idx, l, r);
        return res;
    }

    // O(logN) -- a[i]
    T pointGet(long long i) const {
        auto it = lower_bound(idx.begin(), idx.end(), i);
        return it != idx.end() && *it == i ? vals[it - idx.begin()] : T(0);
    }
};
