// https://leetcode.com/problems/shift-2d-grid/description/
// Difficulty: Easy

// Problem
/*
Simplfied Explanation: You have a matrix, you need to shift every element to the right. The column on the right that is out of bounds should wrap left. That column should then shift down, and the bottom cell should wrap at the top.
*/

// Solution 1
// Time O(n*k), Space: O(1)
/*
Create an output mapping. For each cell, use math to determine where it should go. Compute the number of rightward shifts and downward shifts a cell will undergo, based on k, and determine the ending cell location. k % x is not O(k), it is O(1), so our overall time complexity is O(n*k). We could even modify the cell in place by starting at the top left cell, determining where it should go, putting it there, seeing what cell we just replaced, moving that, etc, until the cycle completes.
*/

var shiftGrid = function (grid, k) {
  const gridHeight = grid.length;
  const gridWidth = grid[0].length;
  const output = new Array(gridHeight).fill().map(() => new Array(gridWidth));
  for (let rowNumber = 0; rowNumber < gridHeight; rowNumber++) {
    for (let colNumber = 0; colNumber < gridWidth; colNumber++) {
      const newCol = (colNumber + k) % gridWidth;

      const downShiftsGuaranteed = Math.floor(k / gridWidth); // for every complete cycle, we are guaranteed to shift down by 1
      const leftoverMoves = k % gridWidth; // we still have some extra moves leftover which could cause an extra down shift, for instance moving 5 times on a 3x3 and we started at the middle
      const movesForExtraShift = gridWidth - colNumber;
      const downShiftsLeftover = leftoverMoves >= movesForExtraShift ? 1 : 0;
      const downShiftsTotal = downShiftsGuaranteed + downShiftsLeftover;
      const newRow = (rowNumber + downShiftsTotal) % gridHeight;
      output[newRow][newCol] = grid[rowNumber][colNumber];
    }
  }
  return output;
};

// Solution 2
// Time: O(n*m*k), Space: O(n) as we temporarily store a column in a variable. We could also do O(1) space by creating an output matrix and directly figuring out where each element should go in that matrix. Though the current solution changes the grid in place.
/*
A shift is moving m elements (number of columns) over, for n rows. We do this k times. During the shift, we also shift an individual column, which is n rows, so that does not affect the time complexity.
*/
var shiftGrid = function (grid, k) {
  // run the shift k times
  for (let i = 0; i < k; i++) {
    // store the right column as we iterate through the rows, also pop off the values
    const rightCol = [];

    for (const row of grid) {
      rightCol.push(row.pop());
    }
    // shift the right column
    rightCol.splice(0, 0, rightCol[rightCol.length - 1]);
    rightCol.pop();

    for (let i = 0; i < grid.length; i++) {
      const row = grid[i];
      row.splice(0, 0, rightCol[i]);
    }
  }
  return grid;
};
