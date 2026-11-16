// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries-2d/grid-bit-rect-add/template.cpp
#include <bits/stdc++.h>
using namespace std;
// @operations: pointAdd pointAssign pointChmax pointChmin pointGet rectAdd
// @data-structure-type: BIT
// @input: grid
// @complexities:
//   pointAdd: log(R)*log(C)
//   pointAssign: log(R)*log(C)
//   pointChmax: log(R)*log(C)
//   pointChmin: log(R)*log(C)
//   pointGet: log(R)*log(C)
//   rectAdd: log(R)*log(C)
//   build: R*C
// @memory:
//   layout: none
//   node: bit[1*R*C]
//   tags: none
//   other: none
//   note: one Fenwick tree over the marks a rectangle add leaves at its four corners; each is (R + 1) by (C + 1), flat

// Rectangle add and point read on an R x C grid with one 2D Fenwick tree, O(log R * log C) each. An add of v on rows
// r1..r2, columns c1..c2 leaves four marks, +v at (r1, c1) and (r2 + 1, c2 + 1), -v at (r1, c2 + 1) and (r2 + 1, c1);
// a cell's value is the sum of the marks above-left of it, a prefix query. When every add comes before any read, the
// difference array does this in O(1) per add. Rows and columns are 0-based and rectangles are inclusive. The (R, C)
// constructor starts with every cell 0.
// T is any integer type (int, long long, ...); sums are kept in S (long long for a smaller T).
template <typename T>
struct RectAddFenwick2D {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    int R, C, W;
    vector<S> bit;

    // O(R*C) -- R rows by C columns, every cell 0; needs R >= 1 and C >= 1, else throws invalid_argument
    RectAddFenwick2D(int rows, int cols) : R(rows), C(cols), W(cols + 1) {
        if (R < 1 || C < 1) throw invalid_argument("RectAddFenwick2D: needs R >= 1 and C >= 1");
        bit.assign((size_t)(R + 1) * W, 0);
    }

    // O(R*C) -- grid: R rows of C numbers each; needs R >= 1 and C >= 1, else throws invalid_argument
    explicit RectAddFenwick2D(const vector<vector<T>>& grid)
        : RectAddFenwick2D((int)grid.size(), grid.empty() ? 0 : (int)grid[0].size()) {
        for (auto& row : grid)
            if ((int)row.size() != C) throw invalid_argument("RectAddFenwick2D: every row needs the same C values");
        for (int r = 0; r < R; r++) {
            for (int c = 0; c < C; c++) {
                // the mark that makes this cell's value come out right
                S left = c ? S(grid[r][c - 1]) : 0, up = r ? S(grid[r - 1][c]) : 0;
                S upLeft = r && c ? S(grid[r - 1][c - 1]) : 0;
                S d = S(grid[r][c]) - left - up + upLeft;
                size_t at = (size_t)(r + 1) * W + c + 1;
                bit[at] = d;
            }
        }
        for (auto* t : {&bit}) {
            for (int r = 1; r <= R; r++)
                for (int c = 1; c <= C; c++) {
                    int j = c + (c & -c);
                    if (j <= C) (*t)[r * W + j] += (*t)[r * W + c];
                }
            for (int r = 1; r <= R; r++) {
                int j = r + (r & -r);
                if (j > R) continue;
                for (int c = 1; c <= C; c++) (*t)[j * W + c] += (*t)[r * W + c];
            }
        }
    }

    // a mark d at (r, c): every cell at or below-right of it gains d
    void mark(int r, int c, S d) {
        for (int i = r + 1; i <= R; i += i & -i)
            for (int j = c + 1; j <= C; j += j & -j) bit[i * W + j] += d;
    }

    void addRect(int r1, int c1, int r2, int c2, S v) {
        mark(r1, c1, v);
        if (c2 + 1 < C) mark(r1, c2 + 1, -v);
        if (r2 + 1 < R) mark(r2 + 1, c1, -v);
        if (r2 + 1 < R && c2 + 1 < C) mark(r2 + 1, c2 + 1, v);
    }

    S get(int r, int c) const {
        S res = 0;
        for (int i = r + 1; i > 0; i &= i - 1)
            for (int j = c + 1; j > 0; j &= j - 1) res += bit[i * W + j];
        return res;
    }

    // O(log R * log C) -- adds v to every cell of rows r1..r2, columns c1..c2; needs 0 <= r1 <= r2 < R and 0 <= c1 <=
    // c2
    // < C, else throws out_of_range
    void rectAdd(int r1, int c1, int r2, int c2, T v) {
        if (r1 < 0 || r1 > r2 || r2 >= R || c1 < 0 || c1 > c2 || c2 >= C)
            throw out_of_range("rectAdd: needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C");
        addRect(r1, c1, r2, c2, v);
    }

    // O(log R * log C) -- the value at (r, c); needs 0 <= r < R and 0 <= c < C, else throws out_of_range
    T pointGet(int r, int c) const {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("pointGet: needs 0 <= r < R and 0 <= c < C");
        return T(get(r, c));
    }

    // O(log R * log C) -- the cell at (r, c) becomes v; needs 0 <= r < R and 0 <= c < C, else throws out_of_range
    void pointAssign(int r, int c, T v) {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("pointAssign: needs 0 <= r < R and 0 <= c < C");
        addRect(r, c, r, c, S(v) - get(r, c));
    }

    // O(log R * log C) -- adds v to the cell at (r, c); needs 0 <= r < R and 0 <= c < C, else throws out_of_range
    void pointAdd(int r, int c, T v) {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("pointAdd: needs 0 <= r < R and 0 <= c < C");
        addRect(r, c, r, c, v);
    }

    // O(log R * log C) -- the cell at (r, c) becomes max(itself, v); needs 0 <= r < R and 0 <= c < C, else throws
    // out_of_range
    void pointChmax(int r, int c, T v) {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("pointChmax: needs 0 <= r < R and 0 <= c < C");
        S cur = get(r, c);
        if (S(v) > cur) addRect(r, c, r, c, S(v) - cur);
    }

    // O(log R * log C) -- the cell at (r, c) becomes min(itself, v); needs 0 <= r < R and 0 <= c < C, else throws
    // out_of_range
    void pointChmin(int r, int c, T v) {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("pointChmin: needs 0 <= r < R and 0 <= c < C");
        S cur = get(r, c);
        if (S(v) < cur) addRect(r, c, r, c, S(v) - cur);
    }
};
