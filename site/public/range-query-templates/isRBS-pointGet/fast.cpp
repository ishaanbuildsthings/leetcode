// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/isRBS-pointGet/fast.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: isRBS pointGet
// @data-structure-type: sparse-table
// @letters: same
// @complexities:
//   isRBS: 1
//   pointGet: 1
//   build: N*log(N)
// @memory:
//   layout: none
//   node: table[1*N*log(N)]
//   tags: none
//   other: P[1*N] s[1*N]
//   note: P: prefix sums; the table holds P's minimums over every power-of-two window

// Static bracket sequence: isRBS(l, r) asks whether s[l..r] is a regular (balanced) bracket sequence, in O(1).
// With open = +1 and anything else = -1, s[l..r] is regular iff its total is 0 and no prefix of it dips below 0. With
// prefix sums P (P[0] = 0, P[i + 1] = P[i] + s[i]) that is P[r + 1] == P[l] and min(P[l + 1..r + 1]) >= P[l]: a sparse
// table answers the min in O(1). All indices 0-based, ranges inclusive. The values are the characters themselves.
// T: char (or any type: openChar is the one that opens).
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
struct StaticBrackets {
    HotVector<T> s;
    HotVector<int> P;              // prefix sums of +-1
    HotVector<vector<int>> table;  // table[k][i] = min(P[i .. i + 2^k - 1])

    // O(N log N) -- brackets: the sequence, e.g. vector<char>(str.begin(), str.end()); openChar: the character that
    // opens ('(' unless you pass e.g. '['); every other character closes
    explicit StaticBrackets(const vector<T>& brackets, T openChar = T('(')) : s(brackets), P(brackets.size() + 1, 0) {
        int n = (int)brackets.size();
        for (int i = 0; i < n; i++) P[i + 1] = P[i] + (brackets[i] == openChar ? 1 : -1);
        table.push_back(P);
        for (int k = 1; 2 * k <= n + 1; k *= 2) {
            const vector<int>& prev = table.back();
            vector<int> cur(prev.size() - k);
            for (size_t i = 0; i < cur.size(); i++) cur[i] = min(prev[i], prev[i + k]);
            table.push_back(std::move(cur));
        }
    }

    // O(1) -- the length of the array
    LEETCODE_NO_SANITIZE int size() const { return (int)s.size(); }

    // O(1) -- brackets[i]; needs 0 <= i < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE T pointGet(int i) const {
        if (i < 0 || i >= size()) throw out_of_range("pointGet: needs 0 <= i < size()");
        return s[i];
    }

    // O(1) -- is brackets[l..r] a regular bracket sequence (balanced, never closing more than it opened)?; needs
    // 0 <= l <= r < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE bool isRBS(int l, int r) const {
        if (l < 0 || l > r || r >= size()) throw out_of_range("isRBS: needs 0 <= l <= r < size()");
        if (P[r + 1] != P[l]) return false;
        int lo = l + 1, hi = r + 1, k = 31 - __builtin_clz(hi - lo + 1);
        return min(table[k][lo], table[k][hi - (1 << k) + 1]) >= P[l];
    }
};
