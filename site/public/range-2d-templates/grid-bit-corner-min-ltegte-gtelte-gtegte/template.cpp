// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries-2d/grid-bit-corner-min-ltegte-gtelte-gtegte/template.cpp
#include <bits/stdc++.h>
using namespace std;
// @operations: minAll minGteGte minGteLte minLteGte pointChmin
// @data-structure-type: BIT
// @input: grid
// @empty-cells: yes
// @complexities:
//   minAll: 1
//   minGteGte: log(R)*log(C)
//   minGteLte: log(R)*log(C)
//   minLteGte: log(R)*log(C)
//   pointChmin: log(R)*log(C)
//   build: R*C
// @memory:
//   layout: none
//   node: tLteGte[1*R*C] tGteLte[1*R*C] tGteGte[1*R*C]
//   tags: none
//   other: none
//   note: one Fenwick tree per corner direction, each (R + 1) by (C + 1), flat; a >= direction is the same tree with that axis mirrored

// Corner min with a 2D Fenwick tree: pointChmin at a cell and the min over a corner of the grid (every cell with row
// <= r or >= r, and column <= c or >= c), O(log R * log C) each, with a quarter of a 2D segment tree's memory per
// direction and a much smaller constant. This works because values only move one way: a cell can only go down
// (pointChmin), so a tree entry never has to forget a value. For a cell that can move both ways, or for rectangles
// that aren't corners, use the 2D segment tree. A cell can be empty and queries only see set cells. Rows and columns
// are 0-based. The (R, C) constructor starts with every cell empty, and a min over no set cell is NO_MIN.
// T is any integer type (int, long long, ...).
template <typename T>
struct CornerMinFenwick2D {
    static constexpr T NO_MIN = numeric_limits<T>::max();  // what a min over no set cell gives
    int R, C, W;
    T best = NO_MIN;
    vector<T> tLteGte, tGteLte, tGteGte;

    // O(R*C) -- R rows by C columns, every cell empty; needs R >= 1 and C >= 1, else throws invalid_argument
    CornerMinFenwick2D(int rows, int cols) : R(rows), C(cols), W(cols + 1) {
        if (R < 1 || C < 1) throw invalid_argument("CornerMinFenwick2D: needs R >= 1 and C >= 1");
        tLteGte.assign((size_t)(R + 1) * W, NO_MIN);
        tGteLte.assign((size_t)(R + 1) * W, NO_MIN);
        tGteGte.assign((size_t)(R + 1) * W, NO_MIN);
    }

    // O(R*C) -- grid: R rows of C values each, every cell set; needs R >= 1 and C >= 1, else throws invalid_argument
    explicit CornerMinFenwick2D(const vector<vector<T>>& grid)
        : CornerMinFenwick2D((int)grid.size(), grid.empty() ? 0 : (int)grid[0].size()) {
        for (auto& row : grid)
            if ((int)row.size() != C) throw invalid_argument("CornerMinFenwick2D: every row needs the same C values");
        for (auto& row : grid)
            for (T v : row) best = min(best, v);
        for (int r = 0; r < R; r++)
            for (int c = 0; c < C; c++) tLteGte[(r + 1) * W + C - c] = grid[r][c];
        for (int r = 0; r < R; r++)
            for (int c = 0; c < C; c++) tGteLte[(R - r) * W + c + 1] = grid[r][c];
        for (int r = 0; r < R; r++)
            for (int c = 0; c < C; c++) tGteGte[(R - r) * W + C - c] = grid[r][c];
        for (auto* t : {&tLteGte, &tGteLte, &tGteGte}) {
            for (int i = 1; i <= R; i++)
                for (int j = 1; j <= C; j++) {
                    int p = j + (j & -j);  // each entry is folded into the next one that covers it
                    if (p <= C) (*t)[i * W + p] = min((*t)[i * W + p], (*t)[i * W + j]);
                }
            for (int i = 1; i <= R; i++) {
                int p = i + (i & -i);
                if (p > R) continue;
                for (int j = 1; j <= C; j++) (*t)[p * W + j] = min((*t)[p * W + j], (*t)[i * W + j]);
            }
        }
    }

    // O(log R * log C) -- the cell at (r, c) becomes min(itself, v); an empty cell becomes v; needs 0 <= r < R and 0
    // <= c
    // < C, else throws out_of_range
    void pointChmin(int r, int c, T v) {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("pointChmin: needs 0 <= r < R and 0 <= c < C");
        best = min(best, v);
        for (int i = r + 1; i <= R; i += i & -i)
            for (int j = C - c; j <= C; j += j & -j) tLteGte[i * W + j] = min(tLteGte[i * W + j], v);
        for (int i = R - r; i <= R; i += i & -i)
            for (int j = c + 1; j <= C; j += j & -j) tGteLte[i * W + j] = min(tGteLte[i * W + j], v);
        for (int i = R - r; i <= R; i += i & -i)
            for (int j = C - c; j <= C; j += j & -j) tGteGte[i * W + j] = min(tGteGte[i * W + j], v);
    }

    // O(log R * log C) -- min of the set cells with row <= r and column >= c (NO_MIN if there are none); needs 0 <= r
    // < R
    // and 0 <= c < C, else throws out_of_range
    T minLteGte(int r, int c) const {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("minLteGte: needs 0 <= r < R and 0 <= c < C");
        T res = NO_MIN;
        for (int i = r + 1; i > 0; i &= i - 1)
            for (int j = C - c; j > 0; j &= j - 1) res = min(res, tLteGte[i * W + j]);
        return res;
    }

    // O(log R * log C) -- min of the set cells with row >= r and column <= c (NO_MIN if there are none); needs 0 <= r
    // < R
    // and 0 <= c < C, else throws out_of_range
    T minGteLte(int r, int c) const {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("minGteLte: needs 0 <= r < R and 0 <= c < C");
        T res = NO_MIN;
        for (int i = R - r; i > 0; i &= i - 1)
            for (int j = c + 1; j > 0; j &= j - 1) res = min(res, tGteLte[i * W + j]);
        return res;
    }

    // O(log R * log C) -- min of the set cells with row >= r and column >= c (NO_MIN if there are none); needs 0 <= r
    // < R
    // and 0 <= c < C, else throws out_of_range
    T minGteGte(int r, int c) const {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("minGteGte: needs 0 <= r < R and 0 <= c < C");
        T res = NO_MIN;
        for (int i = R - r; i > 0; i &= i - 1)
            for (int j = C - c; j > 0; j &= j - 1) res = min(res, tGteGte[i * W + j]);
        return res;
    }

    // O(1) -- min of every set cell (NO_MIN if there are none)
    T minAll() const {
        return best;
    }
};
