// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries-2d/grid-corner-table-max-ltegte/template.cpp
#include <bits/stdc++.h>
using namespace std;
// @operations: maxAll maxLteGte
// @data-structure-type: corner-table
// @input: grid
// @complexities:
//   maxAll: 1
//   maxLteGte: 1
//   build: R*C
// @memory:
//   layout: none
//   node: tLteGte[1*R*C]
//   tags: none
//   other: none
//   note: one R by C table per corner direction, flat

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

// min / max that still inline with sanitizers skipped (std::min and std::max do not)
template <typename A>
LEETCODE_NO_SANITIZE_INLINE A hotMax(A a, A b) { return a < b ? b : a; }

// Static corner max: the max over a corner of the grid (every cell with row <= r or >= r, and column <= c or >= c) in
// O(1), from one R x C table per direction filled in a single pass (a cell's corner is its own row's running max
// joined with the corner of the cell one row back). No updates. Rows and columns are 0-based.
// T is any type with < (int, long long, double, ...).
template <typename T>
struct CornerMaxTable2D {
    int R, C;
    T best;
    HotVector<T> tLteGte;

    // O(R*C) -- grid: R rows of C numbers each; needs R >= 1 and C >= 1, else throws invalid_argument
    explicit CornerMaxTable2D(const vector<vector<T>>& grid)
        : R((int)grid.size()), C(grid.empty() ? 0 : (int)grid[0].size()) {
        if (R < 1 || C < 1) throw invalid_argument("CornerMaxTable2D: needs R >= 1 and C >= 1");
        for (auto& row : grid)
            if ((int)row.size() != C) throw invalid_argument("CornerMaxTable2D: every row needs the same C values");
        best = grid[0][0];
        for (auto& row : grid)
            for (const T& v : row) best = hotMax(best, v);
        tLteGte.resize((size_t)R * C);
        for (int r = 0; r < R; r++) {
            T run = grid[r][C - 1];
            bool hasBack = r > 0;
            size_t at = (size_t)r * C, back = at - C;
            for (int c = C - 1; c >= 0; c--) {
                run = hotMax(run, grid[r][c]);
                tLteGte[at + c] = hasBack ? hotMax(run, tLteGte[back + c]) : run;
            }
        }
    }

    // O(1) -- max of the cells with row <= r and column >= c; needs 0 <= r < R and 0 <= c < C, else throws out_of_range
    LEETCODE_NO_SANITIZE T maxLteGte(int r, int c) const {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("maxLteGte: needs 0 <= r < R and 0 <= c < C");
        return tLteGte[(size_t)r * C + c];
    }

    // O(1) -- max of the whole grid
    LEETCODE_NO_SANITIZE T maxAll() const {
        return best;
    }
};
