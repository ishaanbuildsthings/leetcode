// https://leetcode.com/problems/equal-row-and-column-pairs/description/
// Difficulty: Medium

// Problem
/*
Simplified:
Input: grid = [[3,2,1],[1,7,6],[2,7,7]]
Output: 1
Explanation: There is 1 equal row and column pair:
- (Row 2, Column 1): [2,7,7]

Detailed:
Given a 0-indexed n x n integer matrix grid, return the number of pairs (ri, cj) such that row ri and column cj are equal.

A row and column pair is considered equal if they contain the same elements in the same order (i.e., an equal array).
*/

// Solution, O(n*m) time and O(n*m) space. Serialize all rows and columns and crosscheck.

var equalPairs = function (grid) {
  const rows = {}; // maps serialized rows to the # of times they occured

  for (const row of grid) {
    const serialized = JSON.stringify(row);
    if (serialized in rows) {
      rows[serialized]++;
    } else {
      rows[serialized] = 1;
    }
  }

  const cols = {};

  for (let colNumber = 0; colNumber < grid[0].length; colNumber++) {
    const column = grid.map((row) => row[colNumber]);
    const serialized = JSON.stringify(column);
    if (serialized in cols) {
      cols[serialized]++;
    } else {
      cols[serialized] = 1;
    }
  }

  let result = 0;

  for (const row in rows) {
    if (row in cols) {
      result += rows[row] * cols[row];
    }
  }

  return result;
};
