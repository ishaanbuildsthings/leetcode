// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries-2d/grid-seg-tree-gcd-or/template.cpp
#include <bits/stdc++.h>
using namespace std;
// @operations: gcdAll orAll pointAdd pointAssign pointChmax pointChmin pointGet rectGcd rectOr
// @data-structure-type: seg-tree
// @input: grid
// @complexities:
//   gcdAll: 1
//   orAll: 1
//   pointAdd: log(R)*log(C)*log(U) ?
//   pointAssign: log(R)*log(C)*log(U) ?
//   pointChmax: log(R)*log(C)*log(U) ?
//   pointChmin: log(R)*log(C)*log(U) ?
//   pointGet: 1
//   rectGcd: log(R)*log(C)+log(U) ?
//   rectOr: log(R)*log(C)
//   build: R*C*log(U) ?
// @memory:
//   layout: 2n-iterative
//   node: gc[4*R*C] orr[4*R*C]
//   tags: none
//   other: none
//   note: one flat array per aggregate, 2R row-nodes by 2C column-nodes; the cells are the last R row-nodes' last C entries

// 2D segment tree (gcd, OR): point updates and any-rectangle queries on an R x C grid, O(log R * log C) each. A tree
// over the rows whose every node is a tree over the columns, bottom-up, in one flat array per aggregate. Rows and
// columns are 0-based and rectangles are inclusive: rows r1..r2, columns c1..c2. The (R, C) constructor starts with
// every cell 0.
// T is any integer type (int, long long, ...).
template <typename T>
struct SegTree2D {
    int R, C, W;
    vector<T> gc;
    vector<T> orr;

    static T gcdOf(T a, T b) { return std::gcd(a, b); }

    // O(R*C) -- R rows by C columns, every cell 0; needs R >= 1 and C >= 1, else throws invalid_argument
    SegTree2D(int rows, int cols) : R(rows), C(cols), W(2 * cols) {
        if (R < 1 || C < 1) throw invalid_argument("SegTree2D: needs R >= 1 and C >= 1");
        gc.assign((size_t)2 * R * W, T(0));
        orr.assign((size_t)2 * R * W, T(0));
    }

    // O(R*C) -- grid: R rows of C values each; needs R >= 1 and C >= 1, else throws invalid_argument
    explicit SegTree2D(const vector<vector<T>>& grid)
        : SegTree2D((int)grid.size(), grid.empty() ? 0 : (int)grid[0].size()) {
        for (int r = 0; r < R; r++) {
            if ((int)grid[r].size() != C) throw invalid_argument("SegTree2D: every row needs the same C values");
            int base = (r + R) * W;
            for (int c = 0; c < C; c++) {
                gc[base + C + c] = grid[r][c];
                orr[base + C + c] = grid[r][c];
            }
            for (int pc = C - 1; pc >= 1; pc--) {
                gc[base + pc] = gcdOf(gc[base + 2 * pc], gc[base + 2 * pc + 1]);
                orr[base + pc] = orr[base + 2 * pc] | orr[base + 2 * pc + 1];
            }
        }
        for (int pr = R - 1; pr >= 1; pr--) {
            int base = pr * W, lo = 2 * base, hi = lo + W;
            for (int pc = 1; pc < W; pc++) {
                gc[base + pc] = gcdOf(gc[lo + pc], gc[hi + pc]);
                orr[base + pc] = orr[lo + pc] | orr[hi + pc];
            }
        }
    }

    // cell (r, c) = v, then every node above it
    void setCell(int r, int c, T v) {
        int base = (r + R) * W;
        gc[base + c + C] = v;
        orr[base + c + C] = v;
        for (int pc = (c + C) >> 1; pc >= 1; pc >>= 1) {
            gc[base + pc] = gcdOf(gc[base + 2 * pc], gc[base + 2 * pc + 1]);
            orr[base + pc] = orr[base + 2 * pc] | orr[base + 2 * pc + 1];
        }
        for (int pr = (r + R) >> 1; pr >= 1; pr >>= 1) {
            base = pr * W;
            int lo = 2 * base, hi = lo + W;
            for (int pc = c + C; pc >= 1; pc >>= 1) {
                gc[base + pc] = gcdOf(gc[lo + pc], gc[hi + pc]);
                orr[base + pc] = orr[lo + pc] | orr[hi + pc];
            }
        }
    }

    // O(1) -- the value at (r, c); needs 0 <= r < R and 0 <= c < C, else throws out_of_range
    T pointGet(int r, int c) const {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("pointGet: needs 0 <= r < R and 0 <= c < C");
        return T(orr[(r + R) * W + c + C]);
    }

