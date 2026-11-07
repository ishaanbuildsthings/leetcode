// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/manacher-palindromes/fast.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: getAll isPalindrome longestPalCenteredAtI longestPalCenteredAtIPlusOne pointGet
// @data-structure-type: manacher
// @letters: same
// @complexities:
//   getAll: N
//   isPalindrome: 1
//   longestPalCenteredAtI: 1
//   longestPalCenteredAtIPlusOne: 1
//   pointGet: 1
//   build: N
// @memory:
//   layout: none
//   node: odd[1*N] even[1*N]
//   tags: none
//   other: A[1*N]
//   note: odd[i] = how far the palindrome centred on a[i] reaches (its radius, counting a[i]), even[i] = how many pairs the one centred between a[i-1] and a[i] has; Manacher's reuse of the mirrored centre inside the rightmost palindrome makes the build linear

// Manacher's algorithm over a static array: the radius of the longest palindrome around every centre (on a value, and
// between two values), built in O(N), so the longest palindrome around a centre and any palindrome check are O(1)
// with no hashing. Values are numbers or single characters. All indices 0-based, ranges inclusive.
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
struct Manacher {
    int n;
    HotVector<T> A;
    HotVector<int> odd;  // odd[i]: the largest k with a[i-k+1..i+k-1] a palindrome (so at least 1)
    HotVector<int> even;  // even[i]: the largest k with a[i-k..i+k-1] a palindrome (the centre is between a[i-1] and a[i]; 0 when none)

    // O(N) -- arr: the array (non-empty); T: int, long long, char, ...
    explicit Manacher(const vector<T>& arr) : n((int)arr.size()), A(arr), odd(n, 0), even(n, 0) {
        for (int i = 0, l = 0, r = -1; i < n; i++) {
            int k = i > r ? 1 : min(odd[l + r - i], r - i + 1);
            while (0 <= i - k && i + k < n && A[i - k] == A[i + k]) k++;
            odd[i] = k;
            if (i + k - 1 > r) l = i - k + 1, r = i + k - 1;
        }
        for (int i = 0, l = 0, r = -1; i < n; i++) {
            int k = i > r ? 0 : min(even[l + r - i + 1], r - i + 1);
            while (0 <= i - k - 1 && i + k < n && A[i - k - 1] == A[i + k]) k++;
            even[i] = k;
            if (i + k - 1 > r) l = i - k, r = i + k - 1;
        }
    }

    // O(N) -- the whole array
    LEETCODE_NO_SANITIZE vector<T> getAll() const { return A; }

    // O(1) -- a[i]; needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE T pointGet(int i) const {
        if (i < 0 || i >= n) throw out_of_range("pointGet: needs 0 <= i < n");
        return A[i];
    }

    // O(1) -- is a[l..r] a palindrome; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE bool isPalindrome(int l, int r) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("isPalindrome: needs 0 <= l <= r < n");
        int m = r - l + 1;
        if (m & 1) return odd[(l + r) / 2] >= (m + 1) / 2;
        return even[(l + r + 1) / 2] >= m / 2;
    }

    // O(1) -- (l, r) of the longest odd palindrome a[l..r] centred on a[i] (at least (i, i)); needs 0 <= i < n, else
    // throws out_of_range
    LEETCODE_NO_SANITIZE pair<int, int> longestPalCenteredAtI(int i) const {
        if (i < 0 || i >= n) throw out_of_range("longestPalCenteredAtI: needs 0 <= i < n");
        int k = odd[i] - 1;
        return {i - k, i + k};
    }

    // O(1) -- (l, r) of the longest even palindrome a[l..r] centred between a[i] and a[i+1]; (i + 1, i), the empty range,
    // when there is none (so also for i = n - 1); needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE pair<int, int> longestPalCenteredAtIPlusOne(int i) const {
        if (i < 0 || i >= n) throw out_of_range("longestPalCenteredAtIPlusOne: needs 0 <= i < n");
        int k = i + 1 < n ? even[i + 1] : 0;
        return {i - k + 1, i + k};
    }
};
