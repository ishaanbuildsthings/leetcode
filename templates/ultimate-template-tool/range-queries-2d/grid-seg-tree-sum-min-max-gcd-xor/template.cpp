// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries-2d/grid-seg-tree-sum-min-max-gcd-xor/template.cpp
#include <bits/stdc++.h>
using namespace std;
// @operations: gcdAll maxAll maxGteGte maxGteLte maxLteGte maxLteLte minAll minGteGte minGteLte minLteGte minLteLte pointAdd pointAssign pointChmax pointChmin pointGet rectGcd rectMax rectMin rectSum rectXor sumAll xorAll
// @data-structure-type: seg-tree
// @input: grid
// @empty-cells: yes
// @complexities:
//   gcdAll: 1
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
//   pointAdd: log(R)*log(C)*log(U) ?
//   pointAssign: log(R)*log(C)*log(U) ?
//   pointChmax: log(R)*log(C)*log(U) ?
//   pointChmin: log(R)*log(C)*log(U) ?
//   pointGet: 1
//   rectGcd: log(R)*log(C)+log(U) ?
//   rectMax: log(R)*log(C)
//   rectMin: log(R)*log(C)
//   rectSum: log(R)*log(C)
//   rectXor: log(R)*log(C)
//   sumAll: 1
//   xorAll: 1
//   build: R*C*log(U) ?
// @memory:
//   layout: 2n-iterative
//   node: sm[4*R*C] mn[4*R*C] mx[4*R*C] gc[4*R*C] xr[4*R*C]
//   tags: none
//   other: none
//   note: one flat array per aggregate, 2R row-nodes by 2C column-nodes; the cells are the last R row-nodes' last C entries

// 2D segment tree (sum, min, max, gcd, xor): point updates and any-rectangle queries on an R x C grid, O(log R * log
// C) each. A tree over the rows whose every node is a tree over the columns, bottom-up, in one flat array per
// aggregate. Rows and columns are 0-based and rectangles are inclusive: rows r1..r2, columns c1..c2. A cell can be
// empty (the (R, C) constructor starts with every cell empty) and queries only see set cells: a min / max over no set
// cell is NO_MIN / NO_MAX; a sum / gcd / xor over none is 0.
// T is any integer type (int, long long, ...); sums are kept in S (long long for a smaller T).
template <typename T>
struct SegTree2D {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    static constexpr T NO_MAX = numeric_limits<T>::min();  // what a max over no set cell gives
    static constexpr T NO_MIN = numeric_limits<T>::max();  // what a min over no set cell gives
    int R, C, W;
    vector<S> sm;
    vector<T> mn;
    vector<T> mx;
    vector<T> gc;
    vector<T> xr;

    static T gcdOf(T a, T b) { return std::gcd(a, b); }

