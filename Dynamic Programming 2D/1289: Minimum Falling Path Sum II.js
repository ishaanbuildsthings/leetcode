// https://leetcode.com/problems/minimum-falling-path-sum-ii/description/
// Difficulty: Hard
// tags: dynamic programming 2d, bottom up recursion

// Problem
/*
Simplified:
We have an n x n matrix of numbers. We must make a path starting from the first row, to the last row. Adjacent rows in the path cannot share the same column. Find the minimum falling path sum.

Detailed:
Given an n x n integer matrix grid, return the minimum sum of a falling path with non-zero shifts.

A falling path with non-zero shifts is a choice of exactly one element from each row of grid such that no two elements chosen in adjacent rows are in the same column.
*/

// Solution, O(n^3) time and O(n^2) space.
// Can be improved to O(n) space if we store a single row of the dp. We can reduce to O(1) space for this problem by using pointers. We can also reduce to O(n^2) time with pointers. The idea is to scan a row, pick the two smallest numbers. Now for the next row, we pick the smallest provided a row is different, and repeat.

/*
Create a dp matrix. Start from the 2nd to last row, going up (as the last row of the dp is just the values from the matrix). For each value, find the minimum below it, that doesn't share a column. Fill the dp. Return the minimum from the first row.

Because we process n^2 elements, and for each element we have to check n elements below it, the time complexity is O(n^3). The space complexity is O(n^2) because we have to store the dp.
*/

var minFallingPathSum = function (matrix) {
  const SIDELENGTH = matrix.length;
  // maintain a dp array, each falling path minimum sum will use the minimum of the three options below it.
  const dp = new Array(SIDELENGTH)
    .fill()
    .map(() => new Array(SIDELENGTH).fill(null));

  // seed the bottom row
  for (let colNum = 0; colNum < SIDELENGTH; colNum++) {
    dp[matrix.length - 1][colNum] = matrix[matrix.length - 1][colNum];
  }

  // console.log(`dp is: ${JSON.stringify(dp)}`);

  // start iterating from the second to bottom row, filling out the dp
  for (let rowNum = SIDELENGTH - 2; rowNum >= 0; rowNum--) {
    // we start at 1, since the edges of the DP are padded
    for (let colNum = 0; colNum < SIDELENGTH; colNum++) {
      // for a given cell, we can choose any cell one row below, as long as it isn't in the same column
      let currentMinimum = Infinity;
      // console.log(`solving for cell ${rowNum} ${colNum} which has value: ${matrix[rowNum][colNum]}`)
      for (let i = 0; i < SIDELENGTH; i++) {
        // console.log(`checking child at column ${i}`)
        // don't consider same column
        if (i === colNum) {
          // console.log(`same column, skipping`)
          continue;
        }
        const rowBelowMinSum = dp[rowNum + 1][i];
        // console.log(`row below min sum: ${rowBelowMinSum}`)

        currentMinimum = Math.min(currentMinimum, rowBelowMinSum);
      }

      dp[rowNum][colNum] = matrix[rowNum][colNum] + currentMinimum;
    }
  }

  return Math.min(...dp[0]); // return the smallest number from the first row, as we would start there
};
