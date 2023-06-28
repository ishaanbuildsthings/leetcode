// https://leetcode.com/problems/rotting-oranges/description/
// Difficulty: Medium
// tags: matrix bfs, graphs

// Problem
/*
You are given an m x n grid where each cell can have one of three values:

0 representing an empty cell,
1 representing a fresh orange, or
2 representing a rotten orange.
Every minute, any fresh orange that is 4-directionally adjacent to a rotten orange becomes rotten.

Return the minimum number of minutes that must elapse until no cell has a fresh orange. If this is impossible, return -1.
*/

// Solution, O(n*m) time and O(n*m) space
/*
Initialize a visited grid, which indicates which oranges we have handled already. Get all the rotten ones and put them in a queue. Do a BFS (because we need to know how many minutes have passed), and for each minute rot the adjacent oranges, using the visited grid to not overlap. At the end return the number of minutes (minus 1 as an initial rotten orange takes 0 minutes). Handle some edge cases where we have only fresh oranges left or no oranges. There are ways to speed this up slightly with adding a counter for # of fresh oranges but I left it out for clarity.
*/

var orangesRotting = function (grid) {
  const HEIGHT = grid.length;
  const WIDTH = grid[0].length;

  const visited = new Array(HEIGHT)
    .fill()
    .map(() => new Array(WIDTH).fill(false));

  const deque = []; // fake deque, maintains tuples for coordinates, used in the bfs search
  for (let row = 0; row < HEIGHT; row++) {
    for (let col = 0; col < WIDTH; col++) {
      const cell = grid[row][col];
      if (cell === 2) {
        deque.push([row, col]);
        visited[row][col] = true; // any initial rotted oranges should not be later considered
      }
    }
  }

  let result = 0;

  // while there are rotten oranges we have not yet processed (not considered their neighbors)
  while (deque.length > 0) {
    // do a one-minute phase
    const length = deque.length;
    result++;

    for (let i = 0; i < length; i++) {
      const [row, col] = deque.shift(); // pretend O(1)

      // if we have a rotted orange, we want to make its fresh neighbors rotten, and then add those fresh ones to the queue so that they can rot more in turn

      // right adjacency
      if (
        col + 1 < WIDTH &&
        grid[row][col + 1] === 1 &&
        !visited[row][col + 1]
      ) {
        visited[row][col + 1] = true;
        grid[row][col + 1] = 2;
        deque.push([row, col + 1]);
      }

      // left adjacency
      if (col - 1 >= 0 && grid[row][col - 1] === 1 && !visited[row][col - 1]) {
        visited[row][col - 1] = true;
        grid[row][col - 1] = 2;
        deque.push([row, col - 1]);
      }

      // top adjacency
      if (row - 1 >= 0 && grid[row - 1][col] === 1 && !visited[row - 1][col]) {
        visited[row - 1][col] = true;
        grid[row - 1][col] = 2;
        deque.push([row - 1, col]);
      }

      // down adjacency
      if (
        row + 1 < HEIGHT &&
        grid[row + 1][col] === 1 &&
        !visited[row + 1][col]
      ) {
        visited[row + 1][col] = true;
        grid[row + 1][col] = 2;
        deque.push([row + 1, col]);
      }
    }
  }
  for (const row of grid) {
    for (const cell of row) {
      if (cell === 1) return -1;
    }
  }

  if (result - 1 === -1) return 0;

  return result - 1;
};
