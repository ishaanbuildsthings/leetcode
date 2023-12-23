// https://leetcode.com/problems/number-of-islands/description/
// Difficulty: Medium
// tags: graph, matrix dfs

// Problem
/*
Example:
Input: grid = [
  ["1","1","1","1","0"],
  ["1","1","0","1","0"],
  ["1","1","0","0","0"],
  ["0","0","0","0","0"]
]
Output: 1

Detailed:
Given an m x n 2D binary grid grid which represents a map of '1's (land) and '0's (water), return the number of islands.

An island is surrounded by water and is formed by connecting adjacent lands horizontally or vertically. You may assume all four edges of the grid are all surrounded by water.
*/

// Solution 1, O(n*m) time and O(n*m) space
/*
Maintain a visited set/matrix. Iterate across root cells, if we see a 1, fill to adjacent cells that are 1s and not yet visited, then gain 1 island.
*/
// * We could have O(min(n, m)) space when using BFS, and modifying the input matrix. The BFS would hold at most that many elements in the queue, assuming we start from the top left of the island, as our queue will hold diagonals of the island (really you need a picture to see this).

var numIslands = function (grid) {
  const HEIGHT = grid.length;
  const WIDTH = grid[0].length;

  const visited = new Set();

  function visit(r, c) {
    const key = WIDTH * r + c;
    if (visited.has(key)) {
      return;
    }

    visited.add(key);

    // recurse on adjacent, in bounds, cells of 1, that are unvisited cells
    const diffs = [
      [1, 0],
      [-1, 0],
      [0, 1],
      [0, -1],
    ];

    for (const [rowDiff, colDiff] of diffs) {
      const newR = r + rowDiff;
      const newC = c + colDiff;
      if (
        newR < HEIGHT &&
        newR >= 0 &&
        newC < WIDTH &&
        newC >= 0 &&
        !visited.has(newR * WIDTH + newC) &&
        grid[newR][newC] === "1"
      ) {
        visit(newR, newC);
      }
    }
  }

  let result = 0;

  for (let row = 0; row < HEIGHT; row++) {
    for (let col = 0; col < WIDTH; col++) {
      const key = WIDTH * row + col;
      if (!visited.has(key) && grid[row][col] === "1") {
        visit(row, col);
        result++;
      }
    }
  }

  return result;
};
