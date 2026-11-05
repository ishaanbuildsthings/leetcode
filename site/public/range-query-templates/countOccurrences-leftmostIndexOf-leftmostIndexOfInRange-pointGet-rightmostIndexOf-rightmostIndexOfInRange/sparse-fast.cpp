// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/countOccurrences-leftmostIndexOf-leftmostIndexOfInRange-pointGet-rightmostIndexOf-rightmostIndexOfInRange/sparse-fast.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: countOccurrences leftmostIndexOf leftmostIndexOfInRange pointGet rightmostIndexOf rightmostIndexOfInRange
// @data-structure-type: positions
// @complexities:
//   countOccurrences: log(N)
//   leftmostIndexOf: log(N)
//   leftmostIndexOfInRange: log(N)
//   pointGet: log(N)
//   rightmostIndexOf: log(N)
//   rightmostIndexOfInRange: log(N)
//   build: N*log(N)
// @memory:
//   layout: sparse
//   node: pos[1*N]
//   tags: none
//   other: idx[1*N] vals[1*N]
//   note: built from N given values (index, value pairs) over any index range [lo, hi], every other index 0; costs are in N; pos maps each value to its sorted indices; 0 also counts the zeros of [l, r] (its length minus the given values inside)

// "How many times does x appear in a[l..r]?" and "where is x's first / last copy (in a[l..r])?" over any index range
// [lo, hi], built from given values (index, value pairs); every other index is 0. Each value keeps its sorted indices;
// x == 0 also counts the zeros of [l, r] (its length minus the given values inside), and its first / last copy may be
// an index nobody gave: the end of a run of consecutive given indices, found by a binary search on idx[k] - k.
// T: any type usable as a std::map key.
// FAST MODE drawbacks compared with sparse.cpp:
//   - sanitizers are skipped inside this template, so a bad access in it goes unreported
// Same public operations and answers, same limits; it needs GCC or Clang and C++17.
#ifdef __SSE2__
#include <immintrin.h>
#endif

// LEETCODE_NO_SANITIZE skips sanitizers in a function. It only changes anything where sanitizers run, like LeetCode: on
// Codeforces it compiles and does nothing.
// This template already uses it. To go further, put it on the one function with your hot loop:
//   LEETCODE_NO_SANITIZE long long maxSum(vector<int>& nums, int k) {
// A lambda needs its own: [&](int x) LEETCODE_NO_SANITIZE { ... }. It does not carry into anything that function calls.
// Inside a marked function use raw pointers and plain comparisons, not vector[] and min / max, or it can get slower.
// Bad memory accesses in a marked function go unreported.
#ifndef LEETCODE_NO_SANITIZE
#define LEETCODE_NO_SANITIZE __attribute__((no_sanitize("address"), no_sanitize("undefined")))
#endif
#define LEETCODE_NO_SANITIZE_INLINE LEETCODE_NO_SANITIZE __attribute__((always_inline)) inline

// A vector whose [] and size() always inline, even with sanitizers skipped (libstdc++ only; elsewhere a plain vector)
template <typename U>
struct HotVector : vector<U> {
    using vector<U>::vector;
    HotVector() = default;
    HotVector(const vector<U>& other) : vector<U>(other) {}
    HotVector(vector<U>&& other) : vector<U>(move(other)) {}
#ifdef __GLIBCXX__
    LEETCODE_NO_SANITIZE_INLINE typename vector<U>::reference operator[](size_t i) { return this->_M_impl._M_start[i]; }
    LEETCODE_NO_SANITIZE_INLINE typename vector<U>::const_reference operator[](size_t i) const { return this->_M_impl._M_start[i]; }
    LEETCODE_NO_SANITIZE_INLINE size_t size() const { return size_t(this->_M_impl._M_finish - this->_M_impl._M_start); }
#endif
};

template <typename T>
struct SparseStaticOccurrences {
    long long lo, hi;
    HotVector<long long> idx;
    HotVector<T> vals;
    map<T, vector<long long>> pos;

    // O(N log N) -- [lo, hi] all 0 except the given values: (index, value) pairs with distinct indices; N = len(values)
    SparseStaticOccurrences(long long lo, long long hi, vector<pair<long long, T>> values) : lo(lo), hi(hi) {
        sort(values.begin(), values.end());
        for (auto& [i, v] : values) idx.push_back(i), vals.push_back(v), pos[v].push_back(i);
    }

