// https://leetcode.com/problems/minimum-falling-path-sum/description/
// Difficulty: Medium
// tags: dynamic programming 2d, bottom up recursion

// Problem
/*
Simplified:
We have an n x n matrix with numbers. Starting from the first row, we must fall down to the bottom. Falling is either choosing col-1, col, or col+1. Find the minimum falling path sum.

Detailed:

Given an n x n array of integers matrix, return the minimum sum of any falling path through matrix.

A falling path starts at any element in the first row and chooses the element in the next row that is either directly below or diagonally left/right. Specifically, the next element from position (row, col) will be (row + 1, col - 1), (row + 1, col), or (row + 1, col + 1).
*/

// Solution, O(n^2) time and O(n^2) space.
// * Can be improved to O(n) space if we just maintain a single row of the dp, and keep overwriting it. Or O(1) space if we overwrite the initial input.

/*
Create a dp array. Start at the 2nd to last row, determininig the minimum path we can take. Fill the dp. Keep iterating up, then return the smallest from the first row, since we could start at any index.
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

  // start iterating from the second to bottom row, filling out the dp
  for (let rowNum = SIDELENGTH - 2; rowNum >= 0; rowNum--) {
    // we start at 1, since the edges of the DP are padded
    for (let colNum = 0; colNum < SIDELENGTH; colNum++) {
      const leftOption = dp[rowNum + 1][colNum === 0 ? 0 : colNum - 1]; // a little trick, if we are on the left edge, just default to the option right below it, otherwise go left
      const middleOption = dp[rowNum + 1][colNum];
      const rightOption =
        dp[rowNum + 1][colNum === SIDELENGTH - 1 ? colNum : colNum + 1];

      const newMinimum =
        matrix[rowNum][colNum] +
        Math.min(leftOption, middleOption, rightOption);
      dp[rowNum][colNum] = newMinimum;
    }
  }

  return Math.min(...dp[0]); // return the smallest number from the first row, as we would start there
};
