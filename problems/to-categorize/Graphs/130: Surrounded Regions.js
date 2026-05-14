// https://leetcode.com/problems/surrounded-regions/description/
// Difficulty: Medium
// tags: graphs, matrix dfs

// Problem
/*
Given an m x n matrix board containing 'X' and 'O', capture all regions that are 4-directionally surrounded by 'X'.

A region is captured by flipping all 'O's into 'X's in that surrounded region.
*/

// Solution, O(m*n) time and O(m*n) space for the visited matrix and recursive callstack
// * I think you could reduce the space complexity by any of the following: maybe some iterative solution so there is no callstack. doing a bfs and mutating the input instead of allocating a visited matrix, might let you get min(m, n) complexity for the queue size.
/*
To see what regions are surrounded, we can scan all regions via a dfs, if we eventually touch an edge, update all cells that we touched an edge. This is the same complexity, but a bit slow (this is my original solution for pacific atlantic water flow). Instead, we can just recurse from all edges, seeing which regions we touch or not. I used a visited array to track what we had seen, but we could mutate the array, then fix the visited ones to go back to normal land later. After all, we are to mutate the input array in the question.

I also didn't recurse to bad neighbors, to prevent callstack overhead, as opposed to terminating within the recursive function if we go out of bounds or something.
*/

var solve = function (board) {
  const HEIGHT = board.length;
  const WIDTH = board[0].length;

  // tracks cells that we have seen from the edge, also used to not recurse into the same cell multiple times
  const visitedFromEdge = new Array(HEIGHT)
    .fill()
    .map(() => new Array(WIDTH).fill(false));

  function visit(r, c) {
    visitedFromEdge[r][c] = true;

    const diffs = [
      [1, 0],
      [-1, 0],
      [0, 1],
      [0, -1],
    ];

    for (const [rowDiff, colDiff] of diffs) {
      const newR = r + rowDiff;
      const newC = c + colDiff;
      // recurse to neighbors that are in bounds, 'O's, and not visited
      if (
        newR >= 0 &&
        newR < HEIGHT &&
        newC >= 0 &&
        newC < WIDTH &&
        !visitedFromEdge[newR][newC] &&
        board[newR][newC] === "O"
      ) {
        visit(newR, newC);
      }
    }
  }

  // run a root dfs call from every edge cell that is an 'O', and not visited before (just a small optimization)
  // top and bottom edge
  for (let c = 0; c < WIDTH; c++) {
    if (!visitedFromEdge[0][c] && board[0][c] === "O") {
      visit(0, c);
    }
    if (!visitedFromEdge[HEIGHT - 1][c] && board[HEIGHT - 1][c] === "O") {
      visit(HEIGHT - 1, c);
    }
  }

  // left edge and right edges
  for (let r = 0; r < HEIGHT; r++) {
    if (!visitedFromEdge[r][0] && board[r][0] === "O") {
      visit(r, 0);
    }
    if (!visitedFromEdge[r][WIDTH - 1] && board[r][WIDTH - 1] === "O") {
      visit(r, WIDTH - 1);
    }
  }

  // edit the matrix to capture regions, this could be done the moment we reached that cell from the edge too, but seaparting it makes it a bit easier
  for (let r = 0; r < HEIGHT; r++) {
    for (let c = 0; c < WIDTH; c++) {
      // if we couldn't reach that point from an edge at a 0, it's captures
      if (!visitedFromEdge[r][c]) {
        board[r][c] = "X";
      }
    }
  }

  return board;
};