    LEETCODE_NO_SANITIZE static long long countIn(const vector<long long>& p, long long l, long long r) {
        return (long long)(upper_bound(p.begin(), p.end(), r) - lower_bound(p.begin(), p.end(), l));
    }

    // O(logN) -- # of i in [l, r] with a[i] == x; needs lo <= l <= r <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE long long countOccurrences(long long l, long long r, const T& x) const {
        if (l < lo || l > r || r > hi) throw out_of_range("countOccurrences: needs lo <= l <= r <= hi");
        if (l > r) return 0;
        auto it = pos.find(x);
        long long res = it == pos.end() ? 0 : countIn(it->second, l, r);
        if (x == T(0)) res += (r - l + 1) - countIn(idx, l, r);
        return res;
    }

    // O(logN) -- the smallest i in [lo, hi] with a[i] == x, or lo - 1 if there is none
    LEETCODE_NO_SANITIZE long long leftmostIndexOf(const T& x) const { return leftmostIndexOfInRange(lo, hi, x); }

    // O(logN) -- the largest i in [lo, hi] with a[i] == x, or lo - 1 if there is none
    LEETCODE_NO_SANITIZE long long rightmostIndexOf(const T& x) const { return rightmostIndexOfInRange(lo, hi, x); }

    // O(logN) -- the smallest i in [l, r] with a[i] == x, or lo - 1 if there is none; needs lo <= l <= r <= hi, else
    // throws out_of_range
    LEETCODE_NO_SANITIZE long long leftmostIndexOfInRange(long long l, long long r, const T& x) const {
        if (l < lo || l > r || r > hi) throw out_of_range("leftmostIndexOfInRange: needs lo <= l <= r <= hi");
        long long best = r + 1;
        auto it = pos.find(x);
        if (it != pos.end()) {
            auto j = lower_bound(it->second.begin(), it->second.end(), l);
            if (j != it->second.end()) best = *j;
        }
        if (x == T(0)) best = min(best, firstGap(l));
        return best <= r ? best : lo - 1;
    }

    // O(logN) -- the largest i in [l, r] with a[i] == x, or lo - 1 if there is none; needs lo <= l <= r <= hi, else
    // throws out_of_range
    LEETCODE_NO_SANITIZE long long rightmostIndexOfInRange(long long l, long long r, const T& x) const {
        if (l < lo || l > r || r > hi) throw out_of_range("rightmostIndexOfInRange: needs lo <= l <= r <= hi");
        long long best = l - 1;
        auto it = pos.find(x);
        if (it != pos.end()) {
            auto j = upper_bound(it->second.begin(), it->second.end(), r);
            if (j != it->second.begin()) best = *prev(j);
        }
        if (x == T(0)) best = max(best, lastGap(r));
        return best >= l ? best : lo - 1;
    }

    LEETCODE_NO_SANITIZE long long firstGap(long long i) const {  // the smallest index >= i that wasn't given (it holds 0)
        long long k = lower_bound(idx.begin(), idx.end(), i) - idx.begin();
        if (k == (long long)idx.size() || idx[k] != i) return i;
        long long a = k, b = (long long)idx.size() - 1;  // idx[k..a] = i, i + 1, ...: the largest such a
        while (a < b) {
            long long m = (a + b + 1) / 2;
            if (idx[m] - m == i - k) a = m;
            else b = m - 1;
        }
        return i + (a - k) + 1;
    }

    LEETCODE_NO_SANITIZE long long lastGap(long long i) const {  // the largest index <= i that wasn't given (it holds 0)
        long long k = (upper_bound(idx.begin(), idx.end(), i) - idx.begin()) - 1;
        if (k < 0 || idx[k] != i) return i;
        long long a = 0, b = k;  // idx[a..k] = ..., i - 1, i: the smallest such a
        while (a < b) {
            long long m = (a + b) / 2;
            if (idx[m] - m == i - k) b = m;
            else a = m + 1;
        }
        return i - (k - a) - 1;
    }

    // O(logN) -- a[i]; needs lo <= i <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE T pointGet(long long i) const {
        if (i < lo || i > hi) throw out_of_range("pointGet: needs lo <= i <= hi");
        auto it = lower_bound(idx.begin(), idx.end(), i);
        return it != idx.end() && *it == i ? vals[it - idx.begin()] : T(0);
    }
};
