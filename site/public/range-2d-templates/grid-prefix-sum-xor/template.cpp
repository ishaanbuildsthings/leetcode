// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries-2d/grid-prefix-sum-xor/template.cpp
#include <bits/stdc++.h>
using namespace std;
// @operations: pointGet rectSum rectXor sumAll xorAll
// @data-structure-type: prefix-sum
// @input: grid
// @complexities:
//   pointGet: 1
//   rectSum: 1
//   rectXor: 1
//   sumAll: 1
//   xorAll: 1
//   build: R*C
// @memory:
//   layout: none
//   node: sm[1*R*C] xr[1*R*C]
//   tags: none
//   other: none
//   note: each table is (R + 1) by (C + 1), flat: entry [r][c] covers the rows above r and the columns left of c

// Static 2D prefix sum and xors: any rectangle in O(1) from four table entries (the big corner, minus the strip
// above, minus the strip to the left, plus the corner both took off). No updates. Rows and columns are 0-based and
// rectangles are inclusive: rows r1..r2, columns c1..c2.
// T is any integer type (int, long long, ...); sums are kept in S (long long for a smaller T).
template <typename T>
struct PrefixSumsXors2D {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    int R, C, W;
    vector<S> sm;
    vector<T> xr;

    // O(R*C) -- grid: R rows of C numbers each; needs R >= 1 and C >= 1, else throws invalid_argument
    explicit PrefixSumsXors2D(const vector<vector<T>>& grid)
        : R((int)grid.size()), C(grid.empty() ? 0 : (int)grid[0].size()), W(C + 1) {
        if (R < 1 || C < 1) throw invalid_argument("PrefixSumsXors2D: needs R >= 1 and C >= 1");
        for (auto& row : grid)
            if ((int)row.size() != C) throw invalid_argument("PrefixSumsXors2D: every row needs the same C values");
        sm.assign((size_t)(R + 1) * W, 0);
        xr.assign((size_t)(R + 1) * W, 0);
        for (int r = 0; r < R; r++) {
            int up = r * W, at = up + W;
            S runSum = 0;
            T runXor = 0;
            for (int c = 0; c < C; c++) {
                runSum += grid[r][c];
                sm[at + c + 1] = sm[up + c + 1] + runSum;
                runXor ^= grid[r][c];
                xr[at + c + 1] = xr[up + c + 1] ^ runXor;
            }
        }
    }

    // O(1) -- sum of rows r1..r2, columns c1..c2; needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C, else throws
    // out_of_range
    S rectSum(int r1, int c1, int r2, int c2) const {
        if (r1 < 0 || r1 > r2 || r2 >= R || c1 < 0 || c1 > c2 || c2 >= C)
            throw out_of_range("rectSum: needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C");
        int top = r1 * W, bot = (r2 + 1) * W;
        return sm[bot + c2 + 1] - sm[top + c2 + 1] - sm[bot + c1] + sm[top + c1];
    }

    // O(1) -- sum of the whole grid
    S sumAll() const {
        return sm.back();
    }

    // O(1) -- xor of rows r1..r2, columns c1..c2; needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C, else throws
    // out_of_range
    T rectXor(int r1, int c1, int r2, int c2) const {
        if (r1 < 0 || r1 > r2 || r2 >= R || c1 < 0 || c1 > c2 || c2 >= C)
            throw out_of_range("rectXor: needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C");
        int top = r1 * W, bot = (r2 + 1) * W;
        return xr[bot + c2 + 1] ^ xr[top + c2 + 1] ^ xr[bot + c1] ^ xr[top + c1];
    }

    // O(1) -- xor of the whole grid
    T xorAll() const {
        return xr.back();
    }

    // O(1) -- the value at (r, c); needs 0 <= r < R and 0 <= c < C, else throws out_of_range
    T pointGet(int r, int c) const {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("pointGet: needs 0 <= r < R and 0 <= c < C");
        int top = r * W, bot = top + W;
        return T(sm[bot + c + 1] - sm[top + c + 1] - sm[bot + c] + sm[top + c]);
    }
};
