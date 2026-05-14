// https://leetcode.com/problems/set-matrix-zeroes/description/
// Difficulty: Medium

// Problem
/*
Given an m x n integer matrix matrix, if an element is 0, set its entire row and column to 0's.

You must do it in place.
*/

// Solution 1
// O(n*m) time and O(1) space. First, iterate over the top row and leftmost column and determine if they will need to eventually be zeroed out. We cannot zero them out immediately, because we will use these rows and columns to track the other cells that should be zeroed out. Then iterate, over all the cells except the headers. If the cell is a 0, assign their respective headers to be 0. Now, all our headers will indicate which rows and columns should be zeroed out. Then, iterate over the cells again, zero-ing them based on headers. Finally, zero out the headers if necessary. We have to do two n*m iterations, consider 1 0, when we are at the 1, the row header is still a 1, so we don't overwrite it, only when we reach the 0 do we overwrite the row header, but now we wouldn't get to update the first cell

var setZeroes = function (matrix) {
  // if any of the cells in the first row are 0, we will need to overwrite the full header row at the end
  let overwriteRow = false;
  for (let colNumber = 0; colNumber < matrix[0].length; colNumber++) {
    if (matrix[0][colNumber] === 0) {
      overwriteRow = true;
      break;
    }
  }
  // same thing with the first column
  let overwriteCol = false;
  for (let rowNumber = 0; rowNumber < matrix.length; rowNumber++) {
    if (matrix[rowNumber][0] === 0) {
      overwriteCol = true;
      break;
    }
  }

  // read all non-header cells, update the headers, we need to do this step entirely first before writing, consider 1 0, when we are at the 1, the row header is still a 1, so we don't overwrite it, only when we reach the 0 do we overwrite the row header, but now we wouldn't get to update the first cell
  for (let rowNumber = 1; rowNumber < matrix.length; rowNumber++) {
    for (let colNumber = 1; colNumber < matrix[0].length; colNumber++) {
      // if we see a 0 in the cell, overwrite the headers
      if (matrix[rowNumber][colNumber] === 0) {
        matrix[rowNumber][0] = 0;
        matrix[0][colNumber] = 0;
      }
    }
  }

  // now update the cells
  for (let rowNumber = 1; rowNumber < matrix.length; rowNumber++) {
    for (let colNumber = 1; colNumber < matrix[0].length; colNumber++) {
      if (matrix[0][colNumber] === 0 || matrix[rowNumber][0] === 0) {
        matrix[rowNumber][colNumber] = 0;
      }
    }
  }

  // update the headers
  if (overwriteRow) {
    for (let colNumber = 0; colNumber < matrix[0].length; colNumber++) {
      matrix[0][colNumber] = 0;
    }
  }
  if (overwriteCol) {
    for (let rowNumber = 0; rowNumber < matrix.length; rowNumber++) {
      matrix[rowNumber][0] = 0;
    }
  }
};

// Solution 2
// O(n*m*(n+m)) time, O(1) space
// Iterate over every cell, if a cell is a 0, "zero out" that row and column with a symbol, ignoring other root 0s. Once that is done, replace all symbols with a 0.

var setZeroes = function (matrix) {
  const symbol = Symbol();

  for (let rowNumber = 0; rowNumber < matrix.length; rowNumber++) {
    for (let colNumber = 0; colNumber < matrix[0].length; colNumber++) {
      // if we see a symbol or a number, keep going
      if (matrix[rowNumber][colNumber] !== 0) {
        continue;
      }
      // if we see a 0, ovewrite all non-zeroes in the row and column with a symbol, don't overwrite 0s since those can propogate their own symbols
      // overwrite column
      for (let rowNum = 0; rowNum < matrix.length; rowNum++) {
        if (matrix[rowNum][colNumber] !== 0) {
          matrix[rowNum][colNumber] = symbol;
        }
      }
      // overwrite row
      for (let colNum = 0; colNum < matrix[0].length; colNum++) {
        if (matrix[rowNumber][colNum] !== 0) {
          matrix[rowNumber][colNum] = symbol;
        }
      }
    }
  }

  for (let rowNumber = 0; rowNumber < matrix.length; rowNumber++) {
    for (let colNumber = 0; colNumber < matrix[0].length; colNumber++) {
      if (matrix[rowNumber][colNumber] === symbol) {
        matrix[rowNumber][colNumber] = 0;
      }
    }
  }
};
