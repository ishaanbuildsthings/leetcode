// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries-2d/grid-bit-sum/template.cpp
#include <bits/stdc++.h>
using namespace std;
// @operations: pointAdd pointAssign pointChmax pointChmin pointGet rectSum sumAll
// @data-structure-type: BIT
// @input: grid
// @complexities:
//   pointAdd: log(R)*log(C)
//   pointAssign: log(R)*log(C)
//   pointChmax: log(R)*log(C)
//   pointChmin: log(R)*log(C)
//   pointGet: 1
//   rectSum: log(R)*log(C)
//   sumAll: 1
//   build: R*C
// @memory:
//   layout: none
//   node: sm[1*R*C]
//   tags: none
//   other: vals[1*R*C]
//   note: each Fenwick tree is (R + 1) by (C + 1), flat, 1-based; vals keeps the cells themselves for O(1) reads

// 2D Fenwick tree (sum): point updates and any-rectangle sum on an R x C grid, O(log R * log C) each, with a quarter
// of a 2D segment tree's memory and a smaller constant. A rectangle is four prefix queries (the big corner, minus the
// strip above, minus the strip to the left, plus the corner both took off). Rows and columns are 0-based and
// rectangles are inclusive: rows r1..r2, columns c1..c2. The (R, C) constructor starts with every cell 0.
// T is any integer type (int, long long, ...); sums are kept in S (long long for a smaller T).
template <typename T>
struct Fenwick2D {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    int R, C, W;
    vector<T> vals;
    vector<S> sm;
    S totalSum = 0;

    // O(R*C) -- R rows by C columns, every cell 0; needs R >= 1 and C >= 1, else throws invalid_argument
    Fenwick2D(int rows, int cols) : R(rows), C(cols), W(cols + 1) {
        if (R < 1 || C < 1) throw invalid_argument("Fenwick2D: needs R >= 1 and C >= 1");
        vals.assign((size_t)R * C, T(0));
        sm.assign((size_t)(R + 1) * W, 0);
    }

    // O(R*C) -- grid: R rows of C numbers each; needs R >= 1 and C >= 1, else throws invalid_argument
    explicit Fenwick2D(const vector<vector<T>>& grid)
        : Fenwick2D((int)grid.size(), grid.empty() ? 0 : (int)grid[0].size()) {
        for (int r = 0; r < R; r++) {
            if ((int)grid[r].size() != C) throw invalid_argument("Fenwick2D: every row needs the same C values");
            for (int c = 0; c < C; c++) vals[(size_t)r * C + c] = grid[r][c];
        }
        auto& tSum = sm;
        for (int r = 1; r <= R; r++) {
            int at = r * W;
            for (int c = 1; c <= C; c++) {
                tSum[at + c] += grid[r - 1][c - 1];
                totalSum += grid[r - 1][c - 1];
                int j = c + (c & -c);  // each entry is added into the next one that covers it
                if (j <= C) tSum[at + j] += tSum[at + c];
            }
        }
        for (int r = 1; r <= R; r++) {
            int j = r + (r & -r);
            if (j > R) continue;
            for (int c = 1; c <= C; c++) tSum[j * W + c] += tSum[r * W + c];
        }
    }

    // cell (r, c) becomes v
    void setCell(int r, int c, T v) {
        T old = vals[(size_t)r * C + c];
        vals[(size_t)r * C + c] = v;
        S dSum = S(v) - old;
        totalSum += dSum;
        for (int i = r + 1; i <= R; i += i & -i)
            for (int j = c + 1; j <= C; j += j & -j) sm[i * W + j] += dSum;
    }

    // sum of the first r rows and first c columns
    S prefixSum(int r, int c) const {
        S res = 0;
        for (int i = r; i > 0; i &= i - 1)
            for (int j = c; j > 0; j &= j - 1) res += sm[i * W + j];
        return res;
    }

    // O(1) -- the value at (r, c); needs 0 <= r < R and 0 <= c < C, else throws out_of_range
    T pointGet(int r, int c) const {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("pointGet: needs 0 <= r < R and 0 <= c < C");
        return vals[(size_t)r * C + c];
    }

    // O(log R * log C) -- the cell at (r, c) becomes v; needs 0 <= r < R and 0 <= c < C, else throws out_of_range
    void pointAssign(int r, int c, T v) {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("pointAssign: needs 0 <= r < R and 0 <= c < C");
        setCell(r, c, v);
    }

    // O(log R * log C) -- adds v to the cell at (r, c); needs 0 <= r < R and 0 <= c < C, else throws out_of_range
    void pointAdd(int r, int c, T v) {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("pointAdd: needs 0 <= r < R and 0 <= c < C");
        setCell(r, c, T(vals[(size_t)r * C + c] + v));
    }

    // O(log R * log C) -- the cell at (r, c) becomes max(itself, v); needs 0 <= r < R and 0 <= c < C, else throws
    // out_of_range
    void pointChmax(int r, int c, T v) {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("pointChmax: needs 0 <= r < R and 0 <= c < C");
        if (v > vals[(size_t)r * C + c]) setCell(r, c, v);
    }

    // O(log R * log C) -- the cell at (r, c) becomes min(itself, v); needs 0 <= r < R and 0 <= c < C, else throws
    // out_of_range
    void pointChmin(int r, int c, T v) {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("pointChmin: needs 0 <= r < R and 0 <= c < C");
        if (v < vals[(size_t)r * C + c]) setCell(r, c, v);
    }

    // O(log R * log C) -- sum of rows r1..r2, columns c1..c2; needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C, else
    // throws
    // out_of_range
    S rectSum(int r1, int c1, int r2, int c2) const {
        if (r1 < 0 || r1 > r2 || r2 >= R || c1 < 0 || c1 > c2 || c2 >= C)
            throw out_of_range("rectSum: needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C");
        return prefixSum(r2 + 1, c2 + 1) - prefixSum(r1, c2 + 1) - prefixSum(r2 + 1, c1) + prefixSum(r1, c1);
    }

    // O(1) -- sum of the whole grid
    S sumAll() const {
        return totalSum;
    }
};
