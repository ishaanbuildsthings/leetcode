// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries-2d/grid-rect-assign-point-get/template.cpp
#include <bits/stdc++.h>
using namespace std;
// @operations: pointAssign pointGet rectAssign
// @data-structure-type: seg-tree-kept-tags
// @input: grid
// @complexities:
//   pointAssign: log(R)*log(C)
//   pointGet: log(R)*log(C)
//   rectAssign: log(R)*log(C)
//   build: R*C
// @memory:
//   layout: 2n-iterative
//   node: stamp[4*R*C]
//   tags: none
//   other: vals[1*R*C]
//   note: 2R row-nodes by 2C column-nodes of timestamps, flat; vals holds the grid's values then one more per write (the value written at each timestamp)

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


// Rectangle assign and point get on an R x C grid, O(log R * log C) each. rectAssign(r1, c1, r2, c2, v) makes every
// cell of the rectangle v; pointGet(r, c) reads one cell. Every write gets the next timestamp, and a 2D segment tree
// keeps the newest timestamp at the nodes that make up the write's rectangle (no push-down: a newer write always
// wins, so nothing is ever undone). A read takes the newest timestamp on its cell's path up both trees and returns
// the value written at that time. Rows and columns are 0-based and rectangles are inclusive: rows r1..r2, columns
// c1..c2. For rectangle sums or maxes after rectangle assigns, there is no log^2 template: loop the rows with a 1D
// lazy segment tree each.
template <typename T>
struct RectAssignPointGet2D {
    int R, C, W;
    HotVector<int> stamp;  // per row-node, per column-node: the newest timestamp put there
    HotVector<T> vals;  // vals[t]: the value written at timestamp t; 1..R*C are the grid's own

    // O(R*C) -- grid: R rows of C values each; needs R >= 1 and C >= 1, else throws invalid_argument
    explicit RectAssignPointGet2D(const vector<vector<T>>& grid) {
        R = (int)grid.size();
        C = R ? (int)grid[0].size() : 0;
        if (R < 1 || C < 1) throw invalid_argument("RectAssignPointGet2D: needs R >= 1 rows of C >= 1 values");
        for (const auto& row : grid)
            if ((int)row.size() != C) throw invalid_argument("RectAssignPointGet2D: every row needs the same C values");
        W = 2 * C;
        stamp.assign((size_t)2 * R * W, 0);
        vals.reserve((size_t)R * C + 1);
        vals.push_back(T());
        for (int r = 0; r < R; r++)
            for (int c = 0; c < C; c++) {
                vals.push_back(grid[r][c]);
                stamp[(size_t)(r + R) * W + C + c] = (int)vals.size() - 1;
            }
    }

    // one column tree (the one starting at `base`): columns c1..c2 get timestamp t
    LEETCODE_NO_SANITIZE void mark(size_t base, int c1, int c2, int t) {
        int* s = stamp.data() + base;
        for (int lo = c1 + C, hi = c2 + C + 1; lo < hi; lo >>= 1, hi >>= 1) {
            if (lo & 1) s[lo++] = t;
            if (hi & 1) s[--hi] = t;
        }
    }

    // every cell of the rectangle gets the next timestamp, which stands for v
    LEETCODE_NO_SANITIZE void write(int r1, int c1, int r2, int c2, T v) {
        vals.push_back(v);
        int t = (int)vals.size() - 1;
        for (int lo = r1 + R, hi = r2 + R + 1; lo < hi; lo >>= 1, hi >>= 1) {
            if (lo & 1) mark((size_t)lo++ * W, c1, c2, t);
            if (hi & 1) mark((size_t)--hi * W, c1, c2, t);
        }
    }

    // O(log R * log C) -- every cell of rows r1..r2, columns c1..c2 becomes v; needs 0 <= r1 <= r2 < R and 0 <= c1 <=
    // c2 < C, else throws out_of_range
    LEETCODE_NO_SANITIZE void rectAssign(int r1, int c1, int r2, int c2, T v) {
        if (!(0 <= r1 && r1 <= r2 && r2 < R && 0 <= c1 && c1 <= c2 && c2 < C))
            throw out_of_range("rectAssign: needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C");
        write(r1, c1, r2, c2, v);
    }

    // O(log R * log C) -- the cell (r, c) becomes v; needs 0 <= r < R and 0 <= c < C, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAssign(int r, int c, T v) {
        if (!(0 <= r && r < R && 0 <= c && c < C)) throw out_of_range("pointAssign: needs 0 <= r < R and 0 <= c < C");
        write(r, c, r, c, v);
    }

    // O(log R * log C) -- the value at (r, c); needs 0 <= r < R and 0 <= c < C, else throws out_of_range
    LEETCODE_NO_SANITIZE T pointGet(int r, int c) const {
        if (!(0 <= r && r < R && 0 <= c && c < C)) throw out_of_range("pointGet: needs 0 <= r < R and 0 <= c < C");
        int best = 0;
        for (int pr = r + R; pr; pr >>= 1) {
            const int* s = stamp.data() + (size_t)pr * W;
            for (int pc = c + C; pc; pc >>= 1)
                if (s[pc] > best) best = s[pc];
        }
        return vals[best];
    }
};
