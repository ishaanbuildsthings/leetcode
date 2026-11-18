// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries-2d/compressed-seg-tree-sum-min-max-xor-and/template.cpp
#include <bits/stdc++.h>
using namespace std;
// @operations: andAll maxAll maxGteGte maxGteLte maxLteGte maxLteLte minAll minGteGte minGteLte minLteGte minLteLte pointAdd pointAssign pointChmax pointChmin pointGet rectAnd rectMax rectMin rectSum rectXor sumAll sumGteGte sumGteLte sumLteGte sumLteLte xorAll
// @data-structure-type: seg-tree
// @input: compressed
// @empty-cells: yes
// @complexities:
//   andAll: 1
//   maxAll: 1
//   maxGteGte: log(X)*log(Y)
//   maxGteLte: log(X)*log(Y)
//   maxLteGte: log(X)*log(Y)
//   maxLteLte: log(X)*log(Y)
//   minAll: 1
//   minGteGte: log(X)*log(Y)
//   minGteLte: log(X)*log(Y)
//   minLteGte: log(X)*log(Y)
//   minLteLte: log(X)*log(Y)
//   pointAdd: log(X)*log(Y)
//   pointAssign: log(X)*log(Y)
//   pointChmax: log(X)*log(Y)
//   pointChmin: log(X)*log(Y)
//   pointGet: 1
//   rectAnd: log(X)*log(Y)
//   rectMax: log(X)*log(Y)
//   rectMin: log(X)*log(Y)
//   rectSum: log(X)*log(Y)
//   rectXor: log(X)*log(Y)
//   sumAll: 1
//   sumGteGte: log(X)*log(Y)
//   sumGteLte: log(X)*log(Y)
//   sumLteGte: log(X)*log(Y)
//   sumLteLte: log(X)*log(Y)
//   xorAll: 1
//   build: X*Y
// @memory:
//   layout: 2n-iterative
//   node: sm[4*X*Y] mn[4*X*Y] mx[4*X*Y] xr[4*X*Y] an[4*X*Y]
//   tags: none
//   other: xs[1*X] ys[1*Y] xAt[1*X] yAt[1*Y]
//   note: X = how many distinct x's, Y = distinct y's; one flat array per aggregate, 2R row-nodes by 2C column-nodes; the cells are the last R row-nodes' last C entries

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

// 2D segment tree (sum, min, max, xor, AND): point updates and any-rectangle queries on an R x C grid, O(log R * log
// C) each. A tree over the rows whose every node is a tree over the columns, bottom-up, in one flat array per
// aggregate. Rows and columns are 0-based and rectangles are inclusive: rows r1..r2, columns c1..c2. A cell can be
// empty (the (R, C) constructor starts with every cell empty) and queries only see set cells: a min / max over no set
// cell is NO_MIN / NO_MAX; a sum / xor over none is 0; an AND over none is -1 (every bit set).
// T is any integer type (int, long long, ...); sums are kept in S (long long for a smaller T).
template <typename T>
struct SegTree2D {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    static constexpr T NO_MAX = numeric_limits<T>::lowest();  // the smallest value T can hold: a max over no set cell
    static constexpr T NO_MIN = numeric_limits<T>::max();  // the largest value T can hold: a min over no set cell
    int R, C, W;
    HotVector<S> sm;
    HotVector<T> mn;
    HotVector<T> mx;
    HotVector<T> xr;
    HotVector<T> an;

    // O(R*C) -- R rows by C columns, every cell empty; needs R >= 1 and C >= 1, else throws invalid_argument
    SegTree2D(int rows, int cols) : R(rows), C(cols), W(2 * cols) {
        if (R < 1 || C < 1) throw invalid_argument("SegTree2D: needs R >= 1 and C >= 1");
        sm.assign((size_t)2 * R * W, S(0));
        mn.assign((size_t)2 * R * W, NO_MIN);
        mx.assign((size_t)2 * R * W, NO_MAX);
        xr.assign((size_t)2 * R * W, T(0));
        an.assign((size_t)2 * R * W, T(-1));
    }

