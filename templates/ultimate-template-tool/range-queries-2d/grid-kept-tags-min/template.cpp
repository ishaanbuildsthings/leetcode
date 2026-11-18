// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries-2d/grid-kept-tags-min/template.cpp
#include <bits/stdc++.h>
using namespace std;
// @operations: minAll minGteGte minGteLte minLteGte minLteLte pointChmin pointGet rectChmin rectMin
// @data-structure-type: seg-tree-kept-tags
// @input: grid
// @empty-cells: yes
// @complexities:
//   minAll: 1
//   minGteGte: log(R)*log(C)
//   minGteLte: log(R)*log(C)
//   minLteGte: log(R)*log(C)
//   minLteLte: log(R)*log(C)
//   pointChmin: log(R)*log(C)
//   pointGet: log(R)*log(C)
//   rectChmin: log(R)*log(C)
//   rectMin: log(R)*log(C)
//   build: R*C
// @memory:
//   layout: 2n-iterative
//   node: fullBest[4*R*C] partBest[4*R*C]
//   tags: fullTag[4*R*C] partTag[4*R*C]
//   other: none
//   note: per row-node two column trees (updates covering all of its rows; updates touching any of its rows), each a tag array and a best-below array, 2R row-nodes by 2C column-nodes, flat

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

// min / max that still inline with sanitizers skipped (std::min and std::max do not)
template <typename A>
LEETCODE_NO_SANITIZE_INLINE A hotMin(A a, A b) { return b < a ? b : a; }

// Rectangle chmin and rectangle min on an R x C grid, O(log R * log C) each: a 2D segment tree whose tags stay where
// they are put (no push-down, which a tree of trees can't do). rectChmin(r1, c1, r2, c2, v) makes every cell of the
// rectangle min(itself, v). Every row-node keeps two column trees: one for the updates that cover all of its rows,
// and one for the updates that touch any of its rows. A query takes, from the row-nodes that make up its rows, the
// second kind, and from the row-nodes above those, the first kind (an update covering a whole row-node above covers
// the query's rows too). Each column tree works the same way one level down. This only works because chmin never has
// to be undone: there is no rectangle assign or add here. A cell can be empty and queries only see set cells. Rows
// and columns are 0-based and rectangles are inclusive: rows r1..r2, columns c1..c2. The (R, C) constructor starts
// with every cell empty, and a min over no set cell is NO_MIN.
// T is any integer type (int, long long, ...).
template <typename T>
struct RectChminRectMin2D {
    static constexpr T NO_MIN = numeric_limits<T>::max();  // the largest value T can hold: a min over no set cell
    int R, C, W;
    T best = NO_MIN;
    HotVector<T> fullTag, fullBest, partTag, partBest;

    // O(R*C) -- R rows by C columns, every cell empty; needs R >= 1 and C >= 1, else throws invalid_argument
    RectChminRectMin2D(int rows, int cols) : R(rows), C(cols), W(2 * cols) {
        if (R < 1 || C < 1) throw invalid_argument("RectChminRectMin2D: needs R >= 1 and C >= 1");
        fullTag.assign((size_t)2 * R * W, NO_MIN);
        fullBest = partTag = partBest = fullTag;
    }

    // O(R*C) -- grid: R rows of C values each, every cell set; needs R >= 1 and C >= 1, else throws invalid_argument
    explicit RectChminRectMin2D(const vector<vector<T>>& grid)
        : RectChminRectMin2D((int)grid.size(), grid.empty() ? 0 : (int)grid[0].size()) {
        for (int r = 0; r < R; r++) {
            if ((int)grid[r].size() != C)
                throw invalid_argument("RectChminRectMin2D: every row needs the same C values");
            int base = (r + R) * W;
            for (int c = 0; c < C; c++) {
                fullBest[base + C + c] = grid[r][c];
                best = hotMin(best, grid[r][c]);
            }
            for (int pc = C - 1; pc >= 1; pc--)
                fullBest[base + pc] = hotMin(fullBest[base + 2 * pc], fullBest[base + 2 * pc + 1]);
        }
        partBest = fullBest;  // a single row: the two trees agree
        for (int pr = R - 1; pr >= 1; pr--) {
            int base = pr * W, lo = 2 * base, hi = lo + W;
            for (int pc = 1; pc < W; pc++) partBest[base + pc] = hotMin(partBest[lo + pc], partBest[hi + pc]);
        }
    }

    // one column tree (the one starting at `base`): columns c1..c2 become min(themselves, v)
    LEETCODE_NO_SANITIZE void colsUpdate(HotVector<T>& tag, HotVector<T>& bst, int base, int c1, int c2, T v) {
        int lc = c1 + C, rc = c2 + C + 1;
        // every node above the two ends has v somewhere below it now
        for (int a = lc >> 1; a >= 1; a >>= 1) bst[base + a] = hotMin(bst[base + a], v);
        for (int b = (rc - 1) >> 1; b >= 1; b >>= 1) bst[base + b] = hotMin(bst[base + b], v);
        for (; lc < rc; lc >>= 1, rc >>= 1) {
            if (lc & 1) {
                tag[base + lc] = hotMin(tag[base + lc], v);
                bst[base + lc] = hotMin(bst[base + lc], v);
                lc++;
            }
            if (rc & 1) {
                --rc;
                tag[base + rc] = hotMin(tag[base + rc], v);
                bst[base + rc] = hotMin(bst[base + rc], v);
            }
        }
    }

