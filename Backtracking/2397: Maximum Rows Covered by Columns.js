// https://leetcode.com/problems/maximum-rows-covered-by-columns/description/
// difficulty: Medium
// tags: Backtracking

// Problem
/*
You are given a 0-indexed m x n binary matrix matrix and an integer numSelect, which denotes the number of distinct columns you must select from matrix.

Let us consider s = {c1, c2, ...., cnumSelect} as the set of columns selected by you. A row row is covered by s if:

For each cell matrix[row][col] (0 <= col <= n - 1) where matrix[row][col] == 1, col is present in s or,
No cell in row has a value of 1.
You need to choose numSelect columns such that the number of rows that are covered is maximized.

Return the maximum number of rows that can be covered by a set of numSelect columns.
*/

// Solution, O(2^cols * rows * cols) time and O(rows * cols) space
/*
I just brute forced it with backtracking. For each column, we can take or skip it. Once we have taken numSelect column, check each row, which takes n*m time for all rows. There are at most 12 columns, so 2^12 possibilities, and each state takes m*n time. I am sure there are some optimizations with pruning/caching/bitmask :)
*/

var maximumRows = function (matrix, numSelect) {
  const HEIGHT = matrix.length;
  const WIDTH = matrix[0].length;

  let result = 0;

  function backtrack(selectedCols, i) {
    if (selectedCols.length === numSelect) {
      let totalRowsCovered = 0;
      // check all rows and see which are covered
      for (let r = 0; r < HEIGHT; r++) {
        let invalidFound = false;
        for (let c = 0; c < WIDTH; c++) {
          // if we see a 1, and we didn't select that column, we don't add that row
          if (matrix[r][c] === 1 && !selectedCols.includes(c)) {
            invalidFound = true;
            break;
          }
        }
        if (!invalidFound) {
          totalRowsCovered++;
        }
      }
      result = Math.max(totalRowsCovered, result);
      return;
    }

    // if we ran out of columns to choose from, stop
    if (i === WIDTH) {
      return;
    }

    // if we take the current column
    selectedCols.push(i);
    backtrack(selectedCols, i + 1);
    selectedCols.pop();

    // leave the current column
    backtrack(selectedCols, i + 1);
  }

  backtrack([], 0);

  return result;
};
