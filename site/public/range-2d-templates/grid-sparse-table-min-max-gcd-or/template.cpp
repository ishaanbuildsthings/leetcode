// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries-2d/grid-sparse-table-min-max-gcd-or/template.cpp
#include <bits/stdc++.h>
using namespace std;
// @operations: gcdAll maxAll maxGteGte maxGteLte maxLteGte maxLteLte minAll minGteGte minGteLte minLteGte minLteLte orAll pointGet rectGcd rectMax rectMin rectOr squareGcd squareMax squareMin squareOr
// @data-structure-type: sparse-table
// @input: grid
// @complexities:
//   gcdAll: log(U) ?
//   maxAll: 1
//   maxGteGte: 1
//   maxGteLte: 1
//   maxLteGte: 1
//   maxLteLte: 1
//   minAll: 1
//   minGteGte: 1
//   minGteLte: 1
//   minLteGte: 1
//   minLteLte: 1
//   orAll: 1
//   pointGet: 1
//   rectGcd: log(U) ?
//   rectMax: 1
//   rectMin: 1
//   rectOr: 1
//   squareGcd: log(U) ?
//   squareMax: 1
//   squareMin: 1
//   squareOr: 1
//   build: R*C*log(R)*log(C)*log(U) ?
// @memory:
//   layout: none
//   node: mn[1*R*C*log(R)*log(C)] mx[1*R*C*log(R)*log(C)] gc[1*R*C*log(R)*log(C)] orr[1*R*C*log(R)*log(C)]
//   tags: none
//   other: none
//   note: per aggregate, one table for every pair of a power-of-two height and a power-of-two width (the 1 x 1 table is the grid itself, shared)

// Static 2D sparse table (min, max, gcd, OR): any rectangle in O(1) (one gcd run, O(log U)). For every power-of-two
// height and power-of-two width there is a table holding the aggregate of each window of that size; a rectangle is
// covered by four such windows, one in each corner (they overlap, which is fine: each of these gives the same answer
// when a cell is counted twice). Memory and build are R * C * log R * log C: when only squares are asked for, the
// square sparse table needs a single log. No updates. Rows and columns are 0-based and rectangles are inclusive: rows
// r1..r2, columns c1..c2.
// T is any integer type (int, long long, ...).
template <typename T>
struct SparseTable2D {
    int R, C;
    vector<vector<vector<T>>> mn;  // [kr][kc]: windows of 2^kr rows by 2^kc columns, flat
    vector<vector<vector<T>>> mx;  // [kr][kc]: windows of 2^kr rows by 2^kc columns, flat
    vector<vector<vector<T>>> gc;  // [kr][kc]: windows of 2^kr rows by 2^kc columns, flat
    vector<vector<vector<T>>> orr;  // [kr][kc]: windows of 2^kr rows by 2^kc columns, flat