    // O(R*C) -- grid: R rows of C values each; needs R >= 1 and C >= 1, else throws invalid_argument
    explicit SegTree2D(const vector<vector<T>>& grid)
        : SegTree2D((int)grid.size(), grid.empty() ? 0 : (int)grid[0].size()) {
        for (int r = 0; r < R; r++) {
            if ((int)grid[r].size() != C) throw invalid_argument("SegTree2D: every row needs the same C values");
            int base = (r + R) * W;
            for (int c = 0; c < C; c++) {
                sm[base + C + c] = grid[r][c];
                mn[base + C + c] = grid[r][c];
                mx[base + C + c] = grid[r][c];
                xr[base + C + c] = grid[r][c];
                an[base + C + c] = grid[r][c];
            }
            for (int pc = C - 1; pc >= 1; pc--) {
                sm[base + pc] = sm[base + 2 * pc] + sm[base + 2 * pc + 1];
                mn[base + pc] = hotMin(mn[base + 2 * pc], mn[base + 2 * pc + 1]);
                mx[base + pc] = hotMax(mx[base + 2 * pc], mx[base + 2 * pc + 1]);
                xr[base + pc] = xr[base + 2 * pc] ^ xr[base + 2 * pc + 1];
                an[base + pc] = an[base + 2 * pc] & an[base + 2 * pc + 1];
            }
        }
        for (int pr = R - 1; pr >= 1; pr--) {
            int base = pr * W, lo = 2 * base, hi = lo + W;
            for (int pc = 1; pc < W; pc++) {
                sm[base + pc] = sm[lo + pc] + sm[hi + pc];
                mn[base + pc] = hotMin(mn[lo + pc], mn[hi + pc]);
                mx[base + pc] = hotMax(mx[lo + pc], mx[hi + pc]);
                xr[base + pc] = xr[lo + pc] ^ xr[hi + pc];
                an[base + pc] = an[lo + pc] & an[hi + pc];
            }
        }
    }

    // cell (r, c) = v, then every node above it
    LEETCODE_NO_SANITIZE void setCell(int r, int c, T v) {
        int base = (r + R) * W;
        sm[base + c + C] = v;
        mn[base + c + C] = v;
        mx[base + c + C] = v;
        xr[base + c + C] = v;
        an[base + c + C] = v;
        for (int pc = (c + C) >> 1; pc >= 1; pc >>= 1) {
            sm[base + pc] = sm[base + 2 * pc] + sm[base + 2 * pc + 1];
            mn[base + pc] = hotMin(mn[base + 2 * pc], mn[base + 2 * pc + 1]);
            mx[base + pc] = hotMax(mx[base + 2 * pc], mx[base + 2 * pc + 1]);
            xr[base + pc] = xr[base + 2 * pc] ^ xr[base + 2 * pc + 1];
            an[base + pc] = an[base + 2 * pc] & an[base + 2 * pc + 1];
        }
        for (int pr = (r + R) >> 1; pr >= 1; pr >>= 1) {
            base = pr * W;
            int lo = 2 * base, hi = lo + W;
            for (int pc = c + C; pc >= 1; pc >>= 1) {
                sm[base + pc] = sm[lo + pc] + sm[hi + pc];
                mn[base + pc] = hotMin(mn[lo + pc], mn[hi + pc]);
                mx[base + pc] = hotMax(mx[lo + pc], mx[hi + pc]);
                xr[base + pc] = xr[lo + pc] ^ xr[hi + pc];
                an[base + pc] = an[lo + pc] & an[hi + pc];
            }
        }
    }

    // O(1) -- the value at (r, c), NO_MAX, automatically the smallest value of your type T, if the cell is empty;
    // needs 0 <= r < R and 0 <= c < C, else throws out_of_range
    LEETCODE_NO_SANITIZE T pointGet(int r, int c) const {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("pointGet: needs 0 <= r < R and 0 <= c < C");
        return T(mx[(r + R) * W + c + C]);
    }

