// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/generic-2d/GenericSquareSparseTable.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// e.g. long long, char, pair, struct, ...
using RawVal = long long;

struct Node {
    // long long mn;
    // long long mx;
};

Node baseFn(const RawVal& v, int r, int c) {
    // Node res;
    // res.mn = v, res.mx = v;
    // return res;
}

// combine MUST be idempotent: combine(x, x) == x (min, max, gcd, lcm, AND, OR, ... but NOT sum or count), and the
// order of its two arguments must not matter
Node combine(const Node& a, const Node& b) {
    // Node res;
    // res.mn = min(a.mn, b.mn);
    // res.mx = max(a.mx, b.mx);
    // return res;
}

// A static R x C grid (no updates), square queries only: O(R*C*log(min(R, C))) build and Nodes of memory (a single
// log, where GenericRectSparseTable needs log R * log C), O(1) squareQuery (at most 3 combine calls).
// SquareSparseTable st(grid);    // grid: vector<vector<RawVal>>, R rows of C values
struct SquareSparseTable {
    int R, C;
    vector<vector<Node>> t;  // t[k]: the Node of every 2^k by 2^k window, flat, (R - 2^k + 1) rows of (C - 2^k + 1)

    SquareSparseTable(const vector<vector<RawVal>>& grid) : R(grid.size()), C(grid.empty() ? 0 : grid[0].size()) {
        if (R < 1 || C < 1) throw invalid_argument("SquareSparseTable: needs R >= 1 and C >= 1");
        for (auto& row : grid)
            if ((int)row.size() != C) throw invalid_argument("SquareSparseTable: every row needs the same C values");
        int levels = 32 - __builtin_clz(min(R, C));
        t.resize(levels);
        t[0].reserve((size_t)R * C);
        for (int r = 0; r < R; r++)
            for (int c = 0; c < C; c++) t[0].push_back(baseFn(grid[r][c], r, c));
        for (int k = 1; k < levels; k++) {
            int half = 1 << (k - 1), prevW = C - half + 1, h = R - (1 << k) + 1, w = C - (1 << k) + 1;
            const auto& prev = t[k - 1];
            auto& cur = t[k];
            cur.reserve((size_t)h * w);
            for (int i = 0; i < h; i++) {
                const Node* top = prev.data() + (size_t)i * prevW;
                const Node* bot = top + (size_t)half * prevW;
                for (int j = 0; j < w; j++)
                    cur.push_back(combine(combine(top[j], top[j + half]), combine(bot[j], bot[j + half])));
            }
        }
    }

    // the Node of cell (r, c); needs 0 <= r < R and 0 <= c < C, else out_of_range
    Node pointGet(int r, int c) {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("pointGet: needs 0 <= r < R and 0 <= c < C");
        return t[0][(size_t)r * C + c];
    }

    // the Node of the square with top-left cell (r, c) and that many rows and columns: the combine of four power-of-two
    // squares, one in each corner (they overlap, which is why combine must be idempotent); needs
    // side >= 1 and the square inside the grid, else out_of_range
    Node squareQuery(int r, int c, int side) {
        if (side < 1 || r < 0 || r + side > R || c < 0 || c + side > C)
            throw out_of_range("squareQuery: needs side >= 1 and the square inside the grid");
        int k = 31 - __builtin_clz(side), w = C - (1 << k) + 1, d = side - (1 << k), i = r * w + c, j = i + d * w;
        const auto& tab = t[k];
        if (!d) return tab[i];
        return combine(combine(tab[i], tab[i + d]), combine(tab[j], tab[j + d]));
    }
};
