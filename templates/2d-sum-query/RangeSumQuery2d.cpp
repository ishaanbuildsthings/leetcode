// RangeSumQuery2d<int> rsq({{3, 0, 1}, {5, 6, 3}, {1, 2, 0}}); rsq.sumRegion(0, 1, 2, 2) == 12;
#include <bits/stdc++.h>
using namespace std;
template <typename T>
class RangeSumQuery2d {
public:
    // O(rows * cols) time, O(rows * cols) space.
    RangeSumQuery2d(const vector<vector<T>>& matrix) {
        int rows = matrix.size();
        int cols = matrix[0].size();
        prefixSums.assign(rows, vector<T>(cols, T{}));
        for (int r = 0; r < rows; r++) {
            for (int c = 0; c < cols; c++) {
                T sumForCell = T{};
                if (r > 0) {
                    sumForCell += prefixSums[r - 1][c];
                }
                if (c > 0) {
                    sumForCell += prefixSums[r][c - 1];
                }
                sumForCell += matrix[r][c];
                if (r > 0 && c > 0) {
                    sumForCell -= prefixSums[r - 1][c - 1];
                }
                prefixSums[r][c] = sumForCell;
            }
        }
    }

    // Sum over the inclusive rectangle [row1..row2] x [col1..col2]. O(1) time.
    T sumRegion(int row1, int col1, int row2, int col2) {
        T sumForRegion = T{};
        sumForRegion += prefixSums[row2][col2];
        if (row1 > 0 && col1 > 0) {
            sumForRegion += prefixSums[row1 - 1][col1 - 1];
        }
        if (col1 > 0) {
            sumForRegion -= prefixSums[row2][col1 - 1];
        }
        if (row1 > 0) {
            sumForRegion -= prefixSums[row1 - 1][col2];
        }
        return sumForRegion;
    }

private:
    vector<vector<T>> prefixSums;
};