    // O(log R * log C) -- the cell at (r, c) becomes v (it may go down as well as up); needs 0 <= r < R and 0 <= c <
    // C, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAssign(int r, int c, T v) {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("pointAssign: needs 0 <= r < R and 0 <= c < C");
        setCell(r, c, v);
    }

    // O(log R * log C) -- adds v to the cell at (r, c); an empty cell becomes v; needs 0 <= r < R and 0 <= c < C,
    // else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAdd(int r, int c, T v) {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("pointAdd: needs 0 <= r < R and 0 <= c < C");
        T cur = T(mx[(r + R) * W + c + C]);
        setCell(r, c, cur == NO_MAX ? v : T(cur + v));
    }

    // O(log R * log C) -- the cell at (r, c) becomes max(itself, v); an empty cell becomes v; needs 0 <= r < R and 0
    // <= c < C, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointChmax(int r, int c, T v) {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("pointChmax: needs 0 <= r < R and 0 <= c < C");
        T cur = T(mx[(r + R) * W + c + C]);
        if (cur == NO_MAX || v > cur) setCell(r, c, v);
    }

    // O(log R * log C) -- the cell at (r, c) becomes min(itself, v); an empty cell becomes v; needs 0 <= r < R and 0
    // <= c < C, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointChmin(int r, int c, T v) {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("pointChmin: needs 0 <= r < R and 0 <= c < C");
        T cur = T(mx[(r + R) * W + c + C]);
        if (cur == NO_MAX || v < cur) setCell(r, c, v);
    }

    LEETCODE_NO_SANITIZE S sumOf(int r1, int c1, int r2, int c2) const {
        S res = S(0);
        int cl = c1 + C, cr = c2 + C + 1;
        for (int lr = r1 + R, rr = r2 + R + 1; lr < rr; lr >>= 1, rr >>= 1) {
            if (lr & 1) {
                int base = lr++ * W;
                for (int lc = cl, rc = cr; lc < rc; lc >>= 1, rc >>= 1) {
                    if (lc & 1) res += sm[base + lc++];
                    if (rc & 1) res += sm[base + --rc];
                }
            }
            if (rr & 1) {
                int base = --rr * W;
                for (int lc = cl, rc = cr; lc < rc; lc >>= 1, rc >>= 1) {
                    if (lc & 1) res += sm[base + lc++];
                    if (rc & 1) res += sm[base + --rc];
                }
            }
        }
        return res;
    }

    // O(log R * log C) -- sum of the set cells in rows r1..r2, columns c1..c2 (0 if there are none); needs 0 <= r1 <=
    // r2 < R and 0 <= c1 <= c2 < C, else throws out_of_range
    LEETCODE_NO_SANITIZE S rectSum(int r1, int c1, int r2, int c2) const {
        if (r1 < 0 || r1 > r2 || r2 >= R || c1 < 0 || c1 > c2 || c2 >= C)
            throw out_of_range("rectSum: needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C");
        return sumOf(r1, c1, r2, c2);
    }

    // O(1) -- sum of every set cell (0 if there are none)
    LEETCODE_NO_SANITIZE S sumAll() const {
        return sm[W + 1];
    }

    // O(log R * log C) -- sum of the set cells with row <= r and column <= c; needs 0 <= r < R and 0 <= c < C, else
    // throws out_of_range
    LEETCODE_NO_SANITIZE S sumLteLte(int r, int c) const {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("sumLteLte: needs 0 <= r < R and 0 <= c < C");
        return sumOf(0, 0, r, c);
    }

    // O(log R * log C) -- sum of the set cells with row <= r and column >= c; needs 0 <= r < R and 0 <= c < C, else
    // throws out_of_range
    LEETCODE_NO_SANITIZE S sumLteGte(int r, int c) const {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("sumLteGte: needs 0 <= r < R and 0 <= c < C");
        return sumOf(0, c, r, C - 1);
    }

    // O(log R * log C) -- sum of the set cells with row >= r and column <= c; needs 0 <= r < R and 0 <= c < C, else
    // throws out_of_range
    LEETCODE_NO_SANITIZE S sumGteLte(int r, int c) const {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("sumGteLte: needs 0 <= r < R and 0 <= c < C");
        return sumOf(r, 0, R - 1, c);
    }

    // O(log R * log C) -- sum of the set cells with row >= r and column >= c; needs 0 <= r < R and 0 <= c < C, else
    // throws out_of_range
    LEETCODE_NO_SANITIZE S sumGteGte(int r, int c) const {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("sumGteGte: needs 0 <= r < R and 0 <= c < C");
        return sumOf(r, c, R - 1, C - 1);
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

    // O(log R * log C) -- min of the set cells in rows r1..r2, columns c1..c2 (NO_MIN, automatically the largest
    // value of your type T, if there are none); needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C, else throws out_of_range
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

    // O(log R * log C) -- max of the set cells in rows r1..r2, columns c1..c2 (NO_MAX, automatically the smallest
    // value of your type T, if there are none); needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C, else throws out_of_range
    LEETCODE_NO_SANITIZE T rectMax(int r1, int c1, int r2, int c2) const {
        if (r1 < 0 || r1 > r2 || r2 >= R || c1 < 0 || c1 > c2 || c2 >= C)
            throw out_of_range("rectMax: needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C");
        return maxOf(r1, c1, r2, c2);
    }

    // O(1) -- max of every set cell (NO_MAX, automatically the smallest value of your type T, if there are none)
    LEETCODE_NO_SANITIZE T maxAll() const {
        return mx[W + 1];
    }

    // O(log R * log C) -- max of the set cells with row <= r and column <= c (NO_MAX, automatically the smallest
    // value of your type T, if there are none); needs 0 <= r < R and 0 <= c < C, else throws out_of_range
    LEETCODE_NO_SANITIZE T maxLteLte(int r, int c) const {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("maxLteLte: needs 0 <= r < R and 0 <= c < C");
        return maxOf(0, 0, r, c);
    }

    // O(log R * log C) -- max of the set cells with row <= r and column >= c (NO_MAX, automatically the smallest
    // value of your type T, if there are none); needs 0 <= r < R and 0 <= c < C, else throws out_of_range
    LEETCODE_NO_SANITIZE T maxLteGte(int r, int c) const {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("maxLteGte: needs 0 <= r < R and 0 <= c < C");
        return maxOf(0, c, r, C - 1);
    }

    // O(log R * log C) -- max of the set cells with row >= r and column <= c (NO_MAX, automatically the smallest
    // value of your type T, if there are none); needs 0 <= r < R and 0 <= c < C, else throws out_of_range
    LEETCODE_NO_SANITIZE T maxGteLte(int r, int c) const {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("maxGteLte: needs 0 <= r < R and 0 <= c < C");
        return maxOf(r, 0, R - 1, c);
    }

    // O(log R * log C) -- max of the set cells with row >= r and column >= c (NO_MAX, automatically the smallest
    // value of your type T, if there are none); needs 0 <= r < R and 0 <= c < C, else throws out_of_range
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
};

