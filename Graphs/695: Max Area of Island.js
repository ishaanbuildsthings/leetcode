// https://leetcode.com/problems/max-area-of-island/description/
// Difficulty: Medium
// tags: graph, matrix dfs

// Problem
/*
You are given an m x n binary matrix grid. An island is a group of 1's (representing land) connected 4-directionally (horizontal or vertical.) You may assume all four edges of the grid are surrounded by water.

The area of an island is the number of cells with a value 1 in the island.

Return the maximum area of an island in grid. If there is no island, return 0.
*/

// Solution, O(n*m) time and O(n*m) space
/*
Maintain a visited matrix of cells. Iterate through all root cells, doing a dfs for the whole island, tracking the size. Update the result as needed. There are a few ways to handle the base cases.

1) When we reach a cell out of bounds, or water, we return 0. Otherwise, we return 1 (for the current cell) plus the sum of the dfs calls for the adjacent cells.
2) We never recurse to invalid cells. We return 1 + the size of the adjacent cells.

I did option 2.
*/
var maxAreaOfIsland = function (grid) {
  const HEIGHT = grid.length;
  const WIDTH = grid[0].length;

  const visited = new Array(HEIGHT)
    .fill()
    .map(() => new Array(WIDTH).fill(false));

  function sizeOfIsland(r, c) {
    visited[r][c] = true;

    // visit adjacent cells that are in bounds, unvisited, and land

    const diffs = [
      [1, 0],
      [-1, 0],
      [0, 1],
      [0, -1],
    ];

    let total = 0;

    for (const [rowDiff, colDiff] of diffs) {
      const newRow = r + rowDiff;
      const newCol = c + colDiff;
      if (
        newRow < HEIGHT &&
        newRow >= 0 &&
        newCol < WIDTH &&
        newCol >= 0 &&
        !visited[newRow][newCol] &&
        grid[newRow][newCol] === 1
      ) {
        total += sizeOfIsland(newRow, newCol);
      }
    }

    return 1 + total;
  }

  let result = 0;

  for (let row = 0; row < HEIGHT; row++) {
    for (let col = 0; col < WIDTH; col++) {
      if (!visited[row][col] && grid[row][col] === 1) {
        result = Math.max(result, sizeOfIsland(row, col));
      }
    }
  }

  return result;
};
