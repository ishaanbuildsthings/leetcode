// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries-2d/grid-sparse-table-min-and/template.cpp
#include <bits/stdc++.h>
using namespace std;
// @operations: andAll minAll minGteGte minGteLte minLteGte minLteLte pointGet rectAnd rectMin squareAnd squareMin
// @data-structure-type: sparse-table
// @input: grid
// @complexities:
//   andAll: 1
//   minAll: 1
//   minGteGte: 1
//   minGteLte: 1
//   minLteGte: 1
//   minLteLte: 1
//   pointGet: 1
//   rectAnd: 1
//   rectMin: 1
//   squareAnd: 1
//   squareMin: 1
//   build: R*C*log(R)*log(C)
// @memory:
//   layout: none
//   node: mn[1*R*C*log(R)*log(C)] an[1*R*C*log(R)*log(C)]
//   tags: none
//   other: none
//   note: per aggregate, one table for every pair of a power-of-two height and a power-of-two width (the 1 x 1 table is the grid itself, shared)

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
LEETCODE_NO_SANITIZE_INLINE A hotMin(A a, A b) { return b < a ? b : a; }

// Static 2D sparse table (min, AND): any rectangle in O(1). For every power-of-two height and power-of-two width
// there is a table holding the aggregate of each window of that size; a rectangle is covered by four such windows,
// one in each corner (they overlap, which is fine: each of these gives the same answer when a cell is counted twice).
// Memory and build are R * C * log R * log C: when only squares are asked for, the square sparse table needs a single
// log. No updates. Rows and columns are 0-based and rectangles are inclusive: rows r1..r2, columns c1..c2.
// T is any integer type (int, long long, ...).
template <typename T>
struct SparseTable2D {
    int R, C, levelsR, levelsC;
    HotVector<size_t> at;  // at[kr * levelsC + kc]: where the table of 2^kr rows by 2^kc columns starts in each array
    HotVector<T> mn;  // every table back to back, each flat: (R - 2^kr + 1) rows of (C - 2^kc + 1)
    HotVector<T> an;  // every table back to back, each flat: (R - 2^kr + 1) rows of (C - 2^kc + 1)

    // O(R*C*logR*logC) -- grid: R rows of C numbers each; needs R >= 1 and C >= 1, else throws invalid_argument
    explicit SparseTable2D(const vector<vector<T>>& grid)
        : R((int)grid.size()), C(grid.empty() ? 0 : (int)grid[0].size()) {
        if (R < 1 || C < 1) throw invalid_argument("SparseTable2D: needs R >= 1 and C >= 1");
        for (auto& row : grid)
            if ((int)row.size() != C) throw invalid_argument("SparseTable2D: every row needs the same C values");
        levelsR = 32 - __builtin_clz(R), levelsC = 32 - __builtin_clz(C);
        at.assign((size_t)levelsR * levelsC + 1, 0);
        for (int kr = 0; kr < levelsR; kr++)
            for (int kc = 0; kc < levelsC; kc++)
                at[kr * levelsC + kc + 1] = at[kr * levelsC + kc] + (size_t)(R - (1 << kr) + 1) * (C - (1 << kc) + 1);
        mn.assign(at.back(), T(0));
        for (int r = 0; r < R; r++)
            for (int c = 0; c < C; c++) mn[(size_t)r * C + c] = grid[r][c];
        an.assign(at.back(), T(0));
        for (int r = 0; r < R; r++)
            for (int c = 0; c < C; c++) an[(size_t)r * C + c] = grid[r][c];
        buildLevels();
    }

    // every table from the ones half its size: first the wider ones of single rows, then the taller ones
    LEETCODE_NO_SANITIZE void buildLevels() {
        for (int kc = 1; kc < levelsC; kc++) {
            int half = 1 << (kc - 1), prevW = C - half + 1, w = C - (1 << kc) + 1;
            const T* prev = &mn[at[kc - 1]];
            T* cur = &mn[at[kc]];
            for (int r = 0; r < R; r++)
                for (int c = 0; c < w; c++)
                    cur[(size_t)r * w + c] = hotMin(prev[(size_t)r * prevW + c], prev[(size_t)r * prevW + c + half]);
        }
        for (int kr = 1; kr < levelsR; kr++) {
            int half = 1 << (kr - 1), h = R - (1 << kr) + 1;
            for (int kc = 0; kc < levelsC; kc++) {
                size_t w = C - (1 << kc) + 1, off = half * w, count = h * w;
                const T* prev = &mn[at[(kr - 1) * levelsC + kc]];
                T* cur = &mn[at[kr * levelsC + kc]];
                for (size_t i = 0; i < count; i++) cur[i] = hotMin(prev[i], prev[i + off]);
            }
        }
        for (int kc = 1; kc < levelsC; kc++) {
            int half = 1 << (kc - 1), prevW = C - half + 1, w = C - (1 << kc) + 1;
            const T* prev = &an[at[kc - 1]];
            T* cur = &an[at[kc]];
            for (int r = 0; r < R; r++)
                for (int c = 0; c < w; c++)
                    cur[(size_t)r * w + c] = prev[(size_t)r * prevW + c] & prev[(size_t)r * prevW + c + half];
        }
        for (int kr = 1; kr < levelsR; kr++) {
            int half = 1 << (kr - 1), h = R - (1 << kr) + 1;
            for (int kc = 0; kc < levelsC; kc++) {
                size_t w = C - (1 << kc) + 1, off = half * w, count = h * w;
                const T* prev = &an[at[(kr - 1) * levelsC + kc]];
                T* cur = &an[at[kr * levelsC + kc]];
                for (size_t i = 0; i < count; i++) cur[i] = prev[i] & prev[i + off];
            }
        }
    }