// Coordinate compression in front of SegTree2D: coordinates can be any integers (huge, negative, ...). You list every
// x and every y a point operation (pointGet, pointAdd, ...) will use; rectangles and corners can be any integers.
// Each listed x becomes a row and each listed y a column of a small grid, and the template above does the work on it.
// X = how many distinct x's, Y = distinct y's: memory and costs are the template's for an X by Y grid. A cell is a
// listed x with a listed y, and it is one point, not a block: a rectangle covers just the cells inside it (the gaps
// between listed coordinates don't exist), so a sum adds those cells' values, it is not an area. Cells you never set
// count as empty, a listed x with a listed y you never use together included.
template <typename T>
struct Compressed2D {
    using ll = long long;
    static constexpr T NO_MAX = SegTree2D<T>::NO_MAX;
    static constexpr T NO_MIN = SegTree2D<T>::NO_MIN;
    HotVector<ll> xs, ys;  // the listed coordinates, sorted, each once
    SegTree2D<T> ds;

    // n coordinates 0..n-1: pass upTo(n) for an axis you don't want compressed
    LEETCODE_NO_SANITIZE static vector<ll> upTo(ll n) {
        vector<ll> v(n);
        iota(v.begin(), v.end(), 0LL);
        return v;
    }

    // O(X log X + Y log Y + the template's build) -- xs: every x a point operation will use (any order, repeats are
    // fine), or upTo(n) to leave x as 0..n-1; ys: the same for y. Every cell starts empty. Needs at least one x and one
    // y, else throws invalid_argument
    Compressed2D(vector<ll> xs_, vector<ll> ys_)
        : xs(sorted(std::move(xs_))), ys(sorted(std::move(ys_))), ds(make(xs, ys)) {}

