// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries-2d/grid-square-sparse-table-min-gcd-or/template.cpp
#include <bits/stdc++.h>
using namespace std;
// @operations: pointGet squareGcd squareMin squareOr
// @data-structure-type: square-sparse-table
// @input: grid
// @complexities:
//   pointGet: 1
//   squareGcd: log(U) ?
//   squareMin: 1
//   squareOr: 1
//   build: R*C*log(min(R,C))*log(U) ?
// @memory:
//   layout: none
//   node: mn[1*R*C*log(min(R,C))] gc[1*R*C*log(min(R,C))] orr[1*R*C*log(min(R,C))]
//   tags: none
//   other: none
//   note: per aggregate, one table per power-of-two side (side 1 is the grid itself, shared)

// Static sparse table for square queries only (min, gcd, OR): O(1) per square (one gcd run, O(log U)), with a single
// log of memory and build, R * C * log(min(R, C)), where the any-rectangle sparse table needs log R * log C. Level k
// holds the aggregate of every 2^k by 2^k window; a square is covered by four such windows, one in each corner (they
// overlap, which is fine for these aggregates). No updates. Rows and columns are 0-based; a square is its top-left
// cell (r, c) and its side.
// T is any integer type (int, long long, ...).
template <typename T>
struct SquareSparseTable2D {
    int R, C;
    vector<vector<T>> mn;  // [k]: windows of 2^k by 2^k, flat
    vector<vector<T>> gc;  // [k]: windows of 2^k by 2^k, flat
    vector<vector<T>> orr;  // [k]: windows of 2^k by 2^k, flat

    // O(R*C*log(min(R, C))*logU) -- grid: R rows of C numbers each; needs R >= 1 and C >= 1, else throws
    // invalid_argument
    explicit SquareSparseTable2D(const vector<vector<T>>& grid)
        : R((int)grid.size()), C(grid.empty() ? 0 : (int)grid[0].size()) {
        if (R < 1 || C < 1) throw invalid_argument("SquareSparseTable2D: needs R >= 1 and C >= 1");
        for (auto& row : grid)
            if ((int)row.size() != C) throw invalid_argument("SquareSparseTable2D: every row needs the same C values");
        int levels = 32 - __builtin_clz(min(R, C));
        vector<T> flat;
        flat.reserve((size_t)R * C);
        for (auto& row : grid) flat.insert(flat.end(), row.begin(), row.end());
        mn.assign(levels, vector<T>());
        mn[0] = flat;
        for (int k = 1; k < levels; k++) {
            int half = 1 << (k - 1), prevW = C - half + 1, h = R - (1 << k) + 1, w = C - (1 << k) + 1;
            const auto& prev = mn[k - 1];
            auto& cur = mn[k];
            cur.resize((size_t)h * w);
            for (int i = 0; i < h; i++) {
                const T* top = prev.data() + (size_t)i * prevW;
                const T* bot = top + (size_t)half * prevW;
                T* out = cur.data() + (size_t)i * w;
                for (int j = 0; j < w; j++)
                    out[j] = min(min(top[j], top[j + half]), min(bot[j], bot[j + half]));
            }
        }
        gc.assign(levels, vector<T>());
        gc[0] = flat;
        for (int k = 1; k < levels; k++) {
            int half = 1 << (k - 1), prevW = C - half + 1, h = R - (1 << k) + 1, w = C - (1 << k) + 1;
            const auto& prev = gc[k - 1];
            auto& cur = gc[k];
            cur.resize((size_t)h * w);
            for (int i = 0; i < h; i++) {
                const T* top = prev.data() + (size_t)i * prevW;
                const T* bot = top + (size_t)half * prevW;
                T* out = cur.data() + (size_t)i * w;
                for (int j = 0; j < w; j++)
                    out[j] = std::gcd(std::gcd(top[j], top[j + half]), std::gcd(bot[j], bot[j + half]));
            }
        }
        orr.assign(levels, vector<T>());
        orr[0] = flat;
        for (int k = 1; k < levels; k++) {
            int half = 1 << (k - 1), prevW = C - half + 1, h = R - (1 << k) + 1, w = C - (1 << k) + 1;
            const auto& prev = orr[k - 1];
            auto& cur = orr[k];
            cur.resize((size_t)h * w);
            for (int i = 0; i < h; i++) {
                const T* top = prev.data() + (size_t)i * prevW;
                const T* bot = top + (size_t)half * prevW;
                T* out = cur.data() + (size_t)i * w;
                for (int j = 0; j < w; j++)
                    out[j] = top[j] | top[j + half] | bot[j] | bot[j + half];
            }
        }
    }

    // O(1) -- min of the square with top-left cell (r, c) and that many rows and columns; needs side >= 1 and the
    // square
    // inside the grid, else throws out_of_range
    T squareMin(int r, int c, int side) const {
        if (side < 1 || r < 0 || r + side > R || c < 0 || c + side > C)
            throw out_of_range("squareMin: needs side >= 1 and the square inside the grid");
        int k = 31 - __builtin_clz(side), w = C - (1 << k) + 1, d = side - (1 << k), i = r * w + c, j = i + d * w;
        const auto& t = mn[k];
        return min(min(t[i], t[i + d]), min(t[j], t[j + d]));
    }

    // O(log U) -- gcd of the square with top-left cell (r, c) and that many rows and columns; needs side >= 1 and the
    // square inside the grid, else throws out_of_range
    T squareGcd(int r, int c, int side) const {
        if (side < 1 || r < 0 || r + side > R || c < 0 || c + side > C)
            throw out_of_range("squareGcd: needs side >= 1 and the square inside the grid");
        int k = 31 - __builtin_clz(side), w = C - (1 << k) + 1, d = side - (1 << k), i = r * w + c, j = i + d * w;
        const auto& t = gc[k];
        return std::gcd(std::gcd(t[i], t[i + d]), std::gcd(t[j], t[j + d]));
    }

    // O(1) -- OR of the square with top-left cell (r, c) and that many rows and columns; needs side >= 1 and the square
    // inside the grid, else throws out_of_range
    T squareOr(int r, int c, int side) const {
        if (side < 1 || r < 0 || r + side > R || c < 0 || c + side > C)
            throw out_of_range("squareOr: needs side >= 1 and the square inside the grid");
        int k = 31 - __builtin_clz(side), w = C - (1 << k) + 1, d = side - (1 << k), i = r * w + c, j = i + d * w;
        const auto& t = orr[k];
        return t[i] | t[i + d] | t[j] | t[j + d];
    }

    // O(1) -- the value at (r, c); needs 0 <= r < R and 0 <= c < C, else throws out_of_range
    T pointGet(int r, int c) const {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("pointGet: needs 0 <= r < R and 0 <= c < C");
        return mn[0][(size_t)r * C + c];
    }
};
