// https://leetcode.com/problems/unique-paths/description/
// tags: dynamic programming 2d, bottom up recursion, top down recursion

// Problem
/*
There is a robot on an m x n grid. The robot is initially located at the top-left corner (i.e., grid[0][0]). The robot tries to move to the bottom-right corner (i.e., grid[m - 1][n - 1]). The robot can only move either down or right at any point in time.

Given the two integers m and n, return the number of possible unique paths that the robot can take to reach the bottom-right corner.

The test cases are generated so that the answer will be less than or equal to 2 * 109.
*/

// Solution, O(n*m) time and O(n*m) space. Allocate an n*m matrix. For each cell, the number of ways to reach the end is the sum of the cell below it, and to the right. We can either use bottom up or top down + memoization. I used bottom up. I also allocated an m+1 * n+1 matrix where the bottom row and rightmost column were filled with 0s. I then filled the bottom right cell with 1, and iterated from the bottom right cell to the top left cell, filling in the number of ways to reach the end for each cell. I allocated the extra 0s so I didn't have to deal with checking if things are in range. A simpler way might have been to make the leftmost and topmost areas of the matrix all 1s, so that at the initial bottom right cell, [1,1], we could have 2 paths to reach it.

var uniquePaths = function (m, n) {
  const dp = new Array(m + 1).fill().map(() => new Array(n + 1).fill(0));
  dp[m - 1][n - 1] = 1; // seed the bottom right cell to be one path

  for (let rowNum = m - 1; rowNum >= 0; rowNum--) {
    for (let colNum = n - 1; colNum >= 0; colNum--) {
      if (rowNum === m - 1 && colNum === n - 1) continue; // skip the seeded number
      dp[rowNum][colNum] = dp[rowNum + 1][colNum] + dp[rowNum][colNum + 1];
    }
  }

  return dp[0][0];
};