    LEETCODE_NO_SANITIZE static vector<ll> sorted(vector<ll> v) {
        sort(v.begin(), v.end());
        v.erase(unique(v.begin(), v.end()), v.end());
        return v;
    }

    LEETCODE_NO_SANITIZE static SegTree2D<T> make(const vector<ll>& xs, const vector<ll>& ys) {
        if (xs.empty() || ys.empty()) throw invalid_argument("Compressed2D: needs at least one x and one y");
        int X = (int)xs.size(), Y = (int)ys.size();
        return SegTree2D<T>(X, Y);
    }

    // the row / column of a listed x
    LEETCODE_NO_SANITIZE int xAt(ll x, const char* name) const {
        int lo = 0, hi = (int)xs.size();
        while (lo < hi) {
            int mid = (lo + hi) >> 1;
            if (xs[mid] < x) lo = mid + 1;
            else hi = mid;
        }
        if (lo == (int)xs.size() || xs[lo] != x)
            throw out_of_range(string(name) + ": x is not one of the xs given to the constructor");
        return lo;
    }

    // the row / column of a listed y
    LEETCODE_NO_SANITIZE int yAt(ll y, const char* name) const {
        int lo = 0, hi = (int)ys.size();
        while (lo < hi) {
            int mid = (lo + hi) >> 1;
            if (ys[mid] < y) lo = mid + 1;
            else hi = mid;
        }
        if (lo == (int)ys.size() || ys[lo] != y)
            throw out_of_range(string(name) + ": y is not one of the ys given to the constructor");
        return lo;
    }

    // the rows and columns a rectangle covers, {r1, c1, r2, c2}; r1 = -1 when no listed x or no listed y is inside
    LEETCODE_NO_SANITIZE array<int, 4> rect(ll x1, ll y1, ll x2, ll y2, const char* name) const {
        if (x1 > x2 || y1 > y2) throw out_of_range(string(name) + ": needs x1 <= x2 and y1 <= y2");
        int r1 = int(lower_bound(xs.begin(), xs.end(), x1) - xs.begin());
        int r2 = int(upper_bound(xs.begin(), xs.end(), x2) - xs.begin()) - 1;
        int c1 = int(lower_bound(ys.begin(), ys.end(), y1) - ys.begin());
        int c2 = int(upper_bound(ys.begin(), ys.end(), y2) - ys.begin()) - 1;
        if (r1 > r2 || c1 > c2) return {-1, -1, -1, -1};
        return {r1, c1, r2, c2};
    }

