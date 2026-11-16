// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries-2d/grid-bit-counts-or/template.cpp
#include <bits/stdc++.h>
using namespace std;
// @operations: orAll pointGet rectOr
// @data-structure-type: bit-counts
// @input: grid
// @values: non-negative
// @complexities:
//   orAll: log(U)
//   pointGet: 1
//   rectOr: log(U)
//   build: R*C*log(U)
// @memory:
//   layout: none
//   node: cnt[1*R*C*log(U)]
//   tags: none
//   other: vals[1*R*C]
//   note: one (R + 1) by (C + 1) prefix-count table per bit of the largest value

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

// Static rectangle OR from one 2D prefix-count table per bit: a bit is in the OR when some cell of the rectangle has
// it, and in the AND when every cell does. O(bits) per query, bits = bit length of the largest value, and bits * R *
// C memory (a sparse table answers in O(1) but takes log R * log C tables). Values must be >= 0. No updates. Rows and
// columns are 0-based and rectangles are inclusive: rows r1..r2, columns c1..c2.
// T is any integer type (int, long long, ...).
template <typename T>
struct BitCounts2D {
    int R, C, W, bits;
    size_t plane;  // one table's size, (R + 1) * (C + 1)
    HotVector<int> cnt;  // the prefix counts of bit b are the plane starting at b * plane
    HotVector<T> vals;

    // O(R*C*bits) -- grid: R rows of C numbers each, all >= 0; needs R >= 1 and C >= 1, else throws invalid_argument
    explicit BitCounts2D(const vector<vector<T>>& grid)
        : R((int)grid.size()), C(grid.empty() ? 0 : (int)grid[0].size()), W(C + 1), bits(1) {
        if (R < 1 || C < 1) throw invalid_argument("BitCounts2D: needs R >= 1 and C >= 1");
        for (auto& row : grid)
            if ((int)row.size() != C) throw invalid_argument("BitCounts2D: every row needs the same C values");
        T top = 0;
        for (auto& row : grid)
            for (T v : row) {
                if (v < 0) throw invalid_argument("BitCounts2D: values must be >= 0");
                vals.push_back(v);
                top = hotMax(top, v);
            }
        while (bits < 63 && (top >> bits) > 0) bits++;
        plane = (size_t)(R + 1) * W;
        cnt.assign(bits * plane, 0);
        for (int b = 0; b < bits; b++) {
            int* t = &cnt[b * plane];
            for (int r = 0; r < R; r++) {
                int up = r * W, at = up + W, run = 0;
                for (int c = 0; c < C; c++) {
                    run += (int)(grid[r][c] >> b & 1);
                    t[at + c + 1] = t[up + c + 1] + run;
                }
            }
        }
    }

    // how many cells of the rectangle have bit b
    LEETCODE_NO_SANITIZE int countOf(int b, int r1, int c1, int r2, int c2) const {
        const int* t = &cnt[b * plane];
        return t[(r2 + 1) * W + c2 + 1] - t[r1 * W + c2 + 1] - t[(r2 + 1) * W + c1] + t[r1 * W + c1];
    }

    // O(bits) -- OR of rows r1..r2, columns c1..c2; needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C, else throws
    // out_of_range
    LEETCODE_NO_SANITIZE T rectOr(int r1, int c1, int r2, int c2) const {
        if (r1 < 0 || r1 > r2 || r2 >= R || c1 < 0 || c1 > c2 || c2 >= C)
            throw out_of_range("rectOr: needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C");
        T res = 0;
        for (int b = 0; b < bits; b++)
            if (countOf(b, r1, c1, r2, c2) > 0) res |= T(1) << b;
        return res;
    }

    // O(bits) -- OR of the whole grid
    LEETCODE_NO_SANITIZE T orAll() const {
        int r1 = 0, c1 = 0, r2 = R - 1, c2 = C - 1;
        T res = 0;
        for (int b = 0; b < bits; b++)
            if (countOf(b, r1, c1, r2, c2) > 0) res |= T(1) << b;
        return res;
    }

    // O(1) -- the value at (r, c); needs 0 <= r < R and 0 <= c < C, else throws out_of_range
    LEETCODE_NO_SANITIZE T pointGet(int r, int c) const {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("pointGet: needs 0 <= r < R and 0 <= c < C");
        return vals[(size_t)r * C + c];
    }
};
