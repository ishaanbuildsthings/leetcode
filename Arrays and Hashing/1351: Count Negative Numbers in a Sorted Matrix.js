// https://leetcode.com/problems/count-negative-numbers-in-a-sorted-matrix/description/
// Difficulty: Easy

// Problem
/*
Given a m x n matrix grid which is sorted in non-increasing order both row-wise and column-wise, return the number of negative numbers in grid.
*/

// Solution, O(n+m) time and O(1) space, start iterating from the bottom left and move up or right depending on if the number is negative.

var countNegatives = function (grid) {
  const HEIGHT = grid.length;
  const WIDTH = grid[0].length;

  // start at the bottom left corner
  let row = HEIGHT - 1;
  let col = 0;

  let result = 0;

  while (row >= 0 && col < WIDTH) {
    const val = grid[row][col];

    // if we are positive, we have never yet found a negative, move right to try to decrement the value
    if (val >= 0) {
      col++;
      continue;
    }
    /* here val is negative */

    // if the value above us is negative, i.e. we started in the bottom left at a negative, or we moved right into a higher negative field, traverse up
    while (row > 0 && grid[row - 1][col] < 0) {
      row--;
    }

    const numberOfNegRowsBelow = HEIGHT - row;
    result += numberOfNegRowsBelow;

    col++; // move to the right
  }

  return result;
};