    // the cell a corner query starts from: the last listed x <= x (xLte) or the first listed x >= x, the same for y;
    // {-1, -1} when there is none
    LEETCODE_NO_SANITIZE array<int, 2> corner(ll x, ll y, bool xLte, bool yLte) const {
        int r = xLte ? int(upper_bound(xs.begin(), xs.end(), x) - xs.begin()) - 1
                     : int(lower_bound(xs.begin(), xs.end(), x) - xs.begin());
        int c = yLte ? int(upper_bound(ys.begin(), ys.end(), y) - ys.begin()) - 1
                     : int(lower_bound(ys.begin(), ys.end(), y) - ys.begin());
        if (r < 0 || r >= (int)xs.size() || c < 0 || c >= (int)ys.size()) return {-1, -1};
        return {r, c};
    }

    // O(1) -- AND of every cell
    LEETCODE_NO_SANITIZE auto andAll() {
        return ds.andAll();
    }

    // O(1) -- max of every set cell (NO_MAX, automatically the smallest value of your type T, if there are none)
    LEETCODE_NO_SANITIZE auto maxAll() {
        return ds.maxAll();
    }

    // O(log X * log Y) -- max of the cells with x >= the given x and y >= the given y (NO_MAX, automatically the
    // smallest value of your type T, if there are none); any integers; NO_MAX, automatically the smallest value of your
    // type T, if no cell is there
    LEETCODE_NO_SANITIZE auto maxGteGte(ll x, ll y) {
        auto [r1, c1] = corner(x, y, false, false);
        if (r1 < 0) return NO_MAX;
        return ds.maxGteGte(r1, c1);
    }

    // O(log X * log Y) -- max of the cells with x >= the given x and y <= the given y (NO_MAX, automatically the
    // smallest value of your type T, if there are none); any integers; NO_MAX, automatically the smallest value of your
    // type T, if no cell is there
    LEETCODE_NO_SANITIZE auto maxGteLte(ll x, ll y) {
        auto [r1, c1] = corner(x, y, false, true);
        if (r1 < 0) return NO_MAX;
        return ds.maxGteLte(r1, c1);
    }

    // O(log X * log Y) -- max of the cells with x <= the given x and y >= the given y (NO_MAX, automatically the
    // smallest value of your type T, if there are none); any integers; NO_MAX, automatically the smallest value of your
    // type T, if no cell is there
    LEETCODE_NO_SANITIZE auto maxLteGte(ll x, ll y) {
        auto [r1, c1] = corner(x, y, true, false);
        if (r1 < 0) return NO_MAX;
        return ds.maxLteGte(r1, c1);
    }

    // O(log X * log Y) -- max of the cells with x <= the given x and y <= the given y (NO_MAX, automatically the
    // smallest value of your type T, if there are none); any integers; NO_MAX, automatically the smallest value of your
    // type T, if no cell is there
    LEETCODE_NO_SANITIZE auto maxLteLte(ll x, ll y) {
        auto [r1, c1] = corner(x, y, true, true);
        if (r1 < 0) return NO_MAX;
        return ds.maxLteLte(r1, c1);
    }

    // O(1) -- min of every set cell (NO_MAX, automatically the smallest value of your type T, if there are none)
    LEETCODE_NO_SANITIZE auto minAll() {
        return ds.minAll();
    }

    // O(log X * log Y) -- min of the cells with x >= the given x and y >= the given y (NO_MIN, automatically the
    // largest value of your type T, if there are none); any integers; NO_MIN, automatically the largest value of your
    // type T, if no cell is there
    LEETCODE_NO_SANITIZE auto minGteGte(ll x, ll y) {
        auto [r1, c1] = corner(x, y, false, false);
        if (r1 < 0) return NO_MIN;
        return ds.minGteGte(r1, c1);
    }

    // O(log X * log Y) -- min of the cells with x >= the given x and y <= the given y (NO_MIN, automatically the
    // largest value of your type T, if there are none); any integers; NO_MIN, automatically the largest value of your
    // type T, if no cell is there
    LEETCODE_NO_SANITIZE auto minGteLte(ll x, ll y) {
        auto [r1, c1] = corner(x, y, false, true);
        if (r1 < 0) return NO_MIN;
        return ds.minGteLte(r1, c1);
    }

