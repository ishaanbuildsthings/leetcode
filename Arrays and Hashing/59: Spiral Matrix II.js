//https://leetcode.com/problems/spiral-matrix-ii/description/
// Difficulty: Medium

// Problem
/*
Given a positive integer n, generate an n x n matrix filled with elements from 1 to n2 in spiral order.
*/

// Solution
// O(n^2) time and O(1) space. Create the empty matrix to start with. Start iterating to the right until we hit a boundary or an already filled value, then start going down, etc.

const generateMatrix = function (n) {
  const TOTAL_CELLS = n * n;
  // create an n x n matrix
  const matrix = new Array(n).fill(null).map(() => new Array(n).fill(null));
  let currentDirection = "right";
  let row = 0;
  let col = 0;
  let currentNumber = 1;
  let cellsFilled = 0;

  while (cellsFilled < TOTAL_CELLS) {
    matrix[row][col] = currentNumber; // fill out the number
    cellsFilled++;
    currentNumber++;
    if (currentDirection === "right") {
      const nextCol = col + 1;
      // outside the boundary or we have filled that cell
      if (nextCol >= n || matrix[row][nextCol] !== null) {
        currentDirection = "down";
        row++;
      } else {
        col++;
      }
    } else if (currentDirection === "down") {
      const nextRow = row + 1;
      if (nextRow >= n || matrix[nextRow][col] !== null) {
        currentDirection = "left";
        col--;
      } else {
        row++;
      }
    } else if (currentDirection === "left") {
      const nextCol = col - 1;
      if (nextCol < 0 || matrix[row][nextCol] !== null) {
        currentDirection = "up";
        row--;
      } else {
        col--;
      }
    } else if (currentDirection === "up") {
      const nextRow = row - 1;
      if (nextRow < 0 || matrix[nextRow][col] !== null) {
        currentDirection = "right";
        col++;
      } else {
        row--;
      }
    }
  }
  return matrix;
};
