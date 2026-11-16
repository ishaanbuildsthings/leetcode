// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries-2d/grid-kept-tags-max/template.cpp
#include <bits/stdc++.h>
using namespace std;
// @operations: maxAll maxGteGte maxGteLte maxLteGte maxLteLte pointChmax pointGet rectChmax rectMax
// @data-structure-type: seg-tree-kept-tags
// @input: grid
// @empty-cells: yes
// @complexities:
//   maxAll: 1
//   maxGteGte: log(R)*log(C)
//   maxGteLte: log(R)*log(C)
//   maxLteGte: log(R)*log(C)
//   maxLteLte: log(R)*log(C)
//   pointChmax: log(R)*log(C)
//   pointGet: log(R)*log(C)
//   rectChmax: log(R)*log(C)
//   rectMax: log(R)*log(C)
//   build: R*C
// @memory:
//   layout: 2n-iterative
//   node: fullBest[4*R*C] partBest[4*R*C]
//   tags: fullTag[4*R*C] partTag[4*R*C]
//   other: none
//   note: per row-node two column trees (updates covering all of its rows; updates touching any of its rows), each a tag array and a best-below array, 2R row-nodes by 2C column-nodes, flat

// Rectangle chmax and rectangle max on an R x C grid, O(log R * log C) each: a 2D segment tree whose tags stay where
// they are put (no push-down, which a tree of trees can't do). rectChmax(r1, c1, r2, c2, v) makes every cell of the
// rectangle max(itself, v). Every row-node keeps two column trees: one for the updates that cover all of its rows,
// and one for the updates that touch any of its rows. A query takes, from the row-nodes that make up its rows, the
// second kind, and from the row-nodes above those, the first kind (an update covering a whole row-node above covers
// the query's rows too). Each column tree works the same way one level down. This only works because chmax never has
// to be undone: there is no rectangle assign or add here. A cell can be empty and queries only see set cells. Rows
// and columns are 0-based and rectangles are inclusive: rows r1..r2, columns c1..c2. The (R, C) constructor starts
// with every cell empty, and a max over no set cell is NO_MAX.
// T is any integer type (int, long long, ...).
template <typename T>
struct RectChmaxRectMax2D {
    static constexpr T NO_MAX = numeric_limits<T>::min();  // what a max over no set cell gives
    int R, C, W;
    T best = NO_MAX;
    vector<T> fullTag, fullBest, partTag, partBest;

    // O(R*C) -- R rows by C columns, every cell empty; needs R >= 1 and C >= 1, else throws invalid_argument
    RectChmaxRectMax2D(int rows, int cols) : R(rows), C(cols), W(2 * cols) {
        if (R < 1 || C < 1) throw invalid_argument("RectChmaxRectMax2D: needs R >= 1 and C >= 1");
        fullTag.assign((size_t)2 * R * W, NO_MAX);
        fullBest = partTag = partBest = fullTag;
    }

    // O(R*C) -- grid: R rows of C values each, every cell set; needs R >= 1 and C >= 1, else throws invalid_argument
    explicit RectChmaxRectMax2D(const vector<vector<T>>& grid)
        : RectChmaxRectMax2D((int)grid.size(), grid.empty() ? 0 : (int)grid[0].size()) {
        for (int r = 0; r < R; r++) {
            if ((int)grid[r].size() != C)
                throw invalid_argument("RectChmaxRectMax2D: every row needs the same C values");
            int base = (r + R) * W;
            for (int c = 0; c < C; c++) {
                fullBest[base + C + c] = grid[r][c];
                best = max(best, grid[r][c]);
            }
            for (int pc = C - 1; pc >= 1; pc--)
                fullBest[base + pc] = max(fullBest[base + 2 * pc], fullBest[base + 2 * pc + 1]);
        }
        partBest = fullBest;  // a single row: the two trees agree
        for (int pr = R - 1; pr >= 1; pr--) {
            int base = pr * W, lo = 2 * base, hi = lo + W;
            for (int pc = 1; pc < W; pc++) partBest[base + pc] = max(partBest[lo + pc], partBest[hi + pc]);
        }
    }

    // one column tree (the one starting at `base`): columns c1..c2 become max(themselves, v)
    void colsUpdate(vector<T>& tag, vector<T>& bst, int base, int c1, int c2, T v) {
        int lc = c1 + C, rc = c2 + C + 1;
        // every node above the two ends has v somewhere below it now
        for (int a = lc >> 1; a >= 1; a >>= 1) bst[base + a] = max(bst[base + a], v);
        for (int b = (rc - 1) >> 1; b >= 1; b >>= 1) bst[base + b] = max(bst[base + b], v);
        for (; lc < rc; lc >>= 1, rc >>= 1) {
            if (lc & 1) {
                tag[base + lc] = max(tag[base + lc], v);
                bst[base + lc] = max(bst[base + lc], v);
                lc++;
            }
            if (rc & 1) {
                --rc;
                tag[base + rc] = max(tag[base + rc], v);
                bst[base + rc] = max(bst[base + rc], v);
            }
        }
    }

