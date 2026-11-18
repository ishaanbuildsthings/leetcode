// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries-2d/grid-bit-xor/template.cpp
#include <bits/stdc++.h>
using namespace std;
// @operations: pointAdd pointAssign pointChmax pointChmin pointGet rectXor xorAll
// @data-structure-type: BIT
// @input: grid
// @complexities:
//   pointAdd: log(R)*log(C)
//   pointAssign: log(R)*log(C)
//   pointChmax: log(R)*log(C)
//   pointChmin: log(R)*log(C)
//   pointGet: 1
//   rectXor: log(R)*log(C)
//   xorAll: 1
//   build: R*C
// @memory:
//   layout: none
//   node: xr[1*R*C]
//   tags: none
//   other: vals[1*R*C]
//   note: each Fenwick tree is (R + 1) by (C + 1), flat, 1-based; vals keeps the cells themselves for O(1) reads

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

// 2D Fenwick tree (xor): point updates and any-rectangle xor on an R x C grid, O(log R * log C) each, with a quarter of
// a 2D segment tree's memory and a smaller constant. A rectangle is four prefix queries (the big corner, minus the
// strip above, minus the strip to the left, plus the corner both took off). Rows and columns are 0-based and rectangles
// are inclusive: rows r1..r2, columns c1..c2. The (R, C) constructor starts with every cell 0.
// T is any integer type (int, long long, ...).
template <typename T>
struct Fenwick2D {
    int R, C, W;
    HotVector<T> vals;
    HotVector<T> xr;
    T totalXor = 0;

    // O(R*C) -- R rows by C columns, every cell 0; needs R >= 1 and C >= 1, else throws invalid_argument
    Fenwick2D(int rows, int cols) : R(rows), C(cols), W(cols + 1) {
        if (R < 1 || C < 1) throw invalid_argument("Fenwick2D: needs R >= 1 and C >= 1");
        vals.assign((size_t)R * C, T(0));
        xr.assign((size_t)(R + 1) * W, 0);
    }

    // O(R*C) -- grid: R rows of C numbers each; needs R >= 1 and C >= 1, else throws invalid_argument
    explicit Fenwick2D(const vector<vector<T>>& grid)
        : Fenwick2D((int)grid.size(), grid.empty() ? 0 : (int)grid[0].size()) {
        for (int r = 0; r < R; r++) {
            if ((int)grid[r].size() != C) throw invalid_argument("Fenwick2D: every row needs the same C values");
            for (int c = 0; c < C; c++) vals[(size_t)r * C + c] = grid[r][c];
        }
        auto& tXor = xr;
        for (int r = 1; r <= R; r++) {
            int at = r * W;
            for (int c = 1; c <= C; c++) {
                tXor[at + c] ^= grid[r - 1][c - 1];
                totalXor ^= grid[r - 1][c - 1];
                int j = c + (c & -c);  // each entry is added into the next one that covers it
                if (j <= C) tXor[at + j] ^= tXor[at + c];
            }
        }
        for (int r = 1; r <= R; r++) {
            int j = r + (r & -r);
            if (j > R) continue;
            for (int c = 1; c <= C; c++) tXor[j * W + c] ^= tXor[r * W + c];
        }
    }

    // cell (r, c) becomes v
    LEETCODE_NO_SANITIZE void setCell(int r, int c, T v) {
        T old = vals[(size_t)r * C + c];
        vals[(size_t)r * C + c] = v;
        T dXor = v ^ old;
        totalXor ^= dXor;
        for (int i = r + 1; i <= R; i += i & -i)
            for (int j = c + 1; j <= C; j += j & -j) xr[i * W + j] ^= dXor;
    }

    // xor of the first r rows and first c columns
    LEETCODE_NO_SANITIZE T prefixXor(int r, int c) const {
        T res = 0;
        for (int i = r; i > 0; i &= i - 1)
            for (int j = c; j > 0; j &= j - 1) res ^= xr[i * W + j];
        return res;
    }

    // O(1) -- the value at (r, c); needs 0 <= r < R and 0 <= c < C, else throws out_of_range
    LEETCODE_NO_SANITIZE T pointGet(int r, int c) const {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("pointGet: needs 0 <= r < R and 0 <= c < C");
        return vals[(size_t)r * C + c];
    }

    // O(log R * log C) -- the cell at (r, c) becomes v; needs 0 <= r < R and 0 <= c < C, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAssign(int r, int c, T v) {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("pointAssign: needs 0 <= r < R and 0 <= c < C");
        setCell(r, c, v);
    }

    // O(log R * log C) -- adds v to the cell at (r, c); needs 0 <= r < R and 0 <= c < C, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAdd(int r, int c, T v) {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("pointAdd: needs 0 <= r < R and 0 <= c < C");
        setCell(r, c, T(vals[(size_t)r * C + c] + v));
    }

    // O(log R * log C) -- the cell at (r, c) becomes max(itself, v); needs 0 <= r < R and 0 <= c < C, else throws
    // out_of_range
    LEETCODE_NO_SANITIZE void pointChmax(int r, int c, T v) {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("pointChmax: needs 0 <= r < R and 0 <= c < C");
        if (v > vals[(size_t)r * C + c]) setCell(r, c, v);
    }

    // O(log R * log C) -- the cell at (r, c) becomes min(itself, v); needs 0 <= r < R and 0 <= c < C, else throws
    // out_of_range
    LEETCODE_NO_SANITIZE void pointChmin(int r, int c, T v) {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("pointChmin: needs 0 <= r < R and 0 <= c < C");
        if (v < vals[(size_t)r * C + c]) setCell(r, c, v);
    }

    // O(log R * log C) -- xor of rows r1..r2, columns c1..c2; needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C, else
    // throws out_of_range
    LEETCODE_NO_SANITIZE T rectXor(int r1, int c1, int r2, int c2) const {
        if (r1 < 0 || r1 > r2 || r2 >= R || c1 < 0 || c1 > c2 || c2 >= C)
            throw out_of_range("rectXor: needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C");
        return prefixXor(r2 + 1, c2 + 1) ^ prefixXor(r1, c2 + 1) ^ prefixXor(r2 + 1, c1) ^ prefixXor(r1, c1);
    }

    // O(1) -- xor of the whole grid
    LEETCODE_NO_SANITIZE T xorAll() const {
        return totalXor;
    }
};
