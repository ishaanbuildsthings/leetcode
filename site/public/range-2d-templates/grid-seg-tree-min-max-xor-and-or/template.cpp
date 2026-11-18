// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries-2d/grid-seg-tree-min-max-xor-and-or/template.cpp
#include <bits/stdc++.h>
using namespace std;
// @operations: andAll maxAll maxGteGte maxGteLte maxLteGte maxLteLte minAll minGteGte minGteLte minLteGte minLteLte orAll pointAdd pointAssign pointChmax pointChmin pointGet rectAnd rectMax rectMin rectOr rectXor xorAll
// @data-structure-type: seg-tree
// @input: grid
// @empty-cells: yes
// @complexities:
//   andAll: 1
//   maxAll: 1
//   maxGteGte: log(R)*log(C)
//   maxGteLte: log(R)*log(C)
//   maxLteGte: log(R)*log(C)
//   maxLteLte: log(R)*log(C)
//   minAll: 1
//   minGteGte: log(R)*log(C)
//   minGteLte: log(R)*log(C)
//   minLteGte: log(R)*log(C)
//   minLteLte: log(R)*log(C)
//   orAll: 1
//   pointAdd: log(R)*log(C)
//   pointAssign: log(R)*log(C)
//   pointChmax: log(R)*log(C)
//   pointChmin: log(R)*log(C)
//   pointGet: 1
//   rectAnd: log(R)*log(C)
//   rectMax: log(R)*log(C)
//   rectMin: log(R)*log(C)
//   rectOr: log(R)*log(C)
//   rectXor: log(R)*log(C)
//   xorAll: 1
//   build: R*C
// @memory:
//   layout: 2n-iterative
//   node: mn[4*R*C] mx[4*R*C] xr[4*R*C] an[4*R*C] orr[4*R*C]
//   tags: none
//   other: none
//   note: one flat array per aggregate, 2R row-nodes by 2C column-nodes; the cells are the last R row-nodes' last C entries

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
template <typename A>
LEETCODE_NO_SANITIZE_INLINE A hotMax(A a, A b) { return a < b ? b : a; }

// 2D segment tree (min, max, xor, AND, OR): point updates and any-rectangle queries on an R x C grid, O(log R * log
// C) each. A tree over the rows whose every node is a tree over the columns, bottom-up, in one flat array per
// aggregate. Rows and columns are 0-based and rectangles are inclusive: rows r1..r2, columns c1..c2. A cell can be
// empty (the (R, C) constructor starts with every cell empty) and queries only see set cells: a min / max over no set
// cell is NO_MIN / NO_MAX; a xor / OR over none is 0; an AND over none is -1 (every bit set).
// T is any integer type (int, long long, ...).
template <typename T>
struct SegTree2D {
    static constexpr T NO_MAX = numeric_limits<T>::lowest();  // the smallest value T can hold: a max over no set cell
    static constexpr T NO_MIN = numeric_limits<T>::max();  // the largest value T can hold: a min over no set cell
    int R, C, W;
    HotVector<T> mn;
    HotVector<T> mx;
    HotVector<T> xr;
    HotVector<T> an;
    HotVector<T> orr;

    // O(R*C) -- R rows by C columns, every cell empty; needs R >= 1 and C >= 1, else throws invalid_argument
    SegTree2D(int rows, int cols) : R(rows), C(cols), W(2 * cols) {
        if (R < 1 || C < 1) throw invalid_argument("SegTree2D: needs R >= 1 and C >= 1");
        mn.assign((size_t)2 * R * W, NO_MIN);
        mx.assign((size_t)2 * R * W, NO_MAX);
        xr.assign((size_t)2 * R * W, T(0));
        an.assign((size_t)2 * R * W, T(-1));
        orr.assign((size_t)2 * R * W, T(0));
    }