    // O(R*C*logR*logC*logU) -- grid: R rows of C numbers each; needs R >= 1 and C >= 1, else throws invalid_argument
    explicit SparseTable2D(const vector<vector<T>>& grid)
        : R((int)grid.size()), C(grid.empty() ? 0 : (int)grid[0].size()) {
        if (R < 1 || C < 1) throw invalid_argument("SparseTable2D: needs R >= 1 and C >= 1");
        for (auto& row : grid)
            if ((int)row.size() != C) throw invalid_argument("SparseTable2D: every row needs the same C values");
        int levelsR = 32 - __builtin_clz(R), levelsC = 32 - __builtin_clz(C);
        vector<T> flat;
        flat.reserve((size_t)R * C);
        for (auto& row : grid) flat.insert(flat.end(), row.begin(), row.end());
        mn.assign(levelsR, vector<vector<T>>(levelsC));
        mn[0][0] = flat;
        for (int kc = 1; kc < levelsC; kc++) {
            int half = 1 << (kc - 1), prevW = C - half + 1, w = C - (1 << kc) + 1;
            const auto& prev = mn[0][kc - 1];
            auto& cur = mn[0][kc];
            cur.resize((size_t)R * w);
            for (int r = 0; r < R; r++)
                for (int c = 0; c < w; c++) cur[r * w + c] = min(prev[r * prevW + c], prev[r * prevW + c + half]);
        }
        for (int kr = 1; kr < levelsR; kr++) {
            int half = 1 << (kr - 1), h = R - (1 << kr) + 1;
            for (int kc = 0; kc < levelsC; kc++) {
                int w = C - (1 << kc) + 1, off = half * w;
                const auto& prev = mn[kr - 1][kc];
                auto& cur = mn[kr][kc];
                cur.resize((size_t)h * w);
                for (int i = 0; i < h * w; i++) cur[i] = min(prev[i], prev[i + off]);
            }
        }
        mx.assign(levelsR, vector<vector<T>>(levelsC));
        mx[0][0] = flat;
        for (int kc = 1; kc < levelsC; kc++) {
            int half = 1 << (kc - 1), prevW = C - half + 1, w = C - (1 << kc) + 1;
            const auto& prev = mx[0][kc - 1];
            auto& cur = mx[0][kc];
            cur.resize((size_t)R * w);
            for (int r = 0; r < R; r++)
                for (int c = 0; c < w; c++) cur[r * w + c] = max(prev[r * prevW + c], prev[r * prevW + c + half]);
        }
        for (int kr = 1; kr < levelsR; kr++) {
            int half = 1 << (kr - 1), h = R - (1 << kr) + 1;
            for (int kc = 0; kc < levelsC; kc++) {
                int w = C - (1 << kc) + 1, off = half * w;
                const auto& prev = mx[kr - 1][kc];
                auto& cur = mx[kr][kc];
                cur.resize((size_t)h * w);
                for (int i = 0; i < h * w; i++) cur[i] = max(prev[i], prev[i + off]);
            }
        }
        gc.assign(levelsR, vector<vector<T>>(levelsC));
        gc[0][0] = flat;
        for (int kc = 1; kc < levelsC; kc++) {
            int half = 1 << (kc - 1), prevW = C - half + 1, w = C - (1 << kc) + 1;
            const auto& prev = gc[0][kc - 1];
            auto& cur = gc[0][kc];
            cur.resize((size_t)R * w);
            for (int r = 0; r < R; r++)
                for (int c = 0; c < w; c++) cur[r * w + c] = std::gcd(prev[r * prevW + c], prev[r * prevW + c + half]);
        }
        for (int kr = 1; kr < levelsR; kr++) {
            int half = 1 << (kr - 1), h = R - (1 << kr) + 1;
            for (int kc = 0; kc < levelsC; kc++) {
                int w = C - (1 << kc) + 1, off = half * w;
                const auto& prev = gc[kr - 1][kc];
                auto& cur = gc[kr][kc];
                cur.resize((size_t)h * w);
                for (int i = 0; i < h * w; i++) cur[i] = std::gcd(prev[i], prev[i + off]);
            }
        }
        orr.assign(levelsR, vector<vector<T>>(levelsC));
        orr[0][0] = flat;
        for (int kc = 1; kc < levelsC; kc++) {
            int half = 1 << (kc - 1), prevW = C - half + 1, w = C - (1 << kc) + 1;
            const auto& prev = orr[0][kc - 1];
            auto& cur = orr[0][kc];
            cur.resize((size_t)R * w);
            for (int r = 0; r < R; r++)
                for (int c = 0; c < w; c++) cur[r * w + c] = prev[r * prevW + c] | prev[r * prevW + c + half];
        }
        for (int kr = 1; kr < levelsR; kr++) {
            int half = 1 << (kr - 1), h = R - (1 << kr) + 1;
            for (int kc = 0; kc < levelsC; kc++) {
                int w = C - (1 << kc) + 1, off = half * w;
                const auto& prev = orr[kr - 1][kc];
                auto& cur = orr[kr][kc];
                cur.resize((size_t)h * w);
                for (int i = 0; i < h * w; i++) cur[i] = prev[i] | prev[i + off];
            }
        }
    }

    T minOf(int r1, int c1, int r2, int c2) const {
        int kr = 31 - __builtin_clz(r2 - r1 + 1), kc = 31 - __builtin_clz(c2 - c1 + 1);
        const auto& t = mn[kr][kc];
        int w = C - (1 << kc) + 1, i = r1 * w + c1, j = (r2 - (1 << kr) + 1) * w + c1, d = c2 - (1 << kc) + 1 - c1;
        return min(min(t[i], t[i + d]), min(t[j], t[j + d]));
    }

