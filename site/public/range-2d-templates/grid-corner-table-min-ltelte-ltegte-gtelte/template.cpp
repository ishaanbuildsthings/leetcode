// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries-2d/grid-corner-table-min-ltelte-ltegte-gtelte/template.cpp
#include <bits/stdc++.h>
using namespace std;
// @operations: minAll minGteLte minLteGte minLteLte
// @data-structure-type: corner-table
// @input: grid
// @complexities:
//   minAll: 1
//   minGteLte: 1
//   minLteGte: 1
//   minLteLte: 1
//   build: R*C
// @memory:
//   layout: none
//   node: tLteLte[1*R*C] tLteGte[1*R*C] tGteLte[1*R*C]
//   tags: none
//   other: none
//   note: one R by C table per corner direction, flat

// Static corner min: the min over a corner of the grid (every cell with row <= r or >= r, and column <= c or >= c) in
// O(1), from one R x C table per direction filled in a single pass (a cell's corner is its own row's running min
// joined with the corner of the cell one row back). No updates. Rows and columns are 0-based.
// T is any type with < (int, long long, double, ...).
template <typename T>
struct CornerMinTable2D {
    int R, C;
    T best;
    vector<T> tLteLte, tLteGte, tGteLte;

    // O(R*C) -- grid: R rows of C numbers each; needs R >= 1 and C >= 1, else throws invalid_argument
    explicit CornerMinTable2D(const vector<vector<T>>& grid)
        : R((int)grid.size()), C(grid.empty() ? 0 : (int)grid[0].size()) {
        if (R < 1 || C < 1) throw invalid_argument("CornerMinTable2D: needs R >= 1 and C >= 1");
        for (auto& row : grid)
            if ((int)row.size() != C) throw invalid_argument("CornerMinTable2D: every row needs the same C values");
        best = grid[0][0];
        for (auto& row : grid)
            for (const T& v : row) best = min(best, v);
        tLteLte.resize((size_t)R * C);
        for (int r = 0; r < R; r++) {
            T run = grid[r][0];
            bool hasBack = r > 0;
            size_t at = (size_t)r * C, back = at - C;
            for (int c = 0; c < C; c++) {
                run = min(run, grid[r][c]);
                tLteLte[at + c] = hasBack ? min(run, tLteLte[back + c]) : run;
            }
        }
        tLteGte.resize((size_t)R * C);
        for (int r = 0; r < R; r++) {
            T run = grid[r][C - 1];
            bool hasBack = r > 0;
            size_t at = (size_t)r * C, back = at - C;
            for (int c = C - 1; c >= 0; c--) {
                run = min(run, grid[r][c]);
                tLteGte[at + c] = hasBack ? min(run, tLteGte[back + c]) : run;
            }
        }
        tGteLte.resize((size_t)R * C);
        for (int r = R - 1; r >= 0; r--) {
            T run = grid[r][0];
            bool hasBack = r < R - 1;
            size_t at = (size_t)r * C, back = at + C;
            for (int c = 0; c < C; c++) {
                run = min(run, grid[r][c]);
                tGteLte[at + c] = hasBack ? min(run, tGteLte[back + c]) : run;
            }
        }
    }

    // O(1) -- min of the cells with row <= r and column <= c; needs 0 <= r < R and 0 <= c < C, else throws out_of_range
    T minLteLte(int r, int c) const {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("minLteLte: needs 0 <= r < R and 0 <= c < C");
        return tLteLte[(size_t)r * C + c];
    }

    // O(1) -- min of the cells with row <= r and column >= c; needs 0 <= r < R and 0 <= c < C, else throws out_of_range
    T minLteGte(int r, int c) const {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("minLteGte: needs 0 <= r < R and 0 <= c < C");
        return tLteGte[(size_t)r * C + c];
    }

    // O(1) -- min of the cells with row >= r and column <= c; needs 0 <= r < R and 0 <= c < C, else throws out_of_range
    T minGteLte(int r, int c) const {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("minGteLte: needs 0 <= r < R and 0 <= c < C");
        return tGteLte[(size_t)r * C + c];
    }

    // O(1) -- min of the whole grid
    T minAll() const {
        return best;
    }
};
