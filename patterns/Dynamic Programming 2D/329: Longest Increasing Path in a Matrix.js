// https://leetcode.com/problems/longest-increasing-path-in-a-matrix/description/
// Difficulty: Hard
// tags: dynamic programming 2d, top down recursion

// Problem
/*
Given an m x n integers matrix, return the length of the longest increasing path in matrix.

From each cell, you can either move in four directions: left, right, up, or down. You may not move diagonally or move outside the boundary (i.e., wrap-around is not allowed).
*/

// Solution, O(m*n) time and O(m*n) space for the dp and the visited array.

/*
At any cell, we can increase our path to adjacent cells that are bigger than ours, in bound, and not yet visited in the current path. So we maintain a dp matrix which stores solutions (we don't have to worry about which direct we are coming from, due to the visited array). We check if the result is cached, if not, we check all valid neighbors, then cache the result in the dp.
*/
var longestIncreasingPath = function (matrix) {
  const HEIGHT = matrix.length;
  const WIDTH = matrix[0].length;

  // maps the answer for any given cell
  const dp = new Array(HEIGHT).fill().map(() => new Array(WIDTH).fill(null));

  const visited = new Array(HEIGHT)
    .fill()
    .map(() => new Array(WIDTH).fill(false));

  function recurse(row, col) {
    // check if it is in the cache already
    if (dp[row][col] !== null) {
      return dp[row][col];
    }

    // check adjacent cells, if they are in bounds, larger, and not yet visited
    const diffs = [
      [1, 0],
      [-1, 0],
      [0, 1],
      [0, -1],
    ];
    let maxPath = 1; // by default, our max path is at least 1 for all cells
    for (const [rowDiff, colDiff] of diffs) {
      const newRow = row + rowDiff;
      const newCol = col + colDiff;

      if (
        newRow >= 0 &&
        newRow < HEIGHT &&
        newCol >= 0 &&
        newCol < WIDTH &&
        !visited[newRow][newCol] &&
        matrix[newRow][newCol] > matrix[row][col]
      ) {
        visited[newRow][newCol] = true;
        maxPath = Math.max(maxPath, 1 + recurse(newRow, newCol));
        visited[newRow][newCol] = false;
      }
    }

    dp[row][col] = maxPath;

    return maxPath;
  }

  let result = 1;

  // try a path starting from each cell
  for (let rowNum = 0; rowNum < HEIGHT; rowNum++) {
    for (let colNum = 0; colNum < WIDTH; colNum++) {
      result = Math.max(result, recurse(rowNum, colNum));
    }
  }

  return result;
};
