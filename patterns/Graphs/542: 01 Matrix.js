// https://leetcode.com/problems/01-matrix/description/
// Difficulty: Medium
// Tags: bfs

// Problem
/*
Given an m x n binary matrix mat, return the distance of the nearest 0 for each cell.

The distance between two adjacent cells is 1.
*/

// Solution, O(n*m) time and space
/*
Do a multisource BFS. We solve for each cell so O(n*m) time and O(n*m) space.
*/

// NOTE: adding a cell to seen when we dequeue is bad, because in one layer we might add the same neighbor multiple times, so add a cell to seen when we insert it into the queue
var updateMatrix = function (mat) {
  const HEIGHT = mat.length;
  const WIDTH = mat[0].length;

  const seen = new Set(); // don't repeat solving / overwrite cells

  // start with all zeroes
  const queue = []; // fake queue
  for (let r = 0; r < HEIGHT; r++) {
    for (let c = 0; c < WIDTH; c++) {
      if (mat[r][c] === 0) {
        queue.push([r, c]);
        const key = r * WIDTH + c;
        seen.add(key);
      }
    }
  }

  const result = new Array(HEIGHT).fill().map(() => new Array(WIDTH).fill(0));

  let distance = 0;

  while (queue.length > 0) {
    distance++;
    const length = queue.length;
    for (let i = 0; i < length; i++) {
      const [r, c] = queue.shift();
      const key = r * WIDTH + c;
      const diffs = [
        [1, 0],
        [-1, 0],
        [0, 1],
        [0, -1],
      ];
      for (const [rowDiff, colDiff] of diffs) {
        const newRow = r + rowDiff;
        const newCol = c + colDiff;
        const newKey = newRow * WIDTH + newCol;
        // if the neighbor is in range and not written to
        if (
          newRow >= 0 &&
          newRow < HEIGHT &&
          newCol >= 0 &&
          newCol < WIDTH &&
          !seen.has(newKey)
        ) {
          seen.add(newKey);
          result[newRow][newCol] = distance;
          queue.push([newRow, newCol]);
        }
      }
    }
  }

  return result;
};
