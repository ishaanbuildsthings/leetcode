// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries-2d/grid-prefix-sum/template.cpp
#include <bits/stdc++.h>
using namespace std;
// @operations: pointGet rectSum sumAll
// @data-structure-type: prefix-sum
// @input: grid
// @complexities:
//   pointGet: 1
//   rectSum: 1
//   sumAll: 1
//   build: R*C
// @memory:
//   layout: none
//   node: sm[1*R*C]
//   tags: none
//   other: none
//   note: each table is (R + 1) by (C + 1), flat: entry [r][c] covers the rows above r and the columns left of c

// Sanitizers are skipped inside this template (its methods start with LEETCODE_NO_SANITIZE): where they run, like on
// LeetCode, that is most of its speed. The drawback: a bad memory access inside the template goes unreported. Arguments
// are still checked and still throw. Constructors are left alone. It needs GCC or Clang and C++17.

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
    LEETCODE_NO_SANITIZE_INLINE typename vector<U>::const_reference operator[](size_t i) const {
        return this->_M_impl._M_start[i];
    }
    LEETCODE_NO_SANITIZE_INLINE size_t size() const { return size_t(this->_M_impl._M_finish - this->_M_impl._M_start); }
#endif
};

// Static 2D prefix sums: any rectangle in O(1) from four table entries (the big corner, minus the strip above, minus
// the strip to the left, plus the corner both took off). No updates. Rows and columns are 0-based and rectangles are
// inclusive: rows r1..r2, columns c1..c2.
// T is any integer type (int, long long, ...); sums are kept in S (long long for a smaller T).
template <typename T>
struct PrefixSums2D {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    int R, C, W;
    HotVector<S> sm;

    // O(R*C) -- grid: R rows of C numbers each; needs R >= 1 and C >= 1, else throws invalid_argument
    explicit PrefixSums2D(const vector<vector<T>>& grid)
        : R((int)grid.size()), C(grid.empty() ? 0 : (int)grid[0].size()), W(C + 1) {
        if (R < 1 || C < 1) throw invalid_argument("PrefixSums2D: needs R >= 1 and C >= 1");
        for (auto& row : grid)
            if ((int)row.size() != C) throw invalid_argument("PrefixSums2D: every row needs the same C values");
        sm.assign((size_t)(R + 1) * W, 0);
        for (int r = 0; r < R; r++) {
            int up = r * W, at = up + W;
            S runSum = 0;
            for (int c = 0; c < C; c++) {
                runSum += grid[r][c];
                sm[at + c + 1] = sm[up + c + 1] + runSum;
            }
        }
    }

    // O(1) -- sum of rows r1..r2, columns c1..c2; needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C, else throws
    // out_of_range
    LEETCODE_NO_SANITIZE S rectSum(int r1, int c1, int r2, int c2) const {
        if (r1 < 0 || r1 > r2 || r2 >= R || c1 < 0 || c1 > c2 || c2 >= C)
            throw out_of_range("rectSum: needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C");
        int top = r1 * W, bot = (r2 + 1) * W;
        return sm[bot + c2 + 1] - sm[top + c2 + 1] - sm[bot + c1] + sm[top + c1];
    }

    // O(1) -- sum of the whole grid
    LEETCODE_NO_SANITIZE S sumAll() const {
        return sm.back();
    }

    // O(1) -- the value at (r, c); needs 0 <= r < R and 0 <= c < C, else throws out_of_range
    LEETCODE_NO_SANITIZE T pointGet(int r, int c) const {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("pointGet: needs 0 <= r < R and 0 <= c < C");
        int top = r * W, bot = top + W;
        return T(sm[bot + c + 1] - sm[top + c + 1] - sm[bot + c] + sm[top + c]);
    }
};
