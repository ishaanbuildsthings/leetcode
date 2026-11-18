// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries-2d/grid-hash/template.cpp
#include <bits/stdc++.h>
using namespace std;
// @operations: hashAll rectHash rectsEqual
// @data-structure-type: hash
// @input: grid
// @complexities:
//   hashAll: 1
//   rectHash: 1
//   rectsEqual: 1
//   build: R*C
// @memory:
//   layout: none
//   node: pre[1*R*C]
//   tags: none
//   other: powR[1*R] powC[1*C]
//   note: pre is (R + 1) by (C + 1), flat: the hash of the rows above r and the columns left of c

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

// 2D hashing of a board (the 1D polynomial hash with one base per direction): the hash of any rectangle in O(1), and
// equal rectangles hash equal wherever they sit, so two rectangles of the same size can be compared in O(1). A cell
// (i, j) of a rectangle counts as value * A^(rows below it) * B^(columns right of it), mod the prime 2^61 - 1; the
// prefix table then gives a rectangle from four entries, each shifted by a power of A and B. Both bases and a value
// offset are picked at random each run, so no test can be built against them. Cells can be numbers or single
// characters. No updates. Rows and columns are 0-based and rectangles are inclusive: rows r1..r2, columns c1..c2.
// T is any integer or character type (int, long long, char, ...).
template <typename T>
struct Hash2D {
    using U64 = unsigned long long;
    int R, C, W;
    HotVector<U64> pre, powR, powC;

    LEETCODE_NO_SANITIZE static U64 rnd() {
        static mt19937_64 g(chrono::steady_clock::now().time_since_epoch().count());
        return g();
    }
    // mod the prime 2^61 - 1, with both bases and the value offset picked at random each run
    static constexpr U64 HP = (1ULL << 61) - 1;
    LEETCODE_NO_SANITIZE static U64 HA() {
        static U64 a = (1ULL << 40) + rnd() % (HP - (1ULL << 41));
        return a;
    }
    LEETCODE_NO_SANITIZE static U64 HB() {
        static U64 b = (1ULL << 40) + rnd() % (HP - (1ULL << 41));
        return b;
    }
    LEETCODE_NO_SANITIZE static U64 HO() {
        static U64 o = 1 + rnd() % (HP - 1);
        return o;
    }
    LEETCODE_NO_SANITIZE static U64 hmul(U64 a, U64 b) {
        __uint128_t c = (__uint128_t)a * b;
        U64 r = (U64)(c & HP) + (U64)(c >> 61);
        r = (r & HP) + (r >> 61);
        return r >= HP ? r - HP : r;
    }
    LEETCODE_NO_SANITIZE static U64 hadd(U64 a, U64 b) { return a + b >= HP ? a + b - HP : a + b; }
    LEETCODE_NO_SANITIZE static U64 hsub(U64 a, U64 b) { return a >= b ? a - b : a + HP - b; }
    // a cell's own hash: its value mod the prime (negatives wrap around), shifted by the offset
    LEETCODE_NO_SANITIZE static U64 cell(T v) {
        long long x = (long long)v % (long long)HP;
        return hadd(x < 0 ? (U64)(x + (long long)HP) : (U64)x, HO());
    }

    // O(R*C) -- grid: R rows of C cells each (a vector<string> works with T = char); needs R >= 1 and C >= 1, else
    // throws invalid_argument
    template <typename Row>
    explicit Hash2D(const vector<Row>& grid)
        : R((int)grid.size()), C(grid.empty() ? 0 : (int)grid[0].size()), W(C + 1) {
        if (R < 1 || C < 1) throw invalid_argument("Hash2D: needs R >= 1 and C >= 1");
        for (auto& row : grid)
            if ((int)row.size() != C) throw invalid_argument("Hash2D: every row needs the same C values");
        powR.assign(R + 1, 1);
        for (int i = 0; i < R; i++) powR[i + 1] = hmul(powR[i], HA());
        powC.assign(C + 1, 1);
        for (int j = 0; j < C; j++) powC[j + 1] = hmul(powC[j], HB());
        pre.assign((size_t)(R + 1) * W, 0);
        for (int r = 0; r < R; r++) {
            int up = r * W, at = up + W;
            U64 run = 0;  // this row alone, left to right
            for (int c = 0; c < C; c++) {
                run = hadd(hmul(run, HB()), cell(grid[r][c]));
                pre[at + c + 1] = hadd(hmul(pre[up + c + 1], HA()), run);
            }
        }
    }

    LEETCODE_NO_SANITIZE U64 hashOf(int r1, int c1, int r2, int c2) const {
        U64 a = powR[r2 - r1 + 1], b = powC[c2 - c1 + 1];
        int top = r1 * W, bot = (r2 + 1) * W;
        U64 res = hsub(pre[bot + c2 + 1], hmul(pre[top + c2 + 1], a));
        res = hsub(res, hmul(pre[bot + c1], b));
        return hadd(res, hmul(hmul(pre[top + c1], a), b));
    }

    // O(1) -- hash of rows r1..r2, columns c1..c2: rectangles with equal cells hash equal; needs 0 <= r1 <= r2 < R
    // and 0 <= c1 <= c2 < C, else throws out_of_range
    LEETCODE_NO_SANITIZE U64 rectHash(int r1, int c1, int r2, int c2) const {
        if (r1 < 0 || r1 > r2 || r2 >= R || c1 < 0 || c1 > c2 || c2 >= C)
            throw out_of_range("rectHash: needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C");
        return hashOf(r1, c1, r2, c2);
    }

    // O(1) -- is the rectangle rows r1..r2, columns c1..c2 equal, cell by cell, to the same-size rectangle whose
    // top-left cell is (r3, c3); needs both inside the grid, else throws out_of_range
    LEETCODE_NO_SANITIZE bool rectsEqual(int r1, int c1, int r2, int c2, int r3, int c3) const {
        int r4 = r3 + r2 - r1, c4 = c3 + c2 - c1;
        if (r1 < 0 || r1 > r2 || r2 >= R || c1 < 0 || c1 > c2 || c2 >= C || r3 < 0 || r4 >= R || c3 < 0 || c4 >= C)
            throw out_of_range("rectsEqual: needs both rectangles inside the grid");
        return hashOf(r1, c1, r2, c2) == hashOf(r3, c3, r4, c4);
    }

    // O(1) -- hash of the whole grid
    LEETCODE_NO_SANITIZE U64 hashAll() const {
        return pre.back();
    }
};
