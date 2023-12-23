// https://leetcode.com/problems/pascals-triangle/description/
// Difficulty: Easy

// Problem
/*
Given an integer numRows, return the first numRows of Pascal's triangle.
*/

// Solution
// O(n^2) time and O(1) auxillary space. Iterate over the previous row, and construct the new row. n^2 time since we have to process n rows of length n. Even though the rows are length 1, 2, ... n-1, n, it still works out to n^2.

var generate = function (numRows) {
  const result = [[1]];
  for (let i = 2; i <= numRows; i++) {
    const newRow = [];
    const prevRow = result[i - 2]; // [1]
    for (let j = 0; j < prevRow.length + 1; j++) {
      let newNum;
      if (j === 0 || j === prevRow.length) {
        newNum = 1;
      } else {
        newNum = prevRow[j] + prevRow[j - 1];
      }
      newRow.push(newNum);
    }
    result.push(newRow);
  }
  return result;
};
