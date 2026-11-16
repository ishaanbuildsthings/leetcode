// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries-2d/grid-square-sparse-table-min-max-gcd-and-or/template.cpp
#include <bits/stdc++.h>
using namespace std;
// @operations: pointGet squareAnd squareGcd squareMax squareMin squareOr
// @data-structure-type: square-sparse-table
// @input: grid
// @complexities:
//   pointGet: 1
//   squareAnd: 1
//   squareGcd: log(U) ?
//   squareMax: 1
//   squareMin: 1
//   squareOr: 1
//   build: R*C*log(min(R,C))*log(U) ?
// @memory:
//   layout: none
//   node: mn[1*R*C*log(min(R,C))] mx[1*R*C*log(min(R,C))] gc[1*R*C*log(min(R,C))] an[1*R*C*log(min(R,C))] orr[1*R*C*log(min(R,C))]
//   tags: none
//   other: none
//   note: per aggregate, one table per power-of-two side (side 1 is the grid itself, shared)

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
template <typename A>
LEETCODE_NO_SANITIZE_INLINE A hotMax(A a, A b) { return a < b ? b : a; }

// Static sparse table for square queries only (min, max, gcd, AND, OR): O(1) per square (one gcd run, O(log U)), with
// a single log of memory and build, R * C * log(min(R, C)), where the any-rectangle sparse table needs log R * log C.
// Level k holds the aggregate of every 2^k by 2^k window; a square is covered by four such windows, one in each
// corner (they overlap, which is fine for these aggregates). No updates. Rows and columns are 0-based; a square is
// its top-left cell (r, c) and its side.
// T is any integer type (int, long long, ...).
template <typename T>
struct SquareSparseTable2D {
    int R, C, levels;
    HotVector<size_t> at;  // at[k]: where the table of 2^k by 2^k windows starts in each array
    HotVector<T> mn;  // every table back to back, each flat: (R - 2^k + 1) rows of (C - 2^k + 1)
    HotVector<T> mx;  // every table back to back, each flat: (R - 2^k + 1) rows of (C - 2^k + 1)
    HotVector<T> gc;  // every table back to back, each flat: (R - 2^k + 1) rows of (C - 2^k + 1)
    HotVector<T> an;  // every table back to back, each flat: (R - 2^k + 1) rows of (C - 2^k + 1)
    HotVector<T> orr;  // every table back to back, each flat: (R - 2^k + 1) rows of (C - 2^k + 1)

    // O(R*C*log(min(R, C))*logU) -- grid: R rows of C numbers each; needs R >= 1 and C >= 1, else throws
    // invalid_argument
    explicit SquareSparseTable2D(const vector<vector<T>>& grid)
        : R((int)grid.size()), C(grid.empty() ? 0 : (int)grid[0].size()) {
        if (R < 1 || C < 1) throw invalid_argument("SquareSparseTable2D: needs R >= 1 and C >= 1");
        for (auto& row : grid)
            if ((int)row.size() != C) throw invalid_argument("SquareSparseTable2D: every row needs the same C values");
        levels = 32 - __builtin_clz(hotMin(R, C));
        at.assign(levels + 1, 0);
        for (int k = 0; k < levels; k++) at[k + 1] = at[k] + (size_t)(R - (1 << k) + 1) * (C - (1 << k) + 1);
        mn.assign(at.back(), T(0));
        for (int r = 0; r < R; r++)
            for (int c = 0; c < C; c++) mn[(size_t)r * C + c] = grid[r][c];
        mx.assign(at.back(), T(0));
        for (int r = 0; r < R; r++)
            for (int c = 0; c < C; c++) mx[(size_t)r * C + c] = grid[r][c];
        gc.assign(at.back(), T(0));
        for (int r = 0; r < R; r++)
            for (int c = 0; c < C; c++) gc[(size_t)r * C + c] = grid[r][c];
        an.assign(at.back(), T(0));
        for (int r = 0; r < R; r++)
            for (int c = 0; c < C; c++) an[(size_t)r * C + c] = grid[r][c];
        orr.assign(at.back(), T(0));
        for (int r = 0; r < R; r++)
            for (int c = 0; c < C; c++) orr[(size_t)r * C + c] = grid[r][c];
        buildLevels();
    }

