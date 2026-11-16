// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/generic-2d/GenericRectSparseTable.cpp
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

// A static R x C grid (no updates): O(R*C*logR*logC) build and Nodes of memory, O(1) rectQuery (at most 3 combine
// calls). For square queries only, GenericSquareSparseTable needs a single log.
// RectSparseTable st(grid);    // grid: vector<vector<RawVal>>, R rows of C values
struct RectSparseTable {
    int R, C, levelsR, levelsC;
    // t[kr * levelsC + kc]: the Node of every window of 2^kr rows by 2^kc columns, flat, (R - 2^kr + 1) rows of
    // (C - 2^kc + 1)
    vector<vector<Node>> t;

    RectSparseTable(const vector<vector<RawVal>>& grid) : R(grid.size()), C(grid.empty() ? 0 : grid[0].size()) {
        if (R < 1 || C < 1) throw invalid_argument("RectSparseTable: needs R >= 1 and C >= 1");
        for (auto& row : grid)
            if ((int)row.size() != C) throw invalid_argument("RectSparseTable: every row needs the same C values");
        levelsR = 32 - __builtin_clz(R), levelsC = 32 - __builtin_clz(C);
        t.resize((size_t)levelsR * levelsC);
        t[0].reserve((size_t)R * C);
        for (int r = 0; r < R; r++)
            for (int c = 0; c < C; c++) t[0].push_back(baseFn(grid[r][c], r, c));
        for (int kc = 1; kc < levelsC; kc++) {
            int half = 1 << (kc - 1), prevW = C - half + 1, w = C - (1 << kc) + 1;
            const auto& prev = t[kc - 1];
            auto& cur = t[kc];
            cur.reserve((size_t)R * w);
            for (int r = 0; r < R; r++)
                for (int c = 0; c < w; c++) cur.push_back(combine(prev[r * prevW + c], prev[r * prevW + c + half]));
        }
        for (int kr = 1; kr < levelsR; kr++) {
            int half = 1 << (kr - 1), h = R - (1 << kr) + 1;
            for (int kc = 0; kc < levelsC; kc++) {
                int w = C - (1 << kc) + 1, off = half * w;
                const auto& prev = t[(size_t)(kr - 1) * levelsC + kc];
                auto& cur = t[(size_t)kr * levelsC + kc];
                cur.reserve((size_t)h * w);
                for (int i = 0; i < h * w; i++) cur.push_back(combine(prev[i], prev[i + off]));
            }
        }
    }

    // the Node of cell (r, c); needs 0 <= r < R and 0 <= c < C, else out_of_range
    Node pointGet(int r, int c) {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("pointGet: needs 0 <= r < R and 0 <= c < C");
        return t[0][(size_t)r * C + c];
    }

    // the Node of rows r1..r2, columns c1..c2: the combine of four power-of-two windows, one in each corner (they
    // overlap, which is why combine must be idempotent); needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C, else
    // out_of_range
    Node rectQuery(int r1, int c1, int r2, int c2) {
        if (r1 < 0 || r1 > r2 || r2 >= R || c1 < 0 || c1 > c2 || c2 >= C)
            throw out_of_range("rectQuery: needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C");
        int kr = 31 - __builtin_clz(r2 - r1 + 1), kc = 31 - __builtin_clz(c2 - c1 + 1);
        const auto& tab = t[(size_t)kr * levelsC + kc];
        int w = C - (1 << kc) + 1, i = r1 * w + c1, j = (r2 - (1 << kr) + 1) * w + c1, d = c2 - (1 << kc) + 1 - c1;
        if (i == j) return d ? combine(tab[i], tab[i + d]) : tab[i];
        if (!d) return combine(tab[i], tab[j]);
        return combine(combine(tab[i], tab[i + d]), combine(tab[j], tab[j + d]));
    }

    // the Node of the whole grid
    Node rectQueryAll() { return rectQuery(0, 0, R - 1, C - 1); }
};
