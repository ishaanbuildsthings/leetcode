// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries-2d/grid-corner-table-max-ltegte-gtelte-gtegte/template.cpp
#include <bits/stdc++.h>
using namespace std;
// @operations: maxAll maxGteGte maxGteLte maxLteGte
// @data-structure-type: corner-table
// @input: grid
// @complexities:
//   maxAll: 1
//   maxGteGte: 1
//   maxGteLte: 1
//   maxLteGte: 1
//   build: R*C
// @memory:
//   layout: none
//   node: tLteGte[1*R*C] tGteLte[1*R*C] tGteGte[1*R*C]
//   tags: none
//   other: none
//   note: one R by C table per corner direction, flat

// Static corner max: the max over a corner of the grid (every cell with row <= r or >= r, and column <= c or >= c) in
// O(1), from one R x C table per direction filled in a single pass (a cell's corner is its own row's running max
// joined with the corner of the cell one row back). No updates. Rows and columns are 0-based.
// T is any type with < (int, long long, double, ...).
template <typename T>
struct CornerMaxTable2D {
    int R, C;
    T best;
    vector<T> tLteGte, tGteLte, tGteGte;

    // O(R*C) -- grid: R rows of C numbers each; needs R >= 1 and C >= 1, else throws invalid_argument
    explicit CornerMaxTable2D(const vector<vector<T>>& grid)
        : R((int)grid.size()), C(grid.empty() ? 0 : (int)grid[0].size()) {
        if (R < 1 || C < 1) throw invalid_argument("CornerMaxTable2D: needs R >= 1 and C >= 1");
        for (auto& row : grid)
            if ((int)row.size() != C) throw invalid_argument("CornerMaxTable2D: every row needs the same C values");
        best = grid[0][0];
        for (auto& row : grid)
            for (const T& v : row) best = max(best, v);
        tLteGte.resize((size_t)R * C);
        for (int r = 0; r < R; r++) {
            T run = grid[r][C - 1];
            bool hasBack = r > 0;
            size_t at = (size_t)r * C, back = at - C;
            for (int c = C - 1; c >= 0; c--) {
                run = max(run, grid[r][c]);
                tLteGte[at + c] = hasBack ? max(run, tLteGte[back + c]) : run;
            }
        }
        tGteLte.resize((size_t)R * C);
        for (int r = R - 1; r >= 0; r--) {
            T run = grid[r][0];
            bool hasBack = r < R - 1;
            size_t at = (size_t)r * C, back = at + C;
            for (int c = 0; c < C; c++) {
                run = max(run, grid[r][c]);
                tGteLte[at + c] = hasBack ? max(run, tGteLte[back + c]) : run;
            }
        }
        tGteGte.resize((size_t)R * C);
        for (int r = R - 1; r >= 0; r--) {
            T run = grid[r][C - 1];
            bool hasBack = r < R - 1;
            size_t at = (size_t)r * C, back = at + C;
            for (int c = C - 1; c >= 0; c--) {
                run = max(run, grid[r][c]);
                tGteGte[at + c] = hasBack ? max(run, tGteGte[back + c]) : run;
            }
        }
    }

    // O(1) -- max of the cells with row <= r and column >= c; needs 0 <= r < R and 0 <= c < C, else throws out_of_range
    T maxLteGte(int r, int c) const {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("maxLteGte: needs 0 <= r < R and 0 <= c < C");
        return tLteGte[(size_t)r * C + c];
    }

    // O(1) -- max of the cells with row >= r and column <= c; needs 0 <= r < R and 0 <= c < C, else throws out_of_range
    T maxGteLte(int r, int c) const {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("maxGteLte: needs 0 <= r < R and 0 <= c < C");
        return tGteLte[(size_t)r * C + c];
    }

    // O(1) -- max of the cells with row >= r and column >= c; needs 0 <= r < R and 0 <= c < C, else throws out_of_range
    T maxGteGte(int r, int c) const {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("maxGteGte: needs 0 <= r < R and 0 <= c < C");
        return tGteGte[(size_t)r * C + c];
    }

    // O(1) -- max of the whole grid
    T maxAll() const {
        return best;
    }
};