    // one column tree: the min over columns c1..c2
    LEETCODE_NO_SANITIZE T colsQuery(const HotVector<T>& tag, const HotVector<T>& bst, int base, int c1, int c2) const {
        int lc = c1 + C, rc = c2 + C + 1;
        T res = NO_MIN;
        // a tag on a node above either end covers that end, which is inside c1..c2
        for (int a = lc >> 1; a >= 1; a >>= 1) res = hotMin(res, tag[base + a]);
        for (int b = (rc - 1) >> 1; b >= 1; b >>= 1) res = hotMin(res, tag[base + b]);
        for (; lc < rc; lc >>= 1, rc >>= 1) {
            if (lc & 1) res = hotMin(res, bst[base + lc++]);
            if (rc & 1) res = hotMin(res, bst[base + --rc]);
        }
        return res;
    }

    LEETCODE_NO_SANITIZE void update(int r1, int c1, int r2, int c2, T v) {
        best = hotMin(best, v);
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

    LEETCODE_NO_SANITIZE T query(int r1, int c1, int r2, int c2) const {
        T res = NO_MIN;
        int lr = r1 + R, rr = r2 + R + 1;
        // an update covering a whole row-node above either end covers that end's row
        for (int a = lr >> 1; a >= 1; a >>= 1) res = hotMin(res, colsQuery(fullTag, fullBest, a * W, c1, c2));
        for (int b = (rr - 1) >> 1; b >= 1; b >>= 1) res = hotMin(res, colsQuery(fullTag, fullBest, b * W, c1, c2));
        for (; lr < rr; lr >>= 1, rr >>= 1) {
            if (lr & 1) res = hotMin(res, colsQuery(partTag, partBest, lr++ * W, c1, c2));
            if (rr & 1) res = hotMin(res, colsQuery(partTag, partBest, --rr * W, c1, c2));
        }
        return res;
    }

    // O(log R * log C) -- every cell of rows r1..r2, columns c1..c2 becomes min(itself, v); an empty cell becomes v;
    // needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C, else throws out_of_range
    LEETCODE_NO_SANITIZE void rectChmin(int r1, int c1, int r2, int c2, T v) {
        if (r1 < 0 || r1 > r2 || r2 >= R || c1 < 0 || c1 > c2 || c2 >= C)
            throw out_of_range("rectChmin: needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C");
        update(r1, c1, r2, c2, v);
    }

    // O(log R * log C) -- the cell at (r, c) becomes min(itself, v); an empty cell becomes v; needs 0 <= r < R and 0 <=
    // c < C, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointChmin(int r, int c, T v) {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("pointChmin: needs 0 <= r < R and 0 <= c < C");
        update(r, c, r, c, v);
    }

    // O(log R * log C) -- the value at (r, c), NO_MIN, automatically the largest value of your type T, if the cell is
    // empty; needs 0 <= r < R and 0 <= c < C, else throws out_of_range
    LEETCODE_NO_SANITIZE T pointGet(int r, int c) const {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("pointGet: needs 0 <= r < R and 0 <= c < C");
        return query(r, c, r, c);
    }

    // O(log R * log C) -- min of the set cells in rows r1..r2, columns c1..c2 (NO_MIN, automatically the largest value
    // of your type T, if there are none); needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C, else throws out_of_range
    LEETCODE_NO_SANITIZE T rectMin(int r1, int c1, int r2, int c2) const {
        if (r1 < 0 || r1 > r2 || r2 >= R || c1 < 0 || c1 > c2 || c2 >= C)
            throw out_of_range("rectMin: needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C");
        return query(r1, c1, r2, c2);
    }

    // O(log R * log C) -- min of the set cells with row <= r and column <= c (NO_MIN, automatically the largest value
    // of your type T, if there are none); needs 0 <= r < R and 0 <= c < C, else throws out_of_range
    LEETCODE_NO_SANITIZE T minLteLte(int r, int c) const {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("minLteLte: needs 0 <= r < R and 0 <= c < C");
        return query(0, 0, r, c);
    }

    // O(log R * log C) -- min of the set cells with row <= r and column >= c (NO_MIN, automatically the largest value
    // of your type T, if there are none); needs 0 <= r < R and 0 <= c < C, else throws out_of_range
    LEETCODE_NO_SANITIZE T minLteGte(int r, int c) const {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("minLteGte: needs 0 <= r < R and 0 <= c < C");
        return query(0, c, r, C - 1);
    }

    // O(log R * log C) -- min of the set cells with row >= r and column <= c (NO_MIN, automatically the largest value
    // of your type T, if there are none); needs 0 <= r < R and 0 <= c < C, else throws out_of_range
    LEETCODE_NO_SANITIZE T minGteLte(int r, int c) const {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("minGteLte: needs 0 <= r < R and 0 <= c < C");
        return query(r, 0, R - 1, c);
    }

    // O(log R * log C) -- min of the set cells with row >= r and column >= c (NO_MIN, automatically the largest value
    // of your type T, if there are none); needs 0 <= r < R and 0 <= c < C, else throws out_of_range
    LEETCODE_NO_SANITIZE T minGteGte(int r, int c) const {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("minGteGte: needs 0 <= r < R and 0 <= c < C");
        return query(r, c, R - 1, C - 1);
    }

    // O(1) -- min of every set cell (NO_MIN, automatically the largest value of your type T, if there are none)
    LEETCODE_NO_SANITIZE T minAll() const {
        return best;
    }
};
