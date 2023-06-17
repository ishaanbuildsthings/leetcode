// https://leetcode.com/problems/minimum-path-sum/description/
// difficulty: medium
// tags: dynamic programming 2d

// problem
/*
Given a m x n grid filled with non-negative numbers, find a path from top left to bottom right, which minimizes the sum of all numbers along its path.

Note: You can only move either down or right at any point in time.
*/

/*
WRITEUP

To solve this, for a cell, we need to look at the minimum bottom path sum, and the minimum right path sum, and choose which to go to. We can solve this with recursion + memoization, or tabulation. For recursion, we solve the cell 0,0 by recursing on its neighbors, and doing cache lookups if we have already computed it. For tabulation, we start at the bottom right base problem, and iterate as needed. Both solutions require n*m memory for either the cache or tabulation table, and n*m time as we solve for each cell.
*/

// tabulation solution, a bit hacky with the Infinities, done to avoid checking if neighbors exceed the boundaries.

var minPathSum = function (grid) {
  const HEIGHT = grid.length;
  const WIDTH = grid[0].length;

  const dp = new Array(HEIGHT + 1)
    .fill()
    .map(() => new Array(WIDTH + 1).fill(Infinity));

  for (let rowNum = HEIGHT - 1; rowNum >= 0; rowNum--) {
    for (let colNum = WIDTH - 1; colNum >= 0; colNum--) {
      if (rowNum === HEIGHT - 1 && colNum === WIDTH - 1) {
        dp[rowNum][colNum] = grid[rowNum][colNum];
        continue;
      }
      dp[rowNum][colNum] =
        grid[rowNum][colNum] +
        Math.min(dp[rowNum + 1][colNum], dp[rowNum][colNum + 1]);
    }
  }

  return dp[0][0];
};

// recursion + memoization solution
var minPathSum = function (grid) {
  const HEIGHT = grid.length;
  const WIDTH = grid[0].length;

  const cache = {}; // maps a cell to its result

  // returns the min path sum for a given cell
  function recurse(row, col) {
    const key = JSON.stringify([row, col]);
    if (key in cache) {
      return cache[key];
    }

    const val = grid[row][col];

    // if we can move both down and right
    if (row + 1 < HEIGHT && col + 1 < WIDTH) {
      const currentCellMin =
        val + Math.min(recurse(row + 1, col), recurse(row, col + 1));
      cache[key] = currentCellMin;
      return currentCellMin;
    }
    // if we can only move right
    else if (col + 1 < WIDTH) {
      const currentCellMin = val + recurse(row, col + 1);
      cache[key] = currentCellMin;
      return currentCellMin;
    }
    // if we can only move down
    else if (row + 1 < HEIGHT) {
      const currentCellMin = val + recurse(row + 1, col);
      cache[key] = currentCellMin;
      return currentCellMin;
    }
    // we cannot move right or down
    else {
      cache[key] = val;
      return val;
    }
  }

  return recurse(0, 0);
};