    // O(R*C) -- grid: R rows of C values each; needs R >= 1 and C >= 1, else throws invalid_argument
    explicit SegTree2D(const vector<vector<T>>& grid)
        : SegTree2D((int)grid.size(), grid.empty() ? 0 : (int)grid[0].size()) {
        for (int r = 0; r < R; r++) {
            if ((int)grid[r].size() != C) throw invalid_argument("SegTree2D: every row needs the same C values");
            int base = (r + R) * W;
            for (int c = 0; c < C; c++) {
                mn[base + C + c] = grid[r][c];
                mx[base + C + c] = grid[r][c];
                xr[base + C + c] = grid[r][c];
                an[base + C + c] = grid[r][c];
                orr[base + C + c] = grid[r][c];
            }
            for (int pc = C - 1; pc >= 1; pc--) {
                mn[base + pc] = hotMin(mn[base + 2 * pc], mn[base + 2 * pc + 1]);
                mx[base + pc] = hotMax(mx[base + 2 * pc], mx[base + 2 * pc + 1]);
                xr[base + pc] = xr[base + 2 * pc] ^ xr[base + 2 * pc + 1];
                an[base + pc] = an[base + 2 * pc] & an[base + 2 * pc + 1];
                orr[base + pc] = orr[base + 2 * pc] | orr[base + 2 * pc + 1];
            }
        }
        for (int pr = R - 1; pr >= 1; pr--) {
            int base = pr * W, lo = 2 * base, hi = lo + W;
            for (int pc = 1; pc < W; pc++) {
                mn[base + pc] = hotMin(mn[lo + pc], mn[hi + pc]);
                mx[base + pc] = hotMax(mx[lo + pc], mx[hi + pc]);
                xr[base + pc] = xr[lo + pc] ^ xr[hi + pc];
                an[base + pc] = an[lo + pc] & an[hi + pc];
                orr[base + pc] = orr[lo + pc] | orr[hi + pc];
            }
        }
    }

    // cell (r, c) = v, then every node above it
    LEETCODE_NO_SANITIZE void setCell(int r, int c, T v) {
        int base = (r + R) * W;
        mn[base + c + C] = v;
        mx[base + c + C] = v;
        xr[base + c + C] = v;
        an[base + c + C] = v;
        orr[base + c + C] = v;
        for (int pc = (c + C) >> 1; pc >= 1; pc >>= 1) {
            mn[base + pc] = hotMin(mn[base + 2 * pc], mn[base + 2 * pc + 1]);
            mx[base + pc] = hotMax(mx[base + 2 * pc], mx[base + 2 * pc + 1]);
            xr[base + pc] = xr[base + 2 * pc] ^ xr[base + 2 * pc + 1];
            an[base + pc] = an[base + 2 * pc] & an[base + 2 * pc + 1];
            orr[base + pc] = orr[base + 2 * pc] | orr[base + 2 * pc + 1];
        }
        for (int pr = (r + R) >> 1; pr >= 1; pr >>= 1) {
            base = pr * W;
            int lo = 2 * base, hi = lo + W;
            for (int pc = c + C; pc >= 1; pc >>= 1) {
                mn[base + pc] = hotMin(mn[lo + pc], mn[hi + pc]);
                mx[base + pc] = hotMax(mx[lo + pc], mx[hi + pc]);
                xr[base + pc] = xr[lo + pc] ^ xr[hi + pc];
                an[base + pc] = an[lo + pc] & an[hi + pc];
                orr[base + pc] = orr[lo + pc] | orr[hi + pc];
            }
        }
    }

    // O(1) -- the value at (r, c), NO_MAX, automatically the smallest value of your type T, if the cell is empty; needs
    // 0 <= r < R and 0 <= c < C, else throws out_of_range
    LEETCODE_NO_SANITIZE T pointGet(int r, int c) const {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("pointGet: needs 0 <= r < R and 0 <= c < C");
        return T(mx[(r + R) * W + c + C]);
    }

