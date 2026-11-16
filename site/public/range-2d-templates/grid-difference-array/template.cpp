// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries-2d/grid-difference-array/template.cpp
#include <bits/stdc++.h>
using namespace std;
// @operations: getAll rectAdd
// @data-structure-type: difference-array
// @input: grid
// @complexities:
//   getAll: R*C
//   rectAdd: 1
//   build: R*C
// @memory:
//   layout: none
//   node: diff[1*R*C]
//   tags: none
//   other: base[1*R*C]
//   note: diff is (R + 1) by (C + 1), flat: each rectAdd writes its four corners

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

// 2D difference array: rectangle adds in O(1) each, then one O(R * C) pass (getAll) that turns them into the final
// grid. For when every update comes before any read: there are no queries in between (a Fenwick tree does rectAdd
// with pointGet in between at O(log R * log C) each). An add of v on rows r1..r2, columns c1..c2 marks +v at (r1, c1)
// and (r2 + 1, c2 + 1), and -v at (r1, c2 + 1) and (r2 + 1, c1); the 2D prefix sum of the marks is what every cell
// gained. Rows and columns are 0-based and rectangles are inclusive.
// T is any number type (int, long long, ...).
template <typename T>
struct DifferenceArray2D {
    int R, C, W;
    HotVector<vector<T>> base;
    HotVector<T> diff;

    // O(R*C) -- grid: R rows of C numbers each (the starting values); needs R >= 1 and C >= 1, else throws
    // invalid_argument
    explicit DifferenceArray2D(const vector<vector<T>>& grid)
        : R((int)grid.size()), C(grid.empty() ? 0 : (int)grid[0].size()), W(C + 1), base(grid) {
        if (R < 1 || C < 1) throw invalid_argument("DifferenceArray2D: needs R >= 1 and C >= 1");
        for (auto& row : grid)
            if ((int)row.size() != C) throw invalid_argument("DifferenceArray2D: every row needs the same C values");
        diff.assign((size_t)(R + 1) * W, 0);
    }

    // O(1) -- adds v to every cell of rows r1..r2, columns c1..c2; needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C,
    // else throws out_of_range
    LEETCODE_NO_SANITIZE void rectAdd(int r1, int c1, int r2, int c2, T v) {
        if (r1 < 0 || r1 > r2 || r2 >= R || c1 < 0 || c1 > c2 || c2 >= C)
            throw out_of_range("rectAdd: needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C");
        diff[r1 * W + c1] += v;
        diff[r1 * W + c2 + 1] -= v;
        diff[(r2 + 1) * W + c1] -= v;
        diff[(r2 + 1) * W + c2 + 1] += v;
    }

    // O(R*C) -- the whole grid as it stands (R rows of C values); more rectAdd calls can follow
    vector<vector<T>> getAll() const {
        vector<vector<T>> out(R, vector<T>(C));
        vector<T> above(C, 0);
        for (int r = 0; r < R; r++) {
            T run = 0;
            for (int c = 0; c < C; c++) {
                run += diff[r * W + c];
                above[c] += run;
                out[r][c] = above[c] + base[r][c];
            }
        }
        return out;
    }
};