    LEETCODE_NO_SANITIZE T minOf(int r1, int c1, int r2, int c2) const {
        int kr = 31 - __builtin_clz(r2 - r1 + 1), kc = 31 - __builtin_clz(c2 - c1 + 1);
        const T* t = &mn[at[kr * levelsC + kc]];
        int w = C - (1 << kc) + 1, d = c2 - (1 << kc) + 1 - c1;
        size_t i = (size_t)r1 * w + c1, j = (size_t)(r2 - (1 << kr) + 1) * w + c1;
        return hotMin(hotMin(t[i], t[i + d]), hotMin(t[j], t[j + d]));
    }

    // O(1) -- min of rows r1..r2, columns c1..c2; needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C, else throws
    // out_of_range
    LEETCODE_NO_SANITIZE T rectMin(int r1, int c1, int r2, int c2) const {
        if (r1 < 0 || r1 > r2 || r2 >= R || c1 < 0 || c1 > c2 || c2 >= C)
            throw out_of_range("rectMin: needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C");
        return minOf(r1, c1, r2, c2);
    }

    // O(1) -- min of the square with top-left cell (r, c) and that many rows and columns; needs side >= 1 and the
    // square inside the grid, else throws out_of_range
    LEETCODE_NO_SANITIZE T squareMin(int r, int c, int side) const {
        if (side < 1 || r < 0 || r + side > R || c < 0 || c + side > C)
            throw out_of_range("squareMin: needs side >= 1 and the square inside the grid");
        return minOf(r, c, r + side - 1, c + side - 1);
    }

    // O(1) -- min of the whole grid
    LEETCODE_NO_SANITIZE T minAll() const {
        return minOf(0, 0, R - 1, C - 1);
    }

    // O(1) -- min of the cells with row <= r and column <= c; needs 0 <= r < R and 0 <= c < C, else throws out_of_range
    LEETCODE_NO_SANITIZE T minLteLte(int r, int c) const {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("minLteLte: needs 0 <= r < R and 0 <= c < C");
        return minOf(0, 0, r, c);
    }

    // O(1) -- min of the cells with row <= r and column >= c; needs 0 <= r < R and 0 <= c < C, else throws out_of_range
    LEETCODE_NO_SANITIZE T minLteGte(int r, int c) const {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("minLteGte: needs 0 <= r < R and 0 <= c < C");
        return minOf(0, c, r, C - 1);
    }

    // O(1) -- min of the cells with row >= r and column <= c; needs 0 <= r < R and 0 <= c < C, else throws out_of_range
    LEETCODE_NO_SANITIZE T minGteLte(int r, int c) const {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("minGteLte: needs 0 <= r < R and 0 <= c < C");
        return minOf(r, 0, R - 1, c);
    }

    // O(1) -- min of the cells with row >= r and column >= c; needs 0 <= r < R and 0 <= c < C, else throws out_of_range
    LEETCODE_NO_SANITIZE T minGteGte(int r, int c) const {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("minGteGte: needs 0 <= r < R and 0 <= c < C");
        return minOf(r, c, R - 1, C - 1);
    }

    LEETCODE_NO_SANITIZE T andOf(int r1, int c1, int r2, int c2) const {
        int kr = 31 - __builtin_clz(r2 - r1 + 1), kc = 31 - __builtin_clz(c2 - c1 + 1);
        const T* t = &an[at[kr * levelsC + kc]];
        int w = C - (1 << kc) + 1, d = c2 - (1 << kc) + 1 - c1;
        size_t i = (size_t)r1 * w + c1, j = (size_t)(r2 - (1 << kr) + 1) * w + c1;
        return t[i] & t[i + d] & t[j] & t[j + d];
    }

    // O(1) -- AND of rows r1..r2, columns c1..c2; needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C, else throws
    // out_of_range
    LEETCODE_NO_SANITIZE T rectAnd(int r1, int c1, int r2, int c2) const {
        if (r1 < 0 || r1 > r2 || r2 >= R || c1 < 0 || c1 > c2 || c2 >= C)
            throw out_of_range("rectAnd: needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C");
        return andOf(r1, c1, r2, c2);
    }

    // O(1) -- AND of the square with top-left cell (r, c) and that many rows and columns; needs side >= 1 and the
    // square inside the grid, else throws out_of_range
    LEETCODE_NO_SANITIZE T squareAnd(int r, int c, int side) const {
        if (side < 1 || r < 0 || r + side > R || c < 0 || c + side > C)
            throw out_of_range("squareAnd: needs side >= 1 and the square inside the grid");
        return andOf(r, c, r + side - 1, c + side - 1);
    }

    // O(1) -- AND of the whole grid
    LEETCODE_NO_SANITIZE T andAll() const {
        return andOf(0, 0, R - 1, C - 1);
    }

    // O(1) -- the value at (r, c); needs 0 <= r < R and 0 <= c < C, else throws out_of_range
    LEETCODE_NO_SANITIZE T pointGet(int r, int c) const {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("pointGet: needs 0 <= r < R and 0 <= c < C");
        return mn[(size_t)r * C + c];
    }
};