    // O(log R * log C) -- the cell at (r, c) becomes v (it may go down as well as up); needs 0 <= r < R and 0 <= c < C,
    // else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAssign(int r, int c, T v) {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("pointAssign: needs 0 <= r < R and 0 <= c < C");
        setCell(r, c, v);
    }

    // O(log R * log C) -- adds v to the cell at (r, c); an empty cell becomes v; needs 0 <= r < R and 0 <= c < C, else
    // throws out_of_range
    LEETCODE_NO_SANITIZE void pointAdd(int r, int c, T v) {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("pointAdd: needs 0 <= r < R and 0 <= c < C");
        T cur = T(mx[(r + R) * W + c + C]);
        setCell(r, c, cur == NO_MAX ? v : T(cur + v));
    }

    // O(log R * log C) -- the cell at (r, c) becomes max(itself, v); an empty cell becomes v; needs 0 <= r < R and 0 <=
    // c < C, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointChmax(int r, int c, T v) {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("pointChmax: needs 0 <= r < R and 0 <= c < C");
        T cur = T(mx[(r + R) * W + c + C]);
        if (cur == NO_MAX || v > cur) setCell(r, c, v);
    }

    // O(log R * log C) -- the cell at (r, c) becomes min(itself, v); an empty cell becomes v; needs 0 <= r < R and 0 <=
    // c < C, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointChmin(int r, int c, T v) {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("pointChmin: needs 0 <= r < R and 0 <= c < C");
        T cur = T(mx[(r + R) * W + c + C]);
        if (cur == NO_MAX || v < cur) setCell(r, c, v);
    }

    LEETCODE_NO_SANITIZE T minOf(int r1, int c1, int r2, int c2) const {
        T res = NO_MIN;
        int cl = c1 + C, cr = c2 + C + 1;
        for (int lr = r1 + R, rr = r2 + R + 1; lr < rr; lr >>= 1, rr >>= 1) {
            if (lr & 1) {
                int base = lr++ * W;
                for (int lc = cl, rc = cr; lc < rc; lc >>= 1, rc >>= 1) {
                    if (lc & 1) res = hotMin(res, mn[base + lc++]);
                    if (rc & 1) res = hotMin(res, mn[base + --rc]);
                }
            }
            if (rr & 1) {
                int base = --rr * W;
                for (int lc = cl, rc = cr; lc < rc; lc >>= 1, rc >>= 1) {
                    if (lc & 1) res = hotMin(res, mn[base + lc++]);
                    if (rc & 1) res = hotMin(res, mn[base + --rc]);
                }
            }
        }
        return res;
    }

    // O(log R * log C) -- min of the set cells in rows r1..r2, columns c1..c2 (NO_MIN, automatically the largest value
    // of your type T, if there are none); needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C, else throws out_of_range
    LEETCODE_NO_SANITIZE T rectMin(int r1, int c1, int r2, int c2) const {
        if (r1 < 0 || r1 > r2 || r2 >= R || c1 < 0 || c1 > c2 || c2 >= C)
            throw out_of_range("rectMin: needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C");
        return minOf(r1, c1, r2, c2);
    }

    // O(1) -- min of every set cell (NO_MIN, automatically the largest value of your type T, if there are none)
    LEETCODE_NO_SANITIZE T minAll() const {
        return mn[W + 1];
    }

    // O(log R * log C) -- min of the set cells with row <= r and column <= c (NO_MIN, automatically the largest value
    // of your type T, if there are none); needs 0 <= r < R and 0 <= c < C, else throws out_of_range
    LEETCODE_NO_SANITIZE T minLteLte(int r, int c) const {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("minLteLte: needs 0 <= r < R and 0 <= c < C");
        return minOf(0, 0, r, c);
    }

    // O(log R * log C) -- min of the set cells with row <= r and column >= c (NO_MIN, automatically the largest value
    // of your type T, if there are none); needs 0 <= r < R and 0 <= c < C, else throws out_of_range
    LEETCODE_NO_SANITIZE T minLteGte(int r, int c) const {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("minLteGte: needs 0 <= r < R and 0 <= c < C");
        return minOf(0, c, r, C - 1);
    }

    // O(log R * log C) -- min of the set cells with row >= r and column <= c (NO_MIN, automatically the largest value
    // of your type T, if there are none); needs 0 <= r < R and 0 <= c < C, else throws out_of_range
    LEETCODE_NO_SANITIZE T minGteLte(int r, int c) const {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("minGteLte: needs 0 <= r < R and 0 <= c < C");
        return minOf(r, 0, R - 1, c);
    }

    // O(log R * log C) -- min of the set cells with row >= r and column >= c (NO_MIN, automatically the largest value
    // of your type T, if there are none); needs 0 <= r < R and 0 <= c < C, else throws out_of_range
    LEETCODE_NO_SANITIZE T minGteGte(int r, int c) const {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("minGteGte: needs 0 <= r < R and 0 <= c < C");
        return minOf(r, c, R - 1, C - 1);
    }

    LEETCODE_NO_SANITIZE T maxOf(int r1, int c1, int r2, int c2) const {
        T res = NO_MAX;
        int cl = c1 + C, cr = c2 + C + 1;
        for (int lr = r1 + R, rr = r2 + R + 1; lr < rr; lr >>= 1, rr >>= 1) {
            if (lr & 1) {
                int base = lr++ * W;
                for (int lc = cl, rc = cr; lc < rc; lc >>= 1, rc >>= 1) {
                    if (lc & 1) res = hotMax(res, mx[base + lc++]);
                    if (rc & 1) res = hotMax(res, mx[base + --rc]);
                }
            }
            if (rr & 1) {
                int base = --rr * W;
                for (int lc = cl, rc = cr; lc < rc; lc >>= 1, rc >>= 1) {
                    if (lc & 1) res = hotMax(res, mx[base + lc++]);
                    if (rc & 1) res = hotMax(res, mx[base + --rc]);
                }
            }
        }
        return res;
    }

    // O(log R * log C) -- max of the set cells in rows r1..r2, columns c1..c2 (NO_MAX, automatically the smallest value
    // of your type T, if there are none); needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C, else throws out_of_range
    LEETCODE_NO_SANITIZE T rectMax(int r1, int c1, int r2, int c2) const {
        if (r1 < 0 || r1 > r2 || r2 >= R || c1 < 0 || c1 > c2 || c2 >= C)
            throw out_of_range("rectMax: needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C");
        return maxOf(r1, c1, r2, c2);
    }

    // O(1) -- max of every set cell (NO_MAX, automatically the smallest value of your type T, if there are none)
    LEETCODE_NO_SANITIZE T maxAll() const {
        return mx[W + 1];
    }

    // O(log R * log C) -- max of the set cells with row <= r and column <= c (NO_MAX, automatically the smallest value
    // of your type T, if there are none); needs 0 <= r < R and 0 <= c < C, else throws out_of_range
    LEETCODE_NO_SANITIZE T maxLteLte(int r, int c) const {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("maxLteLte: needs 0 <= r < R and 0 <= c < C");
        return maxOf(0, 0, r, c);
    }

    // O(log R * log C) -- max of the set cells with row <= r and column >= c (NO_MAX, automatically the smallest value
    // of your type T, if there are none); needs 0 <= r < R and 0 <= c < C, else throws out_of_range
    LEETCODE_NO_SANITIZE T maxLteGte(int r, int c) const {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("maxLteGte: needs 0 <= r < R and 0 <= c < C");
        return maxOf(0, c, r, C - 1);
    }

    // O(log R * log C) -- max of the set cells with row >= r and column <= c (NO_MAX, automatically the smallest value
    // of your type T, if there are none); needs 0 <= r < R and 0 <= c < C, else throws out_of_range
    LEETCODE_NO_SANITIZE T maxGteLte(int r, int c) const {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("maxGteLte: needs 0 <= r < R and 0 <= c < C");
        return maxOf(r, 0, R - 1, c);
    }

    // O(log R * log C) -- max of the set cells with row >= r and column >= c (NO_MAX, automatically the smallest value
    // of your type T, if there are none); needs 0 <= r < R and 0 <= c < C, else throws out_of_range
    LEETCODE_NO_SANITIZE T maxGteGte(int r, int c) const {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("maxGteGte: needs 0 <= r < R and 0 <= c < C");
        return maxOf(r, c, R - 1, C - 1);
    }

    LEETCODE_NO_SANITIZE T xorOf(int r1, int c1, int r2, int c2) const {
        T res = T(0);
        int cl = c1 + C, cr = c2 + C + 1;
        for (int lr = r1 + R, rr = r2 + R + 1; lr < rr; lr >>= 1, rr >>= 1) {
            if (lr & 1) {
                int base = lr++ * W;
                for (int lc = cl, rc = cr; lc < rc; lc >>= 1, rc >>= 1) {
                    if (lc & 1) res ^= xr[base + lc++];
                    if (rc & 1) res ^= xr[base + --rc];
                }
            }
            if (rr & 1) {
                int base = --rr * W;
                for (int lc = cl, rc = cr; lc < rc; lc >>= 1, rc >>= 1) {
                    if (lc & 1) res ^= xr[base + lc++];
                    if (rc & 1) res ^= xr[base + --rc];
                }
            }
        }
        return res;
    }

    // O(log R * log C) -- xor of the set cells in rows r1..r2, columns c1..c2 (0 if there are none); needs 0 <= r1 <=
    // r2 < R and 0 <= c1 <= c2 < C, else throws out_of_range
    LEETCODE_NO_SANITIZE T rectXor(int r1, int c1, int r2, int c2) const {
        if (r1 < 0 || r1 > r2 || r2 >= R || c1 < 0 || c1 > c2 || c2 >= C)
            throw out_of_range("rectXor: needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C");
        return xorOf(r1, c1, r2, c2);
    }

    // O(1) -- xor of every set cell (0 if there are none)
    LEETCODE_NO_SANITIZE T xorAll() const {
        return xr[W + 1];
    }

    LEETCODE_NO_SANITIZE T andOf(int r1, int c1, int r2, int c2) const {
        T res = T(-1);
        int cl = c1 + C, cr = c2 + C + 1;
        for (int lr = r1 + R, rr = r2 + R + 1; lr < rr; lr >>= 1, rr >>= 1) {
            if (lr & 1) {
                int base = lr++ * W;
                for (int lc = cl, rc = cr; lc < rc; lc >>= 1, rc >>= 1) {
                    if (lc & 1) res &= an[base + lc++];
                    if (rc & 1) res &= an[base + --rc];
                }
            }
            if (rr & 1) {
                int base = --rr * W;
                for (int lc = cl, rc = cr; lc < rc; lc >>= 1, rc >>= 1) {
                    if (lc & 1) res &= an[base + lc++];
                    if (rc & 1) res &= an[base + --rc];
                }
            }
        }
        return res;
    }

    // O(log R * log C) -- AND of the set cells in rows r1..r2, columns c1..c2 (-1 (every bit set) if there are none);
    // needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C, else throws out_of_range
    LEETCODE_NO_SANITIZE T rectAnd(int r1, int c1, int r2, int c2) const {
        if (r1 < 0 || r1 > r2 || r2 >= R || c1 < 0 || c1 > c2 || c2 >= C)
            throw out_of_range("rectAnd: needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C");
        return andOf(r1, c1, r2, c2);
    }

    // O(1) -- AND of every set cell (-1 (every bit set) if there are none)
    LEETCODE_NO_SANITIZE T andAll() const {
        return an[W + 1];
    }

    LEETCODE_NO_SANITIZE T orOf(int r1, int c1, int r2, int c2) const {
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

    // O(log R * log C) -- OR of the set cells in rows r1..r2, columns c1..c2 (0 if there are none); needs 0 <= r1 <= r2
    // < R and 0 <= c1 <= c2 < C, else throws out_of_range
    LEETCODE_NO_SANITIZE T rectOr(int r1, int c1, int r2, int c2) const {
        if (r1 < 0 || r1 > r2 || r2 >= R || c1 < 0 || c1 > c2 || c2 >= C)
            throw out_of_range("rectOr: needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C");
        return orOf(r1, c1, r2, c2);
    }

    // O(1) -- OR of every set cell (0 if there are none)
    LEETCODE_NO_SANITIZE T orAll() const {
        return orr[W + 1];
    }
};
