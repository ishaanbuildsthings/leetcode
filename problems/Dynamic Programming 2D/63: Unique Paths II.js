// https://leetcode.com/problems/unique-paths-ii/description/
// Difficulty: Medium
// tags: dynamic programming 2d, bottom up recursion

// Problem
/*
Simplified:

We have a grid with potentially some obstacles on it. We need to move from the top left cell, to the bottom right cell, only ever moving down or right. Return the number of ways we can do this.

Detailed:
You are given an m x n integer array grid. There is a robot initially located at the top-left corner (i.e., grid[0][0]). The robot tries to move to the bottom-right corner (i.e., grid[m - 1][n - 1]). The robot can only move either down or right at any point in time.

An obstacle and space are marked as 1 or 0 respectively in grid. A path that the robot takes cannot include any square that is an obstacle.

Return the number of possible unique paths that the robot can take to reach the bottom-right corner.

The testcases are generated so that the answer will be less than or equal to 2 * 109.
*/

// Solution, O(n*m) time and O(n*m) space.
// * We can use O(min(n, m)) space by just maintaining a dp of the previous row or previous column (we could use which is smaller). We could use O(1) space by modifying it in place.

/*
For each cell, the number of ways to reach it is the number of ways coming from above, plus coming from the left. We seed the leftmost column and topmost row with 1s, or a 0 if we have seen an obstacle before / including that point. Then we iterate through the dp, building the tabulation. We return the value at the bottom right dp.
*/

var uniquePathsWithObstacles = function (obstacleGrid) {
  const HEIGHT = obstacleGrid.length;
  const WIDTH = obstacleGrid[0].length;

  // create a dp owhich will help us calculate how many ways we can reach a specific cell.
  const dp = new Array(HEIGHT).fill().map(() => new Array(WIDTH).fill(null));

  // seed the leftmost column, each cell either has 1 way to reach it, or 0 if there is an obstacle at that cell or somewhere above it
  let obstacleFound = false;
  for (let rowNum = 0; rowNum < HEIGHT; rowNum++) {
    if (obstacleFound) {
      dp[rowNum][0] = 0;
      continue;
    }

    // if there is a rock in the leftmost column, the # of ways to reach that cell is 0
    if (obstacleGrid[rowNum][0] === 1) {
      dp[rowNum][0] = 0;
      obstacleFound = true;
    } else {
      dp[rowNum][0] = 1;
    }
  }

  // seed the top row
  let rowObstacleFound = false;
  for (let colNum = 0; colNum < WIDTH; colNum++) {
    if (rowObstacleFound) {
      dp[0][colNum] = 0;
      continue;
    }

    if (obstacleGrid[0][colNum] === 1) {
      dp[0][colNum] = 0;
      rowObstacleFound = true;
    } else {
      dp[0][colNum] = 1;
    }
  }

  // we iterate, ignoring the leftmost and topmost areas. this is because those have predefined values / are base cases, either 1, or 0 if there was an obstacle there
  for (let rowNum = 1; rowNum < HEIGHT; rowNum++) {
    for (let colNum = 1; colNum < WIDTH; colNum++) {
      // if our current cell has an obstacle, there are 0 ways to reach it, so we set that and continue
      if (obstacleGrid[rowNum][colNum] === 1) {
        dp[rowNum][colNum] = 0;
        continue;
      }

      // the number of ways to reach a cell is the sum of the ways from the left, and from above
      dp[rowNum][colNum] = dp[rowNum - 1][colNum] + dp[rowNum][colNum - 1];
    }
  }

  return dp[HEIGHT - 1][WIDTH - 1];
};