    // O(1) -- min of rows r1..r2, columns c1..c2; needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C, else throws
    // out_of_range
    T rectMin(int r1, int c1, int r2, int c2) const {
        if (r1 < 0 || r1 > r2 || r2 >= R || c1 < 0 || c1 > c2 || c2 >= C)
            throw out_of_range("rectMin: needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C");
        return minOf(r1, c1, r2, c2);
    }

    // O(1) -- min of the square with top-left cell (r, c) and that many rows and columns; needs side >= 1 and the
    // square
    // inside the grid, else throws out_of_range
    T squareMin(int r, int c, int side) const {
        if (side < 1 || r < 0 || r + side > R || c < 0 || c + side > C)
            throw out_of_range("squareMin: needs side >= 1 and the square inside the grid");
        return minOf(r, c, r + side - 1, c + side - 1);
    }

    // O(1) -- min of the whole grid
    T minAll() const {
        return minOf(0, 0, R - 1, C - 1);
    }

    // O(1) -- min of the cells with row <= r and column <= c; needs 0 <= r < R and 0 <= c < C, else throws out_of_range
    T minLteLte(int r, int c) const {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("minLteLte: needs 0 <= r < R and 0 <= c < C");
        return minOf(0, 0, r, c);
    }

    // O(1) -- min of the cells with row <= r and column >= c; needs 0 <= r < R and 0 <= c < C, else throws out_of_range
    T minLteGte(int r, int c) const {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("minLteGte: needs 0 <= r < R and 0 <= c < C");
        return minOf(0, c, r, C - 1);
    }

    // O(1) -- min of the cells with row >= r and column <= c; needs 0 <= r < R and 0 <= c < C, else throws out_of_range
    T minGteLte(int r, int c) const {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("minGteLte: needs 0 <= r < R and 0 <= c < C");
        return minOf(r, 0, R - 1, c);
    }

    // O(1) -- min of the cells with row >= r and column >= c; needs 0 <= r < R and 0 <= c < C, else throws out_of_range
    T minGteGte(int r, int c) const {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("minGteGte: needs 0 <= r < R and 0 <= c < C");
        return minOf(r, c, R - 1, C - 1);
    }

    T maxOf(int r1, int c1, int r2, int c2) const {
        int kr = 31 - __builtin_clz(r2 - r1 + 1), kc = 31 - __builtin_clz(c2 - c1 + 1);
        const auto& t = mx[kr][kc];
        int w = C - (1 << kc) + 1, i = r1 * w + c1, j = (r2 - (1 << kr) + 1) * w + c1, d = c2 - (1 << kc) + 1 - c1;
        return max(max(t[i], t[i + d]), max(t[j], t[j + d]));
    }

    // O(1) -- max of rows r1..r2, columns c1..c2; needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C, else throws
    // out_of_range
    T rectMax(int r1, int c1, int r2, int c2) const {
        if (r1 < 0 || r1 > r2 || r2 >= R || c1 < 0 || c1 > c2 || c2 >= C)
            throw out_of_range("rectMax: needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C");
        return maxOf(r1, c1, r2, c2);
    }

    // O(1) -- max of the square with top-left cell (r, c) and that many rows and columns; needs side >= 1 and the
    // square
    // inside the grid, else throws out_of_range
    T squareMax(int r, int c, int side) const {
        if (side < 1 || r < 0 || r + side > R || c < 0 || c + side > C)
            throw out_of_range("squareMax: needs side >= 1 and the square inside the grid");
        return maxOf(r, c, r + side - 1, c + side - 1);
    }

    // O(1) -- max of the whole grid
    T maxAll() const {
        return maxOf(0, 0, R - 1, C - 1);
    }

    // O(1) -- max of the cells with row <= r and column <= c; needs 0 <= r < R and 0 <= c < C, else throws out_of_range
    T maxLteLte(int r, int c) const {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("maxLteLte: needs 0 <= r < R and 0 <= c < C");
        return maxOf(0, 0, r, c);
    }

