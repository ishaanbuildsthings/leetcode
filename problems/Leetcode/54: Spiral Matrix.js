// https://leetcode.com/problems/spiral-matrix/description/
// Difficulty: Medium

// Problem
/*
Given an m x n matrix, return all elements of the matrix in spiral order.
*/

// Solution
// O(n*m) time and O(1) space. If our direction is right, we would: fill a cell, move right, fill a cell, move right, etc, until the last cell we need to move, we would move down. Each time we do a rightward or leftward channel, we decrement the distance we would need to move on the next one. Similarly for vertical movement.

const spiralOrder = function (matrix) {
  const TOTAL_CELLS = matrix[0].length * matrix.length;
  const result = [];
  let horizontalMovement = matrix[0].length;
  let verticalMovement = matrix.length - 1;
  let direction = "right";
  let row = 0;
  let col = 0;

  // we should fill out a cell, then move the appropriate direction
  // we keep adding elements as long as our output hasn't filled all the cells
  // fill a cell + move, but if it is the last loop, fill a cell and do something else
  while (result.length < TOTAL_CELLS) {
    if (direction === "right") {
      for (let i = 0; i < horizontalMovement; i++) {
        result.push(matrix[row][col]);
        // if this is our last iteration of the loop, move down instead
        if (i === horizontalMovement - 1) {
          row++;
        }
        // this is not the last iteration, keep moving right
        else {
          col++;
        }
      }
      direction = "down";
      horizontalMovement--;
    } else if (direction === "down") {
      for (let i = 0; i < verticalMovement; i++) {
        result.push(matrix[row][col]);
        // move left if we are at the end
        if (i === verticalMovement - 1) {
          col--;
        } else {
          row++;
        }
      }
      direction = "left";
      verticalMovement--;
    } else if (direction === "left") {
      for (let i = 0; i < horizontalMovement; i++) {
        result.push(matrix[row][col]);
        // on the last iteration we move up
        if (i === horizontalMovement - 1) {
          row--;
        } else {
          col--;
        }
      }
      direction = "up";
      horizontalMovement--;
    } else if (direction === "up") {
      for (let i = 0; i < verticalMovement; i++) {
        result.push(matrix[row][col]);
        // on the last iteration we move right
        if (i === verticalMovement - 1) {
          col++;
        } else {
          row--;
        }
      }
      direction = "right";
      verticalMovement--;
    }
  }
  return result;
};
