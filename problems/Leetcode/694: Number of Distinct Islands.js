// https://leetcode.com/problems/number-of-distinct-islands/description/
// Difficulty: Medium
// Tags: matrix dfs

// Problem
/*
You are given an m x n binary matrix grid. An island is a group of 1's (representing land) connected 4-directionally (horizontal or vertical.) You may assume all four edges of the grid are surrounded by water.

An island is considered to be the same as another if and only if one island can be translated (and not rotated or reflected) to equal the other.

Return the number of distinct islands.
*/

// Solution, O(m*n) time and O(m*n) space
/*
Iterate through the grid, doing a dfs on each land cell. We mark them as visited to not visit the same island twice. As we dfs, we gather the cells in a list. At the end of the dfs, we translate all cells as if the first cell were at 0,0. We add this to a set to see if other islands of the same shape were there.

Each cell is visited once or skipped. We can also serialize each cell up to one time, so still m*n total time.
*/

var numDistinctIslands = function (grid) {
  const HEIGHT = grid.length;
  const WIDTH = grid[0].length;

  // tracks if a cell has been visited, so we don't revisit the same island, can use a set if we expect very few land compared to water, but matrix constraints are small
  const visited = new Array(HEIGHT)
    .fill()
    .map(() => new Array(WIDTH).fill(false));

  function dfs(r, c, currentSerialization) {
    visited[r][c] = true;
    currentSerialization.push([r, c]);

    const diffs = [
      [1, 0],
      [-1, 0],
      [0, 1],
      [0, -1],
    ];

    for (const [rowDiff, colDiff] of diffs) {
      const newRow = r + rowDiff;
      const newCol = c + colDiff;
      // iterate to adjacent neighbors if they are in bounds, land, and not yet visited
      if (
        newRow >= 0 &&
        newRow < HEIGHT &&
        newCol >= 0 &&
        newCol < WIDTH &&
        grid[newRow][newCol] === 1 &&
        !visited[newRow][newCol]
      ) {
        dfs(newRow, newCol, currentSerialization);
      }
    }
  }

  const serializations = new Set();

  for (let r = 0; r < HEIGHT; r++) {
    for (let c = 0; c < WIDTH; c++) {
      if (visited[r][c]) {
        continue;
      }

      // skip water
      if (grid[r][c] === 0) {
        continue;
      }

      const newSerialization = [];
      dfs(r, c, newSerialization);

      // set everything relative to 0,0 so we can compare serializations properly
      const [topLeftRowCoordDiff, topLeftColCoordDiff] = newSerialization[0];

      for (let i = 0; i < newSerialization.length; i++) {
        newSerialization[i][0] = newSerialization[i][0] - topLeftRowCoordDiff;
        newSerialization[i][1] = newSerialization[i][1] - topLeftColCoordDiff;
      }

      serializations.add(JSON.stringify(newSerialization));
    }
  }

  return Array.from(serializations).length;
};
