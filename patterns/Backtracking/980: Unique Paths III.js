// https://leetcode.com/problems/unique-paths-iii/description/
// Difficulty: Hard
// tags: backtracking

// Problem
/*

You are given an m x n integer array grid where grid[i][j] could be:

1 representing the starting square. There is exactly one starting square.
2 representing the ending square. There is exactly one ending square.
0 representing empty squares we can walk over.
-1 representing obstacles that we cannot walk over.
Return the number of 4-directional walks from the starting square to the ending square, that walk over every non-obstacle square exactly once.

*/

// Solution, Space is kind of hard to compute, a high upper bound is 3^(m*n) as each cell chooses 3 adjacent neighbors, but you could probably calculate a lower upper bound. For space, we use n*m space for the visited array. We could also use less space by modifying the grid in place, but we would still need m*n space for the recursive callstack.
/*
Simple backtracking. Start at the start cell, and backtrack to adjacent neighbors that are not yet visited (as tracked in an n*m visited matrix), not obstacles, and not out of bounds. Mark a cell as visited when we enter it, unmark at the end. Maintain how many cells we have seen total, so if we reach the end, check if we have seen enough.
*/

var uniquePathsIII = function (grid) {
  const HEIGHT = grid.length;
  const WIDTH = grid[0].length;

  const visited = new Array(HEIGHT)
    .fill()
    .map(() => new Array(WIDTH).fill(false)); // initially all cells are unvisisted

  // find the starting square and total number of obstacles (used to cell how many cells we need to visite total)
  let startingRow;
  let startingCol;
  let totalObstacles = 0;

  for (let rowNum = 0; rowNum < HEIGHT; rowNum++) {
    for (let colNum = 0; colNum < WIDTH; colNum++) {
      if (grid[rowNum][colNum] === 1) {
        startingRow = rowNum;
        startingCol = colNum;
      } else if (grid[rowNum][colNum] === -1) {
        totalObstacles++;
      }
    }
  }

  const totalNumberOfCellsNeededToVisit = HEIGHT * WIDTH - totalObstacles;

  let result = 0;

  function backtrack(row, col, totalVisited) {
    // mark the current cell as visited
    visited[row][col] = true;

    // if we have seen every cell and end at the ending square, add a result
    if (
      totalVisited === totalNumberOfCellsNeededToVisit &&
      grid[row][col] === 2
    ) {
      result++;
      // we won't be able to recurse on any neighbors since everything is visited
    }

    // some extra pruning, if we reach the ending cell but haven't seen every cell yet, no need to continue on this path
    if (grid[row][col] === 2) {
      visited[row][col] = false;
      return;
    }

    const diffs = [
      [1, 0],
      [-1, 0],
      [0, 1],
      [0, -1],
    ];

    for (const [rowDiff, colDiff] of diffs) {
      const newRow = row + rowDiff;
      const newCol = col + colDiff;
      // backtrack to adjacent cells that are in range, not visited, and not obstacles
      if (
        newRow >= 0 &&
        newRow < HEIGHT &&
        newCol >= 0 &&
        newCol < WIDTH &&
        !visited[newRow][newCol] &&
        grid[newRow][newCol] !== -1
      ) {
        backtrack(newRow, newCol, totalVisited + 1);
      }
    }
    // once we are done with the branching starting from this cell, unvisit it
    visited[row][col] = false;
  }

  backtrack(startingRow, startingCol, 1); // the initial cell is visited

  return result;
};
