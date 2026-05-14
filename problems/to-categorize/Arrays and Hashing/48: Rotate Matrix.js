// https://leetcode.com/problems/rotate-image/description/
// Difficulty: Medium

// Problem
/*
You are given an n x n 2D matrix representing an image, rotate the image by 90 degrees (clockwise).

You have to rotate the image in-place, which means you have to modify the input 2D matrix directly. DO NOT allocate another 2D matrix and do the rotation.
*/

// Solution
// O(n^2) time and O(1) space. Iterate over the top left block of the grid, swapping values in place. Think of it like iterating over all piece types for a rubik's cube, left wings, right wings, midges, obliques, etc, and performing a 4cycle.
// * Another solution would be to transpose the matrix around the major diagonal, then reflect.

var rotate = function (matrix) {
  const gridHeight = matrix.length;
  const gridWidth = matrix[0].length;

  // iterate over half the rows for even grids, and slightly less for odd grids
  for (let rowNumber = 0; rowNumber < Math.floor(gridHeight / 2); rowNumber++) {
    for (let colNumber = 0; colNumber < Math.ceil(gridWidth / 2); colNumber++) {
      // const topLeftCoords = [rowNumber, colNumber];
      // const topRightCoords = [colNumber, gridHeight - rowNumber - 1];
      // const bottomRightCoords = [gridHeight - rowNumber - 1, gridWidth - colNumber - 1];
      // const bottomLeftCoords = [gridWidth - colNumber - 1, rowNumber];

      const topLeftValue = matrix[rowNumber][colNumber];
      const topRightValue = matrix[colNumber][gridHeight - rowNumber - 1];
      const bottomRightValue =
        matrix[gridHeight - rowNumber - 1][gridWidth - colNumber - 1];
      const bottomLeftValue = matrix[gridWidth - colNumber - 1][rowNumber];

      matrix[rowNumber][colNumber] = bottomLeftValue;
      matrix[colNumber][gridHeight - rowNumber - 1] = topLeftValue;
      matrix[gridHeight - rowNumber - 1][gridWidth - colNumber - 1] =
        topRightValue;
      matrix[gridWidth - colNumber - 1][rowNumber] = bottomRightValue;
    }
  }
};