    // every table from the one of half its side
    LEETCODE_NO_SANITIZE void buildLevels() {
        for (int k = 1; k < levels; k++) {
            int half = 1 << (k - 1), prevW = C - half + 1, h = R - (1 << k) + 1, w = C - (1 << k) + 1;
            const T* prev = &mn[at[k - 1]];
            T* cur = &mn[at[k]];
            for (int i = 0; i < h; i++) {
                const T* top = prev + (size_t)i * prevW;
                const T* bot = top + (size_t)half * prevW;
                T* out = cur + (size_t)i * w;
                for (int j = 0; j < w; j++)
                    out[j] = hotMin(hotMin(top[j], top[j + half]), hotMin(bot[j], bot[j + half]));
            }
        }
        for (int k = 1; k < levels; k++) {
            int half = 1 << (k - 1), prevW = C - half + 1, h = R - (1 << k) + 1, w = C - (1 << k) + 1;
            const T* prev = &mx[at[k - 1]];
            T* cur = &mx[at[k]];
            for (int i = 0; i < h; i++) {
                const T* top = prev + (size_t)i * prevW;
                const T* bot = top + (size_t)half * prevW;
                T* out = cur + (size_t)i * w;
                for (int j = 0; j < w; j++)
                    out[j] = hotMax(hotMax(top[j], top[j + half]), hotMax(bot[j], bot[j + half]));
            }
        }
        for (int k = 1; k < levels; k++) {
            int half = 1 << (k - 1), prevW = C - half + 1, h = R - (1 << k) + 1, w = C - (1 << k) + 1;
            const T* prev = &gc[at[k - 1]];
            T* cur = &gc[at[k]];
            for (int i = 0; i < h; i++) {
                const T* top = prev + (size_t)i * prevW;
                const T* bot = top + (size_t)half * prevW;
                T* out = cur + (size_t)i * w;
                for (int j = 0; j < w; j++)
                    out[j] = std::gcd(std::gcd(top[j], top[j + half]), std::gcd(bot[j], bot[j + half]));
            }
        }
        for (int k = 1; k < levels; k++) {
            int half = 1 << (k - 1), prevW = C - half + 1, h = R - (1 << k) + 1, w = C - (1 << k) + 1;
            const T* prev = &an[at[k - 1]];
            T* cur = &an[at[k]];
            for (int i = 0; i < h; i++) {
                const T* top = prev + (size_t)i * prevW;
                const T* bot = top + (size_t)half * prevW;
                T* out = cur + (size_t)i * w;
                for (int j = 0; j < w; j++)
                    out[j] = top[j] & top[j + half] & bot[j] & bot[j + half];
            }
        }
        for (int k = 1; k < levels; k++) {
            int half = 1 << (k - 1), prevW = C - half + 1, h = R - (1 << k) + 1, w = C - (1 << k) + 1;
            const T* prev = &orr[at[k - 1]];
            T* cur = &orr[at[k]];
            for (int i = 0; i < h; i++) {
                const T* top = prev + (size_t)i * prevW;
                const T* bot = top + (size_t)half * prevW;
                T* out = cur + (size_t)i * w;
                for (int j = 0; j < w; j++)
                    out[j] = top[j] | top[j + half] | bot[j] | bot[j + half];
            }
        }
    }

    // O(1) -- min of the square with top-left cell (r, c) and that many rows and columns; needs side >= 1 and the
    // square
    // inside the grid, else throws out_of_range
    LEETCODE_NO_SANITIZE T squareMin(int r, int c, int side) const {
        if (side < 1 || r < 0 || r + side > R || c < 0 || c + side > C)
            throw out_of_range("squareMin: needs side >= 1 and the square inside the grid");
        int k = 31 - __builtin_clz(side), w = C - (1 << k) + 1, d = side - (1 << k);
        size_t i = (size_t)r * w + c, j = i + (size_t)d * w;
        const T* t = &mn[at[k]];
        return hotMin(hotMin(t[i], t[i + d]), hotMin(t[j], t[j + d]));
    }

    // O(1) -- max of the square with top-left cell (r, c) and that many rows and columns; needs side >= 1 and the
    // square
    // inside the grid, else throws out_of_range
    LEETCODE_NO_SANITIZE T squareMax(int r, int c, int side) const {
        if (side < 1 || r < 0 || r + side > R || c < 0 || c + side > C)
            throw out_of_range("squareMax: needs side >= 1 and the square inside the grid");
        int k = 31 - __builtin_clz(side), w = C - (1 << k) + 1, d = side - (1 << k);
        size_t i = (size_t)r * w + c, j = i + (size_t)d * w;
        const T* t = &mx[at[k]];
        return hotMax(hotMax(t[i], t[i + d]), hotMax(t[j], t[j + d]));
    }

    // O(log U) -- gcd of the square with top-left cell (r, c) and that many rows and columns; needs side >= 1 and the
    // square inside the grid, else throws out_of_range
    LEETCODE_NO_SANITIZE T squareGcd(int r, int c, int side) const {
        if (side < 1 || r < 0 || r + side > R || c < 0 || c + side > C)
            throw out_of_range("squareGcd: needs side >= 1 and the square inside the grid");
        int k = 31 - __builtin_clz(side), w = C - (1 << k) + 1, d = side - (1 << k);
        size_t i = (size_t)r * w + c, j = i + (size_t)d * w;
        const T* t = &gc[at[k]];
        return std::gcd(std::gcd(t[i], t[i + d]), std::gcd(t[j], t[j + d]));
    }

    // O(1) -- AND of the square with top-left cell (r, c) and that many rows and columns; needs side >= 1 and the
    // square
    // inside the grid, else throws out_of_range
    LEETCODE_NO_SANITIZE T squareAnd(int r, int c, int side) const {
        if (side < 1 || r < 0 || r + side > R || c < 0 || c + side > C)
            throw out_of_range("squareAnd: needs side >= 1 and the square inside the grid");
        int k = 31 - __builtin_clz(side), w = C - (1 << k) + 1, d = side - (1 << k);
        size_t i = (size_t)r * w + c, j = i + (size_t)d * w;
        const T* t = &an[at[k]];
        return t[i] & t[i + d] & t[j] & t[j + d];
    }

    // O(1) -- OR of the square with top-left cell (r, c) and that many rows and columns; needs side >= 1 and the square
    // inside the grid, else throws out_of_range
    LEETCODE_NO_SANITIZE T squareOr(int r, int c, int side) const {
        if (side < 1 || r < 0 || r + side > R || c < 0 || c + side > C)
            throw out_of_range("squareOr: needs side >= 1 and the square inside the grid");
        int k = 31 - __builtin_clz(side), w = C - (1 << k) + 1, d = side - (1 << k);
        size_t i = (size_t)r * w + c, j = i + (size_t)d * w;
        const T* t = &orr[at[k]];
        return t[i] | t[i + d] | t[j] | t[j + d];
    }

    // O(1) -- the value at (r, c); needs 0 <= r < R and 0 <= c < C, else throws out_of_range
    LEETCODE_NO_SANITIZE T pointGet(int r, int c) const {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("pointGet: needs 0 <= r < R and 0 <= c < C");
        return mn[(size_t)r * C + c];
    }
};
