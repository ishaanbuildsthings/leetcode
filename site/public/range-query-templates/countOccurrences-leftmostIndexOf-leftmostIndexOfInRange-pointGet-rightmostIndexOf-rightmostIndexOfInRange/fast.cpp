// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/countOccurrences-leftmostIndexOf-leftmostIndexOfInRange-pointGet-rightmostIndexOf-rightmostIndexOfInRange/fast.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: countOccurrences leftmostIndexOf leftmostIndexOfInRange pointGet rightmostIndexOf rightmostIndexOfInRange
// @data-structure-type: positions
// @letters: same
// @complexities:
//   countOccurrences: log(N)
//   leftmostIndexOf: log(N)
//   leftmostIndexOfInRange: log(N)
//   pointGet: 1
//   rightmostIndexOf: log(N)
//   rightmostIndexOfInRange: log(N)
//   build: N*log(N)
// @memory:
//   layout: none
//   node: pos[1*N]
//   tags: none
//   other: arr[1*N]
//   note: pos maps each value to the sorted list of indices holding it; the build sorts the (value, index) pairs, O(N log N)

// Static "how many times does x appear in a[l..r]?". All indices 0-based, ranges inclusive. T: any type with <.
// All (value, index) pairs sorted once; x's occurrences in [l, r] are one contiguous run, found by two binary searches.
// FAST MODE drawbacks compared with template.cpp:
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
struct OccurrenceLists {
    HotVector<T> arr;
    HotVector<pair<T, int>> pos;  // (value, index), sorted

    // O(N log N)
    explicit OccurrenceLists(const vector<T>& a) : arr(a), pos(a.size()) {
        for (int i = 0; i < (int)a.size(); i++) pos[i] = {a[i], i};
        sort(pos.begin(), pos.end());
    }

    // O(logN) -- # of i in [l, r] with a[i] == x; needs 0 <= l <= r < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE int countOccurrences(int l, int r, const T& x) const {
        if (l < 0 || l > r || r >= size()) throw out_of_range("countOccurrences: needs 0 <= l <= r < size()");
        if (l > r) return 0;
        return int(lower_bound(pos.begin(), pos.end(), pair<T, int>{x, r + 1}) - lower_bound(pos.begin(), pos.end(), pair<T, int>{x, l}));
    }

    // O(logN) -- the smallest i with a[i] == x, or -1 if x isn't in the array
    LEETCODE_NO_SANITIZE int leftmostIndexOf(const T& x) const { return leftmostIndexOfInRange(0, (int)arr.size() - 1, x); }

    // O(logN) -- the largest i with a[i] == x, or -1 if x isn't in the array
    LEETCODE_NO_SANITIZE int rightmostIndexOf(const T& x) const { return rightmostIndexOfInRange(0, (int)arr.size() - 1, x); }

    // O(logN) -- the smallest i in [l, r] with a[i] == x, or -1 if there is none; needs 0 <= l <= r < size(), else
    // throws out_of_range
    LEETCODE_NO_SANITIZE int leftmostIndexOfInRange(int l, int r, const T& x) const {
        if (l < 0 || l > r || r >= size()) throw out_of_range("leftmostIndexOfInRange: needs 0 <= l <= r < size()");
        auto it = lower_bound(pos.begin(), pos.end(), pair<T, int>{x, l});
        return it != pos.end() && it->first == x && it->second <= r ? it->second : -1;
    }

    // O(logN) -- the largest i in [l, r] with a[i] == x, or -1 if there is none; needs 0 <= l <= r < size(), else
    // throws out_of_range
    LEETCODE_NO_SANITIZE int rightmostIndexOfInRange(int l, int r, const T& x) const {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rightmostIndexOfInRange: needs 0 <= l <= r < size()");
        auto it = lower_bound(pos.begin(), pos.end(), pair<T, int>{x, r + 1});
        if (it == pos.begin()) return -1;
        --it;
        return it->first == x && it->second >= l ? it->second : -1;
    }

    // O(1) -- the length of the array
    LEETCODE_NO_SANITIZE int size() const { return (int)arr.size(); }

    // O(1) -- a[i]; needs 0 <= i < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE T pointGet(int i) const {
        if (i < 0 || i >= size()) throw out_of_range("pointGet: needs 0 <= i < size()");
        return arr[i];
    }
};
