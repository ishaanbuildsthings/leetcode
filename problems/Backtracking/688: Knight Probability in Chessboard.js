// https://leetcode.com/problems/knight-probability-in-chessboard/description/
// difficulty: Medium
// tags: dynamic programming 2d, backtracking

// Problem
/*
On an n x n chessboard, a knight starts at the cell (row, column) and attempts to make exactly k moves. The rows and columns are 0-indexed, so the top-left cell is (0, 0), and the bottom-right cell is (n - 1, n - 1).

A chess knight has eight possible moves it can make, as illustrated below. Each move is two cells in a cardinal direction, then one cell in an orthogonal direction.

Each time the knight is to move, it chooses one of eight possible moves uniformly at random (even if the piece would go off the chessboard) and moves there.

The knight continues moving until it has made exactly k moves or has moved off the chessboard.

Return the probability that the knight remains on the board after it has stopped moving.
*/

// Solution O(r*c*moves) time, O(r*c*moves) space
/*
We can essentially simulate the movement. The odds we stay on, is the sum of the odds we stay on given all possible adjacent states, divided by 8. We simulate that, but also memoize states [r][c][moves left].

There are r*c*moves possible states, and each state takes O(8) to complete, due to the movements of the knight.
*/

var knightProbability = function (n, k, row, column) {
  const HEIGHT = n;
  const WIDTH = n;

  // memo[row][col][movesleft] stores a memoized answer as there is repeated work
  const memo = new Array(HEIGHT)
    .fill()
    .map(() => new Array(WIDTH).fill().map(() => new Array(k + 1).fill(-1)));

  // returns a percentage chance the knight remains on the board after it stops moving, given the parameters
  function backtrack(movesLeft, r, c) {
    // if we are out of bounds, the odds are 0, and we stop backtracking, this can be pruned without entering recursive call also
    if (r < 0 || r >= HEIGHT || c < 0 || c >= WIDTH) {
      return 0;
    }

    // if we have no moves left, the odds are 1
    if (movesLeft === 0) {
      return 1;
    }

    if (memo[r][c][movesLeft] !== -1) {
      return memo[r][c][movesLeft];
    }

    let totalProbability = 0;

    // otherwise, the odds are the summed odds, divided by 8, for all possible paths
    const diffs = [
      [-1, -2],
      [-2, -1],
      [-2, 1],
      [-1, 2],
      [1, -2],
      [2, -1],
      [2, 1],
      [1, 2],
    ];
    for (const [rowDiff, colDiff] of diffs) {
      const newRow = r + rowDiff;
      const newCol = c + colDiff;
      totalProbability += backtrack(movesLeft - 1, newRow, newCol);
    }

    totalProbability /= 8; // divide by all 8 branches to get the result

    memo[r][c][movesLeft] = totalProbability;
    return totalProbability;
  }

  return backtrack(k, row, column);
};
