// https://leetcode.com/problems/number-of-increasing-paths-in-a-grid/description/
// Difficulty: Hard
// tags: dynamic programming 2d, top down recursion

/*
Example:
Input: grid = [[1,1],[3,4]]
Output: 8
Explanation: The strictly increasing paths are:
- Paths with length 1: [1], [1], [3], [4].
- Paths with length 2: [1 -> 3], [1 -> 4], [3 -> 4].
- Paths with length 3: [1 -> 3 -> 4].
The total number of paths is 4 + 3 + 1 = 8.

Detailed:
You are given an m x n integer matrix grid, where you can move from a cell to any adjacent cell in all 4 directions.

Return the number of strictly increasing paths in the grid such that you can start from any cell and end at any cell. Since the answer may be very large, return it modulo 109 + 7.

Two paths are considered different if they do not have exactly the same sequence of visited cells.
*/

// Solution, O(n*m) time and O(n*m) space.
/*
Allocate an n*m matrix. For each cell, check how many paths you can make starting at that cell. We do this by iterating to adjacent, strictly increasing neighbors. Memoize and reuse results as needed. Instead of using JSON.stringify([row, col]) as a key in a hashmap cash, just allocate a matrix and do lookups in that matrix.
*/

var countPaths = function (grid) {
  const MOD = 10 ** 9 + 7;

  const HEIGHT = grid.length;
  const WIDTH = grid[0].length;

  const cache = new Array(HEIGHT).fill().map(() => new Array(WIDTH).fill(-1)); // -1 means the value hasn't been solved

  function recurse(row, col) {
    if (cache[row][col] !== -1) {
      return cache[row][col];
    }

    const val = grid[row][col];
    let waysFromThisCell = 1; // we can always make a strictly increasing path with at least the current cell

    // if the bottom cell is in bounds and increasing, we will add that sum
    if (row + 1 < HEIGHT && grid[row + 1][col] > val) {
      waysFromThisCell = waysFromThisCell + recurse(row + 1, col);
    }

    // top cell
    if (row - 1 >= 0 && grid[row - 1][col] > val) {
      waysFromThisCell = (waysFromThisCell + recurse(row - 1, col)) % MOD;
    }

    // right cell
    if (col + 1 < WIDTH && grid[row][col + 1] > val) {
      waysFromThisCell = (waysFromThisCell + recurse(row, col + 1)) % MOD;
    }

    // left cell
    if (col - 1 >= 0 && grid[row][col - 1] > val) {
      waysFromThisCell = (waysFromThisCell + recurse(row, col - 1)) % MOD;
    }

    cache[row][col] = waysFromThisCell;

    return waysFromThisCell;
  }

  let result = 0;

  for (let rowNum = 0; rowNum < HEIGHT; rowNum++) {
    for (let colNum = 0; colNum < WIDTH; colNum++) {
      result = (result + recurse(rowNum, colNum)) % MOD;
    }
  }

  return result;
};