    // O(R*C) -- R rows by C columns, every cell empty; needs R >= 1 and C >= 1, else throws invalid_argument
    SegTree2D(int rows, int cols) : R(rows), C(cols), W(2 * cols) {
        if (R < 1 || C < 1) throw invalid_argument("SegTree2D: needs R >= 1 and C >= 1");
        sm.assign((size_t)2 * R * W, S(0));
        mn.assign((size_t)2 * R * W, NO_MIN);
        mx.assign((size_t)2 * R * W, NO_MAX);
        gc.assign((size_t)2 * R * W, T(0));
        xr.assign((size_t)2 * R * W, T(0));
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
                gc[base + C + c] = grid[r][c];
                xr[base + C + c] = grid[r][c];
            }
            for (int pc = C - 1; pc >= 1; pc--) {
                sm[base + pc] = sm[base + 2 * pc] + sm[base + 2 * pc + 1];
                mn[base + pc] = min(mn[base + 2 * pc], mn[base + 2 * pc + 1]);
                mx[base + pc] = max(mx[base + 2 * pc], mx[base + 2 * pc + 1]);
                gc[base + pc] = gcdOf(gc[base + 2 * pc], gc[base + 2 * pc + 1]);
                xr[base + pc] = xr[base + 2 * pc] ^ xr[base + 2 * pc + 1];
            }
        }
        for (int pr = R - 1; pr >= 1; pr--) {
            int base = pr * W, lo = 2 * base, hi = lo + W;
            for (int pc = 1; pc < W; pc++) {
                sm[base + pc] = sm[lo + pc] + sm[hi + pc];
                mn[base + pc] = min(mn[lo + pc], mn[hi + pc]);
                mx[base + pc] = max(mx[lo + pc], mx[hi + pc]);
                gc[base + pc] = gcdOf(gc[lo + pc], gc[hi + pc]);
                xr[base + pc] = xr[lo + pc] ^ xr[hi + pc];
            }
        }
    }

    // cell (r, c) = v, then every node above it
    void setCell(int r, int c, T v) {
        int base = (r + R) * W;
        sm[base + c + C] = v;
        mn[base + c + C] = v;
        mx[base + c + C] = v;
        gc[base + c + C] = v;
        xr[base + c + C] = v;
        for (int pc = (c + C) >> 1; pc >= 1; pc >>= 1) {
            sm[base + pc] = sm[base + 2 * pc] + sm[base + 2 * pc + 1];
            mn[base + pc] = min(mn[base + 2 * pc], mn[base + 2 * pc + 1]);
            mx[base + pc] = max(mx[base + 2 * pc], mx[base + 2 * pc + 1]);
            gc[base + pc] = gcdOf(gc[base + 2 * pc], gc[base + 2 * pc + 1]);
            xr[base + pc] = xr[base + 2 * pc] ^ xr[base + 2 * pc + 1];
        }
        for (int pr = (r + R) >> 1; pr >= 1; pr >>= 1) {
            base = pr * W;
            int lo = 2 * base, hi = lo + W;
            for (int pc = c + C; pc >= 1; pc >>= 1) {
                sm[base + pc] = sm[lo + pc] + sm[hi + pc];
                mn[base + pc] = min(mn[lo + pc], mn[hi + pc]);
                mx[base + pc] = max(mx[lo + pc], mx[hi + pc]);
                gc[base + pc] = gcdOf(gc[lo + pc], gc[hi + pc]);
                xr[base + pc] = xr[lo + pc] ^ xr[hi + pc];
            }
        }
    }

    // O(1) -- the value at (r, c), NO_MAX if the cell is empty; needs 0 <= r < R and 0 <= c < C, else throws
    // out_of_range
    T pointGet(int r, int c) const {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("pointGet: needs 0 <= r < R and 0 <= c < C");
        return T(mx[(r + R) * W + c + C]);
    }

    // O(log R * log C) gcds -- the cell at (r, c) becomes v (it may go down as well as up); needs 0 <= r < R and 0 <=
    // c < C, else throws out_of_range
    void pointAssign(int r, int c, T v) {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("pointAssign: needs 0 <= r < R and 0 <= c < C");
        setCell(r, c, v);
    }

    // O(log R * log C) gcds -- adds v to the cell at (r, c); an empty cell becomes v; needs 0 <= r < R and 0 <= c <
    // C, else throws out_of_range
    void pointAdd(int r, int c, T v) {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("pointAdd: needs 0 <= r < R and 0 <= c < C");
        T cur = T(mx[(r + R) * W + c + C]);
        setCell(r, c, cur == NO_MAX ? v : T(cur + v));
    }

    // O(log R * log C) gcds -- the cell at (r, c) becomes max(itself, v); an empty cell becomes v; needs 0 <= r < R
    // and 0 <= c < C, else throws out_of_range
    void pointChmax(int r, int c, T v) {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("pointChmax: needs 0 <= r < R and 0 <= c < C");
        T cur = T(mx[(r + R) * W + c + C]);
        if (cur == NO_MAX || v > cur) setCell(r, c, v);
    }

    // O(log R * log C) gcds -- the cell at (r, c) becomes min(itself, v); an empty cell becomes v; needs 0 <= r < R
    // and 0 <= c < C, else throws out_of_range
    void pointChmin(int r, int c, T v) {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("pointChmin: needs 0 <= r < R and 0 <= c < C");
        T cur = T(mx[(r + R) * W + c + C]);
        if (cur == NO_MAX || v < cur) setCell(r, c, v);
    }

    S sumOf(int r1, int c1, int r2, int c2) const {
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
    // r2
    // < R and 0 <= c1 <= c2 < C, else throws out_of_range
    S rectSum(int r1, int c1, int r2, int c2) const {
        if (r1 < 0 || r1 > r2 || r2 >= R || c1 < 0 || c1 > c2 || c2 >= C)
            throw out_of_range("rectSum: needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C");
        return sumOf(r1, c1, r2, c2);
    }

    // O(1) -- sum of every set cell (0 if there are none)
    S sumAll() const {
        return sm[W + 1];
    }

    T minOf(int r1, int c1, int r2, int c2) const {
        T res = NO_MIN;
        int cl = c1 + C, cr = c2 + C + 1;
        for (int lr = r1 + R, rr = r2 + R + 1; lr < rr; lr >>= 1, rr >>= 1) {
            if (lr & 1) {
                int base = lr++ * W;
                for (int lc = cl, rc = cr; lc < rc; lc >>= 1, rc >>= 1) {
                    if (lc & 1) res = min(res, mn[base + lc++]);
                    if (rc & 1) res = min(res, mn[base + --rc]);
                }
            }
            if (rr & 1) {
                int base = --rr * W;
                for (int lc = cl, rc = cr; lc < rc; lc >>= 1, rc >>= 1) {
                    if (lc & 1) res = min(res, mn[base + lc++]);
                    if (rc & 1) res = min(res, mn[base + --rc]);
                }
            }
        }
        return res;
    }

    // O(log R * log C) -- min of the set cells in rows r1..r2, columns c1..c2 (NO_MIN if there are none); needs 0 <= r1
    // <= r2 < R and 0 <= c1 <= c2 < C, else throws out_of_range
    T rectMin(int r1, int c1, int r2, int c2) const {
        if (r1 < 0 || r1 > r2 || r2 >= R || c1 < 0 || c1 > c2 || c2 >= C)
            throw out_of_range("rectMin: needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C");
        return minOf(r1, c1, r2, c2);
    }

    // O(1) -- min of every set cell (NO_MIN if there are none)
    T minAll() const {
        return mn[W + 1];
    }

    // O(log R * log C) -- min of the set cells with row <= r and column <= c (NO_MIN if there are none); needs 0 <= r
    // < R
    // and 0 <= c < C, else throws out_of_range
    T minLteLte(int r, int c) const {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("minLteLte: needs 0 <= r < R and 0 <= c < C");
        return minOf(0, 0, r, c);
    }

    // O(log R * log C) -- min of the set cells with row <= r and column >= c (NO_MIN if there are none); needs 0 <= r
    // < R
    // and 0 <= c < C, else throws out_of_range
    T minLteGte(int r, int c) const {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("minLteGte: needs 0 <= r < R and 0 <= c < C");
        return minOf(0, c, r, C - 1);
    }

    // O(log R * log C) -- min of the set cells with row >= r and column <= c (NO_MIN if there are none); needs 0 <= r
    // < R
    // and 0 <= c < C, else throws out_of_range
    T minGteLte(int r, int c) const {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("minGteLte: needs 0 <= r < R and 0 <= c < C");
        return minOf(r, 0, R - 1, c);
    }

    // O(log R * log C) -- min of the set cells with row >= r and column >= c (NO_MIN if there are none); needs 0 <= r
    // < R
    // and 0 <= c < C, else throws out_of_range
    T minGteGte(int r, int c) const {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("minGteGte: needs 0 <= r < R and 0 <= c < C");
        return minOf(r, c, R - 1, C - 1);
    }

    T maxOf(int r1, int c1, int r2, int c2) const {
        T res = NO_MAX;
        int cl = c1 + C, cr = c2 + C + 1;
        for (int lr = r1 + R, rr = r2 + R + 1; lr < rr; lr >>= 1, rr >>= 1) {
            if (lr & 1) {
                int base = lr++ * W;
                for (int lc = cl, rc = cr; lc < rc; lc >>= 1, rc >>= 1) {
                    if (lc & 1) res = max(res, mx[base + lc++]);
                    if (rc & 1) res = max(res, mx[base + --rc]);
                }
            }
            if (rr & 1) {
                int base = --rr * W;
                for (int lc = cl, rc = cr; lc < rc; lc >>= 1, rc >>= 1) {
                    if (lc & 1) res = max(res, mx[base + lc++]);
                    if (rc & 1) res = max(res, mx[base + --rc]);
                }
            }
        }
        return res;
    }

    // O(log R * log C) -- max of the set cells in rows r1..r2, columns c1..c2 (NO_MAX if there are none); needs 0 <= r1
    // <= r2 < R and 0 <= c1 <= c2 < C, else throws out_of_range
    T rectMax(int r1, int c1, int r2, int c2) const {
        if (r1 < 0 || r1 > r2 || r2 >= R || c1 < 0 || c1 > c2 || c2 >= C)
            throw out_of_range("rectMax: needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C");
        return maxOf(r1, c1, r2, c2);
    }

    // O(1) -- max of every set cell (NO_MAX if there are none)
    T maxAll() const {
        return mx[W + 1];
    }

    // O(log R * log C) -- max of the set cells with row <= r and column <= c (NO_MAX if there are none); needs 0 <= r
    // < R
    // and 0 <= c < C, else throws out_of_range
    T maxLteLte(int r, int c) const {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("maxLteLte: needs 0 <= r < R and 0 <= c < C");
        return maxOf(0, 0, r, c);
    }

    // O(log R * log C) -- max of the set cells with row <= r and column >= c (NO_MAX if there are none); needs 0 <= r
    // < R
    // and 0 <= c < C, else throws out_of_range
    T maxLteGte(int r, int c) const {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("maxLteGte: needs 0 <= r < R and 0 <= c < C");
        return maxOf(0, c, r, C - 1);
    }

    // O(log R * log C) -- max of the set cells with row >= r and column <= c (NO_MAX if there are none); needs 0 <= r
    // < R
    // and 0 <= c < C, else throws out_of_range
    T maxGteLte(int r, int c) const {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("maxGteLte: needs 0 <= r < R and 0 <= c < C");
        return maxOf(r, 0, R - 1, c);
    }

    // O(log R * log C) -- max of the set cells with row >= r and column >= c (NO_MAX if there are none); needs 0 <= r
    // < R
    // and 0 <= c < C, else throws out_of_range
    T maxGteGte(int r, int c) const {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("maxGteGte: needs 0 <= r < R and 0 <= c < C");
        return maxOf(r, c, R - 1, C - 1);
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

    // O(log R * log C + log U) -- gcd of the set cells in rows r1..r2, columns c1..c2 (0 if there are none); needs 0 <=
    // r1 <= r2 < R and 0 <= c1 <= c2 < C, else throws out_of_range
    T rectGcd(int r1, int c1, int r2, int c2) const {
        if (r1 < 0 || r1 > r2 || r2 >= R || c1 < 0 || c1 > c2 || c2 >= C)
            throw out_of_range("rectGcd: needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C");
        return gcdOf(r1, c1, r2, c2);
    }

    // O(1) -- gcd of every set cell (0 if there are none)
    T gcdAll() const {
        return gcdOf(gc[W + 1], T(0));
    }

    T xorOf(int r1, int c1, int r2, int c2) const {
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
    // r2
    // < R and 0 <= c1 <= c2 < C, else throws out_of_range
    T rectXor(int r1, int c1, int r2, int c2) const {
        if (r1 < 0 || r1 > r2 || r2 >= R || c1 < 0 || c1 > c2 || c2 >= C)
            throw out_of_range("rectXor: needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C");
        return xorOf(r1, c1, r2, c2);
    }

    // O(1) -- xor of every set cell (0 if there are none)
    T xorAll() const {
        return xr[W + 1];
    }
};
