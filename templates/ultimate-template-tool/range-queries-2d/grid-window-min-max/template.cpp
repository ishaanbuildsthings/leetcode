// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries-2d/grid-window-min-max/template.cpp
#include <bits/stdc++.h>
using namespace std;
// @operations: windowMax windowMin
// @data-structure-type: sliding-window
// @input: grid
// @complexities:
//   windowMax: 1
//   windowMin: 1
//   build: R*C
// @memory:
//   layout: none
//   node: mn[1*R*C] mx[1*R*C]
//   tags: none
//   other: none
//   note: one answer per window position, (R - h + 1) by (C - w + 1); the build also uses one R by (C - w + 1) scratch table

// The min and max of every h x w window of a grid, for one window size fixed at the build: O(R * C) to build with no
// log (a sliding-window min and max along each row with a monotonic queue, then the same down each column of those),
// then O(1) per window. When every query has the same size this beats a sparse table on build time and memory. No
// updates. Rows and columns are 0-based; a window is named by its top-left cell.
// T is any type with < (int, long long, double, ...).
template <typename T>
struct WindowMinMax2D {
    int R, C, h, w, outW;
    vector<T> mn;
    vector<T> mx;

    // O(R*C) -- grid: R rows of C numbers each; windows are h rows by w columns; needs 1 <= h <= R and 1 <= w <= C,
    // else
    // throws invalid_argument
    WindowMinMax2D(const vector<vector<T>>& grid, int h, int w)
        : R((int)grid.size()), C(grid.empty() ? 0 : (int)grid[0].size()), h(h), w(w), outW(C - w + 1) {
        if (R < 1 || C < 1) throw invalid_argument("WindowMinMax2D: needs R >= 1 and C >= 1");
        for (auto& row : grid)
            if ((int)row.size() != C) throw invalid_argument("WindowMinMax2D: every row needs the same C values");
        if (h < 1 || h > R || w < 1 || w > C)
            throw invalid_argument("WindowMinMax2D: needs 1 <= h <= R and 1 <= w <= C");
        vector<T> rows((size_t)R * outW);  // rows[r * outW + c]: that aggregate of grid[r][c .. c + w - 1]
        vector<int> q(max(R, C));
        for (int r = 0; r < R; r++) {
            const auto& row = grid[r];
            int head = 0, tail = 0;
            for (int c = 0; c < C; c++) {
                while (tail > head && !(row[q[tail - 1]] < row[c])) tail--;
                q[tail++] = c;
                if (q[head] <= c - w) head++;
                if (c >= w - 1) rows[(size_t)r * outW + c - w + 1] = row[q[head]];
            }
        }
        mn.resize((size_t)(R - h + 1) * outW);
        for (int c = 0; c < outW; c++) {
            int head = 0, tail = 0;
            for (int r = 0; r < R; r++) {
                while (tail > head && !(rows[(size_t)q[tail - 1] * outW + c] < rows[(size_t)r * outW + c])) tail--;
                q[tail++] = r;
                if (q[head] <= r - h) head++;
                if (r >= h - 1) mn[(size_t)(r - h + 1) * outW + c] = rows[(size_t)q[head] * outW + c];
            }
        }
        for (int r = 0; r < R; r++) {
            const auto& row = grid[r];
            int head = 0, tail = 0;
            for (int c = 0; c < C; c++) {
                while (tail > head && !(row[q[tail - 1]] > row[c])) tail--;
                q[tail++] = c;
                if (q[head] <= c - w) head++;
                if (c >= w - 1) rows[(size_t)r * outW + c - w + 1] = row[q[head]];
            }
        }
        mx.resize((size_t)(R - h + 1) * outW);
        for (int c = 0; c < outW; c++) {
            int head = 0, tail = 0;
            for (int r = 0; r < R; r++) {
                while (tail > head && !(rows[(size_t)q[tail - 1] * outW + c] > rows[(size_t)r * outW + c])) tail--;
                q[tail++] = r;
                if (q[head] <= r - h) head++;
                if (r >= h - 1) mx[(size_t)(r - h + 1) * outW + c] = rows[(size_t)q[head] * outW + c];
            }
        }
    }

    // O(1) -- min of the h x w window whose top-left cell is (r, c); needs 0 <= r <= R - h and 0 <= c <= C - w, else
    // throws out_of_range
    T windowMin(int r, int c) const {
        if (r < 0 || r > R - h || c < 0 || c > C - w)
            throw out_of_range("windowMin: needs 0 <= r <= R - h and 0 <= c <= C - w");
        return mn[(size_t)r * outW + c];
    }

    // O(1) -- max of the h x w window whose top-left cell is (r, c); needs 0 <= r <= R - h and 0 <= c <= C - w, else
    // throws out_of_range
    T windowMax(int r, int c) const {
        if (r < 0 || r > R - h || c < 0 || c > C - w)
            throw out_of_range("windowMax: needs 0 <= r <= R - h and 0 <= c <= C - w");
        return mx[(size_t)r * outW + c];
    }
};