    // O(log R * log C) gcds -- the cell at (r, c) becomes v (it may go down as well as up); needs 0 <= r < R and 0 <=
    // c < C, else throws out_of_range
    void pointAssign(int r, int c, T v) {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("pointAssign: needs 0 <= r < R and 0 <= c < C");
        setCell(r, c, v);
    }

    // O(log R * log C) gcds -- adds v to the cell at (r, c); needs 0 <= r < R and 0 <= c < C, else throws out_of_range
    void pointAdd(int r, int c, T v) {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("pointAdd: needs 0 <= r < R and 0 <= c < C");
        T cur = T(orr[(r + R) * W + c + C]);
        setCell(r, c, T(cur + v));
    }

    // O(log R * log C) gcds -- the cell at (r, c) becomes max(itself, v); needs 0 <= r < R and 0 <= c < C, else
    // throws out_of_range
    void pointChmax(int r, int c, T v) {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("pointChmax: needs 0 <= r < R and 0 <= c < C");
        T cur = T(orr[(r + R) * W + c + C]);
        if (v > cur) setCell(r, c, v);
    }

    // O(log R * log C) gcds -- the cell at (r, c) becomes min(itself, v); needs 0 <= r < R and 0 <= c < C, else
    // throws out_of_range
    void pointChmin(int r, int c, T v) {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("pointChmin: needs 0 <= r < R and 0 <= c < C");
        T cur = T(orr[(r + R) * W + c + C]);
        if (v < cur) setCell(r, c, v);
    }

    T gcdOf(int r1, int c1, int r2, int c2) const {
        T res = T(0);
        int cl = c1 + C, cr = c2 + C + 1;
        for (int lr = r1 + R, rr = r2 + R + 1; lr < rr; lr >>= 1, rr >>= 1) {
            if (lr & 1) {
                int base = lr++ * W;
                for (int lc = cl, rc = cr; lc < rc; lc >>= 1, rc >>= 1) {
                    if (lc & 1) res = gcdOf(res, gc[base + lc++]);
                    if (rc & 1) res = gcdOf(res, gc[base + --rc]);
                }
            }
            if (rr & 1) {
                int base = --rr * W;
                for (int lc = cl, rc = cr; lc < rc; lc >>= 1, rc >>= 1) {
                    if (lc & 1) res = gcdOf(res, gc[base + lc++]);
                    if (rc & 1) res = gcdOf(res, gc[base + --rc]);
                }
            }
        }
        return res;
    }

    // O(log R * log C + log U) -- gcd of rows r1..r2, columns c1..c2; needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C,
    // else
    // throws out_of_range
    T rectGcd(int r1, int c1, int r2, int c2) const {
        if (r1 < 0 || r1 > r2 || r2 >= R || c1 < 0 || c1 > c2 || c2 >= C)
            throw out_of_range("rectGcd: needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C");
        return gcdOf(r1, c1, r2, c2);
    }

    // O(1) -- gcd of the whole grid
    T gcdAll() const {
        return gcdOf(gc[W + 1], T(0));
    }

    T orOf(int r1, int c1, int r2, int c2) const {
        T res = T(0);
        int cl = c1 + C, cr = c2 + C + 1;
        for (int lr = r1 + R, rr = r2 + R + 1; lr < rr; lr >>= 1, rr >>= 1) {
            if (lr & 1) {
                int base = lr++ * W;
                for (int lc = cl, rc = cr; lc < rc; lc >>= 1, rc >>= 1) {
                    if (lc & 1) res |= orr[base + lc++];
                    if (rc & 1) res |= orr[base + --rc];
                }
            }
            if (rr & 1) {
                int base = --rr * W;
                for (int lc = cl, rc = cr; lc < rc; lc >>= 1, rc >>= 1) {
                    if (lc & 1) res |= orr[base + lc++];
                    if (rc & 1) res |= orr[base + --rc];
                }
            }
        }
        return res;
    }

    // O(log R * log C) -- OR of rows r1..r2, columns c1..c2; needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C, else throws
    // out_of_range
    T rectOr(int r1, int c1, int r2, int c2) const {
        if (r1 < 0 || r1 > r2 || r2 >= R || c1 < 0 || c1 > c2 || c2 >= C)
            throw out_of_range("rectOr: needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C");
        return orOf(r1, c1, r2, c2);
    }

    // O(1) -- OR of the whole grid
    T orAll() const {
        return orr[W + 1];
    }
};
