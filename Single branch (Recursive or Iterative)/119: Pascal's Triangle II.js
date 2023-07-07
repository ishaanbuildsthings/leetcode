// https://leetcode.com/problems/pascals-triangle-ii/description/
// Difficulty: Easy
// tags: single branch (recursive or iterative)

// Problem
/*
Given an integer rowIndex, return the rowIndexth (0-indexed) row of the Pascal's triangle.

In Pascal's triangle, each number is the sum of the two numbers directly above it as shown:
*/

// Solution, O(k^2) time and O(k) space
/*
Just build out the rows. We build k rows, each taking k time. We also need to hold at most k memory over the output on the last row.
*/

var getRow = function (rowIndex) {
  if (rowIndex === 0) return [1];
  if (rowIndex === 1) return [1, 1];

  let row = [1, 2];

  while (row.length < rowIndex) {
    const newRow = [1];
    // for iterate over the row, considering every left number as a left number, the last element uses a dummy one
    for (let i = 0; i < row.length - 1; i++) {
      const leftNum = row[i];
      const rightNum = row[i + 1];
      const newElement = leftNum + rightNum;
      newRow.push(newElement);
    }
    newRow.push(row[row.length - 1] + 1);
    row = newRow;
  }

  row.push(1); // add the last ending 1
  return row;
};
