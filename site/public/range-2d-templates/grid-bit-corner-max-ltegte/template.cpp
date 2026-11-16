// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries-2d/grid-bit-corner-max-ltegte/template.cpp
#include <bits/stdc++.h>
using namespace std;
// @operations: maxAll maxLteGte pointChmax
// @data-structure-type: BIT
// @input: grid
// @empty-cells: yes
// @complexities:
//   maxAll: 1
//   maxLteGte: log(R)*log(C)
//   pointChmax: log(R)*log(C)
//   build: R*C
// @memory:
//   layout: none
//   node: tLteGte[1*R*C]
//   tags: none
//   other: none
//   note: one Fenwick tree per corner direction, each (R + 1) by (C + 1), flat; a >= direction is the same tree with that axis mirrored

// Corner max with a 2D Fenwick tree: pointChmax at a cell and the max over a corner of the grid (every cell with row
// <= r or >= r, and column <= c or >= c), O(log R * log C) each, with a quarter of a 2D segment tree's memory per
// direction and a much smaller constant. This works because values only move one way: a cell can only go up
// (pointChmax), so a tree entry never has to forget a value. For a cell that can move both ways, or for rectangles
// that aren't corners, use the 2D segment tree. A cell can be empty and queries only see set cells. Rows and columns
// are 0-based. The (R, C) constructor starts with every cell empty, and a max over no set cell is NO_MAX.
// T is any integer type (int, long long, ...).
template <typename T>
struct CornerMaxFenwick2D {
    static constexpr T NO_MAX = numeric_limits<T>::min();  // what a max over no set cell gives
    int R, C, W;
    T best = NO_MAX;
    vector<T> tLteGte;

    // O(R*C) -- R rows by C columns, every cell empty; needs R >= 1 and C >= 1, else throws invalid_argument
    CornerMaxFenwick2D(int rows, int cols) : R(rows), C(cols), W(cols + 1) {
        if (R < 1 || C < 1) throw invalid_argument("CornerMaxFenwick2D: needs R >= 1 and C >= 1");
        tLteGte.assign((size_t)(R + 1) * W, NO_MAX);
    }

    // O(R*C) -- grid: R rows of C values each, every cell set; needs R >= 1 and C >= 1, else throws invalid_argument
    explicit CornerMaxFenwick2D(const vector<vector<T>>& grid)
        : CornerMaxFenwick2D((int)grid.size(), grid.empty() ? 0 : (int)grid[0].size()) {
        for (auto& row : grid)
            if ((int)row.size() != C) throw invalid_argument("CornerMaxFenwick2D: every row needs the same C values");
        for (auto& row : grid)
            for (T v : row) best = max(best, v);
        for (int r = 0; r < R; r++)
            for (int c = 0; c < C; c++) tLteGte[(r + 1) * W + C - c] = grid[r][c];
        for (auto* t : {&tLteGte}) {
            for (int i = 1; i <= R; i++)
                for (int j = 1; j <= C; j++) {
                    int p = j + (j & -j);  // each entry is folded into the next one that covers it
                    if (p <= C) (*t)[i * W + p] = max((*t)[i * W + p], (*t)[i * W + j]);
                }
            for (int i = 1; i <= R; i++) {
                int p = i + (i & -i);
                if (p > R) continue;
                for (int j = 1; j <= C; j++) (*t)[p * W + j] = max((*t)[p * W + j], (*t)[i * W + j]);
            }
        }
    }

    // O(log R * log C) -- the cell at (r, c) becomes max(itself, v); an empty cell becomes v; needs 0 <= r < R and 0
    // <= c
    // < C, else throws out_of_range
    void pointChmax(int r, int c, T v) {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("pointChmax: needs 0 <= r < R and 0 <= c < C");
        best = max(best, v);
        for (int i = r + 1; i <= R; i += i & -i)
            for (int j = C - c; j <= C; j += j & -j) tLteGte[i * W + j] = max(tLteGte[i * W + j], v);
    }

    // O(log R * log C) -- max of the set cells with row <= r and column >= c (NO_MAX if there are none); needs 0 <= r
    // < R
    // and 0 <= c < C, else throws out_of_range
    T maxLteGte(int r, int c) const {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("maxLteGte: needs 0 <= r < R and 0 <= c < C");
        T res = NO_MAX;
        for (int i = r + 1; i > 0; i &= i - 1)
            for (int j = C - c; j > 0; j &= j - 1) res = max(res, tLteGte[i * W + j]);
        return res;
    }

    // O(1) -- max of every set cell (NO_MAX if there are none)
    T maxAll() const {
        return best;
    }
};
