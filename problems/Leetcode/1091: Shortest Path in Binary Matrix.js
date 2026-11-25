// https://leetcode.com/problems/shortest-path-in-binary-matrix/description/
// Difficulty: Medium
// tags: graph, matrix bfs

// Problem
/*
Simplified:
We need to go from the top left, to the bottom right, in as few nodes as possible. We can go to any 8-directionally adjacent nodes, that are also 0s (1s are walls). Find the shortest path length.

Detailed:
Given an n x n binary matrix grid, return the length of the shortest clear path in the matrix. If there is no clear path, return -1.

A clear path in a binary matrix is a path from the top-left cell (i.e., (0, 0)) to the bottom-right cell (i.e., (n - 1, n - 1)) such that:

All the visited cells of the path are 0.
All the adjacent cells of the path are 8-directionally connected (i.e., they are different and they share an edge or a corner).
The length of a clear path is the number of visited cells of this path.
*/

// Solution, O(n^2) time and O(n) space, since in bfs starting from the top left, our queue size is limited to min(n,m) due to the queue being at most a diagonal.

/*
Start at the top left, bfs out, and repeat, until we reach the ending cell, or the queue is empty, meaning we couldn't.
*/

var shortestPathBinaryMatrix = function (grid) {
  const HEIGHT = grid.length;
  const WIDTH = grid[0].length;

  const visited = new Array(HEIGHT)
    .fill()
    .map(() => new Array(WIDTH).fill(false));

  const queue = [[0, 0]]; // pretend queue

  let result = 0;

  // if the initial cell is a wall, we can never even start the bfs
  if (grid[0][0] === 1) {
    return -1;
  }

  // bfs until we reach the ending cell, or if the queue is empty, we have no way to reach the end
  while (queue.length > 0) {
    result++;
    const length = queue.length;
    for (let i = 0; i < length; i++) {
      const [r, c] = queue.shift(); // pretend O(1)

      if (r === HEIGHT - 1 && c === WIDTH - 1) {
        return result;
      }

      const diffs = [
        [1, 0],
        [-1, 0],
        [0, 1],
        [0, -1],
        [1, 1],
        [1, -1],
        [-1, 1],
        [-1, -1],
      ];

      for (const [rowDiff, colDiff] of diffs) {
        const newRow = r + rowDiff;
        const newCol = c + colDiff;
        if (
          newRow >= 0 &&
          newRow < HEIGHT &&
          newCol >= 0 &&
          newCol < WIDTH &&
          grid[newRow][newCol] === 0 &&
          !visited[newRow][newCol]
        ) {
          queue.push([newRow, newCol]);
          visited[newRow][newCol] = true;
        }
      }
    }
  }

  return -1;
};

/**
1 0 0
1 1 0
1 1 0



*/