    // O(1) -- max of the cells with row <= r and column >= c; needs 0 <= r < R and 0 <= c < C, else throws out_of_range
    T maxLteGte(int r, int c) const {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("maxLteGte: needs 0 <= r < R and 0 <= c < C");
        return maxOf(0, c, r, C - 1);
    }

    // O(1) -- max of the cells with row >= r and column <= c; needs 0 <= r < R and 0 <= c < C, else throws out_of_range
    T maxGteLte(int r, int c) const {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("maxGteLte: needs 0 <= r < R and 0 <= c < C");
        return maxOf(r, 0, R - 1, c);
    }

    // O(1) -- max of the cells with row >= r and column >= c; needs 0 <= r < R and 0 <= c < C, else throws out_of_range
    T maxGteGte(int r, int c) const {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("maxGteGte: needs 0 <= r < R and 0 <= c < C");
        return maxOf(r, c, R - 1, C - 1);
    }

    T gcdOf(int r1, int c1, int r2, int c2) const {
        int kr = 31 - __builtin_clz(r2 - r1 + 1), kc = 31 - __builtin_clz(c2 - c1 + 1);
        const auto& t = gc[kr][kc];
        int w = C - (1 << kc) + 1, i = r1 * w + c1, j = (r2 - (1 << kr) + 1) * w + c1, d = c2 - (1 << kc) + 1 - c1;
        return std::gcd(std::gcd(t[i], t[i + d]), std::gcd(t[j], t[j + d]));
    }

    // O(log U) -- gcd of rows r1..r2, columns c1..c2; needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C, else throws
    // out_of_range
    T rectGcd(int r1, int c1, int r2, int c2) const {
        if (r1 < 0 || r1 > r2 || r2 >= R || c1 < 0 || c1 > c2 || c2 >= C)
            throw out_of_range("rectGcd: needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C");
        return gcdOf(r1, c1, r2, c2);
    }

    // O(log U) -- gcd of the square with top-left cell (r, c) and that many rows and columns; needs side >= 1 and the
    // square inside the grid, else throws out_of_range
    T squareGcd(int r, int c, int side) const {
        if (side < 1 || r < 0 || r + side > R || c < 0 || c + side > C)
            throw out_of_range("squareGcd: needs side >= 1 and the square inside the grid");
        return gcdOf(r, c, r + side - 1, c + side - 1);
    }

    // O(log U) -- gcd of the whole grid
    T gcdAll() const {
        return gcdOf(0, 0, R - 1, C - 1);
    }

    T orOf(int r1, int c1, int r2, int c2) const {
        int kr = 31 - __builtin_clz(r2 - r1 + 1), kc = 31 - __builtin_clz(c2 - c1 + 1);
        const auto& t = orr[kr][kc];
        int w = C - (1 << kc) + 1, i = r1 * w + c1, j = (r2 - (1 << kr) + 1) * w + c1, d = c2 - (1 << kc) + 1 - c1;
        return t[i] | t[i + d] | t[j] | t[j + d];
    }

    // O(1) -- OR of rows r1..r2, columns c1..c2; needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C, else throws
    // out_of_range
    T rectOr(int r1, int c1, int r2, int c2) const {
        if (r1 < 0 || r1 > r2 || r2 >= R || c1 < 0 || c1 > c2 || c2 >= C)
            throw out_of_range("rectOr: needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C");
        return orOf(r1, c1, r2, c2);
    }

    // O(1) -- OR of the square with top-left cell (r, c) and that many rows and columns; needs side >= 1 and the square
    // inside the grid, else throws out_of_range
    T squareOr(int r, int c, int side) const {
        if (side < 1 || r < 0 || r + side > R || c < 0 || c + side > C)
            throw out_of_range("squareOr: needs side >= 1 and the square inside the grid");
        return orOf(r, c, r + side - 1, c + side - 1);
    }

    // O(1) -- OR of the whole grid
    T orAll() const {
        return orOf(0, 0, R - 1, C - 1);
    }

    // O(1) -- the value at (r, c); needs 0 <= r < R and 0 <= c < C, else throws out_of_range
    T pointGet(int r, int c) const {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("pointGet: needs 0 <= r < R and 0 <= c < C");
        return mn[0][0][(size_t)r * C + c];
    }
};