    // O(log X * log Y) -- min of the cells with x <= the given x and y >= the given y (NO_MIN, automatically the
    // largest value of your type T, if there are none); any integers; NO_MIN, automatically the largest value of your
    // type T, if no cell is there
    LEETCODE_NO_SANITIZE auto minLteGte(ll x, ll y) {
        auto [r1, c1] = corner(x, y, true, false);
        if (r1 < 0) return NO_MIN;
        return ds.minLteGte(r1, c1);
    }

    // O(log X * log Y) -- min of the cells with x <= the given x and y <= the given y (NO_MIN, automatically the
    // largest value of your type T, if there are none); any integers; NO_MIN, automatically the largest value of your
    // type T, if no cell is there
    LEETCODE_NO_SANITIZE auto minLteLte(ll x, ll y) {
        auto [r1, c1] = corner(x, y, true, true);
        if (r1 < 0) return NO_MIN;
        return ds.minLteLte(r1, c1);
    }

    // O(log X * log Y) -- adds v to the cell (x, y); an empty cell becomes v; x must be one of the xs and y one of the
    // ys, else throws out_of_range
    LEETCODE_NO_SANITIZE auto pointAdd(ll x, ll y, T v) {
        return ds.pointAdd(xAt(x, "pointAdd"), yAt(y, "pointAdd"), v);
    }

    // O(log X * log Y) -- the cell (x, y) becomes v; an empty cell becomes v; x must be one of the xs and y one of the
    // ys, else throws out_of_range
    LEETCODE_NO_SANITIZE auto pointAssign(ll x, ll y, T v) {
        return ds.pointAssign(xAt(x, "pointAssign"), yAt(y, "pointAssign"), v);
    }

    // O(log X * log Y) -- the cell (x, y) becomes max(itself, v); an empty cell becomes v; x must be one of the xs
    // and y one of the ys, else throws out_of_range
    LEETCODE_NO_SANITIZE auto pointChmax(ll x, ll y, T v) {
        return ds.pointChmax(xAt(x, "pointChmax"), yAt(y, "pointChmax"), v);
    }

    // O(log X * log Y) -- the cell (x, y) becomes min(itself, v); an empty cell becomes v; x must be one of the xs
    // and y one of the ys, else throws out_of_range
    LEETCODE_NO_SANITIZE auto pointChmin(ll x, ll y, T v) {
        return ds.pointChmin(xAt(x, "pointChmin"), yAt(y, "pointChmin"), v);
    }

    // O(1) -- the value at (x, y), NO_MAX, automatically the smallest value of your type T, if the cell is empty; x
    // must be one of the xs and y one of the ys, else throws out_of_range
    LEETCODE_NO_SANITIZE auto pointGet(ll x, ll y) {
        return ds.pointGet(xAt(x, "pointGet"), yAt(y, "pointGet"));
    }

    // O(log X * log Y) -- AND of the cells with x1 <= x <= x2 and y1 <= y <= y2; any integers, needs x1 <= x2 and y1 <=
    // y2, else throws out_of_range; -1 (every bit set) if no cell is inside
    LEETCODE_NO_SANITIZE auto rectAnd(ll x1, ll y1, ll x2, ll y2) {
        auto [r1, c1, r2, c2] = rect(x1, y1, x2, y2, "rectAnd");
        if (r1 < 0) return decltype(ds.rectAnd(0, 0, 0, 0))(-1);
        return ds.rectAnd(r1, c1, r2, c2);
    }

    // O(log X * log Y) -- max of the cells with x1 <= x <= x2 and y1 <= y <= y2 (NO_MAX, automatically the smallest
    // value of your type T, if there are none); any integers, needs x1 <= x2 and y1 <= y2, else throws out_of_range;
    // NO_MAX, automatically the smallest value of your type T, if no cell is inside
    LEETCODE_NO_SANITIZE auto rectMax(ll x1, ll y1, ll x2, ll y2) {
        auto [r1, c1, r2, c2] = rect(x1, y1, x2, y2, "rectMax");
        if (r1 < 0) return NO_MAX;
        return ds.rectMax(r1, c1, r2, c2);
    }