    // one column tree: the max over columns c1..c2
    T colsQuery(const vector<T>& tag, const vector<T>& bst, int base, int c1, int c2) const {
        int lc = c1 + C, rc = c2 + C + 1;
        T res = NO_MAX;
        // a tag on a node above either end covers that end, which is inside c1..c2
        for (int a = lc >> 1; a >= 1; a >>= 1) res = max(res, tag[base + a]);
        for (int b = (rc - 1) >> 1; b >= 1; b >>= 1) res = max(res, tag[base + b]);
        for (; lc < rc; lc >>= 1, rc >>= 1) {
            if (lc & 1) res = max(res, bst[base + lc++]);
            if (rc & 1) res = max(res, bst[base + --rc]);
        }
        return res;
    }

    void update(int r1, int c1, int r2, int c2, T v) {
        best = max(best, v);
        int lr = r1 + R, rr = r2 + R + 1;
        // every row-node above the two ends is touched
        for (int a = lr >> 1; a >= 1; a >>= 1) colsUpdate(partTag, partBest, a * W, c1, c2, v);
        for (int b = (rr - 1) >> 1; b >= 1; b >>= 1) colsUpdate(partTag, partBest, b * W, c1, c2, v);
        for (; lr < rr; lr >>= 1, rr >>= 1) {
            if (lr & 1) {
                colsUpdate(fullTag, fullBest, lr * W, c1, c2, v);
                colsUpdate(partTag, partBest, lr * W, c1, c2, v);
                lr++;
            }
            if (rr & 1) {
                --rr;
                colsUpdate(fullTag, fullBest, rr * W, c1, c2, v);
                colsUpdate(partTag, partBest, rr * W, c1, c2, v);
            }
        }
    }

    T query(int r1, int c1, int r2, int c2) const {
        T res = NO_MAX;
        int lr = r1 + R, rr = r2 + R + 1;
        // an update covering a whole row-node above either end covers that end's row
        for (int a = lr >> 1; a >= 1; a >>= 1) res = max(res, colsQuery(fullTag, fullBest, a * W, c1, c2));
        for (int b = (rr - 1) >> 1; b >= 1; b >>= 1) res = max(res, colsQuery(fullTag, fullBest, b * W, c1, c2));
        for (; lr < rr; lr >>= 1, rr >>= 1) {
            if (lr & 1) res = max(res, colsQuery(partTag, partBest, lr++ * W, c1, c2));
            if (rr & 1) res = max(res, colsQuery(partTag, partBest, --rr * W, c1, c2));
        }
        return res;
    }

    // O(log R * log C) -- every cell of rows r1..r2, columns c1..c2 becomes max(itself, v); an empty cell becomes v;
    // needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C, else throws out_of_range
    void rectChmax(int r1, int c1, int r2, int c2, T v) {
        if (r1 < 0 || r1 > r2 || r2 >= R || c1 < 0 || c1 > c2 || c2 >= C)
            throw out_of_range("rectChmax: needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C");
        update(r1, c1, r2, c2, v);
    }

    // O(log R * log C) -- the cell at (r, c) becomes max(itself, v); an empty cell becomes v; needs 0 <= r < R and 0
    // <= c
    // < C, else throws out_of_range
    void pointChmax(int r, int c, T v) {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("pointChmax: needs 0 <= r < R and 0 <= c < C");
        update(r, c, r, c, v);
    }

    // O(log R * log C) -- the value at (r, c), NO_MAX if the cell is empty; needs 0 <= r < R and 0 <= c < C, else
    // throws
    // out_of_range
    T pointGet(int r, int c) const {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("pointGet: needs 0 <= r < R and 0 <= c < C");
        return query(r, c, r, c);
    }

    // O(log R * log C) -- max of the set cells in rows r1..r2, columns c1..c2 (NO_MAX if there are none); needs 0 <= r1
    // <= r2 < R and 0 <= c1 <= c2 < C, else throws out_of_range
    T rectMax(int r1, int c1, int r2, int c2) const {
        if (r1 < 0 || r1 > r2 || r2 >= R || c1 < 0 || c1 > c2 || c2 >= C)
            throw out_of_range("rectMax: needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C");
        return query(r1, c1, r2, c2);
    }

    // O(log R * log C) -- max of the set cells with row <= r and column <= c (NO_MAX if there are none); needs 0 <= r
    // < R
    // and 0 <= c < C, else throws out_of_range
    T maxLteLte(int r, int c) const {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("maxLteLte: needs 0 <= r < R and 0 <= c < C");
        return query(0, 0, r, c);
    }

    // O(log R * log C) -- max of the set cells with row <= r and column >= c (NO_MAX if there are none); needs 0 <= r
    // < R
    // and 0 <= c < C, else throws out_of_range
    T maxLteGte(int r, int c) const {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("maxLteGte: needs 0 <= r < R and 0 <= c < C");
        return query(0, c, r, C - 1);
    }

    // O(log R * log C) -- max of the set cells with row >= r and column <= c (NO_MAX if there are none); needs 0 <= r
    // < R
    // and 0 <= c < C, else throws out_of_range
    T maxGteLte(int r, int c) const {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("maxGteLte: needs 0 <= r < R and 0 <= c < C");
        return query(r, 0, R - 1, c);
    }

    // O(log R * log C) -- max of the set cells with row >= r and column >= c (NO_MAX if there are none); needs 0 <= r
    // < R
    // and 0 <= c < C, else throws out_of_range
    T maxGteGte(int r, int c) const {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("maxGteGte: needs 0 <= r < R and 0 <= c < C");
        return query(r, c, R - 1, C - 1);
    }

    // O(1) -- max of every set cell (NO_MAX if there are none)
    T maxAll() const {
        return best;
    }
};
