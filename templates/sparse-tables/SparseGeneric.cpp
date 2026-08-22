// TEMPLATE BY ISHAAN AGRAWAL: https://github.com/ishaanbuildsthings
//
// EXAMPLE
//   SparseTable<int> st(nums, [](int a, int b){ return min(a, b); });
//   int m = st.query(l, r);                       // inclusive [l, r]
//
//   // want the position too? feed a mapped array of pairs:
//   vector<pair<int,int>> vi(n);
//   for (int i = 0; i < n; i++) vi[i] = {nums[i], i};
//   SparseTable<pair<int,int>> st2(vi, [](auto a, auto b){ return min(a, b); });
//   auto [val, idx] = st2.query(l, r);            // leftmost min on ties
//
// Static array, no updates. Build O(n log n) time and memory; query is two
// table lookups plus one combineFn call, so O(1) for cheap ops.
//
// COMBINEFN MUST BE IDEMPOTENT: f(a, a) == a. The query overlaps two windows
// that cover [l, r] between them, so anything counted twice is wrong. Min, max,
// gcd, bitwise and/or, and (value, index) pairs under min/max are all fine.
// SUM IS NOT -- use a prefix-sum array or a Fenwick for that.
//
// T can be any copyable type: int, long long, pair, or a small struct with its
// own merge. Elements are stored by value, so keep T small.
#include <bits/stdc++.h>
using namespace std;
template <typename T>
class SparseTable {
public:
    // O(n log n) -- combineFn must be idempotent and associative
    SparseTable(const vector<T>& nums, function<T(T, T)> combineFn)
        : combineFn(combineFn) {
        int n = (int)nums.size();
        log2v.assign(n + 1, 0);
        for (int i = 2; i <= n; i++) log2v[i] = log2v[i >> 1] + 1;
        if (n == 0) return;
        int levels = log2v[n] + 1;
        sparse.assign(levels, vector<T>());
        sparse[0] = nums;
        for (int lvl = 1; lvl < levels; lvl++) {
            int half = 1 << (lvl - 1);
            int limit = n - (1 << lvl) + 1;
            sparse[lvl].resize(limit);
            for (int left = 0; left < limit; left++)
                sparse[lvl][left] = combineFn(sparse[lvl - 1][left],
                                              sparse[lvl - 1][left + half]);
        }
    }
    // O(combineFn) -- combine over the inclusive range [l, r].
    // Caller must ensure 0 <= l <= r < n; there is no identity element to
    // return for an empty range.
    T query(int l, int r) const {
        assert(0 <= l && l <= r && r < (int)sparse[0].size());
        int power = log2v[r - l + 1];
        int windowWidth = 1 << power;
        return combineFn(sparse[power][l], sparse[power][r - windowWidth + 1]);
    }
private:
    vector<vector<T>> sparse;
    vector<int> log2v;
    function<T(T, T)> combineFn;
};