    // O(log X * log Y) -- min of the cells with x1 <= x <= x2 and y1 <= y <= y2 (NO_MIN, automatically the largest
    // value of your type T, if there are none); any integers, needs x1 <= x2 and y1 <= y2, else throws out_of_range;
    // NO_MIN, automatically the largest value of your type T, if no cell is inside
    LEETCODE_NO_SANITIZE auto rectMin(ll x1, ll y1, ll x2, ll y2) {
        auto [r1, c1, r2, c2] = rect(x1, y1, x2, y2, "rectMin");
        if (r1 < 0) return NO_MIN;
        return ds.rectMin(r1, c1, r2, c2);
    }

    // O(log X * log Y) -- sum of the cells with x1 <= x <= x2 and y1 <= y <= y2; any integers, needs x1 <= x2 and y1 <=
    // y2, else throws out_of_range; 0 if no cell is inside
    LEETCODE_NO_SANITIZE auto rectSum(ll x1, ll y1, ll x2, ll y2) {
        auto [r1, c1, r2, c2] = rect(x1, y1, x2, y2, "rectSum");
        if (r1 < 0) return decltype(ds.rectSum(0, 0, 0, 0))(0);
        return ds.rectSum(r1, c1, r2, c2);
    }

    // O(log X * log Y) -- XOR of the cells with x1 <= x <= x2 and y1 <= y <= y2; any integers, needs x1 <= x2 and y1 <=
    // y2, else throws out_of_range; 0 if no cell is inside
    LEETCODE_NO_SANITIZE auto rectXor(ll x1, ll y1, ll x2, ll y2) {
        auto [r1, c1, r2, c2] = rect(x1, y1, x2, y2, "rectXor");
        if (r1 < 0) return decltype(ds.rectXor(0, 0, 0, 0))(0);
        return ds.rectXor(r1, c1, r2, c2);
    }

    // O(1) -- sum of every cell
    LEETCODE_NO_SANITIZE auto sumAll() {
        return ds.sumAll();
    }

    // O(log X * log Y) -- sum of the cells with x >= the given x and y >= the given y; any integers; 0 if no cell is
    // there
    LEETCODE_NO_SANITIZE auto sumGteGte(ll x, ll y) {
        auto [r1, c1] = corner(x, y, false, false);
        if (r1 < 0) return decltype(ds.sumGteGte(0, 0))(0);
        return ds.sumGteGte(r1, c1);
    }

    // O(log X * log Y) -- sum of the cells with x >= the given x and y <= the given y; any integers; 0 if no cell is
    // there
    LEETCODE_NO_SANITIZE auto sumGteLte(ll x, ll y) {
        auto [r1, c1] = corner(x, y, false, true);
        if (r1 < 0) return decltype(ds.sumGteLte(0, 0))(0);
        return ds.sumGteLte(r1, c1);
    }

    // O(log X * log Y) -- sum of the cells with x <= the given x and y >= the given y; any integers; 0 if no cell is
    // there
    LEETCODE_NO_SANITIZE auto sumLteGte(ll x, ll y) {
        auto [r1, c1] = corner(x, y, true, false);
        if (r1 < 0) return decltype(ds.sumLteGte(0, 0))(0);
        return ds.sumLteGte(r1, c1);
    }

    // O(log X * log Y) -- sum of the cells with x <= the given x and y <= the given y; any integers; 0 if no cell is
    // there
    LEETCODE_NO_SANITIZE auto sumLteLte(ll x, ll y) {
        auto [r1, c1] = corner(x, y, true, true);
        if (r1 < 0) return decltype(ds.sumLteLte(0, 0))(0);
        return ds.sumLteLte(r1, c1);
    }

    // O(1) -- XOR of every cell
    LEETCODE_NO_SANITIZE auto xorAll() {
        return ds.xorAll();
    }
};
