// https://leetcode.com/problems/the-maze/description/
// Difficulty: Medium
// Tags: bfs

// Problem
/*
There is a ball in a maze with empty spaces (represented as 0) and walls (represented as 1). The ball can go through the empty spaces by rolling up, down, left or right, but it won't stop rolling until hitting a wall. When the ball stops, it could choose the next direction.

Given the m x n maze, the ball's start position and the destination, where start = [startrow, startcol] and destination = [destinationrow, destinationcol], return true if the ball can stop at the destination, otherwise return false.

You may assume that the borders of the maze are all walls (see examples).
*/

// Solution, O(n*m*(n + m)) time, O(n*m) space
/*
For a given position, we can roll the ball up to 4 possible ways. If we already reached that position before, we shouldn't consider it again. We start at the current position, and bfs adjacent states. At worst case, every cell can be reached. Finding adjacent states takes O(height + width) time, meaning n*m cells take (n+m) time. We also have a queue size of n*m and a seen set of n*m. DFS can also work.
*/

/**
 * @param {number[][]} maze
 * @param {number[]} start
 * @param {number[]} destination
 * @return {boolean}
 */
var hasPath = function (maze, start, destination) {
  const HEIGHT = maze.length;
  const WIDTH = maze[0].length;

  const seen = new Set(); // coordinates we could stop at

  const queue = [start]; // fake queue

  function findRollableAdjacents(row, col) {
    const adjs = [];
    // check left
    for (let colIterator = col - 1; colIterator >= -1; colIterator--) {
      if (colIterator === -1) {
        adjs.push([row, 0]);
        break;
      }
      if (maze[row][colIterator] === 1) {
        // don't add the same cell that we started from
        if (!(col === colIterator + 1)) {
          adjs.push([row, colIterator + 1]);
        }
        break;
      }
    }
    // check right
    for (let colIterator = col + 1; colIterator < WIDTH + 1; colIterator++) {
      if (colIterator === WIDTH) {
        adjs.push([row, WIDTH - 1]);
        break;
      }
      if (maze[row][colIterator] === 1) {
        if (!(col === colIterator - 1)) {
          adjs.push([row, colIterator - 1]);
        }
        break;
      }
    }
    // check down
    for (let rowIterator = row + 1; rowIterator < HEIGHT + 1; rowIterator++) {
      if (rowIterator === HEIGHT) {
        adjs.push([HEIGHT - 1, col]);
        break;
      }
      if (maze[rowIterator][col] === 1) {
        if (!(row === rowIterator - 1)) {
          adjs.push([rowIterator - 1, col]);
        }
        break;
      }
    }
    // check up
    for (let rowIterator = row - 1; rowIterator >= -1; rowIterator--) {
      if (rowIterator === -1) {
        adjs.push([0, col]);
        break;
      }
      if (maze[rowIterator][col] === 1) {
        if (!(row === rowIterator + 1)) {
          adjs.push([rowIterator + 1, col]);
        }
        break;
      }
    }
    return adjs;
  }

  while (queue.length > 0) {
    const length = queue.length;
    for (let i = 0; i < length; i++) {
      const positionRollFrom = queue.shift();
      const [row, col] = positionRollFrom;
      const key = `${row},${col}`;
      seen.add(key);
      const adjs = findRollableAdjacents(row, col);
      for (const [adjRow, adjCol] of adjs) {
        if (adjRow === destination[0] && adjCol === destination[1]) {
          return true;
        }
        const adjKey = `${adjRow},${adjCol}`;
        if (!seen.has(adjKey)) {
          queue.push([adjRow, adjCol]);
        }
      }
    }
  }

  return false;
};
